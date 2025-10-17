"""Error handling middleware."""

from fastapi import Request
from fastapi.responses import JSONResponse


async def error_handler(request: Request, exc: Exception):
    """Handle errors."""
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )


__all__ = ["error_handler"]

