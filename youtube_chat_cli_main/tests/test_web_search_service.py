"""
Unit tests for the Web Search Service.
"""

import pytest
from unittest.mock import Mock, patch

from youtube_chat_cli_main.services.web_search_service import (
    TavilySearchService,
    DuckDuckGoSearchService,
    WebSearchService,
    WebSearchError
)


class TestTavilySearchService:
    """Test suite for TavilySearchService."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.tavily_api_key = "test-api-key"
        return config
    
    @pytest.fixture
    def mock_tavily_client(self):
        """Mock Tavily client."""
        with patch('youtube_chat_cli_main.services.web_search_service.TavilyClient') as mock:
            client = Mock()
            mock.return_value = client
            yield client
    
    def test_initialization(self, mock_config, mock_tavily_client):
        """Test Tavily search service initialization."""
        service = TavilySearchService(mock_config)
        
        assert service.config == mock_config
        mock_tavily_client.assert_called_once()
    
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        config = Mock()
        config.tavily_api_key = None
        
        with pytest.raises(WebSearchError, match="Tavily API key not configured"):
            TavilySearchService(config)
    
    def test_search(self, mock_config, mock_tavily_client):
        """Test Tavily search."""
        mock_tavily_client.search.return_value = {
            "results": [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "content": "Test content 1",
                    "score": 0.9
                },
                {
                    "title": "Test Result 2",
                    "url": "https://example.com/2",
                    "content": "Test content 2",
                    "score": 0.8
                }
            ]
        }
        
        service = TavilySearchService(mock_config)
        results = service.search("test query", max_results=5)
        
        assert len(results) == 2
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["score"] == 0.9
        
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False
        )
    
    def test_search_error_handling(self, mock_config, mock_tavily_client):
        """Test search error handling."""
        mock_tavily_client.search.side_effect = Exception("API error")
        
        service = TavilySearchService(mock_config)
        
        with pytest.raises(WebSearchError, match="Search failed"):
            service.search("test query")


class TestDuckDuckGoSearchService:
    """Test suite for DuckDuckGoSearchService."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        return config
    
    @pytest.fixture
    def mock_ddgs(self):
        """Mock DuckDuckGo search."""
        with patch('youtube_chat_cli_main.services.web_search_service.DDGS') as mock:
            yield mock
    
    def test_initialization(self, mock_config):
        """Test DuckDuckGo search service initialization."""
        service = DuckDuckGoSearchService(mock_config)
        
        assert service.config == mock_config
    
    def test_search(self, mock_config, mock_ddgs):
        """Test DuckDuckGo search."""
        mock_instance = Mock()
        mock_instance.text.return_value = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "Test content 1"
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "Test content 2"
            }
        ]
        mock_ddgs.return_value.__enter__.return_value = mock_instance
        
        service = DuckDuckGoSearchService(mock_config)
        results = service.search("test query", max_results=5)
        
        assert len(results) == 2
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["content"] == "Test content 1"
        assert results[0]["score"] == 1.0  # DuckDuckGo doesn't provide scores
        
        mock_instance.text.assert_called_once_with("test query", max_results=5)
    
    def test_search_error_handling(self, mock_config, mock_ddgs):
        """Test search error handling."""
        mock_ddgs.return_value.__enter__.side_effect = Exception("Search error")
        
        service = DuckDuckGoSearchService(mock_config)
        
        with pytest.raises(WebSearchError, match="Search failed"):
            service.search("test query")


class TestWebSearchService:
    """Test suite for unified WebSearchService."""
    
    @pytest.fixture
    def mock_config_tavily(self):
        """Mock configuration with Tavily."""
        config = Mock()
        config.tavily_api_key = "test-api-key"
        config.use_duckduckgo_fallback = True
        return config
    
    @pytest.fixture
    def mock_config_duckduckgo_only(self):
        """Mock configuration with DuckDuckGo only."""
        config = Mock()
        config.tavily_api_key = None
        config.use_duckduckgo_fallback = True
        return config
    
    @pytest.fixture
    def mock_config_no_search(self):
        """Mock configuration with no search backends."""
        config = Mock()
        config.tavily_api_key = None
        config.use_duckduckgo_fallback = False
        return config
    
    def test_initialization_with_tavily_and_fallback(self, mock_config_tavily):
        """Test initialization with Tavily primary and DuckDuckGo fallback."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_tavily), \
             patch('youtube_chat_cli_main.services.web_search_service.TavilyClient'), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            
            assert service.primary_backend is not None
            assert service.fallback_backend is not None
    
    def test_initialization_with_duckduckgo_only(self, mock_config_duckduckgo_only):
        """Test initialization with DuckDuckGo only."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_duckduckgo_only), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            
            assert service.primary_backend is None
            assert service.fallback_backend is not None
    
    def test_initialization_with_no_backends(self, mock_config_no_search):
        """Test initialization fails with no backends."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_no_search):
            
            with pytest.raises(WebSearchError, match="No web search backend available"):
                WebSearchService()
    
    def test_search_with_primary_success(self, mock_config_tavily):
        """Test search with successful primary backend."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_tavily), \
             patch('youtube_chat_cli_main.services.web_search_service.TavilyClient'), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            service.primary_backend = Mock()
            service.primary_backend.search.return_value = [
                {"title": "Test", "url": "https://example.com", "content": "Test content", "score": 0.9}
            ]
            
            results = service.search("test query")
            
            assert len(results) == 1
            service.primary_backend.search.assert_called_once()
    
    def test_search_with_primary_failure_fallback_success(self, mock_config_tavily):
        """Test search with primary failure and successful fallback."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_tavily), \
             patch('youtube_chat_cli_main.services.web_search_service.TavilyClient'), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            service.primary_backend = Mock()
            service.primary_backend.search.side_effect = Exception("Primary failed")
            service.fallback_backend = Mock()
            service.fallback_backend.search.return_value = [
                {"title": "Fallback", "url": "https://example.com", "content": "Fallback content", "score": 1.0}
            ]
            
            results = service.search("test query")
            
            assert len(results) == 1
            assert results[0]["title"] == "Fallback"
            service.primary_backend.search.assert_called_once()
            service.fallback_backend.search.assert_called_once()
    
    def test_search_with_both_failures(self, mock_config_tavily):
        """Test search with both backends failing."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_tavily), \
             patch('youtube_chat_cli_main.services.web_search_service.TavilyClient'), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            service.primary_backend = Mock()
            service.primary_backend.search.side_effect = Exception("Primary failed")
            service.fallback_backend = Mock()
            service.fallback_backend.search.side_effect = Exception("Fallback failed")
            
            with pytest.raises(WebSearchError, match="All search backends failed"):
                service.search("test query")
    
    def test_format_results_for_context(self, mock_config_tavily):
        """Test formatting search results for LLM context."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_tavily), \
             patch('youtube_chat_cli_main.services.web_search_service.TavilyClient'), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            
            results = [
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "content": "Content 1",
                    "score": 0.9
                },
                {
                    "title": "Result 2",
                    "url": "https://example.com/2",
                    "content": "Content 2",
                    "score": 0.8
                }
            ]
            
            formatted = service.format_results_for_context(results, max_length=500)
            
            assert "[1] Result 1" in formatted
            assert "URL: https://example.com/1" in formatted
            assert "Content 1" in formatted
            assert "[2] Result 2" in formatted
    
    def test_format_results_respects_max_length(self, mock_config_tavily):
        """Test that format_results_for_context respects max_length."""
        with patch('youtube_chat_cli_main.services.web_search_service.get_config', return_value=mock_config_tavily), \
             patch('youtube_chat_cli_main.services.web_search_service.TavilyClient'), \
             patch('youtube_chat_cli_main.services.web_search_service.DDGS'):
            
            service = WebSearchService()
            
            results = [
                {
                    "title": "Result " + str(i),
                    "url": f"https://example.com/{i}",
                    "content": "A" * 1000,  # Very long content
                    "score": 0.9
                }
                for i in range(10)
            ]
            
            formatted = service.format_results_for_context(results, max_length=500)
            
            assert len(formatted) <= 500

