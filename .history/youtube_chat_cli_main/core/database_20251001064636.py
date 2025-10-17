"""
JAEGIS NexusSync - Database Management

This module provides SQLite database management for application state,
processing queue, chat sessions, and metadata.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

from .config import get_config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass


class Database:
    """
    SQLite database manager for JAEGIS NexusSync.
    
    Manages:
    - Processing queue for document ingestion
    - Chat session history
    - Google Drive file metadata
    - Workflow configurations
    - Vector store metadata
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file (default: from config)
        """
        config = get_config()
        self.db_path = db_path or config.database_path
        
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            conn.close()
    
    def _init_schema(self) -> None:
        """Initialize database schema with all required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Processing queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """)
            
            # Create index on status for efficient queue queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_queue_status 
                ON processing_queue(status, priority DESC, created_at)
            """)
            
            # Google Drive files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gdrive_files (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mime_type TEXT,
                    folder_id TEXT,
                    modified_time TIMESTAMP,
                    size INTEGER,
                    md5_checksum TEXT,
                    last_processed TIMESTAMP,
                    processing_status TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chat sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    workflow_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                )
            """)
            
            # Create index on session_id for efficient message queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON chat_messages(session_id, created_at)
            """)
            
            # Workflow configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    config TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Vector store metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_metadata (
                    id TEXT PRIMARY KEY,
                    source_file_id TEXT,
                    source_type TEXT,
                    chunk_index INTEGER,
                    chunk_text TEXT,
                    embedding_model TEXT,
                    vector_store TEXT,
                    collection_name TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on source_file_id for efficient lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vector_source 
                ON vector_metadata(source_file_id, chunk_index)
            """)
            
            logger.info("Database schema initialized successfully")
    
    # -------------------------------------------------------------------------
    # Processing Queue Operations
    # -------------------------------------------------------------------------
    
    def add_to_queue(
        self,
        file_id: str,
        file_name: str,
        source: str,
        file_type: Optional[str] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add a file to the processing queue.
        
        Args:
            file_id: Unique file identifier
            file_name: File name
            source: Source of the file (e.g., 'google_drive', 'local', 'url')
            file_type: MIME type or file extension
            priority: Processing priority (higher = processed first)
            metadata: Additional metadata as dictionary
        
        Returns:
            Queue item ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_queue 
                (file_id, file_name, file_type, source, priority, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                file_name,
                file_type,
                source,
                priority,
                json.dumps(metadata) if metadata else None
            ))
            
            queue_id = cursor.lastrowid
            logger.info(f"Added file to queue: {file_name} (ID: {queue_id})")
            return queue_id
    
    def get_next_queue_item(self) -> Optional[Dict[str, Any]]:
        """
        Get the next item from the processing queue.
        
        Returns:
            Queue item as dictionary, or None if queue is empty
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processing_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_queue_status(
        self,
        queue_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update the status of a queue item.
        
        Args:
            queue_id: Queue item ID
            status: New status ('pending', 'processing', 'completed', 'failed')
            error_message: Error message if status is 'failed'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status == 'completed':
                cursor.execute("""
                    UPDATE processing_queue
                    SET status = ?, processed_at = CURRENT_TIMESTAMP, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, queue_id))
            elif status == 'failed':
                cursor.execute("""
                    UPDATE processing_queue
                    SET status = ?, error_message = ?, retry_count = retry_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, error_message, queue_id))
            else:
                cursor.execute("""
                    UPDATE processing_queue
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, queue_id))
            
            logger.debug(f"Updated queue item {queue_id} status to {status}")
    
    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get processing queue statistics.
        
        Returns:
            Dictionary with counts by status
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM processing_queue
                GROUP BY status
            """)
            
            stats = {row['status']: row['count'] for row in cursor.fetchall()}
            return stats

