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



def test_content_checks_loop_rerun(monkeypatch):
    # Force REDUNDANT first, then NOVEL after rerun by patching vector search
    from youtube_chat_cli_main.workflows import content_checks as cc

    calls = {"n": 0}

    def fake_vs(query, top_k=5):
        calls["n"] += 1
        if calls["n"] == 1:
            return [{"id": "x", "score": 0.99, "metadata": {"source": "gdrive"}}]
        return []

    def fake_deep(topic, max_turns=None, backends=None):
        return {"transcript": [{"content": "new insights"}]}

    monkeypatch.setattr(cc, "_vector_search", fake_vs)
    monkeypatch.setattr(cc.deep_research, "run", fake_deep)

    out = cc.run(topic="t", max_loops=2)
    assert out["decision"] in ("NOVEL", "REDUNDANT")

