"""
JAEGIS NexusSync - Personal Research Insight CLI package.

Modular structure with backward compatibility:
- services: Business logic layer (LLM, TTS, RAG, Content, Search, Storage, Integration, Background)
- api: FastAPI backend with routes, models, and middleware
- cli: Command-line interface with organized commands
- core: Infrastructure (config, database, logging, etc.)
- workflows: LangGraph workflows
- mcp: Model Context Protocol server
- utils: Utility functions
"""

import logging
import sys
from pathlib import Path

# Import and expose key functions for external access (backward compatibility)
from .session_manager import SessionManager, get_session_manager
from .source_processor import SourceProcessor, ProcessingError, get_source_processor
from .llm_service import LLMService, get_llm_service
from .tts_service import TTSService, get_tts_service as get_tts_service_legacy
from .n8n_client import N8nClient, get_n8n_client

# Lazy imports for new modular structure
def __getattr__(name):
    """Lazy load new modular exports."""
    if name in ("BaseLLMService", "OpenRouterLLMService", "OllamaLLMService", "OpenAILLMService"):
        from . import services
        return getattr(services, name)
    elif name in ("TTSOrchestrator", "get_tts_service", "TTSBridgeClient", "TTSConfig"):
        from . import services
        return getattr(services, name)
    elif name in ("AdaptiveRAGEngine", "get_rag_engine"):
        from . import services
        return getattr(services, name)
    elif name in ("ContentProcessor", "get_content_processor"):
        from . import services
        return getattr(services, name)
    elif name in ("SearchAggregator", "WebSearchService", "BraveSearchService"):
        from . import services
        return getattr(services, name)
    elif name in ("VectorStore", "get_vector_store"):
        from . import services
        return getattr(services, name)
    elif name in ("GoogleDriveService", "get_gdrive_watcher", "EmbeddingService", "get_embedding_service"):
        from . import services
        return getattr(services, name)
    elif name in ("BackgroundService", "get_background_service"):
        from . import services
        return getattr(services, name)
    elif name in ("create_app", "app"):
        from . import api
        return getattr(api, name)
    elif name in ("get_config", "get_database"):
        from . import core
        return getattr(core, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Legacy exports (backward compatibility)
    "SessionManager",
    "get_session_manager",
    "SourceProcessor",
    "ProcessingError",
    "get_source_processor",
    "LLMService",
    "get_llm_service",
    "TTSService",
    "get_tts_service_legacy",
    "N8nClient",
    "get_n8n_client",
    # New modular exports
    "BaseLLMService",
    "OpenRouterLLMService",
    "OllamaLLMService",
    "OpenAILLMService",
    "TTSOrchestrator",
    "get_tts_service",
    "TTSBridgeClient",
    "TTSConfig",
    "AdaptiveRAGEngine",
    "get_rag_engine",
    "ContentProcessor",
    "get_content_processor",
    "SearchAggregator",
    "WebSearchService",
    "BraveSearchService",
    "VectorStore",
    "get_vector_store",
    "GoogleDriveService",
    "get_gdrive_watcher",
    "EmbeddingService",
    "get_embedding_service",
    "BackgroundService",
    "get_background_service",
    # API
    "create_app",
    "app",
    # Core
    "get_config",
    "get_database",
    # Exceptions
    "CLIError",
    "APIError",
    "SessionError",
    # Setup
    "setup_logging",
]

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

class SessionError(CLIError):
    """Error related to session management."""
    pass
