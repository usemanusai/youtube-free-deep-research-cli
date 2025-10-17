"""
CLI module for the Personal Research Insight CLI tool.
"""

import uuid
import click
from colorama import init, Fore, Style
from session_manager import SessionManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Create global session manager instance
session_manager = SessionManager()


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
