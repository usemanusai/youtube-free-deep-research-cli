"""
Core functionality for YouTube Chat CLI.

This module contains the fundamental components:
- YouTube API client for video and channel data
- Database management for persistent storage
- Configuration management
"""

from .youtube_api import YouTubeAPIClient, YouTubeAPIError, YouTubeVideo, YouTubeChannel, get_youtube_client
from .database import VideoDatabase, get_video_database
from .config import Config, get_config

__all__ = [
    'YouTubeAPIClient', 'YouTubeAPIError', 'YouTubeVideo', 'YouTubeChannel', 'get_youtube_client',
    'VideoDatabase', 'get_video_database',
    'Config', 'get_config'
]
