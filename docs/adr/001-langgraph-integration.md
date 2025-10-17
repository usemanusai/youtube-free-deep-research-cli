# ADR 001: LangGraph Integration for Nexus Workflows

## Status
Accepted

## Context
We migrated Flowise workflows into native Python to remove external orchestrators while retaining agent behavior. We need a maintainable, observable state machine to express control flow, bounded loops, and routing.

## Decision
Adopt LangGraph to structure both workflows (deep_research, content_checks) as compiled graphs with explicit nodes and conditional edges. All former `run()` logic is moved into node functions; public `run()` now invokes the compiled graph to preserve API/CLI contracts.

## Consequences
- Clear stage boundaries for timing/metrics
- Easier to test nodes in isolation and mock dependencies
- Deterministic routing with bounded loops
- Minimal external runtime requirements when LangGraph is present; fallback paths maintain compatibility

## Alternatives Considered
- Manual function pipeline: harder to visualize and evolve
- Async task queue: overkill for current in-process orchestration

## Follow-ups
- Add correlation IDs and per-node timing in state
- Persist intermediate state when `NEXUS_DEBUG=true`

