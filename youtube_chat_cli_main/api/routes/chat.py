"""Chat endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/")
async def chat():
    """Chat endpoint."""
    return {"message": "Chat endpoint"}


__all__ = ["router"]

