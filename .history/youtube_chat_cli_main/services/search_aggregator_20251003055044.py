"""
Web Search Aggregator Service (initial implementation)

Runs multiple search backends (Brave + Legacy Tavily/DDG) in parallel and merges
results. This version keeps Tavily/DDG as a single "legacy" backend via the
existing WebSearchService to preserve backward compatibility, and adds Brave as
an additional backend when configured.

Next steps (tracked in tasks):
- Split Tavily and DuckDuckGo into distinct calls if/when lower-level APIs are exposed
- Add proper score normalization and recency-aware ranking
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit

from .web_search_service import get_web_search_service
from .brave_search_service import BraveSearchService, BraveSearchError

logger = logging.getLogger(__name__)


def _norm_url(u: str) -> str:
    try:
        p = urlsplit(u or "")
        return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/")
    except Exception:
        return u or ""


class WebSearchAggregatorService:
    """Aggregates multiple web search backends.

    Backends: "brave", "legacy" (Tavily/DDG via existing WebSearchService)
    """

    def __init__(self, backends: Optional[List[str]] = None):
        # Default order if not provided
        self.backends = backends or ["brave", "legacy"]
        self._legacy = get_web_search_service()  # Tavily or DDG fallback
        try:
            self._brave = BraveSearchService()
        except Exception as e:
            logger.warning("BraveSearchService init failed: %s", e)
            self._brave = None

    def _call_backend(self, name: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        if name == "brave" and self._brave:
            try:
                return self._brave.search(query, max_results)
            except BraveSearchError as e:
                logger.warning("Brave backend unavailable: %s", e)
                return []
            except Exception as e:
                logger.warning("Brave backend error: %s", e)
                return []
        elif name == "legacy":
            try:
                return self._legacy.search(query, max_results)
            except Exception as e:
                logger.warning("Legacy backend error: %s", e)
                return []
        else:
            logger.debug("Unknown backend: %s", name)
            return []

    def search(self, query: str, max_results: int = 10, backends: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search using configured backends in parallel; merge and dedupe results.

        Returns a normalized list of results: [{title, url, content, score}]
        """
        use_backends = backends or self.backends
        tasks = {}
        results: List[Dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=len(use_backends)) as ex:
            for b in use_backends:
                tasks[ex.submit(self._call_backend, b, query, max_results)] = b
            for fut in as_completed(tasks):
                backend = tasks[fut]
                try:
                    chunk = fut.result() or []
                    logger.info("Backend %s returned %d results", backend, len(chunk))
                    # annotate with backend for ranking
                    for r in chunk:
                        r.setdefault("backend", backend)
                    results.extend(chunk)
                except Exception as e:
                    logger.warning("Backend %s failed: %s", backend, e)

        # Deduplicate by normalized URL
        seen = set()
        deduped: List[Dict[str, Any]] = []
        for r in results:
            url = _norm_url(r.get("url", ""))
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(r)

        # Ranking: backend weight + (optional) recency bonus if 'published' is ISO date
        weight = {"brave": 0.55, "legacy": 0.45}
        def score_of(item: Dict[str, Any]) -> float:
            base = float(item.get("score", 1.0))
            w = weight.get(item.get("backend", "legacy"), 0.45)
            bonus = 0.0
            dt_str = (item.get("published") or item.get("date") or "").strip()
            if dt_str:
                try:
                    from datetime import datetime, timezone
                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                    age_days = max(0.0, (datetime.now(timezone.utc) - dt).days)
                    bonus = max(0.0, 1.0 - min(age_days, 365.0)/365.0) * 0.1
                except Exception:
                    bonus = 0.0
            return base * w + bonus

        deduped.sort(key=score_of, reverse=True)

        # Truncate to requested max_results overall
        return deduped[:max_results]

    def format_results_for_context(self, results: List[Dict[str, Any]], max_length: int = 2000) -> str:
        # Reuse legacy formatter for now
        return self._legacy.format_results_for_context(results, max_length=max_length)

