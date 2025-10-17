from __future__ import annotations

import os
import time
from typing import Any, Dict

from fastapi import APIRouter

from ..core.config import get_config
from ..core.database import get_database

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/live")
async def liveness() -> Dict[str, Any]:
    return {"status": "ok", "ts": time.time()}


@router.get("/ready")
async def readiness() -> Dict[str, Any]:
    started = time.perf_counter()
    checks: Dict[str, Any] = {}
    ok = True

    # DB check
    try:
        _ = get_database()
        checks["database"] = {"status": "ok"}
    except Exception as e:
        ok = False
        checks["database"] = {"status": "error", "error": str(e)}

    # Redis (optional)
    try:
        if os.getenv("HEALTH_CHECK_REDIS", "false").lower() == "true":
            from ..core.redis_cache import get_redis_client  # type: ignore

            client = get_redis_client()
            pong = client.ping()
            checks["redis"] = {"status": "ok" if pong else "error"}
            ok = ok and bool(pong)
        else:
            checks["redis"] = {"status": "skipped"}
    except Exception as e:
        ok = False
        checks["redis"] = {"status": "error", "error": str(e)}

    # Circuit breakers snapshot (best-effort)
    try:
        from ..core.circuit_health import snapshot  # type: ignore

        snap = snapshot()
        checks["circuit_breakers"] = {"count": len(snap), "open": sum(1 for v in snap.values() if v.get("open"))}
    except Exception:
        checks["circuit_breakers"] = {"status": "unknown"}

    duration_ms = int((time.perf_counter() - started) * 1000)
    return {"status": "ok" if ok else "degraded", "duration_ms": duration_ms, "checks": checks}

