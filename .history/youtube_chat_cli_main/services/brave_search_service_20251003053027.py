"""
Brave Search Service (scaffold)

Provides a simple interface to query Brave Search API. This is a scaffold only
and does not perform real HTTP calls yet. The goal is to define a stable
interface for later implementation and testing with mocks.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from ..core.config import get_config

logger = logging.getLogger(__name__)


class BraveSearchError(Exception):
    pass


class BraveSearchService:
    """Interface to Brave Search API.

    Expected environment/config key: BRAVE_API_KEY
    """

    def __init__(self, api_key: Optional[str] = None):
        cfg = get_config()
        self.api_key = api_key or getattr(cfg, "brave_api_key", None)
        if not self.api_key:
            logger.warning("BraveSearchService initialized without API key. Calls will fail until configured.")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Brave for the given query.

        Args:
            query: Search query text
            max_results: maximum number of results to return

        Returns: A list of normalized results: [{title, url, content, score}]
        """
        # NOTE: This is a scaffold. Real HTTP request will be implemented later.
        # Pseudocode for later implementation (kept here for reference):
        #   url = "https://api.search.brave.com/res/v1/web/search"
        #   headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        #   params = {"q": query, "count": max_results}
        #   resp = requests.get(url, headers=headers, params=params, timeout=30)
        #   resp.raise_for_status()
        #   data = resp.json()
        #   normalized = [...]
        if not self.api_key:
            raise BraveSearchError("Brave API key not configured. Set BRAVE_API_KEY in .env")
        logger.info("[BraveSearchService] search called (scaffold), returning empty results for now")
        return []

