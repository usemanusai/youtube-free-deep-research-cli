"""Services Layer - Core business logic and integrations."""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    """Lazy load services on demand."""
    if name == "BaseLLMService":
        from .llm.base import BaseLLMService
        return BaseLLMService
    elif name == "OpenRouterLLMService":
        from .llm.openrouter import OpenRouterLLMService
        return OpenRouterLLMService
    elif name == "OllamaLLMService":
        from .llm.ollama import OllamaLLMService
        return OllamaLLMService
    elif name == "OpenAILLMService":
        from .llm.openai import OpenAILLMService
        return OpenAILLMService
    elif name == "TTSOrchestrator":
        from .tts.orchestrator import TTSOrchestrator
        return TTSOrchestrator
    elif name == "get_tts_service":
        from .tts.orchestrator import get_tts_service
        return get_tts_service
    elif name == "TTSBridgeClient":
        from .tts.bridge_client import TTSBridgeClient
        return TTSBridgeClient
    elif name == "TTSConfig":
        from .tts.config import TTSConfig
        return TTSConfig
    elif name == "AdaptiveRAGEngine":
        from .rag.engine import AdaptiveRAGEngine
        return AdaptiveRAGEngine
    elif name == "get_rag_engine":
        from .rag.engine import get_rag_engine
        return get_rag_engine
    elif name == "DocumentRetriever":
        from .rag.retriever import DocumentRetriever
        return DocumentRetriever
    elif name == "DocumentGrader":
        from .rag.grader import DocumentGrader
        return DocumentGrader
    elif name == "QueryTransformer":
        from .rag.transformer import QueryTransformer
        return QueryTransformer
    elif name == "ContentProcessor":
        from .content.processor import ContentProcessor
        return ContentProcessor
    elif name == "get_content_processor":
        from .content.processor import get_content_processor
        return get_content_processor
    elif name == "ContentValidator":
        from .content.validators import ContentValidator
        return ContentValidator
    elif name == "SearchAggregator":
        from .search.aggregator import SearchAggregator
        return SearchAggregator
    elif name == "WebSearchService":
        from .search.web_search import WebSearchService
        return WebSearchService
    elif name == "BraveSearchService":
        from .search.brave_search import BraveSearchService
        return BraveSearchService
    elif name == "VectorStoreService":
        from .search.vector_store import VectorStoreService
        return VectorStoreService
    elif name == "VectorStore":
        from .storage.vector_store import VectorStore
        return VectorStore
    elif name == "get_vector_store":
        from .storage.vector_store import get_vector_store
        return get_vector_store
    elif name == "SessionManager":
        from .storage.session_manager import SessionManager
        return SessionManager
    elif name == "get_session_manager":
        from .storage.session_manager import get_session_manager
        return get_session_manager
    elif name == "FileProcessor":
        from .storage.file_processor import FileProcessor
        return FileProcessor
    elif name == "get_file_processor":
        from .storage.file_processor import get_file_processor
        return get_file_processor
    elif name == "GoogleDriveService":
        from .integration.gdrive import GoogleDriveService
        return GoogleDriveService
    elif name == "get_gdrive_watcher":
        from .integration.gdrive import get_gdrive_watcher
        return get_gdrive_watcher
    elif name == "N8nClient":
        from .integration.n8n import N8nClient
        return N8nClient
    elif name == "EmbeddingService":
        from .integration.embedding import EmbeddingService
        return EmbeddingService
    elif name == "get_embedding_service":
        from .integration.embedding import get_embedding_service
        return get_embedding_service
    elif name == "BackgroundService":
        from .background.service import BackgroundService
        return BackgroundService
    elif name == "get_background_service":
        from .background.service import get_background_service
        return get_background_service
    elif name == "BackgroundTasks":
        from .background.tasks import BackgroundTasks
        return BackgroundTasks
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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

