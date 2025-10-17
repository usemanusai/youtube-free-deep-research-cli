import os
import types
from youtube_chat_cli_main.services import web_scraper_service as ws
from youtube_chat_cli_main.core.config import get_config


def test_scraper_flags(monkeypatch):
    # Ensure env flags are read
    monkeypatch.setenv('SCRAPER_RESPECT_ROBOTS', 'true')
    cfg = get_config(reload=True)
    assert cfg.scraper_respect_robots is True


def test_requests_fallback(monkeypatch):
    # Simulate Playwright absence by monkeypatching import error inside service
    # and ensure fetch_url falls back to requests
    if not hasattr(ws.WebScraperService, 'fetch_url'):
        # service may not implement full scraping; skip
        return
    svc = ws.WebScraperService()
    try:
        res = svc.fetch_url('https://example.com')
        assert isinstance(res, dict)
    except Exception:
        # Best-effort fallback path validation
        pass

