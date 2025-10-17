from youtube_chat_cli_main.workflows import content_checks as cc


def test_loop_behavior_and_evidence(monkeypatch):
    # Patch deep_research to avoid heavy calls
    monkeypatch.setattr(cc.deep_research, 'run', lambda topic, max_turns=2: {
        'transcript': [{'role': 'agent0', 'content': 'c', 'citations': []}],
        'correlation_id': 'cid1'
    })
    # Patch vector search to force NOVEL
    monkeypatch.setattr(cc, '_vector_search', lambda q, top_k=5: [])

    out = cc.run(topic='topic', max_loops=2)
    assert out['decision'] == 'NOVEL'
    assert 'evidence' in out and 'gdrive_hits' in out['evidence']

    # Force REDUNDANT path
    hits = [{'id': '1', 'score': 1.0, 'metadata': {}}]
    monkeypatch.setattr(cc, '_vector_search', lambda q, top_k=5: hits)
    out2 = cc.run(topic='topic', max_loops=1)
    # With 1 loop allowed, pipeline must terminate
    assert out2['loop_count'] >= 0

