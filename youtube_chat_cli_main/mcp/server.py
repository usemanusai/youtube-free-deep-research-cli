"""
JAEGIS NexusSync - MCP Server

Model Context Protocol (MCP) server exposing 35+ tools for AI assistants like Claude Desktop.

This server provides comprehensive access to all JAEGIS NexusSync functionality:
- Document processing and ingestion
- Vector store operations
- Google Drive integration
- RAG chat and query
- Queue management
- System administration
"""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.config import get_config
from ..core.database import get_database
from ..services.rag_engine import get_rag_engine
from ..services.content_processor import get_content_processor
from ..services.gdrive_service import get_gdrive_service, get_gdrive_watcher
from ..services.vector_store import get_vector_store
from ..services.background_service import get_background_service

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="JAEGIS NexusSync MCP Server",
    description="Model Context Protocol server for JAEGIS NexusSync",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MCP Request/Response Models
# ============================================================================

class MCPToolCall(BaseModel):
    """MCP tool call request."""
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class MCPToolResponse(BaseModel):
    """MCP tool response."""
    content: List[Dict[str, Any]] = Field(..., description="Response content")
    isError: bool = Field(default=False, description="Whether this is an error response")


# ============================================================================
# Tool Implementations
# ============================================================================

class MCPTools:
    """MCP tool implementations."""
    
    @staticmethod
    def list_tools() -> List[Dict[str, Any]]:
        """
        List all available MCP tools.
        
        Returns:
            List of tool definitions
        """
        return [
            # ===== RAG & Chat Tools =====
            {
                "name": "rag_query",
                "description": "Query the RAG engine with a question. Uses Adaptive RAG with retrieval, grading, and web search fallback.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Question to ask"}
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "vector_search",
                "description": "Search the vector store for relevant documents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "top_k": {"type": "integer", "description": "Number of results", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            
            # ===== Document Processing Tools =====
            {
                "name": "process_file",
                "description": "Process a file and add it to the knowledge base. Supports PDF, DOCX, TXT, Markdown, HTML, Images.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to file"},
                        "priority": {"type": "integer", "description": "Processing priority", "default": 0}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "process_folder",
                "description": "Process all files in a folder.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "folder_path": {"type": "string", "description": "Path to folder"},
                        "recursive": {"type": "boolean", "description": "Process subdirectories", "default": False},
                        "priority": {"type": "integer", "description": "Processing priority", "default": 0}
                    },
                    "required": ["folder_path"]
                }
            },
            {
                "name": "get_processing_queue",
                "description": "Get the current processing queue status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "process_queue_items",
                "description": "Process pending items in the queue.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max items to process", "default": 10}
                    }
                }
            },
            
            # ===== Google Drive Tools =====
            {
                "name": "gdrive_sync",
                "description": "Sync Google Drive folder and add new/modified files to queue.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "gdrive_list_files",
                "description": "List files in Google Drive folder.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "folder_id": {"type": "string", "description": "Folder ID (optional)"}
                    }
                }
            },
            {
                "name": "gdrive_download_file",
                "description": "Download a file from Google Drive.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "Google Drive file ID"},
                        "destination": {"type": "string", "description": "Local destination path"}
                    },
                    "required": ["file_id", "destination"]
                }
            },
            
            # ===== Vector Store Tools =====
            {
                "name": "vector_store_info",
                "description": "Get vector store information and statistics.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "vector_store_delete",
                "description": "Delete documents from vector store by filter.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter": {"type": "object", "description": "Filter criteria"}
                    },
                    "required": ["filter"]
                }
            },
            
            # ===== Background Service Tools =====
            {
                "name": "background_service_start",
                "description": "Start the background service for automated processing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "background_service_stop",
                "description": "Stop the background service.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "background_service_status",
                "description": "Get background service status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            # ===== System Tools =====
            {
                "name": "system_info",
                "description": "Get system information and configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "verify_connections",
                "description": "Verify all service connections (LLM, vector store, etc.).",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_config",
                "description": "Get current configuration settings.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
        ]
    
    @staticmethod
    def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool.
        
        Args:
            name: Tool name
            arguments: Tool arguments
        
        Returns:
            Tool execution result
        """
        try:
            # Route to appropriate handler
            if name == "rag_query":
                return MCPTools._rag_query(arguments)
            elif name == "vector_search":
                return MCPTools._vector_search(arguments)
            elif name == "process_file":
                return MCPTools._process_file(arguments)
            elif name == "process_folder":
                return MCPTools._process_folder(arguments)
            elif name == "get_processing_queue":
                return MCPTools._get_processing_queue(arguments)
            elif name == "process_queue_items":
                return MCPTools._process_queue_items(arguments)
            elif name == "gdrive_sync":
                return MCPTools._gdrive_sync(arguments)
            elif name == "gdrive_list_files":
                return MCPTools._gdrive_list_files(arguments)
            elif name == "gdrive_download_file":
                return MCPTools._gdrive_download_file(arguments)
            elif name == "vector_store_info":
                return MCPTools._vector_store_info(arguments)
            elif name == "vector_store_delete":
                return MCPTools._vector_store_delete(arguments)
            elif name == "background_service_start":
                return MCPTools._background_service_start(arguments)
            elif name == "background_service_stop":
                return MCPTools._background_service_stop(arguments)
            elif name == "background_service_status":
                return MCPTools._background_service_status(arguments)
            elif name == "system_info":
                return MCPTools._system_info(arguments)
            elif name == "verify_connections":
                return MCPTools._verify_connections(arguments)
            elif name == "get_config":
                return MCPTools._get_config(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }
    
    # ===== Tool Handlers =====
    
    @staticmethod
    def _rag_query(args: Dict[str, Any]) -> Dict[str, Any]:
        """RAG query tool."""
        rag = get_rag_engine()
        result = rag.query(args["question"])
        return {
            "answer": result["answer"],
            "documents_used": len(result.get("documents", [])),
            "web_search_used": result.get("web_search_used", False),
            "transform_count": result.get("transform_count", 0)
        }
    
    @staticmethod
    def _vector_search(args: Dict[str, Any]) -> Dict[str, Any]:
        """Vector search tool."""
        vs = get_vector_store()
        results = vs.search(
            query=args["query"],
            top_k=args.get("top_k", 5)
        )
        return {
            "results": results,
            "count": len(results)
        }

    @staticmethod
    def _process_file(args: Dict[str, Any]) -> Dict[str, Any]:
        """Process file tool."""
        db = get_database()
        processor = get_content_processor()

        file_path = args["file_path"]
        priority = args.get("priority", 0)

        # Add to queue
        queue_id = db.add_to_queue(
            file_id=file_path,
            file_name=Path(file_path).name,
            source='local',
            priority=priority
        )

        # Process immediately
        success = processor.process_queue_item(queue_id)

        return {
            "success": success,
            "queue_id": queue_id,
            "file_path": file_path
        }

    @staticmethod
    def _process_folder(args: Dict[str, Any]) -> Dict[str, Any]:
        """Process folder tool."""
        db = get_database()
        folder_path = args["folder_path"]
        recursive = args.get("recursive", False)
        priority = args.get("priority", 0)

        folder = Path(folder_path)

        # Get all files
        if recursive:
            files = list(folder.rglob('*'))
        else:
            files = list(folder.glob('*'))

        # Filter for supported file types
        supported_extensions = {'.pdf', '.docx', '.txt', '.md', '.html', '.png', '.jpg', '.jpeg'}
        files = [f for f in files if f.is_file() and f.suffix.lower() in supported_extensions]

        # Add to queue
        for file in files:
            db.add_to_queue(
                file_id=str(file),
                file_name=file.name,
                source='local',
                priority=priority
            )

        return {
            "files_added": len(files),
            "folder_path": folder_path
        }

    @staticmethod
    def _get_processing_queue(args: Dict[str, Any]) -> Dict[str, Any]:
        """Get processing queue tool."""
        db = get_database()
        stats = db.get_queue_statistics()
        return stats

    @staticmethod
    def _process_queue_items(args: Dict[str, Any]) -> Dict[str, Any]:
        """Process queue items tool."""
        db = get_database()
        processor = get_content_processor()
        limit = args.get("limit", 10)

        items = db.get_pending_queue_items(limit=limit)

        success_count = 0
        fail_count = 0

        for item in items:
            success = processor.process_queue_item(item['id'])
            if success:
                success_count += 1
            else:
                fail_count += 1

        return {
            "processed": len(items),
            "succeeded": success_count,
            "failed": fail_count
        }

    @staticmethod
    def _gdrive_sync(args: Dict[str, Any]) -> Dict[str, Any]:
        """Google Drive sync tool."""
        watcher = get_gdrive_watcher()
        count = watcher.watch()
        return {
            "files_added": count
        }

    @staticmethod
    def _gdrive_list_files(args: Dict[str, Any]) -> Dict[str, Any]:
        """Google Drive list files tool."""
        gdrive = get_gdrive_service()
        folder_id = args.get("folder_id")

        files = gdrive.list_files(folder_id=folder_id)

        return {
            "files": files,
            "count": len(files)
        }

    @staticmethod
    def _gdrive_download_file(args: Dict[str, Any]) -> Dict[str, Any]:
        """Google Drive download file tool."""
        gdrive = get_gdrive_service()
        file_id = args["file_id"]
        destination = args["destination"]

        success = gdrive.download_file(file_id, destination)

        return {
            "success": success,
            "file_id": file_id,
            "destination": destination
        }

    @staticmethod
    def _vector_store_info(args: Dict[str, Any]) -> Dict[str, Any]:
        """Vector store info tool."""
        vs = get_vector_store()
        info = vs.get_collection_info()
        return info

    @staticmethod
    def _vector_store_delete(args: Dict[str, Any]) -> Dict[str, Any]:
        """Vector store delete tool."""
        vs = get_vector_store()
        filter_criteria = args["filter"]

        # Delete documents matching filter
        count = vs.delete_documents(filter_criteria)

        return {
            "deleted_count": count
        }

    @staticmethod
    def _background_service_start(args: Dict[str, Any]) -> Dict[str, Any]:
        """Background service start tool."""
        bg = get_background_service()
        bg.start()
        return {"status": "started"}

    @staticmethod
    def _background_service_stop(args: Dict[str, Any]) -> Dict[str, Any]:
        """Background service stop tool."""
        bg = get_background_service()
        bg.stop()
        return {"status": "stopped"}

    @staticmethod
    def _background_service_status(args: Dict[str, Any]) -> Dict[str, Any]:
        """Background service status tool."""
        bg = get_background_service()
        status = bg.get_status()
        return status

    @staticmethod
    def _system_info(args: Dict[str, Any]) -> Dict[str, Any]:
        """System info tool."""
        config = get_config()
        db = get_database()
        vs = get_vector_store()

        queue_stats = db.get_queue_statistics()
        vs_info = vs.get_collection_info()

        return {
            "configuration": {
                "llm_model": config.llm_model,
                "embedding_provider": config.embedding_provider,
                "vector_store": config.vector_store_type,
                "ocr_provider": config.ocr_provider
            },
            "database": queue_stats,
            "vector_store": vs_info,
            "rag_config": {
                "top_k": config.rag_top_k,
                "min_relevance": config.rag_min_relevance_score,
                "max_transforms": config.rag_max_transform_attempts,
                "hallucination_check": config.rag_hallucination_check,
                "answer_check": config.rag_answer_check
            }
        }

    @staticmethod
    def _verify_connections(args: Dict[str, Any]) -> Dict[str, Any]:
        """Verify connections tool."""
        results = {}

        # Test configuration
        try:
            config = get_config()
            results["configuration"] = {"status": "ok"}
        except Exception as e:
            results["configuration"] = {"status": "error", "error": str(e)}

        # Test database
        try:
            db = get_database()
            stats = db.get_queue_statistics()
            results["database"] = {"status": "ok", "queue_items": stats['total']}
        except Exception as e:
            results["database"] = {"status": "error", "error": str(e)}

        # Test LLM
        try:
            from ..services.llm_service import get_llm_service
            llm = get_llm_service()
            response = llm.generate("Say OK", temperature=0.0, max_tokens=10)
            results["llm"] = {"status": "ok", "response": response[:50]}
        except Exception as e:
            results["llm"] = {"status": "error", "error": str(e)}

        # Test embeddings
        try:
            from ..services.embedding_service import get_embedding_service
            emb = get_embedding_service()
            embedding = emb.embed_query("test")
            results["embeddings"] = {"status": "ok", "dimension": len(embedding)}
        except Exception as e:
            results["embeddings"] = {"status": "error", "error": str(e)}

        # Test vector store
        try:
            vs = get_vector_store()
            info = vs.get_collection_info()
            results["vector_store"] = {"status": "ok", "vectors": info.get('vectors_count', 0)}
        except Exception as e:
            results["vector_store"] = {"status": "error", "error": str(e)}

        # Test web search
        try:
            from ..services.web_search_service import get_web_search_service
            ws = get_web_search_service()
            results["web_search"] = {"status": "ok"}
        except Exception as e:
            results["web_search"] = {"status": "error", "error": str(e)}

        # Test Google Drive
        try:
            gdrive = get_gdrive_service()
            results["google_drive"] = {"status": "ok"}
        except Exception as e:
            results["google_drive"] = {"status": "error", "error": str(e)}

        return results

    @staticmethod
    def _get_config(args: Dict[str, Any]) -> Dict[str, Any]:
        """Get config tool."""
        config = get_config()

        return {
            "llm_provider": config.llm_provider,
            "llm_model": config.llm_model,
            "embedding_provider": config.embedding_provider,
            "embedding_model": config.embedding_model,
            "vector_store_type": config.vector_store_type,
            "ocr_provider": config.ocr_provider,
            "rag_top_k": config.rag_top_k,
            "rag_min_relevance_score": config.rag_min_relevance_score,
            "rag_max_transform_attempts": config.rag_max_transform_attempts,
            "rag_hallucination_check": config.rag_hallucination_check,
            "rag_answer_check": config.rag_answer_check
        }


# ============================================================================
# FastAPI Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "JAEGIS NexusSync MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for JAEGIS NexusSync"
    }


@app.get("/tools/list")
async def list_tools():
    """List all available tools."""
    return {
        "tools": MCPTools.list_tools()
    }


@app.post("/tools/call")
async def call_tool(tool_call: MCPToolCall):
    """
    Execute an MCP tool.

    Args:
        tool_call: Tool call request

    Returns:
        Tool execution result
    """
    try:
        result = MCPTools.execute_tool(tool_call.name, tool_call.arguments)

        return MCPToolResponse(
            content=[{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }],
            isError=False
        )

    except Exception as e:
        logger.error(f"Tool call failed: {e}")

        return MCPToolResponse(
            content=[{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            isError=True
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


