from youtube_chat_cli_main.services.web_scraper_service import WebScraperService

class DummyResp:
    def __init__(self, text, status=200):
        self.text = text
        self.status_code = status
        self.ok = status == 200

HTML = """
<html><head><title>T</title></head>
<body>
<a href="/next">next</a>
<p>Hello</p>
</body></html>
"""


def test_scraper_fallback_requests(monkeypatch):
    svc = WebScraperService()
    # Force playwright path to return empty
    monkeypatch.setattr(svc, "_fetch_playwright", lambda *a, **k: "")
    # Stub requests.get to avoid real HTTP
    import youtube_chat_cli_main.services.web_scraper_service as mod
    def fake_get(url, timeout=None, headers=None):
        return DummyResp(HTML, 200)
    monkeypatch.setattr(mod, "requests", type("R", (), {"get": staticmethod(fake_get)}))

    out = svc.scrape("https://example.com", depth=1, max_pages=2, timeout_s=2)
    assert out["pages"] and out["pages"][0]["status"] == 200

