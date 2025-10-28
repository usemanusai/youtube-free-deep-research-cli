"""Voice cloning CLI commands."""

import click
import logging
from pathlib import Path
from typing import Optional
from colorama import Fore, Style

logger = logging.getLogger(__name__)


@click.group()
def voice_clone():
    """Voice cloning commands for zero-shot TTS with reference audio."""
    pass


@voice_clone.command()
@click.option('--reference', '-r', required=True, type=click.Path(exists=True),
              help='Path to reference audio file (WAV, MP3, FLAC)')
@click.option('--name', '-n', required=True, help='Name for the cloned voice')
@click.option('--metadata', '-m', default=None, help='Optional metadata (JSON string)')
def create(reference: str, name: str, metadata: Optional[str]):
    """Create a new cloned voice from reference audio.

    Example:
        youtube-chat voice-clone create --reference voice.wav --name "my_voice"
    """
    try:
        from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

        click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
        click.echo(Fore.CYAN + "║   Voice Cloning - Create New Voice                        ║")
        click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
        click.echo()

        # Initialize service
        service = VoiceCloningService()
        click.echo(Fore.YELLOW + "🔍 Validating reference audio...")

        # Validate audio
        validation = service.validate_reference_audio(reference)
        if not validation['valid']:
            click.echo(Fore.RED + f"❌ Invalid audio: {', '.join(validation['issues'])}")
            return

        click.echo(Fore.GREEN + f"✅ Audio valid - Duration: {validation['duration']:.1f}s, "
                   f"Sample rate: {validation['sample_rate']}Hz, SNR: {validation['snr_db']:.1f}dB")
        click.echo()

        # Create voice
        click.echo(Fore.YELLOW + f"🎤 Creating voice '{name}'...")
        voice_info = service.create_voice(
            name=name,
            reference_audio=reference,
            metadata=metadata
        )

        click.echo(Fore.GREEN + f"✅ Voice created successfully!")
        click.echo(f"   Voice ID: {voice_info['id']}")
        click.echo(f"   Name: {voice_info['name']}")
        click.echo(f"   Created: {voice_info['created_at']}")
        click.echo()

    except ValueError as e:
        click.echo(Fore.RED + f"❌ Error: {e}")
    except Exception as e:
        click.echo(Fore.RED + f"❌ Failed to create voice: {e}")
        logger.error(f"Voice creation error: {e}", exc_info=True)


@voice_clone.command()
def list():
    """List all cloned voices."""
    try:
        from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

        click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
        click.echo(Fore.CYAN + "║   Voice Cloning - List Voices                            ║")
        click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
        click.echo()

        service = VoiceCloningService()
        voices = service.list_voices()

        if not voices:
            click.echo(Fore.YELLOW + "No voices found. Create one with: voice-clone create")
            return

        click.echo(Fore.GREEN + f"Found {len(voices)} voice(s):\n")

        for voice in voices:
            click.echo(Fore.CYAN + f"  ID: {voice['id']}")
            click.echo(f"  Name: {voice['name']}")
            click.echo(f"  Created: {voice['created_at']}")
            click.echo(f"  Usage count: {voice['usage_count']}")
            if voice.get('last_used'):
                click.echo(f"  Last used: {voice['last_used']}")
            click.echo()

    except Exception as e:
        click.echo(Fore.RED + f"❌ Failed to list voices: {e}")
        logger.error(f"List voices error: {e}", exc_info=True)


@voice_clone.command()
@click.option('--voice-id', '-v', required=True, type=int, help='Voice ID')
@click.option('--text', '-t', required=True, help='Text to generate speech from')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output audio file path')
@click.option('--speed', '-s', default=1.0, type=float,
              help='Speech speed multiplier (0.5-2.0, default 1.0)')
@click.option('--pitch', '-p', default=0.0, type=float,
              help='Pitch adjustment in semitones (-12 to +12, default 0)')
@click.option('--exaggeration', '-e', default=0.5, type=float,
              help='Emotional exaggeration (0.25-2.0, default 0.5)')
@click.option('--cfg-weight', default=0.5, type=float,
              help='CFG weight for rhythm control (0.0-1.0, default 0.5)')
@click.option('--temperature', default=0.9, type=float,
              help='Randomness/variation (0.0-2.0, default 0.9)')
@click.option('--top-p', default=0.95, type=float,
              help='Nucleus sampling parameter (0.0-1.0, default 0.95)')
@click.option('--min-p', default=0.1, type=float,
              help='Minimum probability threshold (0.0-1.0, default 0.1)')
@click.option('--emotion', default='neutral',
              type=click.Choice(['neutral', 'happy', 'sad', 'angry', 'joyful', 'excited',
                               'surprised', 'curious', 'confident', 'empathetic']),
              help='Emotion type (default neutral)')
@click.option('--emphasis', multiple=True,
              help='Words to emphasize (can be used multiple times)')
@click.option('--pause-before', default=0, type=int,
              help='Pause before speech in milliseconds (0-5000, default 0)')
@click.option('--pause-after', default=0, type=int,
              help='Pause after speech in milliseconds (0-5000, default 0)')
@click.option('--breath-frequency', default=0, type=int,
              help='Insert breath every N words (0-20, default 0)')
@click.option('--seed', default=None, type=int,
              help='Random seed for reproducibility (optional)')
@click.option('--quality', '-q', default='balanced', type=click.Choice(['fast', 'balanced', 'high']),
              help='Quality preset (fast, balanced, high)')
def generate(voice_id: int, text: str, output: str, speed: float, pitch: float,
            exaggeration: float, cfg_weight: float, temperature: float, top_p: float,
            min_p: float, emotion: str, emphasis: tuple, pause_before: int,
            pause_after: int, breath_frequency: int, seed: Optional[int], quality: str):
    """Generate speech using a cloned voice with advanced prosody control.

    Examples:
        # Basic generation
        youtube-chat voice-clone generate --voice-id 1 --text "Hello world" --output output.wav

        # With emotion and pitch
        youtube-chat voice-clone generate --voice-id 1 --text "I'm so happy!" \\
          --output happy.wav --emotion happy --pitch 3 --exaggeration 0.7

        # With emphasis and pauses
        youtube-chat voice-clone generate --voice-id 1 --text "This is important" \\
          --output important.wav --emphasis "important" --pause-before 500

        # Professional tone
        youtube-chat voice-clone generate --voice-id 1 --text "Quarterly report" \\
          --output report.wav --emotion confident --speed 1.0 --pitch 1
    """
    try:
        from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

        click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
        click.echo(Fore.CYAN + "║   Voice Cloning - Generate Speech (Advanced)             ║")
        click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
        click.echo()

        service = VoiceCloningService()

        # Display parameters
        click.echo(Fore.YELLOW + f"🎵 Generating speech ({quality} quality)...")
        click.echo(f"   Voice ID: {voice_id}")
        click.echo(f"   Text length: {len(text)} characters")
        click.echo()

        click.echo(Fore.CYAN + "📊 Voice Parameters:")
        click.echo(f"   Speed: {speed}x")
        click.echo(f"   Pitch: {pitch:+.1f} semitones")
        click.echo(f"   Emotion: {emotion}")
        click.echo(f"   Exaggeration: {exaggeration}")
        click.echo(f"   CFG Weight: {cfg_weight}")
        click.echo(f"   Temperature: {temperature}")

        if emphasis:
            click.echo(f"   Emphasis: {', '.join(emphasis)}")
        if pause_before > 0 or pause_after > 0:
            click.echo(f"   Pauses: before={pause_before}ms, after={pause_after}ms")
        if breath_frequency > 0:
            click.echo(f"   Breath frequency: every {breath_frequency} words")
        if seed is not None:
            click.echo(f"   Seed: {seed}")
        click.echo()

        # Generate speech with all parameters
        output_path = service.generate_speech(
            voice_id=voice_id,
            text=text,
            output_file=output,
            speed=speed,
            pitch=pitch,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
            top_p=top_p,
            min_p=min_p,
            emotion=emotion,
            emphasis=list(emphasis) if emphasis else None,
            pause_before=pause_before,
            pause_after=pause_after,
            breath_frequency=breath_frequency,
            seed=seed
        )

        click.echo(Fore.GREEN + f"✅ Speech generated successfully!")
        click.echo(f"   Output: {output_path}")
        click.echo()

    except ValueError as e:
        click.echo(Fore.RED + f"❌ Parameter Error: {e}")
        logger.error(f"Parameter validation error: {e}")
    except Exception as e:
        click.echo(Fore.RED + f"❌ Failed to generate speech: {e}")
        logger.error(f"Speech generation error: {e}", exc_info=True)


@voice_clone.command()
@click.option('--voice-id', '-v', required=True, type=int, help='Voice ID to delete')
@click.confirmation_option(prompt='Are you sure you want to delete this voice?')
def delete(voice_id: int):
    """Delete a cloned voice.

    Example:
        youtube-chat voice-clone delete --voice-id 1
    """
    try:
        from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

        click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
        click.echo(Fore.CYAN + "║   Voice Cloning - Delete Voice                           ║")
        click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
        click.echo()

        service = VoiceCloningService()

        click.echo(Fore.YELLOW + f"🗑️  Deleting voice {voice_id}...")
        service.delete_voice(voice_id)

        click.echo(Fore.GREEN + f"✅ Voice deleted successfully!")
        click.echo()

    except ValueError as e:
        click.echo(Fore.RED + f"❌ Error: {e}")
    except Exception as e:
        click.echo(Fore.RED + f"❌ Failed to delete voice: {e}")
        logger.error(f"Voice deletion error: {e}", exc_info=True)


@voice_clone.command()
def presets():
    """Show available voice parameter presets.

    Presets provide predefined parameter combinations for common voice styles.
    Use these as starting points for your voice generation.

    Example:
        youtube-chat voice-clone presets
    """
    click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
    click.echo(Fore.CYAN + "║   Voice Cloning - Parameter Presets                      ║")
    click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
    click.echo()

    presets_data = {
        "neutral": {
            "speed": 1.0, "pitch": 0, "exaggeration": 0.5, "emotion": "neutral",
            "description": "Natural, balanced speech"
        },
        "happy": {
            "speed": 1.1, "pitch": 2, "exaggeration": 0.7, "emotion": "happy",
            "description": "Upbeat, cheerful speech"
        },
        "sad": {
            "speed": 0.8, "pitch": -3, "exaggeration": 0.6, "emotion": "sad",
            "description": "Slow, melancholic speech"
        },
        "angry": {
            "speed": 1.2, "pitch": 3, "exaggeration": 0.8, "emotion": "angry",
            "description": "Fast, intense speech"
        },
        "excited": {
            "speed": 1.3, "pitch": 4, "exaggeration": 0.9, "emotion": "excited",
            "description": "Very energetic, enthusiastic speech"
        },
        "calm": {
            "speed": 0.9, "pitch": -1, "exaggeration": 0.4, "emotion": "neutral",
            "description": "Slow, relaxed speech"
        },
        "professional": {
            "speed": 1.0, "pitch": 1, "exaggeration": 0.5, "emotion": "confident",
            "description": "Clear, professional speech"
        },
        "dramatic": {
            "speed": 0.95, "pitch": 2, "exaggeration": 1.2, "emotion": "joyful",
            "description": "Theatrical, expressive speech"
        }
    }

    for preset_name, preset_config in presets_data.items():
        click.echo(Fore.GREEN + f"📌 {preset_name.upper()}")
        click.echo(f"   {preset_config['description']}")
        click.echo(f"   Speed: {preset_config['speed']}x | Pitch: {preset_config['pitch']:+d}st | "
                  f"Exaggeration: {preset_config['exaggeration']} | Emotion: {preset_config['emotion']}")
        click.echo()

    click.echo(Fore.CYAN + "💡 Usage Example:")
    click.echo("   youtube-chat voice-clone generate --voice-id 1 --text \"Hello!\" \\")
    click.echo("     --output output.wav --emotion happy --speed 1.1 --pitch 2 --exaggeration 0.7")
    click.echo()


__all__ = ["voice_clone"]

