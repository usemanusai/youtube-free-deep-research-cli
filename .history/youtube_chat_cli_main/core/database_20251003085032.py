"""
JAEGIS NexusSync - Database Management

This module provides SQLite database management for application state,
processing queue, chat sessions, and metadata.
"""

import sqlite3
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
import queue
import threading

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

        # Pool + tuning
        self._pool_size = max(1, int(os.getenv('DB_POOL_SIZE', '5')))
        self._timeout_s = max(1, int(os.getenv('DB_TIMEOUT_S', '10')))
        self._pool: queue.Queue[sqlite3.Connection] = queue.Queue(maxsize=self._pool_size)
        self._pool_lock = threading.Lock()

        # Initialize pool
        for _ in range(self._pool_size):
            self._pool.put(self._create_connection())

        # Initialize database schema
        self._init_schema()

        logger.info(f"Database initialized at {self.db_path} (pool={self._pool_size})")



    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=self._timeout_s, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            c = conn.cursor()
            c.execute("PRAGMA journal_mode=WAL;")
            c.execute("PRAGMA synchronous=NORMAL;")
            c.execute("PRAGMA cache_size=-64000;")
            c.execute("PRAGMA foreign_keys=ON;")
            c.close()
        except Exception:
            pass
        return conn

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

            # Indexing jobs table for archive indexing status
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indexing_jobs (
                    id TEXT PRIMARY KEY,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    files_processed INTEGER DEFAULT 0,
                    files_failed INTEGER DEFAULT 0,
                    failed_files TEXT,
                    status TEXT DEFAULT 'in_progress'
                )
            """)

            # Workflow traces for observability/debugging
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    workflow_type TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_trace_workflow
                ON workflow_traces(workflow_id, created_at)
            """)

            # Dead letter queue for permanently failed jobs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dead_letter_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_table TEXT NOT NULL,
                    original_id TEXT,
                    reason TEXT,
                    payload TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Additional helpful indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_workflow
                ON chat_sessions(workflow_id, created_at)
            """)

            logger.info("Database schema initialized successfully")

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Sessions & Archive Queries
    # -------------------------------------------------------------------------

    def list_sessions(self, limit: int = 50, offset: int = 0, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            params = []
            where = ""
            if workflow_type:
                where = "WHERE workflow_id = ?"
                params.append(workflow_type)
            cursor.execute(f"""
                SELECT * FROM chat_sessions
                {where}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (*params, limit, offset))
            sessions = [dict(row) for row in cursor.fetchall()]
            # total count
            if workflow_type:
                cursor.execute("SELECT COUNT(*) as c FROM chat_sessions WHERE workflow_id = ?", (workflow_type,))
            else:
                cursor.execute("SELECT COUNT(*) as c FROM chat_sessions")
            total = cursor.fetchone()[0]
            return {"sessions": sessions, "total": total, "limit": limit, "offset": offset}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_vector_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vector_metadata")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM vector_metadata WHERE source_type = 'gdrive'")
            gdrive = cursor.fetchone()[0]
            cursor.execute("SELECT MAX(created_at) FROM vector_metadata WHERE source_type = 'gdrive'")
            last = cursor.fetchone()[0]
            return {"total_vectors": total, "gdrive_vectors": gdrive, "last_sync_time": last}

    def get_indexed_gdrive_file_ids(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT source_file_id FROM vector_metadata WHERE source_type='gdrive'")
            return [r[0] for r in cursor.fetchall() if r[0]]

    # -------------------------------------------------------------------------
    # Indexing Jobs
    # -------------------------------------------------------------------------

    def create_indexing_job(self, job_id: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO indexing_jobs (id, status) VALUES (?, 'in_progress')", (job_id,))

    def update_indexing_job(self, job_id: str, files_processed: int = 0, files_failed: int = 0, failed_files: Optional[List[str]] = None, status: Optional[str] = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if failed_files:
                import json as _json
                cursor.execute("UPDATE indexing_jobs SET files_processed = files_processed + ?, files_failed = files_failed + ?, failed_files = COALESCE(failed_files, '[]') WHERE id = ?", (files_processed, files_failed, job_id))
                # fetch current failed_files
                cursor.execute("SELECT failed_files FROM indexing_jobs WHERE id = ?", (job_id,))
                cur = cursor.fetchone()[0] or '[]'
                arr = []
                try:
                    arr = _json.loads(cur)
                except Exception:
                    arr = []
                arr.extend(failed_files)
                cursor.execute("UPDATE indexing_jobs SET failed_files = ? WHERE id = ?", (_json.dumps(arr), job_id))
            else:
                cursor.execute("UPDATE indexing_jobs SET files_processed = files_processed + ?, files_failed = files_failed + ? WHERE id = ?", (files_processed, files_failed, job_id))
            if status:
                if status in ("completed", "failed"):
                    cursor.execute("UPDATE indexing_jobs SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?", (status, job_id))
                else:
                    cursor.execute("UPDATE indexing_jobs SET status = ? WHERE id = ?", (status, job_id))

    def get_in_progress_indexing_job(self) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM indexing_jobs WHERE status='in_progress' ORDER BY started_at DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None

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

    def get_queue_item(self, queue_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific queue item by ID.

        Args:
            queue_id: Queue item ID

        Returns:
            Queue item as dictionary, or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM processing_queue
                WHERE id = ?
            """, (queue_id,))

            row = cursor.fetchone()
            if row:
                item = dict(row)
                # Parse JSON metadata
                if item.get('metadata'):
                    item['metadata'] = json.loads(item['metadata'])
                return item
            return None

    def get_pending_queue_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get pending items from the queue.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of queue items
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM processing_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            """, (limit,))

            items = []
            for row in cursor.fetchall():
                item = dict(row)
                # Parse JSON metadata
                if item.get('metadata'):
                    item['metadata'] = json.loads(item['metadata'])
                items.append(item)

            return items

    def increment_queue_retry(self, queue_id: int) -> None:
        """
        Increment the retry count for a queue item.

        Args:
            queue_id: Queue item ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE processing_queue
                SET retry_count = retry_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (queue_id,))

            logger.debug(f"Incremented retry count for queue item {queue_id}")

    def get_queue_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive queue statistics.

        Returns:
            Dictionary with detailed statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get counts by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM processing_queue
                GROUP BY status
            """)

            status_counts = {}
            for row in cursor.fetchall():
                status_counts[row['status']] = row['count']

            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM processing_queue")
    # -------------------------------------------------------------------------
    # Observability: Workflow traces & Dead letter queue
    # -------------------------------------------------------------------------

    def add_workflow_trace(self, workflow_id: str, workflow_type: str, stage: str, state: Dict[str, Any]) -> None:
        import json
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS workflow_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    workflow_type TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("""
                INSERT INTO workflow_traces (workflow_id, workflow_type, stage, state_json)
                VALUES (?, ?, ?, ?)
            """, (workflow_id, workflow_type, stage, json.dumps(state, ensure_ascii=False)))

    def get_workflow_traces(self, workflow_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT workflow_id, workflow_type, stage, state_json, created_at
                FROM workflow_traces WHERE workflow_id = ? ORDER BY created_at ASC
            """, (workflow_id,))
            rows = c.fetchall()
            out = []
            for r in rows:
                try:
                    import json
                    state = json.loads(r['state_json']) if r['state_json'] else {}
                except Exception:
                    state = {}
                out.append({
                    'workflow_id': r['workflow_id'],
                    'workflow_type': r['workflow_type'],
                    'stage': r['stage'],
                    'state': state,
                    'created_at': r['created_at'],
                })
            return out

    def add_dead_letter(self, source_table: str, original_id: str, reason: str, payload: Dict[str, Any] | None = None) -> None:
        import json
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS dead_letter_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_table TEXT NOT NULL,
                    original_id TEXT,
                    reason TEXT,
                    payload TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("""
                INSERT INTO dead_letter_queue (source_table, original_id, reason, payload)
                VALUES (?, ?, ?, ?)
            """, (source_table, original_id, reason, json.dumps(payload or {}, ensure_ascii=False)))

    def list_dead_letters(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM dead_letter_queue ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = [dict(r) for r in c.fetchall()]
            c.execute("SELECT COUNT(*) AS c FROM dead_letter_queue")
            total = (c.fetchone() or {}).get('c', 0)
            return {'items': rows, 'total': total, 'limit': limit, 'offset': offset}


    def get_queue_breakdown(self) -> Dict[str, Any]:
        """Breakdown of processing_queue by source, file_type, status, age, retry_count.
        Returns a dict with keys: total, by_status, by_source, by_file_type, by_age, by_retry_count
        """
        with self.get_connection() as conn:
            c = conn.cursor()
            # Base total
            c.execute("SELECT COUNT(*) as total FROM processing_queue")
            total = (c.fetchone() or {}).get('total', 0)
            # By status
            c.execute("SELECT status, COUNT(*) AS c FROM processing_queue GROUP BY status")
            by_status = {row['status']: row['c'] for row in c.fetchall()}
            # By source
            c.execute("SELECT COALESCE(source,'unknown') AS s, COUNT(*) AS c FROM processing_queue GROUP BY s")
            by_source = {row['s']: row['c'] for row in c.fetchall()}
            # By file type
            c.execute("SELECT COALESCE(file_type,'unknown') AS t, COUNT(*) AS c FROM processing_queue GROUP BY t")
            by_file_type = {row['t']: row['c'] for row in c.fetchall()}
            # Age buckets based on created_at
            def _age_bucket_sql():
                return (
                    "SELECT CASE "
                    " WHEN julianday('now') - julianday(created_at) < 1.0/24 THEN '<1h' "
                    " WHEN julianday('now') - julianday(created_at) < 1.0 THEN '1h-24h' "
                    " WHEN julianday('now') - julianday(created_at) < 7.0 THEN '1d-7d' "
                    " ELSE '>7d' END AS bucket, COUNT(*) AS c FROM processing_queue GROUP BY bucket"
                )
            c.execute(_age_bucket_sql())
            by_age = {row['bucket']: row['c'] for row in c.fetchall()}
            # Retry buckets
            c.execute("""
                SELECT CASE
                    WHEN retry_count <= 0 THEN '0'
                    WHEN retry_count BETWEEN 1 AND 2 THEN '1-2'
                    ELSE '3+'
                END AS bucket, COUNT(*) AS c
                FROM processing_queue
                GROUP BY bucket
            """)
            by_retry = {row['bucket']: row['c'] for row in c.fetchall()}
            return {
                'total': total,
                'by_status': by_status,
                'by_source': by_source,
                'by_file_type': by_file_type,
                'by_age': by_age,
                'by_retry_count': by_retry,
            }

    # -------------------------------------------------------------------------
    # Google Drive File Operations
    # -------------------------------------------------------------------------

    def upsert_gdrive_file(
        self,
        file_id: str,
        name: str,
        mime_type: str,
        folder_id: Optional[str] = None,
        modified_time: Optional[datetime] = None,
        size: Optional[int] = None,
        md5_checksum: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Insert or update a Google Drive file record.

        Args:
            file_id: Google Drive file ID
            name: File name
            mime_type: MIME type
            folder_id: Parent folder ID
            modified_time: Last modified timestamp
            size: File size in bytes
            md5_checksum: MD5 checksum
            metadata: Additional metadata
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO gdrive_files
                (id, name, mime_type, folder_id, modified_time, size, md5_checksum,
                 metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                file_id,
                name,
                mime_type,
                folder_id,
                modified_time,
                size,
                md5_checksum,
                json.dumps(metadata) if metadata else None
            ))

            logger.debug(f"Upserted Google Drive file: {name} ({file_id})")

    def get_gdrive_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a Google Drive file record.

        Args:
            file_id: Google Drive file ID

        Returns:
            File record as dictionary, or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM gdrive_files WHERE id = ?
            """, (file_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def list_gdrive_files(self) -> List[Dict[str, Any]]:
        """List all Google Drive files known to the DB."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gdrive_files ORDER BY modified_time DESC")
            return [dict(r) for r in cursor.fetchall()]

    def mark_gdrive_file_processed(self, file_id: str, status: str = 'completed') -> None:
        """
        Mark a Google Drive file as processed.

        Args:
            file_id: Google Drive file ID
            status: Processing status
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE gdrive_files
                SET last_processed = CURRENT_TIMESTAMP,
                    processing_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, file_id))

    def update_gdrive_file_status(self, file_id: str, status: str) -> None:
        """
        Update the processing status of a Google Drive file.

        Args:
            file_id: Google Drive file ID
            status: New processing status
        """
        self.mark_gdrive_file_processed(file_id, status)

    # -------------------------------------------------------------------------
    # Chat Session Operations
    # -------------------------------------------------------------------------

    def create_chat_session(
        self,
        session_id: str,
        name: Optional[str] = None,
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a new chat session.

        Args:
            session_id: Unique session ID
            name: Session name
            workflow_id: Associated workflow ID
            metadata: Additional metadata
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO chat_sessions
                (id, name, workflow_id, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session_id,
                name,
                workflow_id,
                json.dumps(metadata) if metadata else None
            ))

            logger.info(f"Created chat session: {session_id}")

    def add_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add a message to a chat session.

        Args:
            session_id: Session ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Additional metadata

        Returns:
            Message ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages
                (session_id, role, content, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                session_id,
                role,
                content,
                json.dumps(metadata) if metadata else None
            ))

            # Update session timestamp
            cursor.execute("""
                UPDATE chat_sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (session_id,))

            return cursor.lastrowid

    def get_chat_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a session.

        Args:
            session_id: Session ID
            limit: Maximum number of messages to return (most recent)

        Returns:
            List of message dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if limit:
                cursor.execute("""
                    SELECT * FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (session_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY created_at ASC
                """, (session_id,))

            messages = [dict(row) for row in cursor.fetchall()]

            # Reverse if limited (to get chronological order)
            if limit:
                messages.reverse()

            return messages

    # -------------------------------------------------------------------------
    # Workflow Operations
    # -------------------------------------------------------------------------

    def save_workflow(
        self,
        workflow_id: str,
        name: str,
        workflow_type: str,
        config: Dict[str, Any],
        enabled: bool = True
    ) -> None:
        """
        Save a workflow configuration.

        Args:
            workflow_id: Unique workflow ID
            name: Workflow name
            workflow_type: Workflow type
            config: Workflow configuration as dictionary
            enabled: Whether workflow is enabled
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO workflows
                (id, name, type, config, enabled, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                workflow_id,
                name,
                workflow_type,
                json.dumps(config),
                enabled
            ))

            logger.info(f"Saved workflow: {name} ({workflow_id})")

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow configuration.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow as dictionary, or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workflows WHERE id = ?
            """, (workflow_id,))

            row = cursor.fetchone()
            if row:
                workflow = dict(row)
                workflow['config'] = json.loads(workflow['config'])
                return workflow
            return None

    def list_workflows(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        List all workflows.

        Args:
            enabled_only: Only return enabled workflows

        Returns:
            List of workflow dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if enabled_only:
                cursor.execute("""
                    SELECT * FROM workflows WHERE enabled = 1
                    ORDER BY name
                """)
            else:
                cursor.execute("""
                    SELECT * FROM workflows ORDER BY name
                """)

            workflows = []
            for row in cursor.fetchall():
                workflow = dict(row)
                workflow['config'] = json.loads(workflow['config'])
                workflows.append(workflow)

            return workflows

    # -------------------------------------------------------------------------
    # Vector Metadata Operations
    # -------------------------------------------------------------------------

    def add_vector_metadata(
        self,
        vector_id: str,
        file_id: Optional[str] = None,
        chunk_index: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add metadata for a vector embedding.

        Args:
            vector_id: Vector ID in the vector store
            file_id: Source file ID
            chunk_index: Chunk index within the file
            metadata: Additional metadata
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vector_metadata
                (id, source_file_id, chunk_index, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                vector_id,
                file_id,
                chunk_index,
                json.dumps(metadata) if metadata else None
            ))

            logger.debug(f"Added vector metadata: {vector_id}")

    def delete_vector_metadata(self, vector_id: str) -> None:
        """
        Delete vector metadata.

        Args:
            vector_id: Vector ID to delete
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM vector_metadata
                WHERE id = ?
            """, (vector_id,))

            logger.debug(f"Deleted vector metadata: {vector_id}")

    def get_vector_metadata(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a vector.

        Args:
            vector_id: Vector ID

        Returns:
            Metadata dictionary or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM vector_metadata
                WHERE id = ?
            """, (vector_id,))

            row = cursor.fetchone()
            if row:
                metadata = dict(row)
                if metadata.get('metadata'):
                    metadata['metadata'] = json.loads(metadata['metadata'])
                return metadata
            return None


# Global database instance
_database: Optional[Database] = None


def get_database(db_path: Optional[str] = None, reload: bool = False) -> Database:
    """
    Get the global database instance.

    Args:
        db_path: Path to database file (only used on first call or if reload=True)
        reload: Force reload of database

    Returns:
        Database instance
    """
    global _database

    if _database is None or reload:
        _database = Database(db_path)
        logger.info("Database instance created")

    return _database

