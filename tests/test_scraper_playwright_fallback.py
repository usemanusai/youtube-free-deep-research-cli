from youtube_chat_cli_main.services.web_scraper_service import WebScraperService
from youtube_chat_cli_main.core.http_client import reset_httpx_client

HTML = """
<html><head><title>T</title></head>
<body>
<a href="/next">next</a>
<p>Hello</p>
</body></html>
"""


def test_scraper_fallback_requests(monkeypatch, respx_mock):
    # Ensure httpx client is created under respx patching
    reset_httpx_client()

    svc = WebScraperService()
    # Force playwright path to return empty
    monkeypatch.setattr(svc, "_fetch_playwright", lambda *a, **k: "")

    # Mock both root and /next
    respx_mock.get("https://example.com/").respond(status_code=200, content=HTML.encode("utf-8"))
    respx_mock.get("https://example.com/next").respond(status_code=200, content=HTML.encode("utf-8"))

    out = svc.scrape("https://example.com", depth=1, max_pages=2, timeout_s=2)
    assert out["pages"] and out["pages"][0]["status"] == 200

