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

