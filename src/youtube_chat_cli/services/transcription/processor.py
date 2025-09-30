"""
Source processor module for fetching and processing content from URLs.
"""

__all__ = ['SourceProcessor', 'ProcessingError', 'APIError', 'get_source_processor']

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs
try:
    from deepmultilingualpunctuation import PunctuationModel
    PUNCTUATION_MODEL_AVAILABLE = True
except ImportError:
    PunctuationModel = None
    PUNCTUATION_MODEL_AVAILABLE = False
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests
from bs4 import BeautifulSoup


class ProcessingError(Exception):
    """Error related to content processing."""
    pass

class APIError(Exception):
    """Error related to external API calls."""
    pass

import logging
logger = logging.getLogger(__name__)


class SourceProcessor:
    """Handles content extraction and processing from various sources."""

    def __init__(self):
        """Initialize the source processor with required models."""
        logger.info("Initializing SourceProcessor...")
        if PUNCTUATION_MODEL_AVAILABLE:
            try:
                # Suppress deprecation warnings from transformers
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
                    self.punctuation_model = PunctuationModel()
                logger.info("PunctuationModel loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load punctuation model: {e}")
                logger.warning("Proceeding without punctuation restoration")
                self.punctuation_model = None
        else:
            logger.warning("PunctuationModel not available - proceeding without punctuation restoration")
            self.punctuation_model = None

    def extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'www.youtube.com':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
        return None

    def get_youtube_transcript(self, url: str) -> str:
        """Fetch and process YouTube video transcript."""
        logger.info(f"Fetching YouTube transcript for URL: {url}")

        video_id = self.extract_youtube_video_id(url)
        if not video_id:
            raise ProcessingError(f"Invalid YouTube URL: {url}")

        try:
            logger.debug(f"Extracted video ID: {video_id}")
            # Create API instance and fetch transcript
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=['en'])

            # Combine all transcript entries into a single text
            transcript_segments = list(transcript)
            raw_text = " ".join([entry.text for entry in transcript_segments])

            logger.info(f"Successfully fetched transcript ({len(transcript_segments)} segments, {len(raw_text)} characters)")

            return raw_text

        except TranscriptsDisabled:
            raise ProcessingError(f"Transcripts are disabled for this video: {url}")
        except NoTranscriptFound:
            raise ProcessingError(f"No English transcript found for video: {url}")
        except Exception as e:
            logger.error(f"Failed to fetch YouTube transcript: {e}")
            raise ProcessingError(f"Failed to fetch video transcript: {str(e)}")

    def scrape_website_text(self, url: str) -> str:
        """Scrape main textual content from a website."""
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
        """Restore punctuation to unpunctuated text."""
        logger.info(f"Restoring punctuation to text ({len(text)} characters)")

        try:
            if self.punctuation_model is None:
                logger.info("Loading punctuation model...")
                self.punctuation_model = PunctuationModel()
                logger.info("Punctuation model loaded successfully")

            punctuated_text = self.punctuation_model.restore_punctuation(text)

            # Post-process: fix sentence breaking
            punctuated_text = punctuated_text.replace('. ', '.\n').replace('? ', '?\n').replace('! ', '!\n')

            logger.info(f"Successfully restored punctuation ({len(punctuated_text)} characters output)")

            return punctuated_text

        except Exception as e:
            logger.error(f"Failed to restore punctuation: {e}")
            logger.warning("Returning original text without punctuation restoration")
            # Return original text if punctuation fails
            return text

    def process_content(self, url: str) -> str:
        """Process content from any supported URL type."""
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

def get_source_processor():
    """Get or create the global source processor instance."""
    global _source_processor
    if _source_processor is None:
        _source_processor = SourceProcessor()
    return _source_processor
