import os
from youtube_chat_cli_main.core.config import get_config

def test_config_new_keys_defaults(monkeypatch):
    monkeypatch.delenv('BRAVE_API_KEY', raising=False)
    monkeypatch.setenv('SEARCH_BACKENDS', 'brave,legacy')
    monkeypatch.delenv('SCRAPER_RATE_LIMIT_QPS', raising=False)
    cfg = get_config(reload=True)

    assert isinstance(cfg.search_backends, list)
    assert 'brave' in cfg.search_backends
    assert cfg.scraper_depth >= 1
    assert cfg.scraper_max_pages >= 1
    assert cfg.scraper_timeout_s >= 5
    assert cfg.scraper_headless in (True, False)
    assert isinstance(cfg.scraper_user_agent, str)
    assert cfg.scraper_rate_limit_qps > 0
    assert 0 < cfg.duplicate_similarity_overlap < 1
    assert 0 < cfg.duplicate_similarity_redundant <= 1
    assert cfg.nexus_max_turns >= 1
    assert cfg.nexus_max_loops >= 1

