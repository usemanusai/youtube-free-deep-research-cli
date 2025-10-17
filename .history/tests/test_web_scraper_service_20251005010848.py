import pytest

from youtube_chat_cli_main.services.web_scraper_service import WebScraperService


def test_scraper_scaffold_basic(respx_mock):
    # Mock example.com to avoid real network (httpx-based)
    respx_mock.get("https://example.com/").respond(
        status_code=200,
        content=b"<html><head><title>Example</title></head><body><p>Hello</p></body></html>",
        headers={"Content-Type": "text/html"},
    )
    respx_mock.get("https://example.com").respond(
        status_code=200,
        content=b"<html><head><title>Example</title></head><body><p>Hello</p></body></html>",
        headers={"Content-Type": "text/html"},
    )

    s = WebScraperService()
    out = s.scrape("https://example.com")
    assert isinstance(out, dict)
    assert out["root_url"] == "https://example.com"
    assert "pages" in out and isinstance(out["pages"], list)
    assert out["pages"][0]["status"] == 200
    assert "Hello" in out["pages"][0]["text"]

