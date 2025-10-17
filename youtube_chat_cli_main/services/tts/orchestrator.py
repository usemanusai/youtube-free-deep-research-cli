"""TTS orchestration service."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in tts_service.py
from ...tts_service import TTSService as TTSOrchestrator, get_tts_service

__all__ = ["TTSOrchestrator", "get_tts_service"]

