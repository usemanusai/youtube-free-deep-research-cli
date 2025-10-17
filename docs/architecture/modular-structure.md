# Modular Structure Guide

Complete guide to the 60+ modular files in YouTube Free Deep Research CLI.

## Directory Structure

```
youtube_chat_cli_main/
├── services/              # 33 service modules
│   ├── __init__.py
│   ├── llm/              # LLM implementations
│   │   ├── __init__.py
│   │   ├── base.py       # Base LLM class
│   │   ├── openrouter.py # OpenRouter implementation
│   │   ├── ollama.py     # Ollama implementation
│   │   └── openai.py     # OpenAI implementation
│   ├── tts/              # TTS orchestrator & engines
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── bridge_client.py
│   │   ├── config.py
│   │   └── engines/
│   │       ├── melotts.py
│   │       ├── chatterbox.py
│   │       ├── edge_tts.py
│   │       ├── gtts.py
│   │       └── pyttsx3.py
│   ├── rag/              # RAG engine
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── retriever.py
│   │   ├── grader.py
│   │   └── transformer.py
│   ├── content/          # Content processing
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   ├── validators.py
│   │   └── extractors/
│   │       ├── youtube.py
│   │       ├── pdf.py
│   │       ├── web.py
│   │       ├── document.py
│   │       └── gdrive.py
│   ├── search/           # Search services
│   │   ├── __init__.py
│   │   ├── aggregator.py
│   │   ├── brave_search.py
│   │   ├── web_search.py
│   │   └── vector_store.py
│   ├── storage/          # Storage services
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   ├── session_manager.py
│   │   └── file_processor.py
│   ├── integration/      # Integration services
│   │   ├── __init__.py
│   │   ├── gdrive.py
│   │   ├── n8n.py
│   │   └── embedding.py
│   └── background/       # Background services
│       ├── __init__.py
│       ├── service.py
│       └── tasks.py
├── api/                  # 13 API modules
│   ├── __init__.py
│   ├── server.py         # FastAPI factory
│   ├── health.py         # Health endpoints
│   ├── nexus_agents.py   # Agent endpoints
│   ├── routes/           # API routes
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── files.py
│   │   ├── search.py
│   │   ├── config.py
│   │   └── background.py
│   ├── models/           # Request/response models
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── files.py
│   │   ├── search.py
│   │   └── common.py
│   └── middleware/       # Middleware
│       ├── __init__.py
│       ├── cors.py
│       ├── error_handler.py
│       └── logging.py
├── cli/                  # 6 CLI modules
│   ├── __init__.py
│   ├── main.py           # CLI entry point
│   ├── commands/         # Command modules
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── files.py
│   │   ├── search.py
│   │   ├── config.py
│   │   └── background.py
│   └── rag_commands.py   # RAG-specific commands
├── utils/                # 4 utility modules
│   ├── __init__.py
│   ├── validators.py     # Input validation
│   ├── formatters.py     # Output formatting
│   └── helpers.py        # Common utilities
├── tests/                # 4 test packages
│   ├── __init__.py
│   ├── unit/             # Unit tests
│   │   ├── test_llm.py
│   │   ├── test_tts.py
│   │   ├── test_rag.py
│   │   └── test_services.py
│   ├── integration/      # Integration tests
│   │   ├── test_api.py
│   │   ├── test_workflows.py
│   │   └── test_end_to_end.py
│   ├── fixtures/         # Test fixtures
│   │   ├── conftest.py
│   │   ├── mock_data.py
│   │   └── factories.py
│   └── __main__.py       # Test runner
├── core/                 # Core utilities
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── http_client.py    # HTTP utilities
│   └── logging.py        # Logging setup
├── __init__.py
├── __main__.py           # Package entry point
└── api_server.py         # API server entry point
```

## Service Modules (33 Total)

### LLM Services (4 modules)
- `base.py` - Abstract base class
- `openrouter.py` - OpenRouter with 31-key rotation
- `ollama.py` - Local Ollama support
- `openai.py` - OpenAI API support

### TTS Services (8 modules)
- `orchestrator.py` - TTS orchestration
- `bridge_client.py` - Python 3.11 bridge
- `config.py` - TTS configuration
- `melotts.py` - MeloTTS engine
- `chatterbox.py` - Chatterbox engine
- `edge_tts.py` - Edge TTS engine
- `gtts.py` - Google TTS engine
- `pyttsx3.py` - pyttsx3 engine

### RAG Services (4 modules)
- `engine.py` - Main RAG engine
- `retriever.py` - Document retrieval
- `grader.py` - Response grading
- `transformer.py` - Context transformation

### Content Services (6 modules)
- `processor.py` - Content processing
- `validators.py` - Input validation
- `youtube.py` - YouTube extraction
- `pdf.py` - PDF extraction
- `web.py` - Web scraping
- `document.py` - Document processing
- `gdrive.py` - Google Drive processing

### Search Services (4 modules)
- `aggregator.py` - Search aggregation
- `brave_search.py` - Brave search
- `web_search.py` - Web search
- `vector_store.py` - Vector search

### Storage Services (3 modules)
- `vector_store.py` - Vector storage
- `session_manager.py` - Session management
- `file_processor.py` - File handling

### Integration Services (3 modules)
- `gdrive.py` - Google Drive integration
- `n8n.py` - N8N workflow integration
- `embedding.py` - Embedding generation

### Background Services (2 modules)
- `service.py` - Background service
- `tasks.py` - Task definitions

## API Modules (13 Total)

### Routes (6 modules)
- `chat.py` - Chat endpoints
- `files.py` - File endpoints
- `search.py` - Search endpoints
- `config.py` - Configuration endpoints
- `background.py` - Background job endpoints
- `health.py` - Health check endpoints

### Models (4 modules)
- `chat.py` - Chat models
- `files.py` - File models
- `search.py` - Search models
- `common.py` - Common models

### Middleware (3 modules)
- `cors.py` - CORS handling
- `error_handler.py` - Error handling
- `logging.py` - Request logging

## CLI Modules (6 Total)

- `main.py` - CLI entry point
- `chat.py` - Chat commands
- `files.py` - File commands
- `search.py` - Search commands
- `config.py` - Configuration commands
- `background.py` - Background commands
- `rag_commands.py` - RAG-specific commands

## Utility Modules (4 Total)

- `validators.py` - Input validation
- `formatters.py` - Output formatting
- `helpers.py` - Common utilities
- `config.py` - Configuration management

## Test Packages (4 Total)

- `unit/` - Unit tests
- `integration/` - Integration tests
- `fixtures/` - Test fixtures
- `conftest.py` - Pytest configuration

## Module Dependencies

```
CLI/API
  ↓
Services (LLM, TTS, RAG, Content, Search, Storage, Integration, Background)
  ↓
Core (Config, Database, HTTP Client, Logging)
  ↓
External APIs (OpenRouter, Google Drive, N8N)
```

## Import Patterns

### Service Import
```python
from youtube_chat_cli_main.services.llm import OpenRouterLLM
from youtube_chat_cli_main.services.tts import TTSOrchestrator
from youtube_chat_cli_main.services.rag import RAGEngine
```

### API Import
```python
from youtube_chat_cli_main.api.routes import chat, files, search
from youtube_chat_cli_main.api.models import ChatRequest, ChatResponse
```

### CLI Import
```python
from youtube_chat_cli_main.cli.commands import chat, files, search
```

### Utility Import
```python
from youtube_chat_cli_main.utils import validators, formatters, helpers
```

## Adding New Modules

1. Create module file in appropriate service directory
2. Add `__init__.py` if creating new package
3. Implement class/functions
4. Add type hints
5. Write unit tests
6. Update documentation

---

See [System Overview](overview.md) for architecture details.

