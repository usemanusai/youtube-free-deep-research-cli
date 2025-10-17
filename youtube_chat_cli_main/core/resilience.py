"""
Resilience helpers: retry with backoff and a simple circuit breaker.
"""
from __future__ import annotations

import time
import threading
from typing import Callable, Type, Any, Iterable

class RetryError(Exception):
    pass


def retry_with_backoff(
    exceptions: Iterable[Type[BaseException]] = (Exception,),
    max_attempts: int = 3,
    initial_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: float = 0.1,
):
    """Decorator to retry the wrapped function with exponential backoff.

    Example:
        @retry_with_backoff((TimeoutError,), max_attempts=5)
        def call_api(...): ...
    """
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs):
            delay = float(initial_delay)
            attempt = 0
            while True:
                attempt += 1
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:  # type: ignore
                    if attempt >= max_attempts:
                        raise RetryError(f"{fn.__name__} failed after {attempt} attempts: {e}")
                    # jittered backoff
                    time.sleep(min(max_delay, delay))
                    delay = min(max_delay, delay * 2.0 + jitter)
        return wrapper
    return decorator


class CircuitBreaker:
    """Very small in-process circuit breaker.

    - When error rate crosses threshold within a window, the breaker opens for `cooldown_s`.
    - While open, calls raise RuntimeError immediately.
    """
    def __init__(self, failures_threshold: int = 5, window_s: float = 60.0, cooldown_s: float = 30.0):
        self.failures_threshold = failures_threshold
        self.window_s = window_s
        self.cooldown_s = cooldown_s
        self._lock = threading.Lock()
        self._failures: list[float] = []
        self._opened_until: float = 0.0

    def _prune(self):
        cutoff = time.time() - self.window_s
        self._failures = [t for t in self._failures if t >= cutoff]

    def allow(self) -> bool:
        with self._lock:
            now = time.time()
            if self._opened_until > now:
                return False
            self._prune()
            return True

    def on_success(self):
        with self._lock:
            self._prune()
            # on success, nothing else needed

    def on_failure(self):
        with self._lock:
            now = time.time()
            self._failures.append(now)
            self._prune()
            if len(self._failures) >= self.failures_threshold:
                self._opened_until = now + self.cooldown_s

    def guarded(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs):
            if not self.allow():
                raise RuntimeError("Circuit open; skipping call")
            try:
                res = fn(*args, **kwargs)
                self.on_success()
                return res
            except Exception:
                self.on_failure()
                raise
        return wrapper

