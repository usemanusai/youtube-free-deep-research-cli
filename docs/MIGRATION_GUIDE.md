# Migration Guide

This guide documents breaking changes and how to migrate from the previous setup to the modernized stack (2025-10-04).

## Summary of Changes

- Introduced pyproject.toml (PEP 621) and uv lockfile for reproducible builds
- Centralized HTTP with httpx and retries/rate limits (`youtube_chat_cli_main/core/http_client.py`)
- WebScraperService now uses httpx-based client (Playwright remains optional)
- Added Placeholder LLM backend for tests/offline via `NEXUS_LLM_BACKEND=placeholder`
- BackgroundService: signal handlers registered only in main thread (fixes test failures)
- SQLite access: fixed `.get` on sqlite3.Row usage
- CI: Matrix across Windows/macOS/Linux; caching and coverage
- Docker: Multi-stage, non-root, production-ready base

## Package Management

- Preferred: uv
  - Create/refresh lock: `uv lock`
  - Install: `uv sync` (if using project layout) or `uv pip install -r requirements.txt`
- Fallback: pip
  - Python deps: `python -m pip install -r requirements.txt -r youtube_chat_cli_main/api_requirements.txt`

## Testing Changes

- New pytest fixtures in `tests/conftest.py`:
  - Platform-aware socket policy (blocks sockets on POSIX; allowed on Windows)
  - `http_responses` (requests) and `respx_mock` (httpx) helpers
- WebScraper tests updated to avoid real network and to stub Playwright path as needed

## Code Changes

- Use `request_with_retry(method, url, **kwargs)` for synchronous HTTP
- Use `get_async_client(rate_limit_per_sec)` for async HTTP
- Add `reset_httpx_client()` in tests if you need the httpx client to be created under a mock transport (respx)

## Environment Variables (new/changed)

- `NEXUS_LLM_BACKEND=placeholder` — force non-networking LLM during tests/offline

## CI/CD Changes

- `.github/workflows/quality-assurance.yml` now runs tests on Ubuntu, Windows, and macOS
- Security scanning is handled by `.github/workflows/security-audit.yml`

## Docker Notes

- Default image is multi-stage and runs as a non-root user
- Build: `docker build -t jaegis-api .`
- Run: `docker run --rm -p 8556:8556 jaegis-api`

## Potential Action Items for Consumers

- If you relied on `requests` behavior in downstream code/tests, switch to httpx or mock via `respx`
- Ensure `.env` is updated according to README and installer outputs
- Review CONTRIBUTING.md for updated guardrails and local checks

