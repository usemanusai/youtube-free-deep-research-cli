"""
Unit tests for llm_service module.
"""

import pytest
from unittest.mock import patch, MagicMock
from llm_service import LLMService, APIError


class TestLLMService:
    """Test cases for LLMService class."""

    @pytest.fixture
    def llm_service(self):
        """Create an LLMService instance with a mock API key."""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}):
            return LLMService()

    def test_initialization_with_env_var(self):
        """Test initialization using environment variable."""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}):
            service = LLMService()
            assert service.api_key == 'test-key'
            assert service.model == 'z-ai/glm-4.5-air:free'

    def test_initialization_with_explicit_key(self):
        """Test initialization with explicit API key."""
        service = LLMService(api_key='explicit-key')
        assert service.api_key == 'explicit-key'

    def test_initialization_missing_api_key(self):
        """Test initialization failure with missing API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
                LLMService()

    def test_format_chat_history(self, llm_service):
        """Test formatting chat history for LLM context."""
        chat_history = [
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI stands for Artificial Intelligence."}
        ]

        formatted = llm_service._format_chat_history(chat_history)

        assert len(formatted) == 2
        assert formatted[0].content == "What is AI?"
        assert formatted[1].content == "AI stands for Artificial Intelligence."

    def test_format_chat_history_empty(self, llm_service):
        """Test formatting empty chat history."""
        formatted = llm_service._format_chat_history([])
        assert formatted == []

    def test_format_chat_history_system_message(self, llm_service):
        """Test formatting chat history with system message."""
        chat_history = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"}
        ]

        formatted = llm_service._format_chat_history(chat_history)

        assert len(formatted) == 2
        assert formatted[0].content == "You are helpful."
        assert formatted[1].content == "Hello"

    def test_generate_response_basic(self, llm_service):
        """Test basic response generation."""
        context = "This is test content."
        query = "What is this about?"

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "This is about testing."
            mock_invoke.return_value = mock_response

            result = llm_service.generate_response(context, query)

            assert result == "This is about testing."

            # Verify the call was made with correct messages
            assert mock_invoke.call_count == 1
            messages = mock_invoke.call_args[0][0]

            # Check system message contains context
            assert "This is test content" in messages[0].content

            # Check user query is the last message
            assert messages[-1].content == query

    def test_generate_response_with_history(self, llm_service):
        """Test response generation with chat history."""
        context = "Test content."
        query = "Tell me more?"
        chat_history = [
            {"role": "user", "content": "What is this?"},
            {"role": "assistant", "content": "It's a test."}
        ]

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "More details about testing."
            mock_invoke.return_value = mock_response

            result = llm_service.generate_response(context, query, chat_history)

            assert result == "More details about testing."

            # Verify messages include history
            messages = mock_invoke.call_args[0][0]
            # System + 2 history messages + user query = 4 messages
            assert len(messages) == 4

    def test_generate_response_api_error(self, llm_service):
        """Test handling of API errors in response generation."""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("API connection failed")

            with pytest.raises(RuntimeError, match="Failed to get response from LLM service"):
                llm_service.generate_response("content", "query")

    def test_summarize_content(self, llm_service):
        """Test content summarization."""
        content = "This is a long piece of content that needs summarizing."

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "Summary of the content."
            mock_invoke.return_value = mock_response

            result = llm_service.summarize_content(content)

            assert result == "Summary of the content."

            # Verify prompt structure
            messages = mock_invoke.call_args[0][0]
            assert "long piece of content" in messages[0].content
            assert "summarize" in messages[0].content.lower()

    def test_generate_faq(self, llm_service):
        """Test FAQ generation."""
        content = "Content about artificial intelligence."

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "Q: What is AI?\nA: Artificial Intelligence."
            mock_invoke.return_value = mock_response

            result = llm_service.generate_faq(content)

            assert "What is AI?" in result

            messages = mock_invoke.call_args[0][0]
            assert "artificial intelligence" in messages[0].content
            assert "faq" in messages[0].content.lower()

    def test_generate_toc(self, llm_service):
        """Test table of contents generation."""
        content = "Introduction section. Methods section. Results section."

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "1. Introduction\n2. Methods\n3. Results"
            mock_invoke.return_value = mock_response

            result = llm_service.generate_toc(content)

            assert "Introduction" in result

            messages = mock_invoke.call_args[0][0]
            assert "table of contents" in messages[0].content.lower()

    def test_generate_podcast_script(self, llm_service):
        """Test podcast script generation."""
        content = "Content about machine learning."

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "Host: Welcome to our podcast!\nExpert: Machine learning is fascinating."
            mock_invoke.return_value = mock_response

            result = llm_service.generate_podcast_script(content)

            assert "Welcome to our podcast" in result

            messages = mock_invoke.call_args[0][0]
            assert "podcast script" in messages[0].content.lower()
            assert "2 speakers" in messages[0].content

    def test_summarize_content_error(self, llm_service):
        """Test error handling in summarization."""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("API error")

            with pytest.raises(RuntimeError, match="Failed to generate summary"):
                llm_service.summarize_content("content")

    def test_generate_faq_error(self, llm_service):
        """Test error handling in FAQ generation."""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("API error")

            with pytest.raises(RuntimeError, match="Failed to generate FAQ"):
                llm_service.generate_faq("content")

    def test_generate_toc_error(self, llm_service):
        """Test error handling in table of contents generation."""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("API error")

            with pytest.raises(RuntimeError, match="Failed to generate table of contents"):
                llm_service.generate_toc("content")

    def test_generate_podcast_script_error(self, llm_service):
        """Test error handling in podcast script generation."""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("API error")

            with pytest.raises(RuntimeError, match="Failed to generate podcast script"):
                llm_service.generate_podcast_script("content")


class TestLLMServiceIntegration:
    """Integration tests for LLMService."""

    def test_prompt_includes_context_instructions(self, llm_service):
        """Test that prompts include proper context instructions."""
        context = "Test context"
        query = "Test question"

        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "Answer"
            mock_invoke.return_value = mock_response

            llm_service.generate_response(context, query)

            messages = mock_invoke.call_args[0][0]
            system_prompt = messages[0].content

            # Check for key instruction elements
            assert context in system_prompt
            assert "using ONLY the information in the provided context" in system_prompt
            assert "not present in the provided context" in system_prompt

    def test_prompt_guards_against_unanswerable_questions(self, llm_service):
        """Test that prompts include guards for unanswerable questions."""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_response = MagicMock()
            mock_response.content = "Answer"
            mock_invoke.return_value = mock_response

            llm_service.generate_response("context", "query")

            messages = mock_invoke.call_args[0][0]
            system_prompt = messages[0].content

            # Check for guard rails
            assert "not present in the provided context" in system_prompt or "can't answer that" in system_prompt
