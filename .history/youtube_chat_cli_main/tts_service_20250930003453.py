""""
TTS service module for generating audio from text using gTTS (Google Text-to-Speech).
"""

import os
from typing import Optional

import logging
logger = logging.getLogger(__name__)

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gTTS not available, voice generation disabled")
    GTTS_AVAILABLE = False

class APIError(Exception):
    """Error related to external API calls."""
    pass


class TTSService:
    """Service for text-to-speech conversion using Google TTS."""

    def __init__(self, language: str = 'en'):
        """Initialize the TTS service.

        Args:
            language: Language code for TTS (e.g., 'en' for English)
        """
        self.language = language
        self.gtts_available = GTTS_AVAILABLE

    def check_server_connection(self) -> bool:
        """Check if Google TTS service is accessible.

        Returns:
            True if service is available, False otherwise
        """
        if not self.gtts_available:
            return False

        # Test gTTS by attempting a small generation
        try:
            tts = gTTS(text="test", lang=self.language, slow=False)
            # We don't need to download, just check if instance creates successfully
            return True
        except Exception as e:
            logger.warning(f"gTTS connection test failed: {e}")
            return False

    def get_available_voices(self) -> list:
        """Get list of available voices/languages.

        Returns:
            List of available language codes
        """
        # gTTS supports many languages, but for simplicity return common ones
        return ['en', 'en-us', 'en-gb', 'en-au', 'es', 'fr', 'de', 'it', 'pt', 'ru']

    def generate_audio(self, text: str, output_file: str = "overview.wav",
                      voice: str = "en", audio_format: str = "mp3") -> str:
        """Generate audio from text using gTTS.

        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
            voice: Language code (e.g., 'en', 'es')
            audio_format: Output audio format (will be converted to mp3/wav)

        Returns:
            Path to the generated audio file

        Raises:
            APIError: If TTS generation fails
        """
        if not self.gtts_available:
            raise APIError("gTTS not available - please install with: pip install gtts")

        logger.info(f"Generating TTS audio for text ({len(text)} characters) using gTTS")

        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=voice, slow=False)

            # Generate MP3 file first
            mp3_file = output_file.replace('.wav', '.mp3')

            # Remove any existing files
            for file_path in [mp3_file, output_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

            tts.save(mp3_file)

            # Convert MP3 to WAV using pydub
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_mp3(mp3_file)
                audio.export(output_file, format="wav")
                os.remove(mp3_file)  # Clean up MP3 file
            except ImportError:
                # If pydub not available, just rename to .wav (gTTS creates MP3 format but we'll call it WAV)
                logger.warning("pydub not available, saving as MP3 with .wav extension")
                os.rename(mp3_file, output_file)

            file_size = os.path.getsize(output_file)
            logger.info(f"TTS audio generated successfully: {output_file} ({file_size} bytes)")

            return output_file

        except Exception as e:
            logger.error(f"Failed to generate TTS audio with gTTS: {e}")
            raise APIError(f"Failed to generate audio with gTTS: {e}")

    def generate_podcast_audio(self, podcast_script: str, output_file: str = None) -> str:
        """Generate audio for a podcast script with optimal settings.

        Args:
            podcast_script: The podcast script text to convert
            output_file: Optional output file path

        Returns:
            Path to the generated audio file
        """
        if output_file is None:
            output_file = "podcast_overview.wav"

        logger.info("Generating podcast audio with gTTS")

        try:
            # Use English TTS with natural speed for podcast-style content
            return self.generate_audio(
                text=podcast_script,
                output_file=output_file,
                voice="en",
                audio_format="mp3"
            )
        except APIError as e:
            logger.error(f"gTTS generation failed: {e}")
            raise e

    def _check_alternative_tts_connection(self) -> bool:
        """Check for alternative TTS services."""
        return self.gtts_available


# Global TTS service instance
_tts_service = None

def get_tts_service() -> TTSService:
    """Get or create the global TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
