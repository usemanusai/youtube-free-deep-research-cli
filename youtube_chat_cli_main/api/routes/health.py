"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness():
    """Liveness probe."""
    return {"status": "alive"}


@router.get("/ready")
async def readiness():
    """Readiness probe."""
    return {"status": "ready"}


__all__ = ["router"]

