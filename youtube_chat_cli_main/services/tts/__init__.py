"""TTS Services - Multi-engine text-to-speech with Python 3.11 bridge."""

from .orchestrator import TTSOrchestrator, get_tts_service
from .bridge_client import TTSBridgeClient
from .config import TTSConfig

__all__ = [
    "TTSOrchestrator",
    "get_tts_service",
    "TTSBridgeClient",
    "TTSConfig",
]

