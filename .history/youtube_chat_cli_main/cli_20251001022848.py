"""
CLI module for the Personal Research Insight CLI tool.
"""

import uuid
import click
from colorama import init, Fore, Style
from halo import Halo
from dotenv import load_dotenv
from session_manager import SessionManager
from source_processor import get_source_processor
from llm_service import get_llm_service
from tts_service import get_tts_service
from tts_config import get_tts_config_manager
from n8n_client import get_n8n_client
from file_processor import get_file_processor, FileProcessingError

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
def install(library_name):
    """Install a TTS library."""
    tts_manager = get_tts_config_manager()

    if tts_manager.is_library_installed(library_name):
        click.echo(Fore.YELLOW + f"Library '{library_name}' is already installed.")
        return 0

    spinner = Halo(text=f'Installing {library_name}...', spinner='dots')
    spinner.start()

    try:
        success, message = tts_manager.install_library(library_name)

        if success:
            spinner.succeed(Fore.GREEN + message)
        else:
            spinner.fail(Fore.RED + message)
            return 1

    except Exception as e:
        spinner.fail(Fore.RED + f"Installation failed: {e}")
        return 1

    return 0


@tts.command()
@click.option('--force', '-f', is_flag=True, help='Reinstall all libraries even if already installed')
def install_all(force):
    """Install all available TTS libraries at once."""
    tts_manager = get_tts_config_manager()
    libraries = tts_manager.list_libraries()

    click.echo(Fore.CYAN + f"Installing all TTS libraries ({len(libraries)} total)")
    click.echo(Fore.YELLOW + "⚠️  Note: Some libraries require Git installation and may take several minutes.")
    click.echo(Fore.YELLOW + "     Large model downloads and compilation may be required for some libraries.")
    click.echo()

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for lib_id, lib_spec in libraries.items():
        if not force and tts_manager.is_library_installed(lib_id):
            click.echo(f"{Fore.YELLOW}○ Skipping {lib_spec.name} (already installed)")
            skipped_count += 1
            continue

        click.echo(f"{Fore.BLUE}Installing {lib_spec.name}...")
        spinner = Halo(text=f'Installing {lib_id}...', spinner='dots')
        spinner.start()

        try:
            spinner.text = f'Installing {lib_spec.name} (with dependency pre-install)...'
            success, message = tts_manager.install_library(lib_id)

            if success:
                spinner.succeed(Fore.GREEN + f"{lib_spec.name}: {message}")
                success_count += 1
            else:
                # Show more detailed error information
                spinner.fail(Fore.RED + f"{lib_spec.name}: {message}")

                # Provide installation guidance for complex libraries
                guidance = tts_manager._get_installation_guidance(lib_id)
                if guidance:
                    click.echo(Fore.YELLOW + f"  {guidance}")

                failed_count += 1

        except Exception as e:
            spinner.fail(Fore.RED + f"{lib_spec.name}: Installation failed: {e}")

            # Provide installation guidance for complex libraries
            guidance = tts_manager._get_installation_guidance(lib_id)
            if guidance:
                click.echo(Fore.YELLOW + f"  {guidance}")

            failed_count += 1

    # Summary
    click.echo()
    click.echo(Fore.CYAN + "=== Installation Summary ===")
    click.echo(f"{Fore.GREEN}Successfully installed: {success_count}")
    if skipped_count > 0:
        click.echo(f"{Fore.YELLOW}Skipped (already installed): {skipped_count}")
    if failed_count > 0:
        click.echo(f"{Fore.RED}Failed: {failed_count}")

    if success_count > 0:
        click.echo()
        click.echo(Fore.GREEN + "You can now test all installed libraries with:")
        click.echo(Fore.WHITE + "  python cli.py tts test <library_name>")
        click.echo(Fore.GREEN + "Or set a default library with:")
        click.echo(Fore.WHITE + "  python cli.py tts set-default <library_name>")

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


@cli.command('process-file')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--session-id', default=None, help='Session ID for tracking (auto-generated if not provided)')
def process_file_command(file_path, session_id):
    """Process a file and add it to the n8n RAG knowledge base.

    Supports 600+ file types including PDF, DOCX, images, code files, and more.

    Example:
        python -m youtube_chat_cli_main.cli process-file document.pdf
        python -m youtube_chat_cli_main.cli process-file meeting_notes.docx --session-id my-session
    """
    init(autoreset=True)

    try:
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        click.echo(Fore.CYAN + f"\n{'='*60}")
        click.echo(Fore.CYAN + "File Processing for RAG Knowledge Base")
        click.echo(Fore.CYAN + f"{'='*60}\n")

        # Get file processor
        file_processor = get_file_processor()

        # Get file info
        file_info = file_processor.get_file_info(file_path)
        click.echo(f"File: {file_info['name']}")
        click.echo(f"Size: {file_info['size']:,} bytes")
        click.echo(f"Type: {file_info['extension']}")
        click.echo(f"Session ID: {session_id}\n")

        # Process file
        spinner = Halo(text='Processing file...', spinner='dots')
        spinner.start()

        try:
            result = file_processor.process_file_for_rag(file_path, session_id)
            spinner.succeed('File processed successfully!')

            click.echo(Fore.GREEN + f"\n✓ {result['message']}")

            if result.get('chunks_created', 0) > 0:
                click.echo(f"  Chunks created: {result['chunks_created']}")
                click.echo(f"  Vectors stored: {result['vectors_stored']}")

        except FileProcessingError as e:
            spinner.fail('File processing failed')
            click.echo(Fore.RED + f"\n✗ Error: {e}")
            return 1

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}", err=True)
        logger.exception("File processing failed")
        return 1

    return 0


@cli.command('generate-podcast-from-rag')
@click.option('--query', required=True, help='Query to retrieve content from RAG knowledge base')
@click.option('--output', default='rag_podcast.wav', help='Output audio file path')
@click.option('--session-id', default=None, help='Session ID for conversation context')
@click.option('--max-duration', default=30, help='Target podcast duration in minutes')
def generate_podcast_from_rag_command(query, output, session_id, max_duration):
    """Generate a podcast from n8n RAG knowledge base content.

    This command:
    1. Queries the n8n RAG agent with your request
    2. Retrieves relevant content from the vector database
    3. Generates a conversational podcast script
    4. Creates high-quality audio using MeloTTS (4/5 quality)

    Example:
        python -m youtube_chat_cli_main.cli generate-podcast-from-rag \\
            --query "Summarize all meeting notes from this week" \\
            --output weekly_summary.wav

        python -m youtube_chat_cli_main.cli generate-podcast-from-rag \\
            --query "Explain the key points from the uploaded research papers" \\
            --max-duration 45
    """
    init(autoreset=True)

    try:
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        click.echo(Fore.CYAN + f"\n{'='*60}")
        click.echo(Fore.CYAN + "Generate Podcast from RAG Knowledge Base")
        click.echo(Fore.CYAN + f"{'='*60}\n")

        click.echo(f"Query: {query}")
        click.echo(f"Output: {output}")
        click.echo(f"Target Duration: {max_duration} minutes")
        click.echo(f"Session ID: {session_id}\n")

        # Step 1: Query n8n RAG agent
        click.echo(Fore.YELLOW + "Step 1: Querying RAG knowledge base...")
        spinner = Halo(text='Retrieving content from vector database...', spinner='dots')
        spinner.start()

        try:
            n8n_client = get_n8n_client()
            rag_response = n8n_client.send_message(query, session_id)
            spinner.succeed('Content retrieved successfully!')

            click.echo(Fore.GREEN + f"\n✓ RAG Response ({len(rag_response)} characters):")
            click.echo(f"  {rag_response[:200]}..." if len(rag_response) > 200 else f"  {rag_response}")

        except Exception as e:
            spinner.fail('RAG query failed')
            click.echo(Fore.RED + f"\n✗ Error querying RAG: {e}")
            click.echo(Fore.YELLOW + "\nNote: Ensure n8n server is running and workflow is active.")
            click.echo(Fore.YELLOW + "See N8N_INTEGRATION_ANALYSIS_AND_FIX.md for setup instructions.")
            return 1

        # Step 2: Generate podcast script from RAG content
        click.echo(Fore.YELLOW + "\nStep 2: Generating podcast script...")
        spinner = Halo(text='Creating conversational script...', spinner='dots')
        spinner.start()

        try:
            llm_service = get_llm_service()

            # Create prompt for podcast script generation
            script_prompt = f"""Based on the following content from our knowledge base, create an engaging conversational podcast script between two hosts discussing the topic.

Content from RAG:
{rag_response}

Create a {max_duration}-minute podcast script with:
- Natural, conversational dialogue
- Two distinct hosts with different perspectives
- Clear explanations of key concepts
- Engaging transitions and questions
- A strong opening and closing

Format the script as:
Host 1: [dialogue]
Host 2: [dialogue]
"""

            script = llm_service.generate_text(script_prompt)
            spinner.succeed('Podcast script generated!')

            click.echo(Fore.GREEN + f"\n✓ Script generated ({len(script)} characters)")

        except Exception as e:
            spinner.fail('Script generation failed')
            click.echo(Fore.RED + f"\n✗ Error generating script: {e}")
            return 1

        # Step 3: Generate audio using TTS
        click.echo(Fore.YELLOW + "\nStep 3: Generating audio with MeloTTS (4/5 quality)...")
        spinner = Halo(text='Converting script to speech...', spinner='dots')
        spinner.start()

        try:
            tts_service = get_tts_service()
            audio_file = tts_service.generate_audio(script, output)
            spinner.succeed('Audio generated successfully!')

            click.echo(Fore.GREEN + f"\n✓ Podcast created: {audio_file}")

        except Exception as e:
            spinner.fail('Audio generation failed')
            click.echo(Fore.RED + f"\n✗ Error generating audio: {e}")
            return 1

        # Success summary
        click.echo(Fore.GREEN + f"\n{'='*60}")
        click.echo(Fore.GREEN + "✓ Podcast Generation Complete!")
        click.echo(Fore.GREEN + f"{'='*60}")
        click.echo(f"\nOutput file: {output}")
        click.echo(f"Quality: 4/5 (MeloTTS)")
        click.echo(f"Source: n8n RAG Knowledge Base")

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}", err=True)
        logger.exception("RAG podcast generation failed")
        return 1

    return 0


@cli.command('list-supported-files')
def list_supported_files_command():
    """List all supported file types for n8n RAG processing.

    Shows the 600+ file types that can be processed through the n8n workflow.
    """
    init(autoreset=True)

    try:
        file_processor = get_file_processor()
        summary = file_processor.get_supported_file_types_summary()

        click.echo(Fore.CYAN + f"\n{'='*60}")
        click.echo(Fore.CYAN + "Supported File Types for n8n RAG Processing")
        click.echo(Fore.CYAN + f"{'='*60}\n")

        click.echo(summary)

        click.echo(Fore.YELLOW + f"\n{'='*60}")
        click.echo(Fore.YELLOW + "Usage Examples:")
        click.echo(Fore.YELLOW + f"{'='*60}\n")

        click.echo("1. Process a single file:")
        click.echo(Fore.GREEN + "   python -m youtube_chat_cli_main.cli process-file document.pdf\n")

        click.echo("2. Generate podcast from RAG content:")
        click.echo(Fore.GREEN + "   python -m youtube_chat_cli_main.cli generate-podcast-from-rag \\")
        click.echo(Fore.GREEN + "       --query \"Summarize the uploaded documents\"\n")

        click.echo("3. Query the RAG knowledge base:")
        click.echo(Fore.GREEN + "   python -m youtube_chat_cli_main.cli invoke-n8n \\")
        click.echo(Fore.GREEN + "       \"What are the key points from the meeting notes?\"\n")

    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}", err=True)
        return 1

    return 0


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
