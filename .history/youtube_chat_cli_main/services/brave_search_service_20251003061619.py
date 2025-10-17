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

    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: Optional[str] = None, timeout_s: int = 30):
        cfg = get_config()
        self.api_key = api_key or getattr(cfg, "brave_api_key", None)
        self.timeout_s = timeout_s
        if not self.api_key:
            logger.warning("BraveSearchService initialized without API key. Calls will fail until configured.")

    def _normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            web = data.get("web", {})
            items = web.get("results", [])
            for it in items:
                url = it.get("url") or it.get("link")
                title = it.get("title") or it.get("name") or ""
                snippet = it.get("description") or it.get("snippet") or ""
                published = it.get("age", {}).get("published") or it.get("date")
                score = float(it.get("meta", {}).get("score", 1.0)) if isinstance(it.get("meta"), dict) else 1.0
                if url:
                    results.append({
                        "title": title,
                        "url": url,
                        "content": snippet,
                        "published": published,
                        "score": score,
                        "backend": "brave",
                    })
        except Exception:
            logger.exception("Failed to normalize brave response")
        return results

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Brave for the given query.

        Args:
            query: Search query text
            max_results: maximum number of results to return

        Returns: A list of normalized results: [{title, url, content, score}]
        """
        if not self.api_key:
            raise BraveSearchError("Brave API key not configured. Set BRAVE_API_KEY in .env")
        try:
            import requests
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
            }
            params = {"q": query, "count": max(1, min(max_results, 20))}
            resp = requests.get(self.BASE_URL, headers=headers, params=params, timeout=self.timeout_s)
            resp.raise_for_status()
            data = resp.json() or {}
            return self._normalize(data)[:max_results]
        except Exception as e:
            logger.warning("Brave search failed: %s", e)
            # Fail closed with empty results so aggregator can fallback
            return []

