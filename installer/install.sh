#!/usr/bin/env bash
# macOS/Linux Installer Entry Point
# Purpose: Bootstrap a minimal Python virtualenv for the installer runtime and invoke the TUI wizard.
# Safe-by-default: Does not install system-wide software; confines changes to repo directory.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

info(){ echo "[Installer] $*"; }
warn(){ echo "[Installer] $*" >&2; }

# 1) Ensure python exists
if ! command -v python >/dev/null 2>&1; then
  warn "Python not found. Please install Python 3.13 and re-run."
  warn "macOS: brew install python@3.13 | Linux: use your distro package manager or pyenv"
  exit 1
fi
info "Detected $(python -V)"

# 2) Create .venv for installer runtime
if [ ! -d .venv ]; then
  info "Creating virtual environment (.venv)"
  python -m venv .venv
fi

# 3) Activate and install installer deps
# shellcheck disable=SC1091
source .venv/bin/activate
info "Installing installer dependencies"
python -m pip install --upgrade pip >/dev/null 2>&1 || true
python -m pip install -r installer/requirements_installer.txt

# 4) Launch TUI wizard
INSTALLER_SKIP_PLAYWRIGHT=${INSTALLER_SKIP_PLAYWRIGHT:-0} \
python installer/setup_wizard.py

info "Installer completed successfully."

