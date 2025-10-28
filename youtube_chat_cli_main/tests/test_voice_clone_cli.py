"""Tests for voice cloning CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from youtube_chat_cli_main.cli.commands.voice_clone import voice_clone


class TestVoiceCloneGenerateCommand:
    """Test voice-clone generate command."""

    def test_generate_basic(self):
        """Test basic generate command."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello world',
                '--output', '/tmp/output.wav'
            ])

            assert result.exit_code == 0
            assert 'Speech generated successfully' in result.output
            mock_service.generate_speech.assert_called_once()

    def test_generate_with_emotion(self):
        """Test generate command with emotion."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'I am happy!',
                '--output', '/tmp/output.wav',
                '--emotion', 'happy'
            ])

            assert result.exit_code == 0
            assert 'happy' in result.output.lower()

    def test_generate_with_pitch(self):
        """Test generate command with pitch adjustment."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello',
                '--output', '/tmp/output.wav',
                '--pitch', '3'
            ])

            assert result.exit_code == 0
            assert '+3' in result.output

    def test_generate_with_speed(self):
        """Test generate command with speed adjustment."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello',
                '--output', '/tmp/output.wav',
                '--speed', '1.5'
            ])

            assert result.exit_code == 0
            assert '1.5' in result.output

    def test_generate_with_emphasis(self):
        """Test generate command with emphasis."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'This is important',
                '--output', '/tmp/output.wav',
                '--emphasis', 'important',
                '--emphasis', 'this'
            ])

            assert result.exit_code == 0
            assert 'important' in result.output

    def test_generate_with_pauses(self):
        """Test generate command with pause parameters."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello',
                '--output', '/tmp/output.wav',
                '--pause-before', '500',
                '--pause-after', '300'
            ])

            assert result.exit_code == 0
            assert '500' in result.output
            assert '300' in result.output

    def test_generate_with_breath_frequency(self):
        """Test generate command with breath frequency."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello world',
                '--output', '/tmp/output.wav',
                '--breath-frequency', '5'
            ])

            assert result.exit_code == 0
            assert '5' in result.output

    def test_generate_with_seed(self):
        """Test generate command with seed for reproducibility."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello',
                '--output', '/tmp/output.wav',
                '--seed', '42'
            ])

            assert result.exit_code == 0
            assert '42' in result.output

    def test_generate_with_all_parameters(self):
        """Test generate command with all parameters."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.return_value = "/tmp/output.wav"

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello world',
                '--output', '/tmp/output.wav',
                '--speed', '1.2',
                '--pitch', '3',
                '--exaggeration', '0.7',
                '--cfg-weight', '0.5',
                '--temperature', '0.9',
                '--top-p', '0.95',
                '--min-p', '0.1',
                '--emotion', 'happy',
                '--emphasis', 'hello',
                '--pause-before', '500',
                '--pause-after', '300',
                '--breath-frequency', '5',
                '--seed', '42'
            ])

            assert result.exit_code == 0
            assert 'Speech generated successfully' in result.output

    def test_generate_missing_text(self):
        """Test generate command without text."""
        runner = CliRunner()

        result = runner.invoke(voice_clone, [
            'generate',
            '--voice-id', '1',
            '--output', '/tmp/output.wav'
        ])

        assert result.exit_code != 0

    def test_generate_missing_voice_id(self):
        """Test generate command without voice ID."""
        runner = CliRunner()

        result = runner.invoke(voice_clone, [
            'generate',
            '--text', 'Hello',
            '--output', '/tmp/output.wav'
        ])

        assert result.exit_code != 0

    def test_generate_error_handling(self):
        """Test generate command error handling."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_speech.side_effect = ValueError("Invalid parameter")

            result = runner.invoke(voice_clone, [
                'generate',
                '--voice-id', '1',
                '--text', 'Hello',
                '--output', '/tmp/output.wav'
            ])

            assert result.exit_code != 0
            assert 'Error' in result.output


class TestVoiceClonePresetsCommand:
    """Test voice-clone presets command."""

    def test_presets_command(self):
        """Test presets command displays all presets."""
        runner = CliRunner()

        result = runner.invoke(voice_clone, ['presets'])

        assert result.exit_code == 0
        assert 'NEUTRAL' in result.output
        assert 'HAPPY' in result.output
        assert 'SAD' in result.output
        assert 'ANGRY' in result.output
        assert 'EXCITED' in result.output
        assert 'CALM' in result.output
        assert 'PROFESSIONAL' in result.output
        assert 'DRAMATIC' in result.output

    def test_presets_command_shows_descriptions(self):
        """Test presets command shows descriptions."""
        runner = CliRunner()

        result = runner.invoke(voice_clone, ['presets'])

        assert result.exit_code == 0
        assert 'Natural' in result.output or 'balanced' in result.output
        assert 'Upbeat' in result.output or 'cheerful' in result.output

    def test_presets_command_shows_parameters(self):
        """Test presets command shows parameter values."""
        runner = CliRunner()

        result = runner.invoke(voice_clone, ['presets'])

        assert result.exit_code == 0
        assert 'Speed' in result.output
        assert 'Pitch' in result.output
        assert 'Exaggeration' in result.output
        assert 'Emotion' in result.output


class TestVoiceCloneListCommand:
    """Test voice-clone list command."""

    def test_list_command(self):
        """Test list command."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.list_voices.return_value = [
                {'id': 1, 'name': 'Voice 1', 'created_at': '2025-01-01'},
                {'id': 2, 'name': 'Voice 2', 'created_at': '2025-01-02'}
            ]

            result = runner.invoke(voice_clone, ['list'])

            assert result.exit_code == 0
            assert 'Voice 1' in result.output
            assert 'Voice 2' in result.output


class TestVoiceCloneDeleteCommand:
    """Test voice-clone delete command."""

    def test_delete_command_with_confirmation(self):
        """Test delete command with confirmation."""
        runner = CliRunner()

        with patch('youtube_chat_cli_main.cli.commands.voice_clone.VoiceCloningService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_voice.return_value = None

            result = runner.invoke(voice_clone, [
                'delete',
                '--voice-id', '1'
            ], input='y\n')

            assert result.exit_code == 0
            assert 'deleted' in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

