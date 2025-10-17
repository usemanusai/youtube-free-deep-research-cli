from click.testing import CliRunner
from youtube_chat_cli_main.cli.agents_commands import agents

def test_graph_exports():
    runner = CliRunner()
    res1 = runner.invoke(agents, ["graph", "deep-research"]) 
    assert res1.exit_code == 0
    assert "```mermaid" in res1.output

    res2 = runner.invoke(agents, ["graph", "content-checks"]) 
    assert res2.exit_code == 0
    assert "```mermaid" in res2.output

