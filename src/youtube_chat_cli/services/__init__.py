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
from .podcast.generator import PodcastGenerator, get_podcast_generator
from .podcast.styles import get_style_manager, PodcastStyle, PodcastLength, PodcastTone
from .content.source_manager import get_source_manager, SourceManager, SourceType, SourceLocation, SourceFilter
from .blueprint.generator import get_blueprint_generator, BlueprintGenerator, BlueprintFormat, BlueprintStyle
from .workflow.manager import get_workflow_manager, WorkflowManager, WorkflowConfig, WorkflowStatus
from .chat.interface import get_chat_interface, InteractiveChatInterface, ChatSession

__all__ = [
    # TTS Services
    'TTSService', 'get_tts_service',
    'TTSConfigManager', 'get_tts_config_manager',

    # Content Processing
    'SourceProcessor', 'get_source_processor',
    'SourceManager', 'get_source_manager', 'SourceType', 'SourceLocation', 'SourceFilter',

    # Monitoring Services
    'ChannelMonitor', 'get_channel_monitor',
    'VideoProcessor', 'get_video_processor',
    'YouTubeMonitoringService', 'get_monitoring_service',
    'VideoProcessingQueue', 'get_video_queue',

    # Import Services
    'BulkImporter', 'get_bulk_importer',

    # External Integrations
    'N8nClient', 'get_n8n_client',

    # Podcast Generation
    'PodcastGenerator', 'get_podcast_generator',
    'get_style_manager', 'PodcastStyle', 'PodcastLength', 'PodcastTone',

    # Blueprint Generation
    'BlueprintGenerator', 'get_blueprint_generator', 'BlueprintFormat', 'BlueprintStyle',

    # Workflow Management
    'WorkflowManager', 'get_workflow_manager', 'WorkflowConfig', 'WorkflowStatus',

    # Interactive Chat
    'InteractiveChatInterface', 'get_chat_interface', 'ChatSession'
]
