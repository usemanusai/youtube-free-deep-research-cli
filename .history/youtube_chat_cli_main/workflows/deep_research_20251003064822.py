"""
Deep Research Workflow (initial implementation)

Topic Enhancer + Agent 0 / Agent 1 cooperative conversation loop using
LLMService + WebSearchAggregatorService + WebScraperService.

Notes:
- Preserves model configuration via existing LLMService config (OpenRouter/Ollama)
- Injects current date into system prompts
- Uses hybrid search aggregator (Brave + legacy) and formats context for agents
- Scraper is scaffolded; pages not fetched by default to avoid external calls
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime, timezone
import logging

from ..services.llm_service import get_llm_service
from ..services.search_aggregator import WebSearchAggregatorService
from ..services.web_scraper_service import WebScraperService

logger = logging.getLogger(__name__)


class Turn(TypedDict, total=False):
    role: str  # enhancer | agent0 | agent1
    content: str
    citations: List[str]
    tools_used: List[str]
    ts: str


ENHANCER_SYSTEM = (
    "You are a Topic Enhancer. Improve and focus the user's topic for high-yield,\n"
    "diverse, current searches. Return a concise, enhanced topic/query.\n"
)

AGENT0_SYSTEM_T = (
    "You are Agent 0 (Researcher). Explore the topic in depth with Agent 1.\n"
    "Use the search context and cite URLs inline when relevant.\n"
    "TODAY'S DATE: {today}\n"
)

AGENT1_SYSTEM_T = (
    "You are Agent 1 (Analyst). Critically analyze Agent 0's findings.\n"
    "Identify gaps, biases, and propose next steps with citations if helpful.\n"
    "TODAY'S DATE: {today}\n"
)

# Optional LangGraph integration (lightweight wrapper)
try:
    from langgraph.graph import StateGraph, END  # type: ignore
    def _build_graph():
        class GState(TypedDict, total=False):
            topic: str
            enhanced: str
            transcript: List[Turn]
            artifacts: Dict[str, Any]
        wf = StateGraph(GState)
        def n_enhance(state: GState) -> GState:
            return state  # enhancement occurs in run() to keep parity
        def n_converse(state: GState) -> GState:
            return state  # conversation occurs in run() to keep parity
        wf.add_node("enhance", n_enhance)
        wf.add_node("converse", n_converse)
        wf.set_entry_point("enhance")
        wf.add_edge("enhance", "converse")
        wf.add_edge("converse", END)
        return wf.compile()
    _DR_GRAPH = _build_graph()
except Exception:
def export_graph_mermaid() -> str:
    return """```mermaid\nflowchart TD\n    A[Enhance Topic] --> B[Agent0 Initial]\n    B --> C{More Turns?}\n    C -- Yes --> D[Agent1 + Agent0 Follow-up]\n    D --> C\n    C -- No --> E[END]\n```"""
    _DR_GRAPH = None


def _today_str() -> str:
    now = datetime.now(timezone.utc).astimezone()
    return now.strftime("%B %d, %Y")


def run(topic: str, max_turns: Optional[int] = None, backends: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run the deep research workflow.

    Args:
        topic: initial topic
        max_turns: maximum number of back-and-forth turns (default small number if None)
        backends: optional search backends override

    Returns:
        dict with keys: transcript, artifacts, started_at, ended_at
    """
    logger.info("[DeepResearch] run called topic=%r", topic)
    started = datetime.now(timezone.utc).isoformat()

    # Initialize services
    llm = get_llm_service()
    aggregator = WebSearchAggregatorService(backends=backends)
    scraper = WebScraperService()

    # Search context
    search_results = aggregator.search(query=topic, max_results=8)
    search_context = aggregator.format_results_for_context(search_results, max_length=3000)
    citations = [r.get("url", "") for r in search_results]

    # Topic enhancement
    enhanced = llm.generate(
        prompt=f"Original topic: {topic}\nReturn improved topic only.",
        system_prompt=ENHANCER_SYSTEM,
        temperature=0.9,
    ).strip()
    if not enhanced:
        enhanced = topic

    transcript: List[Turn] = [
        {
            "role": "enhancer",
            "content": enhanced,
            "citations": [],
            "tools_used": ["llm"],
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    ]

    # Agent conversation loop
    today = _today_str()
    agent0_sys = AGENT0_SYSTEM_T.format(today=today)
    agent1_sys = AGENT1_SYSTEM_T.format(today=today)

    # Keep the loop bounded (default 2 alternating turns)
    turns = max_turns if (isinstance(max_turns, int) and max_turns > 0) else 2

    last_agent0 = llm.generate(
        prompt=(
            f"Topic: {enhanced}\n\nSearch Context (condensed):\n{search_context}\n\n"
            "Write an initial research brief with citations."
        ),
        system_prompt=agent0_sys,
        temperature=0.9,
    )
    transcript.append({
        "role": "agent0",
        "content": last_agent0,
        "citations": citations,
        "tools_used": ["web_search"],
        "ts": datetime.now(timezone.utc).isoformat(),
    })

    for i in range(1, turns):
        # Agent 1 critique
        agent1_reply = llm.generate(
            prompt=(
                "Agent 0 said:\n" + last_agent0 + "\n\n"
                "Provide critical analysis, highlight gaps, propose next steps."
            ),
            system_prompt=agent1_sys,
            temperature=0.7,
        )
        transcript.append({
            "role": "agent1",
            "content": agent1_reply,
            "citations": citations,
            "tools_used": ["llm"],
            "ts": datetime.now(timezone.utc).isoformat(),
        })

        # Agent 0 follow-up (lightweight to keep bounded)
        last_agent0 = llm.generate(
            prompt=(
                "Agent 1 said:\n" + agent1_reply + "\n\n"
                "In 1-2 paragraphs, refine findings and cite URLs as needed."
            ),
            system_prompt=agent0_sys,
            temperature=0.7,
        )
        transcript.append({
            "role": "agent0",
            "content": last_agent0,
            "citations": citations,
            "tools_used": ["llm"],
            "ts": datetime.now(timezone.utc).isoformat(),
        })

    # Artifacts (scraping disabled by default to avoid external calls)
    artifacts: Dict[str, Any] = {
        "search_results": search_results,
        "scraped_pages": [],  # placeholder until scraper is enabled
    }

    # Persist session and messages
    try:
        import uuid
        from ..core.database import get_database
        db = get_database()
        session_id = str(uuid.uuid4())
        db.create_chat_session(session_id=session_id, name=f"deep_research:{topic[:32]}", metadata={
            "enhanced_topic": enhanced,
            "citations": citations,
        })
        for turn in transcript:
            db.add_chat_message(session_id=session_id, role=turn.get("role","assistant"), content=turn.get("content",""), metadata={
                "citations": turn.get("citations", []),
                "tools": turn.get("tools_used", []),
                "ts": turn.get("ts"),
            })
    except Exception as e:
        logger.warning("Failed to persist deep_research session: %s", e)

    ended = datetime.now(timezone.utc).isoformat()
    return {
        "transcript": transcript,
        "artifacts": artifacts,
        "started_at": started,
        "ended_at": ended,
        "topic": topic,
        "enhanced_topic": enhanced,
        "max_turns": turns,
    }

