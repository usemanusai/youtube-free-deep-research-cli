"""
Transcription and content processing services.

Handles extraction and processing of content from:
- YouTube videos (transcripts)
- Web pages (text content)
- Content formatting and punctuation
"""

from .processor import SourceProcessor, get_source_processor

__all__ = ['SourceProcessor', 'get_source_processor']
