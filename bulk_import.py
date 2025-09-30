"""
Bulk import functionality for YouTube videos and channels.
"""

import logging
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime, timedelta
from pathlib import Path
import time

from tqdm import tqdm

from youtube_api import get_youtube_client, YouTubeAPIError, YouTubeVideo
from video_database import get_video_database
from source_processor import get_source_processor
from n8n_client import get_n8n_client

logger = logging.getLogger(__name__)


class BulkImporter:
    """Handles bulk import operations for YouTube content."""
    
    def __init__(self):
        """Initialize bulk importer."""
        self.youtube_client = get_youtube_client()
        self.video_db = get_video_database()
        self.source_processor = get_source_processor()
        self.n8n_client = get_n8n_client()
        
        logger.info("Bulk importer initialized")
    
    def import_from_channel(self, channel_url: str, limit: int = 50, 
                           date_from: Optional[datetime] = None,
                           date_to: Optional[datetime] = None,
                           filters: Optional[Dict[str, Any]] = None,
                           dry_run: bool = False,
                           send_to_n8n: bool = True) -> Dict[str, Any]:
        """Import videos from a YouTube channel.
        
        Args:
            channel_url: YouTube channel URL
            limit: Maximum number of videos to import
            date_from: Only import videos published after this date
            date_to: Only import videos published before this date
            filters: Additional filters to apply
            dry_run: If True, only preview what would be imported
            send_to_n8n: If True, send processed videos to n8n workflow
            
        Returns:
            Import results summary
        """
        try:
            # Get channel information
            channel_info = self.youtube_client.get_channel_info(channel_url)
            if not channel_info:
                raise ValueError(f"Could not retrieve channel information for: {channel_url}")
            
            # Create import job
            job_id = self.video_db.create_import_job(
                job_type='channel',
                source=channel_url,
                total=limit,
                filters=filters
            )
            
            if not dry_run:
                self.video_db.update_import_job(job_id, status='running')
            
            # Get videos from channel
            videos = self.youtube_client.get_channel_videos(
                channel_info.id,
                max_results=limit,
                published_after=date_from
            )
            
            # Apply date and other filters
            filtered_videos = self._apply_import_filters(videos, date_from, date_to, filters)
            
            if dry_run:
                return self._generate_dry_run_report(filtered_videos, 'channel', channel_info.title)
            
            # Process videos
            results = self._process_videos(
                filtered_videos, 
                channel_info, 
                job_id, 
                send_to_n8n=send_to_n8n
            )
            
            # Update job status
            self.video_db.update_import_job(job_id, status='completed')
            
            return results
            
        except Exception as e:
            if not dry_run:
                self.video_db.update_import_job(job_id, status='failed', error_message=str(e))
            raise ValueError(f"Channel import failed: {e}")
    
    def import_from_playlist(self, playlist_url: str, limit: int = 50,
                            filters: Optional[Dict[str, Any]] = None,
                            dry_run: bool = False,
                            send_to_n8n: bool = True) -> Dict[str, Any]:
        """Import videos from a YouTube playlist."""
        try:
            # Create import job
            job_id = self.video_db.create_import_job(
                job_type='playlist',
                source=playlist_url,
                total=limit,
                filters=filters
            )
            
            if not dry_run:
                self.video_db.update_import_job(job_id, status='running')
            
            # Get videos from playlist
            videos = self.youtube_client.get_playlist_videos(playlist_url, max_results=limit)
            
            # Apply filters
            filtered_videos = self._apply_import_filters(videos, None, None, filters)
            
            if dry_run:
                return self._generate_dry_run_report(filtered_videos, 'playlist', playlist_url)
            
            # Process videos
            results = self._process_videos(
                filtered_videos, 
                None, 
                job_id, 
                send_to_n8n=send_to_n8n
            )
            
            # Update job status
            self.video_db.update_import_job(job_id, status='completed')
            
            return results
            
        except Exception as e:
            if not dry_run:
                self.video_db.update_import_job(job_id, status='failed', error_message=str(e))
            raise ValueError(f"Playlist import failed: {e}")
    
    def import_from_file(self, file_path: str, filters: Optional[Dict[str, Any]] = None,
                        dry_run: bool = False, send_to_n8n: bool = True) -> Dict[str, Any]:
        """Import videos from a file containing URLs (one per line)."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")
            
            # Read URLs from file
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                raise ValueError("No valid URLs found in file")
            
            # Create import job
            job_id = self.video_db.create_import_job(
                job_type='file',
                source=str(file_path),
                total=len(urls),
                filters=filters
            )
            
            if not dry_run:
                self.video_db.update_import_job(job_id, status='running')
            
            # Extract video IDs and get video details
            video_ids = []
            for url in urls:
                video_id = self.source_processor.extract_youtube_video_id(url)
                if video_id:
                    video_ids.append(video_id)
            
            if not video_ids:
                raise ValueError("No valid YouTube video URLs found in file")
            
            # Get video details
            videos = self.youtube_client.get_video_details(video_ids)
            
            # Apply filters
            filtered_videos = self._apply_import_filters(videos, None, None, filters)
            
            if dry_run:
                return self._generate_dry_run_report(filtered_videos, 'file', str(file_path))
            
            # Process videos
            results = self._process_videos(
                filtered_videos, 
                None, 
                job_id, 
                send_to_n8n=send_to_n8n
            )
            
            # Update job status
            self.video_db.update_import_job(job_id, status='completed')
            
            return results
            
        except Exception as e:
            if not dry_run:
                self.video_db.update_import_job(job_id, status='failed', error_message=str(e))
            raise ValueError(f"File import failed: {e}")
    
    def _apply_import_filters(self, videos: List[YouTubeVideo], 
                             date_from: Optional[datetime],
                             date_to: Optional[datetime],
                             filters: Optional[Dict[str, Any]]) -> List[YouTubeVideo]:
        """Apply filters to video list."""
        filtered_videos = []
        
        for video in videos:
            # Date filters
            if date_from or date_to:
                try:
                    published_at = datetime.fromisoformat(video.published_at.replace('Z', '+00:00'))
                    if date_from and published_at < date_from:
                        continue
                    if date_to and published_at > date_to:
                        continue
                except (ValueError, AttributeError):
                    # Skip videos with invalid dates
                    continue
            
            # Apply additional filters
            if filters:
                # Duration filters
                if 'min_duration' in filters and video.duration_seconds < filters['min_duration']:
                    continue
                if 'max_duration' in filters and video.duration_seconds > filters['max_duration']:
                    continue
                
                # View count filters
                if 'min_views' in filters and video.view_count < filters['min_views']:
                    continue
                
                # Quality filters (basic implementation)
                if 'min_quality' in filters:
                    # This would require additional API calls to get video quality info
                    # For now, we'll skip this filter
                    pass
                
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
                
                # Exclude shorts
                if filters.get('no_shorts', False) and video.duration_seconds < 60:
                    continue
                
                # Exclude live streams (basic check)
                if filters.get('no_live', False) and 'live' in video.title.lower():
                    continue
            
            filtered_videos.append(video)
        
        return filtered_videos
    
    def _process_videos(self, videos: List[YouTubeVideo], channel_info, job_id: str,
                       send_to_n8n: bool = True) -> Dict[str, Any]:
        """Process a list of videos."""
        results = {
            'total_videos': len(videos),
            'new_videos': 0,
            'skipped_videos': 0,
            'processed_videos': 0,
            'failed_videos': 0,
            'video_ids': []
        }
        
        # Progress bar
        with tqdm(total=len(videos), desc="Processing videos") as pbar:
            for i, video in enumerate(videos):
                try:
                    # Update progress
                    self.video_db.update_import_job(job_id, progress=i + 1)
                    pbar.set_description(f"Processing: {video.title[:50]}...")
                    
                    # Check if already processed
                    if self.video_db.is_video_processed(video.id):
                        results['skipped_videos'] += 1
                        pbar.update(1)
                        continue
                    
                    # Add video to database
                    self.video_db.add_video(
                        video_id=video.id,
                        channel_id=video.channel_id,
                        title=video.title,
                        url=video.url,
                        description=video.description,
                        duration=video.duration_seconds,
                        published_at=video.published_at,
                        view_count=video.view_count,
                        metadata=video.to_dict()
                    )
                    
                    results['new_videos'] += 1
                    results['video_ids'].append(video.id)
                    
                    # Process transcript
                    try:
                        transcript = self.source_processor.get_youtube_transcript(video.url)
                        self.video_db.update_video_status(video.id, 'processed', transcript)
                        results['processed_videos'] += 1
                        
                        # Send to n8n if enabled
                        if send_to_n8n:
                            self._send_to_n8n(video, transcript, channel_info)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process transcript for {video.id}: {e}")
                        self.video_db.update_video_status(video.id, 'failed')
                        results['failed_videos'] += 1
                    
                    pbar.update(1)
                    
                    # Small delay to avoid overwhelming APIs
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to process video {video.id}: {e}")
                    results['failed_videos'] += 1
                    pbar.update(1)
        
        return results

    def _generate_dry_run_report(self, videos: List[YouTubeVideo], import_type: str, source: str) -> Dict[str, Any]:
        """Generate a dry run report without actually importing."""
        total_duration = sum(video.duration_seconds for video in videos)

        return {
            'dry_run': True,
            'import_type': import_type,
            'source': source,
            'total_videos': len(videos),
            'total_duration_seconds': total_duration,
            'total_duration_formatted': self._format_duration(total_duration),
            'videos_preview': [
                {
                    'id': video.id,
                    'title': video.title,
                    'duration': self._format_duration(video.duration_seconds),
                    'published_at': video.published_at,
                    'view_count': video.view_count
                }
                for video in videos[:10]  # Show first 10 videos
            ],
            'estimated_processing_time': f"{len(videos) * 2} seconds"  # Rough estimate
        }

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours}h {minutes}m {seconds}s"

    def _send_to_n8n(self, video: YouTubeVideo, transcript: str, channel_info):
        """Send video data to n8n workflow."""
        try:
            payload = {
                'video_id': video.id,
                'title': video.title,
                'description': video.description,
                'url': video.url,
                'channel_name': channel_info.title if channel_info else video.channel_title,
                'channel_id': video.channel_id,
                'duration': video.duration_seconds,
                'published_at': video.published_at,
                'view_count': video.view_count,
                'transcript': transcript,
                'metadata': video.to_dict()
            }

            response = self.n8n_client.send_video_data(payload)
            logger.info(f"Sent video {video.id} to n8n workflow")

        except Exception as e:
            logger.error(f"Failed to send video {video.id} to n8n: {e}")

    def resume_import_job(self, job_id: str) -> Dict[str, Any]:
        """Resume a failed or interrupted import job."""
        # Get job details
        jobs = self.video_db.get_import_jobs()
        job = next((j for j in jobs if j['id'] == job_id), None)

        if not job:
            raise ValueError(f"Import job not found: {job_id}")

        if job['status'] not in ['failed', 'running']:
            raise ValueError(f"Cannot resume job with status: {job['status']}")

        # Resume based on job type
        if job['type'] == 'channel':
            return self.import_from_channel(
                job['source'],
                limit=job['total'],
                filters=job.get('filters')
            )
        elif job['type'] == 'playlist':
            return self.import_from_playlist(
                job['source'],
                limit=job['total'],
                filters=job.get('filters')
            )
        elif job['type'] == 'file':
            return self.import_from_file(
                job['source'],
                filters=job.get('filters')
            )
        else:
            raise ValueError(f"Unknown job type: {job['type']}")

    def get_import_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get import job history."""
        return self.video_db.get_import_jobs(limit=limit)

    def cancel_import_job(self, job_id: str) -> bool:
        """Cancel a running import job."""
        return self.video_db.update_import_job(job_id, status='cancelled')


# Global bulk importer instance
_bulk_importer = None

def get_bulk_importer() -> BulkImporter:
    """Get or create the global bulk importer instance."""
    global _bulk_importer
    if _bulk_importer is None:
        _bulk_importer = BulkImporter()
    return _bulk_importer
