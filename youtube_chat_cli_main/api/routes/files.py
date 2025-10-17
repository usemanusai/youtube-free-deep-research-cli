"""File endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload")
async def upload():
    """File upload endpoint."""
    return {"message": "Upload endpoint"}


__all__ = ["router"]

