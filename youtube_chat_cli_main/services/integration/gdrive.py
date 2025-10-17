"""Google Drive integration."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/gdrive_service.py
from ..gdrive_service import GoogleDriveService, get_gdrive_watcher

__all__ = ["GoogleDriveService", "get_gdrive_watcher"]

