"""
Source processor module for fetching and processing content from URLs.
"""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs
from deepmultilingualpunctuation import PunctuationModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Error related to content processing."""
    pass

class APIError(Exception):
    """Error related to external API calls."""
    pass


class SourceProcessor:
    """Handles content extraction and processing from various sources."""

    def __init__(self):
        """Initialize the source processor with required models."""
        self.punctuation_model = None  # Lazy loaded to avoid disk issues

    def extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL.

        Args:
            url: YouTube URL (youtu.be or youtube.com formats)

        Returns:
            Video ID string or None if invalid URL
        """
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'www.youtube.com':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
        return None

    def get_youtube_transcript(self, url: str) -> str:
        """Fetch and process YouTube video transcript.

        Args:
            url: YouTube video URL

        Returns:
            Processed transcript text

        Raises:
            ProcessingError: If transcript cannot be fetched or processed
        """
        logger.info(f"Fetching YouTube transcript for URL: {url}")

        video_id = self.extract_youtube_video_id(url)
        if not video_id:
            raise ProcessingError(f"Invalid YouTube URL: {url}")

        try:
            logger.debug(f"Extracted video ID: {video_id}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

            # Combine all transcript entries into a single text
            raw_text = " ".join([entry['text'] for entry in transcript])

            logger.info(f"Successfully fetched transcript ({len(transcript)} segments, {len(raw_text)} characters)")

            return raw_text

        except TranscriptsDisabled:
            raise ProcessingError(f"Transcripts are disabled for this video: {url}")
        except NoTranscriptFound:
            raise ProcessingError(f"No English transcript found for video: {url}")
        except Exception as e:
            logger.error(f"Failed to fetch YouTube transcript: {e}")
            raise ProcessingError(f"Failed to fetch video transcript: {str(e)}")

    def scrape_website_text(self, url: str) -> str:
        """Scrape main textual content from a website.

        Args:
            url: Website URL to scrape

        Returns:
            Main text content from the page

        Raises:
            ProcessingError: If website cannot be accessed or processed
        """
        logger.info(f"Scraping website content from URL: {url}")

        try:
            # Set up headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()

            # Extract text from main content areas
            content_texts = []

            # Try to find main content areas
            main_areas = soup.find_all(['main', 'article', 'div'], class_=re.compile(r'(content|main|post|article)'))

            if main_areas:
                # Use found content areas
                for area in main_areas:
                    text = area.get_text(separator=' ', strip=True)
                    if len(text) > 100:  # Only include substantial content
                        content_texts.append(text)
            else:
                # Fallback: use body text
                body = soup.find('body')
                if body:
                    body_text = body.get_text(separator=' ', strip=True)
                    content_texts.append(body_text)

            # Combine all content
            combined_text = ' '.join(content_texts)

            # Clean up excessive whitespace
            combined_text = re.sub(r'\s+', ' ', combined_text).strip()

            logger.info(f"Successfully scraped website content ({len(combined_text)} characters)")

            return combined_text

        except requests.RequestException as e:
            logger.error(f"Failed to access website: {e}")
            raise ProcessingError(f"Failed to access website: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to process website content: {e}")
            raise ProcessingError(f"Failed to process website content: {str(e)}")

    def restore_punctuation(self, text: str) -> str:
        """Restore punctuation to unpunctuated text.

        Args:
            text: Raw text without punctuation

        Returns:
            Text with restored punctuation

        Raises:
            ProcessingError: If punctuation restoration fails
        """
        logger.info(f"Restoring punctuation to text ({len(text)} characters)")

        try:
            punctuated_text = self.punctuation_model.restore_punctuation(text)

            # Post-process: fix sentence breaking
            punctuated_text = punctuated_text.replace('. ', '.\n').replace('? ', '?\n').replace('! ', '!\n')

            logger.info(f"Successfully restored punctuation ({len(punctuated_text)} characters output)")

            return punctuated_text

        except Exception as e:
            logger.error(f"Failed to restore punctuation: {e}")
            raise ProcessingError(f"Failed to restore punctuation: {str(e)}")

    def process_content(self, url: str) -> str:
        """Process content from any supported URL type.

        Args:
            url: URL to process (YouTube or website)

        Returns:
            Processed and punctuated text content

        Raises:
            ProcessingError: If URL type is not supported or processing fails
        """
        logger.info(f"Processing content from URL: {url}")

        # Determine URL type and process accordingly
        if 'youtube.com' in url or 'youtu.be' in url:
            raw_text = self.get_youtube_transcript(url)
        elif url.startswith('http://') or url.startswith('https://'):
            raw_text = self.scrape_website_text(url)
        else:
            raise ProcessingError(f"Unsupported URL scheme. Only HTTP/HTTPS and YouTube URLs are supported: {url}")

        # Restore punctuation to the raw text
        processed_text = self.restore_punctuation(raw_text)

        logger.info(f"Content processing complete ({len(processed_text)} characters)")

        return processed_text


# Global source processor instance
_source_processor = None

def get_source_processor() -> SourceProcessor:
    """Get or create the global source processor instance."""
    global _source_processor
    if _source_processor is None:
        _source_processor = SourceProcessor()
    return _source_processor
