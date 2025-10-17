import pytest
from youtube_chat_cli_main.services.search_aggregator import WebSearchAggregatorService


def test_aggregator_merges_and_dedupes(monkeypatch):
    agg = WebSearchAggregatorService(backends=["brave", "legacy"])  # force order

    def fake_call_backend(name, query, max_results):
        if name == "brave":
            return [
                {"title": "A", "url": "https://a.com/path", "content": "a", "score": 1.0, "backend": "brave"},
                {"title": "B", "url": "https://b.com", "content": "b", "score": 0.9, "backend": "brave"},
            ]
        if name == "legacy":
            # Duplicate of https://a.com/path with query params; should dedupe to 1 entry
            return [
                {"title": "A2", "url": "https://a.com/path?ref=dup", "content": "a2", "score": 0.5, "backend": "legacy"},
                {"title": "C", "url": "https://c.com", "content": "c", "score": 0.8, "backend": "legacy"},
            ]
        return []

    monkeypatch.setattr(agg, "_call_backend", fake_call_backend)

    out = agg.search("q", max_results=10)
    urls = [r["url"] for r in out]

    # Expect 3 unique URLs (a.com/path deduped), order by weighted score
    assert len(out) == 3
    assert "https://a.com/path" in urls or any(u.startswith("https://a.com/path") for u in urls)
    assert set(urls) >= {"https://b.com", "https://c.com"}


def test_aggregator_scoring_recency(monkeypatch):
    agg = WebSearchAggregatorService(backends=["brave"])  # single backend to isolate scoring

    recent = {"title": "R", "url": "https://recent.com", "content": "r", "score": 1.0, "backend": "brave", "published": "2099-01-01T00:00:00Z"}
    old = {"title": "O", "url": "https://old.com", "content": "o", "score": 1.0, "backend": "brave", "published": "2000-01-01T00:00:00Z"}

    def fake_call_backend(name, query, max_results):
        return [old, recent]

    monkeypatch.setattr(agg, "_call_backend", fake_call_backend)

    out = agg.search("q", max_results=2)
    # Recent should score slightly higher due to recency bonus
    assert out[0]["url"].endswith("recent.com")

