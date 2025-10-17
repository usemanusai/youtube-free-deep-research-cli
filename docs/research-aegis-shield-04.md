# Aegis Shield Scaffolding — Phase 1 Research (Runtime Monitoring & Logging)

Date: 2025-10-03
Scope: FastAPI (Python 3.13) runtime health checks and structured JSON logging using open‑source, free, CPU‑efficient libraries.

## Executive Summary
- Adopt structured logging with structlog + stdlib logging, JSON output by default.
- Introduce dual health endpoints:
  - Liveness: GET /health/live – constant 200 OK, no dependencies.
  - Readiness: GET /health/ready – shallow dependency checks (DB/Redis/circuit breakers), sub‑5ms budget.
- Keep overhead minimal: no external calls, no I/O beyond quick pings; avoid LLM/vector operations.
- Provide env flags to switch pretty console logs in dev vs JSON in prod, and to enable/disable Redis checks.

## Library Selection & Justification
- structlog (MIT) — Mature, well‑maintained, integrates with stdlib logging, flexible processors, JSONRenderer, ContextVars. Fast enough for high‑throughput services.
  - PyPI shows active releases through 2025. Community guidance recommends structlog for structured JSON.
- Avoid python-json-logger as primary: had CVE (2025‑03) and recent maintainer changes; structlog covers JSON formatting without it.
- Avoid loguru as primary: great DX, but global singleton and non‑stdlib compatibility can complicate integration in larger apps; performance similar class, but structlog offers clearer stdlib bridge.
- FastAPI stays as is; we add a router for health checks plus a lightweight request/response logging middleware (optional).

## Performance Expectations (targets)
- Logging overhead: ~< 1–2 ms per log event on typical x86 dev hardware when using JSONRenderer; negligible when log level filters out.
- Health endpoints:
  - /health/live: ~< 1 ms (constant payload)
  - /health/ready: ~2–5 ms (SQLite existence check, optional Redis PING with short timeout, circuit breaker snapshot in‑process)
- Resource budget: < 50 MB incremental memory; < 5% CPU at typical dev/test loads.

## Health Check Best Practices (applied)
- Separate liveness (process is up) from readiness (dependencies OK).
- Keep checks fast and shallow; never call LLMs, crawlers, or vector search.
- Return machine‑readable JSON with per‑check status and durations.
- Do not fail liveness; readiness may return 503 when a critical dependency is down.
- Timebox external pings (e.g., Redis) to small timeouts (e.g., 50–100 ms) and make them optional.

## Proposed Endpoints & Payloads
- GET /health/live → 200 OK
  ```json
  {"status":"ok","timestamp":"2025-10-03T12:34:56Z"}
  ```
- GET /health/ready → 200 OK or 503 Service Unavailable
  ```json
  {
    "status":"ok|degraded|error",
    "timestamp":"2025-10-03T12:34:56Z",
    "checks":{
      "database":{"status":"ok|error","detail":"path or message","duration_ms":0.5},
      "redis":{"status":"ok|skip|error","detail":"pong|disabled|message","duration_ms":0.7},
      "circuit_breakers":{"status":"ok","open":0,"total":N,"duration_ms":0.1}
    },
    "durations_ms":{"total":2.1}
  }
  ```

## Integration Plan (Phase 2 preview, no code yet)
- Create module youtube_chat_cli_main/api/health.py providing a FastAPI APIRouter with /health/live and /health/ready.
  - DB probe: lightweight existence/heartbeat (e.g., quick read or connection acquisition) using existing get_database().
  - Redis probe: only if config.redis_enabled; perform ping with small timeout and catch exceptions.
  - Circuit breaker snapshot: reuse core.circuit_health.snapshot() if available; otherwise return counts from in‑memory registry.
- Add router include in api_server.py with prefix /api/v1 (or adjust existing root links accordingly). We will avoid breaking the simple /api/v1/health already present by preserving it and mapping it to /health/live for backward compatibility.
- Logging: add youtube_chat_cli_main/core/logging_config.py to configure structlog + stdlib once at startup.
  - JSON in production; pretty console in development.
  - Include fields: ts, level, event, logger, request_id, path, method, status, duration_ms (for access logs).
  - Optional request/response logging middleware capturing timing and status.

## Installation Commands (copy‑paste ready)
Python (app root virtualenv):
```
pip install -U structlog orjson
# orjson optional but recommended for faster JSON serialization
```
Optional (only if Redis client missing; adapt to project’s existing client):
```
pip install -U redis
```

## Configuration (Environment Variables)
- LOG_LEVEL=INFO|DEBUG|WARNING (default INFO)
- LOG_FORMAT=json|pretty (default json in prod, pretty in dev)
- HEALTH_CHECK_REDIS=true|false (default false; auto‑enable if redis_enabled config is true)
- HEALTH_TIMEOUT_MS=100 (cap per dependency probe)

## Verification Plan (Phase 2 follow‑up)
- Start app; verify that logs are JSON (prod) or pretty (dev) and include request_id.
- curl tests:
  - `curl -s localhost:8000/api/v1/health/live | jq .`
  - `curl -s -i localhost:8000/api/v1/health/ready`
- Degrade Redis (if enabled) and confirm /ready returns 503 with `redis.status=error` while /live remains 200.
- Load test endpoints (e.g., `hey -n 1000 -c 50 http://localhost:8000/api/v1/health/live`) to confirm sub‑5ms median.

## Compatibility & Licensing
- structlog: MIT; active releases through 2025; Python 3.13 compatible.
- FastAPI: actively maintained; latest releases in 2025; Python 3.13 support as of Pydantic v2 stack.
- Redis Python client (redis-py): MIT; widely used.
- orjson: Apache‑2.0; optional, widely used in FastAPI stacks for faster JSON.
- All choices are open‑source and free to use.

## Alternatives Considered
- loguru: simpler API, but deviates from stdlib; acceptable as a secondary sink, not primary.
- python-json-logger: directly formats stdlib logs as JSON, but recent CVE and less flexible processing pipeline vs structlog.
- Keeping stdlib only: simplest, but loses structured context and consistent JSON formatting across app and dependencies.

## Risks & Mitigations
- Duplicate Uvicorn/FastAPI logs: ensure we configure logging once and avoid double handlers; optionally disable Uvicorn’s default access log and emit our own structured access logs.
- Slow probes causing readiness slowness: enforce small timeouts and never block on external networks.
- Windows/WSL differences: all libraries are pure Python or provide wheels; no compilation expected.

## Sources & Pointers (representative)
- FastAPI PyPI (latest 2025 release)
- structlog PyPI and GitHub (active 2025)
- Community guides on structlog + FastAPI + Uvicorn JSON logging
- Best practices for liveness/readiness health checks in web services

---
This document completes Phase 1 for Integration Prompt #4. On approval, Phase 2 will implement: health.py router (+tests), logging_config.py, env wiring, minimal edits to api_server.py, and verification steps.

