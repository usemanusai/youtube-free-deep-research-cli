"""Web search service."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/web_search_service.py
from ..web_search_service import WebSearchService

__all__ = ["WebSearchService"]

