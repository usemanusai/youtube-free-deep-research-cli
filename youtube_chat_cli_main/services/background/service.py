"""Background service."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/background_service.py
from ..background_service import BackgroundService, get_background_service

__all__ = ["BackgroundService", "get_background_service"]

