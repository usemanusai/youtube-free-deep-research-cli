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
import time
import platform
import sys
import shutil
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
        package_name="git+https://github.com/hexgrad/kokoro.git",
        license_type="Apache 2.0",
        description="Ultra-lightweight TTS with 82M parameters, optimized for CPU efficiency",
        voice_cloning=False,
        emotion_control=False,
        parameter_count=82_000_000
    ),

    "openvoice_v2": TTSLibrarySpec(
        name="OpenVoice v2",
        package_name="git+https://github.com/myshell-ai/OpenVoice.git",
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
            "chatterbox": {
                "enabled": True,  # Enable if installed
                "device": "auto",
                "emotion_level": 0.5,
                "use_multilingual": False
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

    def install_library(self, library_name: str, cpu_only: bool = True, retry_count: int = 3, timeout: int = 300) -> Tuple[bool, str]:
        """Install a TTS library with robust error handling and retry logic."""
        if library_name not in TTS_LIBRARIES:
            return False, f"Unknown library: {library_name}"

        spec = TTS_LIBRARIES[library_name]
        logger.info(f"Starting installation of {spec.name} ({library_name})")

        # Check Python compatibility
        if not self._check_python_compatibility(library_name):
            return False, f"Python version incompatible with {spec.name}"

        # Install system dependencies first
        if not self._install_system_dependencies(library_name):
            logger.warning(f"Some system dependencies for {spec.name} may be missing")

        # Install base dependencies
        if not self._install_base_dependencies(cpu_only):
            return False, f"Failed to install base dependencies for {spec.name}"

        # Try library-specific installation
        success, message = self._install_library_with_retry(library_name, retry_count, timeout)

        if success:
            # Mark as installed
            if "installed_libraries" not in self.config:
                self.config["installed_libraries"] = []
            if library_name not in self.config["installed_libraries"]:
                self.config["installed_libraries"].append(library_name)

            self.save_config()

            # Verify installation
            if self._verify_library_installation(library_name):
                return True, f"Successfully installed and verified {spec.name}"
            else:
                return True, f"Installed {spec.name} but verification failed - may still work"

        return False, message

    def _check_python_compatibility(self, library_name: str) -> bool:
        """Check if current Python version is compatible with the library."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        # Chatterbox has specific Python version requirements
        if library_name == "chatterbox" and float(python_version) >= 3.12:
            logger.error(f"Chatterbox requires Python < 3.12, current version: {python_version}")
            return False

        return True

    def _install_system_dependencies(self, library_name: str) -> bool:
        """Install system-level dependencies required by TTS libraries."""
        system_deps = {
            "kokoro": ["git", "espeak-ng", "espeak-ng-data"],
            "openvoice_v2": ["git", "ffmpeg"],
            "melotts": ["git", "ffmpeg"],
            "chatterbox": ["git"],
        }

        deps = system_deps.get(library_name, [])
        if not deps:
            return True

        logger.info(f"Installing system dependencies for {library_name}: {deps}")

        # Detect package manager
        if shutil.which("apt-get"):
            return self._install_apt_packages(deps)
        elif shutil.which("yum"):
            return self._install_yum_packages(deps)
        elif shutil.which("brew"):
            return self._install_brew_packages(deps)
        else:
            logger.warning("No supported package manager found, skipping system dependencies")
            return True

    def _install_apt_packages(self, packages: List[str]) -> bool:
        """Install packages using apt-get."""
        try:
            # Update package list
            subprocess.run(["sudo", "apt-get", "update", "-qq"], check=True, capture_output=True)

            # Install packages
            cmd = ["sudo", "apt-get", "install", "-y", "-qq"] + packages
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install apt packages: {e}")
            return False

    def _install_yum_packages(self, packages: List[str]) -> bool:
        """Install packages using yum."""
        try:
            cmd = ["sudo", "yum", "install", "-y"] + packages
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install yum packages: {e}")
            return False

    def _install_brew_packages(self, packages: List[str]) -> bool:
        """Install packages using Homebrew."""
        try:
            for package in packages:
                subprocess.run(["brew", "install", package], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install brew packages: {e}")
            return False

    def _install_base_dependencies(self, cpu_only: bool = True) -> bool:
        """Install base dependencies required by most TTS libraries."""
        logger.info("Installing base dependencies...")

        constraints_file = Path(__file__).parent / "install_constraints.txt"

        try:
            # Install PyTorch CPU version for compatibility
            if cpu_only:
                torch_cmd = [
                    "pip", "install",
                    "torch", "torchaudio", "torchvision",
                    "--index-url", "https://download.pytorch.org/whl/cpu",
                    "--upgrade"
                ]
                subprocess.run(torch_cmd, check=True, capture_output=True, timeout=300)

            # Install other base dependencies with constraints
            if constraints_file.exists():
                base_cmd = [
                    "pip", "install",
                    "-c", str(constraints_file),
                    "transformers", "tokenizers", "huggingface-hub",
                    "librosa", "soundfile", "pydub",
                    "numpy", "scipy", "requests", "tqdm",
                    "--upgrade"
                ]
                subprocess.run(base_cmd, check=True, capture_output=True, timeout=300)

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install base dependencies: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Base dependency installation timed out")
            return False

    def _install_library_with_retry(self, library_name: str, retry_count: int, timeout: int) -> Tuple[bool, str]:
        """Install library with retry logic and exponential backoff."""
        spec = TTS_LIBRARIES[library_name]

        for attempt in range(retry_count):
            logger.info(f"Installation attempt {attempt + 1}/{retry_count} for {spec.name}")

            success, message = self._try_library_installation(library_name, timeout)
            if success:
                return True, message

            if attempt < retry_count - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

        return False, f"All {retry_count} installation attempts failed for {spec.name}"

    def _try_library_installation(self, library_name: str, timeout: int) -> Tuple[bool, str]:
        """Try installing a library using library-specific methods."""
        spec = TTS_LIBRARIES[library_name]

        # Get installation methods for this library
        methods = self._get_installation_methods(library_name)

        for method_name, command in methods:
            try:
                logger.info(f"Trying {method_name} for {spec.name}...")

                # Run with timeout and capture output
                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    timeout=timeout,
                    text=True
                )

                logger.info(f"Successfully installed {spec.name} using {method_name}")
                return True, f"Installed using {method_name}"

            except subprocess.CalledProcessError as e:
                logger.warning(f"{method_name} failed: {e.stderr if e.stderr else str(e)}")
                continue
            except subprocess.TimeoutExpired:
                logger.warning(f"{method_name} timed out after {timeout} seconds")
                continue

        return False, f"All installation methods failed for {spec.name}"

    def _get_installation_methods(self, library_name: str) -> List[Tuple[str, List[str]]]:
        """Get multiple installation methods to try for each library."""
        spec = TTS_LIBRARIES[library_name]

        # Library-specific installation methods
        if library_name == "kokoro":
            return self._get_kokoro_methods()
        elif library_name == "openvoice_v2":
            return self._get_openvoice_methods()
        elif library_name == "melotts":
            return self._get_melotts_methods()
        elif library_name == "chatterbox":
            return self._get_chatterbox_methods()
        else:
            # Standard methods for simple packages
            return [
                ("Standard pip", ["pip", "install", spec.package_name, "--upgrade"]),
                ("Force reinstall", ["pip", "install", spec.package_name, "--force-reinstall"]),
                ("No cache", ["pip", "install", spec.package_name, "--no-cache-dir", "--upgrade"]),
            ]

        # For git installations, add git-specific methods
        if spec.package_name.startswith("git+"):
            git_repo_url = spec.package_name.replace("git+", "")
            git_methods = [
                ("Git clone + setup", ["pip", "install", spec.package_name]),
                ("Git with dependencies", ["pip", "install", spec.package_name, "--force-reinstall"]),
            ]
            return base_methods + git_methods

        return base_methods

    def _get_kokoro_methods(self) -> List[Tuple[str, List[str]]]:
        """Get installation methods for Kokoro TTS."""
        return [
            ("Direct git install", ["pip", "install", "git+https://github.com/hexgrad/kokoro.git"]),
            ("Git with no deps", ["pip", "install", "git+https://github.com/hexgrad/kokoro.git", "--no-deps"]),
            ("Force reinstall", ["pip", "install", "git+https://github.com/hexgrad/kokoro.git", "--force-reinstall"]),
        ]

    def _get_openvoice_methods(self) -> List[Tuple[str, List[str]]]:
        """Get installation methods for OpenVoice v2."""
        return [
            ("Direct git install", ["pip", "install", "git+https://github.com/myshell-ai/OpenVoice.git"]),
            ("Git with no deps", ["pip", "install", "git+https://github.com/myshell-ai/OpenVoice.git", "--no-deps"]),
            ("Force reinstall", ["pip", "install", "git+https://github.com/myshell-ai/OpenVoice.git", "--force-reinstall"]),
        ]

    def _get_melotts_methods(self) -> List[Tuple[str, List[str]]]:
        """Get installation methods for MeloTTS."""
        return [
            ("Git install", ["pip", "install", "git+https://github.com/myshell-ai/MeloTTS.git"]),
            ("PyPI install", ["pip", "install", "MeloTTS", "--upgrade"]),
            ("PyPI no cache", ["pip", "install", "MeloTTS", "--no-cache-dir"]),
            ("Force reinstall", ["pip", "install", "MeloTTS", "--force-reinstall"]),
        ]

    def _get_chatterbox_methods(self) -> List[Tuple[str, List[str]]]:
        """Get installation methods for Chatterbox TTS."""
        return [
            ("PyPI install", ["pip", "install", "chatterbox-tts", "--upgrade"]),
            ("Compatible versions", ["pip", "install", "chatterbox-tts", "--no-deps"]),
            ("Force reinstall", ["pip", "install", "chatterbox-tts", "--force-reinstall"]),
        ]

    def _verify_library_installation(self, library_name: str) -> bool:
        """Verify that a library was installed correctly."""
        try:
            if library_name == "kokoro":
                import kokoro
                return True
            elif library_name == "openvoice_v2":
                import openvoice
                return True
            elif library_name == "melotts":
                import melo
                return True
            elif library_name == "chatterbox":
                import chatterbox
                return True
            elif library_name == "edge_tts":
                import edge_tts
                return True
            elif library_name == "gtts":
                import gtts
                return True
            else:
                return False
        except ImportError:
            return False

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

    def _get_installation_guidance(self, library_name: str) -> Optional[str]:
        """Provide installation guidance for complex libraries."""
        if library_name == "kokoro":
            return ("Requires manual Git setup. Clone https://github.com/hexgrad/kokoro.git and follow local install instructions. May require espeak-ng and other dependencies.")
        elif library_name == "openvoice_v2":
            return ("Complex multi-step installation required. See https://github.com/myshell-ai/OpenVoice for detailed setup steps including MeloTTS dependency.")
        elif library_name == "melotts":
            return ("May require manual installation from source or additional dependencies. Check https://github.com/myshell-ai/MeloTTS for setup instructions.")
        elif library_name == "chatterbox":
            python_version = f"{importlib.util.sys.version_info.major}.{importlib.util.sys.version_info.minor}"
            if float(python_version) >= 3.12:
                return (". Package built for Python 3.11 only. Error: 'pkgutil.ImpImporter' removed in Python 3.12+. Use Python 3.11 environment.")
            else:
                return ("Requires PyTorch and may need CUDA. Follow https://github.com/resemble-ai/chatterbox for installation guide.")
        else:
            return None

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
            from edge_tts import Communicate

            async def test_generation():
                # Test generation with default voice
                communicate = Communicate("This is Edge TTS. Natural and human-like voice synthesis.", "en-US-AriaNeural")
                sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                await communicate.save(sample_file.name)
                return sample_file.name

            sample_file = asyncio.run(test_generation())

            # Common Edge TTS voices (hardcoded to avoid VoicesManager complexity)
            voices = [
                "en-US-AriaNeural", "en-US-ZiraNeural", "en-US-BenjaminNeural",
                "en-GB-SoniaNeural", "en-GB-RyanNeural"
            ]

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
            from chatterbox.tts import ChatterboxTTS
            import time

            # Get device config
            config = self.get_library_config("chatterbox")
            device = config.get("device", "auto")
            if device == "auto":
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"

            # Initialize model
            start_time = time.time()
            tts = ChatterboxTTS.from_pretrained(device=device)
            init_time = time.time() - start_time

            # Generate sample
            gen_start = time.time()
            text = "Hello from Chatterbox TTS. This is a test of the emotion control system."
            wav_data = tts.generate(text)
            gen_time = time.time() - gen_start

            # Save sample
            sample_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

            # Chatterbox returns tensor directly - save with torchaudio
            import torchaudio as ta
            ta.save(sample_file.name, wav_data.unsqueeze(0), tts.sr)

            return {
                "success": True,
                "message": ".2f",
                "sample_file": sample_file.name,
                "voices": ['English (en)'],
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
