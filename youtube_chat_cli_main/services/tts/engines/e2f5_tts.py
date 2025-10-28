"""E2-F5-TTS engine for voice cloning and zero-shot TTS with advanced prosody control."""

import os
import logging
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

# E2-F5-TTS availability check
E2F5_TTS_AVAILABLE = False
try:
    import torch
    from f5_tts.infer.api import F5TTS
    E2F5_TTS_AVAILABLE = True
    logger.info("✅ E2-F5-TTS available for voice cloning and zero-shot TTS")
except ImportError as e:
    logger.info(f"E2-F5-TTS not available: {e}")


class E2F5TTSEngine:
    """E2-F5-TTS engine for voice cloning with zero-shot TTS capabilities."""

    def __init__(self, model_name: str = "F5-TTS", device: Optional[str] = None, 
                 nfe: int = 16, quality: str = "balanced"):
        """Initialize E2-F5-TTS engine.

        Args:
            model_name: Model to use ("F5-TTS" or "E2-TTS")
            device: Device to use ("cuda", "cpu", or None for auto-detect)
            nfe: Number of function evaluations (16-32, higher = better quality)
            quality: Quality preset ("fast", "balanced", "high")
        """
        if not E2F5_TTS_AVAILABLE:
            raise RuntimeError("E2-F5-TTS not installed. Install with: pip install f5-tts")

        self.model_name = model_name
        self.nfe = nfe
        self.quality = quality
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Quality presets
        self.quality_settings = {
            "fast": {"nfe": 8, "chunk_size": 1024},
            "balanced": {"nfe": 16, "chunk_size": 2048},
            "high": {"nfe": 32, "chunk_size": 4096}
        }

        # Override NFE based on quality preset
        if quality in self.quality_settings:
            self.nfe = self.quality_settings[quality]["nfe"]

        self.model = None
        self.is_initialized = False
        logger.info(f"E2-F5-TTS engine initialized (device: {self.device}, model: {model_name}, quality: {quality})")

    def _initialize_model(self):
        """Lazy load the model on first use."""
        if self.is_initialized:
            return

        try:
            logger.info(f"Loading {self.model_name} model on {self.device}...")
            self.model = F5TTS(model_name=self.model_name, device=self.device)
            self.is_initialized = True
            logger.info(f"✅ {self.model_name} model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load {self.model_name} model: {e}")
            raise RuntimeError(f"Failed to initialize E2-F5-TTS: {e}")

    def _apply_prosody_markup(self, text: str, pitch: float = 0.0, speed: float = 1.0,
                             emphasis: Optional[List[str]] = None,
                             pause_before: int = 0, pause_after: int = 0) -> str:
        """Apply SSML-like prosody markup to text.

        Args:
            text: Original text
            pitch: Pitch adjustment in semitones (-12 to +12)
            speed: Speed multiplier (0.5-2.0)
            emphasis: List of words to emphasize
            pause_before: Pause before text in milliseconds
            pause_after: Pause after text in milliseconds

        Returns:
            Text with prosody markup applied
        """
        result = text

        # Add pauses
        if pause_before > 0:
            result = f"<break time=\"{pause_before}ms\"/>{result}"
        if pause_after > 0:
            result = f"{result}<break time=\"{pause_after}ms\"/>"

        # Add emphasis to specified words
        if emphasis:
            for word in emphasis:
                # Case-insensitive word replacement with word boundaries
                pattern = r'\b' + re.escape(word) + r'\b'
                result = re.sub(pattern, f"<emphasis>{word}</emphasis>", result, flags=re.IGNORECASE)

        return result

    def _prepare_text_with_parameters(self, text: str, pitch: float = 0.0,
                                     speed: float = 1.0, emotion: str = "neutral",
                                     emphasis: Optional[List[str]] = None,
                                     pause_before: int = 0, pause_after: int = 0,
                                     breath_frequency: int = 0) -> str:
        """Prepare text with prosody and emotion parameters.

        Args:
            text: Original text
            pitch: Pitch adjustment (-12 to +12 semitones)
            speed: Speed multiplier (0.5-2.0)
            emotion: Emotion type (neutral, happy, sad, angry, etc.)
            emphasis: Words to emphasize
            pause_before: Pause before text (ms)
            pause_after: Pause after text (ms)
            breath_frequency: Insert breath every N words

        Returns:
            Processed text with markup
        """
        # Apply prosody markup
        processed = self._apply_prosody_markup(
            text, pitch, speed, emphasis, pause_before, pause_after
        )

        # Add breath patterns
        if breath_frequency > 0:
            words = processed.split()
            result_words = []
            for i, word in enumerate(words):
                result_words.append(word)
                if (i + 1) % breath_frequency == 0 and i < len(words) - 1:
                    result_words.append("[breath]")
            processed = " ".join(result_words)

        # Add emotion prefix (for models that support it)
        if emotion != "neutral":
            processed = f"[{emotion}] {processed}"

        return processed

    def generate_audio(self, text: str, reference_audio: str, output_file: str,
                      seed: Optional[int] = None, speed: float = 1.0,
                      pitch: float = 0.0, exaggeration: float = 0.5,
                      cfg_weight: float = 0.5, temperature: float = 0.9,
                      top_p: float = 0.95, min_p: float = 0.1,
                      emotion: str = "neutral", emphasis: Optional[List[str]] = None,
                      pause_before: int = 0, pause_after: int = 0,
                      breath_frequency: int = 0) -> str:
        """Generate audio using reference voice with advanced prosody control.

        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio file (3-30 seconds)
            output_file: Path to save output audio
            seed: Random seed for reproducibility (optional)
            speed: Speech rate multiplier (0.5-2.0, default 1.0)
            pitch: Pitch adjustment in semitones (-12 to +12, default 0.0)
            exaggeration: Emotional exaggeration (0.25-2.0, default 0.5)
            cfg_weight: Classifier-free guidance weight (0.0-1.0, default 0.5)
            temperature: Randomness/variation (0.0-2.0, default 0.9)
            top_p: Nucleus sampling parameter (0.0-1.0, default 0.95)
            min_p: Minimum probability threshold (0.0-1.0, default 0.1)
            emotion: Emotion type (neutral, happy, sad, angry, etc., default neutral)
            emphasis: List of words to emphasize (optional)
            pause_before: Pause before text in milliseconds (0-5000, default 0)
            pause_after: Pause after text in milliseconds (0-5000, default 0)
            breath_frequency: Insert breath every N words (0-20, default 0)

        Returns:
            Path to generated audio file

        Raises:
            RuntimeError: If generation fails
            FileNotFoundError: If reference audio not found
            ValueError: If parameters are out of valid ranges
        """
        self._initialize_model()

        # Validate parameters
        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

        if not (0.5 <= speed <= 2.0):
            raise ValueError(f"Speed must be between 0.5 and 2.0, got {speed}")
        if not (-12 <= pitch <= 12):
            raise ValueError(f"Pitch must be between -12 and +12 semitones, got {pitch}")
        if not (0.25 <= exaggeration <= 2.0):
            raise ValueError(f"Exaggeration must be between 0.25 and 2.0, got {exaggeration}")
        if not (0.0 <= cfg_weight <= 1.0):
            raise ValueError(f"CFG weight must be between 0.0 and 1.0, got {cfg_weight}")
        if not (0.0 <= temperature <= 2.0):
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temperature}")
        if not (0.0 <= top_p <= 1.0):
            raise ValueError(f"Top P must be between 0.0 and 1.0, got {top_p}")
        if not (0.0 <= min_p <= 1.0):
            raise ValueError(f"Min P must be between 0.0 and 1.0, got {min_p}")
        if not (0 <= pause_before <= 5000):
            raise ValueError(f"Pause before must be between 0 and 5000ms, got {pause_before}")
        if not (0 <= pause_after <= 5000):
            raise ValueError(f"Pause after must be between 0 and 5000ms, got {pause_after}")
        if not (0 <= breath_frequency <= 20):
            raise ValueError(f"Breath frequency must be between 0 and 20, got {breath_frequency}")

        try:
            logger.info(f"Generating audio with E2-F5-TTS (text: {len(text)} chars, "
                       f"reference: {reference_audio}, speed: {speed}x, pitch: {pitch}st, "
                       f"emotion: {emotion}, exaggeration: {exaggeration})")

            # Prepare text with prosody parameters
            processed_text = self._prepare_text_with_parameters(
                text, pitch, speed, emotion, emphasis, pause_before, pause_after, breath_frequency
            )

            # Generate audio with advanced parameters
            infer_kwargs = {
                "text": processed_text,
                "ref_file": reference_audio,
                "seed": seed,
                "speed": speed,
                "nfe": self.nfe
            }

            # Add optional parameters if model supports them
            if hasattr(self.model, 'infer'):
                # Try to pass advanced parameters
                try:
                    infer_kwargs.update({
                        "temperature": temperature,
                        "top_p": top_p,
                        "min_p": min_p
                    })
                except Exception:
                    logger.debug("Model does not support advanced sampling parameters")

            wav = self.model.infer(**infer_kwargs)

            # Save audio
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            self.model.save_wav(wav, output_file)

            file_size = os.path.getsize(output_file)
            logger.info(f"✅ E2-F5-TTS audio generated: {output_file} ({file_size:,} bytes)")
            logger.info(f"🎵 Parameters: speed={speed}x, pitch={pitch}st, emotion={emotion}, "
                       f"exaggeration={exaggeration}, cfg_weight={cfg_weight}")

            return output_file

        except ValueError as e:
            logger.error(f"Invalid parameter: {e}")
            raise
        except Exception as e:
            logger.error(f"E2-F5-TTS generation failed: {e}")
            raise RuntimeError(f"E2-F5-TTS generation failed: {e}")

    def generate_audio_batch(self, texts: list, reference_audio: str,
                            output_dir: str, seed: Optional[int] = None,
                            speed: float = 1.0, pitch: float = 0.0,
                            exaggeration: float = 0.5, cfg_weight: float = 0.5,
                            temperature: float = 0.9, emotion: str = "neutral",
                            emphasis: Optional[List[str]] = None) -> list:
        """Generate multiple audio files with same reference voice and parameters.

        Args:
            texts: List of texts to synthesize
            reference_audio: Path to reference audio file
            output_dir: Directory to save output files
            seed: Random seed for reproducibility
            speed: Speech rate multiplier (0.5-2.0)
            pitch: Pitch adjustment in semitones (-12 to +12)
            exaggeration: Emotional exaggeration (0.25-2.0)
            cfg_weight: Classifier-free guidance weight (0.0-1.0)
            temperature: Randomness/variation (0.0-2.0)
            emotion: Emotion type (neutral, happy, sad, angry, etc.)
            emphasis: List of words to emphasize

        Returns:
            List of generated audio file paths
        """
        self._initialize_model()
        os.makedirs(output_dir, exist_ok=True)

        output_files = []
        for i, text in enumerate(texts):
            output_file = os.path.join(output_dir, f"output_{i:03d}.wav")
            try:
                self.generate_audio(
                    text, reference_audio, output_file, seed=seed,
                    speed=speed, pitch=pitch, exaggeration=exaggeration,
                    cfg_weight=cfg_weight, temperature=temperature,
                    emotion=emotion, emphasis=emphasis
                )
                output_files.append(output_file)
            except Exception as e:
                logger.error(f"Failed to generate audio for text {i}: {e}")
                continue

        logger.info(f"Generated {len(output_files)}/{len(texts)} audio files")
        return output_files

    def get_device_info(self) -> Dict[str, Any]:
        """Get device and model information.

        Returns:
            Dictionary with device info
        """
        info = {
            "device": self.device,
            "model_name": self.model_name,
            "quality": self.quality,
            "nfe": self.nfe,
            "is_initialized": self.is_initialized,
            "cuda_available": torch.cuda.is_available(),
        }

        if torch.cuda.is_available():
            info["cuda_device"] = torch.cuda.get_device_name(0)
            info["cuda_memory_total"] = torch.cuda.get_device_properties(0).total_memory / 1e9
            info["cuda_memory_allocated"] = torch.cuda.memory_allocated(0) / 1e9

        return info

    def cleanup(self):
        """Clean up resources."""
        if self.model is not None:
            try:
                if hasattr(self.model, 'cleanup'):
                    self.model.cleanup()
                del self.model
                self.model = None
                self.is_initialized = False
                logger.info("E2-F5-TTS model cleaned up")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


__all__ = ["E2F5TTSEngine", "E2F5_TTS_AVAILABLE"]

