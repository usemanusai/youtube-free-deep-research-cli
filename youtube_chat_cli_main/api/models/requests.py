"""API request models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatQueryRequest(BaseModel):
    """Request model for RAG chat query."""
    question: str = Field(..., description="User question")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    stream: bool = Field(False, description="Enable streaming response")


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


__all__ = [
    "ChatQueryRequest",
    "FileProcessRequest",
    "ConfigUpdateRequest",
    "BackgroundServiceRequest",
]

