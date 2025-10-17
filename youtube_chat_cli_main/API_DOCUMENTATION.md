# 📚 JAEGIS NexusSync - API Documentation

Complete API reference for all services, classes, and functions.

## 📋 Table of Contents

1. [Core Services](#core-services)
2. [RAG Engine](#rag-engine)
3. [LLM Service](#llm-service)
4. [Vector Store](#vector-store)
5. [Web Search](#web-search)
6. [Content Processor](#content-processor)
7. [Google Drive Service](#google-drive-service)
8. [Background Service](#background-service)
9. [Database](#database)
10. [MCP Server](#mcp-server)

---

## 🎯 Core Services

### Configuration (`core/config.py`)

```python
from youtube_chat_cli_main.core.config import get_config

# Get configuration instance
config = get_config()

# Access configuration values
llm_model = config.llm_model
embedding_provider = config.embedding_provider
vector_store_type = config.vector_store_type
```

**Key Properties:**
- `llm_provider`: LLM provider ("ollama" or "openrouter")
- `llm_model`: LLM model name
- `embedding_provider`: Embedding provider ("ollama" or "openai")
- `embedding_model`: Embedding model name
- `vector_store_type`: Vector store type ("qdrant" or "chroma")
- `rag_top_k`: Number of documents to retrieve
- `rag_min_relevance_score`: Minimum relevance score
- `rag_max_transform_attempts`: Max query transformation attempts

---

## 🧠 RAG Engine

### AdaptiveRAGEngine (`services/rag_engine.py`)

Adaptive RAG engine with LangGraph state machine.

```python
from youtube_chat_cli_main.services.rag_engine import get_rag_engine

# Get RAG engine instance
rag = get_rag_engine()

# Query the RAG system
result = rag.query("What is machine learning?")

# Access result
print(result["answer"])
print(result["documents"])
print(result["web_search_used"])
```

**Methods:**

#### `query(question: str, session_id: Optional[str] = None) -> Dict[str, Any]`

Query the RAG system with a question.

**Parameters:**
- `question` (str): The question to answer
- `session_id` (Optional[str]): Session ID for chat history

**Returns:**
- `Dict[str, Any]`: Result dictionary with:
  - `answer` (str): Generated answer
  - `documents` (List[Dict]): Retrieved documents
  - `web_search_used` (bool): Whether web search was used
  - `transform_count` (int): Number of query transformations
  - `session_id` (str): Session ID

**Example:**
```python
result = rag.query("Explain neural networks")

print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['documents'])} documents")
print(f"Web search used: {result['web_search_used']}")
```

---

## 💬 LLM Service

### LLMService (`services/llm_service.py`)

Unified interface for LLM providers (Ollama, OpenRouter).

```python
from youtube_chat_cli_main.services.llm_service import get_llm_service

# Get LLM service instance
llm = get_llm_service()

# Generate text
response = llm.generate("Explain quantum computing")

# Generate structured output
grading = llm.generate_structured(
    prompt="Is this document relevant? Answer yes or no.",
    response_format={"type": "json_object"}
)

# Stream response
for chunk in llm.stream("Tell me a story"):
    print(chunk, end="", flush=True)

# Chat with history
response = llm.chat(
    messages=[
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi! How can I help?"},
        {"role": "user", "content": "What's the weather?"}
    ]
)
```

**Methods:**

#### `generate(prompt: str, **kwargs) -> str`

Generate text from a prompt.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Additional parameters (temperature, max_tokens, etc.)

**Returns:**
- `str`: Generated text

#### `generate_structured(prompt: str, response_format: Dict, **kwargs) -> Dict`

Generate structured JSON output.

**Parameters:**
- `prompt` (str): Input prompt
- `response_format` (Dict): Expected JSON format
- `**kwargs`: Additional parameters

**Returns:**
- `Dict`: Parsed JSON response

#### `stream(prompt: str, **kwargs) -> Iterator[str]`

Stream generated text.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Additional parameters

**Yields:**
- `str`: Text chunks

#### `chat(messages: List[Dict], **kwargs) -> str`

Chat with message history.

**Parameters:**
- `messages` (List[Dict]): Chat messages
- `**kwargs`: Additional parameters

**Returns:**
- `str`: Assistant response

---

## 🗄️ Vector Store

### VectorStore (`services/vector_store.py`)

Unified interface for vector stores (Qdrant, ChromaDB).

```python
from youtube_chat_cli_main.services.vector_store import get_vector_store

# Get vector store instance
vs = get_vector_store()

# Add documents
documents = [
    {"content": "Machine learning is...", "metadata": {"source": "ml.pdf"}},
    {"content": "Deep learning is...", "metadata": {"source": "dl.pdf"}}
]
doc_ids = vs.add_documents(documents)

# Search
results = vs.search("What is machine learning?", top_k=5)

# Delete documents
count = vs.delete_documents({"source": "ml.pdf"})

# Get collection info
info = vs.get_collection_info()
```

**Methods:**

#### `add_documents(documents: List[Dict], embeddings: Optional[List[List[float]]] = None) -> List[str]`

Add documents to the vector store.

**Parameters:**
- `documents` (List[Dict]): Documents with content and metadata
- `embeddings` (Optional[List[List[float]]]): Pre-computed embeddings (auto-generated if None)

**Returns:**
- `List[str]`: Document IDs

#### `search(query: Union[str, List[float]], top_k: int = 5) -> List[Dict]`

Search for similar documents.

**Parameters:**
- `query` (Union[str, List[float]]): Query text or embedding
- `top_k` (int): Number of results

**Returns:**
- `List[Dict]`: Search results with content, metadata, and score

#### `delete_documents(filter_criteria: Dict) -> int`

Delete documents matching criteria.

**Parameters:**
- `filter_criteria` (Dict): Filter criteria

**Returns:**
- `int`: Number of deleted documents

#### `get_collection_info() -> Dict`

Get collection information.

**Returns:**
- `Dict`: Collection info (name, vectors_count, etc.)

---

## 🔍 Web Search

### WebSearchService (`services/web_search_service.py`)

Web search with automatic fallback (Tavily → DuckDuckGo).

```python
from youtube_chat_cli_main.services.web_search_service import get_web_search_service

# Get web search service
ws = get_web_search_service()

# Search
results = ws.search("latest AI news", max_results=5)

# Format for LLM context
formatted = ws.format_results_for_context(results, max_length=2000)
```

**Methods:**

#### `search(query: str, max_results: int = 5) -> List[Dict]`

Search the web.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum results

**Returns:**
- `List[Dict]`: Search results with title, url, content, score

#### `format_results_for_context(results: List[Dict], max_length: int = 2000) -> str`

Format results for LLM context.

**Parameters:**
- `results` (List[Dict]): Search results
- `max_length` (int): Maximum length

**Returns:**
- `str`: Formatted results

---

## 📄 Content Processor

### ContentProcessor (`services/content_processor.py`)

Multi-format document processing with markdown-aware chunking.

```python
from youtube_chat_cli_main.services.content_processor import get_content_processor

# Get content processor
processor = get_content_processor()

# Process queue item
success = processor.process_queue_item(queue_id=1)

# Process file directly
content = processor._process_file("document.pdf")

# Split by markdown headings
chunks = processor._split_by_markdown_headings(content)
```

**Supported Formats:**
- PDF (`.pdf`)
- Word (`.docx`)
- Text (`.txt`)
- Markdown (`.md`)
- HTML (`.html`)
- Images (`.png`, `.jpg`, `.jpeg`) - with OCR

**Methods:**

#### `process_queue_item(queue_id: int) -> bool`

Process a document from the queue.

**Parameters:**
- `queue_id` (int): Queue item ID

**Returns:**
- `bool`: Success status

---

## 📁 Google Drive Service

### GoogleDriveService (`services/gdrive_service.py`)

Google Drive integration with OAuth 2.0.

```python
from youtube_chat_cli_main.services.gdrive_service import get_gdrive_service

# Get Google Drive service
gdrive = get_gdrive_service()

# Authenticate
gdrive.authenticate()

# List files in folder
files = gdrive.list_files_in_folder(folder_id="...")

# Download file
local_path = gdrive.download_file(file_id="...", destination="./downloads")

# Watch folder for changes
watcher = GoogleDriveWatcher()
watcher.start()
```

**Methods:**

#### `authenticate() -> bool`

Authenticate with Google Drive.

**Returns:**
- `bool`: Success status

#### `list_files_in_folder(folder_id: str) -> List[Dict]`

List files in a folder.

**Parameters:**
- `folder_id` (str): Folder ID

**Returns:**
- `List[Dict]`: File metadata

#### `download_file(file_id: str, destination: str) -> str`

Download a file.

**Parameters:**
- `file_id` (str): File ID
- `destination` (str): Destination path

**Returns:**
- `str`: Local file path

---

## ⚙️ Background Service

### BackgroundService (`services/background_service.py`)

Automated background processing with APScheduler.

```python
from youtube_chat_cli_main.services.background_service import get_background_service

# Get background service
bg = get_background_service()

# Start service
bg.start()

# Get status
status = bg.get_status()

# Stop service
bg.stop()
```

**Methods:**

#### `start()`

Start background service.

#### `stop()`

Stop background service.

#### `get_status() -> Dict`

Get service status.

**Returns:**
- `Dict`: Status information

---

## 💾 Database

### Database (`core/database.py`)

SQLite database with 6 tables.

```python
from youtube_chat_cli_main.core.database import get_database

# Get database instance
db = get_database()

# Queue operations
queue_id = db.add_to_queue("file.pdf", "file.pdf", "local", priority=0)
item = db.get_queue_item(queue_id)
db.update_queue_status(queue_id, "completed")

# Get statistics
stats = db.get_queue_statistics()
```

**Methods:**

#### `add_to_queue(file_id: str, file_name: str, source: str, priority: int = 0) -> int`

Add item to processing queue.

**Returns:**
- `int`: Queue item ID

#### `get_queue_item(queue_id: int) -> Optional[Dict]`

Get queue item by ID.

**Returns:**
- `Optional[Dict]`: Queue item or None

#### `update_queue_status(queue_id: int, status: str)`

Update queue item status.

#### `get_queue_statistics() -> Dict`

Get queue statistics.

**Returns:**
- `Dict`: Statistics (total, by_status, etc.)

---

## 🔌 MCP Server

### MCP Server (`mcp/server.py`)

FastAPI-based MCP server with 17+ tools.

```python
# Start server
uvicorn youtube_chat_cli_main.mcp.server:app --host 0.0.0.0 --port 8000
```

**Endpoints:**

#### `GET /tools/list`

List all available tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "rag_query",
      "description": "Query the RAG system",
      "inputSchema": {...}
    }
  ]
}
```

#### `POST /tools/call`

Execute a tool.

**Request:**
```json
{
  "name": "rag_query",
  "arguments": {
    "question": "What is machine learning?"
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "..."
    }
  ],
  "isError": false
}
```

---

## 🎉 Complete!

You now have complete API documentation for JAEGIS NexusSync!

For more information, see:
- [CLI Usage Guide](CLI_USAGE_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [MCP Setup Guide](mcp/MCP_SETUP_GUIDE.md)

