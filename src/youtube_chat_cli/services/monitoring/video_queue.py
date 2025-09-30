"""
Video processing queue system with intelligent rate limiting.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import uuid

logger = logging.getLogger(__name__)


class VideoProcessingQueue:
    """Manages video processing queue with rate limiting to avoid IP blocking."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize video processing queue.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            user_data_dir = Path.home() / ".youtube-chat-cli"
            user_data_dir.mkdir(exist_ok=True)
            db_path = user_data_dir / "videos.db"
        
        self.db_path = str(db_path)
        self._init_queue_tables()
        
        # Rate limiting configuration
        self.max_videos_per_day = 5
        self.min_delay_between_videos = 3600  # 1 hour in seconds
        self.max_delay_between_videos = 7200  # 2 hours in seconds
        self.exponential_backoff_base = 2
        self.max_retries = 3
        
        logger.info("Video processing queue initialized with rate limiting")
    
    def _init_queue_tables(self):
        """Initialize queue-related database tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Processing queue table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_queue (
                    id TEXT PRIMARY KEY,
                    video_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    scheduled_at TIMESTAMP,
                    attempts INTEGER DEFAULT 0,
                    last_attempt TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """)
            
            # Rate limiting tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limit_tracking (
                    date TEXT PRIMARY KEY,
                    videos_processed INTEGER DEFAULT 0,
                    last_processing_time TIMESTAMP,
                    backoff_until TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON processing_queue (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_scheduled ON processing_queue (scheduled_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_priority ON processing_queue (priority DESC)")
            
            conn.commit()
    
    def add_to_queue(self, video_id: str, channel_id: str, priority: int = 0) -> str:
        """Add a video to the processing queue.
        
        Args:
            video_id: YouTube video ID
            channel_id: YouTube channel ID
            priority: Processing priority (higher = processed first)
            
        Returns:
            Queue entry ID
        """
        queue_id = str(uuid.uuid4())
        
        # Calculate when this video should be processed
        scheduled_at = self._calculate_next_processing_time()
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if video is already in queue
            cursor = conn.execute(
                "SELECT id FROM processing_queue WHERE video_id = ? AND status IN ('pending', 'processing')",
                (video_id,)
            )
            
            if cursor.fetchone():
                logger.info(f"Video {video_id} already in processing queue")
                return None
            
            # Add to queue
            conn.execute("""
                INSERT INTO processing_queue 
                (id, video_id, channel_id, priority, scheduled_at)
                VALUES (?, ?, ?, ?, ?)
            """, (queue_id, video_id, channel_id, priority, scheduled_at.isoformat()))
            
            conn.commit()
        
        logger.info(f"Added video {video_id} to processing queue, scheduled for {scheduled_at}")
        return queue_id
    
    def _calculate_next_processing_time(self) -> datetime:
        """Calculate when the next video should be processed based on rate limits."""
        now = datetime.now()
        today = now.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get today's processing stats
            cursor = conn.execute(
                "SELECT videos_processed, last_processing_time, backoff_until FROM rate_limit_tracking WHERE date = ?",
                (today,)
            )
            row = cursor.fetchone()
            
            if not row:
                # First video of the day
                return now + timedelta(seconds=self.min_delay_between_videos)
            
            videos_processed, last_processing_str, backoff_until_str = row
            
            # Check if we're in backoff period
            if backoff_until_str:
                backoff_until = datetime.fromisoformat(backoff_until_str)
                if now < backoff_until:
                    logger.info(f"In backoff period until {backoff_until}")
                    return backoff_until + timedelta(seconds=self.min_delay_between_videos)
            
            # Check daily limit
            if videos_processed >= self.max_videos_per_day:
                # Schedule for tomorrow
                tomorrow = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
                logger.info(f"Daily limit reached, scheduling for tomorrow: {tomorrow}")
                return tomorrow
            
            # Calculate next processing time based on last processing
            if last_processing_str:
                last_processing = datetime.fromisoformat(last_processing_str)
                min_next_time = last_processing + timedelta(seconds=self.min_delay_between_videos)
                
                if now < min_next_time:
                    return min_next_time
            
            # Distribute remaining videos throughout the day
            remaining_videos = self.max_videos_per_day - videos_processed
            remaining_hours = 24 - now.hour
            
            if remaining_hours > 0 and remaining_videos > 0:
                hours_between_videos = max(1, remaining_hours // remaining_videos)
                next_time = now + timedelta(hours=hours_between_videos)
            else:
                next_time = now + timedelta(seconds=self.min_delay_between_videos)
            
            return next_time
    
    def get_next_video_to_process(self) -> Optional[Dict[str, Any]]:
        """Get the next video that should be processed."""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM processing_queue 
                WHERE status = 'pending' 
                AND scheduled_at <= ? 
                AND attempts < ?
                ORDER BY priority DESC, scheduled_at ASC 
                LIMIT 1
            """, (now.isoformat(), self.max_retries))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            return None
    
    def mark_processing_started(self, queue_id: str) -> bool:
        """Mark a video as currently being processed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE processing_queue 
                SET status = 'processing', last_attempt = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'pending'
            """, (queue_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def mark_processing_completed(self, queue_id: str, success: bool, error_message: Optional[str] = None):
        """Mark a video processing as completed."""
        status = 'completed' if success else 'failed'
        
        with sqlite3.connect(self.db_path) as conn:
            # Update queue entry
            conn.execute("""
                UPDATE processing_queue 
                SET status = ?, processed_at = CURRENT_TIMESTAMP, error_message = ?
                WHERE id = ?
            """, (status, error_message, queue_id))
            
            if success:
                # Update rate limiting tracking
                today = datetime.now().date().isoformat()
                conn.execute("""
                    INSERT OR REPLACE INTO rate_limit_tracking 
                    (date, videos_processed, last_processing_time)
                    VALUES (?, 
                        COALESCE((SELECT videos_processed FROM rate_limit_tracking WHERE date = ?), 0) + 1,
                        CURRENT_TIMESTAMP)
                """, (today, today))
            
            conn.commit()
        
        logger.info(f"Marked queue entry {queue_id} as {status}")
    
    def handle_rate_limit_detected(self, queue_id: str, backoff_minutes: int = 60):
        """Handle when rate limiting is detected."""
        backoff_until = datetime.now() + timedelta(minutes=backoff_minutes)
        today = datetime.now().date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Update rate limiting tracking
            conn.execute("""
                INSERT OR REPLACE INTO rate_limit_tracking 
                (date, videos_processed, last_processing_time, backoff_until)
                VALUES (?, 
                    COALESCE((SELECT videos_processed FROM rate_limit_tracking WHERE date = ?), 0),
                    CURRENT_TIMESTAMP,
                    ?)
            """, (today, today, backoff_until.isoformat()))
            
            # Reschedule the failed video
            new_scheduled_time = backoff_until + timedelta(seconds=self.min_delay_between_videos)
            conn.execute("""
                UPDATE processing_queue 
                SET status = 'pending', 
                    scheduled_at = ?,
                    attempts = attempts + 1,
                    error_message = 'Rate limit detected, rescheduled'
                WHERE id = ?
            """, (new_scheduled_time.isoformat(), queue_id))
            
            conn.commit()
        
        logger.warning(f"Rate limit detected, backing off until {backoff_until}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Queue stats
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM processing_queue 
                GROUP BY status
            """)
            queue_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Today's processing stats
            today = datetime.now().date().isoformat()
            cursor = conn.execute("""
                SELECT videos_processed, last_processing_time, backoff_until 
                FROM rate_limit_tracking 
                WHERE date = ?
            """, (today,))
            
            row = cursor.fetchone()
            if row:
                videos_today, last_processing, backoff_until = row
            else:
                videos_today, last_processing, backoff_until = 0, None, None
            
            # Next scheduled video
            cursor = conn.execute("""
                SELECT MIN(scheduled_at) 
                FROM processing_queue 
                WHERE status = 'pending'
            """)
            next_scheduled = cursor.fetchone()[0]
            
            return {
                'queue_stats': queue_stats,
                'videos_processed_today': videos_today,
                'daily_limit': self.max_videos_per_day,
                'last_processing_time': last_processing,
                'backoff_until': backoff_until,
                'next_scheduled_video': next_scheduled
            }
    
    def cleanup_old_entries(self, days: int = 7) -> int:
        """Clean up old completed/failed queue entries."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM processing_queue 
                WHERE status IN ('completed', 'failed') 
                AND processed_at < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count


# Global video queue instance
_video_queue = None

def get_video_queue() -> VideoProcessingQueue:
    """Get or create the global video queue instance."""
    global _video_queue
    if _video_queue is None:
        _video_queue = VideoProcessingQueue()
    return _video_queue
