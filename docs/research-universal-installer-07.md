# Universal Project Installer – Phase 1 Research (Integration Prompt #7)

Date of Execution: 2025-10-03 (established via public time sources)

Scope: youtube-chat-cli-main (Python 3.13 / FastAPI backend; Next.js 15 dashboard)

## 1) Verified Project Stack (from repository)

- Python: 3.13 target (requirements span modern libs; uvicorn/fastapi confirmed in api_requirements.txt)
- Node.js / Next.js: Next 15.3.5 in workspace package.json → recommend Node 20 LTS (≥18.18 supported, 20 preferred)
- Optional services: Redis (caching), Qdrant/Chroma (vector store), Playwright browsers, Tesseract OCR, Git (pre-commit)
- Testing: pytest; pre-commit (ruff, bandit, detect-secrets, pytest); CI via GitHub Actions

## 2) Constraints mapping → Strategy

- 100% open source and free → Prefer script-based, no proprietary installer runtimes
- Cross-platform (Windows/macOS/Linux) → Dual-entry: PowerShell (.ps1) + Bash (.sh) wrapper; Python TUI for unified logic
- Self-contained / minimal admin → Use user-local installs when possible (pyenv/fnm). Provide silent installers as fallback
- Graceful degradation → Optional features (Redis, Playwright, Tesseract, Qdrant) are skippable with clear messaging
- Idempotent → Re-run-safe: detect existing venv/node_modules, verify versions, resume via .installer_state.json
- Secure → TUI secret prompts; never echo keys; write to .env and dashboard .env.local; validation pings are opt-in

## 3) Tooling options (survey and recommendations)

### 3.1 Installer frameworks (cross‑platform)
- NSIS/Inno/WiX: Windows‑only. Not suitable as sole cross‑platform base.
- Electron/Squirrel: heavy; not aligned with CLI-first, open-source minimalism.
- Script + Python TUI (Recommended):
  - Pros: zero vendor lock-in; trivial maintenance; works everywhere with Python
  - Cons: depends on having a workable Python (the installer will acquire/ensure it)

Conclusion: Choose Option A – shell/PowerShell entry scripts + Python TUI wizard (rich + questionary), with robust checks.

### 3.2 Runtime acquisition
- Python 3.13:
  - Windows: official python.org installer (silent: /quiet InstallAllUsers=0 PrependPath=1 Include_test=0)
  - macOS/Linux: pyenv (no root required; installs to $HOME). Alternative: asdf.
- Node.js 20 LTS:
  - Cross-platform: FNM (Fast Node Manager) is lightweight and works across OSes; nvm-windows is Windows-only; asdf also works but heavier.

Recommendation: pyenv (macOS/Linux), python.org silent installer (Windows). FNM for Node 20 across all OSes.

### 3.3 Libraries for the TUI wizard
- rich: progress bars, tables, status spinners, colorized output
- questionary: ergonomic prompts (password, select, confirm) built on prompt_toolkit
- Alternative: textual (full TUI apps); heavier than needed here

Recommendation: rich + questionary

### 3.4 Config & secrets
- python-dotenv to write and load .env and dashboard .env.local
- Secure prompts: mask input; avoid logging; store only in env files owned by the user

### 3.5 Ports and service checks
- Check if a port is open with socket.connect_ex; suggest next available (8555→8556, 3000→3001)
- For optional Redis: detect via TCP connection; propose Docker variant or skip

### 3.6 Error handling patterns
- Retriable operations with exponential backoff (downloads, pip/npm install)
- Auto-fix: pip with --no-cache-dir on retry; npm ci on retry; clear node_modules only if idempotent
- Rollback: on partial setup failure, remove incomplete venv and re-run
- Resume: write step markers to .installer_state.json

### 3.7 Packaging & distribution (optional)
- PyInstaller: simplest to bundle Python CLI; Nuitka: faster executables, more complex; cx_Freeze: alternative
- Code signing: out of scope here (requires user certs); document how-to in INSTALLATION.md

## 4) Concrete selections for Phase 2

- Entry points:
  - installer/install.ps1 (PowerShell 5.1+), installer/install.sh (Bash/Zsh)
  - Both call Python: installer/setup_wizard.py
- Python dependencies for installer runtime (requirements_installer.txt):
  - rich, questionary, python-dotenv, requests, packaging (version checks)
- Dependency manager: installer/dependency_manager.py
  - Python ensure (pyenv or python.org as needed)
  - Node ensure (fnm → Node 20 LTS)
  - Create .venv (python -m venv .venv) and pip install -r requirements.txt and api_requirements.txt
  - playwright install chromium (if user opted to install Playwright runtime)
  - npm install in dashboard workspace; npx husky install when enabled
- Config validator: installer/config_validator.py
  - API key probes (OpenRouter/OpenAI), port availability check, vector store endpoint check (if provided)
- Artifacts written:
  - .env (backend), workspace-*/.env.local (dashboard)
  - .installer_state.json with last successful step and versions

## 5) Version guidance

- Python: 3.13.x (latest patch)
- Node: 20.x LTS (compatible with Next 15, covers modern toolchains)
- Playwright browsers: chromium only by default (lightweight); user may add firefox/webkit later
- Qdrant/Chroma: Use local Chroma by default if user doesn’t provide Qdrant credentials/URL

## 6) UX flow for the wizard

1) Welcome + overview (estimated 5–12 minutes on typical network)
2) Preflight checks (OS, PowerShell/Bash version, write permissions)
3) Dependency detection and plan (Python, Node, Git; optional Redis/Tesseract/Playwright)
4) Acquire runtimes (offer to install or skip; show progress bars)
5) Python venv + pip install (requirements.txt, api_requirements.txt)
6) Node install + npm install (workspace dashboard)
7) API keys collection (at least one of OpenRouter/OpenAI required; Tavily/Brave optional)
8) Service configuration (ports, Redis enable, vector store selection)
9) Write .env files + state file
10) Verification (DB init, health checks; optional dashboard build)
11) Success summary + next steps

## 7) Code snippets (illustrative patterns to implement)

### 7.1 Port check & next available
```python
import socket

def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def next_available_port(start: int, host: str = "127.0.0.1") -> int:
    p = start
    while is_port_open(host, p):
        p += 1
    return p
```

### 7.2 Write .env safely
```python
from pathlib import Path

def write_env(path: Path, data: dict):
    lines = []
    for k, v in data.items():
        if v is None:
            continue
        safe = str(v).replace("\n", "\\n")
        lines.append(f"{k}={safe}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
```

### 7.3 Minimal validation ping (OpenRouter)
```python
import os, requests

def validate_openrouter(key: str) -> bool:
    try:
        r = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {key}"}, timeout=10,
        )
        return r.status_code in (200, 401)  # 401 means key recognized flow
    except Exception:
        return False
```

## 8) Optional components and handling

- Redis: if user opts in, provide Docker command; otherwise skip gracefully
  - `docker run -p 6379:6379 --name redis -d redis:7`
- Tesseract OCR: document package names (brew install tesseract; apt-get install tesseract-ocr; Windows installer link)
- Playwright browsers: run `python -m playwright install chromium` after pip install when enabled

## 9) Idempotency & rollback

- Idempotent re-runs by checking:
  - .venv exists and python -V matches ≥3.13 → reuse or upgrade path
  - Node version via `node -v`; if mismatch, let fnm switch
- On failure:
  - Record failure stage in .installer_state.json
  - Offer cleanup of partial venv/node_modules and resume

## 10) Documentation to accompany

- INSTALLATION.md: quick start (./installer/install.ps1 or ./installer/install.sh), manual fallback, troubleshooting, uninstall
- README_INSTALLER.md: describes installer internals, prerequisites, and supported options

## 11) References (representative)

- Python 3.13 downloads (python.org)
- pyenv project (GitHub: pyenv/pyenv)
- FNM (Fast Node Manager) (GitHub: Schniz/fnm)
- Playwright install docs (microsoft/playwright)
- python-dotenv (pypi)
- rich, questionary (pypi)

---

Decision for Phase 2: Implement Option A – script entry points + Python TUI (rich + questionary), with dependency acquisition (pyenv/fnm, or python.org installer on Windows), secure env generation, port conflict resolution, verification steps, and idempotent resume.

