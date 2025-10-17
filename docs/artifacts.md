## Project Vision & Core Requirements
Migrate Flowise agent workflows (Deep Research and Content Checks) into native Python with LangGraph, preserving capabilities while improving observability, resilience, and performance. Provide API/CLI parity, caching, circuit breakers, and documentation.

## Key Concepts & Terminology
- Nexus Agents: Native Python equivalents of Flowise graphs
- Correlation ID: UUID per workflow run for tracing
- Dead Letter Queue (DLQ): Storage for permanently failed jobs
- Redis Cache: Optional distributed cache with in-memory TTL fallback
- Circuit Breaker: Prevents cascading failures for LLM/Search/Vector

## Key Decisions & Designs
- LangGraph orchestration for both workflows
- Optional Redis caching for vector and web search results
- SQLite with connection pooling + WAL PRAGMAs
- Resilience: retry_with_backoff + circuit breakers + DLQ
- Observability: correlation IDs, timing metrics, trace persistence

## Current Status & Next Actions
- Implemented caching, pooling, circuit breakers, trace/health endpoints
- Added test suite coverage (12 passing focused tests)
- Docs and notebooks created
Next: Optionally integrate Redis Search/JSON for native vector KNN; add per-node timing visualization endpoint.

## Technical & Environmental Context
- Python 3.13 on Windows (PowerShell)
- Optional Redis instance (REDIS_ENABLED=true)
- External services (LLM/Brave/Tavily) treated as optional and gracefully degrade

## Session Artifacts Log
- New tests under tests/*.py (12 passing focused tests)
- Updated youtube_chat_cli_main/README.md with Mermaid architecture
- Updated docs/TROUBLESHOOTING.md (Redis, CB, tuning)
- New notebooks in examples/notebooks/*.ipynb
- Config fixes in youtube_chat_cli_main/core/config.py
- Deep Research resilience tweaks in youtube_chat_cli_main/workflows/deep_research.py
- Duplicate score hardening in youtube_chat_cli_main/workflows/content_checks.py

