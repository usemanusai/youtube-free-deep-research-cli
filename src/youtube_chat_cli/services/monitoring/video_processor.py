"""
Video processor with intelligent rate limiting and queue management.
"""

import logging
import time
from typing import Dict, Optional, Any
from datetime import datetime

from youtube_chat_cli.services.monitoring.video_queue import get_video_queue
from youtube_chat_cli.core.database import get_video_database
from youtube_chat_cli.services.transcription.processor import get_source_processor
from youtube_chat_cli.services.n8n.client import get_n8n_client

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes videos from the queue with intelligent rate limiting."""
    
    def __init__(self):
        """Initialize video processor."""
        self.video_queue = get_video_queue()
        self.video_db = get_video_database()
        self.source_processor = get_source_processor()
        self.n8n_client = get_n8n_client()
        
        logger.info("Video processor initialized")
    
    def process_next_video(self) -> Optional[Dict[str, Any]]:
        """Process the next video in the queue.
        
        Returns:
            Processing result or None if no video to process
        """
        # Get next video to process
        queue_entry = self.video_queue.get_next_video_to_process()
        if not queue_entry:
            return None
        
        queue_id = queue_entry['id']
        video_id = queue_entry['video_id']
        channel_id = queue_entry['channel_id']
        
        logger.info(f"Processing video {video_id} from queue (attempt {queue_entry['attempts'] + 1})")
        
        # Mark as processing
        if not self.video_queue.mark_processing_started(queue_id):
            logger.warning(f"Failed to mark video {video_id} as processing")
            return None
        
        try:
            # Get video details from database
            video = self.video_db.get_video(video_id)
            if not video:
                error_msg = f"Video {video_id} not found in database"
                logger.error(error_msg)
                self.video_queue.mark_processing_completed(queue_id, False, error_msg)
                return {'success': False, 'error': error_msg}
            
            # Process transcript with rate limiting awareness
            result = self._process_video_transcript(video, queue_id)
            
            if result['success']:
                # Send to n8n if configured
                n8n_result = self._send_to_n8n(video, result['transcript'])
                result['n8n_sent'] = n8n_result
                
                # Mark as completed
                self.video_queue.mark_processing_completed(queue_id, True)
                
                # Update video status in database
                self.video_db.update_video_status(video_id, 'processed', result['transcript'])
                
                logger.info(f"Successfully processed video {video_id}")
            else:
                # Handle failure
                if result.get('rate_limited'):
                    # Handle rate limiting
                    self.video_queue.handle_rate_limit_detected(queue_id, backoff_minutes=120)
                    logger.warning(f"Rate limit detected for video {video_id}, rescheduled")
                else:
                    # Mark as failed
                    self.video_queue.mark_processing_completed(queue_id, False, result['error'])
                    self.video_db.update_video_status(video_id, 'failed')
                    logger.error(f"Failed to process video {video_id}: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error processing video {video_id}: {e}"
            logger.error(error_msg)
            self.video_queue.mark_processing_completed(queue_id, False, error_msg)
            self.video_db.update_video_status(video_id, 'failed')
            return {'success': False, 'error': error_msg}
    
    def _process_video_transcript(self, video: Dict[str, Any], queue_id: str) -> Dict[str, Any]:
        """Process video transcript with rate limiting detection.
        
        Args:
            video: Video data from database
            queue_id: Queue entry ID
            
        Returns:
            Processing result
        """
        video_id = video['video_id']
        video_url = video['url']
        
        try:
            logger.info(f"Fetching transcript for video {video_id}")
            
            # Add small delay before processing to be respectful
            time.sleep(2)
            
            # Attempt to get transcript
            transcript = self.source_processor.get_youtube_transcript(video_url)
            
            if not transcript or len(transcript.strip()) < 100:
                return {
                    'success': False,
                    'error': 'Transcript too short or empty',
                    'rate_limited': False
                }
            
            logger.info(f"Successfully fetched transcript for {video_id} ({len(transcript)} characters)")
            
            return {
                'success': True,
                'transcript': transcript,
                'video_id': video_id
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detect rate limiting patterns
            rate_limit_indicators = [
                'ip has been blocked',
                'too many requests',
                'rate limit',
                'blocked by youtube',
                'cloud provider',
                'requests from your ip'
            ]
            
            is_rate_limited = any(indicator in error_msg for indicator in rate_limit_indicators)
            
            return {
                'success': False,
                'error': str(e),
                'rate_limited': is_rate_limited,
                'video_id': video_id
            }
    
    def _send_to_n8n(self, video: Dict[str, Any], transcript: str) -> bool:
        """Send video data to n8n workflow with retry logic.
        
        Args:
            video: Video data
            transcript: Video transcript
            
        Returns:
            True if sent successfully
        """
        try:
            # Prepare payload
            payload = {
                'video_id': video['video_id'],
                'title': video['title'],
                'description': video['description'],
                'url': video['url'],
                'channel_id': video['channel_id'],
                'duration': video['duration'],
                'published_at': video['published_at'],
                'view_count': video['view_count'],
                'transcript': transcript,
                'metadata': video.get('metadata', {}),
                'processed_at': datetime.now().isoformat()
            }
            
            # Send to n8n with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.n8n_client.send_video_data(payload)
                    logger.info(f"Successfully sent video {video['video_id']} to n8n workflow")
                    return True
                    
                except Exception as e:
                    logger.warning(f"n8n send attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logger.error(f"Failed to send video {video['video_id']} to n8n after {max_retries} attempts")
                        return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error preparing n8n payload for video {video['video_id']}: {e}")
            return False
    
    def process_available_videos(self, max_videos: int = 1) -> Dict[str, Any]:
        """Process multiple videos from the queue.
        
        Args:
            max_videos: Maximum number of videos to process
            
        Returns:
            Processing summary
        """
        results = {
            'processed': 0,
            'failed': 0,
            'rate_limited': 0,
            'no_videos': False
        }
        
        for i in range(max_videos):
            result = self.process_next_video()
            
            if not result:
                results['no_videos'] = True
                break
            
            if result['success']:
                results['processed'] += 1
            else:
                results['failed'] += 1
                if result.get('rate_limited'):
                    results['rate_limited'] += 1
                    # Stop processing if rate limited
                    break
        
        return results
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        queue_stats = self.video_queue.get_queue_stats()
        
        return {
            'queue_stats': queue_stats,
            'processor_ready': True,
            'next_video_ready': self.video_queue.get_next_video_to_process() is not None
        }


# Global video processor instance
_video_processor = None

def get_video_processor() -> VideoProcessor:
    """Get or create the global video processor instance."""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor
