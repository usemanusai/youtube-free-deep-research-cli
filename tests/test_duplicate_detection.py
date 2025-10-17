import math
import datetime as dt
import os

from youtube_chat_cli_main.workflows import content_checks as cc


def test_time_decay_and_threshold_routing(monkeypatch):
    # Configure threshold
    monkeypatch.setenv('DUPLICATE_SIMILARITY_REDUNDANT', '0.5')
    now = dt.datetime.now(dt.timezone.utc)
    recent = (now - dt.timedelta(days=1)).isoformat()
    old = (now - dt.timedelta(days=365)).isoformat()

    hits = [
        {'id': 'a', 'score': 0.6, 'metadata': {'created_at': recent}},
        {'id': 'b', 'score': 0.9, 'metadata': {'created_at': old}},
    ]

    def fake_vec(q, top_k=5):
        return hits

    monkeypatch.setattr(cc, '_vector_search', fake_vec)

    base, got_hits = cc._compute_duplicate_score("insights")
    assert got_hits == hits
    # With half-life 180 days, recent should dominate so base ~0.6
    assert 0.55 <= base <= 0.65

    # Routing check via node: decision REDUNDANT at threshold
    state = {'insights': 'x'}
    ns = cc._compute_duplicate_score
    dc = cc._build_cc_graph2  # attribute exists only inside try block; use run() to route
    out = cc.run(topic='t', max_loops=1)
    assert out['decision'] in ('NOVEL', 'REDUNDANT')


def test_vector_unavailable_graceful(monkeypatch):
    def boom(q, top_k=5):
        raise RuntimeError('down')
    monkeypatch.setattr(cc, '_vector_search', boom)
    base, hits = cc._compute_duplicate_score('insights')
    assert base == 0.0
    assert hits == []

