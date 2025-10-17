"""
JAEGIS NexusSync - Background Service

This module provides automated background processing including:
- Google Drive folder monitoring
- Processing queue management
- Scheduled document ingestion
- Automatic retry logic

Uses APScheduler for reliable background task execution.
"""

import logging
from datetime import datetime
from typing import Optional
import signal
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from ..core.config import get_config
from ..core.database import get_database
from .gdrive_service import get_gdrive_watcher
from .content_processor import get_content_processor

logger = logging.getLogger(__name__)


class BackgroundService:
    """
    Background service for automated document processing.

    Features:
    - Google Drive folder monitoring
    - Processing queue management
    - Automatic retry for failed items
    - Graceful shutdown handling
    """

    def __init__(self):
        """Initialize background service."""
        self.config = get_config()
        self.db = get_database()
        self.scheduler = BackgroundScheduler()
        self.is_running = False

        # Get service instances
        self.gdrive_watcher = get_gdrive_watcher()
        self.content_processor = get_content_processor()

        # Configure scheduler event listeners
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._job_error_listener,
            EVENT_JOB_ERROR
        )

        # Register signal handlers for graceful shutdown (only in main thread)
        try:
            import threading
            if threading.current_thread() is threading.main_thread():
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            else:
                logger.debug("Skipping signal handler registration (not main thread)")
        except Exception as e:
            logger.debug("Skipping signal handler registration: %s", e)

    def start(self) -> None:
        """
        Start the background service.

        This starts all scheduled jobs:
        - Google Drive monitoring
        - Queue processing
        """
        if self.is_running:
            logger.warning("Background service is already running")
            return

        logger.info("Starting JAEGIS NexusSync background service...")

        # Add Google Drive monitoring job
        if self.config.google_drive_folder_id:
            self.scheduler.add_job(
                func=self._watch_google_drive,
                trigger=IntervalTrigger(
                    seconds=self.config.google_drive_poll_interval
                ),
                id='gdrive_watcher',
                name='Google Drive Watcher',
                replace_existing=True
            )
            logger.info(
                f"✅ Google Drive watcher scheduled "
                f"(interval: {self.config.google_drive_poll_interval}s)"
            )
        else:
            logger.warning("Google Drive folder ID not configured, skipping watcher")

        # Add queue processing job
        self.scheduler.add_job(
            func=self._process_queue,
            trigger=IntervalTrigger(
                seconds=self.config.background_service_interval
            ),
            id='queue_processor',
            name='Queue Processor',
            replace_existing=True
        )
        logger.info(
            f"✅ Queue processor scheduled "
            f"(interval: {self.config.background_service_interval}s)"
        )

        # Start the scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("🚀 Background service started successfully")
        logger.info("Press Ctrl+C to stop")

    def stop(self) -> None:
        """Stop the background service gracefully."""
        if not self.is_running:
            logger.warning("Background service is not running")
            return

        logger.info("Stopping background service...")

        # Shutdown scheduler
        self.scheduler.shutdown(wait=True)
        self.is_running = False

        logger.info("✅ Background service stopped")

    def _watch_google_drive(self) -> None:
        """
        Watch Google Drive for changes.

        This job runs periodically to check for new or modified files.
        """
        try:
            logger.debug("Running Google Drive watcher...")
            count = self.gdrive_watcher.watch()

            if count > 0:
                logger.info(f"Google Drive watcher added {count} files to queue")

        except Exception as e:
            logger.error(f"Google Drive watcher failed: {e}")

    def _process_queue(self) -> None:
        """
        Process items from the queue.

        This job runs periodically to process pending items.
        """
        try:
            logger.debug("Running queue processor...")

            # Get pending items from queue
            pending_items = self.db.get_pending_queue_items(limit=10)

            if not pending_items:
                logger.debug("No pending items in queue")
                return

            logger.info(f"Processing {len(pending_items)} queue items...")

            success_count = 0
            fail_count = 0

            for item in pending_items:
                queue_id = item['id']

                try:
                    # Process the item
                    success = self.content_processor.process_queue_item(queue_id)

                    if success:
                        success_count += 1
                    else:
                        fail_count += 1

                except Exception as e:
                    logger.error(f"Failed to process queue item {queue_id}: {e}")
                    fail_count += 1

            logger.info(
                f"Queue processing complete: "
                f"{success_count} succeeded, {fail_count} failed"
            )

        except Exception as e:
            logger.error(f"Queue processor failed: {e}")

    def _job_executed_listener(self, event) -> None:
        """
        Listener for successful job execution.

        Args:
            event: Job execution event
        """
        logger.debug(f"Job '{event.job_id}' executed successfully")

    def _job_error_listener(self, event) -> None:
        """
        Listener for job execution errors.

        Args:
            event: Job error event
        """
        logger.error(
            f"Job '{event.job_id}' failed with exception: {event.exception}"
        )

    def _signal_handler(self, signum, frame) -> None:
        """
        Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def get_status(self) -> dict:
        """
        Get the current status of the background service.

        Returns:
            Dictionary with service status information
        """
        jobs = []

        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                })

        # Get queue statistics
        queue_stats = self.db.get_queue_statistics()

        return {
            'is_running': self.is_running,
            'jobs': jobs,
            'queue_statistics': queue_stats
        }

    def run_once(self) -> dict:
        """
        Run all background tasks once (for testing/manual execution).

        Returns:
            Dictionary with execution results
        """
        logger.info("Running background tasks once...")

        results = {
            'gdrive_watcher': 0,
            'queue_processor': 0
        }

        # Run Google Drive watcher
        if self.config.google_drive_folder_id:
            try:
                count = self.gdrive_watcher.watch()
                results['gdrive_watcher'] = count
                logger.info(f"Google Drive watcher: {count} files added")
            except Exception as e:
                logger.error(f"Google Drive watcher failed: {e}")

        # Run queue processor
        try:
            pending_items = self.db.get_pending_queue_items(limit=10)

            for item in pending_items:
                try:
                    success = self.content_processor.process_queue_item(item['id'])
                    if success:
                        results['queue_processor'] += 1
                except Exception as e:
                    logger.error(f"Failed to process item {item['id']}: {e}")

            logger.info(f"Queue processor: {results['queue_processor']} items processed")

        except Exception as e:
            logger.error(f"Queue processor failed: {e}")

        return results
    # ---------------------------------------------------------------------
    # Archive Indexer (GDrive) helpers
    # ---------------------------------------------------------------------
    def start_reindex_job(self, force: bool = False) -> str:
        """Create an indexing job and run background processing once in a thread.
        Returns the job_id immediately.
        """
        import uuid, threading
        job_id = str(uuid.uuid4())
        self.db.create_indexing_job(job_id)

        # Invalidate caches related to search/vector before reindex starts
        try:
            from ..core.redis_cache import get_cache
            c = get_cache()
            c.clear_prefix("vector:")
            c.clear_prefix("search:")
        except Exception:
            pass

        def _runner():
            try:
                # Enqueue missing or all files
                try:
                    indexed_ids = set(self.db.get_indexed_gdrive_file_ids())
                    files = self.db.list_gdrive_files()
                    batch_size = self.config.gdrive_indexing_batch_size
                    to_enqueue = []
                    for f in files:
                        fid = f.get('id')
                        if force or (fid and fid not in indexed_ids):
                            to_enqueue.append(f)
                    # batches
                    total = len(to_enqueue)
                    processed = 0
                    for i in range(0, total, batch_size):
                        batch = to_enqueue[i:i+batch_size]
                        for f in batch:
                            try:
                                self.db.add_to_queue(
                                    file_id=f.get('id',''),
                                    file_name=f.get('name','unknown'),
                                    source='gdrive',
                                    file_type=f.get('mime_type'),
                                    metadata={'reindex_job_id': job_id}
                                )
                                processed += 1
                            except Exception as fe:
                                self.db.update_indexing_job(job_id, files_failed=1, failed_files=[f.get('id','')])
                        self.db.update_indexing_job(job_id, files_processed=processed, status='in_progress')
                except Exception as e:
                    logger.error("Indexer enqueue failed: %s", e)
                # Kick a single run of processors
                self.run_once()
                self.db.update_indexing_job(job_id, status='completed')
            except Exception as e:
                logger.error("Indexer job failed: %s", e)
                self.db.update_indexing_job(job_id, status='failed')
        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        return job_id

    def get_indexing_status(self) -> dict:
        """Return current indexing status using DB counters and jobs."""
        stats = self.db.get_vector_stats()
        job = self.db.get_in_progress_indexing_job()
        status = job.get('status') if job else 'idle'
        return {
            **stats,
            'indexing_status': status,
            'files_indexed': stats.get('gdrive_vectors', 0),
            'files_pending': None  # unknown without full queue introspection
        }



# Global service instance
_background_service: Optional[BackgroundService] = None


def get_background_service() -> BackgroundService:
    """
    Get the global background service instance.

    Returns:
        BackgroundService instance
    """
    global _background_service

    if _background_service is None:
        _background_service = BackgroundService()
        logger.info("Background service instance created")

    return _background_service

