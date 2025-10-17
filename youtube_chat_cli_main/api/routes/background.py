"""Background service endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/background", tags=["background"])


@router.post("/start")
async def start():
    """Start background service."""
    return {"message": "Start endpoint"}


__all__ = ["router"]

