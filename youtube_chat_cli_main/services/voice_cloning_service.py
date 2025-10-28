"""Voice cloning service for managing cloned voices and generating speech with advanced parameters."""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import librosa
import numpy as np

logger = logging.getLogger(__name__)

# Valid emotion types
VALID_EMOTIONS = [
    'neutral', 'happy', 'sad', 'angry', 'joyful', 'excited',
    'surprised', 'curious', 'confident', 'empathetic'
]

from youtube_chat_cli_main.services.tts.engines.e2f5_tts import E2F5TTSEngine, E2F5_TTS_AVAILABLE
from youtube_chat_cli_main.core.database import get_database


class VoiceCloningService:
    """Service for managing voice cloning operations."""

    def __init__(self, storage_path: str = "./voice_clones", device: Optional[str] = None):
        """Initialize voice cloning service.

        Args:
            storage_path: Directory to store reference audio files
            device: Device for TTS ("cuda", "cpu", or None for auto)
        """
        if not E2F5_TTS_AVAILABLE:
            raise RuntimeError("E2-F5-TTS not available. Install with: pip install f5-tts")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.engine = E2F5TTSEngine(device=device)
        self.db = get_database()
        logger.info(f"Voice cloning service initialized (storage: {storage_path})")

    def validate_voice_parameters(self, speed: float = 1.0, pitch: float = 0.0,
                                 exaggeration: float = 0.5, cfg_weight: float = 0.5,
                                 temperature: float = 0.9, top_p: float = 0.95,
                                 min_p: float = 0.1, emotion: str = "neutral",
                                 pause_before: int = 0, pause_after: int = 0,
                                 breath_frequency: int = 0) -> Dict[str, Any]:
        """Validate voice generation parameters.

        Args:
            speed: Speech rate multiplier (0.5-2.0)
            pitch: Pitch adjustment in semitones (-12 to +12)
            exaggeration: Emotional exaggeration (0.25-2.0)
            cfg_weight: Classifier-free guidance weight (0.0-1.0)
            temperature: Randomness/variation (0.0-2.0)
            top_p: Nucleus sampling parameter (0.0-1.0)
            min_p: Minimum probability threshold (0.0-1.0)
            emotion: Emotion type
            pause_before: Pause before text (0-5000ms)
            pause_after: Pause after text (0-5000ms)
            breath_frequency: Insert breath every N words (0-20)

        Returns:
            Dictionary with validation results

        Raises:
            ValueError: If any parameter is invalid
        """
        errors = []

        # Validate numeric ranges
        if not (0.5 <= speed <= 2.0):
            errors.append(f"Speed must be 0.5-2.0, got {speed}")
        if not (-12 <= pitch <= 12):
            errors.append(f"Pitch must be -12 to +12, got {pitch}")
        if not (0.25 <= exaggeration <= 2.0):
            errors.append(f"Exaggeration must be 0.25-2.0, got {exaggeration}")
        if not (0.0 <= cfg_weight <= 1.0):
            errors.append(f"CFG weight must be 0.0-1.0, got {cfg_weight}")
        if not (0.0 <= temperature <= 2.0):
            errors.append(f"Temperature must be 0.0-2.0, got {temperature}")
        if not (0.0 <= top_p <= 1.0):
            errors.append(f"Top P must be 0.0-1.0, got {top_p}")
        if not (0.0 <= min_p <= 1.0):
            errors.append(f"Min P must be 0.0-1.0, got {min_p}")
        if not (0 <= pause_before <= 5000):
            errors.append(f"Pause before must be 0-5000ms, got {pause_before}")
        if not (0 <= pause_after <= 5000):
            errors.append(f"Pause after must be 0-5000ms, got {pause_after}")
        if not (0 <= breath_frequency <= 20):
            errors.append(f"Breath frequency must be 0-20, got {breath_frequency}")

        # Validate emotion
        if emotion not in VALID_EMOTIONS:
            errors.append(f"Invalid emotion '{emotion}'. Valid: {', '.join(VALID_EMOTIONS)}")

        if errors:
            raise ValueError("; ".join(errors))

        return {
            "valid": True,
            "speed": speed,
            "pitch": pitch,
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
            "temperature": temperature,
            "top_p": top_p,
            "min_p": min_p,
            "emotion": emotion,
            "pause_before": pause_before,
            "pause_after": pause_after,
            "breath_frequency": breath_frequency
        }

    def validate_reference_audio(self, audio_path: str) -> Dict[str, Any]:
        """Validate reference audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with validation results

        Raises:
            ValueError: If audio is invalid
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)

            # Validation checks
            issues = []
            if sr < 22000:
                issues.append(f"Sample rate too low: {sr}Hz (minimum: 22kHz)")
            if duration < 3:
                issues.append(f"Audio too short: {duration:.1f}s (minimum: 3s)")
            if duration > 300:
                issues.append(f"Audio too long: {duration:.1f}s (maximum: 300s)")

            # Calculate SNR (Signal-to-Noise Ratio)
            # Simple estimation: ratio of signal power to noise power
            signal_power = np.mean(y ** 2)
            noise_power = np.mean(np.abs(np.diff(y)) ** 2)
            snr_db = 10 * np.log10(signal_power / (noise_power + 1e-10))

            if snr_db < 15:
                issues.append(f"Low SNR: {snr_db:.1f}dB (recommended: >20dB)")

            result = {
                "valid": len(issues) == 0,
                "duration": duration,
                "sample_rate": sr,
                "snr_db": snr_db,
                "issues": issues,
                "file_size": os.path.getsize(audio_path)
            }

            logger.info(f"Audio validation: {result}")
            return result

        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            raise ValueError(f"Failed to validate audio: {e}")

    def create_voice(self, name: str, reference_audio: str, 
                    consent_ip: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a cloned voice from reference audio.

        Args:
            name: Name for the cloned voice
            reference_audio: Path to reference audio file
            consent_ip: IP address of consent (for compliance)
            metadata: Additional metadata (seed, settings, etc.)

        Returns:
            Dictionary with voice information

        Raises:
            ValueError: If validation fails
        """
        # Validate audio
        validation = self.validate_reference_audio(reference_audio)
        if not validation["valid"]:
            raise ValueError(f"Invalid reference audio: {validation['issues']}")

        # Calculate audio hash for deduplication
        with open(reference_audio, 'rb') as f:
            audio_hash = hashlib.sha256(f.read()).hexdigest()

        # Copy reference audio to storage
        stored_path = self.storage_path / f"{name}_{audio_hash[:8]}.wav"
        os.makedirs(self.storage_path, exist_ok=True)

        try:
            import shutil
            shutil.copy2(reference_audio, stored_path)
        except Exception as e:
            logger.error(f"Failed to copy reference audio: {e}")
            raise

        # Store in database
        voice_metadata = {
            "seed": metadata.get("seed", 42) if metadata else 42,
            "quality": metadata.get("quality", "balanced") if metadata else "balanced",
            "validation": validation,
            **(metadata or {})
        }

        try:
            # Insert into database
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO cloned_voices 
                (name, reference_audio_path, reference_audio_hash, metadata, 
                 consent_timestamp, consent_ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                str(stored_path),
                audio_hash,
                json.dumps(voice_metadata),
                datetime.now().isoformat(),
                consent_ip or "unknown"
            ))
            self.db.conn.commit()
            voice_id = cursor.lastrowid

            logger.info(f"✅ Voice '{name}' created (ID: {voice_id})")

            return {
                "id": voice_id,
                "name": name,
                "reference_audio_path": str(stored_path),
                "audio_hash": audio_hash,
                "metadata": voice_metadata,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to store voice in database: {e}")
            # Clean up stored file
            if stored_path.exists():
                stored_path.unlink()
            raise

    def list_voices(self) -> List[Dict[str, Any]]:
        """List all cloned voices.

        Returns:
            List of voice dictionaries
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT id, name, reference_audio_path, created_at, usage_count, metadata
                FROM cloned_voices
                WHERE is_active = 1
                ORDER BY created_at DESC
            """)

            voices = []
            for row in cursor.fetchall():
                voices.append({
                    "id": row[0],
                    "name": row[1],
                    "reference_audio_path": row[2],
                    "created_at": row[3],
                    "usage_count": row[4],
                    "metadata": json.loads(row[5]) if row[5] else {}
                })

            return voices

        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []

    def generate_speech(self, voice_id: int, text: str, output_file: str,
                       speed: float = 1.0, pitch: float = 0.0,
                       exaggeration: float = 0.5, cfg_weight: float = 0.5,
                       temperature: float = 0.9, top_p: float = 0.95,
                       min_p: float = 0.1, emotion: str = "neutral",
                       emphasis: Optional[List[str]] = None,
                       pause_before: int = 0, pause_after: int = 0,
                       breath_frequency: int = 0, seed: Optional[int] = None) -> str:
        """Generate speech using a cloned voice with advanced prosody control.

        Args:
            voice_id: ID of cloned voice
            text: Text to synthesize
            output_file: Path to save output
            speed: Speech rate multiplier (0.5-2.0, default 1.0)
            pitch: Pitch adjustment in semitones (-12 to +12, default 0.0)
            exaggeration: Emotional exaggeration (0.25-2.0, default 0.5)
            cfg_weight: Classifier-free guidance weight (0.0-1.0, default 0.5)
            temperature: Randomness/variation (0.0-2.0, default 0.9)
            top_p: Nucleus sampling parameter (0.0-1.0, default 0.95)
            min_p: Minimum probability threshold (0.0-1.0, default 0.1)
            emotion: Emotion type (default neutral)
            emphasis: List of words to emphasize (optional)
            pause_before: Pause before text in milliseconds (0-5000, default 0)
            pause_after: Pause after text in milliseconds (0-5000, default 0)
            breath_frequency: Insert breath every N words (0-20, default 0)
            seed: Random seed for reproducibility (optional)

        Returns:
            Path to generated audio file

        Raises:
            ValueError: If parameters are invalid or voice not found
        """
        try:
            # Validate parameters
            self.validate_voice_parameters(
                speed=speed, pitch=pitch, exaggeration=exaggeration,
                cfg_weight=cfg_weight, temperature=temperature,
                top_p=top_p, min_p=min_p, emotion=emotion,
                pause_before=pause_before, pause_after=pause_after,
                breath_frequency=breath_frequency
            )

            # Get voice from database
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT reference_audio_path, metadata FROM cloned_voices WHERE id = ?
            """, (voice_id,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Voice not found: {voice_id}")

            reference_audio, metadata_json = row
            metadata = json.loads(metadata_json) if metadata_json else {}

            # Use provided seed or fall back to stored seed
            final_seed = seed if seed is not None else metadata.get("seed", 42)

            # Generate audio with advanced parameters
            output = self.engine.generate_audio(
                text=text,
                reference_audio=reference_audio,
                output_file=output_file,
                seed=final_seed,
                speed=speed,
                pitch=pitch,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
                temperature=temperature,
                top_p=top_p,
                min_p=min_p,
                emotion=emotion,
                emphasis=emphasis,
                pause_before=pause_before,
                pause_after=pause_after,
                breath_frequency=breath_frequency
            )

            # Update usage count
            cursor.execute("""
                UPDATE cloned_voices
                SET usage_count = usage_count + 1, last_used = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), voice_id))
            self.db.conn.commit()

            # Log operation with parameters
            params_json = json.dumps({
                "speed": speed,
                "pitch": pitch,
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "temperature": temperature,
                "emotion": emotion,
                "seed": final_seed
            })

            cursor.execute("""
                INSERT INTO voice_cloning_logs
                (voice_id, operation, text_length, output_path, duration_seconds, parameters)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (voice_id, "generate", len(text), output, 0, params_json))
            self.db.conn.commit()

            logger.info(f"✅ Speech generated: voice_id={voice_id}, text_len={len(text)}, "
                       f"emotion={emotion}, pitch={pitch}st, speed={speed}x")

            return output

        except ValueError as e:
            logger.error(f"Invalid parameters: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate speech: {e}")
            raise

    def delete_voice(self, voice_id: int) -> bool:
        """Delete a cloned voice.

        Args:
            voice_id: ID of voice to delete

        Returns:
            True if successful
        """
        try:
            cursor = self.db.conn.cursor()

            # Get voice info
            cursor.execute("""
                SELECT reference_audio_path FROM cloned_voices WHERE id = ?
            """, (voice_id,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Voice not found: {voice_id}")

            # Delete file
            audio_path = Path(row[0])
            if audio_path.exists():
                audio_path.unlink()

            # Mark as inactive in database
            cursor.execute("""
                UPDATE cloned_voices SET is_active = 0 WHERE id = ?
            """, (voice_id,))
            self.db.conn.commit()

            logger.info(f"✅ Voice {voice_id} deleted")
            return True

        except Exception as e:
            logger.error(f"Failed to delete voice: {e}")
            return False


__all__ = ["VoiceCloningService"]

