# File Upload Feature Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                    (Next.js Dashboard - Port 3000)                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌───────────────────────┐   ┌──────────────────────┐
        │   Chat Interface      │   │  File Upload Dialog  │
        │   Component           │   │  Component           │
        │                       │   │                      │
        │  - Message Display    │   │  ┌────────────────┐ │
        │  - Input Field        │   │  │  Local Files   │ │
        │  - Paperclip Button ──┼───┼─▶│  Tab           │ │
        │  - Send Button        │   │  │  - File Picker │ │
        │                       │   │  │  - Upload      │ │
        └───────────────────────┘   │  └────────────────┘ │
                                    │  ┌────────────────┐ │
                                    │  │  Google Drive  │ │
                                    │  │  Tab           │ │
                                    │  │  - File List   │ │
                                    │  │  - Download    │ │
                                    │  └────────────────┘ │
                                    └──────────────────────┘
                                              │
                                              │ HTTP Requests
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │                                                   │
                    ▼                                                   ▼
        ┌───────────────────────┐                         ┌──────────────────────┐
        │  POST /api/v1/files/  │                         │  GET /api/v1/gdrive/ │
        │  upload               │                         │  list                │
        │                       │                         │                      │
        │  - Receives file      │                         │  - Lists GDrive files│
        │  - Saves to temp      │                         │  - Returns metadata  │
        │  - Adds to queue      │                         │                      │
        └───────────────────────┘                         └──────────────────────┘
                    │                                                   │
                    │                                                   │
                    │                         ┌──────────────────────┐  │
                    │                         │  POST /api/v1/gdrive/│  │
                    │                         │  download            │  │
                    │                         │                      │  │
                    │                         │  - Downloads file    │◀─┘
                    │                         │  - Saves to temp     │
                    │                         │  - Adds to queue     │
                    │                         └──────────────────────┘
                    │                                     │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │     PROCESSING QUEUE                │
                    │     (SQLite Database)               │
                    │                                     │
                    │  - Queue ID                         │
                    │  - File Path                        │
                    │  - File Name                        │
                    │  - Source (local/gdrive)            │
                    │  - Status (pending/processing/done) │
                    │  - Priority                         │
                    └─────────────────────────────────────┘
                                      │
                                      │ Background Processing
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │     FILE PROCESSOR                  │
                    │                                     │
                    │  1. Read file content               │
                    │  2. Extract text                    │
                    │  3. Split into chunks               │
                    │  4. Generate embeddings             │
                    │  5. Store in vector DB              │
                    └─────────────────────────────────────┘
                                      │
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │     CHROMADB VECTOR STORE           │
                    │                                     │
                    │  - Document chunks                  │
                    │  - Embeddings                       │
                    │  - Metadata                         │
                    │  - Searchable index                 │
                    └─────────────────────────────────────┘
                                      │
                                      │ Semantic Search
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │     RAG QUERY ENGINE                │
                    │                                     │
                    │  1. Receive user question           │
                    │  2. Search vector DB                │
                    │  3. Retrieve relevant chunks        │
                    │  4. Generate answer with LLM        │
                    │  5. Return to chat interface        │
                    └─────────────────────────────────────┘
                                      │
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │     CHAT INTERFACE                  │
                    │     (Display Answer)                │
                    └─────────────────────────────────────┘
```

## Data Flow

### Local File Upload Flow

```
User Action → Select File → Click Upload
                    ↓
            FormData Created
                    ↓
    POST /api/v1/files/upload
                    ↓
        File Saved to Temp Dir
                    ↓
        Added to Processing Queue
                    ↓
        Queue ID Returned
                    ↓
    Success Message in Chat
                    ↓
    Background: File Processed
                    ↓
    Background: Indexed in ChromaDB
                    ↓
        Ready for Queries
```

### Google Drive File Flow

```
User Action → Click GDrive Tab → Load Files
                    ↓
    GET /api/v1/gdrive/list
                    ↓
        Files Displayed
                    ↓
    User Selects File
                    ↓
    POST /api/v1/gdrive/download
                    ↓
    File Downloaded from GDrive
                    ↓
        Saved to Temp Dir
                    ↓
        Added to Processing Queue
                    ↓
        Queue ID Returned
                    ↓
    Success Message in Chat
                    ↓
    Background: File Processed
                    ↓
    Background: Indexed in ChromaDB
                    ↓
        Ready for Queries
```

## Component Interaction

### Frontend Components

```
ChatInterface
    │
    ├─ State Management
    │   ├─ messages: Message[]
    │   ├─ input: string
    │   ├─ uploadDialogOpen: boolean
    │   └─ uploadedFiles: any[]
    │
    ├─ Event Handlers
    │   ├─ handleSubmit() - Send chat message
    │   ├─ handleFileUploaded() - Process uploaded file
    │   └─ handleNewSession() - Reset session
    │
    └─ Child Components
        ├─ Input Field
        ├─ Paperclip Button → Opens FileUploadDialog
        ├─ Send Button
        └─ FileUploadDialog
            │
            ├─ Local Files Tab
            │   ├─ File Input
            │   ├─ Progress Bar
            │   └─ Upload Button
            │
            └─ Google Drive Tab
                ├─ File List (ScrollArea)
                ├─ Progress Bar
                └─ Refresh Button
```

### Backend API Endpoints

```
FastAPI Server (Port 8555)
    │
    ├─ /api/v1/files/upload
    │   ├─ Accepts: multipart/form-data
    │   ├─ Returns: { success, file_id, queue_id, ... }
    │   └─ Side Effects: Saves file, adds to queue
    │
    ├─ /api/v1/gdrive/list
    │   ├─ Accepts: folder_id?, page_size?
    │   ├─ Returns: { success, files[], count }
    │   └─ Side Effects: Queries Google Drive API
    │
    ├─ /api/v1/gdrive/download
    │   ├─ Accepts: { file_id }
    │   ├─ Returns: { success, file_name, queue_id, ... }
    │   └─ Side Effects: Downloads file, adds to queue
    │
    └─ /api/v1/chat/query
        ├─ Accepts: { question, session_id? }
        ├─ Returns: { answer, documents[], ... }
        └─ Side Effects: Searches ChromaDB, calls LLM
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: shadcn/ui (Radix UI + Tailwind CSS)
- **State Management**: React Hooks (useState, useRef)
- **HTTP Client**: Fetch API
- **Notifications**: Sonner (toast)

### Backend
- **Framework**: FastAPI (Python)
- **File Handling**: Python standard library (tempfile, pathlib)
- **Google Drive**: Google Drive API v3
- **Database**: SQLite (queue management)
- **Vector Store**: ChromaDB
- **LLM**: OpenAI API / Local LLM

### Infrastructure
- **API Server**: Uvicorn (ASGI)
- **Dashboard**: Next.js Dev Server
- **Authentication**: Google OAuth 2.0
- **File Storage**: Temporary directories

## Security Considerations

1. **File Validation**
   - File type checking (whitelist)
   - File size limits
   - Malware scanning (recommended)

2. **Authentication**
   - Google OAuth for Drive access
   - Session management for chat
   - API key protection

3. **Data Privacy**
   - Temporary file cleanup
   - Secure token storage
   - HTTPS in production

4. **Rate Limiting**
   - Upload frequency limits
   - API request throttling
   - Queue size limits

## Performance Optimizations

1. **File Processing**
   - Asynchronous queue processing
   - Batch embedding generation
   - Chunking strategy optimization

2. **Frontend**
   - Progress indicators for UX
   - Lazy loading of file lists
   - Debounced search

3. **Backend**
   - Connection pooling
   - Caching of embeddings
   - Efficient vector search

## Monitoring & Logging

1. **API Server Logs**
   - File upload events
   - Processing queue status
   - Error tracking

2. **Frontend Logs**
   - User interactions
   - API call failures
   - Performance metrics

3. **Metrics**
   - Upload success rate
   - Processing time
   - Query response time

