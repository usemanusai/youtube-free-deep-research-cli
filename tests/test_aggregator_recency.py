from youtube_chat_cli_main.services.search_aggregator import WebSearchAggregatorService


def test_aggregator_recency_bonus(monkeypatch):
    aggr = WebSearchAggregatorService(backends=["legacy"])  # single backend for determinism

    def fake_call_backend(name, query, max_results):
        assert name == "legacy"
        return [
            {"title": "Old", "url": "https://ex.com/a", "content": "", "score": 1.0, "backend": "legacy", "published": "2023-01-01T00:00:00+00:00"},
            {"title": "New", "url": "https://ex.com/b", "content": "", "score": 1.0, "backend": "legacy", "published": "2025-01-01T00:00:00+00:00"},
        ]

    monkeypatch.setattr(WebSearchAggregatorService, "_call_backend", staticmethod(fake_call_backend))

    out = aggr.search("q", max_results=2)
    assert len(out) == 2
    # Expect "New" comes before "Old" due to recency bonus
    assert out[0]["title"] == "New"

