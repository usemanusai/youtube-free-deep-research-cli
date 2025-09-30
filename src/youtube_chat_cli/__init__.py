"""
YouTube Chat CLI - AI-powered tool for YouTube video analysis and channel monitoring.

This package provides comprehensive functionality for:
- Interactive chat with YouTube video transcripts
- Automated channel monitoring with intelligent rate limiting
- Bulk import from channels, playlists, and URL files
- Text-to-speech generation with multiple TTS libraries
- n8n RAG workflow integration
- Background service for continuous monitoring
"""

__version__ = "2.0.0"
__author__ = "YouTube Chat CLI Team"
__email__ = "youtube-chat-cli@example.com"

# Core functionality
from .core.youtube_api import YouTubeAPIClient, YouTubeAPIError, get_youtube_client
from .core.database import VideoDatabase, get_video_database
from .core.config import Config, get_config

# Services
from .services.tts.service import TTSService, get_tts_service
from .services.tts.config_manager import TTSConfigManager, get_tts_config_manager
from .services.transcription.processor import SourceProcessor, get_source_processor
from .services.monitoring.channel_monitor import ChannelMonitor, get_channel_monitor
from .services.monitoring.video_processor import VideoProcessor, get_video_processor
from .services.monitoring.background_service import YouTubeMonitoringService, get_monitoring_service
from .services.import_service.bulk_import import BulkImporter, get_bulk_importer
from .services.n8n.client import N8nClient, get_n8n_client

# Queue system
from .services.monitoring.video_queue import VideoProcessingQueue, get_video_queue

# Session management
from .utils.session_manager import SessionManager

# LLM service
from .utils.llm_service import LLMService, get_llm_service

__all__ = [
    # Core
    'YouTubeAPIClient', 'YouTubeAPIError', 'get_youtube_client',
    'VideoDatabase', 'get_video_database',
    'Config', 'get_config',
    
    # Services
    'TTSService', 'get_tts_service',
    'TTSConfigManager', 'get_tts_config_manager',
    'SourceProcessor', 'get_source_processor',
    'ChannelMonitor', 'get_channel_monitor',
    'VideoProcessor', 'get_video_processor',
    'YouTubeMonitoringService', 'get_monitoring_service',
    'BulkImporter', 'get_bulk_importer',
    'N8nClient', 'get_n8n_client',
    'VideoProcessingQueue', 'get_video_queue',
    
    # Utils
    'SessionManager',
    'LLMService', 'get_llm_service',
    
    # Metadata
    '__version__', '__author__', '__email__'
]
