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
from core.config import get_config
from core.database import get_database
from services.rag_engine import get_rag_engine
from services.content_processor import get_content_processor
from services.gdrive_service import get_gdrive_watcher
from services.background_service import get_background_service
from services.vector_store import get_vector_store
from services.llm_service import get_llm_service

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

