"""TTS bridge client for Python 3.11 subprocess."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in tts_bridge_client.py
from ...tts_bridge_client import TTSBridgeClient

__all__ = ["TTSBridgeClient"]

