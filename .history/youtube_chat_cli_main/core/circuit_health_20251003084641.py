"""
Global circuit breaker registry and helpers.
"""
from __future__ import annotations

from typing import Dict
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
    for k, b in _breakers.items():
        st = b.state()
        out[k] = {
            "open": st["open"],
            "opened_until": st["opened_until"],
            "failures": st["failures"],
        }
    return out

