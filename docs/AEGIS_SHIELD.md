# Aegis Shield: Runtime Monitoring & Structured Logging

This project includes:
- JSON structured logs via structlog (pretty console in development)
- Health endpoints:
  - `GET /api/v1/health/live` (liveness)
  - `GET /api/v1/health/ready` (readiness with DB and optional Redis)

## Configuration (env vars)

- `LOG_LEVEL`: INFO|DEBUG|WARNING|ERROR (default: INFO)
- `LOG_FORMAT`: json|pretty (default: json)
- `HEALTH_CHECK_REDIS`: true|false (default: false)

## Quick test

```bash
# Start API (from repo root)
python youtube_chat_cli_main/run_api_server.py

# Liveness
curl -s http://localhost:8000/api/v1/health/live | jq

# Readiness
curl -s http://localhost:8000/api/v1/health/ready | jq
```

## Notes

- Uvicorn access logs are reduced to avoid duplicates with structlog.
- Redis check is disabled by default. Enable by setting `HEALTH_CHECK_REDIS=true` and ensure Redis is reachable.

