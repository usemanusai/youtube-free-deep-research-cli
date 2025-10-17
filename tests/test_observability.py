import os
import json

def test_workflow_traces_are_recorded(monkeypatch):
    # Enable debug mode
    monkeypatch.setenv('NEXUS_DEBUG', 'true')
    from youtube_chat_cli_main.workflows import deep_research
    res = deep_research.run(topic="test topic", max_turns=1)
    cid = res.get('correlation_id')
    assert cid
    from youtube_chat_cli_main.core.database import get_database
    db = get_database()
    traces = db.get_workflow_traces(cid)
    assert isinstance(traces, list)
    assert any(t['stage'] == 'init' for t in traces)


def test_trace_api_and_cli(monkeypatch):
    monkeypatch.setenv('NEXUS_DEBUG', 'true')
    from youtube_chat_cli_main.workflows import deep_research
    res = deep_research.run(topic="another topic", max_turns=1)
    cid = res.get('correlation_id')

    # API
    from youtube_chat_cli_main.api.nexus_agents import get_workflow_trace
    import anyio
    async def _call():
        return await get_workflow_trace(workflow_id=cid)  # type: ignore
    out = anyio.run(_call)
    assert out.workflow_id == cid
    assert len(out.traces) >= 1

