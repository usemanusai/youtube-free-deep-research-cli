"""
Headless Web Scraper Service (initial functionality)

Provides a production-ready interface for scraping pages. This version includes
an HTTP-based fallback (requests + simple HTML to text) and stubs for an optional
Playwright path that can be enabled later without changing the interface.
"""
from __future__ import annotations

from typing import Any, Dict, List
import logging
from datetime import datetime, timezone
import re

import requests

logger = logging.getLogger(__name__)


def _html_to_text(html: str) -> str:
    # Very small, dependency-free conversion to text
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class WebScraperService:
    """Headless web scraper interface."""

    def __init__(self):
        logger.info("WebScraperService initialized")

    def scrape(self, url: str, depth: int = 1, max_pages: int = 50, timeout_s: int = 60) -> Dict[str, Any]:
        """Scrape a URL with limited recursion (depth is currently ignored).

        Returns a dict: {root_url, pages: [{url, title, text, status, fetched_at}], errors: []}
        """
        logger.info("[WebScraperService] scrape -> %s", url)
        pages: List[Dict[str, Any]] = []
        errors: List[str] = []
        try:
            resp = requests.get(url, timeout=timeout_s, headers={"User-Agent": "JAEGIS-NexusScraper/1.0"})
            status = resp.status_code
            text = _html_to_text(resp.text or "") if resp.ok else ""
            pages.append({
                "url": url,
                "title": "",
                "text": text,
                "status": status,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            errors.append(f"{url}: {e}")

        return {
            "root_url": url,
            "pages": pages,
            "errors": errors,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def scrape_many(self, urls: List[str], depth: int = 1, max_pages: int = 50, timeout_s: int = 60) -> Dict[str, Any]:
        logger.info("[WebScraperService] scrape_many -> %d urls", len(urls))
        all_pages: List[Dict[str, Any]] = []
        errors: List[str] = []
        for u in urls:
            try:
                result = self.scrape(u, depth=depth, max_pages=max_pages, timeout_s=timeout_s)
                all_pages.extend(result.get("pages", []))
            except Exception as e:
                errors.append(f"{u}: {e}")
        return {
            "root_urls": urls,
            "pages": all_pages,
            "errors": errors,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

