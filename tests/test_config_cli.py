import json
from click.testing import CliRunner
from youtube_chat_cli_main.cli.agents_commands import agents

def test_config_validate_export_diff():
    r = CliRunner().invoke(agents, ["config", "validate"])
    assert r.exit_code == 0
    r2 = CliRunner().invoke(agents, ["config", "export"])
    assert r2.exit_code == 0
    data = json.loads(r2.output)
    assert "search_backends" in data
    r3 = CliRunner().invoke(agents, ["config", "diff"])
    assert r3.exit_code == 0
    diff = json.loads(r3.output)
    assert "diff" in diff

