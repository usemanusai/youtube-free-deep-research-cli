import pytest

from youtube_chat_cli_main.services.brave_search_service import BraveSearchService, BraveSearchError


def test_brave_service_requires_api_key(monkeypatch):
    # Ensure no api key present
    class DummyCfg:
        brave_api_key = None

    monkeypatch.setattr("youtube_chat_cli_main.services.brave_search_service.get_config", lambda: DummyCfg())

    svc = BraveSearchService()
    with pytest.raises(BraveSearchError):
        svc.search("hello")

