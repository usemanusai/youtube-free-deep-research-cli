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


@agents.group("sessions")
def sessions_group():
    """Manage Nexus Agent sessions"""
    pass

@sessions_group.command("list")
@click.option("--limit", type=int, default=50)
@click.option("--offset", type=int, default=0)
@click.option("--workflow-type", type=str, default=None)
def cmd_sessions_list(limit: int, offset: int, workflow_type: str | None):
    try:
        from ..core.database import get_database
        db = get_database()
        res = db.list_sessions(limit=limit, offset=offset, workflow_type=workflow_type)
        click.echo(json.dumps(res, ensure_ascii=False))
    except Exception as e:
        logger.error("sessions list failed: %s", e)
        raise SystemExit(1)

@sessions_group.command("get")
@click.argument("session_id")
def cmd_sessions_get(session_id: str):
    try:
        from ..core.database import get_database
        db = get_database()
        sess = db.get_session(session_id)
        if not sess:
            raise click.ClickException("Session not found")
        msgs = db.get_session_messages(session_id)
        click.echo(json.dumps({"session": sess, "messages": msgs}, ensure_ascii=False))
    except Exception as e:
        logger.error("sessions get failed: %s", e)
        raise SystemExit(1)

@agents.group("archive")
def archive_group():
    """Manage archive indexing"""
    pass

@archive_group.command("status")
def cmd_archive_status():
    try:
        from youtube_chat_cli_main.services.background_service import get_background_service
        svc = get_background_service()
        click.echo(json.dumps(svc.get_indexing_status(), ensure_ascii=False))
    except Exception as e:
        logger.error("archive status failed: %s", e)
        raise SystemExit(1)

@archive_group.command("reindex")
@click.option("--force", is_flag=True, default=False)
def cmd_archive_reindex(force: bool):
    try:
        from youtube_chat_cli_main.services.background_service import get_background_service
        svc = get_background_service()
        job_id = svc.start_reindex_job(force=force)
        click.echo(json.dumps({"job_id": job_id, "status": "started"}, ensure_ascii=False))
    except Exception as e:
        logger.error("archive reindex failed: %s", e)
        raise SystemExit(1)

@archive_group.command("queue")
def cmd_archive_queue():
    """Show archive processing queue breakdown."""
    try:
        from ..core.database import get_database
        db = get_database()
        res = db.get_queue_breakdown()
        click.echo(json.dumps(res, ensure_ascii=False))
    except Exception as e:
        logger.error("archive queue failed: %s", e)
        raise SystemExit(1)


@agents.command("graph")
@click.argument("which", type=click.Choice(["deep-research","content-checks"]))
def cmd_graph(which: str):
    try:
        if which == "deep-research":
            from ..workflows.deep_research import export_graph_mermaid as exp
        else:
            from ..workflows.content_checks import export_graph_mermaid as exp
        click.echo(exp())
    except Exception as e:
        logger.error("graph export failed: %s", e)
        raise SystemExit(1)



@agents.command("trace")
@click.argument("workflow_id")
def cmd_trace(workflow_id: str):
    """Fetch workflow trace by correlation/workflow ID."""
    try:
        from ..core.database import get_database
        db = get_database()
        traces = db.get_workflow_traces(workflow_id)
        click.echo(json.dumps({"workflow_id": workflow_id, "traces": traces}, ensure_ascii=False))
    except Exception as e:
        logger.error("trace fetch failed: %s", e)
        raise SystemExit(1)
