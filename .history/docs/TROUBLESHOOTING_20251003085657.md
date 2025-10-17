# Troubleshooting

- Brave API key not configured
  - Symptom: Brave search returns no results; logs show warning
  - Solution: Set BRAVE_API_KEY in .env

- Vector store unavailable
  - Symptom: Duplicate checks log warning; content-checks defaults to NOVEL
  - Solution: Configure Qdrant or Chroma in .env; ensure service is running

- LLM unavailable
  - Symptom: Workflows return placeholders; warnings in logs
  - Solution: Set OPENROUTER_API_KEY or OPENAI_API_KEY in .env

- Playwright not installed
  - Symptom: Scraper falls back to requests; warning in logs
  - Solution (optional):
    - pip install playwright
    - playwright install chromium

- Scraper blocked by robots.txt
  - Symptom: Error entry "Disallowed by robots.txt"
  - Solution: Set SCRAPER_RESPECT_ROBOTS=false (not recommended in production)

- Session not found
  - Symptom: 404 on GET /sessions/{session_id}
  - Solution: Verify UUID; ensure session exists


## Observability & Debugging
- Enable workflow traces: set NEXUS_DEBUG=true (in .env)
- Use returned correlation_id to fetch traces via CLI `jaegis agents trace <id>` or API `/api/v1/nexus-agents/workflows/<id>/trace`


## Redis Cache Issues
- Symptom: Cache not used; frequent external calls
- Checks:
  - Ensure REDIS_ENABLED=true and REDIS_URL points to a reachable instance
  - `redis-cli PING` should return PONG; API health will still work without Redis
- Fallback: The app gracefully falls back to in-memory TTL cache

## Circuit Breaker Open
- Symptom: LLM/search/vector calls short-circuit with placeholders or cache
- Checks:
  - GET `/api/v1/nexus-agents/health/circuit-breakers` to view breaker state
  - Breakers auto-close after cooldown; repeated failures re-open
- Mitigation:
  - Fix upstream outage; or reduce load; breakers reset automatically

## Performance Tuning
- SQLite PRAGMA: WAL + NORMAL sync + increased cache size applied per connection
- Pool size: `DB_POOL_SIZE` (default 5); `DB_TIMEOUT_S` (default 10)
- Enable Redis for cross-process caching of web search and vector results
