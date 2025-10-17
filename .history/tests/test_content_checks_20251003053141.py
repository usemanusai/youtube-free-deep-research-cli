import pytest

from youtube_chat_cli_main.workflows import content_checks


def test_content_checks_scaffold_run():
    out = content_checks.run(topic="Test Topic", max_loops=2)
    assert isinstance(out, dict)
    assert out["decision"] in ("NOVEL", "REDUNDANT")

