# Redis 8.2 Integration Plan (Beyond Caching)

## Executive Summary
We currently use Redis as an optional cache for web search and vector search. Redis 8.2 adds production-grade Search/JSON with vector KNN (including the SVS-VAMANA index type with compression). This plan outlines how to evolve from cache-only to native vector storage and query, while keeping graceful fallbacks.

## Relevant Features (Redis 8/8.2)
- Query Engine over Hash/JSON documents with vector fields (KNN)
- JSON document modeling for metadata + vectors
- New SVS-VAMANA vector index type (compression; lower memory footprint)
- Mature search operators (filters, pagination, scoring)

## Proposed Architecture
- Collection key prefix: `vec:docs`
- Each document as JSON with fields:
  - `id`, `source`, `created_at`, `text_snippet`
  - `embedding` (vector field)
- Index definition:
  - Tag/Text indexes for metadata
  - Vector index on `$.embedding` using SVS-VAMANA

## Migration Steps
1. Feature flag: `VECTOR_BACKEND=redis|qdrant|chroma` (default current backend)
2. Writer path: during indexing jobs, compute embeddings and `JSON.SET` the document
3. Index creation: `FT.CREATE` with vector schema + JSON
4. Search path: translate our current `vs.search` into `FT.SEARCH` KNN query with filters
5. Fallback: if Redis unavailable or feature flag disabled, use existing vector store

## Operational Considerations
- TTL not recommended for stored embeddings (persistent knowledge); keep cache TTLs for web+vector query results
- Bulk indexing: use pipelines/batching; monitor memory
- Observability: log index sizes and search latency; expose `/health/search` stats

## Rollout Plan
- Phase 1: Implement feature flag and minimal Redis vector write path
- Phase 2: Implement search path + parity tests (compare top-k results to current store on small sample)
- Phase 3: Backfill indexing job; enable in staging; measure latency, recall
- Phase 4: Optional: enable SVS-VAMANA compression tuning; production rollout

## Risks & Mitigations
- Memory footprint: Start with small K and dimensionality; use compression index
- Query latency: Warm index, measure, and tune index parameters
- Consistency: Ensure reindex invalidates cache prefixes (`vector:*`) to avoid stale results

