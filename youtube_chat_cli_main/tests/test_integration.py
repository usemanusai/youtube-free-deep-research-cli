"""
Integration tests for the CLI application.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import os
import json


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @pytest.fixture
    def temp_env_file(self):
        """Create a temporary .env file."""
        env_content = """OPENROUTER_API_KEY=test_key
MARYTTS_SERVER_URL=http://localhost:59125
N8N_WEBHOOK_URL=http://localhost:5678/webhook/test

# LLM and TTS test settings for integration tests
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_path = f.name

        # Set environment variable
        os.environ['OPENROUTER_API_KEY'] = 'test_key'
        os.environ['MARYTTS_SERVER_URL'] = 'http://localhost:59125'
        os.environ['N8N_WEBHOOK_URL'] = 'http://localhost:5678/webhook/test'

        yield env_path

        # Cleanup
        Path(env_path).unlink(missing_ok=True)

    @pytest.fixture
    def mock_session_manager(self, temp_env_file):
        """Mock session manager with proper file path."""
        with patch('session_manager.SessionManager._get_session_file_path') as mock_get_path:
            mock_get_path.return_value = Path(tempfile.gettempdir()) / 'test_session.json'
            from session_manager import SessionManager
            manager = SessionManager()
            yield manager

    def test_session_workflow(self, mock_session_manager):
        """Test complete session management workflow."""
        # Test initial session creation
        session_id1 = mock_session_manager.get_session_id()
        assert session_id1

        # Test setting source
        test_url = "https://example.com"
        mock_session_manager.set_active_source(test_url)
        assert mock_session_manager.get_active_source() == test_url

        # Test adding chat history
        mock_session_manager.add_to_chat_history("user", "Hello")
        mock_session_manager.add_to_chat_history("assistant", "Hi there!")

        history = mock_session_manager.get_chat_history()
        assert len(history) == 2
        assert history[0]['content'] == "Hello"
        assert history[1]['content'] == "Hi there!"

        # Test session persistence
        mock_session_manager.save_session(mock_session_manager.load_session())

        # Create new manager instance to test persistence
        with patch('session_manager.SessionManager._get_session_file_path') as mock_get_path:
            mock_get_path.return_value = Path(tempfile.gettempdir()) / 'test_session.json'
            from session_manager import SessionManager
            new_manager = SessionManager()

            assert new_manager.get_active_source() == test_url
            assert len(new_manager.get_chat_history()) == 2

    @patch('source_processor.YouTubeTranscriptApi.get_transcript')
    @patch('source_processor.PunctuationModel.restore_punctuation')
    def test_content_processing_pipeline(self, mock_punct, mock_get_transcript):
        """Test the complete content processing pipeline."""
        from source_processor import SourceProcessor

        # Mock transcript
        mock_transcript = [
            {'text': 'Hello world'},
            {'text': 'This is a test'}
        ]
        mock_get_transcript.return_value = mock_transcript
        mock_punct.return_value = "Hello world. This is a test."

        processor = SourceProcessor()

        # Test YouTube processing
        result = processor.process_content("https://www.youtube.com/watch?v=test123")

        assert "Hello world" in result
        assert ". " in result  # Check punctuation was applied

        mock_get_transcript.assert_called_once_with('test123', languages=['en'])
        mock_punct.assert_called_once()

    @patch('source_processor.requests.get')
    @patch('source_processor.PunctuationModel.restore_punctuation')
    def test_website_processing_pipeline(self, mock_punct, mock_get):
        """Test website content processing pipeline."""
        from source_processor import SourceProcessor

        # Mock web response
        mock_response = MagicMock()
        mock_response.content = b'<html><body><h1>Test</h1><p>Content here</p></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        mock_punct.return_value = "Test. Content here."

        processor = SourceProcessor()

        # Test website processing
        result = processor.process_content("https://example.com")

        assert "Test" in result
        assert "Content here" in result
        mock_get.assert_called_once()
        mock_punct.assert_called_once()

    @patch('llm_service.ChatOpenAI.invoke')
    def test_llm_service_complete_workflow(self, mock_invoke):
        """Test LLM service complete workflow with mocking."""
        from llm_service import LLMService

        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}):
            service = LLMService()

            # Mock LLM response
            mock_response = MagicMock()
            mock_response.content = "This is a summary response."
            mock_invoke.return_value = mock_response

            # Test summarize
            result = service.summarize_content("Test content for summary")
            assert "summary response" in result

            # Test FAQ generation
            result = service.generate_faq("Test content for FAQ")
            assert "summary response" in result

            # Test TOC generation
            result = service.generate_toc("Test content for TOC")
            assert "summary response" in result

            # Verify calls were made
            assert mock_invoke.call_count == 3

    @patch('tts_service.requests.post')
    def test_tts_service_basic_workflow(self, mock_post):
        """Test TTS service basic workflow."""
        from tts_service import TTSService

        # Mock TTS response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'fake_audio_data'
        mock_post.return_value = mock_response

        service = TTSService()

        # Test audio generation
        result = service.generate_audio("Test text", "test_output.wav")

        assert result == "test_output.wav"
        mock_post.assert_called_once()

        # Verify file was created
        assert Path("test_output.wav").exists()

        # Cleanup
        Path("test_output.wav").unlink(missing_ok=True)

    @patch('n8n_client.requests.post')
    def test_n8n_client_workflow(self, mock_post):
        """Test n8n client communication workflow."""
        from n8n_client import N8nClient

        with patch.dict('os.environ', {'N8N_WEBHOOK_URL': 'http://test.com/webhook'}):
            client = N8nClient()

            # Mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"response": "Test response"}
            mock_post.return_value = mock_response

            # Test message sending
            result = client.send_chat_message("Hello", "session123")

            assert result == "Test response"
            mock_post.assert_called_once()

            # Verify payload structure
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert payload['chatInput'] == "Hello"
            assert payload['sessionId'] == "session123"

    def test_service_initialization_chain(self, temp_env_file):
        """Test the complete service initialization chain."""
        # This test verifies that all services can be initialized without errors
        # (Though actual API calls will be mocked)

        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}):
            # Test service factory functions
            from session_manager import SessionManager

            # Test session manager
            manager = SessionManager()

            # Test that we can create service instances (even if they don't fully connect)
            from source_processor import get_source_processor
            processor = get_source_processor()
            assert processor is not None

            # Test LLM service initialization (with mock)
            with patch('llm_service.ChatOpenAI'):
                from llm_service import LLMService
                llm = LLMService()
                assert llm is not None

            # Test TTS service
            with patch.dict('os.environ', {'MARYTTS_SERVER_URL': 'http://test.com'}):
                from tts_service import get_tts_service
                tts = get_tts_service()
                assert tts is not None

            # Test n8n client
            with patch.dict('os.environ', {'N8N_WEBHOOK_URL': 'http://test.com/webhook'}):
                from n8n_client import get_n8n_client
                n8n = get_n8n_client()
                assert n8n is not None

    def test_error_handling_through_stack(self, temp_env_file):
        """Test error handling propagates correctly through the stack."""
        from . import ProcessingError, APIError

        # Test custom exceptions exist and are importable
        assert ProcessingError
        assert APIError

        # Test error inheritance
        assert issubclass(ProcessingError, Exception)
        assert issubclass(APIError, Exception)

        # Test session manager error handling
        from session_manager import SessionManager
        manager = SessionManager()

        # Test invalid JSON handling (should recover gracefully)
        with patch.object(manager, '_save_session_file', side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                manager.save_session({"test": "data"})


# Helper function for running integration tests (for when pytest works)
def run_integration_tests():
    """Run integration tests manually if pytest isn't available."""
    print("Running integration test stubs...")

    try:
        # Basic import check
        from session_manager import SessionManager
        print("✓ SessionManager imports successfully")

        from source_processor import SourceProcessor
        print("✓ SourceProcessor imports successfully")

        from llm_service import LLMService
        print("✓ LLMService imports successfully")

        from tts_service import TTSService
        print("✓ TTSService imports successfully")

        from n8n_client import N8nClient
        print("✓ N8nClient imports successfully")

        print("✓ All modules import successfully")
        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


if __name__ == "__main__":
    run_integration_tests()
