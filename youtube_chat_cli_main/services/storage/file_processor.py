"""File processor storage."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in file_processor.py
from ...file_processor import FileProcessor, get_file_processor

__all__ = ["FileProcessor", "get_file_processor"]

