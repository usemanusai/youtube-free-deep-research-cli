"""
Channel monitoring configuration and management.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from youtube_api import get_youtube_client, YouTubeAPIError
from video_database import get_video_database
from n8n_client import get_n8n_client
from source_processor import get_source_processor
from video_queue import get_video_queue

logger = logging.getLogger(__name__)


class ChannelMonitor:
    """Manages channel monitoring configuration and operations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize channel monitor.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        if config_path is None:
            user_data_dir = Path.home() / ".youtube-chat-cli"
            user_data_dir.mkdir(exist_ok=True)
            config_path = user_data_dir / "channel_monitor.json"
        
        self.config_path = Path(config_path)
        self.video_db = get_video_database()
        self.source_processor = get_source_processor()
        self.video_queue = get_video_queue()

        # Initialize YouTube client only when needed
        self._youtube_client = None
        
        # Load configuration
        self.config = self._load_config()
        
        logger.info(f"Channel monitor initialized with config: {self.config_path}")

    @property
    def youtube_client(self):
        """Get YouTube client, initializing only when needed."""
        if self._youtube_client is None:
            self._youtube_client = get_youtube_client()
        return self._youtube_client
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            "n8n": {
                "webhook_url": "",
                "api_key": "",
                "enabled": False
            },
            "monitoring": {
                "default_check_interval": 24,
                "max_videos_per_check": 50,
                "auto_process_transcripts": True
            }
        }
        
        if not self.config_path.exists():
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config, using defaults: {e}")
            return default_config
    
    def _save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file."""
        config = config or self.config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save config: {e}")
    
    def add_channel(self, channel_url: str, check_interval: int = 24, 
                   filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a channel for monitoring."""
        try:
            # Get channel information from YouTube API
            channel_info = self.youtube_client.get_channel_info(channel_url)
            if not channel_info:
                raise ValueError(f"Could not retrieve channel information for: {channel_url}")
            
            # Add to database
            channel_uuid = self.video_db.add_channel(
                url=channel_url,
                channel_id=channel_info.id,
                name=channel_info.title,
                description=channel_info.description,
                check_interval=check_interval,
                filters=filters
            )
            
            logger.info(f"Added channel for monitoring: {channel_info.title}")
            
            return {
                'id': channel_uuid,
                'channel_id': channel_info.id,
                'name': channel_info.title,
                'url': channel_url,
                'check_interval': check_interval,
                'filters': filters or {}
            }
            
        except YouTubeAPIError as e:
            raise ValueError(f"YouTube API error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to add channel: {e}")
    
    def remove_channel(self, channel_id: str) -> bool:
        """Remove a channel from monitoring."""
        return self.video_db.remove_channel(channel_id)
    
    def list_channels(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all monitored channels."""
        return self.video_db.get_channels(active_only=active_only)
    
    def update_channel(self, channel_id: str, **kwargs) -> bool:
        """Update channel monitoring settings."""
        return self.video_db.update_channel(channel_id, **kwargs)
    
    def scan_channel(self, channel_id: str, force: bool = False) -> Dict[str, Any]:
        """Scan a specific channel for new videos."""
        channel = self.video_db.get_channel(channel_id)
        if not channel:
            raise ValueError(f"Channel not found: {channel_id}")
        
        if not channel['active'] and not force:
            raise ValueError(f"Channel is inactive: {channel['name']}")
        
        try:
            # Calculate date filter based on last check
            published_after = None
            if channel['last_check'] and not force:
                published_after = datetime.fromisoformat(channel['last_check'])
                # Ensure timezone awareness
                if published_after.tzinfo is None:
                    published_after = published_after.replace(tzinfo=datetime.now().astimezone().tzinfo)
            elif not force:
                # Default to last 7 days for first scan
                published_after = datetime.now() - timedelta(days=7)
                # Ensure timezone awareness
                if published_after.tzinfo is None:
                    published_after = published_after.replace(tzinfo=datetime.now().astimezone().tzinfo)
            
            # Get recent videos from YouTube
            max_results = self.config['monitoring']['max_videos_per_check']
            videos = self.youtube_client.get_channel_videos(
                channel['channel_id'], 
                max_results=max_results,
                published_after=published_after
            )
            
            # Filter videos based on channel filters
            filtered_videos = self._apply_filters(videos, channel.get('filters', {}))
            
            # Process new videos using queue system
            new_videos = []
            queued_videos = []
            skipped_videos = []

            for video in filtered_videos:
                if self.video_db.is_video_processed(video.id):
                    skipped_videos.append(video.id)
                    continue

                # Add video to database
                self.video_db.add_video(
                    video_id=video.id,
                    channel_id=channel['channel_id'],
                    title=video.title,
                    url=video.url,
                    description=video.description,
                    duration=video.duration_seconds,
                    published_at=video.published_at,
                    view_count=video.view_count,
                    metadata=video.to_dict()
                )

                new_videos.append(video.id)

                # Add to processing queue instead of immediate processing
                if self.config['monitoring']['auto_process_transcripts']:
                    queue_id = self.video_queue.add_to_queue(
                        video_id=video.id,
                        channel_id=channel['channel_id'],
                        priority=1  # Channel monitoring has priority
                    )
                    if queue_id:
                        queued_videos.append(video.id)
                        logger.info(f"Added video {video.id} to processing queue")
                    else:
                        logger.info(f"Video {video.id} already in processing queue")
            
            # Update last check time
            self.video_db.update_channel(channel_id, last_check=datetime.now().isoformat())
            
            return {
                'channel_name': channel['name'],
                'total_videos_found': len(videos),
                'filtered_videos': len(filtered_videos),
                'new_videos': len(new_videos),
                'queued_for_processing': len(queued_videos),
                'skipped_videos': len(skipped_videos),
                'video_ids': new_videos
            }
            
        except YouTubeAPIError as e:
            raise ValueError(f"YouTube API error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to scan channel: {e}")
    
    def scan_all_channels(self) -> Dict[str, Any]:
        """Scan all active channels for new videos."""
        channels = self.video_db.get_channels(active_only=True)
        results = {
            'total_channels': len(channels),
            'successful_scans': 0,
            'failed_scans': 0,
            'total_new_videos': 0,
            'channel_results': []
        }
        
        for channel in channels:
            try:
                # Check if it's time to scan this channel
                if channel['last_check']:
                    last_check = datetime.fromisoformat(channel['last_check'])
                    next_check = last_check + timedelta(hours=channel['check_interval'])
                    if datetime.now() < next_check:
                        continue
                
                scan_result = self.scan_channel(channel['id'])
                results['successful_scans'] += 1
                results['total_new_videos'] += scan_result['new_videos']
                results['channel_results'].append({
                    'channel_id': channel['id'],
                    'channel_name': channel['name'],
                    'status': 'success',
                    'new_videos': scan_result['new_videos']
                })
                
            except Exception as e:
                logger.error(f"Failed to scan channel {channel['name']}: {e}")
                results['failed_scans'] += 1
                results['channel_results'].append({
                    'channel_id': channel['id'],
                    'channel_name': channel['name'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def _apply_filters(self, videos: List, filters: Dict[str, Any]) -> List:
        """Apply channel-specific filters to videos."""
        if not filters:
            return videos
        
        filtered_videos = []
        
        for video in videos:
            # Duration filters
            if 'min_duration' in filters and video.duration_seconds < filters['min_duration']:
                continue
            if 'max_duration' in filters and video.duration_seconds > filters['max_duration']:
                continue
            
            # View count filters
            if 'min_views' in filters and video.view_count < filters['min_views']:
                continue
            
            # Keyword filters
            if 'include_keywords' in filters:
                keywords = filters['include_keywords']
                if not any(keyword.lower() in video.title.lower() or 
                          keyword.lower() in video.description.lower() 
                          for keyword in keywords):
                    continue
            
            if 'exclude_keywords' in filters:
                keywords = filters['exclude_keywords']
                if any(keyword.lower() in video.title.lower() or 
                      keyword.lower() in video.description.lower() 
                      for keyword in keywords):
                    continue
            
            # Exclude shorts (videos under 60 seconds)
            if filters.get('no_shorts', False) and video.duration_seconds < 60:
                continue
            
            filtered_videos.append(video)
        
        return filtered_videos
    
    def _send_to_n8n(self, video, transcript: str, channel: Dict[str, Any]):
        """Send video data to n8n workflow."""
        try:
            n8n_client = get_n8n_client()
            
            payload = {
                'video_id': video.id,
                'title': video.title,
                'description': video.description,
                'url': video.url,
                'channel_name': channel['name'],
                'channel_id': channel['channel_id'],
                'duration': video.duration_seconds,
                'published_at': video.published_at,
                'view_count': video.view_count,
                'transcript': transcript,
                'metadata': video.to_dict()
            }
            
            # Send to n8n webhook
            response = n8n_client.send_video_data(payload)
            logger.info(f"Sent video {video.id} to n8n workflow")
            
        except Exception as e:
            logger.error(f"Failed to send video {video.id} to n8n: {e}")
    
    def configure_n8n(self, webhook_url: str, api_key: Optional[str] = None, enabled: bool = True):
        """Configure n8n integration."""
        self.config['n8n'] = {
            'webhook_url': webhook_url,
            'api_key': api_key or '',
            'enabled': enabled
        }
        self._save_config()
        logger.info("n8n configuration updated")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return self.video_db.get_statistics()


# Global channel monitor instance
_channel_monitor = None

def get_channel_monitor() -> ChannelMonitor:
    """Get or create the global channel monitor instance."""
    global _channel_monitor
    if _channel_monitor is None:
        _channel_monitor = ChannelMonitor()
    return _channel_monitor
