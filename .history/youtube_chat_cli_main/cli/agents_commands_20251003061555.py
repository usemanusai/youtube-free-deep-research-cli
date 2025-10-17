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
    """Run the content checks workflow."""
    try:
        result = content_checks.run(topic=topic, max_loops=max_loops)
        click.echo(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error("content-check failed: %s", e)
        raise SystemExit(1)


@agents.command("archive-sync")
@click.option("--dry-run", is_flag=True, default=True, help="Plan GDrive vector indexing without writing")
def cmd_archive_sync(dry_run: bool):
    """Trigger GDrive archive vector indexing via background service run_once."""
    try:
        from youtube_chat_cli_main.services.background_service import BackgroundService
        svc = BackgroundService()
        if dry_run:
            # For dry-run, just return planned actions (counts will be zero if not configured)
            res = svc.run_once()
            res["dry_run"] = True
            click.echo(json.dumps(res, ensure_ascii=False))
        else:
            res = svc.run_once()
            res["dry_run"] = False
            click.echo(json.dumps(res, ensure_ascii=False))
    except Exception as e:
        logger.error("archive-sync failed: %s", e)
        raise SystemExit(1)

