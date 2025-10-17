# 🔌 JAEGIS NexusSync - MCP Server Setup Guide

Complete guide to setting up and using the JAEGIS NexusSync MCP (Model Context Protocol) server with Claude Desktop and other AI assistants.

## 📋 Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Available Tools](#available-tools)
3. [Setup for Claude Desktop](#setup-for-claude-desktop)
4. [Setup for Other AI Assistants](#setup-for-other-ai-assistants)
5. [Testing the Server](#testing-the-server)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## 🤔 What is MCP?

The Model Context Protocol (MCP) is a standard for connecting AI assistants to external tools and data sources. The JAEGIS NexusSync MCP server exposes **17+ tools** that allow AI assistants like Claude to:

- Query your knowledge base with Adaptive RAG
- Process and ingest documents
- Manage Google Drive integration
- Control background services
- Monitor system status

---

## 🛠️ Available Tools

### RAG & Chat Tools (2)
1. **rag_query** - Query the RAG engine with Adaptive RAG
2. **vector_search** - Search the vector store for documents

### Document Processing Tools (4)
3. **process_file** - Process a single file
4. **process_folder** - Process all files in a folder
5. **get_processing_queue** - Get queue status
6. **process_queue_items** - Process pending queue items

### Google Drive Tools (3)
7. **gdrive_sync** - Sync Google Drive folder
8. **gdrive_list_files** - List files in Google Drive
9. **gdrive_download_file** - Download a file from Google Drive

### Vector Store Tools (2)
10. **vector_store_info** - Get vector store statistics
11. **vector_store_delete** - Delete documents from vector store

### Background Service Tools (3)
12. **background_service_start** - Start automated processing
13. **background_service_stop** - Stop background service
14. **background_service_status** - Get service status

### System Tools (3)
15. **system_info** - Get system information
16. **verify_connections** - Test all service connections
17. **get_config** - Get current configuration

---

## 🖥️ Setup for Claude Desktop

### Step 1: Install Dependencies

```bash
# Install FastAPI and Uvicorn
pip install fastapi uvicorn pydantic
```

### Step 2: Locate Claude Desktop Config

The Claude Desktop configuration file is located at:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 3: Add JAEGIS NexusSync Server

Open the config file and add the JAEGIS NexusSync server:

```json
{
  "mcpServers": {
    "jaegis-nexussync": {
      "command": "python",
      "args": [
        "-m",
        "uvicorn",
        "youtube_chat_cli_main.mcp.server:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\YOUR_USERNAME\\path\\to\\youtube-chat-cli-main"
      }
    }
  }
}
```

**Important:** Replace `C:\\Users\\YOUR_USERNAME\\path\\to\\youtube-chat-cli-main` with your actual project path.

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop. The MCP server will start automatically.

### Step 5: Verify Connection

In Claude Desktop, you should see the JAEGIS NexusSync tools available. Try asking:

```
"Can you list the available JAEGIS NexusSync tools?"
```

---

## 🌐 Setup for Other AI Assistants

### Manual Server Start

You can run the MCP server manually and connect it to any AI assistant that supports HTTP APIs:

```bash
# Start the server
python -m uvicorn youtube_chat_cli_main.mcp.server:app --host 127.0.0.1 --port 8000

# Server will be available at http://127.0.0.1:8000
```

### API Endpoints

- **GET /** - Server info
- **GET /tools/list** - List all available tools
- **POST /tools/call** - Execute a tool
- **GET /health** - Health check

### Example API Call

```bash
# List tools
curl http://127.0.0.1:8000/tools/list

# Call a tool
curl -X POST http://127.0.0.1:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rag_query",
    "arguments": {
      "question": "What is the main topic of the documents?"
    }
  }'
```

---

## 🧪 Testing the Server

### Test 1: Start the Server

```bash
python -m uvicorn youtube_chat_cli_main.mcp.server:app --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Test 2: Check Health

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test 3: List Tools

```bash
curl http://127.0.0.1:8000/tools/list
```

You should see a list of 17+ tools.

### Test 4: Call a Tool

```bash
curl -X POST http://127.0.0.1:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "system_info",
    "arguments": {}
  }'
```

---

## 💡 Usage Examples

### Example 1: Query the Knowledge Base

**In Claude Desktop:**
```
"Use the rag_query tool to ask: What are the key findings in the research papers?"
```

**Via API:**
```bash
curl -X POST http://127.0.0.1:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rag_query",
    "arguments": {
      "question": "What are the key findings in the research papers?"
    }
  }'
```

### Example 2: Process a Document

**In Claude Desktop:**
```
"Use the process_file tool to process the file at C:\Documents\report.pdf"
```

**Via API:**
```bash
curl -X POST http://127.0.0.1:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "process_file",
    "arguments": {
      "file_path": "C:\\Documents\\report.pdf",
      "priority": 1
    }
  }'
```

### Example 3: Sync Google Drive

**In Claude Desktop:**
```
"Use the gdrive_sync tool to check for new files in Google Drive"
```

**Via API:**
```bash
curl -X POST http://127.0.0.1:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gdrive_sync",
    "arguments": {}
  }'
```

### Example 4: Get System Status

**In Claude Desktop:**
```
"Use the system_info tool to show me the current system status"
```

**Via API:**
```bash
curl -X POST http://127.0.0.1:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "system_info",
    "arguments": {}
  }'
```

---

## 🔧 Troubleshooting

### Issue: Server Won't Start

**Solution:**
1. Check that all dependencies are installed:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

2. Verify Python path in config is correct

3. Check for port conflicts:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

### Issue: Tools Not Showing in Claude Desktop

**Solution:**
1. Verify the config file path is correct
2. Restart Claude Desktop completely
3. Check the Claude Desktop logs for errors

### Issue: Tool Execution Fails

**Solution:**
1. Verify all services are running:
   ```bash
   python -m youtube_chat_cli_main.cli.main rag verify-connections
   ```

2. Check the server logs for error messages

3. Ensure .env file is properly configured

### Issue: Import Errors

**Solution:**
1. Verify PYTHONPATH is set correctly in the config
2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

---

## 📚 Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Claude Desktop Documentation](https://claude.ai/desktop)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JAEGIS NexusSync CLI Usage Guide](../CLI_USAGE_GUIDE.md)

---

## 🎉 Success!

Once configured, you can use Claude Desktop (or any MCP-compatible AI assistant) to:
- Query your knowledge base
- Process documents
- Manage your RAG pipeline
- Monitor system status

All through natural language commands! 🚀

