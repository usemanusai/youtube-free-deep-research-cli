"""
JAEGIS NexusSync - Configuration Management

This module provides centralized configuration management with environment variable
loading, validation, and type conversion.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


class Config:
    """
    Centralized configuration manager for JAEGIS NexusSync.
    
    Loads configuration from environment variables (.env file) and provides
    validated access to all configuration values.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Path to .env file (default: .env in current directory)
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Validate required configuration
        self._validate_config()
    
    # -------------------------------------------------------------------------
    # LLM Configuration
    # -------------------------------------------------------------------------
    
    @property
    def openrouter_api_key(self) -> Optional[str]:
        """OpenRouter API key for LLM access."""
        return os.getenv('OPENROUTER_API_KEY')
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API key (alternative to OpenRouter)."""
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def llm_model(self) -> str:
        """Default LLM model to use."""
        return os.getenv('LLM_MODEL', 'meta-llama/llama-3.1-70b-instruct')
    
    @property
    def has_llm_api_key(self) -> bool:
        """Check if any LLM API key is configured."""
        return bool(self.openrouter_api_key or self.openai_api_key)
    
    # -------------------------------------------------------------------------
    # Google Drive Configuration
    # -------------------------------------------------------------------------
    
    @property
    def google_client_secrets_file(self) -> str:
        """Path to Google OAuth 2.0 client secrets JSON file."""
        return os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'client_secret.json')
    
    @property
    def google_drive_folder_id(self) -> Optional[str]:
        """Google Drive folder ID to monitor."""
        return os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    @property
    def google_drive_poll_interval(self) -> int:
        """Google Drive polling interval in seconds."""
        return int(os.getenv('GOOGLE_DRIVE_POLL_INTERVAL', '60'))
    
    @property
    def has_google_drive_config(self) -> bool:
        """Check if Google Drive is configured."""
        return os.path.exists(self.google_client_secrets_file)
    
    # -------------------------------------------------------------------------
    # Vector Store Configuration
    # -------------------------------------------------------------------------
    
    @property
    def vector_store_type(self) -> str:
        """Vector store type: 'qdrant' or 'chroma'."""
        return os.getenv('VECTOR_STORE_TYPE', 'qdrant').lower()
    
    @property
    def qdrant_url(self) -> Optional[str]:
        """Qdrant server URL."""
        return os.getenv('QDRANT_URL')
    
    @property
    def qdrant_api_key(self) -> Optional[str]:
        """Qdrant API key."""
        return os.getenv('QDRANT_API_KEY')
    
    @property
    def qdrant_collection_name(self) -> str:
        """Qdrant collection name."""
        return os.getenv('QDRANT_COLLECTION_NAME', 'documents')
    
    @property
    def chroma_persist_directory(self) -> str:
        """Chroma persistence directory."""
        return os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    
    @property
    def chroma_collection_name(self) -> str:
        """Chroma collection name."""
        return os.getenv('CHROMA_COLLECTION_NAME', 'documents')
    
    @property
    def has_vector_store_config(self) -> bool:
        """Check if vector store is configured."""
        if self.vector_store_type == 'qdrant':
            return bool(self.qdrant_url and self.qdrant_api_key)
        elif self.vector_store_type == 'chroma':
            return True  # Chroma works locally without credentials
        return False
    
    # -------------------------------------------------------------------------
    # Embedding Configuration
    # -------------------------------------------------------------------------
    
    @property
    def embedding_provider(self) -> str:
        """Embedding provider: 'ollama' or 'openai'."""
        return os.getenv('EMBEDDING_PROVIDER', 'ollama').lower()
    
    @property
    def ollama_base_url(self) -> str:
        """Ollama server base URL."""
        return os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    @property
    def ollama_embedding_model(self) -> str:
        """Ollama embedding model name."""
        return os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    
    @property
    def openai_embedding_model(self) -> str:
        """OpenAI embedding model name."""
        return os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    # -------------------------------------------------------------------------
    # Web Search Configuration
    # -------------------------------------------------------------------------
    
    @property
    def tavily_api_key(self) -> Optional[str]:
        """Tavily API key for web search."""
        return os.getenv('TAVILY_API_KEY')
    
    @property
    def has_web_search_config(self) -> bool:
        """Check if web search is configured."""
        return bool(self.tavily_api_key)
    
    # -------------------------------------------------------------------------
    # OCR Configuration
    # -------------------------------------------------------------------------
    
    @property
    def ocr_provider(self) -> str:
        """OCR provider: 'mistral', 'google_vision', or 'tesseract'."""
        return os.getenv('OCR_PROVIDER', 'mistral').lower()
    
    @property
    def mistral_api_key(self) -> Optional[str]:
        """Mistral API key for OCR."""
        return os.getenv('MISTRAL_API_KEY')
    
    @property
    def google_vision_credentials_file(self) -> Optional[str]:
        """Google Cloud Vision credentials file."""
        return os.getenv('GOOGLE_VISION_CREDENTIALS_FILE')
    
    @property
    def has_ocr_config(self) -> bool:
        """Check if OCR is configured."""
        if self.ocr_provider == 'mistral':
            return bool(self.mistral_api_key)
        elif self.ocr_provider == 'google_vision':
            return bool(self.google_vision_credentials_file and 
                       os.path.exists(self.google_vision_credentials_file))
        elif self.ocr_provider == 'tesseract':
            return True  # Tesseract is local
        return False
    
    # -------------------------------------------------------------------------
    # Database Configuration
    # -------------------------------------------------------------------------
    
    @property
    def database_path(self) -> str:
        """SQLite database file path."""
        return os.getenv('DATABASE_PATH', './jaegis_nexus_sync.db')
    
    # -------------------------------------------------------------------------
    # Background Service Configuration
    # -------------------------------------------------------------------------
    
    @property
    def background_service_enabled(self) -> bool:
        """Whether background service is enabled."""
        return os.getenv('BACKGROUND_SERVICE_ENABLED', 'true').lower() == 'true'
    
    @property
    def background_service_interval(self) -> int:
        """Background service check interval in seconds."""
        return int(os.getenv('BACKGROUND_SERVICE_INTERVAL', '300'))
    
    # -------------------------------------------------------------------------
    # Text Splitting Configuration
    # -------------------------------------------------------------------------
    
    @property
    def chunk_size(self) -> int:
        """Text chunk size in characters."""
        return int(os.getenv('CHUNK_SIZE', '1000'))
    
    @property
    def chunk_overlap(self) -> int:
        """Text chunk overlap in characters."""
        return int(os.getenv('CHUNK_OVERLAP', '200'))
    
    @property
    def split_by_headings(self) -> bool:
        """Whether to split text by markdown headings."""
        return os.getenv('SPLIT_BY_HEADINGS', 'true').lower() == 'true'
    
    # -------------------------------------------------------------------------
    # RAG Configuration
    # -------------------------------------------------------------------------
    
    @property
    def rag_top_k(self) -> int:
        """Number of documents to retrieve for RAG."""
        return int(os.getenv('RAG_TOP_K', '5'))
    
    @property
    def rag_min_relevance_score(self) -> float:
        """Minimum relevance score for retrieved documents."""
        return float(os.getenv('RAG_MIN_RELEVANCE_SCORE', '0.7'))
    
    @property
    def rag_max_transform_attempts(self) -> int:
        """Maximum query transformation attempts."""
        return int(os.getenv('RAG_MAX_TRANSFORM_ATTEMPTS', '3'))
    
    @property
    def rag_hallucination_check(self) -> bool:
        """Whether to enable hallucination checking."""
        return os.getenv('RAG_HALLUCINATION_CHECK', 'true').lower() == 'true'
    
    @property
    def rag_answer_check(self) -> bool:
        """Whether to enable answer relevance checking."""
        return os.getenv('RAG_ANSWER_CHECK', 'true').lower() == 'true'

    # -------------------------------------------------------------------------
    # PostgreSQL Configuration (Optional)
    # -------------------------------------------------------------------------

    @property
    def postgres_host(self) -> Optional[str]:
        """PostgreSQL host."""
        return os.getenv('POSTGRES_HOST')

    @property
    def postgres_port(self) -> int:
        """PostgreSQL port."""
        return int(os.getenv('POSTGRES_PORT', '5432'))

    @property
    def postgres_db(self) -> Optional[str]:
        """PostgreSQL database name."""
        return os.getenv('POSTGRES_DB')

    @property
    def postgres_user(self) -> Optional[str]:
        """PostgreSQL user."""
        return os.getenv('POSTGRES_USER')

    @property
    def postgres_password(self) -> Optional[str]:
        """PostgreSQL password."""
        return os.getenv('POSTGRES_PASSWORD')

    @property
    def has_postgres_config(self) -> bool:
        """Check if PostgreSQL is configured."""
        return all([
            self.postgres_host,
            self.postgres_db,
            self.postgres_user,
            self.postgres_password
        ])

    # -------------------------------------------------------------------------
    # TTS Configuration
    # -------------------------------------------------------------------------

    @property
    def marytts_server_url(self) -> Optional[str]:
        """MaryTTS server URL."""
        return os.getenv('MARYTTS_SERVER_URL')

    @property
    def tts_bridge_python(self) -> str:
        """Python 3.11 executable for TTS bridge."""
        return os.getenv('TTS_BRIDGE_PYTHON', 'python3.11')

    # -------------------------------------------------------------------------
    # n8n Integration (Backward Compatibility)
    # -------------------------------------------------------------------------

    @property
    def n8n_webhook_url(self) -> Optional[str]:
        """n8n webhook URL for legacy RAG workflow."""
        return os.getenv('N8N_WEBHOOK_URL')

    # -------------------------------------------------------------------------
    # Logging Configuration
    # -------------------------------------------------------------------------

    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv('LOG_LEVEL', 'INFO').upper()

    @property
    def log_file(self) -> str:
        """Log file path."""
        return os.getenv('LOG_FILE', './logs/jaegis_nexus_sync.log')

    # -------------------------------------------------------------------------
    # MCP Server Configuration
    # -------------------------------------------------------------------------

    @property
    def mcp_server_port(self) -> int:
        """MCP server port."""
        return int(os.getenv('MCP_SERVER_PORT', '3000'))

    @property
    def mcp_server_enabled(self) -> bool:
        """Whether MCP server is enabled."""
        return os.getenv('MCP_SERVER_ENABLED', 'false').lower() == 'true'

    # -------------------------------------------------------------------------
    # Development/Testing Configuration
    # -------------------------------------------------------------------------

    @property
    def debug(self) -> bool:
        """Whether debug mode is enabled."""
        return os.getenv('DEBUG', 'false').lower() == 'true'

    @property
    def mock_apis(self) -> bool:
        """Whether to mock external API calls for testing."""
        return os.getenv('MOCK_APIS', 'false').lower() == 'true'

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    def _validate_config(self) -> None:
        """
        Validate configuration and log warnings for missing optional components.

        Raises:
            ConfigurationError: If required configuration is missing
        """
        # Check for at least one LLM API key
        if not self.has_llm_api_key:
            logger.warning(
                "No LLM API key configured. Set OPENROUTER_API_KEY or OPENAI_API_KEY "
                "in .env file for AI features to work."
            )

        # Check vector store configuration
        if not self.has_vector_store_config:
            logger.warning(
                f"Vector store '{self.vector_store_type}' is not properly configured. "
                "RAG features will not work until configured."
            )

        # Check web search configuration
        if not self.has_web_search_config:
            logger.warning(
                "Tavily API key not configured. Web search in Adaptive RAG will be disabled."
            )

        # Check OCR configuration
        if not self.has_ocr_config:
            logger.warning(
                f"OCR provider '{self.ocr_provider}' is not properly configured. "
                "PDF and image processing may be limited."
            )

        # Check Google Drive configuration
        if not self.has_google_drive_config:
            logger.info(
                "Google Drive not configured. Automated document ingestion will be disabled. "
                "You can still process files manually."
            )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.

        Returns:
            Dictionary with configuration status
        """
        return {
            'llm_configured': self.has_llm_api_key,
            'llm_model': self.llm_model,
            'google_drive_configured': self.has_google_drive_config,
            'vector_store_type': self.vector_store_type,
            'vector_store_configured': self.has_vector_store_config,
            'embedding_provider': self.embedding_provider,
            'web_search_configured': self.has_web_search_config,
            'ocr_provider': self.ocr_provider,
            'ocr_configured': self.has_ocr_config,
            'background_service_enabled': self.background_service_enabled,
            'mcp_server_enabled': self.mcp_server_enabled,
            'debug': self.debug,
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config(env_file: Optional[str] = None, reload: bool = False) -> Config:
    """
    Get the global configuration instance.

    Args:
        env_file: Path to .env file (only used on first call or if reload=True)
        reload: Force reload of configuration

    Returns:
        Config instance
    """
    global _config

    if _config is None or reload:
        _config = Config(env_file)
        logger.info("Configuration loaded successfully")

    return _config

