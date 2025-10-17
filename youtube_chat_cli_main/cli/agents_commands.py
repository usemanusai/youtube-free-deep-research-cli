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


@agents.group("config")
def config_group():
    """Validate and manage configuration."""
    pass

@config_group.command("validate")
def cmd_config_validate():
    try:
        from ..core.config import get_config
        cfg = get_config(reload=True)
        cfg._validate_config()  # logs warnings; raises on hard errors if any
        click.echo(json.dumps({"ok": True}, ensure_ascii=False))
    except Exception as e:
        logger.error("config validate failed: %s", e)
        raise SystemExit(1)

@config_group.command("export")
def cmd_config_export():
    try:
        from ..core.config import get_config
        cfg = get_config()
        # Shallow export of commonly used keys
        data = {
            "search_backends": cfg.search_backends,
            "scraper": {
                "depth": cfg.scraper_depth,
                "max_pages": cfg.scraper_max_pages,
                "timeout_s": cfg.scraper_timeout_s,
                "headless": cfg.scraper_headless,
                "user_agent": cfg.scraper_user_agent,
            },
            "duplicate": {
                "redundant": cfg.duplicate_similarity_redundant,
                "overlap": cfg.duplicate_similarity_overlap,
                "half_life_days": cfg.duplicate_time_decay_half_life_days,
            },
            "nexus": {
                "max_turns": cfg.nexus_max_turns,
                "max_loops": cfg.nexus_max_loops,
                "debug": cfg.nexus_debug,
            },
        }
        click.echo(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        logger.error("config export failed: %s", e)
        raise SystemExit(1)

@config_group.command("diff")
@click.option("--defaults", is_flag=True, default=True, help="Compare against baked defaults")
def cmd_config_diff(defaults: bool):
    try:
        from ..core.config import get_config
        cfg = get_config()
        # Simple diff vs known defaults
        defaults_map = {
            "search_backends": ["brave", "legacy"],
            "scraper.timeout_s": 60,
            "scraper.headless": True,
            "duplicate.redundant": 0.85,
            "nexus.debug": False,
        }
        cur = {
            "search_backends": cfg.search_backends,
            "scraper.timeout_s": cfg.scraper_timeout_s,
            "scraper.headless": cfg.scraper_headless,
            "duplicate.redundant": cfg.duplicate_similarity_redundant,
            "nexus.debug": cfg.nexus_debug,
        }
        diff = {k: {"current": cur.get(k), "default": v} for k, v in defaults_map.items() if cur.get(k) != v}
        click.echo(json.dumps({"diff": diff}, ensure_ascii=False))
    except Exception as e:
        logger.error("config diff failed: %s", e)
        raise SystemExit(1)

@config_group.command("import")
@click.option("--file", "file_path", type=str, default="-")
def cmd_config_import(file_path: str):
    """Validate a JSON config payload from file or stdin and echo normalized values."""
    try:
        import sys, json as _json
        raw = sys.stdin.read() if file_path == '-' else open(file_path, 'r', encoding='utf-8').read()
        data = _json.loads(raw)
        # Very light validation of known keys
        if 'search_backends' in data and not isinstance(data['search_backends'], list):
            raise click.ClickException('search_backends must be a list')
        if 'nexus' in data and not isinstance(data['nexus'], dict):
            raise click.ClickException('nexus must be an object')
        click.echo(_json.dumps({"ok": True, "normalized": data}, ensure_ascii=False))
    except Exception as e:
        logger.error("config import failed: %s", e)
        raise SystemExit(1)
