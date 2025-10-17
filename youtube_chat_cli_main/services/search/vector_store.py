"""Vector store service."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/vector_store.py
from ..vector_store import VectorStore

__all__ = ["VectorStoreService"]


class VectorStoreService(VectorStore):
    """Vector store service wrapper."""
    pass

