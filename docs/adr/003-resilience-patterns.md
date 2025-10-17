# ADR 003: Resilience Patterns

## Context
External calls (LLM, search, scraper, vector store) can fail transiently. We need guardrails to keep workflows usable.

## Decision
- Introduce `retry_with_backoff` decorator with jitter for transient errors.
- Provide `CircuitBreaker` for repeated failures; can be applied to hot paths as needed.
- Add Dead Letter Queue (DLQ) table for items that exceed retry thresholds in background jobs.
- Add observability via `workflow_traces` for step-level snapshots when `NEXUS_DEBUG=true`.

## Consequences
- Increased robustness against transient errors.
- Slight latency increase due to retries.
- Improved debuggability with correlation-id traces.

