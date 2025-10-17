"""
JAEGIS NexusSync - FastAPI Backend Server

This server provides REST API and WebSocket endpoints for the dashboard interface.
It wraps the existing services layer without modifying any core functionality.

Architecture:
    Dashboard (Next.js) → FastAPI Backend → Services Layer → External APIs

Author: Augment Agent
Date: October 1, 2025
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import existing services (no modifications needed)
# Use relative imports to match the package structure
from .core.config import get_config
from .core.database import get_database
from .services.rag_engine import get_rag_engine
from .services.content_processor import get_content_processor
from .services.gdrive_service import get_gdrive_watcher
from .services.background_service import get_background_service
from .services.vector_store import get_vector_store
from .services.llm_service import get_llm_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class ChatQueryRequest(BaseModel):
    """Request model for RAG chat query."""
    question: str = Field(..., description="User question")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    stream: bool = Field(False, description="Enable streaming response")

class ChatQueryResponse(BaseModel):
    """Response model for RAG chat query."""
    answer: str
    question: str
    documents: List[Dict[str, Any]] = []
    web_search_used: bool = False
    transform_count: int = 0
    session_id: Optional[str] = None

class FileProcessRequest(BaseModel):
    """Request model for file processing."""
    file_path: str = Field(..., description="Path to file to process")
    priority: int = Field(0, description="Processing priority")

class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates."""
    config: Dict[str, str] = Field(..., description="Configuration key-value pairs")

class BackgroundServiceRequest(BaseModel):
    """Request model for background service control."""
    action: str = Field(..., description="Action: start, stop, status")

class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    services: Dict[str, Dict[str, Any]]
    uptime: Optional[str] = None
    version: str = "2.0.0"

# ============================================================================
# Application Lifecycle Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    logger.info("🚀 Starting JAEGIS NexusSync API Server...")
    
    # Initialize services on startup
    try:
        config = get_config()
        logger.info("✅ Configuration loaded")
        
        db = get_database()
        logger.info("✅ Database initialized")
        
        # Store in app state for access in routes
        app.state.config = config
        app.state.db = db
        
        logger.info("🎉 API Server started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down API Server...")
    try:
        # Stop background service if running
        bg_service = get_background_service()
        if bg_service.is_running:
            bg_service.stop()
            logger.info("✅ Background service stopped")
    except Exception as e:
        logger.warning(f"⚠️ Error during shutdown: {e}")
    
    logger.info("👋 API Server shutdown complete")

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="JAEGIS NexusSync API",
    description="REST API and WebSocket server for JAEGIS NexusSync dashboard",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Health & System Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "JAEGIS NexusSync API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/v1/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get comprehensive system status."""
    try:
        config = get_config()
        db = get_database()
        
        services_status = {
            "database": {
                "status": "healthy",
                "type": "SQLite",
                "path": config.database_path
            },
            "vector_store": {
                "status": "unknown",
                "type": config.vector_store_type
            },
            "llm": {
                "status": "unknown",
                "provider": "Ollama" if config.ollama_base_url else "OpenRouter"
            },
            "background_service": {
                "status": "unknown",
                "running": False
            }
        }
        
        # Check vector store
        try:
            vector_store = get_vector_store()
            services_status["vector_store"]["status"] = "healthy"
        except Exception as e:
            services_status["vector_store"]["status"] = "error"
            services_status["vector_store"]["error"] = str(e)
        
        # Check LLM service
        try:
            llm = get_llm_service()
            services_status["llm"]["status"] = "healthy"
        except Exception as e:
            services_status["llm"]["status"] = "error"
            services_status["llm"]["error"] = str(e)
        
        # Check background service
        try:
            bg_service = get_background_service()
            services_status["background_service"]["running"] = bg_service.is_running
            services_status["background_service"]["status"] = "running" if bg_service.is_running else "stopped"
        except Exception as e:
            services_status["background_service"]["status"] = "error"
            services_status["background_service"]["error"] = str(e)
        
        return SystemStatusResponse(
            status="healthy",
            services=services_status,
            version="2.0.0"
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/verify")
async def verify_connections():
    """Verify all service connections."""
    try:
        config = get_config()
        results = {
            "config": {"status": "ok"},
            "database": {"status": "unknown"},
            "vector_store": {"status": "unknown"},
            "llm": {"status": "unknown"},
            "embeddings": {"status": "unknown"},
        }
        
        # Test database
        try:
            db = get_database()
            results["database"]["status"] = "ok"
        except Exception as e:
            results["database"]["status"] = "error"
            results["database"]["error"] = str(e)
        
        # Test vector store
        try:
            vector_store = get_vector_store()
            results["vector_store"]["status"] = "ok"
            results["vector_store"]["type"] = config.vector_store_type
        except Exception as e:
            results["vector_store"]["status"] = "error"
            results["vector_store"]["error"] = str(e)
        
        # Test LLM
        try:
            llm = get_llm_service()
            results["llm"]["status"] = "ok"
        except Exception as e:
            results["llm"]["status"] = "error"
            results["llm"]["error"] = str(e)
        
        # Determine overall status
        all_ok = all(r.get("status") == "ok" for r in results.values())
        
        return {
            "overall_status": "ok" if all_ok else "degraded",
            "services": results
        }
        
    except Exception as e:
        logger.error(f"Error verifying connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Chat & RAG Endpoints
# ============================================================================

@app.post("/api/v1/chat/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    """
    Query the RAG engine with a question.

    This endpoint uses the existing RAG engine to answer questions using
    the vector store and web search fallback.
    """
    try:
        logger.info(f"Chat query: {request.question[:100]}...")

        # Get RAG engine
        rag_engine = get_rag_engine()

        # Query the RAG engine
        result = rag_engine.query(request.question)

        # Add session_id if provided
        result["session_id"] = request.session_id

        logger.info(f"Query completed: {len(result.get('answer', ''))} chars")

        return ChatQueryResponse(**result)

    except Exception as e:
        logger.error(f"Error in chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    try:
        # TODO: Implement session-based chat history
        # For now, return empty history
        return {
            "session_id": session_id,
            "messages": [],
            "created_at": None
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/session")
async def create_chat_session():
    """Create a new chat session."""
    try:
        import uuid
        session_id = str(uuid.uuid4())

        return {
            "session_id": session_id,
            "created_at": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# File Processing Endpoints
# ============================================================================

@app.post("/api/v1/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing.

    The file is saved to a temporary location and added to the processing queue.
    """
    try:
        logger.info(f"Uploading file: {file.filename}")

        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)

        # Save uploaded file
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved: {file_path} ({len(content)} bytes)")

        # Add to processing queue
        db = get_database()
        queue_id = db.add_to_queue(
            file_id=str(file_path),
            file_name=file.filename,
            source='upload',
            priority=0
        )

        return {
            "success": True,
            "file_path": str(file_path),
            "file_name": file.filename,
            "file_size": len(content),
            "queue_id": queue_id
        }

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/files/process")
async def process_file(request: FileProcessRequest):
    """Process a file immediately."""
    try:
        logger.info(f"Processing file: {request.file_path}")

        # Get services
        db = get_database()
        processor = get_content_processor()

        # Add to queue
        queue_id = db.add_to_queue(
            file_id=request.file_path,
            file_name=Path(request.file_path).name,
            source='local',
            priority=request.priority
        )

        # Process immediately
        success = processor.process_queue_item(queue_id)

        return {
            "success": success,
            "queue_id": queue_id,
            "file_path": request.file_path
        }

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/files/queue")
async def get_processing_queue(limit: int = 50, status: Optional[str] = None):
    """Get the processing queue."""
    try:
        db = get_database()

        if status == "pending":
            items = db.get_pending_queue_items(limit=limit)
        else:
            # Get all items (we'll need to add this method to database)
            items = db.get_pending_queue_items(limit=limit)

        return {
            "items": items,
            "count": len(items)
        }

    except Exception as e:
        logger.error(f"Error getting queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/files/queue/process")
async def process_queue(limit: int = 10):
    """Process pending items in the queue."""
    try:
        logger.info(f"Processing queue (limit: {limit})")

        db = get_database()
        processor = get_content_processor()

        # Get pending items
        items = db.get_pending_queue_items(limit=limit)

        results = {
            "processed": 0,
            "failed": 0,
            "total": len(items)
        }

        # Process each item
        for item in items:
            try:
                success = processor.process_queue_item(item['id'])
                if success:
                    results["processed"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(f"Error processing queue item {item['id']}: {e}")
                results["failed"] += 1

        return results

    except Exception as e:
        logger.error(f"Error processing queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Google Drive Endpoints
# ============================================================================

@app.post("/api/v1/gdrive/sync")
async def sync_google_drive():
    """Trigger Google Drive sync."""
    try:
        logger.info("Triggering Google Drive sync...")

        config = get_config()

        if not config.google_drive_folder_id:
            raise HTTPException(
                status_code=400,
                detail="Google Drive folder ID not configured"
            )

        # Get Google Drive watcher
        gdrive_watcher = get_gdrive_watcher()

        # Trigger sync
        new_files_count = gdrive_watcher.watch()

        return {
            "success": True,
            "new_files": new_files_count,
            "message": f"Sync completed: {new_files_count} new files added to queue"
        }

    except Exception as e:
        logger.error(f"Error syncing Google Drive: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/gdrive/status")
async def get_gdrive_status():
    """Get Google Drive sync status."""
    try:
        config = get_config()
        db = get_database()

        if not config.google_drive_folder_id:
            return {
                "configured": False,
                "folder_id": None,
                "total_files": 0
            }

        # Get file count from database
        # TODO: Add method to get Google Drive file count

        return {
            "configured": True,
            "folder_id": config.google_drive_folder_id,
            "total_files": 0,  # Placeholder
            "last_sync": None  # Placeholder
        }

    except Exception as e:
        logger.error(f"Error getting Google Drive status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Background Service Endpoints
# ============================================================================

@app.post("/api/v1/background/start")
async def start_background_service():
    """Start the background service."""
    try:
        logger.info("Starting background service...")

        bg_service = get_background_service()

        if bg_service.is_running:
            return {
                "success": False,
                "message": "Background service is already running"
            }

        bg_service.start()

        return {
            "success": True,
            "message": "Background service started successfully"
        }

    except Exception as e:
        logger.error(f"Error starting background service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/background/stop")
async def stop_background_service():
    """Stop the background service."""
    try:
        logger.info("Stopping background service...")

        bg_service = get_background_service()

        if not bg_service.is_running:
            return {
                "success": False,
                "message": "Background service is not running"
            }

        bg_service.stop()

        return {
            "success": True,
            "message": "Background service stopped successfully"
        }

    except Exception as e:
        logger.error(f"Error stopping background service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/background/status")
async def get_background_status():
    """Get background service status."""
    try:
        bg_service = get_background_service()

        return {
            "running": bg_service.is_running,
            "jobs": []  # TODO: Get scheduled jobs info
        }

    except Exception as e:
        logger.error(f"Error getting background service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.get("/api/v1/config")
async def get_configuration():
    """Get current configuration (sanitized)."""
    try:
        config = get_config()

        # Return sanitized config (hide API keys)
        return {
            "llm": {
                "model": config.llm_model,
                "provider": "Ollama" if config.ollama_base_url else "OpenRouter",
                "ollama_url": config.ollama_base_url,
                "has_api_key": config.has_llm_api_key
            },
            "vector_store": {
                "type": config.vector_store_type,
                "qdrant_url": config.qdrant_url if config.vector_store_type == "qdrant" else None,
                "chroma_path": config.chroma_persist_directory if config.vector_store_type == "chroma" else None
            },
            "google_drive": {
                "configured": bool(config.google_drive_folder_id),
                "folder_id": config.google_drive_folder_id,
                "poll_interval": config.google_drive_poll_interval
            },
            "rag": {
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "max_transform_attempts": config.rag_max_transform_attempts
            },
            "background_service": {
                "interval": config.background_service_interval
            }
        }

    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/config")
async def update_configuration(request: ConfigUpdateRequest):
    """
    Update configuration.

    WARNING: This updates the .env file. Use with caution.
    """
    try:
        logger.info(f"Updating configuration: {list(request.config.keys())}")

        # Path to .env file
        env_file = Path(".env")

        if not env_file.exists():
            raise HTTPException(status_code=404, detail=".env file not found")

        # Read current .env
        with open(env_file, 'r') as f:
            lines = f.readlines()

        # Update values
        updated_lines = []
        updated_keys = set()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                updated_lines.append(line)
                continue

            if '=' in line:
                key = line.split('=')[0].strip()
                if key in request.config:
                    updated_lines.append(f"{key}={request.config[key]}")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add new keys that weren't in the file
        for key, value in request.config.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}")

        # Write updated .env
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))

        # Reload configuration
        get_config(reload=True)

        return {
            "success": True,
            "message": "Configuration updated successfully",
            "updated_keys": list(request.config.keys())
        }

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/reload")
async def reload_configuration():
    """Reload configuration from .env file."""
    try:
        get_config(reload=True)

        return {
            "success": True,
            "message": "Configuration reloaded successfully"
        }

    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Podcast Generation Endpoints
# ============================================================================

class PodcastGenerateRequest(BaseModel):
    """Request model for podcast generation."""
    query: Optional[str] = Field(None, description="RAG query for content")
    source_url: Optional[str] = Field(None, description="Source URL for content")
    style: str = Field("conversational", description="Podcast style")
    tts_engine: str = Field("auto", description="TTS engine to use")
    output_name: Optional[str] = Field(None, description="Output filename")

@app.post("/api/v1/podcast/generate")
async def generate_podcast(request: PodcastGenerateRequest):
    """
    Generate a podcast from RAG query or source URL.

    This is a long-running operation. Consider using WebSocket for progress updates.
    """
    try:
        logger.info(f"Generating podcast: query={request.query}, source={request.source_url}")

        # Import TTS and LLM services
        from tts_service import get_tts_service
        from llm_service import get_llm_service

        tts = get_tts_service()
        llm = get_llm_service()

        # Generate content
        if request.query:
            # Use RAG to generate content
            rag_engine = get_rag_engine()
            result = rag_engine.query(request.query)
            content = result['answer']
        elif request.source_url:
            # Process source URL
            from source_processor import get_source_processor
            processor = get_source_processor()
            content = processor.process_content(request.source_url)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either query or source_url must be provided"
            )

        # Generate podcast script
        podcast_script = llm.generate_podcast_script(content)

        # Generate audio
        output_name = request.output_name or f"podcast_{asyncio.get_event_loop().time()}.wav"
        output_path = Path("podcasts") / output_name
        output_path.parent.mkdir(exist_ok=True)

        audio_file = tts.generate_podcast_audio(podcast_script, str(output_path))

        return {
            "success": True,
            "audio_file": str(audio_file),
            "script_length": len(podcast_script),
            "file_size": os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
        }

    except Exception as e:
        logger.error(f"Error generating podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/podcast/list")
async def list_podcasts():
    """List all generated podcasts."""
    try:
        podcasts_dir = Path("podcasts")

        if not podcasts_dir.exists():
            return {"podcasts": []}

        podcasts = []
        for file_path in podcasts_dir.glob("*.wav"):
            podcasts.append({
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "created": file_path.stat().st_mtime
            })

        # Sort by creation time (newest first)
        podcasts.sort(key=lambda x: x['created'], reverse=True)

        return {"podcasts": podcasts}

    except Exception as e:
        logger.error(f"Error listing podcasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/podcast/{podcast_name}")
async def download_podcast(podcast_name: str):
    """Download a podcast file."""
    try:
        podcast_path = Path("podcasts") / podcast_name

        if not podcast_path.exists():
            raise HTTPException(status_code=404, detail="Podcast not found")

        return FileResponse(
            path=str(podcast_path),
            media_type="audio/wav",
            filename=podcast_name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Vector Store Search Endpoints
# ============================================================================

class SearchRequest(BaseModel):
    """Request model for vector store search."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum number of results")

@app.post("/api/v1/search")
async def search_documents(request: SearchRequest):
    """Search the vector store."""
    try:
        logger.info(f"Searching: {request.query}")

        vector_store = get_vector_store()

        # Search vector store
        results = vector_store.search(
            query=request.query,
            limit=request.limit
        )

        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents")
async def list_documents(limit: int = 50, offset: int = 0):
    """List all documents in the vector store."""
    try:
        # TODO: Implement document listing
        # This would require adding a method to the vector store service

        return {
            "documents": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

