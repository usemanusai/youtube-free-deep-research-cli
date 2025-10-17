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
    # Circuit breaker for LLM
    try:
        from ..core.circuit_health import get_breaker
        br = get_breaker("llm")
        if not br.allow():
            return "LLM_PLACEHOLDER"
    except Exception:
        br = None  # type: ignore
    try:
        from ..services.llm_service import get_llm_service  # lazy import
        llm = get_llm_service()
        out = llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=temperature)
        if br:
            br.on_success()
        return out
    except Exception as e:
        if br:
            br.on_failure()
        logger.warning("LLM unavailable for content-checks synthesis/refinement: %s", e)
        return ""


def _vector_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Vector search with Redis cache and graceful fallback."""
    cache_key = f"vector:{top_k}:{hash(query)}"
    try:
        from ..core.redis_cache import get_cache
        cache = get_cache()
        cached = cache.get_json(cache_key)
        if isinstance(cached, list):
            return cached
    except Exception:
        cached = None
    try:
        from ..services.vector_store import get_vector_store  # lazy import
        vs = get_vector_store()
        hits = vs.search(query=query, top_k=top_k, filter_dict={"source": "gdrive"}) or []
        try:
            from ..core.redis_cache import get_cache
            get_cache().set_json(cache_key, hits)
        except Exception:
            pass
        return hits
    except Exception as e:
        logger.warning("Vector store unavailable for duplicate check: %s", e)
        # Default NOVEL by returning no hits
        return []

# Optional LangGraph integration (lightweight wrapper)
try:
    from langgraph.graph import StateGraph, END  # type: ignore
    def _build_cc_graph():
        class CCState(dict):
            pass
        wf = StateGraph(CCState)
        def n_start(s: CCState) -> CCState:
            return s
        def n_route(s: CCState) -> CCState:
            return s
        wf.add_node("start", n_start)
        wf.add_node("route", n_route)
        wf.set_entry_point("start")
        wf.add_edge("start", "route")
        wf.add_edge("route", END)
        return wf.compile()
    _CC_GRAPH = _build_cc_graph()
except Exception:
    _CC_GRAPH = None

# LangGraph execution refactor with advanced duplicate scoring
try:
    from langgraph.graph import StateGraph, END  # type: ignore
    from typing import TypedDict

    class CCState(TypedDict, total=False):
        topic: str
        max_loops: int
        loop_count: int
        conv: dict
        insights: str
        decision: str
        evidence: dict
        output: dict
        citations: list
        started_at: str
        ended_at: str

    def _compute_duplicate_score(insights: str) -> tuple[float, list]:
        cfg = get_config()
        try:
            hits = _vector_search(insights, top_k=5)
        except Exception:
            hits = []
        half_life = getattr(cfg, 'duplicate_time_decay_half_life_days', 180)
        overlap_w = getattr(cfg, 'duplicate_citation_overlap_weight', 0.15)
        import math, datetime as _dt
        # max score with simple time-decay
        scores = []
        for h in hits:
            s = float(h.get('score', 0.0))
            meta = h.get('metadata', {}) or {}
            # time decay
            ts = meta.get('created_at') or meta.get('date')
            decay = 1.0
            try:
                if ts:
                    dt = _dt.datetime.fromisoformat(ts.replace('Z','+00:00'))
                    days = max(0.0, (_dt.datetime.now(_dt.timezone.utc) - dt.replace(tzinfo=_dt.timezone.utc)).days)
                    decay = 0.5 ** (days / float(max(1, half_life)))
            except Exception:
                pass
            scores.append(s * decay)
        base = max(scores) if scores else 0.0
        return base, hits

    def _citations_from_conv(conv: dict) -> list:
        cites = []
        try:
            for t in conv.get('transcript', []):
                for u in t.get('citations', []) or []:
                    if u and u not in cites:
                        cites.append(u)
        except Exception:
            pass
        return cites

    def _build_cc_graph2():
        wf = StateGraph(CCState)

        def _trace_if_debug(cid: str, stage: str, snapshot: dict):
            try:
                from ..core.config import get_config
                if not get_config().nexus_debug:
                    return
                from ..core.database import get_database
                get_database().add_workflow_trace(cid, 'content_checks', stage, snapshot)
            except Exception:
                pass

        def n_execute(state: CCState) -> CCState:
            import time, uuid
            t0 = time.time()
            cid = state.get('conv', {}).get('correlation_id') or state.get('correlation_id') or str(uuid.uuid4())
            started = datetime.now(timezone.utc).isoformat()
            conv = deep_research.run(state['topic'], max_turns=2)
            insights = "\n\n".join(t.get('content','') for t in conv.get('transcript', [])) or f"Topic: {state['topic']}"
            timings = {'execute_ms': int((time.time()-t0)*1000)}
            _trace_if_debug(cid, 'execute', {'t': timings['execute_ms']})
            return {**state, 'correlation_id': cid, 'conv': conv, 'insights': insights, 'started_at': started, 'citations': _citations_from_conv(conv), 'timings': timings}

        def n_duplicate_check(state: CCState) -> CCState:
            import time
            t0 = time.time()
            base, hits = _compute_duplicate_score(state.get('insights',''))
            cfg = get_config()
            red_thresh = getattr(cfg, 'duplicate_similarity_redundant', 0.85)
            decision = 'REDUNDANT' if base >= red_thresh else 'NOVEL'
            ev = {
                'gdrive_hits': [{'id': h.get('id'), 'score': h.get('score'), 'metadata': h.get('metadata', {})} for h in hits],
                'max_score': base,
                'threshold': red_thresh,
            }
            timings = dict(state.get('timings', {})); timings['duplicate_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'duplicate', {'max_score': base, 't': timings['duplicate_ms']})
            return {**state, 'decision': decision, 'evidence': ev, 'timings': timings}

        def n_synthesize(state: CCState) -> CCState:
            import time
            t0 = time.time()
            synthesis = _safe_llm_generate(
                prompt=("Synthesize the key findings into a concise brief with citations if present.\n\n" f"INSIGHTS:\n{state.get('insights','')}\n"),
                system_prompt=("You are a Synthesizer. Produce a succinct, high-signal brief."),
                temperature=0.4,
            ) or "SYNTHESIS_PLACEHOLDER"
            timings = dict(state.get('timings', {})); timings['synthesize_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'synthesize', {'t': timings['synthesize_ms']})
            return {**state, 'output': {'synthesis': synthesis}, 'timings': timings}

        def n_refine(state: CCState) -> CCState:
            import time
            t0 = time.time()
            refined = _safe_llm_generate(
                prompt=("Given the following insights appear redundant in the archive, propose a refined prompt to elicit novel angles and sources. Return only the refined prompt.\n\n" f"INSIGHTS:\n{state.get('insights','')}\n"),
                system_prompt=("You are a Prompt Engineer. Return just the improved prompt text."),
                temperature=0.6,
            ) or "REFINEMENT_PLACEHOLDER"
            try:
                rerun = deep_research.run(refined, max_turns=2)
                insights = "\n\n".join(t.get('content','') for t in rerun.get('transcript', [])) or refined
            except Exception:
                insights = refined
                rerun = {}
            loops = int(state.get('loop_count', 0)) + 1
            timings = dict(state.get('timings', {})); timings['refine_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'refine', {'loops': loops, 't': timings['refine_ms']})
            return {**state, 'output': {'refined_prompt': refined}, 'insights': insights, 'loop_count': loops, 'conv': rerun, 'timings': timings}

        def n_finalize(state: CCState) -> CCState:
            ended = datetime.now(timezone.utc).isoformat()
            _trace_if_debug(state.get('correlation_id',''), 'finalize', {})
            return {**state, 'ended_at': ended}

        wf.add_node('execute', n_execute)
        wf.add_node('duplicate', n_duplicate_check)
        wf.add_node('synthesize', n_synthesize)
        wf.add_node('refine', n_refine)
        wf.add_node('finalize', n_finalize)
        wf.set_entry_point('execute')
        wf.add_edge('execute', 'duplicate')

        def route(state: CCState):
            max_loops = int(state.get('max_loops', 1))
            loops = int(state.get('loop_count', 0))
            if state.get('decision') == 'NOVEL':
                return 'synthesize'
            if loops >= max_loops:
                return 'finalize'
            return 'refine'

        wf.add_conditional_edges('duplicate', route, {'synthesize': 'synthesize', 'refine': 'refine', 'finalize': 'finalize'})
        wf.add_edge('synthesize', 'finalize')
        wf.add_edge('refine', 'duplicate')
        wf.add_edge('finalize', END)
        return wf.compile()

    _CC_GRAPH = _build_cc_graph2()
except Exception:
    pass

def export_graph_mermaid() -> str:
    return """```mermaid\nflowchart TD\n    A[Execute Deep Research] --> B[Duplicate Check]\n    B --> C{NOVEL or REDUNDANT}\n    C -- NOVEL --> D[Synthesize] --> E[END]\n    C -- REDUNDANT --> F[Refine Prompt] --> A\n```"""

def run(topic: str, max_loops: Optional[int] = None) -> Dict[str, Any]:
    """Run the content checks workflow via compiled LangGraph."""
    logger.info("[ContentChecks] run called topic=%r", topic)
    loops = max_loops if (isinstance(max_loops, int) and max_loops > 0) else 1
    graph = _CC_GRAPH
    if graph is None:
        # Minimal fallback result
        now = datetime.now(timezone.utc).isoformat()
        return {
            'decision': 'NOVEL',
            'output': {'synthesis': ''},
            'loop_count': 0,
            'evidence': {'gdrive_hits': [], 'max_score': 0.0, 'threshold': getattr(get_config(), 'duplicate_similarity_redundant', 0.85)},
            'started_at': now,
            'ended_at': now,
            'topic': topic,
            'max_loops': loops,
            'conversation': {},
        }
    out = graph.invoke({'topic': topic, 'max_loops': loops})
    # Persist session (best-effort)
    try:
        import uuid
        from ..core.database import get_database
        db = get_database()
        session_id = str(uuid.uuid4())
        db.create_chat_session(session_id=session_id, name=f"content_checks:{topic[:32]}", metadata={
            'decision': out.get('decision'),
            'max_score': (out.get('evidence') or {}).get('max_score'),
        })
        tx = ((out.get('conv') or {}).get('transcript') or []) if isinstance(out.get('conv'), dict) else []
        for t in tx[:10]:
            db.add_chat_message(session_id=session_id, role=t.get('role','assistant'), content=t.get('content',''), metadata={})
    except Exception as e:
        logger.warning("Failed to persist content_checks session: %s", e)

    return {
        'decision': out.get('decision'),
        'output': out.get('output', {}),
        'loop_count': int(out.get('loop_count', 0)),
        'evidence': out.get('evidence', {}),
        'started_at': out.get('started_at'),
        'ended_at': out.get('ended_at'),
        'topic': topic,
        'max_loops': loops,
        'conversation': out.get('conv', {}),
    }

