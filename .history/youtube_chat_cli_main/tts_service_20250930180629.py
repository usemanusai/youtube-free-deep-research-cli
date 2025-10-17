""""
TTS service module for generating audio from text using gTTS (Google Text-to-Speech).
"""

import os
from typing import Optional, Dict, Any

import logging
logger = logging.getLogger(__name__)

try:
    import asyncio
    from edge_tts import Communicate, VoicesManager
    EDGE_TTS_AVAILABLE = True
except ImportError:
    logger.warning("edge-tts not available, falling back to gTTS")
    EDGE_TTS_AVAILABLE = False
    asyncio = None

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gTTS not available, voice generation disabled")
    GTTS_AVAILABLE = False

# Chatterbox integration (optional advanced TTS)
CHATTERBOX_AVAILABLE = False
try:
    import torch
    from chatterbox.tts import ChatterboxTTS
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    CHATTERBOX_AVAILABLE = True
    logger.info("Chatterbox TTS available as advanced option")
except ImportError:
    logger.info("Chatterbox TTS not available - optional enhancement")

# pyttsx3 integration (emergency fallback - minimal dependencies, robotic voice)
PYTTSX3_AVAILABLE = False
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    logger.info("pyttsx3 available as emergency fallback (robotic voice quality)")
except ImportError:
    logger.info("pyttsx3 not available")

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
        self.edge_tts_available = EDGE_TTS_AVAILABLE
        self.chatterbox_available = CHATTERBOX_AVAILABLE
        self.pyttsx3_available = PYTTSX3_AVAILABLE

        # Auto-detect device for Chatterbox
        if CHATTERBOX_AVAILABLE:
            try:
                import torch
                self.chatterbox_device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Chatterbox TTS will use device: {self.chatterbox_device}")
            except:
                self.chatterbox_device = "cpu"
            self.chatterbox_model = None  # Lazy load

        # pyttsx3 initialization (lazy load)
        if PYTTSX3_AVAILABLE:
            self.pyttsx3_engine = None
            logger.info("pyttsx3 initialized (engine will be loaded on first use)")

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

    def generate_audio_edge(self, text: str, output_file: str = "overview.wav", voice: str = None) -> str:
        """Generate natural audio using Edge TTS (Microsoft Edge).

        Args:
            text: Text to convert to speech
            output_file: Path to save the wav file
            voice: Edge TTS voice name (e.g., 'en-US-AriaNeural')

        Returns:
            Path to the generated audio file

        Raises:
            APIError: If TTS generation fails
        """
        if not self.edge_tts_available:
            raise APIError("Edge TTS not available")

        logger.info(f"Generating natural TTS audio for text ({len(text)} characters) using Edge TTS")

        try:
            # Create Edge TTS communication object
            communicate = Communicate(text, voice)

            # Remove any existing output file
            if os.path.exists(output_file):
                os.remove(output_file)

            # Generate audio file synchronously
            # Edge TTS is asynchronous, so we need to run it in sync context
            async def generate():
                await communicate.save(output_file)

            # Run the async function
            asyncio.run(generate())

            file_size = os.path.getsize(output_file)
            logger.info(f"Edge TTS audio generated successfully: {output_file} ({file_size} bytes)")

            return output_file

        except Exception as e:
            logger.error(f"Failed to generate Edge TTS audio: {e}")
            raise APIError(f"Failed to generate audio with Edge TTS: {e}")

    def generate_audio_chatterbox(self, text: str, output_file: str = "chatterbox_output.wav",
                                  device: Optional[str] = None, emotion_level: float = 0.5) -> str:
        """Generate audio using Chatterbox TTS (advanced emotion control).

        Args:
            text: Text to convert to speech
            output_file: Path to save the wav file
            device: Device to use ('cuda', 'cpu', or 'auto')
            emotion_level: Emotion intensity (0.0 to 1.0)

        Returns:
            Path to the generated audio file

        Raises:
            APIError: If Chatterbox TTS generation fails
        """
        if not self.chatterbox_available:
            raise APIError("Chatterbox TTS not available")

        logger.info(f"Generating advanced TTS audio for text ({len(text)} characters) using Chatterbox")

        try:
            # Get configuration
            config = get_tts_config_manager().get_library_config("chatterbox")
            use_multilingual = config.get("use_multilingual", False)

            # Resolve device
            device_setting = device or config.get("device", "auto")
            if device_setting == "auto":
                device_setting = self.chatterbox_device
            elif device_setting not in ["cuda", "cpu"]:
                device_setting = self.chatterbox_device

            # Initialize appropriate model
            if use_multilingual:
                # Use multilingual model
                if (self.chatterbox_model is None or
                    not hasattr(self.chatterbox_model, 'generate')):
                    logger.info(f"Initializing Chatterbox Multilingual model on device: {device_setting}")
                    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
                    self.chatterbox_model = ChatterboxMultilingualTTS.from_pretrained(device=device_setting)
                    logger.info("Chatterbox multilingual model initialized successfully")

                # Use language_id from text analysis (simplified - default to English)
                language_id = "en"  # Could be expanded for language detection
                wav_data = self.chatterbox_model.generate(text, language_id=language_id)
            else:
                # Use standard English model
                if (self.chatterbox_model is None or
                    not isinstance(self.chatterbox_model.__class__.__name__, str) or
                    'Multilingual' in self.chatterbox_model.__class__.__name__):
                    logger.info(f"Initializing Chatterbox English model on device: {device_setting}")
                    from chatterbox.tts import ChatterboxTTS
                    self.chatterbox_model = ChatterboxTTS.from_pretrained(device=device_setting)
                    logger.info("Chatterbox English model initialized successfully")

                # Generate with optional emotion control
                if emotion_level != 0.5:
                    wav_data = self.chatterbox_model.generate(text, exaggeration=emotion_level)
                else:
                    wav_data = self.chatterbox_model.generate(text)

            # Save audio file
            if os.path.exists(output_file):
                os.remove(output_file)

            # Chatterbox returns tensor - save with torchaudio
            import torchaudio as ta
            ta.save(output_file, wav_data.unsqueeze(0), self.chatterbox_model.sr)

            file_size = os.path.getsize(output_file)
            logger.info(f"Chatterbox audio generated successfully: {output_file} ({file_size} bytes)")

            return output_file

        except Exception as e:
            logger.error(f"Failed to generate Chatterbox audio: {e}")
            raise APIError(f"Failed to generate audio with Chatterbox: {e}")

    def generate_audio_pyttsx3(self, text: str, output_file: str = "pyttsx3_output.wav",
                               voice_index: int = 0, rate: int = 150) -> str:
        """Generate audio using pyttsx3 (emergency fallback - robotic voice quality).

        Args:
            text: Text to convert to speech
            output_file: Output WAV file path
            voice_index: Index of voice to use (0=female, 1=male on Windows)
            rate: Speech rate (words per minute, default 150)

        Returns:
            Path to generated audio file
        """
        if not self.pyttsx3_available:
            raise APIError("pyttsx3 not available")

        try:
            # Lazy load pyttsx3 engine
            if self.pyttsx3_engine is None:
                import pyttsx3
                logger.info("Initializing pyttsx3 engine (first use)...")
                self.pyttsx3_engine = pyttsx3.init()
                logger.info("✅ pyttsx3 engine initialized")

            # Get available voices
            voices = self.pyttsx3_engine.getProperty('voices')

            # Select voice (default to first available)
            if voice_index < len(voices):
                self.pyttsx3_engine.setProperty('voice', voices[voice_index].id)
            else:
                logger.warning(f"Voice index {voice_index} not available, using default")

            # Set speech rate and volume
            self.pyttsx3_engine.setProperty('rate', rate)
            self.pyttsx3_engine.setProperty('volume', 0.9)

            # Generate audio
            logger.info(f"Generating pyttsx3 audio (rate: {rate}, voice: {voice_index})")
            self.pyttsx3_engine.save_to_file(text, output_file)
            self.pyttsx3_engine.runAndWait()

            # Verify file was created
            if not os.path.exists(output_file):
                raise APIError(f"pyttsx3 failed to create output file: {output_file}")

            file_size = os.path.getsize(output_file)
            logger.info(f"✅ pyttsx3 audio generated: {output_file} ({file_size:,} bytes)")
            logger.warning("⚠️  pyttsx3 produces robotic-sounding audio - emergency fallback only")

            return output_file

        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e}")
            raise APIError(f"pyttsx3 generation failed: {e}")

    def generate_audio(self, text: str, output_file: str = "overview.wav",
                      voice: str = "en-US-AriaNeural", audio_format: str = "wav", slow: bool = False) -> str:
        """Generate audio from text using Edge TTS (preferred) or gTTS (fallback).

        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
            voice: Edge TTS voice name or language code for fallback
            audio_format: Output audio format (wav recommended for Edge TTS)
            slow: Whether to use slow speech for different voice articulation (gTTS only)

        Returns:
            Path to the generated audio file

        Raises:
            APIError: If TTS generation fails
        """
        logger.info(f"Generating audio for text ({len(text)} characters)")

        # Try Chatterbox first if enabled and available
        if (self.chatterbox_available and
            self.chatterbox_device and
            get_tts_config_manager().get_library_config("chatterbox").get("enabled", True)):
            try:
                return self.generate_audio_chatterbox(text, output_file, emotion_level=0.5)
            except Exception as e:
                logger.warning(f"Chatterbox failed, falling back to other TTS: {e}")

        # Try Edge TTS first for natural voices
        if self.edge_tts_available:
            try:
                # Map voice parameter to Edge TTS voices
                edge_voice = voice
                if isinstance(voice, tuple):
                    # Handle legacy tuple format from podcast segments
                    lang, slow_param = voice
                    if 'host' in str(slow_param).lower() or 'en,false' in str(voice).lower():
                        edge_voice = "en-US-AriaNeural"  # Natural female voice
                    elif 'expert' in str(slow_param).lower() or 'en,true' in str(voice).lower():
                        edge_voice = "en-GB-SoniaNeural"  # British female voice for differentiation
                    else:
                        edge_voice = "en-US-AriaNeural"
                elif voice == "en":
                    edge_voice = "en-US-AriaNeural"

                return self.generate_audio_edge(text, output_file, edge_voice)

            except Exception as e:
                logger.warning(f"Edge TTS failed, falling back to gTTS: {e}")

        # Fallback to gTTS
        if self.gtts_available:
            logger.info("Using gTTS fallback")
            try:
                # Handle voice parameter for gTTS
                if isinstance(voice, tuple):
                    lang, slow_param = voice
                    slow = slow_param
                else:
                    lang = voice if voice in ['en', 'es', 'fr', 'de'] else 'en'

                # Create gTTS object
                tts = gTTS(text=text, lang=lang, slow=slow)

                # Generate MP3 file first
                mp3_file = output_file.replace('.wav', '.mp3')

                # Remove any existing files
                for file_path in [mp3_file, output_file]:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                tts.save(mp3_file)

                # Convert MP3 to WAV using pydub if available
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_mp3(mp3_file)
                    audio.export(output_file, format="wav")
                    os.remove(mp3_file)  # Clean up MP3 file
                except ImportError:
                    # If pydub not available, just rename to .wav
                    logger.warning("pydub not available, saving as MP3 with .wav extension")
                    if output_file.endswith('.wav') and not output_file.endswith('.mp3'):
                        os.rename(mp3_file, output_file)
                    else:
                        # Just leave as MP3
                        pass

                file_size = os.path.getsize(output_file)
                logger.info(f"gTTS audio generated successfully: {output_file} ({file_size} bytes)")

                return output_file

            except Exception as e:
                logger.error(f"Failed to generate gTTS audio: {e}")
                raise APIError(f"All TTS services failed. Last error: {e}")

        else:
            raise APIError("No TTS service available - please install edge-tts or gtts")

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

        # Define voice mapping for speakers - using Edge TTS voices for natural sound
        # Edge TTS voices are extremely natural - no robotic sound
        voice_map = {
            'host': "en-US-AriaNeural",      # Natural female American voice
            'expert': "en-GB-SoniaNeural",   # Natural female British voice
            'h': "en-US-AriaNeural",         # Short forms
            'e': "en-GB-SoniaNeural",
            'alex': "en-GB-SoniaNeural",
            'chen': "en-GB-SoniaNeural"
        }

        temp_files = []

        try:
            for speaker_info, text in matches:
                speaker_clean = speaker_info.lower().strip()

                # Determine voice based on speaker name - use Edge TTS voice names directly
                selected_voice = "en-US-AriaNeural"  # default American voice
                for key, voice_name in voice_map.items():
                    if key in speaker_clean:
                        selected_voice = voice_name
                        break

                # Generate temp file for this segment
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_files.append(temp_file.name)

                # Generate audio for this segment sequentially to avoid file locking
                try:
                    temp_wav_file = temp_file.name
                    temp_file.close()  # Close the temp file handle first

                    self.generate_audio(text.strip(), temp_wav_file, voice=selected_voice)
                    segments.append((speaker_info, selected_voice, text.strip(), temp_wav_file))
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
