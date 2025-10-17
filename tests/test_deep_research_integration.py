import json
from youtube_chat_cli_main.workflows import deep_research as dr


class DummyLLM:
    def generate(self, prompt: str, system_prompt=None, temperature=0.0, max_tokens=None):
        # Return short deterministic outputs
        if 'Return improved topic only' in prompt:
            return 'Improved Topic'
        return 'LLM OUT'


def test_deep_research_e2e_monkeypatched(monkeypatch):
    # Patch LLM
    monkeypatch.setattr(dr, 'get_llm_service', lambda: DummyLLM())

    # Patch search aggregator
    class DummyAgg:
        def search(self, query, max_results=8):
            return [
                {'title': 'A', 'url': 'https://x/y', 'score': 1.0},
                {'title': 'B', 'url': 'https://z/w', 'score': 0.9},
            ]
        def format_results_for_context(self, results, max_length=3000):
            return '\n'.join([r['title'] for r in results])
    monkeypatch.setattr(dr, 'WebSearchAggregatorService', lambda *a, **k: DummyAgg())

    res = dr.run(topic='t', max_turns=2)
    assert 'correlation_id' in res
    assert isinstance(res['timings'], dict)
    assert res['enhanced_topic'] in ('Improved Topic', 't')
    assert res['artifacts'] is not None

