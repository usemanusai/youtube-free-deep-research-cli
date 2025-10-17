# JAEGIS Nexus Agents: Deep Research and Content Checks

This document describes the native Python implementations of the Flowise workflows for Deep Research and Content Checks integrated into youtube-chat-cli-main.

## Configuration (.env)

- BRAVE_API_KEY
- SEARCH_BACKENDS (default: "brave,legacy")
- SCRAPER_DEPTH (default: 1)
- SCRAPER_MAX_PAGES (default: 50)
- SCRAPER_TIMEOUT_S (default: 60)
- SCRAPER_HEADLESS (default: true)
- SCRAPER_USER_AGENT (default: JAEGIS-NexusScraper/1.0)
- SCRAPER_RESPECT_ROBOTS (default: true)
- SCRAPER_RATE_LIMIT_QPS (default: 0.5)
- DUPLICATE_SIMILARITY_REDUNDANT (default: 0.85)
- DUPLICATE_SIMILARITY_OVERLAP (default: 0.70)
- DUPLICATE_TIME_WINDOW_DAYS (default: 365)
- NEXUS_MAX_TURNS (default: 100)
- NEXUS_MAX_LOOPS (default: 10)

## CLI

- agents deep-research --topic "..." [--max-turns N]
- agents content-check --topic "..." [--max-loops N]
- agents archive-sync [--dry-run]

## API

- POST /api/v1/nexus-agents/deep-research {"topic": str, "max_turns": int|null, "backends": [str]}
- POST /api/v1/nexus-agents/content-check {"topic": str, "max_loops": int|null}

## Notes

- Web scraper uses Playwright if installed, otherwise requests fallback. Respects robots.txt when enabled.
- Hybrid web search: Brave + legacy (Tavily/DDG) with recency-aware ranking.
- Duplicate detection consults vector store (filter {source: 'gdrive'}) with thresholds from config.
- Sessions (transcripts) are persisted to SQLite.

