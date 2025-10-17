from youtube_chat_cli_main.workflows import content_checks as cc


def test_llm_fallback_placeholder(monkeypatch):
    class Boom:
        def generate(self, *a, **k):
            raise RuntimeError('down')
    monkeypatch.setattr(cc, '_safe_llm_generate', lambda *a, **k: '')
    out = cc.run(topic='t', max_loops=1)
    assert 'decision' in out

