"""
Personal Research Insight CLI package.
"""

import logging
import sys
from pathlib import Path

# Set up logging
def setup_logging(debug: bool = False):
    """Set up logging configuration for the application."""
    log_level = logging.DEBUG if debug else logging.INFO

    # Create logs directory if it doesn't exist
    log_dir = Path.home() / ".youtube-chat-cli" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "cli.log"),
            logging.StreamHandler(sys.stderr)
        ]
    )

    # Suppress verbose logging from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

# Get logger for this package
logger = logging.getLogger(__name__)

# Custom exception classes for better error handling
class CLIError(Exception):
    """Base exception for CLI-specific errors."""
    pass

class APIError(CLIError):
    """Error related to external API calls."""
    pass

class ProcessingError(CLIError):
    """Error related to content processing."""
    pass

class SessionError(CLIError):
    """Error related to session management."""
    pass
