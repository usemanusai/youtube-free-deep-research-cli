"""
Global circuit breaker registry and helpers.
"""
from __future__ import annotations

from typing import Dict
import time
from .resilience import CircuitBreaker


_breakers: Dict[str, CircuitBreaker] = {
    "llm": CircuitBreaker(failures_threshold=5, window_s=60.0, cooldown_s=30.0),
    "search": CircuitBreaker(failures_threshold=5, window_s=60.0, cooldown_s=30.0),
    "vector": CircuitBreaker(failures_threshold=5, window_s=60.0, cooldown_s=30.0),
}


def get_breaker(name: str) -> CircuitBreaker:
    return _breakers[name]


def snapshot() -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    now = time.time()
    for k, b in _breakers.items():
        # access internal fields for snapshot (best-effort)
        opened_until = getattr(b, "_opened_until", 0.0)
        failures = len(getattr(b, "_failures", []))
        out[k] = {
            "open": bool(opened_until > now),
            "opened_until": opened_until,
            "failures": failures,
        }
    return out

