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

