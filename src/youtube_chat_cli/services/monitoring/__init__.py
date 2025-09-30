"""
Channel monitoring and video processing services.

Provides automated monitoring of YouTube channels with:
- Channel configuration and management
- Video processing queue with rate limiting
- Background service for continuous monitoring
- Intelligent scheduling to prevent IP blocking
"""

from .channel_monitor import ChannelMonitor, get_channel_monitor
from .video_processor import VideoProcessor, get_video_processor
from .background_service import YouTubeMonitoringService, get_monitoring_service
from .video_queue import VideoProcessingQueue, get_video_queue

__all__ = [
    'ChannelMonitor', 'get_channel_monitor',
    'VideoProcessor', 'get_video_processor',
    'YouTubeMonitoringService', 'get_monitoring_service',
    'VideoProcessingQueue', 'get_video_queue'
]
