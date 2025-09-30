"""
Background service for automated YouTube channel monitoring and video processing.
"""

import os
import json
import logging
import signal
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import threading
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from youtube_chat_cli.services.monitoring.channel_monitor import get_channel_monitor
from youtube_chat_cli.services.monitoring.video_processor import get_video_processor
from youtube_chat_cli.services.monitoring.video_queue import get_video_queue

logger = logging.getLogger(__name__)


# Standalone job functions to avoid serialization issues
def scan_channels_job():
    """Scheduled job to scan channels for new videos."""
    try:
        logger.info("Starting scheduled channel scan")

        channel_monitor = get_channel_monitor()
        results = channel_monitor.scan_all_channels()

        logger.info(f"Channel scan completed: {results['successful_scans']} successful, "
                   f"{results['failed_scans']} failed, {results['total_new_videos']} new videos")

        # Log individual channel results
        for result in results['channel_results']:
            if result['status'] == 'success':
                logger.info(f"Channel {result['channel_name']}: {result['new_videos']} new videos")
            else:
                logger.error(f"Channel {result['channel_name']} failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Error in channel scan job: {e}")


def process_videos_job():
    """Scheduled job to process videos from the queue."""
    try:
        logger.info("Starting scheduled video processing")

        # Process up to 1 video per run to respect rate limits
        video_processor = get_video_processor()
        results = video_processor.process_available_videos(max_videos=1)

        if results['no_videos']:
            logger.info("No videos ready for processing")
        else:
            logger.info(f"Video processing completed: {results['processed']} processed, "
                       f"{results['failed']} failed, {results['rate_limited']} rate limited")

        # Log queue status
        video_queue = get_video_queue()
        queue_stats = video_queue.get_queue_stats()
        pending_count = queue_stats['queue_stats'].get('pending', 0)
        logger.info(f"Queue status: {pending_count} videos pending")

    except Exception as e:
        logger.error(f"Error in video processing job: {e}")


def cleanup_job():
    """Scheduled job to clean up old data."""
    try:
        logger.info("Starting scheduled cleanup")

        # Clean up old queue entries
        video_queue = get_video_queue()
        deleted_count = video_queue.cleanup_old_entries(days=7)
        logger.info(f"Cleaned up {deleted_count} old queue entries")

    except Exception as e:
        logger.error(f"Error in cleanup job: {e}")


def health_check_job():
    """Scheduled job for health checks."""
    try:
        # Check if service is still responsive
        video_queue = get_video_queue()
        queue_stats = video_queue.get_queue_stats()

        # Log basic health info
        pending_videos = queue_stats['queue_stats'].get('pending', 0)
        videos_today = queue_stats['videos_processed_today']

        logger.info(f"Health check: {pending_videos} pending videos, "
                   f"{videos_today} processed today")

        # Check for stuck processing
        processing_count = queue_stats['queue_stats'].get('processing', 0)
        if processing_count > 0:
            logger.warning(f"Found {processing_count} videos stuck in processing state")

    except Exception as e:
        logger.error(f"Error in health check job: {e}")


class YouTubeMonitoringService:
    """Background service for automated YouTube channel monitoring."""
    
    def __init__(self):
        """Initialize the background service."""
        self.user_data_dir = Path.home() / ".youtube-chat-cli"
        self.user_data_dir.mkdir(exist_ok=True)
        
        self.pid_file = self.user_data_dir / "service.pid"
        self.log_file = self.user_data_dir / "service.log"
        self.config_file = self.user_data_dir / "service_config.json"
        
        # Don't store references to avoid serialization issues
        # self.channel_monitor = get_channel_monitor()
        # self.video_processor = get_video_processor()
        # self.video_queue = get_video_queue()
        
        self.scheduler = None
        self.running = False
        
        # Setup logging
        self._setup_service_logging()
        
        logger.info("YouTube monitoring service initialized")
    
    def _setup_service_logging(self):
        """Setup logging for the service."""
        # Create file handler for service logs
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.INFO)
    
    def _setup_scheduler(self):
        """Setup the APScheduler."""
        # Job store configuration
        jobstore_url = f"sqlite:///{self.user_data_dir}/scheduler.db"
        jobstores = {
            'default': SQLAlchemyJobStore(url=jobstore_url)
        }
        
        # Executor configuration
        executors = {
            'default': ThreadPoolExecutor(max_workers=2)
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add jobs
        self._add_scheduled_jobs()
    
    def _add_scheduled_jobs(self):
        """Add scheduled jobs to the scheduler."""
        # Channel scanning job - daily at 8 AM
        self.scheduler.add_job(
            func=scan_channels_job,
            trigger=CronTrigger(hour=8, minute=0),
            id='scan_channels',
            name='Scan YouTube channels for new videos',
            replace_existing=True
        )

        # Video processing job - every 2 hours
        self.scheduler.add_job(
            func=process_videos_job,
            trigger=IntervalTrigger(hours=2),
            id='process_videos',
            name='Process videos from queue',
            replace_existing=True
        )

        # Queue cleanup job - daily at midnight
        self.scheduler.add_job(
            func=cleanup_job,
            trigger=CronTrigger(hour=0, minute=0),
            id='cleanup',
            name='Clean up old queue entries',
            replace_existing=True
        )

        # Health check job - every 30 minutes
        self.scheduler.add_job(
            func=health_check_job,
            trigger=IntervalTrigger(minutes=30),
            id='health_check',
            name='Service health check',
            replace_existing=True
        )
    

    def start(self, daemon: bool = False) -> bool:
        """Start the background service.
        
        Args:
            daemon: Whether to run as daemon process
            
        Returns:
            True if started successfully
        """
        if self.is_running():
            logger.warning("Service is already running")
            return False
        
        try:
            # Write PID file
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            # Setup scheduler
            self._setup_scheduler()
            
            # Start scheduler
            self.scheduler.start()
            self.running = True
            
            # Register cleanup handlers
            atexit.register(self.stop)
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            
            logger.info("YouTube monitoring service started")
            
            if daemon:
                # Run as daemon
                self._run_daemon()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the background service."""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
            
            self.running = False
            
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            logger.info("YouTube monitoring service stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping service: {e}")
            return False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def _run_daemon(self):
        """Run the service as a daemon."""
        logger.info("Running as daemon, press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, stopping...")
            self.stop()
    
    def is_running(self) -> bool:
        """Check if the service is currently running."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # Process not running, remove stale PID file
                self.pid_file.unlink()
                return False
                
        except (ValueError, FileNotFoundError):
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information."""
        status = {
            'running': self.is_running(),
            'pid_file': str(self.pid_file),
            'log_file': str(self.log_file)
        }
        
        if self.scheduler:
            # Get job information
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                })
            
            status['jobs'] = jobs
        
        # Get queue status
        video_queue = get_video_queue()
        queue_stats = video_queue.get_queue_stats()
        status['queue'] = queue_stats
        
        return status
    
    def get_logs(self, lines: int = 50) -> str:
        """Get recent service logs.
        
        Args:
            lines: Number of lines to return
            
        Returns:
            Log content
        """
        if not self.log_file.exists():
            return "No log file found"
        
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
            
            # Return last N lines
            return ''.join(log_lines[-lines:])
            
        except Exception as e:
            return f"Error reading log file: {e}"


# Global service instance
_service = None

def get_monitoring_service() -> YouTubeMonitoringService:
    """Get or create the global monitoring service instance."""
    global _service
    if _service is None:
        _service = YouTubeMonitoringService()
    return _service
