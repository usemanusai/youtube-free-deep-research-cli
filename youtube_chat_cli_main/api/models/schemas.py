"""Common API schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class DocumentSchema(BaseModel):
    """Document schema."""
    id: str
    content: str
    metadata: Dict[str, Any] = {}
    score: Optional[float] = None


class SearchResultSchema(BaseModel):
    """Search result schema."""
    title: str
    url: str
    snippet: str
    source: str


class ErrorSchema(BaseModel):
    """Error schema."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


__all__ = [
    "DocumentSchema",
    "SearchResultSchema",
    "ErrorSchema",
]

