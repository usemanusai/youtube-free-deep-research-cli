"""
Unit tests for source_processor module.
"""

import pytest
from unittest.mock import patch, MagicMock
from source_processor import SourceProcessor, ProcessingError


class TestSourceProcessor:
    """Test cases for SourceProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create a SourceProcessor instance."""
        return SourceProcessor()

    def test_youtube_video_id_extraction_standard_url(self, processor):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = processor.extract_youtube_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_video_id_extraction_short_url(self, processor):
        """Test extracting video ID from shortened YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = processor.extract_youtube_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_video_id_extraction_invalid_url(self, processor):
        """Test extracting video ID from invalid URL returns None."""
        url = "https://example.com/video"
        video_id = processor.extract_youtube_video_id(url)
        assert video_id is None

    @patch('source_processor.YouTubeTranscriptApi.get_transcript')
    def test_get_youtube_transcript_success(self, mock_get_transcript, processor):
        """Test successful YouTube transcript retrieval."""
        # Mock transcript data
        mock_transcript = [
            {'text': 'Hello'},
            {'text': 'world'}
        ]
        mock_get_transcript.return_value = mock_transcript

        # Mock punctuation restoration
        with patch.object(processor.punctuation_model, 'restore_punctuation') as mock_punct:
            mock_punct.return_value = "Hello world."

            result = processor.get_youtube_transcript("https://www.youtube.com/watch?v=test123")

            assert "Hello world" in result
            mock_get_transcript.assert_called_once_with('test123', languages=['en'])
            mock_punct.assert_called_once_with("Hello world")

    @patch('source_processor.YouTubeTranscriptApi.get_transcript')
    def test_get_youtube_transcript_disabled(self, mock_get_transcript, processor):
        """Test handling of disabled transcripts."""
        from youtube_transcript_api import TranscriptsDisabled
        mock_get_transcript.side_effect = TranscriptsDisabled("Transcripts disabled")

        with pytest.raises(ProcessingError, match="Transcripts are disabled"):
            processor.get_youtube_transcript("https://www.youtube.com/watch?v=test123")

    @patch('source_processor.YouTubeTranscriptApi.get_transcript')
    def test_get_youtube_transcript_no_transcript(self, mock_get_transcript, processor):
        """Test handling of no transcript found."""
        from youtube_transcript_api import NoTranscriptFound
        mock_get_transcript.side_effect = NoTranscriptFound("No transcript")

        with pytest.raises(ProcessingError, match="No English transcript found"):
            processor.get_youtube_transcript("https://www.youtube.com/watch?v=test123")

    def test_get_youtube_transcript_invalid_url(self, processor):
        """Test handling of invalid YouTube URL."""
        with pytest.raises(ProcessingError, match="Invalid YouTube URL"):
            processor.get_youtube_transcript("https://example.com")

    @patch('source_processor.requests.get')
    @patch.object(SourceProcessor, 'restore_punctuation')
    def test_scrape_website_text_success(self, mock_restore_punct, mock_get, processor):
        """Test successful website content scraping."""
        # Mock the web response
        mock_response = MagicMock()
        mock_response.content = b'<html><body><h1>Test Article</h1><p>This is content.</p><script>ignore me</script></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_restore_punct.return_value = "Test Article. This is content."

        result = processor.scrape_website_text("https://example.com")

        assert "Test Article" in result
        assert "This is content" in result
        mock_get.assert_called_once()
        mock_restore_punct.assert_called_once()

    @patch('source_processor.requests.get')
    def test_scrape_website_text_request_failure(self, mock_get, processor):
        """Test handling of website request failures."""
        import requests
        mock_get.side_effect = requests.RequestException("Connection failed")

        with pytest.raises(ProcessingError, match="Failed to access website"):
            processor.scrape_website_text("https://example.com")

    def test_restore_punctuation_success(self, processor):
        """Test successful punctuation restoration."""
        # Mock the punctuation model
        with patch.object(processor.punctuation_model, 'restore_punctuation') as mock_punct:
            mock_punct.return_value = "Hello world."

            result = processor.restore_punctuation("hello world")

            assert result == "Hello.\nworld."
            mock_punct.assert_called_once_with("hello world")

    def test_restore_punctuation_failure(self, processor):
        """Test handling of punctuation restoration errors."""
        with patch.object(processor.punctuation_model, 'restore_punctuation') as mock_punct:
            mock_punct.side_effect = Exception("Punctuation error")

            with pytest.raises(ProcessingError, match="Failed to restore punctuation"):
                processor.restore_punctuation("hello world")

    def test_process_content_youtube(self, processor):
        """Test processing YouTube content."""
        with patch.object(processor, 'get_youtube_transcript') as mock_get:
            mock_get.return_value = "Hello world"

            with patch.object(processor, 'restore_punctuation') as mock_punct:
                mock_punct.return_value = "Hello world."

                result = processor.process_content("https://youtu.be/test123")

                assert result == "Hello world."
                mock_get.assert_called_once_with("https://youtu.be/test123")
                mock_punct.assert_called_once_with("Hello world")

    def test_process_content_website(self, processor):
        """Test processing website content."""
        with patch.object(processor, 'scrape_website_text') as mock_scrape:
            mock_scrape.return_value = "Website content"

            with patch.object(processor, 'restore_punctuation') as mock_punct:
                mock_punct.return_value = "Website content."

                result = processor.process_content("https://example.com")

                assert result == "Website content."
                mock_scrape.assert_called_once_with("https://example.com")
                mock_punct.assert_called_once_with("Website content")

    def test_process_content_unsupported_scheme(self, processor):
        """Test processing unsupported URL scheme."""
        with pytest.raises(ProcessingError, match="Unsupported URL scheme"):
            processor.process_content("ftp://example.com")
