"""
Podcast generation services for YouTube Chat CLI.

This module provides functionality for generating podcast-style audio content
from YouTube videos with optional n8n RAG workflow integration.
"""

from .generator import PodcastGenerator, get_podcast_generator

__all__ = [
    'PodcastGenerator',
    'get_podcast_generator'
]
