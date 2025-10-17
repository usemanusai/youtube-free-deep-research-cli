"""
Web Search Aggregator Service (scaffold)

Runs multiple search backends in parallel (Brave, Tavily, DuckDuckGo) and merges
results. For now, this scaffold returns results from the existing WebSearchService
as a placeholder to maintain backward compatibility while we flesh out the
hybrid strategy.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from .web_search_service import get_web_search_service

logger = logging.getLogger(__name__)


class WebSearchAggregatorService:
    """Aggregates multiple web search backends.

    This scaffold currently proxies to the existing WebSearchService to avoid
    behavior changes until full hybrid implementation is added.
    """

    def __init__(self, backends: Optional[List[str]] = None):
        self.backends = backends  # e.g., ["brave", "tavily", "duckduckgo"]
        self._fallback = get_web_search_service()

    def search(self, query: str, max_results: int = 10, backends: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search using configured backends.

        Returns a normalized list of results: [{title, url, content, score}]
        """
        # Placeholder behavior: just delegate to existing service
        logger.info("[WebSearchAggregatorService] Delegating to WebSearchService (scaffold)")
        return self._fallback.search(query=query, max_results=max_results)

    def format_results_for_context(self, results: List[Dict[str, Any]], max_length: int = 2000) -> str:
        return self._fallback.format_results_for_context(results, max_length=max_length)

