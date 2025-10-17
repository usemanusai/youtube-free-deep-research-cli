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
