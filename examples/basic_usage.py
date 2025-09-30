#!/usr/bin/env python3
"""
Basic usage examples for YouTube Chat CLI.
"""

import sys
import os

# Add the src directory to the Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_chat_cli.core.youtube_api import get_youtube_client
from youtube_chat_cli.services.transcription.processor import get_source_processor
from youtube_chat_cli.utils.llm_service import get_llm_service


def example_youtube_transcript():
    """Example: Get transcript from a YouTube video."""
    print("=== YouTube Transcript Example ===")
    
    # Initialize source processor
    processor = get_source_processor()
    
    # Example YouTube video URL
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        transcript = processor.get_youtube_transcript(video_url)
        print(f"Transcript length: {len(transcript)} characters")
        print(f"First 200 characters: {transcript[:200]}...")
    except Exception as e:
        print(f"Error getting transcript: {e}")


def example_youtube_api():
    """Example: Use YouTube API to get video information."""
    print("\n=== YouTube API Example ===")
    
    try:
        # Initialize YouTube client
        youtube_client = get_youtube_client()
        
        # Get video details
        video_id = "dQw4w9WgXcQ"
        videos = youtube_client.get_video_details([video_id])
        
        if videos:
            video = videos[0]
            print(f"Title: {video.title}")
            print(f"Channel: {video.channel_title}")
            print(f"Duration: {video.duration_seconds} seconds")
            print(f"Views: {video.view_count}")
        else:
            print("No video found")
            
    except Exception as e:
        print(f"Error using YouTube API: {e}")


def example_llm_chat():
    """Example: Chat with LLM about content."""
    print("\n=== LLM Chat Example ===")
    
    try:
        # Initialize LLM service
        llm_service = get_llm_service()
        
        # Example content
        content = "This is a sample video transcript about artificial intelligence and machine learning."
        
        # Ask a question
        question = "What is this content about?"
        response = llm_service.ask_question(content, question)
        
        print(f"Question: {question}")
        print(f"Answer: {response}")
        
    except Exception as e:
        print(f"Error with LLM service: {e}")


if __name__ == "__main__":
    print("YouTube Chat CLI - Basic Usage Examples")
    print("=" * 50)
    
    example_youtube_transcript()
    example_youtube_api()
    example_llm_chat()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
