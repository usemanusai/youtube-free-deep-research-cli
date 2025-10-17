"""Brave search service."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/brave_search_service.py
from ..brave_search_service import BraveSearchService

__all__ = ["BraveSearchService"]

