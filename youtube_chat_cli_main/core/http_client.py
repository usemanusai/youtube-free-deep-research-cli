"""
Centralized HTTPX client(s) with sane defaults: timeouts, retries, and rate limiting.

Usage (sync):
    from youtube_chat_cli_main.core.http_client import httpx_client, request_with_retry
    r = request_with_retry("GET", "https://example.com")

Usage (async):
    from youtube_chat_cli_main.core.http_client import get_async_client
    async with get_async_client() as client:
        resp = await client.get("https://example.com", timeout=DEFAULT_TIMEOUT)
"""
from __future__ import annotations

import threading
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

try:
    from aiolimiter import AsyncLimiter  # type: ignore
except Exception:  # optional at runtime
    AsyncLimiter = None  # type: ignore

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=10.0, read=10.0, write=10.0)
DEFAULT_HEADERS = {
    "User-Agent": "JAEGIS-NexusSync/1.0 (+https://github.com/usemanusai/youtube-free-deep-research-cli)"
}

# Shared sync client (thread-safe lazy singleton)
_sync_client: Optional[httpx.Client] = None
_sync_lock = threading.Lock()


def httpx_client() -> httpx.Client:
    global _sync_client
    if _sync_client is None:
        with _sync_lock:
            if _sync_client is None:
                _sync_client = httpx.Client(timeout=DEFAULT_TIMEOUT, headers=DEFAULT_HEADERS)
    return _sync_client


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.RemoteProtocolError)),
)
def request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    """Synchronous request helper with retries and timeouts.
    Respects provided timeout, else applies DEFAULT_TIMEOUT.
    """
    client = httpx_client()
    if "timeout" not in kwargs:
        kwargs["timeout"] = DEFAULT_TIMEOUT
    return client.request(method, url, **kwargs)


def reset_httpx_client() -> None:
    """Reset the shared sync client (useful for tests to re-create under respx)."""
    global _sync_client
    with _sync_lock:
        if _sync_client is not None:
            try:
                _sync_client.close()
            except Exception:
                pass
            _sync_client = None



# Async client factory with optional rate limiting
async def get_async_client(rate_limit_per_sec: Optional[float] = None) -> httpx.AsyncClient:
    headers = DEFAULT_HEADERS.copy()
    client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, headers=headers)

    if rate_limit_per_sec and AsyncLimiter is not None:
        limiter = AsyncLimiter(rate_limit_per_sec, time_period=1)

        class _RateLimitedClient(httpx.AsyncClient):
            async def request(self, *args, **kwargs):  # type: ignore[override]
                async with limiter:
                    return await super().request(*args, **kwargs)

        return _RateLimitedClient(timeout=DEFAULT_TIMEOUT, headers=headers)

    return client

