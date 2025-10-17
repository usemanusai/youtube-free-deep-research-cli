"""Configuration endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/")
async def get_config():
    """Get configuration."""
    return {"message": "Config endpoint"}


__all__ = ["router"]

