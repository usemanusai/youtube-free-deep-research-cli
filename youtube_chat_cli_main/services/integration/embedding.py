"""Embedding service integration."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/embedding_service.py
from ..embedding_service import EmbeddingService, get_embedding_service

__all__ = ["EmbeddingService", "get_embedding_service"]

