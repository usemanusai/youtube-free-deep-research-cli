# System Architecture Overview

Comprehensive overview of the YouTube Free Deep Research CLI system architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  CLI Tools   │  │  REST API    │  │  WebSocket   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routes    │  │   Models     │  │  Middleware  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  LLM Svc     │  │  TTS Svc     │  │  RAG Svc     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Content Svc  │  │ Search Svc   │  │ Storage Svc  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │Integration   │  │ Background   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SQLite DB   │  │ Vector Store │  │  File Store  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ OpenRouter   │  │ Google Drive │  │  N8N         │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Client Layer

**CLI Tools**
- Command-line interface for direct interaction
- Python 3.13+ compatible
- Rich terminal UI with formatting

**REST API**
- FastAPI-based HTTP endpoints
- OpenAPI/Swagger documentation
- Request/response validation

**WebSocket**
- Real-time bidirectional communication
- Streaming responses
- Event-based updates

### API Layer (FastAPI)

**Routes**
- Health endpoints (`/health/live`, `/health/ready`)
- Chat endpoints
- File upload/download
- Search endpoints
- Configuration endpoints

**Models**
- Pydantic request/response models
- Data validation
- Type hints

**Middleware**
- CORS handling
- Error handling
- Request logging
- Authentication

### Service Layer (33 Modules)

**LLM Services**
- OpenRouter integration with 31-key rotation
- Ollama support
- OpenAI compatibility
- Intelligent failover

**TTS Services**
- MeloTTS (high quality)
- Chatterbox (alternative)
- Edge TTS (cloud-based)
- gTTS (Google)
- pyttsx3 (offline)

**RAG Services**
- LangGraph-based engine
- Document retrieval
- Context grading
- Response generation

**Content Services**
- YouTube processing
- PDF extraction
- Web scraping
- Document parsing

**Search Services**
- Web search aggregation
- Brave search integration
- Vector similarity search
- Keyword extraction

**Storage Services**
- Vector store (Qdrant/Chroma)
- Session management
- File processing
- Caching

**Integration Services**
- Google Drive API
- N8N workflows
- Embedding generation
- External API calls

**Background Services**
- APScheduler-based jobs
- Async task processing
- Queue management
- Health monitoring

### Data Layer

**SQLite Database**
- Persistent storage
- Indexed queries
- Transaction support

**Vector Store**
- Qdrant or Chroma
- Semantic search
- Embedding storage

**File Store**
- Local file system
- Temporary storage
- Cache management

### External Services

**OpenRouter**
- 31-key rotation
- Multiple LLM models
- Intelligent failover

**Google Drive**
- OAuth authentication
- File access
- Document processing

**N8N**
- Workflow automation
- Webhook integration
- Data transformation

## Data Flow

```
User Input
    ↓
CLI/API Layer
    ↓
Service Layer (Processing)
    ├─ LLM Service (Generate)
    ├─ RAG Service (Retrieve)
    ├─ TTS Service (Synthesize)
    └─ Search Service (Find)
    ↓
Data Layer (Store/Retrieve)
    ├─ Database
    ├─ Vector Store
    └─ File Store
    ↓
External Services (Integrate)
    ├─ OpenRouter
    ├─ Google Drive
    └─ N8N
    ↓
Response to User
```

## Key Design Principles

1. **Modularity** - 60+ files organized into logical services
2. **Separation of Concerns** - Clear boundaries between layers
3. **Scalability** - Async/await for concurrent operations
4. **Reliability** - Error handling and retry logic
5. **Maintainability** - Type hints and comprehensive documentation
6. **Backward Compatibility** - 100% compatible with existing code

## Technology Stack

- **Language**: Python 3.13+
- **Web Framework**: FastAPI
- **LLM**: OpenRouter, Ollama, OpenAI
- **RAG**: LangGraph, LangChain
- **Vector Store**: Qdrant, Chroma
- **TTS**: MeloTTS, Chatterbox, Edge TTS
- **Database**: SQLite, PostgreSQL
- **Task Queue**: APScheduler
- **Testing**: pytest, pytest-asyncio

## Performance Characteristics

- **Latency**: <100ms for API responses
- **Throughput**: 100+ concurrent requests
- **Memory**: ~500MB baseline
- **Storage**: Configurable (SQLite or PostgreSQL)

## Security Considerations

- API key rotation (31 keys)
- OAuth for Google Drive
- CORS protection
- Input validation
- Error message sanitization

---

See [Modular Structure](modular-structure.md) for detailed file organization.

