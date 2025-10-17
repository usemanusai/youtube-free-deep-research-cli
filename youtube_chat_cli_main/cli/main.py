"""
JAEGIS NexusSync - Main CLI Entry Point

Unified CLI combining:
- Original Personal Research Insight CLI commands
- New JAEGIS NexusSync RAG commands
"""

import click
import logging
from colorama import init
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """
    JAEGIS NexusSync - Adaptive RAG CLI

    Personal Research Insight CLI with advanced RAG capabilities.
    """
    pass


# Import and register RAG commands
try:
    from .rag_commands import rag
    cli.add_command(rag, name='rag')
except ImportError as e:
    logger.warning(f"Failed to import RAG commands: {e}")


# Import and register Nexus Agents commands (scaffold)
try:
    from .agents_commands import agents
    cli.add_command(agents, name='agents')
except ImportError as e:
    logger.warning(f"Failed to import Agents commands: {e}")


# Import and register original CLI commands (if available)
try:
    import sys
    from pathlib import Path

    # Add parent directory to path to import original cli.py
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    # Import original CLI commands
    from cli import session, process, chat as original_chat, podcast, blueprint

    # Register original commands
    cli.add_command(session, name='session')
    cli.add_command(process, name='process')
    cli.add_command(original_chat, name='chat-legacy')
    cli.add_command(podcast, name='podcast')
    cli.add_command(blueprint, name='blueprint')

except ImportError as e:
    logger.warning(f"Failed to import original CLI commands: {e}")


if __name__ == '__main__':
    cli()

