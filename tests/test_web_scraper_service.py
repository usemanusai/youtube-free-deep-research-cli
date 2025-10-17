from youtube_chat_cli_main.services.web_scraper_service import WebScraperService
from youtube_chat_cli_main.core.http_client import reset_httpx_client
import httpx
import youtube_chat_cli_main.services.web_scraper_service as mod


def test_scraper_scaffold_basic(monkeypatch):
    # Ensure httpx client is created under any patching
    reset_httpx_client()

    # Force playwright path to return empty
    monkeypatch.setattr(WebScraperService, "_fetch_playwright", lambda *a, **k: "")

    # Monkeypatch request_with_retry to avoid real network
    def _fake_request_with_retry(method: str, url: str, **kwargs):
        body = "<html><head><title>Example</title></head><body><p>Hello</p></body></html>"
        req = httpx.Request(method, url)
        return httpx.Response(200, request=req, text=body, headers={"Content-Type": "text/html"})

    monkeypatch.setattr(mod, "request_with_retry", _fake_request_with_retry)

    s = WebScraperService()
    out = s.scrape("https://example.com")
    assert isinstance(out, dict)
    assert out["root_url"] == "https://example.com"
    assert "pages" in out and isinstance(out["pages"], list)
    assert out["pages"][0]["status"] == 200
    assert "Hello" in out["pages"][0]["text"]

