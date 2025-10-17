"""Vector store storage."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/vector_store.py
from ..vector_store import VectorStore, get_vector_store

__all__ = ["VectorStore", "get_vector_store"]

