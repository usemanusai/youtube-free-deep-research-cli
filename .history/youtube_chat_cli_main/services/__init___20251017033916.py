"""Services Layer - Core business logic and integrations."""

# LLM Services
from .llm import (
    BaseLLMService,
    OpenRouterLLMService,
    OllamaLLMService,
    OpenAILLMService,
)

# TTS Services
from .tts import (
    TTSOrchestrator,
    get_tts_service,
    TTSBridgeClient,
    TTSConfig,
)

# RAG Services
from .rag import (
    AdaptiveRAGEngine,
    get_rag_engine,
    DocumentRetriever,
    DocumentGrader,
    QueryTransformer,
)

# Content Services
from .content import (
    ContentProcessor,
    get_content_processor,
    ContentValidator,
)

# Search Services
from .search import (
    SearchAggregator,
    WebSearchService,
    BraveSearchService,
    VectorStoreService,
)

# Storage Services
from .storage import (
    VectorStore,
    get_vector_store,
    SessionManager,
    get_session_manager,
    FileProcessor,
    get_file_processor,
)

# Integration Services
from .integration import (
    GoogleDriveService,
    get_gdrive_watcher,
    N8nClient,
    EmbeddingService,
    get_embedding_service,
)

# Background Services
from .background import (
    BackgroundService,
    get_background_service,
    BackgroundTasks,
)

__all__ = [
    # LLM
    "BaseLLMService",
    "OpenRouterLLMService",
    "OllamaLLMService",
    "OpenAILLMService",
    # TTS
    "TTSOrchestrator",
    "get_tts_service",
    "TTSBridgeClient",
    "TTSConfig",
    # RAG
    "AdaptiveRAGEngine",
    "get_rag_engine",
    "DocumentRetriever",
    "DocumentGrader",
    "QueryTransformer",
    # Content
    "ContentProcessor",
    "get_content_processor",
    "ContentValidator",
    # Search
    "SearchAggregator",
    "WebSearchService",
    "BraveSearchService",
    "VectorStoreService",
    # Storage
    "VectorStore",
    "get_vector_store",
    "SessionManager",
    "get_session_manager",
    "FileProcessor",
    "get_file_processor",
    # Integration
    "GoogleDriveService",
    "get_gdrive_watcher",
    "N8nClient",
    "EmbeddingService",
    "get_embedding_service",
    # Background
    "BackgroundService",
    "get_background_service",
    "BackgroundTasks",
]

