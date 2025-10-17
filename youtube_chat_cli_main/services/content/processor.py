"""Content processor."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/content_processor.py
from ..content_processor import ContentProcessor, get_content_processor

__all__ = ["ContentProcessor", "get_content_processor"]

