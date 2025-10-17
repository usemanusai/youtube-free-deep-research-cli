"""
Agents CLI Commands (scaffold)

Adds `jaegis agents deep-research` and `jaegis agents content-check` commands.
"""
from __future__ import annotations

import json
import click
import logging

from ..workflows import deep_research, content_checks

logger = logging.getLogger(__name__)


@click.group()
def agents():
    """Nexus Agents - multi-agent research and content checks."""
    pass


@agents.command("deep-research")
@click.option("--topic", required=True, help="Topic to research")
@click.option("--max-turns", type=int, default=None, help="Max conversation turns")
@click.option("--backends", type=str, default=None, help="Comma-separated backends (e.g. brave,tavily,duckduckgo)")
def cmd_deep_research(topic: str, max_turns: int | None, backends: str | None):
    """Run the deep research workflow (scaffold)."""
    try:
        backends_list = [b.strip() for b in backends.split(',')] if backends else None
        result = deep_research.run(topic=topic, max_turns=max_turns, backends=backends_list)
        click.echo(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error("deep-research failed: %s", e)
        raise SystemExit(1)


@agents.command("content-check")
@click.option("--topic", required=True, help="Topic to check for novelty vs redundancy")
@click.option("--max-loops", type=int, default=None, help="Max refinement loops")
def cmd_content_check(topic: str, max_loops: int | None):
    """Run the content checks workflow (scaffold)."""
    try:
        result = content_checks.run(topic=topic, max_loops=max_loops)
        click.echo(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error("content-check failed: %s", e)
        raise SystemExit(1)

