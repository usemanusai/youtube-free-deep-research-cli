# REST API Reference

Complete REST API documentation for YouTube Free Deep Research CLI.

## Base URL

```
http://localhost:8556
```

## Authentication

Currently, the API does not require authentication. In production, add API key authentication:

```bash
# Header
Authorization: Bearer YOUR_API_KEY
```

## Health Endpoints

### Liveness Probe

```http
GET /health/live
```

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-10-17T12:00:00Z"
}
```

### Readiness Probe

```http
GET /health/ready
```

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-10-17T12:00:00Z",
  "services": {
    "database": "ok",
    "vector_store": "ok",
    "llm": "ok"
  }
}
```

## Chat Endpoints

### Start Chat Session

```http
POST /api/chat/session
Content-Type: application/json

{
  "session_id": "optional-session-id",
  "system_prompt": "optional-system-prompt"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "created_at": "2025-10-17T12:00:00Z",
  "status": "active"
}
```

### Send Message

```http
POST /api/chat/message
Content-Type: application/json

{
  "session_id": "uuid",
  "message": "Your question here",
  "stream": false
}
```

**Response:**
```json
{
  "message_id": "uuid",
  "response": "AI response here",
  "tokens_used": 150,
  "timestamp": "2025-10-17T12:00:00Z"
}
```

### Stream Message

```http
POST /api/chat/message
Content-Type: application/json

{
  "session_id": "uuid",
  "message": "Your question here",
  "stream": true
}
```

**Response (Server-Sent Events):**
```
data: {"chunk": "AI response", "tokens": 10}
data: {"chunk": " chunk", "tokens": 2}
...
```

## File Endpoints

### Upload File

```http
POST /api/files/upload
Content-Type: multipart/form-data

file: <binary-file>
```

**Response:**
```json
{
  "file_id": "uuid",
  "filename": "document.pdf",
  "size": 1024000,
  "mime_type": "application/pdf",
  "uploaded_at": "2025-10-17T12:00:00Z"
}
```

### List Files

```http
GET /api/files?limit=10&offset=0
```

**Response:**
```json
{
  "files": [
    {
      "file_id": "uuid",
      "filename": "document.pdf",
      "size": 1024000,
      "uploaded_at": "2025-10-17T12:00:00Z"
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

### Download File

```http
GET /api/files/{file_id}/download
```

**Response:** Binary file content

### Delete File

```http
DELETE /api/files/{file_id}
```

**Response:**
```json
{
  "status": "deleted",
  "file_id": "uuid"
}
```

## Search Endpoints

### Web Search

```http
POST /api/search/web
Content-Type: application/json

{
  "query": "search query",
  "limit": 10,
  "include_snippets": true
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "snippet": "Result snippet...",
      "rank": 1
    }
  ],
  "total": 42,
  "query": "search query"
}
```

### Vector Search

```http
POST /api/search/vector
Content-Type: application/json

{
  "query": "search query",
  "limit": 5,
  "threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "uuid",
      "content": "Relevant content...",
      "score": 0.95,
      "metadata": {}
    }
  ],
  "total": 5
}
```

## Configuration Endpoints

### Get Configuration

```http
GET /api/config
```

**Response:**
```json
{
  "api_version": "2.0.1",
  "python_version": "3.13.0",
  "services": {
    "llm": "openrouter",
    "tts": "edge-tts",
    "rag": "enabled"
  }
}
```

### Update Configuration

```http
PATCH /api/config
Content-Type: application/json

{
  "default_tts_engine": "melotts",
  "log_level": "DEBUG"
}
```

**Response:**
```json
{
  "status": "updated",
  "changes": {
    "default_tts_engine": "melotts",
    "log_level": "DEBUG"
  }
}
```

## Background Job Endpoints

### List Jobs

```http
GET /api/jobs?status=running&limit=10
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "uuid",
      "status": "running",
      "progress": 45,
      "created_at": "2025-10-17T12:00:00Z"
    }
  ],
  "total": 5
}
```

### Get Job Status

```http
GET /api/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "result": {},
  "created_at": "2025-10-17T12:00:00Z",
  "completed_at": "2025-10-17T12:05:00Z"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "bad_request",
  "message": "Invalid request parameters",
  "details": {
    "field": "message",
    "issue": "required field missing"
  }
}
```

### 404 Not Found

```json
{
  "error": "not_found",
  "message": "Resource not found",
  "resource": "session",
  "id": "uuid"
}
```

### 500 Internal Server Error

```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "uuid"
}
```

## Rate Limiting

- **Limit**: 100 requests per minute
- **Header**: `X-RateLimit-Remaining`
- **Reset**: `X-RateLimit-Reset`

## Pagination

All list endpoints support pagination:

```
GET /api/resource?limit=10&offset=0
```

- `limit`: Number of results (default: 10, max: 100)
- `offset`: Number of results to skip (default: 0)

## Sorting

Supported sort parameters:

```
GET /api/resource?sort=created_at&order=desc
```

- `sort`: Field to sort by
- `order`: `asc` or `desc` (default: `asc`)

## Interactive Documentation

Visit `http://localhost:8556/docs` for interactive Swagger UI.

---

See [WebSocket API](websocket-api.md) for real-time endpoints.

