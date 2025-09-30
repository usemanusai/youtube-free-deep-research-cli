"""
Services module for YouTube Chat CLI.

This module contains all service implementations:
- TTS (Text-to-Speech) services
- Transcription processing
- Channel monitoring and video processing
- Bulk import functionality
- n8n integration
"""

# Import all services for easy access
from .tts.service import TTSService, get_tts_service
from .tts.config_manager import TTSConfigManager, get_tts_config_manager
from .transcription.processor import SourceProcessor, get_source_processor
from .monitoring.channel_monitor import ChannelMonitor, get_channel_monitor
from .monitoring.video_processor import VideoProcessor, get_video_processor
from .monitoring.background_service import YouTubeMonitoringService, get_monitoring_service
from .monitoring.video_queue import VideoProcessingQueue, get_video_queue
from .import_service.bulk_import import BulkImporter, get_bulk_importer
from .n8n.client import N8nClient, get_n8n_client

__all__ = [
    'TTSService', 'get_tts_service',
    'TTSConfigManager', 'get_tts_config_manager',
    'SourceProcessor', 'get_source_processor',
    'ChannelMonitor', 'get_channel_monitor',
    'VideoProcessor', 'get_video_processor',
    'YouTubeMonitoringService', 'get_monitoring_service',
    'VideoProcessingQueue', 'get_video_queue',
    'BulkImporter', 'get_bulk_importer',
    'N8nClient', 'get_n8n_client'
]
