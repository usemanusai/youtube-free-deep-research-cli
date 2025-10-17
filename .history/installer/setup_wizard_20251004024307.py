"""
Universal Installer TUI Wizard (rich + questionary)
Non-intrusive: confines changes to repo; guides user; writes .env and state.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json
import os
import sys

from packaging import version
from rich.console import Console
from rich.table import Table
import questionary

try:
    from .dependency_manager import ensure_venv, pip_install, ensure_fnm_and_node, npm_install, playwright_install_chromium
    from .config_validator import next_available_port, looks_like_api_key, write_env, write_state
except ImportError:
    import sys as _sys, pathlib as _pathlib
    _sys.path.append(str(_pathlib.Path(__file__).resolve().parent))
    from dependency_manager import ensure_venv, pip_install, ensure_fnm_and_node, npm_install, playwright_install_chromium
    from config_validator import next_available_port, looks_like_api_key, write_env, write_state

console = Console()
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ENV = REPO_ROOT / ".env"
DASHBOARD_DIR = next((p for p in REPO_ROOT.glob("youtube_chat_cli_main/workspace-*/") if (p / "package.json").exists()), None)
DASHBOARD_ENV = DASHBOARD_DIR / ".env.local" if DASHBOARD_DIR else None
STATE_FILE = REPO_ROOT / ".installer_state.json"


def _py_ver_ok() -> bool:
    try:
        v = version.parse("".join(sys.version.split()[0]))
        return v >= version.parse("3.13")
    except Exception:
        return True


def main() -> int:
    console.rule("[bold cyan]Universal Installer Wizard")

    # Preflight
    ok_py = _py_ver_ok()
    if not ok_py:
        console.print("[yellow]Warning: Python 3.13+ recommended.")

    # Plan summary table
    tbl = Table(title="Planned Steps")
    tbl.add_column("Step")
    tbl.add_column("Detail")
    tbl.add_row("Python venv", ".venv in repo root (installer runtime)")
    tbl.add_row("Pip deps", "installer/requirements_installer.txt")
    tbl.add_row("Node.js", "Use existing node or FNM if available (Node 20)")
    tbl.add_row("Dashboard", "npm install in dashboard workspace (if found)")
    tbl.add_row("Config", "Prompt for keys; write .env and .env.local")
    tbl.add_row("Verify", "Optional health checks")
    console.print(tbl)

    # Confirm
    if not questionary.confirm("Proceed with installation?").ask():
        console.print("[yellow]Cancelled by user")
        return 0

    # Ensure venv and installer deps already handled by entry script
    ensure_venv(REPO_ROOT / ".venv")

    # Node setup (non-destructive)
    ensure_fnm_and_node('20')

    # Dashboard install (if present)
    if DASHBOARD_DIR:
        console.print(f"[cyan]Installing dashboard deps in {DASHBOARD_DIR}")
        try:
            npm_install(DASHBOARD_DIR)
        except Exception as e:
            console.print(f"[yellow]Dashboard install skipped: {e}")

    # Collect minimal config
    console.print("[bold]Configuration[/bold]")
    api_key = questionary.text("Enter OpenRouter or OpenAI API key (leave blank to skip)", default="").ask()
    brave_key = questionary.text("Enter BRAVE_API_KEY (optional)", default="").ask()
    tavily_key = questionary.text("Enter TAVILY_API_KEY (optional)", default="").ask()

    backend_port = next_available_port(8555)
    dashboard_port = next_available_port(3000)

    # Prepare envs
    backend_env: Dict[str, Any] = {
        "OPENROUTER_API_KEY": api_key or "",
        "OPENAI_API_KEY": "",
        "BRAVE_API_KEY": brave_key or "",
        "TAVILY_API_KEY": tavily_key or "",
        "APP_PORT": str(backend_port),
        "LOG_LEVEL": "INFO",
        "VECTOR_STORE_TYPE": "chroma",  # default safe
    }
    dash_env: Dict[str, Any] = {
        "NEXT_PUBLIC_API_URL": f"http://127.0.0.1:{backend_port}",
        "PORT": str(dashboard_port),
    }

    # Heuristic checks
    if api_key and not looks_like_api_key(api_key):
        console.print("[yellow]API key format looks unusual; you can update .env later.")

    # Write env files
    write_env(BACKEND_ENV, backend_env)
    if DASHBOARD_ENV:
        write_env(DASHBOARD_ENV, dash_env)

    # Optional Playwright browser install (skip if env var set)
    skip_pw = os.environ.get('INSTALLER_SKIP_PLAYWRIGHT') == '1'
    playwright_install_chromium(skip=skip_pw)

    # Persist state
    state = {
        "python": sys.version,
        "node": os.popen('node -v 2>NUL || node -v 2>/dev/null').read().strip(),
        "backend_env": str(BACKEND_ENV),
        "dashboard_env": str(DASHBOARD_ENV) if DASHBOARD_ENV else None,
        "completed": True,
    }
    write_state(STATE_FILE, state)

    console.print("[green]Installation complete. You can now run the backend and dashboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

