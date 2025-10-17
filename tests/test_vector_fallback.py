from youtube_chat_cli_main.workflows import content_checks as cc


def test_vector_fallback_defaults_to_novel(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError('vec down')
    monkeypatch.setattr(cc, '_vector_search', boom)
    out = cc.run(topic='t', max_loops=1)
    assert out['decision'] == 'NOVEL'

