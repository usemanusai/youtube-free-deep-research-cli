import pytest

from youtube_chat_cli_main.services.web_scraper_service import WebScraperService


def test_scraper_scaffold_basic():
    s = WebScraperService()
    out = s.scrape("https://example.com")
    assert isinstance(out, dict)
    assert out["root_url"] == "https://example.com"
    assert "pages" in out and isinstance(out["pages"], list)

