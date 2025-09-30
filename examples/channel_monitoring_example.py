#!/usr/bin/env python3
"""
Channel monitoring examples for YouTube Chat CLI.
"""

import sys
import os
import time

# Add the src directory to the Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_chat_cli.services.monitoring.channel_monitor import get_channel_monitor
from youtube_chat_cli.services.monitoring.video_queue import get_video_queue
from youtube_chat_cli.services.monitoring.video_processor import get_video_processor
from youtube_chat_cli.core.database import get_video_database


def example_add_channel():
    """Example: Add a channel for monitoring."""
    print("=== Add Channel Example ===")
    
    try:
        channel_monitor = get_channel_monitor()
        
        # Add a channel with filters
        channel_url = "https://www.youtube.com/@3Blue1Brown"
        filters = {
            "no_shorts": True,
            "min_duration": 300,  # 5 minutes minimum
            "include_keywords": ["mathematics", "visualization"]
        }
        
        result = channel_monitor.add_channel(
            channel_url=channel_url,
            check_interval=24,  # Check daily
            filters=filters
        )
        
        print(f"Added channel: {result['name']}")
        print(f"Channel ID: {result['channel_id']}")
        print(f"Filters: {result['filters']}")
        
    except Exception as e:
        print(f"Error adding channel: {e}")


def example_scan_channel():
    """Example: Scan a channel for new videos."""
    print("\n=== Scan Channel Example ===")
    
    try:
        channel_monitor = get_channel_monitor()
        video_db = get_video_database()
        
        # Get first active channel
        channels = video_db.get_channels(active_only=True)
        if not channels:
            print("No active channels found. Add a channel first.")
            return
        
        channel = channels[0]
        print(f"Scanning channel: {channel['name']}")
        
        # Scan for new videos
        result = channel_monitor.scan_channel(channel['id'], force=True)
        
        print(f"Videos found: {result['total_videos_found']}")
        print(f"After filtering: {result['filtered_videos']}")
        print(f"New videos: {result['new_videos']}")
        print(f"Queued for processing: {result['queued_for_processing']}")
        
    except Exception as e:
        print(f"Error scanning channel: {e}")


def example_queue_status():
    """Example: Check video processing queue status."""
    print("\n=== Queue Status Example ===")
    
    try:
        video_queue = get_video_queue()
        
        # Get queue statistics
        stats = video_queue.get_queue_stats()
        
        print("Queue Statistics:")
        print(f"  Queue stats: {stats['queue_stats']}")
        print(f"  Videos processed today: {stats['videos_processed_today']}/{stats['daily_limit']}")
        
        if stats['next_scheduled_video']:
            print(f"  Next video scheduled: {stats['next_scheduled_video']}")
        
        if stats['backoff_until']:
            print(f"  Backing off until: {stats['backoff_until']}")
        
    except Exception as e:
        print(f"Error getting queue status: {e}")


def example_process_video():
    """Example: Process one video from the queue."""
    print("\n=== Process Video Example ===")
    
    try:
        video_processor = get_video_processor()
        
        # Check processing status
        status = video_processor.get_processing_status()
        print(f"Processor ready: {status['processor_ready']}")
        print(f"Next video ready: {status['next_video_ready']}")
        
        if status['next_video_ready']:
            print("Processing next video...")
            result = video_processor.process_next_video()
            
            if result:
                if result['success']:
                    print(f"✓ Successfully processed video: {result['video_id']}")
                    if result.get('n8n_sent'):
                        print("✓ Video data sent to n8n workflow")
                else:
                    print(f"✗ Failed to process video: {result['error']}")
                    if result.get('rate_limited'):
                        print("⚠ Rate limiting detected")
            else:
                print("No videos ready for processing")
        else:
            print("No videos ready for processing")
        
    except Exception as e:
        print(f"Error processing video: {e}")


def example_statistics():
    """Example: Get monitoring statistics."""
    print("\n=== Statistics Example ===")
    
    try:
        video_db = get_video_database()
        
        # Get comprehensive statistics
        stats = video_db.get_statistics()
        
        print("System Statistics:")
        print(f"  Channels: {stats['channels']['active']} active, {stats['channels']['total']} total")
        print(f"  Videos: {stats['videos']['total']} total, {stats['videos']['processed']} processed")
        print(f"  Recent activity: {stats['videos']['last_24h']} videos in last 24h")
        
        if stats['videos']['total'] > 0:
            success_rate = (stats['videos']['processed'] / stats['videos']['total']) * 100
            print(f"  Success rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"Error getting statistics: {e}")


if __name__ == "__main__":
    print("YouTube Chat CLI - Channel Monitoring Examples")
    print("=" * 60)
    
    example_add_channel()
    example_scan_channel()
    example_queue_status()
    example_process_video()
    example_statistics()
    
    print("\n" + "=" * 60)
    print("Channel monitoring examples completed!")
    print("\nNote: These examples demonstrate the API usage.")
    print("For production use, run the background service:")
    print("  python -m youtube_chat_cli.cli.main service start --daemon")
