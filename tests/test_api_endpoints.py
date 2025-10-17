from fastapi import FastAPI
from fastapi.testclient import TestClient

from youtube_chat_cli_main.api.nexus_agents import router

def make_app():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/nexus-agents")
    return app


def test_sessions_list_empty():
    app = make_app()
    client = TestClient(app)
    r = client.get("/api/v1/nexus-agents/sessions")
    assert r.status_code == 200
    data = r.json()
    assert "sessions" in data
    assert isinstance(data["total"], int)


def test_archive_status():
    app = make_app()
    client = TestClient(app)
    r = client.get("/api/v1/nexus-agents/archive/status")
    assert r.status_code == 200
    data = r.json()
    assert "indexing_status" in data

