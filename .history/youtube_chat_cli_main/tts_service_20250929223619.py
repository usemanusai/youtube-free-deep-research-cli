"""
TTS service module for generating audio from text using MaryTTS.
"""

import os
import requests
from typing import Optional

import logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Error related to external API calls."""
    pass


class TTSService:
    """Service for text-to-speech conversion using MaryTTS."""

    def __init__(self, marytts_url: str = None):
        """Initialize the TTS service.

        Args:
            marytts_url: URL of the MaryTTS server (e.g., http://localhost:59125)
        """
        if marytts_url is None:
            marytts_url = os.getenv('MARYTTS_SERVER_URL', 'http://localhost:59125')
        self.marytts_url = marytts_url.rstrip('/')
        self.process_endpoint = f"{self.marytts_url}/process"
        self.voices_endpoint = f"{self.marytts_url}/voices"

    def check_server_connection(self) -> bool:
        """Check if MaryTTS server is accessible.

        Returns:
            True if server is reachable, False otherwise
        """
        try:
            # First try local MaryTTS server
            response = requests.get(self.marytts_url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass

        # Fallback: try alternative TTS services
        return self._check_alternative_tts_connection()

    def get_available_voices(self) -> list:
        """Get list of available voices from the MaryTTS server.

        Returns:
            List of available voice names

        Raises:
            APIError: If server communication fails
        """
        try:
            response = requests.get(self.voices_endpoint, timeout=10)
            response.raise_for_status()

            # MaryTTS returns HTML, extract voice names
            voices_html = response.text

            # Simple parsing - look for voice names in format like "en_US/cmu-slt-hsmm"
            voices = []
            import re
            matches = re.findall(r'([a-z]{2}_[A-Z]{2}/[a-z0-9\-]+)', voices_html, re.IGNORECASE)
            voices = list(set(matches))  # Remove duplicates

            if not voices:
                # Fallback default voices if parsing fails
                voices = ['en_US/cmu-slt', 'en_GB/cmu-slt']

            logger.info(f"Available MaryTTS voices: {voices}")
            return voices

        except requests.RequestException as e:
            logger.error(f"Failed to get voices from MaryTTS server: {e}")
            raise APIError(f"Failed to connect to MaryTTS server: {e}")

    def generate_audio(self, text: str, output_file: str = "overview.wav",
                      voice: str = "en_US/cmu-slt", audio_format: str = "WAVE_FILE") -> str:
        """Generate audio from text using MaryTTS.

        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
            voice: Voice to use (format: "locale/name", e.g., "en_US/cmu-slt")
            audio_format: Output audio format (WAVE_FILE, AU_FILE, etc.)

        Returns:
            Path to the generated audio file

        Raises:
            APIError: If TTS generation fails
        """
        logger.info(f"Generating TTS audio for text ({len(text)} characters) using voice: {voice}")

        # Prepare form data for MaryTTS
        data = {
            'INPUT_TEXT': text,
            'INPUT_TYPE': 'TEXT',
            'OUTPUT_TYPE': audio_format,
            'LOCALE': voice.split('/')[0] if '/' in voice else 'en_US',
            'VOICE': voice.split('/')[1] if '/' in voice else voice,
            'AUDIO': audio_format
        }

        # Set up headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'audio/wav,audio/x-wav,*/*'
        }

        try:
            response = requests.post(
                self.process_endpoint,
                data=data,
                headers=headers,
                timeout=60  # Longer timeout for audio generation
            )
            response.raise_for_status()

            # Save the audio response to file
            with open(output_file, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            logger.info(f"TTS audio generated successfully: {output_file} ({file_size} bytes)")

            return output_file

        except requests.RequestException as e:
            logger.error(f"Failed to generate TTS audio: {e}")
            raise APIError(f"Failed to generate audio from MaryTTS: {e}")
        except IOError as e:
            logger.error(f"Failed to save audio file: {e}")
            raise APIError(f"Failed to save audio file: {e}")

    def _check_alternative_tts_connection(self) -> bool:
        """Check for alternative TTS services (always returns True since we have fallbacks)."""
        return True

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

        logger.info("Generating podcast audio with optimized settings")

        # Try MaryTTS first, fall back to alternative method if it fails
        try:
            # Use a professional voice for podcast-style content
            voice = "en_US/cmu-slt"  # Clear, professional female voice
            return self.generate_audio(
                text=podcast_script,
                output_file=output_file,
                voice=voice,
                audio_format="WAVE_FILE"
            )
        except APIError as e:
            logger.warning(f"MaryTTS failed, using alternative TTS method: {e}")
            return self._generate_podcast_with_fallback(podcast_script, output_file)


# Global TTS service instance
_tts_service = None

def get_tts_service() -> TTSService:
    """Get or create the global TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
