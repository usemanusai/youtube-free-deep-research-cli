# Architecture Overview

## Workflows

```mermaid
flowchart LR
  subgraph DeepResearch
    A[User Topic] --> B[Topic Enhancer]
    B --> C[Search Aggregator]
    C --> D[Agent 0]
    D <--> E[Agent 1]
    E --> F[Session Persistence]
    F --> G[Output]
  end

  subgraph ContentChecks
    H[User Topic] --> I[Deep Research]
    I --> J[Vector Duplicate Check]
    J --> K{NOVEL or REDUNDANT}
    K -- NOVEL --> L[Synthesizer] --> M[Session Persistence]
    K -- REDUNDANT --> N[Prompt Refinement] --> I
  end
```

## Components

- CLI / API → Workflows
- Workflows → Services (LLM, Search, Scraper, Vector Store)
- Services → Database (SQLite)
- BackgroundService → GDrive → Queue → Vector Store

