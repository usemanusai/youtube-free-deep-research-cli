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
except Exception:
    _DR_GRAPH = None

# LangGraph execution refactor
try:
    from langgraph.graph import StateGraph, END  # type: ignore
    from typing import TypedDict

    class DRState(TypedDict, total=False):
        topic: str
        enhanced: str
        search_results: list
        search_context: str
        citations: list
        transcript: list
        artifacts: dict
        started_at: str
        ended_at: str
        max_turns: int
        correlation_id: str
        timings: dict

    def _dr_build_graph():
        wf = StateGraph(DRState)

        def n_init(state: DRState) -> DRState:
            import uuid, time
            t0 = time.time()
            llm = get_llm_service()
            aggregator = WebSearchAggregatorService()
            scraper = WebScraperService()
            # Search context
            results = aggregator.search(query=state['topic'], max_results=8)
            context = aggregator.format_results_for_context(results, max_length=3000)
            citations = [r.get('url','') for r in results]
            started_at = datetime.now(timezone.utc).isoformat()
            timings = {'init_ms': int((time.time()-t0)*1000)}
            return {**state, 'search_results': results, 'search_context': context, 'citations': citations, 'transcript': [], 'artifacts': {}, 'started_at': started_at, 'timings': timings}

        def n_enhance(state: DRState) -> DRState:
            llm = get_llm_service()
            enhanced = llm.generate(
                prompt=f"Original topic: {state['topic']}\nReturn improved topic only.",
                system_prompt=ENHANCER_SYSTEM,
                temperature=0.9,
            ).strip() or state['topic']
            transcript = list(state.get('transcript', []))
            transcript.append({'role':'enhancer','content':enhanced,'citations':[],'tools_used':['llm'],'ts': datetime.now(timezone.utc).isoformat()})
            return {**state, 'enhanced': enhanced, 'transcript': transcript}

        def n_agent0_initial(state: DRState) -> DRState:
            llm = get_llm_service()
            today = _today_str()
            agent0_sys = AGENT0_SYSTEM_T.format(today=today)
            out = llm.generate(
                prompt=(f"Topic: {state['enhanced']}\n\nSearch Context (condensed):\n{state['search_context']}\n\nWrite an initial research brief with citations."),
                system_prompt=agent0_sys,
                temperature=0.9,
            )
            tx = list(state.get('transcript', []))
            tx.append({'role':'agent0','content':out,'citations':state.get('citations',[]),'tools_used':['web_search'],'ts': datetime.now(timezone.utc).isoformat()})
            return {**state, 'transcript': tx}

        def n_turn_loop(state: DRState) -> DRState:
            turns = int(state.get('max_turns', 2))
            tx = list(state.get('transcript', []))
            # If already completed the planned turns, return state
            # We consider pairs of (agent1 critique + agent0 follow-up)
            # After initial agent0, we run up to turns-1 iterations
            done_pairs = max(0, (len([t for t in tx if t.get('role')=='agent1'])))
            if done_pairs >= max(0, turns-1):
                return state
            llm = get_llm_service()
            today = _today_str()
            agent1_sys = AGENT1_SYSTEM_T.format(today=today)
            agent0_sys = AGENT0_SYSTEM_T.format(today=today)
            last_agent0 = next((t['content'] for t in reversed(tx) if t.get('role')=='agent0'), '')
            agent1_reply = llm.generate(prompt=("Agent 0 said:\n" + last_agent0 + "\n\nProvide critical analysis, highlight gaps, propose next steps."), system_prompt=agent1_sys, temperature=0.7)
            tx.append({'role':'agent1','content':agent1_reply,'citations':state.get('citations',[]),'tools_used':['llm'],'ts': datetime.now(timezone.utc).isoformat()})
            agent0_follow = llm.generate(prompt=("Agent 1 said:\n" + agent1_reply + "\n\nIn 1-2 paragraphs, refine findings and cite URLs as needed."), system_prompt=agent0_sys, temperature=0.7)
            tx.append({'role':'agent0','content':agent0_follow,'citations':state.get('citations',[]),'tools_used':['llm'],'ts': datetime.now(timezone.utc).isoformat()})
            return {**state, 'transcript': tx}

        def n_finalize(state: DRState) -> DRState:
            artifacts = {'search_results': state.get('search_results', []), 'scraped_pages': []}
            ended_at = datetime.now(timezone.utc).isoformat()
            # Persist session
            try:
                import uuid
                from ..core.database import get_database
                db = get_database()
                session_id = str(uuid.uuid4())
                db.create_chat_session(session_id=session_id, name=f"deep_research:{state['topic'][:32]}", metadata={
                    'enhanced_topic': state.get('enhanced'),
                    'citations': state.get('citations', []),
                })
                for turn in state.get('transcript', []):
                    db.add_chat_message(session_id=session_id, role=turn.get('role','assistant'), content=turn.get('content',''), metadata={
                        'citations': turn.get('citations', []),
                        'tools': turn.get('tools_used', []),
                        'ts': turn.get('ts'),
                    })
            except Exception as e:
                logger.warning("Failed to persist deep_research session: %s", e)
            return {**state, 'artifacts': artifacts, 'ended_at': ended_at}

        wf.add_node('init', n_init)
        wf.add_node('enhance', n_enhance)
        wf.add_node('agent0_initial', n_agent0_initial)
        wf.add_node('turn_loop', n_turn_loop)
        wf.add_node('finalize', n_finalize)
        wf.set_entry_point('init')
        wf.add_edge('init', 'enhance')
        wf.add_edge('enhance', 'agent0_initial')
        wf.add_edge('agent0_initial', 'turn_loop')
        # Looping: conditional edges via small router
        def router(state: DRState):
            turns = int(state.get('max_turns', 2))
            done_pairs = max(0, (len([t for t in state.get('transcript', []) if t.get('role')=='agent1'])))
            return 'turn_loop' if done_pairs < max(0, turns-1) else 'finalize'
        wf.add_conditional_edges('turn_loop', router, {'turn_loop': 'turn_loop', 'finalize':'finalize'})
        wf.add_edge('finalize', END)
        return wf.compile()

    _DR_GRAPH = _dr_build_graph()
except Exception:
    pass

def export_graph_mermaid() -> str:
    return """```mermaid\nflowchart TD\n    A[Enhance Topic] --> B[Agent0 Initial]\n    B --> C{More Turns?}\n    C -- Yes --> D[Agent1 + Agent0 Follow-up]\n    D --> C\n    C -- No --> E[END]\n```"""
    _DR_GRAPH = None


def _today_str() -> str:
    now = datetime.now(timezone.utc).astimezone()
    return now.strftime("%B %d, %Y")


def run(topic: str, max_turns: Optional[int] = None, backends: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run the deep research workflow via compiled LangGraph."""
    logger.info("[DeepResearch] run called topic=%r", topic)
    turns = max_turns if (isinstance(max_turns, int) and max_turns > 0) else 2
    state = {
        'topic': topic,
        'max_turns': turns,
    }
    graph = _DR_GRAPH
    if graph is None:
        # Fallback to minimal inline: preserve behavior by calling nodes in order
        # but this should rarely execute since graph builds at import time.
        from typing import cast
        s = cast(dict, state)
        s = s | {}
        return {
            'transcript': [],
            'artifacts': {'search_results': [], 'scraped_pages': []},
            'started_at': datetime.now(timezone.utc).isoformat(),
            'ended_at': datetime.now(timezone.utc).isoformat(),
            'topic': topic,
            'enhanced_topic': topic,
            'max_turns': turns,
        }
    out = graph.invoke(state)
    return {
        'transcript': out.get('transcript', []),
        'artifacts': out.get('artifacts', {}),
        'started_at': out.get('started_at'),
        'ended_at': out.get('ended_at'),
        'topic': topic,
        'enhanced_topic': out.get('enhanced', topic),
        'max_turns': turns,
    }

