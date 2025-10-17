# ADR 002: Duplicate Detection Strategy

## Context
We need to route Content Checks as NOVEL vs REDUNDANT. The archive consists of vectorized chunks with metadata (including created_at when available).

## Decision
- Use vector similarity search (top_k=5) against GDrive-sourced items.
- Apply exponential time decay to similarity scores using half-life (env: DUPLICATE_TIME_DECAY_HALF_LIFE_DAYS, default 180).
- Compare max(decayed_scores) to threshold (env: DUPLICATE_SIMILARITY_REDUNDANT, default 0.85) to decide.
- Surface evidence payload for transparency (hits, max score, threshold).

## Consequences
- Recent documents are favored in redundancy detection.
- Requires vector store availability; failure degrades gracefully to NOVEL.
- Threshold and half-life are configurable via .env.

