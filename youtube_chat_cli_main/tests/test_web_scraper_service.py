import types
import pytest

from youtube_chat_cli_main.services.web_scraper_service import WebScraperService


class DummyResp:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        self.ok = status_code == 200


def test_scrape_uses_requests_when_playwright_unavailable(monkeypatch):
    svc = WebScraperService(rate_limit_qps=100.0)

    # Force playwright path to return empty string
    monkeypatch.setattr(svc, "_fetch_playwright", lambda url, timeout_s: "")

    # Mock requests.get to return deterministic HTML
    def fake_get(url, timeout, headers):
        return DummyResp("""
            <html><head><title>T</title></head>
            <body>
                <h1>Hello</h1>
                <a href=\"/sub\">Sub</a>
                <script>var x=1</script>
            </body>
            </html>
        """)

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    out = svc.scrape("https://example.com", depth=1, max_pages=5, timeout_s=5)

    assert out["root_url"] == "https://example.com"
    assert out["pages"][0]["status"] == 200
    assert "Hello" in out["pages"][0]["text"]
    assert out["errors"] == []

