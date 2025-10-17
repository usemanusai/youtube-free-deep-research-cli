from youtube_chat_cli_main.workflows import deep_research as dr, content_checks as cc


def test_empty_and_long_topics():
    out1 = dr.run(topic='', max_turns=1)
    assert 'transcript' in out1
    long = 'x' * 2000
    out2 = cc.run(topic=long, max_loops=1)
    assert 'decision' in out2

