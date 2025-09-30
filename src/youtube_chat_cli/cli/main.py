"""
CLI module for the Personal Research Insight CLI tool.
"""

import uuid
import json
import click
from colorama import init, Fore, Style
from halo import Halo
from dotenv import load_dotenv
from datetime import datetime
from youtube_chat_cli.utils.session_manager import SessionManager
from youtube_chat_cli.services.transcription.processor import get_source_processor
from youtube_chat_cli.utils.llm_service import get_llm_service
from youtube_chat_cli.services.tts.service import get_tts_service
from youtube_chat_cli.services.tts.config_manager import get_tts_config_manager
from youtube_chat_cli.services.monitoring.channel_monitor import get_channel_monitor
from youtube_chat_cli.services.import_service.bulk_import import get_bulk_importer
from youtube_chat_cli.core.database import get_video_database
from youtube_chat_cli.core.youtube_api import get_youtube_client, YouTubeAPIError
from youtube_chat_cli.services.n8n.client import get_n8n_client
from youtube_chat_cli.services.monitoring.background_service import get_monitoring_service
from youtube_chat_cli.services.monitoring.video_processor import get_video_processor
from youtube_chat_cli.services.monitoring.video_queue import get_video_queue

# Load environment variables
load_dotenv()

# Set up basic logging for CLI
import logging
import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CLIError(Exception):
    """Base CLI exception."""
    pass

class ProcessingError(Exception):
    """Content processing error."""
    pass

class APIError(Exception):
    """API communication error."""
    pass

def setup_logging():
    """Set up basic logging - simplified for standalone execution."""
    pass

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Set up logging
setup_logging()

# Create global instances
session_manager = SessionManager()
source_processor = get_source_processor()
llm_service = None  # Will be initialized when needed (requires API key)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Personal Research Insight CLI - Extract, process, and query content from YouTube videos and websites."""
    pass


@cli.group()
def session():
    """Manage CLI session state."""
    pass


@session.command()
def view():
    """View current session information."""
    session_id = session_manager.get_session_id()
    active_source = session_manager.get_active_source()
    chat_history = session_manager.get_chat_history()

    click.echo(Fore.CYAN + "=== Session Information ===")
    click.echo(f"Session ID: {Fore.GREEN}{session_id}")
    click.echo(f"Active Source: {Fore.GREEN}{active_source or 'None'}")
    click.echo(f"Chat History: {Fore.GREEN}{len(chat_history)} messages")


@session.command()
def clear_history():
    """Clear the chat history for the current source."""
    session_manager.clear_chat_history()
    click.echo(Fore.GREEN + "Chat history cleared.")


@session.command()
def clear_all():
    """Clear everything (source and chat history), but keep session ID."""
    session_manager.set_active_source("")
    session_manager.clear_chat_history()
    click.echo(Fore.GREEN + "Session cleared (source and history).")


@session.command()
def new_id():
    """Generate a new session ID."""
    new_session_id = str(uuid.uuid4())
    session_manager.set_session_id(new_session_id)
    click.echo(f"New session ID generated: {Fore.GREEN}{new_session_id}")


@cli.command()
@click.argument('url')
def set_source(url):
    """Set the active source URL and process its content."""
    spinner = Halo(text='Processing content...', spinner='dots')
    spinner.start()

    try:
        # Process the content
        processed_content = source_processor.process_content(url)

        # Save to session
        session_manager.set_active_source(url)
        session_manager.clear_chat_history()  # Clear old chat history for new source

        spinner.succeed(Fore.GREEN + f'Source set successfully ({len(processed_content)} characters processed)')

    except (ProcessingError, APIError) as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in set_source: {e}")
        return 1

    return 0


@cli.command()
def print_text():
    """Print the processed text of the currently active source."""
    active_source = session_manager.get_active_source()

    if not active_source:
        click.echo(Fore.RED + "No active source set. Use 'set-source <URL>' to set one first.")
        return 1

    spinner = Halo(text='Retrieving content...', spinner='dots')
    spinner.start()

    try:
        # Get the processed content (needs to reprocess each time for simplicity)
        processed_content = source_processor.process_content(active_source)
        spinner.succeed(Fore.GREEN + f'Content retrieved')

        # Print the content
        click.echo(Fore.CYAN + "\n=== Processed Content ===")
        click.echo(processed_content)
        click.echo(Fore.CYAN + "=== End of Content ===\n")

    except (ProcessingError, APIError) as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in print_text: {e}")
        return 1

    return 0


def _get_llm_service():
    """Get LLM service instance, initializing it if needed."""
    global llm_service
    if llm_service is None:
        try:
            llm_service = get_llm_service()
        except ValueError as e:
            click.echo(Fore.RED + str(e))
            click.echo(Fore.YELLOW + "Make sure your .env file is properly configured.")
            return None
    return llm_service


@cli.command()
def summarize():
    """Generate a summary of the active source content."""
    active_source = session_manager.get_active_source()

    if not active_source:
        click.echo(Fore.RED + "No active source set. Use 'set-source <URL>' to set one first.")
        return 1

    # Initialize LLM service
    llm = _get_llm_service()
    if not llm:
        return 1

    spinner = Halo(text='Generating summary...', spinner='dots')
    spinner.start()

    try:
        # Get content and generate summary
        context = source_processor.process_content(active_source)
        summary = llm.summarize_content(context)

        spinner.succeed(Fore.GREEN + 'Summary generated')

        click.echo(Fore.CYAN + "\n=== Content Summary ===")
        click.echo(summary)
        click.echo()

    except (ProcessingError, APIError) as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in summarize: {e}")
        return 1

    return 0


@cli.command()
def faq():
    """Generate an FAQ from the active source content."""
    active_source = session_manager.get_active_source()

    if not active_source:
        click.echo(Fore.RED + "No active source set. Use 'set-source <URL>' to set one first.")
        return 1

    # Initialize LLM service
    llm = _get_llm_service()
    if not llm:
        return 1

    spinner = Halo(text='Generating FAQ...', spinner='dots')
    spinner.start()

    try:
        # Get content and generate FAQ
        context = source_processor.process_content(active_source)
        faq_content = llm.generate_faq(context)

        spinner.succeed(Fore.GREEN + 'FAQ generated')

        click.echo(Fore.CYAN + "\n=== Frequently Asked Questions ===")
        click.echo(faq_content)
        click.echo()

    except (ProcessingError, APIError) as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in faq: {e}")
        return 1

    return 0


@cli.command()
def toc():
    """Generate a table of contents for the active source content."""
    active_source = session_manager.get_active_source()

    if not active_source:
        click.echo(Fore.RED + "No active source set. Use 'set-source <URL>' to set one first.")
        return 1

    # Initialize LLM service
    llm = _get_llm_service()
    if not llm:
        return 1

    spinner = Halo(text='Generating table of contents...', spinner='dots')
    spinner.start()

    try:
        # Get content and generate TOC
        context = source_processor.process_content(active_source)
        toc_content = llm.generate_toc(context)

        spinner.succeed(Fore.GREEN + 'Table of contents generated')

        click.echo(Fore.CYAN + "\n=== Table of Contents ===")
        click.echo(toc_content)
        click.echo()

    except (ProcessingError, APIError) as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in toc: {e}")
        return 1

    return 0


@cli.command()
def chat():
    """Start an interactive chat session with the active source."""
    active_source = session_manager.get_active_source()

    if not active_source:
        click.echo(Fore.RED + "No active source set. Use 'set-source <URL>' to set one first.")
        return 1

    # Initialize LLM service
    llm = _get_llm_service()
    if not llm:
        return 1

    try:
        context = source_processor.process_content(active_source)
    except (ProcessingError, APIError) as e:
        click.echo(Fore.RED + f"Failed to load content: {e}")
        return 1

    chat_history = session_manager.get_chat_history()

    click.echo(Fore.CYAN + "\n=== Interactive Chat Session ===")
    click.echo(Fore.GREEN + "You can chat with the AI about the content.")
    click.echo(Fore.YELLOW + "Type 'exit', 'quit', or CTRL+C to end the session.")
    click.echo()

    while True:
        try:
            user_input = click.prompt(Fore.YELLOW + "You")

            if user_input.lower() in ['exit', 'quit']:
                click.echo(Fore.GREEN + "Chat session ended.")
                break

            # Generate AI response
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()

            try:
                response = llm.generate_response(context, user_input, chat_history)
                spinner.succeed(Fore.GREEN + 'AI Response:')

                # Save to chat history
                session_manager.add_to_chat_history("user", user_input)
                session_manager.add_to_chat_history("assistant", response)

                # Update local chat history
                chat_history = session_manager.get_chat_history()

                click.echo(Fore.GREEN + f"AI: {response}")
                click.echo()

            except Exception as e:
                spinner.fail(Fore.RED + f"Error generating response: {e}")
                logger.error(f"Error in chat response generation: {e}")

        except click.Abort:
            click.echo(Fore.GREEN + "\nChat session ended.")
            break
        except KeyboardInterrupt:
            click.echo(Fore.GREEN + "\nChat session ended.")
            break

    return 0


@cli.command()
@click.option('--output', '-o', default='podcast_overview.wav', help='Output audio file path')
def podcast(output):
    """Generate a podcast-style audio overview of the active source."""
    active_source = session_manager.get_active_source()

    if not active_source:
        click.echo(Fore.RED + "No active source set. Use 'set-source <URL>' to set one first.")
        return 1

    # Initialize services
    llm = _get_llm_service()
    if not llm:
        return 1

    tts = get_tts_service()

    spinner = Halo(text='Generating podcast script...', spinner='dots')
    spinner.start()

    try:
        # Step 1: Generate podcast script
        context = source_processor.process_content(active_source)
        podcast_script = llm.generate_podcast_script(context)

        spinner.succeed(Fore.GREEN + 'Podcast script generated')
        spinner = Halo(text='Generating audio...', spinner='dots')
        spinner.start()

        # Step 2: Generate audio from script
        audio_file = tts.generate_podcast_audio(podcast_script, output)

        spinner.succeed(Fore.GREEN + f'Podcast audio generated: {audio_file}')

        click.echo(Fore.CYAN + "\n=== Podcast Generation Complete ===")
        click.echo(f"Script length: {len(podcast_script)} characters")
        click.echo(f"Audio saved to: {Fore.GREEN}{audio_file}")
        click.echo("\nTip: Play the audio file with your preferred media player.")
        click.echo()

    except (ProcessingError, APIError) as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in podcast: {e}")
        return 1

    return 0


@cli.command()
def verify_connections():
    """Verify connections to all external services."""
    click.echo(Fore.CYAN + "Verifying External Service Connections")
    click.echo("=" * 50)

    # Check OpenRouter
    click.echo("1. Testing OpenRouter API connection...")
    try:
        from llm_service import get_llm_service
        llm = get_llm_service()
        # Simple test - this will fail if API key is invalid
        # We don't actually call the API here to avoid usage charges
        click.echo(Fore.GREEN + "   ✓ OpenRouter service initialized (API key found)")
    except ValueError as e:
        click.echo(Fore.RED + f"   ✗ OpenRouter Error: {e}")
    except Exception as e:
        click.echo(Fore.YELLOW + f"   ⚠ OpenRouter Warning: {e}")

    # Check MaryTTS
    click.echo("2. Testing MaryTTS server connection...")
    try:
        from tts_service import get_tts_service
        tts = get_tts_service()
        connected = tts.check_server_connection()
        if connected:
            click.echo(Fore.GREEN + "   ✓ MaryTTS server is accessible")
        else:
            click.echo(Fore.RED + "   ✗ MaryTTS server is not responding")
    except Exception as e:
        click.echo(Fore.RED + f"   ✗ MaryTTS Error: {e}")

    # Check n8n
    click.echo("3. Testing n8n workflow connection...")
    try:
        from n8n_client import get_n8n_client
        n8n = get_n8n_client()
        connected = n8n.check_workflow_connection()
        if connected:
            click.echo(Fore.GREEN + "   ✓ n8n workflow is accessible")
        else:
            click.echo(Fore.RED + "   ✗ n8n workflow is not responding")
    except ValueError as e:
        click.echo(Fore.RED + f"   ✗ n8n Error: {e}")
    except Exception as e:
        click.echo(Fore.RED + f"   ✗ n8n Error: {e}")

    click.echo(Fore.CYAN + "\nConnection verification complete.")
    click.echo("Note: This is a basic connectivity test.")
    click.echo("Full functionality may require proper API key configuration.")


@cli.command()
@click.argument('message')
def invoke_n8n(message):
    """Send a message to the n8n RAG AI agent workflow."""
    session_id = session_manager.get_session_id()

    try:
        n8n = get_n8n_client()
    except ValueError as e:
        click.echo(Fore.RED + str(e))
        click.echo(Fore.YELLOW + "Make sure your .env file is properly configured with N8N_WEBHOOK_URL.")
        return 1

    spinner = Halo(text='Sending message to n8n workflow...', spinner='dots')
    spinner.start()

    try:
        response = n8n.send_chat_message(message, session_id)

        spinner.succeed(Fore.GREEN + 'Response received from n8n')

        click.echo(Fore.CYAN + "\n=== n8n Agent Response ===")
        click.echo(response)
        click.echo()

    except APIError as e:
        spinner.fail(Fore.RED + str(e))
        return 1
    except Exception as e:
        spinner.fail(Fore.RED + f"Unexpected error: {e}")
        logger.error(f"Unexpected error in invoke_n8n: {e}")
        return 1

    return 0


# TTS Library Management Commands
@cli.group()
def tts():
    """Manage Text-to-Speech (TTS) libraries and configurations."""
    pass


@tts.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
def list(verbose):
    """List all available TTS libraries."""
    tts_manager = get_tts_config_manager()
    libraries = tts_manager.list_libraries()

    click.echo(Fore.CYAN + "Available TTS Libraries")
    click.echo("=" * 50)

    for lib_id, lib_spec in libraries.items():
        installed = tts_manager.is_library_installed(lib_id)
        status = Fore.GREEN + "✓ Installed" if installed else Fore.YELLOW + "○ Available"

        click.echo(f"\n{Fore.MAGENTA}{lib_spec.name} {Fore.WHITE}({lib_id})")
        click.echo(f"  {Fore.BLUE}License: {Fore.WHITE}{lib_spec.license_type}")
        click.echo(f"  {Fore.BLUE}Status: {status}")

        if lib_spec.parameter_count:
            click.echo(f"  {Fore.BLUE}Parameters: {Fore.WHITE}{lib_spec.parameter_count:,}")
        else:
            click.echo(f"  {Fore.BLUE}Parameters: {Fore.WHITE}N/A")

        click.echo(f"  {Fore.BLUE}Voice Cloning: {Fore.WHITE}{'✓ Yes' if lib_spec.voice_cloning else '○ No'}")
        click.echo(f"  {Fore.BLUE}Emotion Control: {Fore.WHITE}{'✓ Yes' if lib_spec.emotion_control else '○ No'}")

        if verbose:
            click.echo(f"  {Fore.BLUE}Description: {Fore.WHITE}{lib_spec.description}")
            click.echo(f"  {Fore.BLUE}Package: {Fore.WHITE}{lib_spec.package_name}")
        else:
            click.echo(f"  {Fore.BLUE}Description: {Fore.WHITE}{lib_spec.description[:80]}" + ("..." if len(lib_spec.description) > 80 else ""))

    current = tts_manager.get_current_library()
    click.echo(f"\n{Fore.GREEN}Current Default Library: {Fore.WHITE}{current}")

    return 0


@tts.command()
@click.argument('library_name')
def info(library_name):
    """Show detailed information about a specific TTS library."""
    tts_manager = get_tts_config_manager()
    lib_spec = tts_manager.get_library_info(library_name)

    if not lib_spec:
        click.echo(Fore.RED + f"Unknown library: {library_name}")
        click.echo(Fore.YELLOW + "Use 'tts list' to see available libraries.")
        return 1

    installed = tts_manager.is_library_installed(library_name)
    config = tts_manager.get_library_config(library_name)

    click.echo(Fore.CYAN + f"=== {lib_spec.name} ({library_name}) ===")
    click.echo(f"{Fore.BLUE}Package: {Fore.WHITE}{lib_spec.package_name}")
    click.echo(f"{Fore.BLUE}License: {Fore.WHITE}{lib_spec.license_type}")
    click.echo(f"{Fore.BLUE}Installed: {Fore.WHITE}{'Yes' if installed else 'No'}")
    click.echo(f"{Fore.BLUE}Description: {Fore.WHITE}{lib_spec.description}")

    if lib_spec.parameter_count:
        click.echo(f"{Fore.BLUE}Parameters: {Fore.WHITE}{lib_spec.parameter_count:,}")

    click.echo(f"{Fore.BLUE}Features:")
    click.echo(f"  Voice Cloning: {Fore.WHITE}{'✓ Yes' if lib_spec.voice_cloning else '○ No'}")
    click.echo(f"  Emotion Control: {Fore.WHITE}{'✓ Yes' if lib_spec.emotion_control else '○ No'}")

    if config:
        click.echo(f"{Fore.BLUE}Configuration: {Fore.WHITE}{config}")

    if library_name == tts_manager.get_current_library():
        click.echo(Fore.GREEN + "Currently selected as default library")

    return 0


@tts.command()
@click.argument('library_name')
@click.option('--cpu-only', is_flag=True, default=True, help='Install CPU-only versions for compatibility')
@click.option('--retry-count', default=3, help='Number of retry attempts (default: 3)')
@click.option('--timeout', default=300, help='Installation timeout in seconds (default: 300)')
@click.option('--force', '-f', is_flag=True, help='Force reinstall even if already installed')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed installation progress')
def install(library_name, cpu_only, retry_count, timeout, force, verbose):
    """Install a specific TTS library with enhanced options."""
    tts_manager = get_tts_config_manager()

    # Configure logging level
    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    if not force and tts_manager.is_library_installed(library_name):
        click.echo(Fore.YELLOW + f"Library '{library_name}' is already installed.")
        click.echo(Fore.WHITE + "Use --force to reinstall or try a different library.")
        return 0

    lib_spec = tts_manager.get_library_info(library_name)
    if not lib_spec:
        click.echo(Fore.RED + f"Unknown library: {library_name}")
        click.echo(Fore.WHITE + "Available libraries:")
        for lib_id, spec in tts_manager.list_libraries().items():
            click.echo(f"  • {lib_id}: {spec.name}")
        return 1

    click.echo(Fore.CYAN + f"Installing {lib_spec.name}...")
    click.echo(f"  • CPU-only mode: {cpu_only}")
    click.echo(f"  • Retry attempts: {retry_count}")
    click.echo(f"  • Timeout: {timeout}s")
    click.echo()

    spinner = Halo(text=f'Installing {lib_spec.name}...', spinner='dots')
    spinner.start()

    try:
        success, message = tts_manager.install_library(
            library_name,
            cpu_only=cpu_only,
            retry_count=retry_count,
            timeout=timeout
        )

        if success:
            spinner.succeed(Fore.GREEN + f"✓ {message}")
            click.echo()
            click.echo(Fore.GREEN + "🎉 Installation completed successfully!")
            click.echo(Fore.WHITE + f"Test it with: python cli.py tts test {library_name}")
        else:
            spinner.fail(Fore.RED + f"✗ {message}")

            # Provide installation guidance
            guidance = tts_manager._get_installation_guidance(library_name)
            if guidance:
                click.echo(Fore.YELLOW + f"💡 {guidance}")

            return 1

    except Exception as e:
        spinner.fail(Fore.RED + f"Installation failed: {e}")

        if verbose:
            import traceback
            click.echo(Fore.RED + f"Debug: {traceback.format_exc()}")

        return 1

    return 0


@tts.command()
@click.option('--force', '-f', is_flag=True, help='Reinstall all libraries even if already installed')
@click.option('--cpu-only', is_flag=True, default=True, help='Install CPU-only versions for compatibility (default: True)')
@click.option('--retry-count', default=3, help='Number of retry attempts per library (default: 3)')
@click.option('--timeout', default=300, help='Installation timeout per library in seconds (default: 300)')
@click.option('--skip-system-deps', is_flag=True, help='Skip system dependency installation')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed installation progress')
def install_all(force, cpu_only, retry_count, timeout, skip_system_deps, verbose):
    """Install all available TTS libraries with robust error handling."""
    tts_manager = get_tts_config_manager()
    libraries = tts_manager.list_libraries()

    # Configure logging level
    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    click.echo(Fore.CYAN + f"🚀 Installing all TTS libraries ({len(libraries)} total)")
    click.echo(Fore.CYAN + f"Configuration:")
    click.echo(f"  • CPU-only mode: {cpu_only}")
    click.echo(f"  • Retry attempts: {retry_count}")
    click.echo(f"  • Timeout per library: {timeout}s")
    click.echo(f"  • Skip system deps: {skip_system_deps}")
    click.echo()

    if not skip_system_deps:
        click.echo(Fore.YELLOW + "⚠️  Note: This will install system dependencies (requires sudo)")
    click.echo(Fore.YELLOW + "⚠️  Large downloads and compilation may take several minutes per library")
    click.echo()

    success_count = 0
    failed_count = 0
    skipped_count = 0
    failed_libraries = []

    # Install libraries in optimal order (simple ones first)
    install_order = ["gtts", "edge_tts", "melotts", "chatterbox", "kokoro", "openvoice_v2"]
    ordered_libraries = []

    for lib_id in install_order:
        if lib_id in libraries:
            ordered_libraries.append((lib_id, libraries[lib_id]))

    # Add any remaining libraries
    for lib_id, lib_spec in libraries.items():
        if lib_id not in install_order:
            ordered_libraries.append((lib_id, lib_spec))

    for i, (lib_id, lib_spec) in enumerate(ordered_libraries, 1):
        click.echo(f"{Fore.CYAN}[{i}/{len(libraries)}] Processing {lib_spec.name}...")

        if not force and tts_manager.is_library_installed(lib_id):
            click.echo(f"{Fore.YELLOW}  ○ Already installed, skipping")
            skipped_count += 1
            continue

        spinner = Halo(text=f'Installing {lib_spec.name}...', spinner='dots')
        spinner.start()

        try:
            # Override system dependency installation if requested
            if skip_system_deps:
                # Temporarily disable system dependency installation
                original_method = tts_manager._install_system_dependencies
                tts_manager._install_system_dependencies = lambda x: True

            success, message = tts_manager.install_library(
                lib_id,
                cpu_only=cpu_only,
                retry_count=retry_count,
                timeout=timeout
            )

            # Restore original method
            if skip_system_deps:
                tts_manager._install_system_dependencies = original_method

            if success:
                spinner.succeed(Fore.GREEN + f"✓ {lib_spec.name}: {message}")
                success_count += 1
            else:
                spinner.fail(Fore.RED + f"✗ {lib_spec.name}: {message}")
                failed_libraries.append(lib_id)

                # Provide installation guidance
                guidance = tts_manager._get_installation_guidance(lib_id)
                if guidance:
                    click.echo(Fore.YELLOW + f"    💡 {guidance}")

                failed_count += 1

        except Exception as e:
            spinner.fail(Fore.RED + f"✗ {lib_spec.name}: Unexpected error: {e}")
            failed_libraries.append(lib_id)

            if verbose:
                import traceback
                click.echo(Fore.RED + f"    Debug: {traceback.format_exc()}")

            failed_count += 1

    # Installation Summary
    click.echo()
    click.echo(Fore.CYAN + "=" * 50)
    click.echo(Fore.CYAN + "📊 INSTALLATION SUMMARY")
    click.echo(Fore.CYAN + "=" * 50)
    click.echo(f"{Fore.GREEN}✓ Successfully installed: {success_count}")
    if skipped_count > 0:
        click.echo(f"{Fore.YELLOW}○ Skipped (already installed): {skipped_count}")
    if failed_count > 0:
        click.echo(f"{Fore.RED}✗ Failed: {failed_count}")
        click.echo(f"{Fore.RED}  Failed libraries: {', '.join(failed_libraries)}")

    if success_count > 0:
        click.echo()
        click.echo(Fore.GREEN + "🎉 Next steps:")
        click.echo(Fore.WHITE + "  • Test libraries: python cli.py tts test <library_name>")
        click.echo(Fore.WHITE + "  • Set default: python cli.py tts set-default <library_name>")
        click.echo(Fore.WHITE + "  • List all: python cli.py tts list")

    if failed_count > 0:
        click.echo()
        click.echo(Fore.YELLOW + "🔧 For failed installations:")
        click.echo(Fore.WHITE + "  • Try with --verbose for more details")
        click.echo(Fore.WHITE + "  • Check system dependencies manually")
        click.echo(Fore.WHITE + "  • Install individual libraries: python cli.py tts install <library_name>")

    return 0 if failed_count == 0 else 1


@tts.command()
@click.argument('library_name')
def uninstall(library_name):
    """Uninstall a TTS library."""
    tts_manager = get_tts_config_manager()

    if not tts_manager.is_library_installed(library_name):
        click.echo(Fore.YELLOW + f"Library '{library_name}' is not installed.")
        return 0

    # Check if it's the current default
    current = tts_manager.get_current_library()
    if library_name == current:
        click.echo(Fore.YELLOW + "This is your current default library. After uninstalling,")
        click.echo(Fore.YELLOW + "the system will fall back to Edge TTS.")
        if not click.confirm("Continue?"):
            return 0

    spinner = Halo(text=f'Uninstalling {library_name}...', spinner='dots')
    spinner.start()

    try:
        success, message = tts_manager.uninstall_library(library_name)

        if success:
            spinner.succeed(Fore.GREEN + message)
            # Reset to edge_tts if we uninstalled the current default
            if library_name == current:
                tts_manager.set_default_library("edge_tts")
                click.echo(Fore.BLUE + "Reset default library to edge_tts")
        else:
            spinner.fail(Fore.RED + message)
            return 1

    except Exception as e:
        spinner.fail(Fore.RED + f"Uninstallation failed: {e}")
        return 1

    return 0


@tts.command()
@click.argument('library_name')
def test(library_name):
    """Test a TTS library by generating sample audio."""
    tts_manager = get_tts_config_manager()

    if not tts_manager.is_library_installed(library_name):
        click.echo(Fore.RED + f"Library '{library_name}' is not installed.")
        click.echo(Fore.YELLOW + f"Install it first with: tts install {library_name}")
        return 1

    spinner = Halo(text=f'Testing {library_name}...', spinner='dots')
    spinner.start()

    try:
        result = tts_manager.test_library(library_name)

        if result.get("success"):
            spinner.succeed(Fore.GREEN + result["message"])

            if result.get("sample_file"):
                click.echo(Fore.BLUE + f"Sample audio saved to: {result['sample_file']}")
                click.echo(Fore.BLUE + "Play the file to hear the generated speech.")

            if result.get("voices"):
                click.echo(Fore.BLUE + f"Available voices: {', '.join(result['voices'][:10])}" +
                          ("..." if len(result['voices']) > 10 else ""))

            if result.get("performance"):
                perf = result["performance"]
                click.echo(Fore.BLUE + "Performance metrics:")
                for key, value in perf.items():
                    if isinstance(value, float):
                        click.echo(f"  {key.replace('_', ' ').title()}: {value:.2f}s")
                    else:
                        click.echo(f"  {key.replace('_', ' ').title()}: {value}")

        else:
            spinner.fail(Fore.RED + result["message"])
            return 1

    except Exception as e:
        spinner.fail(Fore.RED + f"Test failed: {e}")
        return 1

    return 0


@tts.command()
@click.argument('library_name')
def set_default(library_name):
    """Set a TTS library as the default for future use."""
    tts_manager = get_tts_config_manager()

    spinner = Halo(text=f'Setting {library_name} as default...', spinner='dots')
    spinner.start()

    try:
        success, message = tts_manager.set_default_library(library_name)

        if success:
            spinner.succeed(Fore.GREEN + message)
        else:
            spinner.fail(Fore.RED + message)
            return 1

    except Exception as e:
        spinner.fail(Fore.RED + f"Failed to set default: {e}")
        return 1

    return 0


@tts.command()
def status():
    """Show current TTS configuration status."""
    tts_manager = get_tts_config_manager()

    click.echo(Fore.CYAN + "=== TTS Configuration Status ===")

    current = tts_manager.get_current_library()
    click.echo(f"{Fore.BLUE}Current Default Library: {Fore.GREEN}{current}")

    click.echo(f"\n{Fore.BLUE}Installed Libraries:")
    for lib_id in tts_manager.config.get("installed_libraries", []):
        lib_spec = tts_manager.get_library_info(lib_id)
        if lib_spec:
            click.echo(f"  {Fore.GREEN}✓ {lib_spec.name} ({lib_id})")

    click.echo(f"\n{Fore.BLUE}Available Libraries:")
    for lib_id, lib_spec in tts_manager.list_libraries().items():
        if not tts_manager.is_library_installed(lib_id):
            click.echo(f"  {Fore.YELLOW}○ {lib_spec.name} ({lib_id})")

    return 0


@tts.command()
@click.argument('library_name')
def configure(library_name):
    """Configure settings for a specific TTS library."""
    tts_manager = get_tts_config_manager()

    if not tts_manager.is_library_installed(library_name):
        click.echo(Fore.RED + f"Library '{library_name}' is not installed.")
        click.echo(Fore.YELLOW + f"Install it first with: tts install {library_name}")
        return 1

    lib_spec = tts_manager.get_library_info(library_name)
    current_config = tts_manager.get_library_config(library_name)

    click.echo(Fore.CYAN + f"=== Configuring {lib_spec.name} ({library_name}) ===")

    if library_name in ["edge_tts", "gtts"]:
        # Simple configuration
        if library_name == "edge_tts":
            current_voice = current_config.get("default_voice", "en-US-AriaNeural")
            new_voice = click.prompt("Default voice", default=current_voice)
            tts_manager.set_library_config(library_name, {"default_voice": new_voice})
            click.echo(Fore.GREEN + f"Default voice set to: {new_voice}")

        elif library_name == "gtts":
            current_lang = current_config.get("default_lang", "en")
            new_lang = click.prompt("Default language", default=current_lang)
            tts_manager.set_library_config(library_name, {"default_lang": new_lang})
            click.echo(Fore.GREEN + f"Default language set to: {new_lang}")

    elif library_name == "kokoro":
        click.echo("Kokoro configuration:")
        click.echo("Voice settings are configured programmatically.")
        click.echo("Available voices: af_sarah, am_michael, bf_emma, bm_george")
        voice = click.prompt("Preferred voice", default="af_sarah")
        tts_manager.set_library_config(library_name, {"preferred_voice": voice})

    elif library_name in ["melotts", "chatterbox"]:
        click.echo(f"{lib_spec.name} configuration:")
        click.echo("This library supports advanced features.")
        emotion_level = click.prompt("Emotion level (0-1)", default=0.5, type=float)
        tts_manager.set_library_config(library_name, {"emotion_level": emotion_level})

    elif library_name == "openvoice_v2":
        click.echo("OpenVoice v2 requires reference audio for voice cloning.")
        click.echo("Configuration involves setting reference audio paths.")
        ref_audio = click.prompt("Reference audio file path (leave empty to skip)")
        if ref_audio.strip():
            tts_manager.set_library_config(library_name, {"reference_audio": ref_audio})
            click.echo(Fore.GREEN + f"Reference audio configured: {ref_audio}")

    elif library_name == "chatterbox":
        click.echo("Chatterbox TTS Configuration")
        click.echo("=" * 40)

        # Device selection
        current_device = current_config.get("device", "auto")
        click.echo(f"Current device: {current_device}")
        device_options = ["auto", "cuda", "cpu"]
        device_choice = click.prompt("Device to use", default=current_device, type=click.Choice(device_options))

        # Emotion level (0.0-1.0)
        current_emotion = current_config.get("emotion_level", 0.5)
        emotion_level = click.prompt("Emotion level (0.0-1.0)", default=current_emotion, type=float)
        emotion_level = max(0.0, min(1.0, emotion_level))  # Clamp to range

        # Multilingual toggle
        current_multilingual = current_config.get("use_multilingual", False)
        use_multilingual = click.confirm("Enable multilingual features?", default=current_multilingual)

        # Enable/disable toggle
        current_enabled = current_config.get("enabled", True)
        enabled = click.confirm("Enable Chatterbox TTS?", default=current_enabled)

        # Save configuration
        tts_manager.set_library_config(library_name, {
            "device": device_choice,
            "emotion_level": emotion_level,
            "use_multilingual": use_multilingual,
            "enabled": enabled
        })

        click.echo(Fore.GREEN + f"Chatterbox configuration saved!")
        click.echo(f"  Device: {device_choice}")
        click.echo(f"  Emotion Level: {emotion_level}")
        click.echo(f"  Multilingual: {use_multilingual}")
        click.echo(f"  Enabled: {enabled}")

    click.echo(Fore.GREEN + f"\n{lib_spec.name} configuration updated.")
    return 0


# =============================================================================
# CHANNEL MONITORING COMMANDS
# =============================================================================

@cli.group()
def channel():
    """Manage YouTube channel monitoring."""
    pass


@channel.command()
@click.argument('channel_url')
@click.option('--check-interval', default=24, help='Check interval in hours (default: 24)')
@click.option('--include-keywords', multiple=True, help='Include videos with these keywords')
@click.option('--exclude-keywords', multiple=True, help='Exclude videos with these keywords')
@click.option('--min-duration', type=int, help='Minimum video duration in seconds')
@click.option('--max-duration', type=int, help='Maximum video duration in seconds')
@click.option('--no-shorts', is_flag=True, help='Exclude YouTube Shorts (videos < 60s)')
def add(channel_url, check_interval, include_keywords, exclude_keywords,
        min_duration, max_duration, no_shorts):
    """Add a YouTube channel for monitoring."""
    try:
        channel_monitor = get_channel_monitor()

        # Build filters
        filters = {}
        if include_keywords:
            filters['include_keywords'] = list(include_keywords)
        if exclude_keywords:
            filters['exclude_keywords'] = list(exclude_keywords)
        if min_duration:
            filters['min_duration'] = min_duration
        if max_duration:
            filters['max_duration'] = max_duration
        if no_shorts:
            filters['no_shorts'] = True

        spinner = Halo(text='Adding channel for monitoring...', spinner='dots')
        spinner.start()

        result = channel_monitor.add_channel(
            channel_url=channel_url,
            check_interval=check_interval,
            filters=filters if filters else None
        )

        spinner.succeed(Fore.GREEN + f"✓ Added channel: {result['name']}")

        click.echo(f"Channel ID: {result['channel_id']}")
        click.echo(f"Check interval: {check_interval} hours")
        if filters:
            click.echo(f"Filters: {json.dumps(filters, indent=2)}")

        click.echo(Fore.CYAN + "\nNext steps:")
        click.echo("• Start monitoring: python cli.py service start")
        click.echo("• Manual scan: python cli.py channel scan")

    except (ValueError, YouTubeAPIError) as e:
        if 'spinner' in locals():
            spinner.fail(Fore.RED + f"✗ Failed to add channel")
        click.echo(Fore.RED + f"Error: {e}")
        return 1
    except Exception as e:
        if 'spinner' in locals():
            spinner.fail(Fore.RED + f"✗ Unexpected error")
        click.echo(Fore.RED + f"Unexpected error: {e}")
        return 1


@channel.command()
def list():
    """List all monitored channels."""
    try:
        video_db = get_video_database()
        channels = video_db.get_channels()

        if not channels:
            click.echo(Fore.YELLOW + "No channels are currently being monitored.")
            click.echo(Fore.WHITE + "Add a channel with: python cli.py channel add <channel_url>")
            return

        click.echo(Fore.CYAN + f"Monitored Channels ({len(channels)} total)")
        click.echo("=" * 60)

        for channel in channels:
            status = "🟢 Active" if channel['active'] else "🔴 Inactive"
            last_check = channel['last_check'] or "Never"
            if channel['last_check']:
                try:
                    last_check_dt = datetime.fromisoformat(channel['last_check'])
                    last_check = last_check_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass

            click.echo(f"\n{Fore.WHITE}{channel['name']}")
            click.echo(f"  Status: {status}")
            click.echo(f"  Channel ID: {channel['channel_id']}")
            click.echo(f"  URL: {channel['url']}")
            click.echo(f"  Check interval: {channel['check_interval']} hours")
            click.echo(f"  Last check: {last_check}")

            if channel['filters']:
                click.echo(f"  Filters: {json.dumps(channel['filters'], indent=4)}")

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}")
        return 1


@channel.command()
@click.argument('channel_id')
def remove(channel_id):
    """Remove a channel from monitoring."""
    try:
        channel_monitor = get_channel_monitor()

        # Get channel info first
        video_db = get_video_database()
        channel = video_db.get_channel(channel_id)

        if not channel:
            click.echo(Fore.RED + f"Channel not found: {channel_id}")
            return 1

        # Confirm removal
        if not click.confirm(f"Remove channel '{channel['name']}' from monitoring?"):
            click.echo("Cancelled.")
            return

        success = channel_monitor.remove_channel(channel_id)

        if success:
            click.echo(Fore.GREEN + f"✓ Removed channel: {channel['name']}")
        else:
            click.echo(Fore.RED + f"Failed to remove channel: {channel_id}")
            return 1

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}")
        return 1


@channel.command()
@click.argument('channel_id')
@click.option('--check-interval', type=int, help='Update check interval in hours')
@click.option('--active/--inactive', default=None, help='Enable/disable monitoring')
def update(channel_id, check_interval, active):
    """Update channel monitoring settings."""
    try:
        video_db = get_video_database()

        # Get current channel info
        channel = video_db.get_channel(channel_id)
        if not channel:
            click.echo(Fore.RED + f"Channel not found: {channel_id}")
            return 1

        # Build update parameters
        updates = {}
        if check_interval is not None:
            updates['check_interval'] = check_interval
        if active is not None:
            updates['active'] = active

        if not updates:
            click.echo(Fore.YELLOW + "No updates specified.")
            return

        success = video_db.update_channel(channel_id, **updates)

        if success:
            click.echo(Fore.GREEN + f"✓ Updated channel: {channel['name']}")
            for key, value in updates.items():
                click.echo(f"  {key}: {value}")
        else:
            click.echo(Fore.RED + f"Failed to update channel: {channel_id}")
            return 1

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}")
        return 1


@channel.command()
@click.option('--channel-id', help='Scan specific channel by ID')
@click.option('--all', 'scan_all', is_flag=True, help='Scan all active channels')
@click.option('--force', is_flag=True, help='Force scan even if recently checked')
def scan(channel_id, scan_all, force):
    """Manually trigger channel scanning for new videos."""
    try:
        channel_monitor = get_channel_monitor()

        if channel_id:
            # Scan specific channel
            spinner = Halo(text=f'Scanning channel...', spinner='dots')
            spinner.start()

            result = channel_monitor.scan_channel(channel_id, force=force)

            spinner.succeed(Fore.GREEN + f"✓ Scan completed: {result['channel_name']}")

            click.echo(f"Videos found: {result['total_videos_found']}")
            click.echo(f"After filtering: {result['filtered_videos']}")
            click.echo(f"New videos: {result['new_videos']}")
            click.echo(f"Queued for processing: {result['queued_for_processing']}")
            click.echo(f"Skipped: {result['skipped_videos']}")

            if result['queued_for_processing'] > 0:
                click.echo(Fore.CYAN + f"\n💡 {result['queued_for_processing']} videos added to processing queue")
                click.echo("Videos will be processed gradually to avoid rate limiting")
                click.echo("Use 'python cli.py service start' to enable background processing")

        elif scan_all:
            # Scan all channels
            spinner = Halo(text='Scanning all channels...', spinner='dots')
            spinner.start()

            results = channel_monitor.scan_all_channels()

            spinner.succeed(Fore.GREEN + f"✓ Scan completed for {results['total_channels']} channels")

            click.echo(f"Successful scans: {results['successful_scans']}")
            click.echo(f"Failed scans: {results['failed_scans']}")
            click.echo(f"Total new videos: {results['total_new_videos']}")

            if results['channel_results']:
                click.echo("\nChannel Results:")
                for result in results['channel_results']:
                    status_icon = "✓" if result['status'] == 'success' else "✗"
                    click.echo(f"  {status_icon} {result['channel_name']}: {result.get('new_videos', 0)} new videos")
        else:
            click.echo(Fore.YELLOW + "Please specify --channel-id or --all")
            return 1

    except Exception as e:
        if 'spinner' in locals():
            spinner.fail(Fore.RED + f"✗ Scan failed")
        click.echo(Fore.RED + f"Error: {e}")
        return 1


# =============================================================================
# BULK IMPORT COMMANDS
# =============================================================================

@cli.group()
def import_cmd():
    """Bulk import YouTube videos and channels."""
    pass

# Rename the group to avoid Python keyword conflict
cli.add_command(import_cmd, name='import')


@import_cmd.command()
@click.argument('channel_url')
@click.option('--limit', default=50, help='Maximum number of videos to import (default: 50)')
@click.option('--date-from', help='Import videos published after this date (YYYY-MM-DD)')
@click.option('--date-to', help='Import videos published before this date (YYYY-MM-DD)')
@click.option('--include-keywords', multiple=True, help='Include videos with these keywords')
@click.option('--exclude-keywords', multiple=True, help='Exclude videos with these keywords')
@click.option('--min-duration', type=int, help='Minimum video duration in seconds')
@click.option('--max-duration', type=int, help='Maximum video duration in seconds')
@click.option('--no-shorts', is_flag=True, help='Exclude YouTube Shorts (videos < 60s)')
@click.option('--no-live', is_flag=True, help='Exclude live streams')
@click.option('--dry-run', is_flag=True, help='Preview what would be imported without processing')
@click.option('--no-n8n', is_flag=True, help='Skip sending to n8n workflow')
def channel(channel_url, limit, date_from, date_to, include_keywords, exclude_keywords,
           min_duration, max_duration, no_shorts, no_live, dry_run, no_n8n):
    """Import videos from a YouTube channel."""
    try:
        bulk_importer = get_bulk_importer()

        # Parse dates
        date_from_dt = None
        date_to_dt = None

        if date_from:
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                click.echo(Fore.RED + f"Invalid date format for --date-from: {date_from}")
                return 1

        if date_to:
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                click.echo(Fore.RED + f"Invalid date format for --date-to: {date_to}")
                return 1

        # Build filters
        filters = {}
        if include_keywords:
            filters['include_keywords'] = list(include_keywords)
        if exclude_keywords:
            filters['exclude_keywords'] = list(exclude_keywords)
        if min_duration:
            filters['min_duration'] = min_duration
        if max_duration:
            filters['max_duration'] = max_duration
        if no_shorts:
            filters['no_shorts'] = True
        if no_live:
            filters['no_live'] = True

        # Perform import
        result = bulk_importer.import_from_channel(
            channel_url=channel_url,
            limit=limit,
            date_from=date_from_dt,
            date_to=date_to_dt,
            filters=filters if filters else None,
            dry_run=dry_run,
            send_to_n8n=not no_n8n
        )

        if dry_run:
            click.echo(Fore.CYAN + "=== DRY RUN RESULTS ===")
            click.echo(f"Source: {result['source']}")
            click.echo(f"Total videos: {result['total_videos']}")
            click.echo(f"Total duration: {result['total_duration_formatted']}")
            click.echo(f"Estimated processing time: {result['estimated_processing_time']}")

            if result['videos_preview']:
                click.echo("\nFirst 10 videos:")
                for video in result['videos_preview']:
                    click.echo(f"  • {video['title']} ({video['duration']})")
        else:
            click.echo(Fore.GREEN + "=== IMPORT COMPLETED ===")
            click.echo(f"Total videos found: {result['total_videos']}")
            click.echo(f"New videos imported: {result['new_videos']}")
            click.echo(f"Successfully processed: {result['processed_videos']}")
            click.echo(f"Skipped (already exists): {result['skipped_videos']}")
            click.echo(f"Failed to process: {result['failed_videos']}")

    except Exception as e:
        click.echo(Fore.RED + f"Channel import failed: {e}")
        return 1


@import_cmd.command()
@click.argument('playlist_url')
@click.option('--limit', default=50, help='Maximum number of videos to import (default: 50)')
@click.option('--include-keywords', multiple=True, help='Include videos with these keywords')
@click.option('--exclude-keywords', multiple=True, help='Exclude videos with these keywords')
@click.option('--min-duration', type=int, help='Minimum video duration in seconds')
@click.option('--max-duration', type=int, help='Maximum video duration in seconds')
@click.option('--no-shorts', is_flag=True, help='Exclude YouTube Shorts (videos < 60s)')
@click.option('--no-live', is_flag=True, help='Exclude live streams')
@click.option('--dry-run', is_flag=True, help='Preview what would be imported without processing')
@click.option('--no-n8n', is_flag=True, help='Skip sending to n8n workflow')
def playlist(playlist_url, limit, include_keywords, exclude_keywords,
            min_duration, max_duration, no_shorts, no_live, dry_run, no_n8n):
    """Import videos from a YouTube playlist."""
    try:
        bulk_importer = get_bulk_importer()

        # Build filters
        filters = {}
        if include_keywords:
            filters['include_keywords'] = list(include_keywords)
        if exclude_keywords:
            filters['exclude_keywords'] = list(exclude_keywords)
        if min_duration:
            filters['min_duration'] = min_duration
        if max_duration:
            filters['max_duration'] = max_duration
        if no_shorts:
            filters['no_shorts'] = True
        if no_live:
            filters['no_live'] = True

        # Perform import
        result = bulk_importer.import_from_playlist(
            playlist_url=playlist_url,
            limit=limit,
            filters=filters if filters else None,
            dry_run=dry_run,
            send_to_n8n=not no_n8n
        )

        if dry_run:
            click.echo(Fore.CYAN + "=== DRY RUN RESULTS ===")
            click.echo(f"Source: {result['source']}")
            click.echo(f"Total videos: {result['total_videos']}")
            click.echo(f"Total duration: {result['total_duration_formatted']}")
            click.echo(f"Estimated processing time: {result['estimated_processing_time']}")
        else:
            click.echo(Fore.GREEN + "=== IMPORT COMPLETED ===")
            click.echo(f"Total videos found: {result['total_videos']}")
            click.echo(f"New videos imported: {result['new_videos']}")
            click.echo(f"Successfully processed: {result['processed_videos']}")
            click.echo(f"Skipped (already exists): {result['skipped_videos']}")
            click.echo(f"Failed to process: {result['failed_videos']}")

    except Exception as e:
        click.echo(Fore.RED + f"Playlist import failed: {e}")
        return 1


@import_cmd.command()
@click.argument('file_path')
@click.option('--include-keywords', multiple=True, help='Include videos with these keywords')
@click.option('--exclude-keywords', multiple=True, help='Exclude videos with these keywords')
@click.option('--min-duration', type=int, help='Minimum video duration in seconds')
@click.option('--max-duration', type=int, help='Maximum video duration in seconds')
@click.option('--no-shorts', is_flag=True, help='Exclude YouTube Shorts (videos < 60s)')
@click.option('--no-live', is_flag=True, help='Exclude live streams')
@click.option('--dry-run', is_flag=True, help='Preview what would be imported without processing')
@click.option('--no-n8n', is_flag=True, help='Skip sending to n8n workflow')
def file(file_path, include_keywords, exclude_keywords, min_duration, max_duration,
         no_shorts, no_live, dry_run, no_n8n):
    """Import videos from a file containing YouTube URLs (one per line)."""
    try:
        bulk_importer = get_bulk_importer()

        # Build filters
        filters = {}
        if include_keywords:
            filters['include_keywords'] = list(include_keywords)
        if exclude_keywords:
            filters['exclude_keywords'] = list(exclude_keywords)
        if min_duration:
            filters['min_duration'] = min_duration
        if max_duration:
            filters['max_duration'] = max_duration
        if no_shorts:
            filters['no_shorts'] = True
        if no_live:
            filters['no_live'] = True

        # Perform import
        result = bulk_importer.import_from_file(
            file_path=file_path,
            filters=filters if filters else None,
            dry_run=dry_run,
            send_to_n8n=not no_n8n
        )

        if dry_run:
            click.echo(Fore.CYAN + "=== DRY RUN RESULTS ===")
            click.echo(f"Source: {result['source']}")
            click.echo(f"Total videos: {result['total_videos']}")
            click.echo(f"Total duration: {result['total_duration_formatted']}")
            click.echo(f"Estimated processing time: {result['estimated_processing_time']}")
        else:
            click.echo(Fore.GREEN + "=== IMPORT COMPLETED ===")
            click.echo(f"Total videos found: {result['total_videos']}")
            click.echo(f"New videos imported: {result['new_videos']}")
            click.echo(f"Successfully processed: {result['processed_videos']}")
            click.echo(f"Skipped (already exists): {result['skipped_videos']}")
            click.echo(f"Failed to process: {result['failed_videos']}")

    except Exception as e:
        click.echo(Fore.RED + f"File import failed: {e}")
        return 1


# =============================================================================
# N8N CONFIGURATION COMMANDS
# =============================================================================

@cli.group()
def n8n():
    """Configure n8n RAG workflow integration."""
    pass


@n8n.command()
@click.argument('webhook_url')
@click.option('--api-key', help='Optional API key for authentication')
@click.option('--disable', is_flag=True, help='Disable n8n integration')
def configure(webhook_url, api_key, disable):
    """Configure n8n webhook URL and settings."""
    try:
        channel_monitor = get_channel_monitor()

        channel_monitor.configure_n8n(
            webhook_url=webhook_url,
            api_key=api_key,
            enabled=not disable
        )

        status = "disabled" if disable else "enabled"
        click.echo(Fore.GREEN + f"✓ n8n integration {status}")
        click.echo(f"Webhook URL: {webhook_url}")
        if api_key:
            click.echo(f"API Key: {'*' * len(api_key)}")

    except Exception as e:
        click.echo(Fore.RED + f"Configuration failed: {e}")
        return 1


@n8n.command()
@click.argument('video_id')
def send(video_id):
    """Manually send a specific video to n8n workflow."""
    try:
        video_db = get_video_database()

        # Get video from database
        videos = video_db.get_videos()
        video = next((v for v in videos if v['video_id'] == video_id), None)

        if not video:
            click.echo(Fore.RED + f"Video not found: {video_id}")
            return 1

        if not video['transcript']:
            click.echo(Fore.YELLOW + f"Video has no transcript: {video['title']}")
            return 1

        # Send to n8n
        n8n_client = get_n8n_client()

        payload = {
            'video_id': video['video_id'],
            'title': video['title'],
            'description': video['description'],
            'url': video['url'],
            'transcript': video['transcript'],
            'metadata': video['metadata'] or {}
        }

        spinner = Halo(text='Sending to n8n workflow...', spinner='dots')
        spinner.start()

        response = n8n_client.send_video_data(payload)

        spinner.succeed(Fore.GREEN + f"✓ Sent video to n8n: {video['title']}")

        if response.get('mock'):
            click.echo(Fore.YELLOW + "Note: Using mock response (n8n not configured)")

    except Exception as e:
        if 'spinner' in locals():
            spinner.fail(Fore.RED + f"✗ Failed to send video")
        click.echo(Fore.RED + f"Error: {e}")
        return 1


# =============================================================================
# STATISTICS AND HISTORY COMMANDS
# =============================================================================

@cli.command()
def stats():
    """Show monitoring and import statistics."""
    try:
        video_db = get_video_database()
        stats = video_db.get_statistics()

        click.echo(Fore.CYAN + "=== YouTube Chat CLI Statistics ===")
        click.echo()

        # Channel stats
        click.echo(Fore.WHITE + "📺 Channels:")
        click.echo(f"  Active: {stats['channels']['active']}")
        click.echo(f"  Total: {stats['channels']['total']}")
        click.echo()

        # Video stats
        click.echo(Fore.WHITE + "🎥 Videos:")
        click.echo(f"  Total: {stats['videos']['total']}")
        click.echo(f"  Processed: {stats['videos']['processed']}")
        click.echo(f"  Pending: {stats['videos']['pending']}")
        click.echo(f"  Last 24h: {stats['videos']['last_24h']}")
        click.echo()

        # Import job stats
        click.echo(Fore.WHITE + "⚙️ Import Jobs:")
        click.echo(f"  Currently running: {stats['import_jobs']['running']}")

        # Processing rate
        if stats['videos']['total'] > 0:
            success_rate = (stats['videos']['processed'] / stats['videos']['total']) * 100
            click.echo()
            click.echo(Fore.WHITE + "📊 Success Rate:")
            click.echo(f"  {success_rate:.1f}% of videos successfully processed")

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}")
        return 1


@cli.command()
@click.option('--channel-id', help='Show history for specific channel')
@click.option('--limit', default=20, help='Number of recent items to show (default: 20)')
def history(channel_id, limit):
    """View import history and recent activity."""
    try:
        video_db = get_video_database()
        bulk_importer = get_bulk_importer()

        if channel_id:
            # Show videos for specific channel
            videos = video_db.get_videos(channel_id=channel_id, limit=limit)

            if not videos:
                click.echo(Fore.YELLOW + f"No videos found for channel: {channel_id}")
                return

            click.echo(Fore.CYAN + f"Recent Videos for Channel ({len(videos)} shown)")
            click.echo("=" * 60)

            for video in videos:
                status_icon = {
                    'processed': '✅',
                    'failed': '❌',
                    'pending': '⏳',
                    'skipped': '⏭️'
                }.get(video['status'], '❓')

                published = video['published_at'] or 'Unknown'
                if video['published_at']:
                    try:
                        published_dt = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                        published = published_dt.strftime("%Y-%m-%d")
                    except:
                        pass

                click.echo(f"\n{status_icon} {video['title']}")
                click.echo(f"   Published: {published}")
                click.echo(f"   Status: {video['status']}")
                click.echo(f"   URL: {video['url']}")
        else:
            # Show import job history
            jobs = bulk_importer.get_import_history(limit=limit)

            if not jobs:
                click.echo(Fore.YELLOW + "No import history found.")
                return

            click.echo(Fore.CYAN + f"Import Job History ({len(jobs)} shown)")
            click.echo("=" * 60)

            for job in jobs:
                status_icon = {
                    'completed': '✅',
                    'failed': '❌',
                    'running': '🔄',
                    'pending': '⏳',
                    'cancelled': '🚫'
                }.get(job['status'], '❓')

                created = job['created_at']
                try:
                    created_dt = datetime.fromisoformat(job['created_at'])
                    created = created_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass

                click.echo(f"\n{status_icon} {job['type'].title()} Import")
                click.echo(f"   Source: {job['source']}")
                click.echo(f"   Status: {job['status']}")
                click.echo(f"   Progress: {job['progress']}/{job['total']}")
                click.echo(f"   Created: {created}")

                if job['error_message']:
                    click.echo(f"   Error: {job['error_message']}")

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}")
        return 1


# =============================================================================
# BACKGROUND SERVICE COMMANDS
# =============================================================================

@cli.group()
def service():
    """Manage the background monitoring service."""
    pass


@service.command()
@click.option('--daemon', is_flag=True, help='Run as daemon process')
def start(daemon):
    """Start the background monitoring service."""
    try:
        monitoring_service = get_monitoring_service()

        if monitoring_service.is_running():
            click.echo(Fore.YELLOW + "Service is already running")
            return

        click.echo(Fore.CYAN + "Starting YouTube monitoring service...")

        success = monitoring_service.start(daemon=daemon)

        if success:
            click.echo(Fore.GREEN + "✓ Service started successfully")

            if not daemon:
                click.echo(Fore.WHITE + "Service is running in the background")
                click.echo("Use 'python cli.py service status' to check status")
                click.echo("Use 'python cli.py service stop' to stop the service")
        else:
            click.echo(Fore.RED + "✗ Failed to start service")
            return 1

    except Exception as e:
        click.echo(Fore.RED + f"Error starting service: {e}")
        return 1


@service.command()
def stop():
    """Stop the background monitoring service."""
    try:
        monitoring_service = get_monitoring_service()

        if not monitoring_service.is_running():
            click.echo(Fore.YELLOW + "Service is not running")
            return

        click.echo(Fore.CYAN + "Stopping YouTube monitoring service...")

        success = monitoring_service.stop()

        if success:
            click.echo(Fore.GREEN + "✓ Service stopped successfully")
        else:
            click.echo(Fore.RED + "✗ Failed to stop service")
            return 1

    except Exception as e:
        click.echo(Fore.RED + f"Error stopping service: {e}")
        return 1


@service.command()
def status():
    """Check the status of the background monitoring service."""
    try:
        monitoring_service = get_monitoring_service()
        status = monitoring_service.get_status()

        # Service status
        if status['running']:
            click.echo(Fore.GREEN + "🟢 Service Status: RUNNING")
        else:
            click.echo(Fore.RED + "🔴 Service Status: STOPPED")

        click.echo(f"PID File: {status['pid_file']}")
        click.echo(f"Log File: {status['log_file']}")

        # Scheduled jobs
        if 'jobs' in status and status['jobs']:
            click.echo(Fore.CYAN + "\n📅 Scheduled Jobs:")
            for job in status['jobs']:
                next_run = job['next_run'] or 'Not scheduled'
                if job['next_run']:
                    try:
                        next_run_dt = datetime.fromisoformat(job['next_run'].replace('Z', '+00:00'))
                        next_run = next_run_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                    except:
                        pass

                click.echo(f"  • {job['name']}")
                click.echo(f"    Next run: {next_run}")

        # Queue status
        if 'queue' in status:
            queue_info = status['queue']
            click.echo(Fore.CYAN + "\n📊 Processing Queue:")

            queue_stats = queue_info.get('queue_stats', {})
            for status_type, count in queue_stats.items():
                click.echo(f"  {status_type.title()}: {count}")

            videos_today = queue_info.get('videos_processed_today', 0)
            daily_limit = queue_info.get('daily_limit', 5)
            click.echo(f"  Today: {videos_today}/{daily_limit} videos processed")

            next_scheduled = queue_info.get('next_scheduled_video')
            if next_scheduled:
                try:
                    next_dt = datetime.fromisoformat(next_scheduled)
                    next_formatted = next_dt.strftime("%Y-%m-%d %H:%M:%S")
                    click.echo(f"  Next video: {next_formatted}")
                except:
                    click.echo(f"  Next video: {next_scheduled}")

    except Exception as e:
        click.echo(Fore.RED + f"Error getting service status: {e}")
        return 1


@service.command()
@click.option('--lines', default=50, help='Number of log lines to show (default: 50)')
def logs(lines):
    """View service logs."""
    try:
        monitoring_service = get_monitoring_service()
        log_content = monitoring_service.get_logs(lines=lines)

        click.echo(Fore.CYAN + f"=== Service Logs (last {lines} lines) ===")
        click.echo(log_content)

    except Exception as e:
        click.echo(Fore.RED + f"Error reading logs: {e}")
        return 1


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}", err=True)
        return 1
    return 0


if __name__ == "__main__":
    main()
