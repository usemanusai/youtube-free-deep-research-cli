"""Search endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/")
async def search():
    """Search endpoint."""
    return {"message": "Search endpoint"}


__all__ = ["router"]

