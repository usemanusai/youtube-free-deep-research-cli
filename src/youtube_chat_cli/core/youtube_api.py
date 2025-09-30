"""
YouTube Data API client for channel monitoring and video discovery.
"""

import os
import re
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import json

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.exceptions import GoogleAuthError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class YouTubeAPIError(Exception):
    """YouTube API related errors."""
    pass


class RateLimitError(YouTubeAPIError):
    """API rate limit exceeded."""
    pass


class YouTubeVideo:
    """Represents a YouTube video with metadata."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.title = data.get('snippet', {}).get('title', '')
        self.description = data.get('snippet', {}).get('description', '')
        self.channel_id = data.get('snippet', {}).get('channelId', '')
        self.channel_title = data.get('snippet', {}).get('channelTitle', '')
        self.published_at = data.get('snippet', {}).get('publishedAt', '')
        self.thumbnail_url = data.get('snippet', {}).get('thumbnails', {}).get('medium', {}).get('url', '')
        
        # Statistics (if available)
        stats = data.get('statistics', {})
        self.view_count = int(stats.get('viewCount', 0))
        self.like_count = int(stats.get('likeCount', 0))
        self.comment_count = int(stats.get('commentCount', 0))
        
        # Content details (if available)
        content = data.get('contentDetails', {})
        self.duration = content.get('duration', '')
        self.duration_seconds = self._parse_duration(self.duration)
        
        # Build URL
        self.url = f"https://www.youtube.com/watch?v={self.id}"
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        if not duration:
            return 0
        
        # Parse PT1H2M3S format
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'channel_id': self.channel_id,
            'channel_title': self.channel_title,
            'published_at': self.published_at,
            'url': self.url,
            'duration_seconds': self.duration_seconds,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'thumbnail_url': self.thumbnail_url
        }


class YouTubeChannel:
    """Represents a YouTube channel with metadata."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.title = data.get('snippet', {}).get('title', '')
        self.description = data.get('snippet', {}).get('description', '')
        self.custom_url = data.get('snippet', {}).get('customUrl', '')
        self.thumbnail_url = data.get('snippet', {}).get('thumbnails', {}).get('medium', {}).get('url', '')
        
        # Statistics
        stats = data.get('statistics', {})
        self.subscriber_count = int(stats.get('subscriberCount', 0))
        self.video_count = int(stats.get('videoCount', 0))
        self.view_count = int(stats.get('viewCount', 0))
        
        # Build URL
        if self.custom_url:
            self.url = f"https://www.youtube.com/@{self.custom_url}"
        else:
            self.url = f"https://www.youtube.com/channel/{self.id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'subscriber_count': self.subscriber_count,
            'video_count': self.video_count,
            'view_count': self.view_count,
            'thumbnail_url': self.thumbnail_url
        }


class YouTubeAPIClient:
    """YouTube Data API v3 client with rate limiting and caching."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API key. If None, will try to get from environment.
        """
        if not YOUTUBE_API_AVAILABLE:
            raise YouTubeAPIError("YouTube API dependencies not installed. Run: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise YouTubeAPIError("YouTube API key not provided. Set YOUTUBE_API_KEY environment variable or pass api_key parameter.")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        except GoogleAuthError as e:
            raise YouTubeAPIError(f"Failed to initialize YouTube API client: {e}")
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        self.quota_used = 0
        self.daily_quota_limit = 10000  # Default quota limit
        
        logger.info("YouTube API client initialized successfully")
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, request, quota_cost: int = 1) -> Any:
        """Make API request with rate limiting and error handling."""
        if self.quota_used + quota_cost > self.daily_quota_limit:
            raise RateLimitError(f"Daily quota limit ({self.daily_quota_limit}) would be exceeded")
        
        self._wait_for_rate_limit()
        
        try:
            response = request.execute()
            self.quota_used += quota_cost
            logger.debug(f"API request successful, quota used: {self.quota_used}/{self.daily_quota_limit}")
            return response
        except HttpError as e:
            if e.resp.status == 403:
                error_details = json.loads(e.content.decode())
                error_reason = error_details.get('error', {}).get('errors', [{}])[0].get('reason', '')
                
                if error_reason == 'quotaExceeded':
                    raise RateLimitError("YouTube API quota exceeded")
                elif error_reason == 'keyInvalid':
                    raise YouTubeAPIError("Invalid YouTube API key")
                else:
                    raise YouTubeAPIError(f"YouTube API error: {e}")
            else:
                raise YouTubeAPIError(f"YouTube API HTTP error: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"Unexpected YouTube API error: {e}")
    
    def extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from various YouTube URL formats."""
        # Handle different URL formats
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                identifier = match.group(1)
                
                # If it's already a channel ID (starts with UC), return it
                if identifier.startswith('UC') and len(identifier) == 24:
                    return identifier
                
                # Otherwise, resolve it via API
                return self._resolve_channel_identifier(identifier, url)
        
        return None
    
    def _resolve_channel_identifier(self, identifier: str, original_url: str) -> Optional[str]:
        """Resolve channel identifier to channel ID via API."""
        try:
            # Try by username first
            request = self.youtube.channels().list(
                part='id',
                forUsername=identifier
            )
            response = self._make_request(request, quota_cost=1)
            
            if response.get('items'):
                return response['items'][0]['id']
            
            # Try by custom URL
            request = self.youtube.search().list(
                part='id',
                q=identifier,
                type='channel',
                maxResults=1
            )
            response = self._make_request(request, quota_cost=100)
            
            if response.get('items'):
                return response['items'][0]['id']['channelId']
            
        except Exception as e:
            logger.warning(f"Failed to resolve channel identifier '{identifier}': {e}")
        
        return None

    def get_channel_info(self, channel_url: str) -> Optional[YouTubeChannel]:
        """Get channel information from URL."""
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            raise YouTubeAPIError(f"Could not extract channel ID from URL: {channel_url}")

        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            response = self._make_request(request, quota_cost=1)

            if not response.get('items'):
                raise YouTubeAPIError(f"Channel not found: {channel_id}")

            return YouTubeChannel(response['items'][0])

        except Exception as e:
            raise YouTubeAPIError(f"Failed to get channel info: {e}")

    def get_channel_videos(self, channel_id: str, max_results: int = 50,
                          published_after: Optional[datetime] = None) -> List[YouTubeVideo]:
        """Get recent videos from a channel."""
        try:
            # First, get the uploads playlist ID
            request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            response = self._make_request(request, quota_cost=1)

            if not response.get('items'):
                raise YouTubeAPIError(f"Channel not found: {channel_id}")

            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # Get videos from uploads playlist
            videos = []
            next_page_token = None

            while len(videos) < max_results:
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                response = self._make_request(request, quota_cost=1)

                items = response.get('items', [])
                if not items:
                    break

                # Filter by date if specified
                for item in items:
                    if published_after:
                        published_at = datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00'))
                        # Ensure both datetimes are timezone-aware for comparison
                        if published_after.tzinfo is None:
                            published_after = published_after.replace(tzinfo=published_at.tzinfo)
                        if published_at < published_after:
                            continue

                    video_id = item['snippet']['resourceId']['videoId']
                    videos.append(video_id)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            # Get detailed video information
            return self.get_video_details(videos[:max_results])

        except Exception as e:
            raise YouTubeAPIError(f"Failed to get channel videos: {e}")

    def get_video_details(self, video_ids: List[str]) -> List[YouTubeVideo]:
        """Get detailed information for multiple videos."""
        if not video_ids:
            return []

        videos = []

        # Process in batches of 50 (API limit)
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]

            try:
                request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch)
                )
                response = self._make_request(request, quota_cost=1)

                for item in response.get('items', []):
                    videos.append(YouTubeVideo(item))

            except Exception as e:
                logger.warning(f"Failed to get details for video batch: {e}")
                continue

        return videos

    def get_playlist_videos(self, playlist_url: str, max_results: int = 50) -> List[YouTubeVideo]:
        """Get videos from a playlist."""
        # Extract playlist ID from URL
        playlist_id = self._extract_playlist_id(playlist_url)
        if not playlist_id:
            raise YouTubeAPIError(f"Could not extract playlist ID from URL: {playlist_url}")

        try:
            videos = []
            video_ids = []
            next_page_token = None

            while len(video_ids) < max_results:
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(video_ids)),
                    pageToken=next_page_token
                )
                response = self._make_request(request, quota_cost=1)

                items = response.get('items', [])
                if not items:
                    break

                for item in items:
                    video_id = item['snippet']['resourceId']['videoId']
                    video_ids.append(video_id)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            # Get detailed video information
            return self.get_video_details(video_ids[:max_results])

        except Exception as e:
            raise YouTubeAPIError(f"Failed to get playlist videos: {e}")

    def _extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL."""
        parsed_url = urlparse(url)
        if 'list' in parse_qs(parsed_url.query):
            return parse_qs(parsed_url.query)['list'][0]
        return None

    def search_videos(self, query: str, channel_id: Optional[str] = None,
                     max_results: int = 50) -> List[YouTubeVideo]:
        """Search for videos with optional channel filter."""
        try:
            video_ids = []
            next_page_token = None

            while len(video_ids) < max_results:
                request = self.youtube.search().list(
                    part='id',
                    q=query,
                    type='video',
                    channelId=channel_id,
                    maxResults=min(50, max_results - len(video_ids)),
                    pageToken=next_page_token
                )
                response = self._make_request(request, quota_cost=100)

                items = response.get('items', [])
                if not items:
                    break

                for item in items:
                    video_ids.append(item['id']['videoId'])

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            # Get detailed video information
            return self.get_video_details(video_ids[:max_results])

        except Exception as e:
            raise YouTubeAPIError(f"Failed to search videos: {e}")

    def get_quota_usage(self) -> Dict[str, int]:
        """Get current quota usage information."""
        return {
            'used': self.quota_used,
            'limit': self.daily_quota_limit,
            'remaining': self.daily_quota_limit - self.quota_used
        }


# Global YouTube API client instance
_youtube_client = None

def get_youtube_client() -> YouTubeAPIClient:
    """Get or create the global YouTube API client instance."""
    global _youtube_client
    if _youtube_client is None:
        _youtube_client = YouTubeAPIClient()
    return _youtube_client
