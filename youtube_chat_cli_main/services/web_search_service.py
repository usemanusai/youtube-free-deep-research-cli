"""
JAEGIS NexusSync - Web Search Service

This module provides web search capabilities with multiple backends:
- Tavily (FREE tier: 1,000 searches/month)
- DuckDuckGo (FREE, unlimited, fallback)

Used by Adaptive RAG for web search when vector store doesn't have answers.
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# DuckDuckGo
try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

from ..core.config import get_config

logger = logging.getLogger(__name__)


class WebSearchError(Exception):
    """Raised when web search operations fail."""
    pass


class BaseWebSearchService(ABC):
    """Abstract base class for web search services."""
    
    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the web and return results."""
        pass


class TavilySearchService(BaseWebSearchService):
    """
    Tavily search service (FREE tier: 1,000 searches/month).
    
    High-quality search results optimized for AI/RAG applications.
    """
    
    def __init__(self, config):
        """Initialize Tavily search service."""
        if not TAVILY_AVAILABLE:
            raise WebSearchError(
                "Tavily package not installed. Install with: pip install tavily-python"
            )
        
        self.config = config
        
        if not config.tavily_api_key:
            raise WebSearchError("Tavily API key not configured")
        
        try:
            self.client = TavilyClient(api_key=config.tavily_api_key)
            logger.info("✅ Tavily search service initialized")
        except Exception as e:
            raise WebSearchError(f"Failed to initialize Tavily client: {e}")
    
    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search using Tavily.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of search result dictionaries
        """
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0)
                })
            
            logger.info(f"Tavily search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise WebSearchError(f"Search failed: {e}")


class DuckDuckGoSearchService(BaseWebSearchService):
    """
    DuckDuckGo search service (FREE, unlimited).
    
    Fallback search when Tavily is not available or rate limited.
    """
    
    def __init__(self, config):
        """Initialize DuckDuckGo search service."""
        if not DUCKDUCKGO_AVAILABLE:
            raise WebSearchError(
                "DuckDuckGo package not installed. Install with: pip install duckduckgo-search"
            )
        
        self.config = config
        logger.info("✅ DuckDuckGo search service initialized")
    
    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of search result dictionaries
        """
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(
                    query,
                    max_results=max_results
                ))
            
            results = []
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'content': result.get('body', ''),
                    'score': 1.0  # DuckDuckGo doesn't provide scores
                })
            
            logger.info(f"DuckDuckGo search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise WebSearchError(f"Search failed: {e}")


class WebSearchService:
    """
    Unified web search service with automatic fallback.
    
    Tries Tavily first (if configured), falls back to DuckDuckGo.
    """
    
    def __init__(self):
        """Initialize web search service with configured backends."""
        self.config = get_config()
        self.primary_backend = None
        self.fallback_backend = None
        
        # Try to initialize Tavily as primary
        if self.config.tavily_api_key:
            try:
                self.primary_backend = TavilySearchService(self.config)
                logger.info("Using Tavily as primary search backend")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily: {e}")
        
        # Initialize DuckDuckGo as fallback
        if self.config.use_duckduckgo_fallback:
            try:
                self.fallback_backend = DuckDuckGoSearchService(self.config)
                logger.info("Using DuckDuckGo as fallback search backend")
            except Exception as e:
                logger.warning(f"Failed to initialize DuckDuckGo: {e}")
        
        # Ensure at least one backend is available
        if not self.primary_backend and not self.fallback_backend:
            raise WebSearchError(
                "No web search backend available. Please configure:\n"
                "- Tavily API key (TAVILY_API_KEY), or\n"
                "- Enable DuckDuckGo fallback (USE_DUCKDUCKGO_FALLBACK=true)"
            )
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        use_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search the web with automatic fallback.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            use_fallback: Whether to use fallback on primary failure
        
        Returns:
            List of search result dictionaries
        """
        # Try primary backend first
        if self.primary_backend:
            try:
                results = self.primary_backend.search(query, max_results)
                if results:
                    return results
                logger.warning("Primary search returned no results, trying fallback...")
            except Exception as e:
                logger.warning(f"Primary search failed: {e}, trying fallback...")
        
        # Try fallback backend
        if use_fallback and self.fallback_backend:
            try:
                return self.fallback_backend.search(query, max_results)
            except Exception as e:
                logger.error(f"Fallback search also failed: {e}")
                raise WebSearchError(f"All search backends failed: {e}")
        
        # No results from any backend
        raise WebSearchError("No search results available")
    
    def format_results_for_context(
        self,
        results: List[Dict[str, Any]],
        max_length: int = 2000
    ) -> str:
        """
        Format search results as context for LLM.
        
        Args:
            results: List of search results
            max_length: Maximum total length of formatted text
        
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results, 1):
            # Format single result
            result_text = (
                f"[{i}] {result['title']}\n"
                f"URL: {result['url']}\n"
                f"{result['content']}\n"
            )
            
            # Check if adding this result would exceed max length
            if current_length + len(result_text) > max_length:
                break
            
            context_parts.append(result_text)
            current_length += len(result_text)
        
        return "\n".join(context_parts)


# Global service instance
_web_search_service: Optional[WebSearchService] = None


def get_web_search_service() -> WebSearchService:
    """
    Get the global web search service instance.
    
    Returns:
        WebSearchService instance
    """
    global _web_search_service
    
    if _web_search_service is None:
        _web_search_service = WebSearchService()
        logger.info("Web search service instance created")
    
    return _web_search_service

