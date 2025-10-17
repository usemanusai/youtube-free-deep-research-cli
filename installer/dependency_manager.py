"""
Dependency Manager for Universal Installer
- Ensures Python venv, pip installs, Node via fnm (if available), Playwright browsers (optional)
- Non-intrusive: does not install system-wide runtimes; prints guidance when missing
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional
import os
import subprocess
import sys


def run(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> int:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check).returncode


def ensure_venv(venv_dir: Path = Path('.venv')) -> Path:
    if not venv_dir.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
    return venv_dir


def pip_install(requirements_files: Iterable[Path]) -> None:
    # Upgrade pip quietly (best-effort)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=False)
    for rf in requirements_files:
        if rf.exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(rf)], check=True)


def ensure_fnm_and_node(target_node: str = '20') -> None:
    """Ensure Node.js using FNM if present; otherwise, use existing node or print guidance.
    Non-destructive: does not install system-wide.
    """
    def has(cmd: str) -> bool:
        return subprocess.run(['bash', '-lc', f'command -v {cmd} >/dev/null 2>&1'], check=False).returncode == 0 if os.name != 'nt' else subprocess.run(['where', cmd], check=False).returncode == 0

    if has('fnm'):
        # Shell out to set Node version for this session
        if os.name == 'nt':
            subprocess.run(['fnm', 'use', target_node], check=False)
        else:
            subprocess.run(['bash', '-lc', f'fnm install {target_node} && fnm use {target_node}'], check=False)
    else:
        # Fall back: rely on existing node if any; otherwise print guidance
        if not has('node'):
            print('[Installer] Node.js not found. Please install Node 20 LTS (recommend FNM: https://github.com/Schniz/fnm).')


def npm_install(workspace_dir: Path) -> None:
    if not workspace_dir.exists():
        return
    # Use npm ci when lockfile present, else npm install
    lock = workspace_dir / 'package-lock.json'
    cmd = ['npm', 'ci'] if lock.exists() else ['npm', 'install']
    subprocess.run(cmd, cwd=str(workspace_dir), check=True)


def playwright_install_chromium(skip: bool = False) -> None:
    if skip:
        return
    # Best-effort: install chromium only to minimize CI size
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright>=1.40.0'], check=False)
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=False)
    except Exception:
        pass

