"""
Text-to-Speech (TTS) services.

Provides support for multiple TTS libraries:
- Kokoro TTS
- OpenVoice v2
- MeloTTS
- Chatterbox TTS
- Edge TTS
- Google TTS
"""

from .service import TTSService, get_tts_service
from .config_manager import TTSConfigManager, get_tts_config_manager

__all__ = ['TTSService', 'get_tts_service', 'TTSConfigManager', 'get_tts_config_manager']
