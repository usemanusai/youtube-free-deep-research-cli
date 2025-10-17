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
from urllib.parse import urlsplit, urlunsplit
import urllib.robotparser as robotparser

logger = logging.getLogger(__name__)


def _html_to_text(html: str) -> str:
    # Very small, dependency-free conversion to text
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class WebScraperService:
    """Headless web scraper interface (Playwright optional with graceful fallback)."""

    def _fetch_playwright(self, url: str, timeout_s: int) -> str:
        """Fetch page content using Playwright with retries, stealth, and idle wait.
        Returns HTML on success, or empty string on failure. Never raises.
        """
        try:
            from ..core.config import get_config
            cfg = get_config()
            from playwright.sync_api import sync_playwright  # type: ignore
            import time, os, random

            attempts = max(1, int(getattr(cfg, 'scraper_retry_attempts', 3)))
            wait_idle = bool(getattr(cfg, 'scraper_wait_for_idle', True))
            stealth = bool(getattr(cfg, 'scraper_playwright_stealth', True))
            screenshot_on_error = bool(getattr(cfg, 'scraper_screenshot_on_error', True))

            # Simple UA rotation pool
            ua_pool = [
                self.user_agent,
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/126.0",
            ]

            backoff = 1.0
            last_error = None
            with sync_playwright() as p:
                for i in range(attempts):
                    try:
                        ua = random.choice(ua_pool) if stealth else self.user_agent
                        launch_args = ["--disable-blink-features=AutomationControlled"] if stealth else []
                        proxy = getattr(cfg, 'scraper_proxy_url', None)
                        browser = p.chromium.launch(headless=True, args=launch_args, proxy={"server": proxy} if proxy else None)
                        vp = self._viewport_from_cfg(cfg) if stealth else None
                        context = browser.new_context(
                            user_agent=ua,
                            viewport=vp,
                            locale="en-US"
                        )
                        page = context.new_page()
                        page.set_default_timeout(timeout_s * 1000)
                        self._setup_request_blocking(page, cfg)
                        self._inject_identity(context, page, cfg, url)

                        # Randomized small mouse movement and delay (stealth-ish)
                        if stealth:
                            try:
                                page.mouse.move(random.randint(50, 200), random.randint(50, 200))
                                time.sleep(random.uniform(0.1, 0.3))
                            except Exception:
                                pass

                        page.goto(url, wait_until="domcontentloaded")
                        if wait_idle:
                            try:
                                page.wait_for_load_state("networkidle", timeout=timeout_s * 1000)
                            except Exception:
                                # continue; network idle not always reliable
                                pass

                        # Small post-load delay
                        time.sleep(0.5)

                        html = page.content() or ""
                        browser.close()
                        return html
                    except Exception as e:
                        last_error = e
                        try:
                            if screenshot_on_error:
                                os.makedirs("./logs/scraper_errors", exist_ok=True)
                                safe = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:80]
                                fname = f"./logs/scraper_errors/{int(time.time())}_{i}_{safe}.png"
                                try:
                                    page.screenshot(path=fname, full_page=True)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        try:
                            browser.close()
                        except Exception:
                            pass
                        time.sleep(backoff)
                        backoff *= 2
                # Exhausted attempts
                if last_error:
                    logger.warning("Playwright fetch failed for %s after %d attempts: %s", url, attempts, last_error)
            return ""
        except Exception:
            # Import or global failure
            return ""


    def _viewport_from_cfg(self, cfg) -> dict:
        vp = str(getattr(cfg, 'scraper_viewport', 'desktop'))
        presets = {
            'desktop': {"width": 1920, "height": 1080},
            'tablet': {"width": 834, "height": 1112},
            'mobile': {"width": 390, "height": 844},
        }
        if 'x' in vp.lower():
            try:
                w, h = vp.lower().split('x')
                return {"width": int(w), "height": int(h)}
            except Exception:
                return presets['desktop']
        return presets.get(vp, presets['desktop'])

    def _setup_request_blocking(self, page, cfg):
        block = set([x.lower() for x in getattr(cfg, 'scraper_block_resources', [])])
        if not block:
            return
        def handler(route):
            req = route.request
            url = req.url.lower()
            rtype = req.resource_type.lower() if hasattr(req, 'resource_type') else ''
            if rtype in block or any(k in url for k in block):
                return route.abort()
            return route.continue_()
        try:
            page.route("**/*", handler)
        except Exception:
            pass

    def _inject_identity(self, context, page, cfg, url: str | None = None):  # url reserved for future use
        # Cookies
        try:
            cookies = getattr(cfg, 'scraper_cookies_json', [])
            if cookies:
                context.add_cookies(cookies)
        except Exception:
            pass
        # Local storage
        try:
            ls = getattr(cfg, 'scraper_local_storage_json', {})
            if ls:
                for k, v in ls.items():
                    page.add_init_script(f"window.localStorage.setItem('{k}', '{str(v)}');")
        except Exception:
            pass
        # Canvas spoof
        try:
            if getattr(cfg, 'scraper_canvas_spoof', True):
                page.add_init_script(
                    """
                    const getContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(type) {
                        const ctx = getContext.apply(this, arguments);
                        if (type === '2d') {
                          const toDataURL = ctx.canvas.toDataURL.bind(ctx.canvas);
                          ctx.canvas.toDataURL = function() {
                            return toDataURL().replace(/.$/, Math.random().toString(36).slice(2,3));
                          }
                        }
                        return ctx;
                    };
                    """
                )
        except Exception:
            pass

    def _apply_site_waits(self, page, url: str, cfg, timeout_s: int):
        import time
        try:
            from urllib.parse import urlsplit
            host = urlsplit(url).netloc
            waits = getattr(cfg, 'scraper_wait_selectors', {})
            sels = waits.get(host) or waits.get('*')
            if not sels:
                return
            if isinstance(sels, str):
                sels = [sels]
            for sel in sels[:5]:
                try:
                    page.wait_for_selector(sel, timeout=timeout_s * 1000)
                except Exception:
                    time.sleep(0.2)
        except Exception:
            pass

    def __init__(self, rate_limit_qps: float = None):
        from ..core.config import get_config
        cfg = get_config()
        logger.info("WebScraperService initialized")
        self.rate_limit_qps = rate_limit_qps if rate_limit_qps is not None else cfg.scraper_rate_limit_qps
        self.user_agent = cfg.scraper_user_agent
        self.respect_robots = cfg.scraper_respect_robots
        self._last_fetch_ts = 0.0

    def _rate_limit(self):
        try:
            import time
            min_interval = 1.0 / max(self.rate_limit_qps, 0.0001)
            delta = time.time() - self._last_fetch_ts
            if delta < min_interval:
                time.sleep(min_interval - delta)
            self._last_fetch_ts = time.time()
        except Exception:
            pass

    def _extract_links_same_host(self, html: str, base_url: str, limit: int = 10) -> List[str]:
        try:
            parsed = urlsplit(base_url)
            host = f"{parsed.scheme}://{parsed.netloc}"
            links = []
            for m in re.finditer(r"href=\"([^\"]+)\"", html, flags=re.I):
                href = m.group(1)
                if href.startswith("/"):
                    href_abs = host + href
                elif href.startswith("http://") or href.startswith("https://"):
                    href_abs = href
                else:
                    continue
                if urlsplit(href_abs).netloc == parsed.netloc and href_abs not in links:
                    links.append(href_abs)
                if len(links) >= limit:
                    break
            return links
        except Exception:
            return []

    def scrape(self, url: str, depth: int = 1, max_pages: int = 50, timeout_s: int = 60) -> Dict[str, Any]:
        """Scrape a URL with limited recursion (depth<=1 supported).

        Returns a dict: {root_url, pages: [{url, title, text, status, fetched_at}], errors: []}
        """
        logger.info("[WebScraperService] scrape -> %s", url)
        pages: List[Dict[str, Any]] = []
        errors: List[str] = []
        try:
            # robots.txt respect (best-effort)
            ua = self.user_agent
            try:
                parsed = urlsplit(url)
                robots_url = urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))
                rp = robotparser.RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                if self.respect_robots and hasattr(rp, "can_fetch") and not rp.can_fetch(ua, url):
                    errors.append(f"Disallowed by robots.txt: {url}")
                    return {
                        "root_url": url,
                        "pages": pages,
                        "errors": errors,
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }
            except Exception:
                # If robots cannot be fetched/parsed, proceed
                pass

            # Try Playwright first if available and headless requested
            html_main = ""
            if self.respect_robots:
                # Already checked robots.txt above
                pass
            # Fetch main page
            self._rate_limit()
            html_main = self._fetch_playwright(url, timeout_s) or html_main
            if not html_main:
                resp = requests.get(url, timeout=timeout_s, headers={"User-Agent": ua})
                status = resp.status_code
                text = _html_to_text(resp.text or "") if resp.ok else ""
            else:
                status = 200
                text = _html_to_text(html_main)
            pages.append({
                "url": url,
                "title": "",
                "text": text,
                "status": status,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

            # Shallow recursion: fetch a few same-host links if depth>=1
            if depth and depth > 1 and (html_main or status == 200):
                base_html = html_main if html_main else (resp.text if 'resp' in locals() and hasattr(resp, 'text') else "")
                links = self._extract_links_same_host(base_html, url, limit=min(10, max_pages))
                for link in links[: max_pages - 1]:
                    try:
                        self._rate_limit()
                        html2 = self._fetch_playwright(link, timeout_s)
                        if not html2:
                            r2 = requests.get(link, timeout=timeout_s, headers={"User-Agent": ua})
                            text2 = _html_to_text(r2.text or "") if r2.ok else ""
                            status2 = r2.status_code
                        else:
                            text2 = _html_to_text(html2)
                            status2 = 200
                        pages.append({
                            "url": link,
                            "title": "",
                            "text": text2,
                            "status": status2,
                            "fetched_at": datetime.now(timezone.utc).isoformat(),
                        })
                    except Exception as sub_e:
                        errors.append(f"{link}: {sub_e}")
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

