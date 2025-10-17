# JAEGIS NexusSync - Dashboard Integration Guide

This document describes the integration between the CLI and the web-based dashboard interface.

## 📋 Overview

The dashboard integration adds a modern web interface to JAEGIS NexusSync while maintaining 100% backward compatibility with the existing CLI. The architecture uses a **FastAPI backend layer** that wraps the existing services without modifying them.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                           │
├──────────────────────────┬──────────────────────────────────┤
│   CLI (cli/main.py)      │   Dashboard (Next.js)            │
│   Port: N/A              │   Port: 3000                     │
└──────────────────────────┴──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (api_server.py)                 │
│                      Port: 8000                              │
│  - REST API endpoints                                        │
│  - CORS middleware for Next.js                               │
│  - Request/response validation (Pydantic)                    │
│  - No modifications to services layer                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Services Layer (Unchanged)                 │
│  - rag_engine.py         - Adaptive RAG with LangGraph       │
│  - content_processor.py  - Multi-format file processing      │
│  - vector_store.py       - Qdrant/Chroma integration         │
│  - llm_service.py        - Ollama/OpenRouter providers       │
│  - background_service.py - APScheduler automation            │
│  - gdrive_service.py     - Google Drive monitoring           │
│  - tts_service.py        - MeloTTS/Chatterbox (Python 3.11)  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

### Backend (Python)

```
youtube_chat_cli_main/
├── api_server.py              # NEW: FastAPI backend server
├── api_requirements.txt       # NEW: FastAPI dependencies
├── start_api_server.bat       # NEW: Windows startup script
├── start_api_server.sh        # NEW: Linux/Mac startup script
├── cli/                       # UNCHANGED: Existing CLI
│   ├── main.py
│   └── rag_commands.py
├── services/                  # UNCHANGED: Existing services
│   ├── rag_engine.py
│   ├── content_processor.py
│   ├── vector_store.py
│   ├── llm_service.py
│   ├── background_service.py
│   └── gdrive_service.py
└── core/                      # UNCHANGED: Core utilities
    ├── config.py
    └── database.py
```

### Frontend (TypeScript/Next.js)

```
workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # MODIFIED: Added Providers
│   │   ├── page.tsx           # MODIFIED: Added new tabs
│   │   └── providers.tsx      # NEW: React Query provider
│   ├── components/
│   │   ├── chat-interface.tsx # NEW: RAG chat UI
│   │   ├── file-upload.tsx    # NEW: File upload UI
│   │   ├── queue-manager.tsx  # NEW: Queue monitoring UI
│   │   ├── system-status.tsx  # MODIFIED: Uses real API
│   │   └── terminal.tsx       # MODIFIED: Calls real API
│   ├── hooks/
│   │   └── use-api.ts         # NEW: React Query hooks
│   └── lib/
│       └── api-client.ts      # NEW: TypeScript API client
└── .env.local.example         # NEW: Environment variables
```

## 🚀 Setup Instructions

### 1. Install FastAPI Dependencies

```bash
cd youtube_chat_cli_main
pip install -r api_requirements.txt
```

### 2. Start the FastAPI Backend

**Windows:**
```bash
start_api_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_api_server.sh
./start_api_server.sh
```

**Or manually:**
```bash
cd youtube_chat_cli_main
python api_server.py
```

The API server will start on `http://localhost:8000`

### 3. Install Dashboard Dependencies

```bash
cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm install
```

### 4. Configure Dashboard

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Start the Dashboard

```bash
npm run dev
```

The dashboard will start on `http://localhost:3000`

## 🔌 API Endpoints

### Health & System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/system/status` | System status with service health |
| GET | `/api/v1/system/verify` | Verify all connections |

### Chat & RAG

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/query` | Query RAG engine |
| POST | `/api/v1/chat/session` | Create new chat session |
| GET | `/api/v1/chat/history/{session_id}` | Get chat history |

### File Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/files/upload` | Upload file (multipart/form-data) |
| POST | `/api/v1/files/process` | Process file immediately |
| GET | `/api/v1/files/queue` | Get processing queue |
| POST | `/api/v1/files/queue/process` | Process pending queue items |

### Google Drive

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/gdrive/sync` | Trigger Google Drive sync |
| GET | `/api/v1/gdrive/status` | Get sync status |

### Background Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/background/start` | Start background service |
| POST | `/api/v1/background/stop` | Stop background service |
| GET | `/api/v1/background/status` | Get service status |

### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/config` | Get configuration (sanitized) |
| PUT | `/api/v1/config` | Update configuration (.env file) |
| POST | `/api/v1/config/reload` | Reload configuration |

### Podcast Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/podcast/generate` | Generate podcast |
| GET | `/api/v1/podcast/list` | List generated podcasts |
| GET | `/api/v1/podcast/{name}` | Download podcast file |

### Search & Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/search` | Search vector store |
| GET | `/api/v1/documents` | List documents |

## 🎨 Dashboard Features

### 1. Overview Tab
- System metrics and statistics
- Quick access cards
- Recent activity

### 2. Chat Tab
- Real-time RAG chat interface
- Session management
- Source document display
- Web search indicators
- Query transformation tracking

### 3. Upload Tab
- Drag-and-drop file upload
- Progress tracking
- Multi-file support
- Supported formats: PDF, DOC, DOCX, TXT, MD, JSON, XML, CSV, Images

### 4. Queue Tab
- Processing queue monitoring
- Filter by status (pending, processing, completed, failed)
- Priority management
- Batch processing control

### 5. Terminal Tab
- Execute CLI commands from web interface
- Command suggestions
- Real-time output
- Command history

### 6. Settings Tab
- Configuration management
- Service control
- Environment variable editing

### 7. Commands Tab
- Complete CLI command reference
- Command categories
- Usage examples

### 8. Status Tab
- Real-time service health monitoring
- System metrics
- Connection verification
- Service logs

## 🔒 Backward Compatibility

The integration maintains 100% backward compatibility:

✅ **CLI Unchanged** - All existing CLI commands work exactly as before
✅ **Services Unchanged** - No modifications to the services layer
✅ **TTS Bridge Preserved** - Python 3.11 subprocess pattern maintained
✅ **Configuration Compatible** - Same .env file format
✅ **Database Schema Unchanged** - No database migrations required

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# System status
curl http://localhost:8000/api/v1/system/status

# Chat query
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is JAEGIS NexusSync?"}'
```

### Test Dashboard

1. Open `http://localhost:3000`
2. Navigate to Chat tab
3. Send a test query
4. Upload a test file in Upload tab
5. Check queue in Queue tab
6. Verify system status in Status tab

## 📊 Monitoring

### API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Logs

- **Backend logs**: Console output from `api_server.py`
- **Dashboard logs**: Browser console (F12)
- **Service logs**: Existing logging in services layer

## 🐛 Troubleshooting

### Backend Issues

**Problem**: API server won't start
- Check if port 8000 is available
- Verify FastAPI dependencies are installed
- Check Python version (3.13+)

**Problem**: CORS errors
- Verify CORS middleware is configured for `http://localhost:3000`
- Check browser console for specific CORS error

### Dashboard Issues

**Problem**: Can't connect to backend
- Verify API server is running: `http://localhost:8000/api/v1/health`
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check browser console for connection errors

**Problem**: File uploads fail
- Check file size limits
- Verify `uploads/` directory exists and is writable
- Check backend logs for errors

## 📝 Development Workflow

### Adding a New Feature

1. **Add API endpoint** in `api_server.py`
2. **Add TypeScript types** in `src/lib/api-client.ts`
3. **Add API client method** in `src/lib/api-client.ts`
4. **Add React Query hook** in `src/hooks/use-api.ts`
5. **Create/update component** in `src/components/`
6. **Add to dashboard** in `src/app/page.tsx`

### Example: Adding a New Endpoint

**Backend (`api_server.py`):**
```python
@app.get("/api/v1/example")
async def example_endpoint():
    return {"message": "Hello from API"}
```

**Frontend (`src/lib/api-client.ts`):**
```typescript
async getExample(): Promise<{ message: string }> {
  const response = await this.client.get('/api/v1/example');
  return response.data;
}
```

**Hook (`src/hooks/use-api.ts`):**
```typescript
export function useExample() {
  return useQuery({
    queryKey: ['example'],
    queryFn: () => apiClient.getExample(),
  });
}
```

**Component:**
```typescript
const { data } = useExample();
```

## 🚀 Production Deployment

### Backend

```bash
# Install production dependencies
pip install -r api_requirements.txt

# Run with Gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build for production
npm run build

# Start production server
npm run start
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Documentation](https://tanstack.com/query/latest)
- [shadcn/ui Documentation](https://ui.shadcn.com)

