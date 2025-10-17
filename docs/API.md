# Nexus Agents API

## POST /api/v1/nexus-agents/deep-research
- Body: {"topic": string, "max_turns"?: number, "backends"?: string[]}
- 200 Response: { transcript: Turn[], artifacts: object, started_at: string, ended_at: string, topic: string, enhanced_topic: string, max_turns: number }

## POST /api/v1/nexus-agents/content-check
- Body: {"topic": string, "max_loops"?: number}
- 200 Response: { decision: string, output: object, loop_count: number, evidence: object, started_at: string, ended_at: string, topic: string, max_loops: number, conversation: object }

## GET /api/v1/nexus-agents/sessions
- Query: limit (int, default 50), offset (int, default 0), workflow_type (optional: deep_research | content_checks)
- 200 Response:
```
{
  "sessions": [{"id": string, "name": string, "workflow_id": string, "created_at": string, "updated_at": string, "metadata": object}],
  "total": number,
  "limit": number,
  "offset": number
}
```

## GET /api/v1/nexus-agents/sessions/{session_id}
- Path: session_id (UUID)
- 200 Response:
```
{
  "session": { ... },
  "messages": [{"id": number, "role": string, "content": string, "metadata": object, "created_at": string}]
}
```
- 400: Invalid session_id
- 404: Not found

## GET /api/v1/nexus-agents/archive/status
- 200 Response:
```
{
  "total_vectors": number,
  "gdrive_vectors": number,
  "last_sync_time": string|null,
  "indexing_status": "idle"|"in_progress"|"completed"|"failed",
  "files_indexed": number,
  "files_pending": number|null
}
```

## POST /api/v1/nexus-agents/archive/reindex
- Body: {"force": boolean}
- 200 Response: {"job_id": string, "status": "started", "message": string}



## GET /api/v1/nexus-agents/archive/queue
- 200 Response: { total: number, by_status: object, by_source: object, by_file_type: object, by_age: object, by_retry_count: object }

## GET /api/v1/nexus-agents/workflows/{workflow_id}/trace
- 200 Response: { workflow_id: string, traces: {workflow_id, workflow_type, stage, state, created_at}[] }

## POST /api/v1/nexus-agents/batch-research
- Body: { topics: string[], max_turns?: number }
- 200 Response: { items: { topic: string, result: object }[] }
