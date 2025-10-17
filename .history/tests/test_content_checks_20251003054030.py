import pytest

from youtube_chat_cli_main.workflows import content_checks


def test_content_checks_scaffold_run(monkeypatch):
    # Avoid real LLM calls via deep_research by mocking it
    from youtube_chat_cli_main.workflows import deep_research

    def fake_run(topic, max_turns=None, backends=None):
        return {"transcript": [], "artifacts": {}, "topic": topic}

    monkeypatch.setattr(deep_research, "run", fake_run)

    out = content_checks.run(topic="Test Topic", max_loops=2)
    assert isinstance(out, dict)
    assert out["decision"] in ("NOVEL", "REDUNDANT")

