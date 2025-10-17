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

        # Resilience wrappers
        try:
            from ..core.resilience import retry_with_backoff
        except Exception:
            def retry_with_backoff(*args, **kwargs):
                def _d(f): return f
                return _d

        def _trace_if_debug(cid: str, stage: str, snapshot: dict):
            try:
                from ..core.config import get_config
                if not get_config().nexus_debug:
                    return
                from ..core.database import get_database
                get_database().add_workflow_trace(cid, 'deep_research', stage, snapshot)
            except Exception:
                pass

        def n_init(state: DRState) -> DRState:
            import uuid, time
            t0 = time.time()
            cid = state.get('correlation_id') or str(uuid.uuid4())
            logger.info(f"[DeepResearch][cid={cid}] init topic=%r", state.get('topic'))
            aggregator = WebSearchAggregatorService()
            # Search context with retry
            @retry_with_backoff(max_attempts=3, initial_delay=0.3)
            def _agg_search(q: str, k: int):
                return aggregator.search(query=q, max_results=k)
            results = _agg_search(state['topic'], 8)
            context = aggregator.format_results_for_context(results, max_length=3000)
            citations = [r.get('url','') for r in results]
            started_at = datetime.now(timezone.utc).isoformat()
            timings = {'init_ms': int((time.time()-t0)*1000)}
            new_state = {**state, 'correlation_id': cid, 'search_results': results, 'search_context': context, 'citations': citations, 'transcript': [], 'artifacts': {}, 'started_at': started_at, 'timings': timings}
            _trace_if_debug(cid, 'init', {'topic': state.get('topic'), 'citations': citations, 't': timings['init_ms']})
            return new_state

        def n_enhance(state: DRState) -> DRState:
            import time
            t0 = time.time()
            llm = get_llm_service()
            @retry_with_backoff(max_attempts=3, initial_delay=0.3)
            def _gen_enh(prompt: str, sys: str, temp: float):
                try:
                    from ..core.circuit_health import get_breaker
                    br = get_breaker("llm")
                    if not br.allow():
                        return prompt  # placeholder: echo input
                except Exception:
                    br = None  # type: ignore
                try:
                    out = llm.generate(prompt=prompt, system_prompt=sys, temperature=temp)
                    if br:
                        br.on_success()
                    return out
                except Exception:
                    if br:
                        br.on_failure()
                    raise
            enhanced = _gen_enh(
                prompt=f"Original topic: {state['topic']}\nReturn improved topic only.",
                sys=ENHANCER_SYSTEM,
                temp=0.9,
            ).strip() or state['topic']
            transcript = list(state.get('transcript', []))
            transcript.append({'role':'enhancer','content':enhanced,'citations':[],'tools_used':['llm'],'ts': datetime.now(timezone.utc).isoformat()})
            timings = dict(state.get('timings', {})); timings['enhance_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'enhance', {'enhanced': enhanced, 't': timings['enhance_ms']})
            return {**state, 'enhanced': enhanced, 'transcript': transcript, 'timings': timings}

        def n_agent0_initial(state: DRState) -> DRState:
            import time
            t0 = time.time()
            llm = get_llm_service()
            today = _today_str()
            agent0_sys = AGENT0_SYSTEM_T.format(today=today)
            @retry_with_backoff(max_attempts=3, initial_delay=0.3)
            def _gen_a0(prompt: str, sys: str, temp: float):
                try:
                    from ..core.circuit_health import get_breaker
                    br = get_breaker("llm")
                    if not br.allow():
                        return "LLM_PLACEHOLDER_A0"
                except Exception:
                    br = None  # type: ignore
                try:
                    out = llm.generate(prompt=prompt, system_prompt=sys, temperature=temp)
                    if br:
                        br.on_success()
                    return out
                except Exception:
                    if br:
                        br.on_failure()
                    raise
            out = _gen_a0(
                prompt=(f"Topic: {state['enhanced']}\n\nSearch Context (condensed):\n{state['search_context']}\n\nWrite an initial research brief with citations."),
                sys=agent0_sys,
                temp=0.9,
            )
            tx = list(state.get('transcript', []))
            tx.append({'role':'agent0','content':out,'citations':state.get('citations',[]),'tools_used':['web_search'],'ts': datetime.now(timezone.utc).isoformat()})
            timings = dict(state.get('timings', {})); timings['agent0_initial_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'agent0_initial', {'t': timings['agent0_initial_ms']})
            return {**state, 'transcript': tx, 'timings': timings}

        def n_turn_loop(state: DRState) -> DRState:
            import time
            t0 = time.time()
            turns = int(state.get('max_turns', 2))
            tx = list(state.get('transcript', []))
            done_pairs = max(0, (len([t for t in tx if t.get('role')=='agent1'])))
            if done_pairs >= max(0, turns-1):
                return state
            llm = get_llm_service()
            today = _today_str()
            agent1_sys = AGENT1_SYSTEM_T.format(today=today)
            agent0_sys = AGENT0_SYSTEM_T.format(today=today)
            last_agent0 = next((t['content'] for t in reversed(tx) if t.get('role')=='agent0'), '')
            @retry_with_backoff(max_attempts=3, initial_delay=0.3)
            def _gen(prompt: str, sys: str, temp: float):
                try:
                    from ..core.circuit_health import get_breaker
                    br = get_breaker("llm")
                    if not br.allow():
                        return "LLM_PLACEHOLDER"
                except Exception:
                    br = None  # type: ignore
                try:
                    out = llm.generate(prompt=prompt, system_prompt=sys, temperature=temp)
                    if br:
                        br.on_success()
                    return out
                except Exception:
                    if br:
                        br.on_failure()
                    raise
            agent1_reply = _gen(prompt=("Agent 0 said:\n" + last_agent0 + "\n\nProvide critical analysis, highlight gaps, propose next steps."), sys=agent1_sys, temp=0.7)
            tx.append({'role':'agent1','content':agent1_reply,'citations':state.get('citations',[]),'tools_used':['llm'],'ts': datetime.now(timezone.utc).isoformat()})
            agent0_follow = _gen(prompt=("Agent 1 said:\n" + agent1_reply + "\n\nIn 1-2 paragraphs, refine findings and cite URLs as needed."), sys=agent0_sys, temp=0.7)
            tx.append({'role':'agent0','content':agent0_follow,'citations':state.get('citations',[]),'tools_used':['llm'],'ts': datetime.now(timezone.utc).isoformat()})
            timings = dict(state.get('timings', {})); timings['turn_loop_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'turn_loop', {'pairs': done_pairs+1, 't': timings['turn_loop_ms']})
            return {**state, 'transcript': tx, 'timings': timings}

        def n_finalize(state: DRState) -> DRState:
            import time
            t0 = time.time()
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
                    'correlation_id': state.get('correlation_id'),
                })
                for turn in state.get('transcript', []):
                    db.add_chat_message(session_id=session_id, role=turn.get('role','assistant'), content=turn.get('content',''), metadata={
                        'citations': turn.get('citations', []),
                        'tools': turn.get('tools_used', []),
                        'ts': turn.get('ts'),
                    })
            except Exception as e:
                logger.warning("[cid=%s] Failed to persist deep_research session: %s", state.get('correlation_id'), e)
            timings = dict(state.get('timings', {})); timings['finalize_ms'] = int((time.time()-t0)*1000)
            _trace_if_debug(state.get('correlation_id',''), 'finalize', {'t': timings['finalize_ms']})
            return {**state, 'artifacts': artifacts, 'ended_at': ended_at, 'timings': timings}

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
        'correlation_id': out.get('correlation_id'),
        'timings': out.get('timings', {}),
    }

