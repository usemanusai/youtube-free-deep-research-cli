import pytest

from youtube_chat_cli_main.services.search_aggregator import WebSearchAggregatorService


def test_search_aggregator_scaffold_instantiation():
    svc = WebSearchAggregatorService()
    assert svc is not None


def test_search_aggregator_scaffold_search(monkeypatch):
    class Dummy:
        def search(self, query, max_results):
            return [{"title": "t", "url": "https://example.com", "content": "c", "score": 1.0}]

        def format_results_for_context(self, results, max_length=2000):
            return "OK"

    # Patch constructor call before instantiation so _legacy is our dummy
    monkeypatch.setattr(
        "youtube_chat_cli_main.services.search_aggregator.get_web_search_service",
        lambda: Dummy(),
    )

    svc = WebSearchAggregatorService(backends=["legacy"])  # avoid brave in tests
    # Ensure already-initialized legacy client is our Dummy
    assert hasattr(svc, "_legacy")

    results = svc.search("hello", 3)
    assert isinstance(results, list)
    assert results and "url" in results[0]

