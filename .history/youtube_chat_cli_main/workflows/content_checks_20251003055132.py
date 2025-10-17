"""
Content Checks Workflow (initial implementation)

Flow: Start -> Execute Deep Research -> Duplicate Check -> Router
(NOVEL -> Synthesizer; REDUNDANT -> Prompt Refinement -> Loop<=10).

Notes:
- Vector store search is best-effort: gracefully degrades if unavailable
- LLM synthesis/refinement is also best-effort: placeholder when LLM not configured
- GDrive evidence filtering is via metadata filter {'source': 'gdrive'}
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import logging

from ..core.config import get_config
from . import deep_research

logger = logging.getLogger(__name__)


def _safe_llm_generate(prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> str:
    try:
        from ..services.llm_service import get_llm_service, LLMError  # lazy import
        llm = get_llm_service()
        return llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=temperature)
    except Exception as e:
        logger.warning("LLM unavailable for content-checks synthesis/refinement: %s", e)
        return ""


def _vector_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    try:
        from ..services.vector_store import get_vector_store, VectorStoreError  # lazy import
        vs = get_vector_store()
        # Filter for Google Drive-originated content if metadata present
        return vs.search(query=query, top_k=top_k, filter_dict={"source": "gdrive"})
    except Exception as e:
        logger.warning("Vector store unavailable for duplicate check: %s", e)
        return []


def run(topic: str, max_loops: Optional[int] = None) -> Dict[str, Any]:
    """Run the content checks workflow."""
    logger.info("[ContentChecks] run called topic=%r", topic)
    started = datetime.now(timezone.utc).isoformat()

    cfg = get_config()
    red_thresh = getattr(cfg, "duplicate_similarity_redundant", 0.85)
    max_iters = max_loops if (isinstance(max_loops, int) and max_loops > 0) else 1

    # 1) Execute deep research conversation once (bounded)
    conv = deep_research.run(topic, max_turns=2)

    # Extract raw insights text (concatenate turns)
    transcript = conv.get("transcript", [])
    raw_insights = "\n\n".join(t.get("content", "") for t in transcript)
    if not raw_insights:
        raw_insights = f"Topic: {topic}"

    # 2) Duplicate check against vectorized archive (best-effort)
    hits = _vector_search(raw_insights, top_k=5)
    max_score = max((h.get("score", 0.0) for h in hits), default=0.0)
    decision = "REDUNDANT" if max_score >= red_thresh else "NOVEL"

    evidence = {
        "gdrive_hits": [
            {
                "id": h.get("id"),
                "score": h.get("score"),
                "metadata": h.get("metadata", {}),
            }
            for h in hits
        ],
        "max_score": max_score,
        "threshold": red_thresh,
    }

    # 3) Route with bounded loop (<= max_iters)
    output: Dict[str, Any] = {}
    loop_count = 0

    current_topic = topic
    current_insights = raw_insights

    for i in range(max_iters):
        loop_count = i + 1
        if decision == "NOVEL":
            synthesis = _safe_llm_generate(
                prompt=(
                    "Synthesize the key findings into a concise brief with citations if present.\n\n"
                    f"INSIGHTS:\n{current_insights}\n"
                ),
                system_prompt=(
                    "You are a Synthesizer. Produce a succinct, high-signal brief."
                ),
                temperature=0.4,
            ) or "SYNTHESIS_PLACEHOLDER"
            output = {"synthesis": synthesis}
            break
        else:
            refined = _safe_llm_generate(
                prompt=(
                    "Given the following insights appear redundant in the archive, propose a refined prompt"
                    " to elicit novel angles and sources. Return only the refined prompt.\n\n"
                    f"INSIGHTS:\n{current_insights}\n"
                ),
                system_prompt=(
                    "You are a Prompt Engineer. Return just the improved prompt text."
                ),
                temperature=0.6,
            ) or "REFINEMENT_PLACEHOLDER"
            output = {"refined_prompt": refined}

            # Re-run deep research with refined prompt to seek novelty (bounded)
            try:
                rerun = deep_research.run(refined, max_turns=2)
                current_insights = "\n\n".join(t.get("content", "") for t in rerun.get("transcript", [])) or refined
                hits = _vector_search(current_insights, top_k=5)
                max_score = max((h.get("score", 0.0) for h in hits), default=0.0)
                decision = "REDUNDANT" if max_score >= red_thresh else "NOVEL"
                evidence = {
                    "gdrive_hits": [
                        {"id": h.get("id"), "score": h.get("score"), "metadata": h.get("metadata", {})}
                        for h in hits
                    ],
                    "max_score": max_score,
                    "threshold": red_thresh,
                }
                if decision == "NOVEL":
                    continue  # will synthesize on next loop iteration
            except Exception as e:
                logger.warning("Rerun failed; stopping loop: %s", e)
                break

    ended = datetime.now(timezone.utc).isoformat()
    return {
        "decision": decision,
        "output": output,
        "loop_count": loop_count,
        "evidence": evidence,
        "started_at": started,
        "ended_at": ended,
        "topic": topic,
        "max_loops": max_loops,
        "conversation": conv,
    }

