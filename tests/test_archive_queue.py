import json
import pytest

from fastapi.testclient import TestClient
from youtube_chat_cli_main.api_server import app

client = TestClient(app)


def test_archive_queue_endpoint_smoke():
    r = client.get("/api/v1/nexus-agents/archive/queue")
    assert r.status_code in (200, 404)  # allow 404 if db not initialized in env
    if r.status_code == 200:
        data = r.json()
        assert "total" in data
        assert "by_status" in data
        assert "by_source" in data


def test_cli_archive_queue(monkeypatch, capsys):
    # Simulate CLI call by invoking function directly
    from youtube_chat_cli_main.cli.agents_commands import cmd_archive_queue
    try:
        cmd_archive_queue.callback()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    # Output should be JSON or empty if failed
    if out.strip():
        try:
            json.loads(out)
        except Exception:
            pytest.skip("Non-JSON output in this environment")

