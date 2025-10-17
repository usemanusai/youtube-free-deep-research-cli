"""Pydantic models for API requests and responses."""

from .requests import (
    ChatQueryRequest,
    FileProcessRequest,
    ConfigUpdateRequest,
    BackgroundServiceRequest,
)

from .responses import (
    ChatQueryResponse,
    FileProcessResponse,
    ConfigResponse,
    SystemStatusResponse,
)

from .schemas import (
    DocumentSchema,
    SearchResultSchema,
    ErrorSchema,
)

__all__ = [
    # Requests
    "ChatQueryRequest",
    "FileProcessRequest",
    "ConfigUpdateRequest",
    "BackgroundServiceRequest",
    # Responses
    "ChatQueryResponse",
    "FileProcessResponse",
    "ConfigResponse",
    "SystemStatusResponse",
    # Schemas
    "DocumentSchema",
    "SearchResultSchema",
    "ErrorSchema",
]

