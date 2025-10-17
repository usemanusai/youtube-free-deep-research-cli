# N8N Integration Guide

Complete guide to integrating YouTube Free Deep Research CLI with N8N workflows.

## Overview

N8N is a workflow automation platform. This guide shows how to integrate with the API.

## Setup

### 1. Start N8N

```bash
# Using Docker
docker run -it --rm \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Visit http://localhost:5678
```

### 2. Create Webhook

In N8N:
1. Create new workflow
2. Add "Webhook" node
3. Set method to POST
4. Copy webhook URL

### 3. Configure API

```bash
# Set N8N webhook URL
export N8N_WEBHOOK_URL=http://localhost:5678/webhook/your-webhook-id

# Set N8N API key (if needed)
export N8N_API_KEY=your_api_key
```

## Basic Workflow

### 1. Receive Message

```json
{
  "type": "webhook",
  "method": "POST",
  "path": "/webhook/chat"
}
```

### 2. Call API

```json
{
  "type": "http",
  "method": "POST",
  "url": "http://localhost:8556/api/chat/message",
  "body": {
    "session_id": "{{ $json.session_id }}",
    "message": "{{ $json.message }}"
  }
}
```

### 3. Process Response

```json
{
  "type": "set",
  "value": {
    "response": "{{ $json.response }}",
    "tokens": "{{ $json.tokens_used }}"
  }
}
```

### 4. Send Response

```json
{
  "type": "webhook",
  "method": "POST",
  "url": "{{ $json.callback_url }}",
  "body": {
    "response": "{{ $json.response }}"
  }
}
```

## Advanced Workflows

### File Processing Workflow

```
1. Receive file upload
2. Upload to API (/api/files/upload)
3. Extract text
4. Index in RAG
5. Send confirmation
```

### Search and Chat Workflow

```
1. Receive search query
2. Search web (/api/search/web)
3. Search vector store (/api/search/vector)
4. Combine results
5. Generate response (/api/chat/message)
6. Send response
```

### Background Job Workflow

```
1. Receive job request
2. Create background job
3. Poll job status (/api/jobs/{job_id})
4. When complete, process results
5. Send notification
```

## N8N Nodes

### HTTP Request Node

```javascript
// Configuration
{
  "method": "POST",
  "url": "http://localhost:8556/api/chat/message",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "session_id": "{{ $json.session_id }}",
    "message": "{{ $json.message }}"
  }
}
```

### Set Node

```javascript
// Set variables
{
  "response": "{{ $json.response }}",
  "tokens": "{{ $json.tokens_used }}",
  "timestamp": "{{ $now.toISOString() }}"
}
```

### Conditional Node

```javascript
// Check response
if ($json.response && $json.response.length > 0) {
  return true;
} else {
  return false;
}
```

### Loop Node

```javascript
// Process multiple items
{
  "items": "{{ $json.results }}",
  "iterations": "{{ $json.results.length }}"
}
```

## Error Handling

### Retry Logic

```json
{
  "type": "http",
  "url": "http://localhost:8556/api/chat/message",
  "retry": {
    "maxRetries": 3,
    "delay": 1000,
    "backoff": 2
  }
}
```

### Error Catch

```javascript
// Catch errors
try {
  // API call
} catch (error) {
  // Send error notification
  return {
    "error": error.message,
    "status": "failed"
  };
}
```

## Examples

### Example 1: Simple Chat

```
Webhook (receive message)
  ↓
HTTP Request (POST /api/chat/message)
  ↓
Set (format response)
  ↓
Webhook (send response)
```

### Example 2: File Upload and Search

```
Webhook (receive file)
  ↓
HTTP Request (POST /api/files/upload)
  ↓
HTTP Request (POST /api/search/vector)
  ↓
Set (combine results)
  ↓
Webhook (send results)
```

### Example 3: Scheduled Job

```
Cron (every hour)
  ↓
HTTP Request (GET /api/jobs)
  ↓
Loop (process each job)
  ↓
HTTP Request (POST /api/jobs/{id}/process)
  ↓
Webhook (send notification)
```

## Testing

### Test Webhook

```bash
# Send test request
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "message": "Hello"
  }'
```

### Test API Integration

```bash
# In N8N, use "Test" button to verify workflow
# Check logs for errors
# Use "Debug" mode for detailed output
```

## Monitoring

### View Workflow Executions

1. Open workflow
2. Click "Executions" tab
3. View execution history
4. Check logs for errors

### Enable Logging

```javascript
// Add logging node
{
  "type": "log",
  "message": "Processing: {{ $json }}"
}
```

## Best Practices

1. **Error Handling** - Always add error catch nodes
2. **Retry Logic** - Implement retry for API calls
3. **Logging** - Log important steps
4. **Testing** - Test workflows before production
5. **Monitoring** - Monitor execution history
6. **Documentation** - Document workflow purpose

## Troubleshooting

### Webhook Not Triggering

```bash
# Check webhook URL
# Verify method is POST
# Check N8N logs
docker logs n8n
```

### API Connection Error

```bash
# Check API is running
curl http://localhost:8556/health/live

# Check firewall
# Verify URL in N8N

# Check logs
docker logs jaegis-api
```

### Timeout Error

```bash
# Increase timeout in HTTP node
# Check API performance
# Reduce payload size
```

## Advanced Integration

### Custom Functions

```javascript
// In N8N Function node
return {
  "processed": $json.data.map(item => ({
    ...item,
    processed_at: new Date().toISOString()
  }))
};
```

### Conditional Routing

```javascript
// Route based on response
if ($json.response.includes("error")) {
  return [[], [$json]];  // Send to error handler
} else {
  return [[$json], []];  // Send to success handler
}
```

### Data Transformation

```javascript
// Transform data
return {
  "formatted_response": $json.response.toUpperCase(),
  "word_count": $json.response.split(" ").length,
  "timestamp": new Date().toISOString()
};
```

---

See [REST API](../api/rest-api.md) for API endpoints.

