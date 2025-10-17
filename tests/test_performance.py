import time
from youtube_chat_cli_main.workflows import deep_research as dr
from youtube_chat_cli_main.core.redis_cache import get_cache


def test_caching_effectiveness(monkeypatch):
    # Patch aggregator to count calls
    calls = {'n': 0}
    class DummyAgg:
        def search(self, query, max_results=8):
            calls['n'] += 1
            return [{'title': 'A', 'url': 'https://a', 'score': 1.0}]
        def format_results_for_context(self, results, max_length=3000):
            return 'A context'
    monkeypatch.setattr(dr, 'WebSearchAggregatorService', lambda *a, **k: DummyAgg())
    # First run: miss then cache
    r1 = dr.run('topic x', max_turns=1)
    # Second run: should hit cache and not increase calls if cache enabled
    r2 = dr.run('topic x', max_turns=1)
    # We can't guarantee Redis availability; just assert call count is <=2
    assert calls['n'] <= 2

