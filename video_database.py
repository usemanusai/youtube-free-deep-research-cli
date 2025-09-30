"""
Video database module for tracking processed videos and channels.
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VideoDatabase:
    """SQLite database for tracking channels, videos, and import jobs."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize video database.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use user data directory
            user_data_dir = Path.home() / ".youtube-chat-cli"
            user_data_dir.mkdir(exist_ok=True)
            db_path = user_data_dir / "videos.db"
        
        self.db_path = str(db_path)
        self._init_database()
        logger.info(f"Video database initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    channel_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    check_interval INTEGER DEFAULT 24,
                    filters TEXT,
                    last_check TIMESTAMP,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    video_id TEXT NOT NULL UNIQUE,
                    channel_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT NOT NULL,
                    duration INTEGER,
                    published_at TIMESTAMP,
                    view_count INTEGER,
                    processed_at TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    metadata TEXT,
                    transcript TEXT,
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS import_jobs (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    total INTEGER DEFAULT 0,
                    filters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_channel_id ON videos (channel_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_published_at ON videos (published_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_channels_active ON channels (active)")
            
            conn.commit()
    
    def add_channel(self, url: str, channel_id: str, name: str, description: str = "",
                   check_interval: int = 24, filters: Optional[Dict] = None) -> str:
        """Add a new channel for monitoring."""
        channel_uuid = str(uuid.uuid4())
        filters_json = json.dumps(filters) if filters else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO channels (id, url, channel_id, name, description, check_interval, filters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (channel_uuid, url, channel_id, name, description, check_interval, filters_json))
            conn.commit()
        
        logger.info(f"Added channel: {name} ({channel_id})")
        return channel_uuid
    
    def get_channels(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all monitored channels."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM channels"
            if active_only:
                query += " WHERE active = 1"
            query += " ORDER BY name"
            
            cursor = conn.execute(query)
            channels = []
            
            for row in cursor.fetchall():
                channel = dict(row)
                if channel['filters']:
                    channel['filters'] = json.loads(channel['filters'])
                channels.append(channel)
            
            return channels
    
    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific channel by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("SELECT * FROM channels WHERE id = ? OR channel_id = ?", 
                                (channel_id, channel_id))
            row = cursor.fetchone()
            
            if row:
                channel = dict(row)
                if channel['filters']:
                    channel['filters'] = json.loads(channel['filters'])
                return channel
            
            return None
    
    def update_channel(self, channel_id: str, **kwargs) -> bool:
        """Update channel settings."""
        if not kwargs:
            return False
        
        # Handle filters serialization
        if 'filters' in kwargs and kwargs['filters'] is not None:
            kwargs['filters'] = json.dumps(kwargs['filters'])
        
        # Build update query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['check_interval', 'filters', 'active', 'last_check']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(channel_id)
        
        query = f"UPDATE channels SET {', '.join(set_clauses)} WHERE id = ? OR channel_id = ?"
        values.append(channel_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def remove_channel(self, channel_id: str) -> bool:
        """Remove a channel from monitoring."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM channels WHERE id = ? OR channel_id = ?", 
                                (channel_id, channel_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_video(self, video_id: str, channel_id: str, title: str, url: str,
                 description: str = "", duration: int = 0, published_at: Optional[str] = None,
                 view_count: int = 0, metadata: Optional[Dict] = None) -> str:
        """Add a video to the database."""
        video_uuid = str(uuid.uuid4())
        metadata_json = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO videos 
                (id, video_id, channel_id, title, description, url, duration, 
                 published_at, view_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (video_uuid, video_id, channel_id, title, description, url, 
                  duration, published_at, view_count, metadata_json))
            conn.commit()
        
        return video_uuid
    
    def get_videos(self, channel_id: Optional[str] = None, status: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """Get videos with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM videos"
            conditions = []
            params = []
            
            if channel_id:
                conditions.append("channel_id = ?")
                params.append(channel_id)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY published_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            videos = []
            
            for row in cursor.fetchall():
                video = dict(row)
                if video['metadata']:
                    video['metadata'] = json.loads(video['metadata'])
                videos.append(video)
            
            return videos

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video details by video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Video data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.execute("""
                SELECT * FROM videos WHERE video_id = ?
            """, (video_id,))

            row = cursor.fetchone()
            if row:
                video_data = dict(row)
                # Parse metadata if it exists
                if video_data['metadata']:
                    try:
                        video_data['metadata'] = json.loads(video_data['metadata'])
                    except (json.JSONDecodeError, TypeError):
                        video_data['metadata'] = {}
                return video_data

            return None

    def is_video_processed(self, video_id: str) -> bool:
        """Check if a video has already been processed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT status FROM videos WHERE video_id = ?", (video_id,))
            row = cursor.fetchone()
            return row is not None and row[0] in ['processed', 'skipped']
    
    def update_video_status(self, video_id: str, status: str, transcript: Optional[str] = None) -> bool:
        """Update video processing status."""
        with sqlite3.connect(self.db_path) as conn:
            if transcript:
                cursor = conn.execute("""
                    UPDATE videos SET status = ?, transcript = ?, processed_at = CURRENT_TIMESTAMP 
                    WHERE video_id = ?
                """, (status, transcript, video_id))
            else:
                cursor = conn.execute("""
                    UPDATE videos SET status = ?, processed_at = CURRENT_TIMESTAMP 
                    WHERE video_id = ?
                """, (status, video_id))
            conn.commit()
            return cursor.rowcount > 0

    def create_import_job(self, job_type: str, source: str, total: int = 0,
                         filters: Optional[Dict] = None) -> str:
        """Create a new import job."""
        job_id = str(uuid.uuid4())
        filters_json = json.dumps(filters) if filters else None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO import_jobs (id, type, source, total, filters)
                VALUES (?, ?, ?, ?, ?)
            """, (job_id, job_type, source, total, filters_json))
            conn.commit()

        return job_id

    def update_import_job(self, job_id: str, status: Optional[str] = None,
                         progress: Optional[int] = None, error_message: Optional[str] = None) -> bool:
        """Update import job progress."""
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)

            if status in ['completed', 'failed', 'cancelled']:
                updates.append("completed_at = CURRENT_TIMESTAMP")

        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)

        if error_message:
            updates.append("error_message = ?")
            params.append(error_message)

        if not updates:
            return False

        params.append(job_id)
        query = f"UPDATE import_jobs SET {', '.join(updates)} WHERE id = ?"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    def get_import_jobs(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get import jobs with optional status filter."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = "SELECT * FROM import_jobs"
            params = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            jobs = []

            for row in cursor.fetchall():
                job = dict(row)
                if job['filters']:
                    job['filters'] = json.loads(job['filters'])
                jobs.append(job)

            return jobs

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Channel stats
            cursor = conn.execute("SELECT COUNT(*) FROM channels WHERE active = 1")
            active_channels = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM channels")
            total_channels = cursor.fetchone()[0]

            # Video stats
            cursor = conn.execute("SELECT COUNT(*) FROM videos")
            total_videos = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM videos WHERE status = 'processed'")
            processed_videos = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM videos WHERE status = 'pending'")
            pending_videos = cursor.fetchone()[0]

            # Recent activity
            cursor = conn.execute("""
                SELECT COUNT(*) FROM videos
                WHERE processed_at > datetime('now', '-24 hours')
            """)
            videos_last_24h = cursor.fetchone()[0]

            # Import job stats
            cursor = conn.execute("SELECT COUNT(*) FROM import_jobs WHERE status = 'running'")
            running_jobs = cursor.fetchone()[0]

            return {
                'channels': {
                    'active': active_channels,
                    'total': total_channels
                },
                'videos': {
                    'total': total_videos,
                    'processed': processed_videos,
                    'pending': pending_videos,
                    'last_24h': videos_last_24h
                },
                'import_jobs': {
                    'running': running_jobs
                }
            }

    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old processed videos and completed jobs."""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            # Clean up old completed import jobs
            cursor = conn.execute("""
                DELETE FROM import_jobs
                WHERE status IN ('completed', 'failed', 'cancelled')
                AND completed_at < ?
            """, (cutoff_date.isoformat(),))

            deleted_jobs = cursor.rowcount
            conn.commit()

            return deleted_jobs


# Global database instance
_video_db = None

def get_video_database() -> VideoDatabase:
    """Get or create the global video database instance."""
    global _video_db
    if _video_db is None:
        _video_db = VideoDatabase()
    return _video_db
