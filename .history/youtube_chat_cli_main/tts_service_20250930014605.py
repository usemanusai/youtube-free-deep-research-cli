""""
TTS service module for generating audio from text using gTTS (Google Text-to-Speech).
"""

import os
from typing import Optional

import logging
logger = logging.getLogger(__name__)

try:
    import asyncio
    from edge_tts import Communicate, VoicesManager
    EDGE_TTS_AVAILABLE = True
except ImportError:
    logger.warning("edge-tts not available, falling back to gTTS")
    EDGE_TTS_AVAILABLE = False

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
                      voice: str = "en", audio_format: str = "mp3", slow: bool = False) -> str:
        """Generate audio from text using gTTS.

        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
            voice: Language code (e.g., 'en', 'es') or tuple (lang, slow)
            audio_format: Output audio format (will be converted to mp3/wav)
            slow: Whether to use slow speech for different voice articulation

        Returns:
            Path to the generated audio file

        Raises:
            APIError: If TTS generation fails
        """
        if not self.gtts_available:
            raise APIError("gTTS not available - please install with: pip install gtts")

        logger.info(f"Generating TTS audio for text ({len(text)} characters) using gTTS")

        # Handle voice parameter
        if isinstance(voice, tuple):
            lang, slow_param = voice
            slow = slow_param
        else:
            lang = voice

        try:
            # Create gTTS object with slow parameter for voice variation
            tts = gTTS(text=text, lang=lang, slow=slow)

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
        """Generate audio for a podcast script with multiple speakers.

        Args:
            podcast_script: The podcast script text with speaker indicators
            output_file: Optional output file path

        Returns:
            Path to the generated audio file
        """
        if output_file is None:
            output_file = "podcast_overview.wav"

        logger.info("Generating multi-speaker podcast audio with gTTS")

        try:
            # Parse the script and generate audio for each speaker segment
            audio_segments = self._generate_podcast_segments(podcast_script)

            if len(audio_segments) == 1:
                # Only one segment, use regular generation
                return self.generate_audio(
                    text=podcast_script,
                    output_file=output_file,
                    voice="en",
                    audio_format="mp3"
                )
            else:
                # Multiple segments, combine them
                combined_audio = self._combine_audio_segments(audio_segments, output_file)
                return combined_audio

        except APIError as e:
            logger.error(f"gTTS generation failed: {e}")
            raise e

    def _generate_podcast_segments(self, podcast_script: str) -> list:
        """Parse podcast script and generate audio segments for different speakers.

        Args:
            podcast_script: The full podcast script text

        Returns:
            List of tuples (speaker_name, voice_code, text_segment, audio_file_path)
        """
        import re
        import tempfile

        segments = []

        # Split script by speaker indicators - simple and reliable pattern
        # Look for **Speaker:** followed by text until next **Speaker:** or end
        pattern = r'\*\*([^*]+?):\*\*\s*(.+?)(?=\*\*[^*]+?:\*\*|Generated on|$|###)'
        matches = re.findall(pattern, podcast_script, re.MULTILINE | re.DOTALL)

        # Debug logging
        logger.info(f"Script parse attempt: found {len(matches)} matches")
        if matches:
            logger.info(f"Sample matches: {matches[:3]}")

        if not matches:
            # Fallback: single speaker mode
            logger.info("No speaker indicators found, using single speaker mode")
            return [("single", "en", podcast_script)]

        logger.info(f"Found {len(matches)} speaker segments")

        # Define voice mapping for speakers - using gTTS slow parameter for different voices
        voice_map = {
            'host': ('en', False),   # Standard English, normal speed
            'expert': ('en', True),  # English, slow speed (different articulation)
            'h': ('en', False),      # Short forms
            'e': ('en', True),
            'alex': ('en', True),
            'chen': ('en', True)
        }

        temp_files = []

        try:
            for speaker_info, text in matches:
                speaker_clean = speaker_info.lower().strip()

                # Determine voice based on speaker name
                voice_params = ('en', False)  # default: normal English, normal speed
                for key, v in voice_map.items():
                    if key in speaker_clean:
                        voice_params = v
                        break

                # Generate temp file for this segment
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_files.append(temp_file.name)

                # Generate audio for this segment sequentially to avoid file locking
                try:
                    temp_wav_file = temp_file.name
                    temp_file.close()  # Close the temp file handle first

                    self.generate_audio(text.strip(), temp_wav_file, voice=voice_params[0], slow=voice_params[1])
                    segments.append((speaker_info, voice_params, text.strip(), temp_wav_file))
                except Exception as e:
                    logger.warning(f"Failed to generate audio for speaker {speaker_info}: {e}")
                    # Clean up failed temp file
                    if os.path.exists(temp_file.name):
                        os.remove(temp_file.name)
                    # Skip this segment but continue
                    continue

        except Exception as e:
            logger.error(f"Error generating podcast segments: {e}")
            # Clean up temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            raise e

        logger.info(f"Generated {len(segments)} audio segments")
        return segments

    def _combine_audio_segments(self, segments: list, output_file: str) -> str:
        """Combine multiple audio segments into a single podcast file.

        Args:
            segments: List of tuples (speaker_name, voice_code, text, audio_file_path)
            output_file: Final output file path

        Returns:
            Path to the combined audio file
        """
        if not segments:
            raise APIError("No audio segments to combine")

        logger.info(f"Combining {len(segments)} audio segments")

        try:
            from pydub import AudioSegment
            pydub_available = True
        except ImportError:
            pydub_available = False
            logger.warning("pydub not available, using simple file concatenation")

        if pydub_available:
            # Use pydub for proper audio concatenation with pauses
            combined_audio = None

            for segment in segments:
                _, _, _, audio_file = segment

                if not os.path.exists(audio_file):
                    logger.warning(f"Audio file missing: {audio_file}")
                    continue

                try:
                    segment_audio = AudioSegment.from_wav(audio_file)

                    if combined_audio is None:
                        combined_audio = segment_audio
                    else:
                        # Add a 300ms pause between speakers to make conversation natural
                        pause = AudioSegment.silent(duration=300)
                        combined_audio = combined_audio + pause + segment_audio

                except Exception as e:
                    logger.warning(f"Failed to load segment {audio_file}: {e}")
                    continue

            if combined_audio is None:
                raise APIError("Failed to combine any audio segments")

            # Export the combined audio
            combined_audio.export(output_file, format="wav")

        else:
            # Fallback: simple file concatenation of MP3 files
            logger.info("Using simple MP3 concatenation (pauses not added)")

            with open(output_file, 'wb') as outfile:
                for segment in segments:
                    _, _, _, audio_file = segment

                    if not os.path.exists(audio_file):
                        logger.warning(f"Audio file missing: {audio_file}")
                        continue

                    try:
                        # Read MP3 file as binary
                        if audio_file.endswith('.wav'):
                            # Skip .wav files if pydub wasn't available, look for .mp3
                            mp3_file = audio_file.replace('.wav', '.mp3')
                            if os.path.exists(mp3_file):
                                with open(mp3_file, 'rb') as infile:
                                    outfile.write(infile.read())
                            else:
                                with open(audio_file, 'rb') as infile:
                                    outfile.write(infile.read())
                        else:
                            with open(audio_file, 'rb') as infile:
                                outfile.write(infile.read())
                    except Exception as e:
                        logger.warning(f"Failed to read segment {audio_file}: {e}")
                        continue

        # Clean up temp files
        for segment in segments:
            _, _, _, audio_file = segment
            if os.path.exists(audio_file):
                os.remove(audio_file)
            # Also clean up any .mp3 files left behind
            mp3_file = audio_file.replace('.wav', '.mp3')
            if os.path.exists(mp3_file):
                os.remove(mp3_file)

        file_size = os.path.getsize(output_file)
        logger.info(f"Podcast combined successfully: {output_file} ({file_size} bytes)")

        return output_file

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
