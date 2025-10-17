"""
JAEGIS NexusSync - Transcription Service

Audio/Video transcription wrapper. Prefers local, free backends when available.

Backends (automatic selection in this order):
1) faster-whisper (GPU/CPU) - fast, local
2) openai-whisper (pip install whisper) - local

Notes:
- Most backends depend on ffmpeg being installed and discoverable in PATH.
- This service only accepts an audio file path. For videos, extract audio first.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionConfig:
    model: str = os.getenv("WHISPER_MODEL", "base")  # base, small, medium, large-v3, etc.
    device: Optional[str] = os.getenv("WHISPER_DEVICE")  # cpu or cuda (auto if None)
    compute_type: Optional[str] = os.getenv("WHISPER_COMPUTE_TYPE")  # e.g., float16, int8


class TranscriptionBackend:
    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError


class FasterWhisperBackend(TranscriptionBackend):
    def __init__(self, cfg: TranscriptionConfig):
        from faster_whisper import WhisperModel  # type: ignore
        kwargs = {}
        if cfg.device:
            kwargs["device"] = cfg.device
        if cfg.compute_type:
            kwargs["compute_type"] = cfg.compute_type
        self.model = WhisperModel(cfg.model, **kwargs)

    def transcribe(self, audio_path: str) -> str:
        logger.info(f"Transcribing with faster-whisper: {audio_path}")
        segments, info = self.model.transcribe(audio_path)
        texts = [seg.text for seg in segments]
        return "\n".join(texts).strip()


class OpenAIWhisperBackend(TranscriptionBackend):
    def __init__(self, cfg: TranscriptionConfig):
        import whisper  # type: ignore
        self.model = whisper.load_model(cfg.model)

    def transcribe(self, audio_path: str) -> str:
        logger.info(f"Transcribing with openai-whisper: {audio_path}")
        import whisper  # type: ignore
        result = self.model.transcribe(audio_path)
        text = result.get("text", "").strip()
        return text


class TranscriptionService:
    def __init__(self, cfg: Optional[TranscriptionConfig] = None):
        self.cfg = cfg or TranscriptionConfig()
        self.backend = self._select_backend()

    def _select_backend(self) -> TranscriptionBackend:
        # Try faster-whisper first
        try:
            import importlib
            importlib.import_module("faster_whisper")
            logger.info("✅ Using faster-whisper backend")
            return FasterWhisperBackend(self.cfg)
        except Exception as e:
            logger.info(f"faster-whisper not available: {e}")
        # Fallback to openai-whisper
        try:
            import importlib
            importlib.import_module("whisper")
            logger.info("✅ Using openai-whisper backend")
            return OpenAIWhisperBackend(self.cfg)
        except Exception as e:
            logger.info(f"openai-whisper not available: {e}")
        # None available
        raise RuntimeError(
            "No transcription backend available. Install 'faster-whisper' or 'whisper', and ensure ffmpeg is installed."
        )

    def transcribe(self, audio_path: str) -> str:
        return self.backend.transcribe(audio_path)


_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service

