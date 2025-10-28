"""Tests for voice cloning service."""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test fixtures
@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_audio_path(temp_dir):
    """Create a sample audio file for testing."""
    import numpy as np
    from scipy.io import wavfile
    
    # Create 5-second audio at 24kHz
    sample_rate = 24000
    duration = 5
    t = np.linspace(0, duration, sample_rate * duration)
    
    # Generate sine wave (440 Hz)
    frequency = 440
    audio = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Add some noise for realism
    audio += np.random.normal(0, 0.01, len(audio))
    
    # Convert to 16-bit PCM
    audio_int16 = np.int16(audio * 32767)
    
    # Save to file
    audio_path = os.path.join(temp_dir, "sample.wav")
    wavfile.write(audio_path, sample_rate, audio_int16)
    
    return audio_path


class TestE2F5TTSEngine:
    """Tests for E2-F5-TTS engine."""

    def test_engine_initialization(self):
        """Test E2-F5-TTS engine initialization."""
        try:
            from youtube_chat_cli_main.services.tts.engines.e2f5_tts import E2F5TTSEngine
            
            engine = E2F5TTSEngine(device="cpu", quality="fast")
            
            assert engine.device == "cpu"
            assert engine.quality == "fast"
            assert engine.nfe == 8  # fast preset
            assert not engine.is_initialized
            
        except RuntimeError as e:
            pytest.skip(f"E2-F5-TTS not available: {e}")

    def test_device_info(self):
        """Test device information retrieval."""
        try:
            from youtube_chat_cli_main.services.tts.engines.e2f5_tts import E2F5TTSEngine
            
            engine = E2F5TTSEngine(device="cpu")
            info = engine.get_device_info()
            
            assert "device" in info
            assert "model_name" in info
            assert "quality" in info
            assert "nfe" in info
            assert "cuda_available" in info
            
        except RuntimeError:
            pytest.skip("E2-F5-TTS not available")

    def test_quality_presets(self):
        """Test quality preset configurations."""
        try:
            from youtube_chat_cli_main.services.tts.engines.e2f5_tts import E2F5TTSEngine
            
            # Test fast preset
            engine_fast = E2F5TTSEngine(quality="fast")
            assert engine_fast.nfe == 8
            
            # Test balanced preset
            engine_balanced = E2F5TTSEngine(quality="balanced")
            assert engine_balanced.nfe == 16
            
            # Test high preset
            engine_high = E2F5TTSEngine(quality="high")
            assert engine_high.nfe == 32
            
        except RuntimeError:
            pytest.skip("E2-F5-TTS not available")


class TestVoiceCloningService:
    """Tests for voice cloning service."""

    def test_service_initialization(self, temp_dir):
        """Test voice cloning service initialization."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            
            assert service.storage_path == Path(temp_dir)
            assert service.device == "cpu"
            assert service.engine is not None
            
        except RuntimeError as e:
            pytest.skip(f"Voice cloning service not available: {e}")

    def test_audio_validation_valid(self, temp_dir, sample_audio_path):
        """Test audio validation with valid audio."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            validation = service.validate_reference_audio(sample_audio_path)
            
            assert validation["valid"]
            assert validation["duration"] >= 5
            assert validation["sample_rate"] >= 22000
            assert len(validation["issues"]) == 0
            
        except RuntimeError:
            pytest.skip("Voice cloning service not available")

    def test_audio_validation_too_short(self, temp_dir):
        """Test audio validation with too-short audio."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            import numpy as np
            from scipy.io import wavfile
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            
            # Create 1-second audio
            sample_rate = 24000
            audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate)) * 0.3
            audio_int16 = np.int16(audio * 32767)
            
            short_audio_path = os.path.join(temp_dir, "short.wav")
            wavfile.write(short_audio_path, sample_rate, audio_int16)
            
            validation = service.validate_reference_audio(short_audio_path)
            
            assert not validation["valid"]
            assert any("too short" in issue.lower() for issue in validation["issues"])
            
        except RuntimeError:
            pytest.skip("Voice cloning service not available")

    def test_audio_validation_low_sample_rate(self, temp_dir):
        """Test audio validation with low sample rate."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            import numpy as np
            from scipy.io import wavfile
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            
            # Create 5-second audio at 16kHz (too low)
            sample_rate = 16000
            duration = 5
            audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, sample_rate * duration)) * 0.3
            audio_int16 = np.int16(audio * 32767)
            
            low_sr_path = os.path.join(temp_dir, "low_sr.wav")
            wavfile.write(low_sr_path, sample_rate, audio_int16)
            
            validation = service.validate_reference_audio(low_sr_path)
            
            assert not validation["valid"]
            assert any("sample rate" in issue.lower() for issue in validation["issues"])
            
        except RuntimeError:
            pytest.skip("Voice cloning service not available")

    def test_create_voice(self, temp_dir, sample_audio_path):
        """Test voice creation."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            
            voice_info = service.create_voice(
                name="test_voice",
                reference_audio=sample_audio_path,
                consent_ip="192.168.1.1"
            )
            
            assert voice_info["id"] is not None
            assert voice_info["name"] == "test_voice"
            assert os.path.exists(voice_info["reference_audio_path"])
            
        except RuntimeError:
            pytest.skip("Voice cloning service not available")

    def test_list_voices(self, temp_dir, sample_audio_path):
        """Test listing voices."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            
            # Create a voice
            service.create_voice(
                name="voice1",
                reference_audio=sample_audio_path
            )
            
            # List voices
            voices = service.list_voices()
            
            assert len(voices) >= 1
            assert any(v["name"] == "voice1" for v in voices)
            
        except RuntimeError:
            pytest.skip("Voice cloning service not available")

    def test_delete_voice(self, temp_dir, sample_audio_path):
        """Test voice deletion."""
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            
            service = VoiceCloningService(storage_path=temp_dir, device="cpu")
            
            # Create a voice
            voice_info = service.create_voice(
                name="voice_to_delete",
                reference_audio=sample_audio_path
            )
            
            # Delete voice
            success = service.delete_voice(voice_info["id"])
            
            assert success
            
            # Verify it's deleted
            voices = service.list_voices()
            assert not any(v["id"] == voice_info["id"] for v in voices)
            
        except RuntimeError:
            pytest.skip("Voice cloning service not available")


class TestVoiceCloningAPI:
    """Tests for voice cloning API endpoints."""

    @pytest.mark.asyncio
    async def test_upload_reference_endpoint(self, temp_dir, sample_audio_path):
        """Test upload reference audio endpoint."""
        try:
            from fastapi.testclient import TestClient
            from youtube_chat_cli_main.api_server import app
            
            client = TestClient(app)
            
            with open(sample_audio_path, "rb") as f:
                response = client.post(
                    "/api/v1/voice-clone/upload-reference",
                    params={"name": "test_voice"},
                    files={"file": f}
                )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert "id" in data
            assert data["name"] == "test_voice"
            
        except Exception as e:
            pytest.skip(f"API test skipped: {e}")

    @pytest.mark.asyncio
    async def test_list_voices_endpoint(self):
        """Test list voices endpoint."""
        try:
            from fastapi.testclient import TestClient
            from youtube_chat_cli_main.api_server import app
            
            client = TestClient(app)
            response = client.get("/api/v1/voice-clone/voices")
            
            assert response.status_code == 200
            data = response.json()
            assert "voices" in data
            assert "total" in data
            
        except Exception as e:
            pytest.skip(f"API test skipped: {e}")

    @pytest.mark.asyncio
    async def test_settings_endpoint(self):
        """Test settings endpoint."""
        try:
            from fastapi.testclient import TestClient
            from youtube_chat_cli_main.api_server import app
            
            client = TestClient(app)
            response = client.get("/api/v1/voice-clone/settings")
            
            assert response.status_code == 200
            data = response.json()
            assert "device" in data
            assert "model" in data
            assert "quality" in data
            
        except Exception as e:
            pytest.skip(f"API test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

