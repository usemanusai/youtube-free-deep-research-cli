"""API response models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatQueryResponse(BaseModel):
    """Response model for RAG chat query."""
    answer: str
    question: str
    documents: List[Dict[str, Any]] = []
    web_search_used: bool = False
    transform_count: int = 0
    session_id: Optional[str] = None


class FileProcessResponse(BaseModel):
    """Response model for file processing."""
    job_id: str
    status: str
    file_path: str
    progress: int = 0


class ConfigResponse(BaseModel):
    """Response model for configuration."""
    config: Dict[str, Any]


class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    services: Dict[str, Dict[str, Any]]
    uptime: Optional[str] = None
    version: str = "2.0.0"


__all__ = [
    "ChatQueryResponse",
    "FileProcessResponse",
    "ConfigResponse",
    "SystemStatusResponse",
]

