# Tech Stack Audit & Modernization — youtube-chat-cli-main (2025-10-04)

This document consolidates current best practices, version recommendations, and migration guidance to ensure the project is portable, secure, and production-ready across Windows, macOS, and Linux (amd64/arm64).

## Executive Summary
- Python: Target 3.13.x LTS line (3.13.7 current) [Py 3.13]. Adopt `pyproject.toml` (PEP 621) with `uv` for fast, reproducible installs; keep `pip` fallback. 
- Testing: `pytest` 8.x + `pytest-cov`; block network in unit tests (`pytest-socket`); mock HTTP via `responses`/`requests-mock`; prefer `httpx` for client code.
- Web API: FastAPI latest stable (0.11x); Pydantic v2; JWT/OAuth2 best practices; consistent OpenAPI; versioned APIs.
- LLM stack: Prefer LangGraph with LangChain v0.3+/v1 migration awareness; add OTEL tracing (OpenLLMetry) and rate limiting (aiolimiter/litellm if used).
- Frontend: Next.js 15.x with React 19 alignment; enable Corepack for npm/pnpm; consider Turbopack builds where stable.
- Vector DB & DB: Prefer Qdrant (stable ARM64 & Docker) over Chroma for robustness; SQLite tuned for WAL & pragmas if used in prod.
- Docker: Multi-stage on `python:3.13-slim`; non-root user; optional Playwright image; consider distroless runtime with trade-offs.
- CI/CD (GitHub Actions): Use setup-python v6 w/ pip cache; matrix for OS/Python; SAST: Semgrep→SARIF, Bandit JSON, Gitleaks with token; SBOM (Syft) + vuln scan (Grype/Trivy); Dependabot or Renovate.

## 1) Python Ecosystem (3.13+)
- Version: Python 3.13.7 (2025-08-14) is current maintenance [Py 3.13].
- Project structure: Prefer `src/` layout for import correctness and packaging [PPUG src-layout].
- Packaging: `pyproject.toml` with PEP 621 metadata; avoid mixed legacy files [PPUG PEP621].
- Environments: Cross-platform via `uv` or stdlib `venv`. `uv` can manage Python installs and lockfiles (`uv.lock`) for reproducibility [uv docs].
- Notes: Mind C-extensions (lxml/selectolax) on Windows; ensure build deps in Docker and CI.

## 2) Package Managers & Dependency Management
- Python: 
  - `uv` (fast resolver/installer, lockfile, drop-in for pip/pip-tools/virtualenv) [uv GH, uv docs].
  - `pip-tools` still solid for constraints/locks if staying with `pip` [pip-tools].
  - Poetry 2.x supports PEP 621; viable if you prefer monolithic workflow [Poetry 2.0].
- Node (dashboard): 
  - Prefer `pnpm` or modern Yarn v4 if team standard; `npm` remains baseline. Use Corepack to pin package manager per `packageManager` field [Corepack].
  - Ensure CI runs `corepack enable` before installs.
- Reproducibility: Lockfiles (`uv.lock`, `requirements.txt` pins if needed; `pnpm-lock.yaml`/`package-lock.json`).
- Security: Add SBOM & vuln scans in CI (Syft + Grype/Trivy).

## 3) Testing Frameworks & Coverage
- Unit tests: `pytest` 8.x [pytest]. Coverage via `pytest-cov`.
- Network isolation: `pytest-socket` to block external calls; selectively allow hosts for integration tests.
- HTTP mocking: `responses` (requests) or `requests-mock`; for `httpx`, use `respx` or `httpx` test clients.
- FastAPI integration: Use `httpx.AsyncClient` with FastAPI test app; avoid real browsers in unit tests; E2E uses Playwright if needed.
- Parallel: `pytest-xdist` cautiously (shared resources can bottleneck). Prefer logical sharding over naive process fan-out.

## 4) Containerization (Docker)
- Images: Base `python:3.13-slim`. Install build deps only in builder stage; copy wheels/venv to runtime.
- Non-root: Create user/group, chown app dirs, switch `USER` in final stage [Docker best practices].
- Multi-arch: Use buildx and QEMU to build `linux/amd64,linux/arm64` [Docker buildx].
- Compose (dev): Compose v2; profiles for optional services (dashboard, qdrant, redis). On Windows, prefer WSL2 backend.
- Browser automation: Use official Playwright Python Docker image where needed; otherwise keep base small.
- Scanning: Trivy image scan in CI; Syft SBOM; Grype for vuln scanning.

## 5) CI/CD with GitHub Actions
- Runners: `ubuntu-latest` now ubuntu-24; test also windows-latest, macos-latest [Actions notices].
- Matrix: Python (3.13, optionally 3.12), OS (ubuntu, windows).
- Caching: setup-python v6 `cache: pip` when lock/constraints exist; setup-node v4 + corepack for Node.
- SAST: Semgrep→SARIF via `github/codeql-action/upload-sarif@v3`; Bandit JSON artifact; Gitleaks action with `github_token` on PRs.
- SBOM & provenance: Syft SBOM + Grype; optional SLSA attestations / actions/attest-build-provenance.
- Dependency updates: Dependabot or Renovate (Renovate offers more flexibility/grouping).
- Artifacts: Publish build artifacts, coverage reports, SARIF; keep retention reasonable.

## 6) Security & SAST Tools
- Semgrep OSS: Tune rules via `.semgrep.yml`; upload SARIF to Security tab [Semgrep CI].
- Bandit: JSON only (no SARIF); consider presenting key issues in job summary; treat as advisory.
- Gitleaks: Pass `github_token` for PR events; SARIF artifact; optionally upload SARIF.
- ESLint security: Use Next.js recommended config; add security-focused rules if dashboard is active.
- SBOM & scanning: Syft (CycloneDX/SPDX) + Grype or Trivy; fail on high/critical vulns.
- Secrets: Use GitHub Environments/Secrets; avoid plaintext `.env` in CI artifacts; consider sops/age for at-rest repo secrets if needed.

## 7) FastAPI & Web Framework
- FastAPI: Track latest 0.11x; ensure Pydantic v2 compatibility; prefer async routes and `httpx` clients.
- Auth: OAuth2 / JWT with rotation and short TTLs; store refresh tokens securely; CSRF for browser flows.
- OpenAPI: Ensure tags, error models; enable versioning in routes (`/v1/...`).
- Perf: Use uvicorn workers with uvloop in production; enable gzip/brotli via proxy; caching headers for static/dashboard.

## 8) LangGraph & LLM Integration
- LangChain v0.3+ and LangGraph improvements; v1.0 migrations in 2025—track docs for API changes.
- Observability: OpenTelemetry tracing; OpenLLMetry or similar open-source tracers; optionally LangSmith or alternatives.
- Rate limiting & cost: Use `aiolimiter` for provider throttling; centralize retries (tenacity) and budget limits; litellm server if multi-provider.
- Safety: Prompt templates with red-teaming rules; log prompts/outputs under privacy guidelines.

## 9) Next.js Dashboard
- Next.js 15.x aligns with React 19; App Router; stable Node middleware; Turbopack builds (watch beta status) [Next 15.x].
- TypeScript: Strict TS; path aliases; Corepack to pin package manager; `next lint` deprecations addressed.
- Build/deploy: Vercel or Docker-based deploy; image optimization cache; analyze bundle sizes; avoid server-only APIs on client.

## 10) Vector Stores & Databases
- Qdrant: Active releases; ARM64 builds; Docker images; robust production posture [Qdrant].
- Chroma: Rapid iteration; reports of stability issues—evaluate carefully if choosing [Chroma issues].
- SQLite: WAL mode; tuned `PRAGMA` (synchronous=normal or full, journal_mode=wal, cache_size, mmap_size). Ensure write perms in containers.
- Migrations: Alembic or SQLAlchemy migrations for schema versioning; keep idempotent, backward compatible where feasible.

## Version Recommendations (as of 2025-10-04)
- Python: 3.13.7
- FastAPI: latest 0.11x compatible with Pydantic v2
- Pydantic: v2.10+
- pytest: 8.x; pytest-cov latest; pytest-socket latest; xdist optional
- HTTP: httpx 0.27+; tenacity 9+
- Security: semgrep latest OSS; bandit 1.8+; gitleaks 8+
- SBOM/Vuln: syft latest; grype latest; trivy latest
- Node: Next.js 15.4+ / 15.5; React 19; TypeScript 5.6+; package manager pinned via Corepack (pnpm 9 or npm 10/11)

## Migration Paths & Breaking Changes
- Pydantic v1→v2: Update `model_dump()`/`model_validate()` usages; strict types; refactor validators.
- httpx over requests: Replace `requests` in new code; for legacy tests, keep `responses`; add `respx` for httpx tests.
- LangChain/LangGraph: Follow official migration guides (0.2→0.3 and toward 1.0) to update imports and memory/persistence APIs.
- Next.js 15 & React 19: Validate App Router features and middleware; check deprecated `next lint` behaviors and TS config updates.

## Security Considerations & Compliance
- PR-level: Require CI checks (build, tests, security scans) to pass before merge.
- Secrets: GitHub Environments; rotate tokens; never echo secrets; redact logs.
- SBOM: Generate per build; fail CI on high/critical vulns.
- Provenance: Optional SLSA attestations for release artifacts.

## Performance Notes
- Docker: Multi-stage; cache wheels; only copy runtime artifacts; small final image (<500MB target).
- Tests: Avoid real network/browser in unit tests; isolate state; parallelize safely.
- SQLite: WAL, tuned pragmas; vacuum schedule if needed.

## Specific Action Items (Implementation Plan)
1. Package mgmt
   - Adopt `uv` with `pyproject.toml` + `uv.lock`; keep `pip` fallback in CI/Docker.
   - Node: Add `packageManager` field; enable Corepack; choose `pnpm` (recommended) or stay with npm.
2. Testing
   - Add `pytest-socket` default-off fixture; standard `responses` fixtures; `respx` if httpx adopted.
3. HTTP & Retries
   - Centralize httpx client with timeouts, retries (tenacity), UA, and rate limiting (aiolimiter) config.
4. FastAPI
   - Confirm Pydantic v2 usage; add JWT/OAuth2 utilities; ensure OpenAPI and API versioning.
5. LLM
   - Add OTEL tracing; rate-limited adapters; configurable providers; budget guards.
6. Docker & Compose
   - Multi-stage Dockerfile; non-root; buildx multi-arch; Compose profiles (api, dashboard, db, qdrant, redis); Playwright variant.
7. CI/CD
   - setup-python v6 (cache pip); setup-node v4 + corepack; Semgrep→SARIF; Bandit JSON; Gitleaks token; Syft+Grype/Trivy; Dependabot or Renovate; optional SLSA provenance.
8. Docs
   - Update README/CONTRIBUTING, deployment guides; migration guide for any breaking changes.

## Key References
- Python 3.13.7: https://www.python.org/downloads/release/python-3137/ | What’s New 3.13: https://docs.python.org/3/whatsnew/3.13.html
- Project structure (src layout): https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- PEP 621: https://packaging.python.org/en/latest/specifications/pyproject-toml/
- uv: https://github.com/astral-sh/uv | https://docs.astral.sh/uv/guides/projects/
- pip-tools: https://github.com/jazzband/pip-tools
- Poetry 2.0: https://python-poetry.org/blog/announcing-poetry-2.0.0/
- pytest: https://pytest.org/ | pytest-socket: https://github.com/miketheman/pytest-socket | responses: https://pypi.org/project/responses/
- httpx: https://www.python-httpx.org/ | tenacity: https://tenacity.readthedocs.io/
- FastAPI: https://fastapi.tiangolo.com/ | Release notes: https://fastapi.tiangolo.com/release-notes/
- LangChain/LangGraph migration: https://python.langchain.com/docs/versions/migrating_memory/
- Next.js 15: https://nextjs.org/blog/next-15 | Next 15.5: https://nextjs.org/blog/next-15-5
- Qdrant: https://qdrant.tech/documentation/guides/installation/
- Docker buildx: https://docs.docker.com/build/building/multi-platform/
- setup-python v6: https://github.com/actions/setup-python | Notices: https://github.blog/changelog/
- Semgrep CI: https://semgrep.dev/docs/semgrep-ci/sample-ci-configs | Upload SARIF: https://docs.github.com/.../uploading-a-sarif-file-to-github
- Syft/Grype: https://github.com/anchore/syft | https://github.com/anchore/grype | Trivy: https://github.com/aquasecurity/trivy-action

