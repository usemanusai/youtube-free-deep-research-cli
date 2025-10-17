"""Session manager storage."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in session_manager.py
from ...session_manager import SessionManager, get_session_manager

__all__ = ["SessionManager", "get_session_manager"]

