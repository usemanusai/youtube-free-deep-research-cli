"""
Optional Redis cache with graceful fallback to in-memory TTL LRU.
"""
from __future__ import annotations

import json
import time
import threading
from typing import Any, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None


class _InMemoryTTLCache:
    def __init__(self, max_items: int = 2048):
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self._max = max_items

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            exp, val = item
            if exp and exp < time.time():
                self._data.pop(key, None)
                return None
            return val

    def set(self, key: str, value: str, ttl_s: int) -> None:
        with self._lock:
            if len(self._data) >= self._max:
                # simple eviction: pop an arbitrary item
                self._data.pop(next(iter(self._data)), None)
            exp = time.time() + max(1, int(ttl_s)) if ttl_s else 0
            self._data[key] = (exp, value)

    def clear_prefix(self, prefix: str) -> int:
        with self._lock:
            ks = [k for k in self._data if k.startswith(prefix)]
            for k in ks:
                self._data.pop(k, None)
            return len(ks)


class RedisCache:
    def __init__(self, url: str, password: Optional[str], db: int, enabled: bool, default_ttl_s: int = 300):
        self.enabled = bool(enabled and redis)
        self.default_ttl_s = max(1, int(default_ttl_s))
        if self.enabled:
            self._r = redis.Redis.from_url(url=url, password=password, db=db, socket_timeout=2, socket_connect_timeout=2)  # type: ignore
        else:
            self._r = None
        self._mem = _InMemoryTTLCache()

    def healthy(self) -> bool:
        if not self.enabled or not self._r:
            return False
        try:
            return bool(self._r.ping())
        except Exception:
            return False

    def get(self, key: str) -> Optional[str]:
        if self._r:
            try:
                v = self._r.get(key)
                return v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else (v if isinstance(v, str) else None)
            except Exception:
                pass
        return self._mem.get(key)

    def set(self, key: str, value: str, ttl_s: Optional[int] = None) -> None:
        ttl = int(ttl_s or self.default_ttl_s)
        if self._r:
            try:
                self._r.setex(key, ttl, value)
                return
            except Exception:
                pass
        self._mem.set(key, value, ttl)

    def get_json(self, key: str) -> Optional[Any]:
        raw = self.get(key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def set_json(self, key: str, obj: Any, ttl_s: Optional[int] = None) -> None:
        try:
            self.set(key, json.dumps(obj, ensure_ascii=False), ttl_s=ttl_s)
        except Exception:
            # best-effort
            pass

    def clear_prefix(self, prefix: str) -> int:
        """Delete all keys starting with prefix. Returns number removed (approximate for Redis)."""
        n = 0
        if self._r:
            try:
                cursor = 0
                pattern = prefix + "*"
                while True:
                    cursor, keys = self._r.scan(cursor=cursor, match=pattern, count=500)
                    if keys:
                        self._r.delete(*keys)
                        n += len(keys)
                    if cursor == 0:
                        break
            except Exception:
                pass
        # Clear memory cache as well
        n += self._mem.clear_prefix(prefix)
        return n


_cache_singleton: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    global _cache_singleton
    if _cache_singleton is None:
        from .config import get_config
        cfg = get_config()
        _cache_singleton = RedisCache(
            url=getattr(cfg, 'redis_url', 'redis://localhost:6379'),
            password=getattr(cfg, 'redis_password', None),
            db=int(getattr(cfg, 'redis_db', 0)),
            enabled=bool(getattr(cfg, 'redis_enabled', False)),
            default_ttl_s=int(getattr(cfg, 'redis_cache_ttl_seconds', 300)),
        )
    return _cache_singleton

