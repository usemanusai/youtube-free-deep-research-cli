# Universal Governance & Execution Suite — Up-to‑Date Research (as of 2025‑10‑04)

This document consolidates current best practices, options, and references for package management, testing, scraping/HTTP, Docker, and CI/CD (GitHub Actions) to keep this project secure, portable, automated, and maintainable.

## Executive summary (recommendations)
- Package manager: Prefer uv (fast, drop‑in for pip/pip‑tools/virtualenv) with pyproject.toml; keep pip fallback. [R1–R5]
- Testing: pytest + pytest‑cov; optional pytest‑xdist for parallelism; block network via pytest‑socket when feasible; mock HTTP with responses or requests‑mock. [T1–T6]
- HTTP/scraping: Prefer httpx (timeouts, async) + tenacity retries; for static pages use selectolax/lxml or trafilatura; for dynamic pages use Playwright; respect robots via protego; rate‑limit via aiolimiter; normalize URLs via urlcanon. [H1–H8]
- Content extraction & dedup: trafilatura and/or readability‑lxml; dedup via trafilatura LSH or SimHash. [C1–C5]
- Docker: Python 3.13 slim base with multi‑stage; Playwright’s official Docker images when browser needed; optionally distroless for runtime images (trade‑offs). Consider uv in Docker for faster installs. [D1–D6]
- CI/CD (GitHub Actions): setup‑python v6 with pip cache; Semgrep SARIF → upload‑sarif@v3; Gitleaks requires github_token input; Bandit JSON (no SARIF); weekly dependency scan (pip‑audit) + Dependabot optional. [A1–A6]
- Security guardrails (local): pre‑commit with ruff (lint+format), bandit, gitleaks, and fast tests. [S1–S3]

## Package management & project layout
- Use pyproject.toml (PEP 621 metadata) as single source of truth; avoid setup.cfg/requirements*.txt except for thin runtime pin files if needed. [P1–P4]
- uv (Astral) benefits:
  - Drop‑in for pip/pip‑tools/virtualenv; generates uv.lock; very fast resolver/installer. [R2,R3]
  - Great in CI and Docker; official docs include Docker integration patterns. [D1,D2]
- Alternatives:
  - pip (25.2 current) for maximal compatibility; pip‑tools for locks. [P5]
  - Poetry (2.x in 2025) still viable; uv momentum is high; be explicit about lockfiles and workflow if choosing Poetry. [R4,R5]

## Testing framework & portability
- pytest (8.x): mature, best‑of‑breed; keep tests small and deterministic. [T1]
- Coverage & parallel:
  - pytest‑cov for coverage; pytest‑xdist for parallel when tests are CPU‑bound and isolation is guaranteed. Beware shared resources. [T2,T7]
- Network isolation & HTTP mocking:
  - Disable outbound network in tests via pytest‑socket; only allow whitelisted hosts if needed. [T3]
  - Mock HTTP with responses (requests) or requests‑mock; for broader clients, MSW (Node) is an option but not required for Python unit tests. [T4–T6]
- Portability:
  - Use tmp_path for files; avoid OS‑specific paths; enforce encodings; avoid time‑sensitive flakiness; parametrize timeouts. [best practice]

## HTTP clients, retries, rate limits
- httpx vs requests vs aiohttp:
  - httpx offers sync/async unified API; good default timeouts, HTTP/2, proxies; pairs well with tenacity. [H5,H6]
  - requests is still fine for simple sync flows but lacks async; aiohttp still fastest async in some benchmarks. Choose per use‑case. [H1,H2,H7,H8]
- Retries & backoff: use tenacity with jitter for idempotent requests; set low connect/read timeouts (e.g., 3–10s) and explicit max attempts. [H3,H4]
- Rate limiting: aiolimiter (async); use asyncio.Semaphore for concurrency bounds; respect 429/Retry‑After. [H9]

## Scraping & content extraction
- Static HTML parsing: selectolax (fast), lxml, or BeautifulSoup4 with lxml/html5lib backends (trade speed vs tolerance). [E1–E5]
- Text extraction: trafilatura (state of the art in open source) and readability‑lxml. Prefer trafilatura for main‑content extraction. [C1–C3]
- Dynamic pages: Playwright (Python) with headless Chromium/Firefox/WebKit; for CI/containers use official Playwright Docker images. [W1–W5]
- Robots.txt & sitemaps: protego for robots; ultimate‑sitemap‑parser for sitemaps; also urllib.robotparser (stdlib) available. [Rbt1,S1]
- URL canonicalization: iipc/urlcanon or url-normalize/werkzeug helpers. [U1]
- Dedup: trafilatura’s built‑in LSH or SimHash (python-simhash libs). [C4,C5]

## Docker images & build strategy
- Base images: python:3.13-slim (Debian trixie/bookworm) minimal runtime; ensure system deps for lxml/selectolax/Playwright as needed. [D3]
- Multi‑stage:
  - Builder: install build deps, compile wheels, run tests.
  - Runtime: copy wheels/venv/app only; drop compilers/headers. [best practice]
- Playwright containers: use official playwright.dev Dockerfiles (noble) with preinstalled browsers & deps. [W3]
- Distroless: smaller attack surface but debugging harder; consider only for stable services. [D4,D5]
- uv in Docker: follow official guide; cache uv + wheelhouse; pin to uv.lock for reproducibility. [D1,D2]

## CI/CD on GitHub Actions (2025)
- setup‑python v6: supports caching for pip/pipenv/poetry; avoid cache when no lock/constraints found. [A1,A2]
- Dependency caching: rely on setup‑python cache or actions/cache keyed by lockfile+Python version. [A3,A4]
- SAST/Secrets:
  - Semgrep OSS → SARIF → github/codeql‑action/upload‑sarif@v3; rules tuned via .semgrep.yml. [G1–G3]
  - Gitleaks GitHub Action requires github_token input on PRs; optional org license; keep SARIF as artifact or upload if desired. [K1–K3]
  - Bandit: JSON only (no SARIF). Aggregate in job summary or artifact. [B1–B5]
- Weekly dependency checks: pip‑audit (Python), npm audit (if Node parts); optionally Dependabot for PRs. [practice]
- Pre‑commit in CI: run ruff check/format, bandit, gitleaks to enforce local guardrails server‑side. [S1–S3]

## Security posture (local + CI)
- Local (Sentry layer): pre‑commit hooks with ruff (lint+format), bandit, gitleaks, and a lightweight pytest target. [S1]
- CI (Crucible): build, test, coverage, packaging checks; (Security‑scan): semgrep, bandit, gitleaks; (Gauntlet): placeholder for E2E; (Helios): weekly dependency check. [G1,K1,B1]

## Implementation guidance for portability
- Tests: Avoid live network; enforce via pytest‑socket; mock HTTP with responses/requests‑mock. Normalize paths with pathlib. Avoid sleeps; use timeouts and fakes.
- Scraping: Feature‑flag dynamic/browser path; default to static extraction. Respect robots and rate limits. Centralize timeouts, retries, UA, headers.
- Docker: Fail early on missing system deps; build multi‑stage; consider separate image flavors (with/without browsers).
- CI: Make steps idempotent; tolerate tool changes (pin major versions); capture SARIF/JSON artifacts consistently.

## Action checklist (proposed)
1) Adopt uv + pyproject/uv.lock in dev/CI/Docker; keep pip fallbacks.
2) Standardize httpx + tenacity; centralize settings (timeouts, retries, UA).
3) Use trafilatura by default; fallback to readability‑lxml; add selectolax for structure queries.
4) Add protego, ultimate‑sitemap‑parser, urlcanon; add aiolimiter.
5) Dockerize with python:3.13‑slim; provide optional Playwright image; consider distroless runtime for APIs.
6) Actions: setup‑python v6, cache pip; Semgrep→SARIF; Gitleaks with token; Bandit JSON; weekly pip‑audit; pre‑commit checks.
7) Tests: pytest‑socket, responses/requests‑mock, pytest‑cov; optional xdist where safe.

---

## References
- Python 3.13: [What's New 3.13](https://docs.python.org/3/whatsnew/3.13.html), [3.13.7 Release](https://www.python.org/downloads/release/python-3137/)
- Requests/httpx/retries: [ZenRows (requests retry)](https://www.zenrows.com/blog/python-requests-retry), [BetterStack (httpx)](https://betterstack.com/community/guides/scaling-python/httpx-explained/)
- pytest & plugins: [pytest docs](https://pytest.org/), [pytest changelog](https://docs.pytest.org/en/stable/changelog.html), [pytest‑cov](https://pypi.org/project/pytest-cov/), [pytest‑socket](https://github.com/miketheman/pytest-socket)
- HTTP mocking: [responses](https://pypi.org/project/responses/), [requests‑mock](https://github.com/jamielennox/requests-mock)
- Playwright & Docker: [Playwright Docker (Python)](https://playwright.dev/python/docs/docker), [Playwright release notes](https://playwright.dev/docs/release-notes)
- Content extraction: [Trafilatura docs](https://trafilatura.readthedocs.io/), [Trafilatura evaluation](https://trafilatura.readthedocs.io/en/latest/evaluation.html), [readability‑lxml](https://pypi.org/project/readability-lxml/)
- Parsers & limits: [selectolax vs bs4 (overview)](https://scrape.do/blog/python-web-scraping-library/), [BeautifulSoup docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- Robots & sitemaps: [protego](https://github.com/scrapy/protego), [urllib.robotparser](https://docs.python.org/3/library/urllib.robotparser.html), [ultimate‑sitemap‑parser](https://pypi.org/project/ultimate-sitemap-parser/)
- URL normalization: [iipc/urlcanon](https://github.com/iipc/urlcanon)
- Retries & rate limits: [tenacity guide](https://leapcell.io/blog/enhancing-python-applications-with-tenacity), [aiolimiter](https://github.com/mjpieters/aiolimiter)
- Docker: [uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/), [distroless images](https://github.com/GoogleContainerTools/distroless)
- GitHub Actions: [setup‑python](https://github.com/actions/setup-python), [Building & testing Python](https://docs.github.com/actions/guides/building-and-testing-python), [Dependency caching](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- Semgrep & SARIF: [Sample CI configs](https://semgrep.dev/docs/semgrep-ci/sample-ci-configs), [Upload SARIF](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github)
- Gitleaks: [gitleaks-action](https://github.com/gitleaks/gitleaks-action), [Marketplace listing](https://github.com/marketplace/actions/gitleaks)
- Bandit: [PyPI](https://pypi.org/project/bandit/)
- Ruff & pre‑commit: [ruff](https://github.com/astral-sh/ruff), [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)

