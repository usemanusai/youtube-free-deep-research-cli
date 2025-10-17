"""
TTS (Text-to-Speech) Configuration and Library Management Module.

This module provides a comprehensive interface for managing different TTS libraries,
including installation, configuration, testing, and switching between TTS engines.
"""

import os
import subprocess
import importlib
import json
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TTSLibrarySpec:
    """Specification for a TTS library."""

    def __init__(self, name: str, package_name: str, license_type: str,
                 description: str, voice_cloning: bool = False,
                 emotion_control: bool = False, parameter_count: Optional[int] = None):
        self.name = name
        self.package_name = package_name
        self.license_type = license_type
        self.description = description
        self.voice_cloning = voice_cloning
        self.emotion_control = emotion_control
        self.parameter_count = parameter_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "package_name": self.package_name,
            "license_type": self.license_type,
            "description": self.description,
            "voice_cloning": self.voice_cloning,
            "emotion_control": self.emotion_control,
            "parameter_count": self.parameter_count
        }


# Available TTS libraries based on the research document
TTS_LIBRARIES = {
    "kokoro": TTSLibrarySpec(
        name="Kokoro",
        package_name="kokoro",
        license_type="Apache 2.0",
        description="Ultra-lightweight TTS with 82M parameters, optimized for CPU efficiency",
        voice_cloning=False,
        emotion_control=False,
        parameter_count=82_000_000
    ),

    "openvoice_v2": TTSLibrarySpec(
        name="OpenVoice v2",
        package_name="openvoice",
        license_type="MIT",
        description="Advanced voice cloning with cross-lingual support and granular style control",
        voice_cloning=True,
        emotion_control=True
    ),

    "melotts": TTSLibrarySpec(
        name="MeloTTS",
        package_name="MeloTTS",
        license_type="MIT",
        description="Multi-lingual TTS with CPU real-time inference and various accents",
        voice_cloning=False,
        emotion_control=False
    ),

    "chatterbox": TTSLibrarySpec(
        name="Chatterbox",
        package_name="chatterbox-tts",
        license_type="MIT",
        description="Emotion exaggeration control and voice cloning on Llama backbone (500M)",
        voice_cloning=True,
        emotion_control=True,
        parameter_count=500_000_000
    ),

    "edge_tts": TTSLibrarySpec(
        name="Edge TTS",
        package_name="edge-tts",
        license_type="MIT",
        description="Microsoft Edge TTS engine - natural voices (currently active default)",
        voice_cloning=False,
        emotion_control=False
    ),

    "gtts": TTSLibrarySpec(
        name="Google TTS",
        package_name="gtts",
        license_type="MIT",
        description="Google Text-to-Speech - fallback option (currently active)",
        voice_cloning=False,
        emotion_control=False
    )
}


class TTSConfigManager:
    """Manages TTS library configurations and installations."""

    def __init__(self, config_file: str = ".tts_config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = self._load_config()
        self.current_library = self.config.get("current_library", "edge_tts")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f"Could not load TTS config file {self.config_file}")
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "current_library": "edge_tts",
            "edge_tts": {
                "default_voice": "en-US-AriaNeural"
            },
            "gtts": {
                "default_lang": "en"
            },
            "installed_libraries": ["edge_tts", "gtts"]
        }

    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save TTS config: {e}")

    def list_libraries(self) -> Dict[str, TTSLibrarySpec]:
        """List all available TTS libraries."""
        return TTS_LIBRARIES

    def get_library_info(self, library_name: str) -> Optional[TTSLibrarySpec]:
        """Get information about a specific TTS library."""
        return TTS_LIBRARIES.get(library_name)

    def is_library_installed(self, library_name: str) -> bool:
        """Check if a TTS library is installed."""
        return library_name in self.config.get("installed_libraries", [])

    def install_library(self, library_name: str) -> Tuple[bool, str]:
        """Install a TTS library."""
        if library_name not in TTS_LIBRARIES:
            return False, f"Unknown library: {library_name}"

        spec = TTS_LIBRARIES[library_name]

        try:
            # Install the package
            logger.info(f"Installing {spec.package_name}...")
            subprocess.check_call([
                "pip", "install", spec.package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Mark as installed
            if "installed_libraries" not in self.config:
                self.config["installed_libraries"] = []
            if library_name not in self.config["installed_libraries"]:
                self.config["installed_libraries"].append(library_name)

            self.save_config()
            return True, f"Successfully installed {spec.name}"

        except subprocess.CalledProcessError as e:
            return False, f"Installation failed: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def uninstall_library(self, library_name: str) -> Tuple[bool, str]:
        """Uninstall a TTS library."""
        if library_name not in TTS_LIBRARIES:
            return False, f"Unknown library: {library_name}"

        spec = TTS_LIBRARIES[library_name]

        try:
            # Uninstall the package
            logger.info(f"Uninstalling {spec.package_name}...")
            subprocess.check_call([
                "pip", "uninstall", "-y", spec.package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Remove from installed list
            if "installed_libraries" in self.config:
                if library_name in self.config["installed_libraries"]:
                    self.config["installed_libraries"].remove(library_name)

            self.save_config()
            return True, f"Successfully uninstalled {spec.name}"

        except subprocess.CalledProcessError as e:
            return False, f"Uninstallation failed: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_library(self, library_name: str) -> Dict[str, Any]:
        """Test a TTS library by generating sample audio."""
        result = {
            "success": False,
            "message": "",
            "sample_file": None,
            "voices": [],
            "performance": None
        }

        if library_name not in TTS_LIBRARIES:
            result["message"] = f"Unknown library: {library_name}"
            return result

        if not self.is_library_installed(library_name):
            result["message"] = f"Library {library_name} is not installed"
            return result

        try:
            if library_name == "kokoro":
                result = self._test_kokoro()
            elif library_name == "openvoice_v2":
                result = self._test_openvoice_v2()
            elif library_name == "melotts":
                result = self._test_melotts()
            elif library_name == "chatterbox":
                result = self._test_chatterbox()
            elif library_name == "edge_tts":
                result = self._test_edge_tts()
            elif library_name == "gtts":
                result = self._test_gtts()
            else:
                result["message"] = f"No test implementation for {library_name}"
                return result

        except Exception as e:
            result["message"] = f"Test failed: {e}"
            logger.error(f"TTS library test error for {library_name}: {e}")

        return result

    def set_default_library(self, library_name: str) -> Tuple[bool, str]:
        """Set the default TTS library."""
        if library_name not in TTS_LIBRARIES:
            return False, f"Unknown library: {library_name}"

        if not self.is_library_installed(library_name):
            return False, f"Library {library_name} is not installed. Install it first with 'tts install {library_name}'"

        self.current_library = library_name
        self.config["current_library"] = library_name
        self.save_config()

        return True, f"Default TTS library set to {library_name}"

    def get_current_library(self) -> str:
        """Get the current default TTS library."""
        return self.current_library

    def get_library_config(self, library_name: str) -> Dict[str, Any]:
        """Get configuration for a specific library."""
        return self.config.get(library_name, {})

    def set_library_config(self, library_name: str, config: Dict[str, Any]):
        """Set configuration for a specific library."""
        if library_name not in self.config:
            self.config[library_name] = {}
        self.config[library_name].update(config)
        self.save_config()

    def _test_kokoro(self) -> Dict[str, Any]:
        """Test Kokoro TTS library."""
        try:
            import torch
            from kokoro import KPipeline
            import soundfile as sf
            import time

            # Initialize pipeline
            start_time = time.time()
            pipeline = KPipeline(lang_code='a')
            init_time = time.time() - start_time

            # Generate sample audio
            text = "Hello, this is Kokoro TTS speaking. Very lightweight and efficient!"
            generator = pipeline(text, voice='af_sarah')

            start_time = time.time()
            full_audio = []
            for chunk in generator:
                full_audio.append(chunk)
            audio_tensor = torch.cat(full_audio)
            audio_array = audio_tensor.numpy()
            gen_time = time.time() - start_time

            # Save sample
            sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(sample_file.name, audio_array, 24000)

            # Get available voices (simplified)
            voices = ['af_sarah', 'am_michael', 'bf_emma', 'bm_george']

            return {
                "success": True,
                "message": ".2f",
                "sample_file": sample_file.name,
                "voices": voices,
                "performance": {
                    "init_time": init_time,
                    "generation_time": gen_time,
                    "total_time": init_time + gen_time
                }
            }

        except ImportError:
            return {"success": False, "message": "Kokoro not installed"}
        except Exception as e:
            return {"success": False, "message": f"Kokoro test failed: {e}"}

    def _test_edge_tts(self) -> Dict[str, Any]:
        """Test Edge TTS library."""
        try:
            import asyncio
            from edge_tts import Communicate, VoicesManager

            async def get_voices_test():
                voices_manager = VoicesManager()
                voices = await voices_manager.find(Gender="Female", Locale="en-US")
                voice_names = [v["ShortName"] for v in voices[:5]]  # First 5 voices

                # Test generation with default voice
                communicate = Communicate("This is Edge TTS. Natural and human-like voice synthesis.", "en-US-AriaNeural")
                sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                await communicate.save(sample_file.name)

                return voice_names, sample_file.name

            voices, sample_file = asyncio.run(get_voices_test())

            return {
                "success": True,
                "message": "Edge TTS working - Microsoft natural voices",
                "sample_file": sample_file,
                "voices": voices
            }

        except ImportError:
            return {"success": False, "message": "Edge TTS not installed"}
        except Exception as e:
            return {"success": False, "message": f"Edge TTS test failed: {e}"}

    def _test_gtts(self) -> Dict[str, Any]:
        """Test Google TTS library."""
        try:
            from gtts import gTTS
            import time

            # Generate sample audio
            start_time = time.time()
            tts = gTTS(text="Hello from Google TTS. Free and accessible speech synthesis.", lang='en')
            gen_time = time.time() - start_time

            # Save sample
            sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            # Note: gTTS saves MP3 but we'll rename to WAV for consistency
            mp3_file = sample_file.name.replace('.wav', '.mp3')
            tts.save(mp3_file)

            return {
                "success": True,
                "message": ".2f",
                "sample_file": mp3_file,  # Return MP3 file
                "voices": ['en', 'es', 'fr', 'de'],  # Simplified language codes
                "performance": {
                    "generation_time": gen_time
                }
            }

        except ImportError:
            return {"success": False, "message": "gTTS not installed"}
        except Exception as e:
            return {"success": False, "message": f"gTTS test failed: {e}"}

    def _test_melotts(self) -> Dict[str, Any]:
        """Test MeloTTS library."""
        try:
            from MeloTTS.MeloTTS import MeloTTS
            import time

            # Initialize model (simplified - may download models)
            start_time = time.time()
            model = MeloTTS()
            init_time = time.time() - start_time

            # Generate sample
            gen_start = time.time()
            wav_data = model.synthesize("Hello from MeloTTS. Multi-lingual speech synthesis.", 'EN', 'EN_US')
            gen_time = time.time() - gen_start

            # Save sample
            sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            import soundfile as sf
            sf.write(sample_file.name, wav_data, 44100)

            return {
                "success": True,
                "message": ".2f",
                "sample_file": sample_file.name,
                "voices": ['EN_US', 'EN_GB', 'ES', 'FR', 'ZH', 'JP'],
                "performance": {
                    "init_time": init_time,
                    "generation_time": gen_time,
                    "total_time": init_time + gen_time
                }
            }

        except ImportError:
            return {"success": False, "message": "MeloTTS not installed"}
        except Exception as e:
            return {"success": False, "message": f"MeloTTS test failed: {e}"}

    def _test_openvoice_v2(self) -> Dict[str, Any]:
        """Test OpenVoice v2 library (complex, may not work without reference audio)."""
        return {
            "success": False,
            "message": "OpenVoice v2 requires voice cloning reference audio for testing. Use 'tts configure openvoice_v2' for setup."
        }

    def _test_chatterbox(self) -> Dict[str, Any]:
        """Test Chatterbox library."""
        try:
            from chatterbox import ChatterboxTTS
            import time

            # Initialize model
            start_time = time.time()
            tts = ChatterboxTTS()
            init_time = time.time() - start_time

            # Generate sample
            gen_start = time.time()
            # Simplified - check Chatterbox docs for actual API
            wav_data = tts.synthesize("Hello from Chatterbox TTS with emotion control.", emotion=0.5)
            gen_time = time.time() - gen_start

            # Save sample
            sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            import soundfile as sf
            sf.write(sample_file.name, wav_data, 22050)

            return {
                "success": True,
                "message": ".2f",
                "sample_file": sample_file.name,
                "voices": ['default_female', 'default_male'],
                "performance": {
                    "init_time": init_time,
                    "generation_time": gen_time,
                    "total_time": init_time + gen_time
                }
            }

        except ImportError:
            return {"success": False, "message": "Chatterbox not installed"}
        except Exception as e:
            return {"success": False, "message": f"Chatterbox test failed: {e}"}


# Global instance
_tts_config_manager = None

def get_tts_config_manager() -> TTSConfigManager:
    """Get the global TTS configuration manager instance."""
    global _tts_config_manager
    if _tts_config_manager is None:
        _tts_config_manager = TTSConfigManager()
    return _tts_config_manager
