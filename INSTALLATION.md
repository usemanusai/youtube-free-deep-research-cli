# Universal Project Installer

This repository includes a cross‑platform installer to bootstrap a local dev environment with minimal friction and no system‑wide changes.

## Quick Start

- Windows (PowerShell):
  - Right‑click Start → Windows PowerShell (or Terminal)
  - Navigate to the repo root, then run:
  
  ```powershell
  ./installer/install.ps1
  ```

- macOS/Linux (Bash/Zsh):
  
  ```bash
  bash ./installer/install.sh
  ```

The installer:
- Creates a local Python virtual environment (.venv)
- Installs minimal installer deps (rich, questionary, dotenv, requests)
- Optionally prepares Node 20 via FNM if present (non‑destructive)
- Installs the dashboard dependencies if a workspace-* folder is found
- Prompts for API keys and writes .env and .env.local
- Optionally installs Playwright Chromium for scraping (can be skipped)

## Requirements

- Python 3.13 on PATH (python -V)
- Node.js LTS recommended (20.x). If not available, the installer prints guidance.
- Git (recommended for hooks and CI integration)

## Options

- PowerShell: `./installer/install.ps1 -SkipPlaywright`
- Bash: `INSTALLER_SKIP_PLAYWRIGHT=1 bash ./installer/install.sh`

## Verification

After the installer finishes:
- Check .env at repo root and .env.local inside the dashboard workspace
- Start backend (example):
  
  ```bash
  # from repo root
  . ./.venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
  python -m youtube_chat_cli_main.api_server
  ```

- Health endpoints:
  
  ```bash
  curl -s http://127.0.0.1:8555/api/v1/health/live | jq .
  curl -s http://127.0.0.1:8555/api/v1/health/ready | jq .
  ```

- Dashboard (from workspace‑*/ dir):
  
  ```bash
  npm run dev
  ```

## Troubleshooting

- Python not found: Install Python 3.13.
- Node not found: Install Node 20 LTS or FNM (https://github.com/Schniz/fnm).
- Playwright download slow: Use `-SkipPlaywright`/`INSTALLER_SKIP_PLAYWRIGHT=1` and install later.
- Network‑restricted env: The installer will skip optional steps and continue.

## Uninstall

- Remove the `.venv` directory to clear Python environment
- Remove `node_modules` in dashboard workspace to clear Node dependencies
- Delete `.installer_state.json`, `.env`, and `.env.local` if you want a clean slate

