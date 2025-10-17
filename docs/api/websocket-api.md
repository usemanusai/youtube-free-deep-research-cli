# WebSocket API Reference

Real-time WebSocket API for YouTube Free Deep Research CLI.

## Connection

```
ws://localhost:8556/ws/chat/{session_id}
```

## Message Format

All messages are JSON:

```json
{
  "type": "message_type",
  "data": {},
  "timestamp": "2025-10-17T12:00:00Z"
}
```

## Client Messages

### Connect

```json
{
  "type": "connect",
  "data": {
    "session_id": "uuid",
    "client_id": "optional-client-id"
  }
}
```

### Send Message

```json
{
  "type": "message",
  "data": {
    "content": "Your message here",
    "stream": true
  }
}
```

### Ping

```json
{
  "type": "ping",
  "data": {}
}
```

### Disconnect

```json
{
  "type": "disconnect",
  "data": {}
}
```

## Server Messages

### Connected

```json
{
  "type": "connected",
  "data": {
    "session_id": "uuid",
    "client_id": "uuid",
    "timestamp": "2025-10-17T12:00:00Z"
  }
}
```

### Message Start

```json
{
  "type": "message_start",
  "data": {
    "message_id": "uuid",
    "timestamp": "2025-10-17T12:00:00Z"
  }
}
```

### Message Chunk

```json
{
  "type": "message_chunk",
  "data": {
    "message_id": "uuid",
    "chunk": "AI response chunk",
    "tokens": 10
  }
}
```

### Message Complete

```json
{
  "type": "message_complete",
  "data": {
    "message_id": "uuid",
    "total_tokens": 150,
    "timestamp": "2025-10-17T12:00:00Z"
  }
}
```

### Pong

```json
{
  "type": "pong",
  "data": {}
}
```

### Error

```json
{
  "type": "error",
  "data": {
    "error": "error_code",
    "message": "Error description",
    "details": {}
  }
}
```

### Disconnected

```json
{
  "type": "disconnected",
  "data": {
    "reason": "client_disconnect",
    "timestamp": "2025-10-17T12:00:00Z"
  }
}
```

## Example: JavaScript Client

```javascript
class ChatClient {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.ws = null;
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8556/ws/chat/${this.sessionId}`);
    
    this.ws.onopen = () => {
      console.log('Connected');
      this.send({
        type: 'connect',
        data: { session_id: this.sessionId }
      });
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Disconnected');
    };
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  sendMessage(content) {
    this.send({
      type: 'message',
      data: { content, stream: true }
    });
  }

  handleMessage(message) {
    switch (message.type) {
      case 'connected':
        console.log('Session connected:', message.data);
        break;
      case 'message_chunk':
        console.log('Chunk:', message.data.chunk);
        break;
      case 'message_complete':
        console.log('Message complete');
        break;
      case 'error':
        console.error('Error:', message.data);
        break;
    }
  }

  disconnect() {
    if (this.ws) {
      this.send({ type: 'disconnect', data: {} });
      this.ws.close();
    }
  }
}

// Usage
const client = new ChatClient('session-uuid');
client.connect();
client.sendMessage('Hello, how are you?');
```

## Example: Python Client

```python
import asyncio
import json
import websockets

class ChatClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.ws = None

    async def connect(self):
        uri = f"ws://localhost:8556/ws/chat/{self.session_id}"
        self.ws = await websockets.connect(uri)
        
        # Send connect message
        await self.send({
            "type": "connect",
            "data": {"session_id": self.session_id}
        })

    async def send(self, message):
        await self.ws.send(json.dumps(message))

    async def send_message(self, content):
        await self.send({
            "type": "message",
            "data": {"content": content, "stream": True}
        })

    async def receive_messages(self):
        async for message in self.ws:
            data = json.loads(message)
            await self.handle_message(data)

    async def handle_message(self, message):
        msg_type = message.get("type")
        
        if msg_type == "message_chunk":
            print(f"Chunk: {message['data']['chunk']}")
        elif msg_type == "message_complete":
            print("Message complete")
        elif msg_type == "error":
            print(f"Error: {message['data']}")

    async def disconnect(self):
        if self.ws:
            await self.send({"type": "disconnect", "data": {}})
            await self.ws.close()

# Usage
async def main():
    client = ChatClient("session-uuid")
    await client.connect()
    await client.send_message("Hello, how are you?")
    await client.receive_messages()

asyncio.run(main())
```

## Connection Management

### Heartbeat

Server sends ping every 30 seconds. Client should respond with pong.

### Timeout

Connection closes after 5 minutes of inactivity.

### Reconnection

Implement exponential backoff for reconnection:

```javascript
let retries = 0;
const maxRetries = 5;
const baseDelay = 1000;

function reconnect() {
  if (retries < maxRetries) {
    const delay = baseDelay * Math.pow(2, retries);
    setTimeout(() => {
      client.connect();
      retries++;
    }, delay);
  }
}
```

## Error Handling

### Connection Errors

```json
{
  "type": "error",
  "data": {
    "error": "connection_error",
    "message": "Failed to establish connection"
  }
}
```

### Message Errors

```json
{
  "type": "error",
  "data": {
    "error": "invalid_message",
    "message": "Message format is invalid"
  }
}
```

### Service Errors

```json
{
  "type": "error",
  "data": {
    "error": "service_error",
    "message": "LLM service is unavailable"
  }
}
```

## Performance Tips

1. **Batch Messages** - Send multiple messages in one connection
2. **Stream Responses** - Use streaming for large responses
3. **Reconnect Gracefully** - Implement exponential backoff
4. **Monitor Heartbeat** - Ensure ping/pong is working
5. **Handle Errors** - Implement proper error handling

---

See [REST API](rest-api.md) for HTTP endpoints.

