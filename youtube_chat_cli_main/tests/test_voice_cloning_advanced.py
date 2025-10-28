"""Tests for advanced voice cloning parameters and functionality."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService, VALID_EMOTIONS
from youtube_chat_cli_main.services.tts.engines.e2f5_tts import E2F5TTSEngine


class TestVoiceParameterValidation:
    """Test voice parameter validation."""

    def test_validate_voice_parameters_valid(self):
        """Test validation with valid parameters."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        result = service.validate_voice_parameters(
            speed=1.0, pitch=0, exaggeration=0.5, cfg_weight=0.5,
            temperature=0.9, emotion="neutral"
        )

        assert result["valid"] is True
        assert result["speed"] == 1.0
        assert result["emotion"] == "neutral"

    def test_validate_voice_parameters_speed_out_of_range(self):
        """Test validation with speed out of range."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        with pytest.raises(ValueError, match="Speed must be 0.5-2.0"):
            service.validate_voice_parameters(speed=3.0)

    def test_validate_voice_parameters_pitch_out_of_range(self):
        """Test validation with pitch out of range."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        with pytest.raises(ValueError, match="Pitch must be -12 to"):
            service.validate_voice_parameters(pitch=15)

    def test_validate_voice_parameters_invalid_emotion(self):
        """Test validation with invalid emotion."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        with pytest.raises(ValueError, match="Invalid emotion"):
            service.validate_voice_parameters(emotion="invalid_emotion")

    def test_validate_voice_parameters_all_emotions(self):
        """Test validation with all valid emotions."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        for emotion in VALID_EMOTIONS:
            result = service.validate_voice_parameters(emotion=emotion)
            assert result["emotion"] == emotion

    def test_validate_voice_parameters_exaggeration_range(self):
        """Test exaggeration parameter range validation."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        # Valid range
        result = service.validate_voice_parameters(exaggeration=0.25)
        assert result["exaggeration"] == 0.25

        result = service.validate_voice_parameters(exaggeration=2.0)
        assert result["exaggeration"] == 2.0

        # Out of range
        with pytest.raises(ValueError, match="Exaggeration must be 0.25-2.0"):
            service.validate_voice_parameters(exaggeration=0.1)

    def test_validate_voice_parameters_cfg_weight_range(self):
        """Test CFG weight parameter range validation."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        result = service.validate_voice_parameters(cfg_weight=0.5)
        assert result["cfg_weight"] == 0.5

        with pytest.raises(ValueError, match="CFG weight must be 0.0-1.0"):
            service.validate_voice_parameters(cfg_weight=1.5)

    def test_validate_voice_parameters_temperature_range(self):
        """Test temperature parameter range validation."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        result = service.validate_voice_parameters(temperature=0.9)
        assert result["temperature"] == 0.9

        with pytest.raises(ValueError, match="Temperature must be 0.0-2.0"):
            service.validate_voice_parameters(temperature=2.5)

    def test_validate_voice_parameters_pause_range(self):
        """Test pause parameter range validation."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        result = service.validate_voice_parameters(pause_before=500, pause_after=1000)
        assert result["pause_before"] == 500
        assert result["pause_after"] == 1000

        with pytest.raises(ValueError, match="Pause before must be 0-5000ms"):
            service.validate_voice_parameters(pause_before=6000)

    def test_validate_voice_parameters_breath_frequency_range(self):
        """Test breath frequency parameter range validation."""
        service = Mock(spec=VoiceCloningService)
        service.validate_voice_parameters = VoiceCloningService.validate_voice_parameters.__get__(service)

        result = service.validate_voice_parameters(breath_frequency=5)
        assert result["breath_frequency"] == 5

        with pytest.raises(ValueError, match="Breath frequency must be 0-20"):
            service.validate_voice_parameters(breath_frequency=25)


class TestE2F5TTSProsodyMarkup:
    """Test E2F5TTS prosody markup generation."""

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_apply_prosody_markup_with_emphasis(self, mock_f5tts):
        """Test prosody markup with emphasis."""
        engine = E2F5TTSEngine()
        text = "This is important"
        result = engine._apply_prosody_markup(text, emphasis=["important"])

        assert "<emphasis>important</emphasis>" in result

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_apply_prosody_markup_with_pauses(self, mock_f5tts):
        """Test prosody markup with pauses."""
        engine = E2F5TTSEngine()
        text = "Hello world"
        result = engine._apply_prosody_markup(text, pause_before=500, pause_after=300)

        assert '<break time="500ms"/>' in result
        assert '<break time="300ms"/>' in result

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_prepare_text_with_parameters_emotion(self, mock_f5tts):
        """Test text preparation with emotion."""
        engine = E2F5TTSEngine()
        text = "Hello world"
        result = engine._prepare_text_with_parameters(text, emotion="happy")

        assert "[happy]" in result

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_prepare_text_with_parameters_breath(self, mock_f5tts):
        """Test text preparation with breath frequency."""
        engine = E2F5TTSEngine()
        text = "one two three four five"
        result = engine._prepare_text_with_parameters(text, breath_frequency=2)

        assert "[breath]" in result


class TestE2F5TTSParameterValidation:
    """Test E2F5TTS parameter validation in generate_audio."""

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_generate_audio_invalid_speed(self, mock_f5tts):
        """Test generate_audio with invalid speed."""
        engine = E2F5TTSEngine()

        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            with pytest.raises(ValueError, match="Speed must be between"):
                engine.generate_audio(
                    text="test",
                    reference_audio=tmp.name,
                    output_file="output.wav",
                    speed=3.0
                )

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_generate_audio_invalid_pitch(self, mock_f5tts):
        """Test generate_audio with invalid pitch."""
        engine = E2F5TTSEngine()

        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            with pytest.raises(ValueError, match="Pitch must be between"):
                engine.generate_audio(
                    text="test",
                    reference_audio=tmp.name,
                    output_file="output.wav",
                    pitch=15
                )

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_generate_audio_invalid_exaggeration(self, mock_f5tts):
        """Test generate_audio with invalid exaggeration."""
        engine = E2F5TTSEngine()

        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            with pytest.raises(ValueError, match="Exaggeration must be between"):
                engine.generate_audio(
                    text="test",
                    reference_audio=tmp.name,
                    output_file="output.wav",
                    exaggeration=3.0
                )

    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.E2F5_TTS_AVAILABLE', True)
    @patch('youtube_chat_cli_main.services.tts.engines.e2f5_tts.F5TTS')
    def test_generate_audio_missing_reference(self, mock_f5tts):
        """Test generate_audio with missing reference audio."""
        engine = E2F5TTSEngine()

        with pytest.raises(FileNotFoundError):
            engine.generate_audio(
                text="test",
                reference_audio="/nonexistent/file.wav",
                output_file="output.wav"
            )


class TestVoiceCloningServiceAdvanced:
    """Test VoiceCloningService with advanced parameters."""

    @patch('youtube_chat_cli_main.services.voice_cloning_service.E2F5TTSEngine')
    @patch('youtube_chat_cli_main.services.voice_cloning_service.get_database')
    def test_generate_speech_with_all_parameters(self, mock_db, mock_engine_class):
        """Test generate_speech with all advanced parameters."""
        mock_engine = MagicMock()
        mock_engine_class.return_value = mock_engine
        mock_engine.generate_audio.return_value = "/tmp/output.wav"

        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_cursor = MagicMock()
        mock_db_instance.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("/tmp/ref.wav", '{"seed": 42}')

        service = VoiceCloningService()

        result = service.generate_speech(
            voice_id=1,
            text="Hello world",
            output_file="/tmp/output.wav",
            speed=1.2,
            pitch=3,
            exaggeration=0.7,
            cfg_weight=0.5,
            temperature=0.9,
            emotion="happy",
            emphasis=["hello"],
            pause_before=500,
            pause_after=300,
            breath_frequency=5,
            seed=42
        )

        assert result == "/tmp/output.wav"
        mock_engine.generate_audio.assert_called_once()

    @patch('youtube_chat_cli_main.services.voice_cloning_service.E2F5TTSEngine')
    @patch('youtube_chat_cli_main.services.voice_cloning_service.get_database')
    def test_generate_speech_invalid_parameters(self, mock_db, mock_engine_class):
        """Test generate_speech with invalid parameters."""
        mock_engine = MagicMock()
        mock_engine_class.return_value = mock_engine

        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance

        service = VoiceCloningService()

        with pytest.raises(ValueError):
            service.generate_speech(
                voice_id=1,
                text="Hello",
                output_file="/tmp/output.wav",
                speed=3.0  # Invalid speed
            )


class TestAPIParameterModels:
    """Test API Pydantic models for parameter validation."""

    def test_voice_generate_request_valid(self):
        """Test VoiceGenerateRequest with valid data."""
        from youtube_chat_cli_main.api.routes.voice_cloning import VoiceGenerateRequest

        request = VoiceGenerateRequest(
            voice_id=1,
            text="Hello world",
            speed=1.0,
            pitch=0,
            exaggeration=0.5,
            emotion="neutral"
        )

        assert request.voice_id == 1
        assert request.text == "Hello world"
        assert request.speed == 1.0

    def test_voice_generate_request_invalid_speed(self):
        """Test VoiceGenerateRequest with invalid speed."""
        from youtube_chat_cli_main.api.routes.voice_cloning import VoiceGenerateRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            VoiceGenerateRequest(
                voice_id=1,
                text="Hello",
                speed=3.0  # Out of range
            )

    def test_voice_generate_request_invalid_pitch(self):
        """Test VoiceGenerateRequest with invalid pitch."""
        from youtube_chat_cli_main.api.routes.voice_cloning import VoiceGenerateRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            VoiceGenerateRequest(
                voice_id=1,
                text="Hello",
                pitch=15  # Out of range
            )

    def test_voice_generate_request_with_emphasis(self):
        """Test VoiceGenerateRequest with emphasis."""
        from youtube_chat_cli_main.api.routes.voice_cloning import VoiceGenerateRequest

        request = VoiceGenerateRequest(
            voice_id=1,
            text="This is important",
            emphasis=["important", "this"]
        )

        assert request.emphasis == ["important", "this"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

