"""
TTS Bridge Client - Python 3.13 Client for Python 3.11 TTS Bridge

This module provides a client interface to communicate with the Python 3.11
TTS bridge subprocess for MeloTTS and Chatterbox engines.

Author: Augment Agent
Date: September 30, 2025
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TTSBridgeClient:
    """Client for communicating with Python 3.11 TTS bridge subprocess."""
    
    def __init__(self, python311_path: Optional[str] = None):
        """
        Initialize TTS Bridge Client.
        
        Args:
            python311_path: Path to Python 3.11 executable. If None, will try to
                          auto-detect from .python311_path file or environment.
        """
        self.python311_path = self._find_python311_path(python311_path)
        self.bridge_script = self._find_bridge_script()
        
        # Verify Python 3.11 is available
        self._verify_python311()
        
        logger.info(f"✅ TTS Bridge initialized with Python 3.11: {self.python311_path}")
    
    def _find_python311_path(self, provided_path: Optional[str]) -> str:
        """Find Python 3.11 executable path."""
        # 1. Use provided path
        if provided_path and os.path.exists(provided_path):
            return provided_path
        
        # 2. Check .python311_path file
        config_file = Path(__file__).parent.parent / ".python311_path"
        if config_file.exists():
            path = config_file.read_text().strip()
            if os.path.exists(path):
                logger.info(f"Found Python 3.11 path from config: {path}")
                return path
        
        # 3. Check environment variable
        env_path = os.environ.get("PYTHON311_PATH")
        if env_path and os.path.exists(env_path):
            logger.info(f"Found Python 3.11 path from environment: {env_path}")
            return env_path
        
        # 4. Try common conda environment locations
        conda_envs = [
            "tts-bridge-py311",
            "tts-bridge",
            "py311"
        ]
        
        for env_name in conda_envs:
            # Try conda
            try:
                result = subprocess.run(
                    ["conda", "run", "-n", env_name, "which", "python"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    path = result.stdout.strip()
                    if os.path.exists(path):
                        logger.info(f"Found Python 3.11 in conda env '{env_name}': {path}")
                        return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # 5. Fallback error
        raise FileNotFoundError(
            "Python 3.11 executable not found. Please:\n"
            "1. Run setup_python311_env.bat (Windows) or setup_python311_env.sh (Linux/Mac)\n"
            "2. Or set PYTHON311_PATH environment variable\n"
            "3. Or create .python311_path file with the path"
        )
    
    def _find_bridge_script(self) -> Path:
        """Find tts_bridge.py script."""
        # Check in parent directory (project root)
        script_path = Path(__file__).parent.parent / "tts_bridge.py"
        
        if not script_path.exists():
            raise FileNotFoundError(
                f"TTS bridge script not found at: {script_path}\n"
                "Please ensure tts_bridge.py is in the project root directory."
            )
        
        return script_path
    
    def _verify_python311(self):
        """Verify Python 3.11 is available and has required packages."""
        try:
            # Check Python version
            result = subprocess.run(
                [self.python311_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to run Python 3.11: {result.stderr}")
            
            version = result.stdout.strip()
            if not version.startswith("Python 3.11"):
                logger.warning(f"Expected Python 3.11, got: {version}")
            
            logger.info(f"Python version: {version}")
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Python 3.11 verification timed out")
        except FileNotFoundError:
            raise FileNotFoundError(f"Python 3.11 executable not found: {self.python311_path}")
    
    def _run_bridge(self, args: list, timeout: int = 120) -> Dict[str, Any]:
        """
        Run TTS bridge subprocess.
        
        Args:
            args: Command line arguments for bridge script
            timeout: Timeout in seconds
        
        Returns:
            Response dictionary from bridge
        """
        cmd = [self.python311_path, str(self.bridge_script)] + args
        
        logger.info(f"Running TTS bridge: {' '.join(args[:4])}...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                # Try to parse error response
                try:
                    error_response = json.loads(result.stderr)
                    error_msg = error_response.get("error", result.stderr)
                except json.JSONDecodeError:
                    error_msg = result.stderr
                
                raise RuntimeError(f"TTS bridge failed: {error_msg}")
            
            # Parse success response
            try:
                response = json.loads(result.stdout)
                if not response.get("success"):
                    raise RuntimeError(f"TTS generation failed: {response.get('error')}")
                
                return response
            
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse bridge response: {e}\nOutput: {result.stdout}")
        
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"TTS bridge timed out after {timeout} seconds")
    
    def generate_melotts(
        self,
        text: str,
        output_file: str,
        language: str = "EN-US",
        speed: float = 1.0,
        voice_index: int = 0
    ) -> str:
        """
        Generate audio using MeloTTS via Python 3.11 bridge.
        
        Args:
            text: Text to synthesize
            output_file: Output WAV file path
            language: Language code (EN-US, EN-BR, EN-AU, ES, FR, ZH, JP, KR)
            speed: Speech speed (0.5 to 2.0)
            voice_index: Voice index for the language
        
        Returns:
            Path to generated audio file
        """
        args = [
            "--engine", "melotts",
            "--text", text,
            "--output", output_file,
            "--language", language,
            "--speed", str(speed),
            "--voice-index", str(voice_index)
        ]
        
        response = self._run_bridge(args)
        logger.info(f"✅ MeloTTS audio generated: {response['output']}")
        
        return response["output"]
    
    def generate_chatterbox(
        self,
        text: str,
        output_file: str,
        audio_prompt: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        language_id: Optional[str] = None
    ) -> str:
        """
        Generate audio using Chatterbox via Python 3.11 bridge.
        
        Args:
            text: Text to synthesize
            output_file: Output WAV file path
            audio_prompt: Path to reference audio for voice cloning
            exaggeration: Emotion exaggeration level (0.0 to 1.0)
            cfg_weight: Classifier-free guidance weight (0.0 to 1.0)
            language_id: Language ID for multilingual model (en, fr, zh, etc.)
        
        Returns:
            Path to generated audio file
        """
        args = [
            "--engine", "chatterbox",
            "--text", text,
            "--output", output_file,
            "--exaggeration", str(exaggeration),
            "--cfg-weight", str(cfg_weight)
        ]
        
        if audio_prompt:
            args.extend(["--audio-prompt", audio_prompt])
        
        if language_id:
            args.extend(["--language-id", language_id])
        
        response = self._run_bridge(args, timeout=180)  # Chatterbox may take longer
        logger.info(f"✅ Chatterbox audio generated: {response['output']}")
        
        return response["output"]

