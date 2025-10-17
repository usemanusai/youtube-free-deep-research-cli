# MCP Server Integration Guide

Complete guide to the Model Context Protocol (MCP) server for Claude Desktop integration.

## Overview

The MCP server allows Claude Desktop to interact with YouTube Free Deep Research CLI through a standardized protocol.

## Installation

### 1. Install MCP Server

```bash
# From npm
npm install -g jaegis-youtube-chat-mcp

# Or from source
cd jaegis-youtube-chat-mcp
npm install
npm run build
npm link
```

### 2. Configure Claude Desktop

Edit `~/.claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jaegis": {
      "command": "jaegis-youtube-chat-mcp",
      "args": [],
      "env": {
        "API_URL": "http://localhost:8556",
        "OPENROUTER_API_KEYS": "your-keys-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

## Available Tools

### Chat Tools

#### send_message

Send a message to the chat API.

```json
{
  "name": "send_message",
  "description": "Send a message to the chat API",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Session ID"
      },
      "message": {
        "type": "string",
        "description": "Message to send"
      },
      "stream": {
        "type": "boolean",
        "description": "Stream response"
      }
    },
    "required": ["session_id", "message"]
  }
}
```

**Usage in Claude**:
```
Use the send_message tool to ask a question:
- session_id: "my-session"
- message: "What is machine learning?"
```

### File Tools

#### upload_file

Upload a file to the API.

```json
{
  "name": "upload_file",
  "description": "Upload a file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Path to file"
      }
    },
    "required": ["file_path"]
  }
}
```

#### list_files

List uploaded files.

```json
{
  "name": "list_files",
  "description": "List uploaded files",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "Number of files"
      }
    }
  }
}
```

#### download_file

Download a file.

```json
{
  "name": "download_file",
  "description": "Download a file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_id": {
        "type": "string",
        "description": "File ID"
      },
      "output_path": {
        "type": "string",
        "description": "Output path"
      }
    },
    "required": ["file_id"]
  }
}
```

### Search Tools

#### web_search

Search the web.

```json
{
  "name": "web_search",
  "description": "Search the web",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "limit": {
        "type": "integer",
        "description": "Number of results"
      }
    },
    "required": ["query"]
  }
}
```

#### vector_search

Search vector store.

```json
{
  "name": "vector_search",
  "description": "Search vector store",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "limit": {
        "type": "integer",
        "description": "Number of results"
      }
    },
    "required": ["query"]
  }
}
```

### RAG Tools

#### index_documents

Index documents for RAG.

```json
{
  "name": "index_documents",
  "description": "Index documents",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to documents"
      }
    },
    "required": ["path"]
  }
}
```

#### rag_query

Query RAG engine.

```json
{
  "name": "rag_query",
  "description": "Query RAG engine",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Query"
      },
      "top_k": {
        "type": "integer",
        "description": "Number of results"
      }
    },
    "required": ["query"]
  }
}
```

## Usage Examples

### Example 1: Ask a Question

```
User: "What is machine learning?"

Claude uses send_message tool:
- session_id: "default"
- message: "What is machine learning?"

Claude receives response and presents it to user.
```

### Example 2: Upload and Search

```
User: "Upload this PDF and search for key findings"

Claude:
1. Uses upload_file tool with file path
2. Gets file_id from response
3. Uses vector_search tool to find "key findings"
4. Presents results to user
```

### Example 3: RAG Query

```
User: "Index my documents and answer questions about them"

Claude:
1. Uses index_documents tool with folder path
2. Uses rag_query tool with user's question
3. Presents answer with source documents
```

## Configuration

### Environment Variables

```bash
# API Configuration
API_URL=http://localhost:8556
API_TIMEOUT=30

# OpenRouter Keys
OPENROUTER_API_KEYS=key1,key2,...,key31

# Logging
LOG_LEVEL=INFO
```

### MCP Server Config

```json
{
  "mcpServers": {
    "jaegis": {
      "command": "jaegis-youtube-chat-mcp",
      "args": ["--port", "3000"],
      "env": {
        "API_URL": "http://localhost:8556",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Troubleshooting

### MCP Server Not Connecting

**Error**: `Failed to connect to MCP server`

**Solution**:
```bash
# Check if server is running
jaegis-youtube-chat-mcp --version

# Check configuration
cat ~/.claude_desktop_config.json

# Restart Claude Desktop
# Close and reopen Claude
```

### API Connection Error

**Error**: `Failed to connect to API`

**Solution**:
```bash
# Check if API is running
curl http://localhost:8556/health/live

# Check API URL in config
# Verify firewall allows connection

# Increase timeout
# Edit config and set API_TIMEOUT=60
```

### Tool Not Available

**Error**: `Tool not found`

**Solution**:
```bash
# Check MCP server logs
# Restart Claude Desktop

# Verify tool is registered
jaegis-youtube-chat-mcp --list-tools
```

## Development

### Build from Source

```bash
# Clone repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd jaegis-youtube-chat-mcp

# Install dependencies
npm install

# Build
npm run build

# Link locally
npm link
```

### Add New Tool

```typescript
// src/tools/my-tool.ts
export const myTool = {
  name: "my_tool",
  description: "My tool description",
  inputSchema: {
    type: "object",
    properties: {
      param: {
        type: "string",
        description: "Parameter"
      }
    },
    required: ["param"]
  },
  handler: async (input) => {
    // Implementation
    return result;
  }
};
```

### Test Tool

```bash
# Run tests
npm test

# Test specific tool
npm test -- my-tool.test.ts
```

## Best Practices

1. **Error Handling** - Always handle errors gracefully
2. **Timeouts** - Set appropriate timeouts
3. **Logging** - Enable logging for debugging
4. **Testing** - Test tools thoroughly
5. **Documentation** - Document tool usage
6. **Performance** - Optimize for speed

## Advanced Usage

### Custom Tool Implementation

```typescript
// Implement custom tool
const customTool = {
  name: "custom_tool",
  handler: async (input) => {
    // Call API
    const response = await fetch(`${API_URL}/api/custom`, {
      method: "POST",
      body: JSON.stringify(input)
    });
    return response.json();
  }
};
```

### Tool Chaining

```
Claude can chain multiple tools:
1. upload_file → get file_id
2. index_documents → index file
3. rag_query → query indexed documents
4. send_message → generate response
```

---

See [REST API](../api/rest-api.md) for API endpoints.

