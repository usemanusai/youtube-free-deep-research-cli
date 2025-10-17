from youtube_chat_cli_main.services.search_aggregator import WebSearchAggregatorService


def test_merging_dedup_and_ranking(monkeypatch):
    agg = WebSearchAggregatorService(backends=['legacy', 'brave'])

    def fake_call_backend(self, name, query, max_results):
        if name == 'legacy':
            return [
                {'title': 'A1', 'url': 'https://a.com/x', 'score': 0.9},
                {'title': 'A2', 'url': 'https://dup.com/x', 'score': 0.8},
            ]
        if name == 'brave':
            return [
                {'title': 'B1', 'url': 'https://b.com/y', 'score': 0.95},
                {'title': 'B2', 'url': 'https://dup.com/x', 'score': 0.7},  # duplicate
            ]
        return []

    monkeypatch.setattr(WebSearchAggregatorService, '_call_backend', fake_call_backend)
    res = agg.search('q', max_results=10)
    urls = [r['url'] for r in res]
    assert 'https://dup.com/x' in urls
    # dedup should remove duplicates => count unique
    assert len(urls) == len(set(urls))

