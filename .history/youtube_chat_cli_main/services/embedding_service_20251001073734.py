"""
JAEGIS NexusSync - Embedding Service

This module provides pluggable embedding generation supporting:
- Ollama (local, free, unlimited)
- OpenAI (costs money, not recommended for free tier)

Default: Ollama with nomic-embed-text model (completely free).
"""

import logging
from typing import List, Optional
from abc import ABC, abstractmethod

# Ollama
import requests

# OpenAI (optional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""
    pass


class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services."""
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        pass


class OllamaEmbeddingService(BaseEmbeddingService):
    """
    Ollama embedding service (FREE, local).
    
    Uses local Ollama instance running in Docker.
    Model: nomic-embed-text (768 dimensions, 274MB)
    """
    
    def __init__(self, config):
        """Initialize Ollama embedding service."""
        self.config = config
        self.base_url = config.ollama_base_url
        self.model = config.ollama_embedding_model
        
        # Verify Ollama is accessible
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Connected to Ollama at {self.base_url}")
        except Exception as e:
            raise EmbeddingError(
                f"Failed to connect to Ollama at {self.base_url}: {e}\n"
                f"Make sure Ollama is running: docker ps | grep ollama"
            )
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query using Ollama."""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get('embedding')
            
            if not embedding:
                raise EmbeddingError("No embedding returned from Ollama")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents using Ollama."""
        embeddings = []
        
        for i, text in enumerate(texts):
            if i % 10 == 0:
                logger.debug(f"Generating embedding {i+1}/{len(texts)}...")
            
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings using Ollama")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension for nomic-embed-text."""
        # nomic-embed-text produces 768-dimensional embeddings
        return 768


class OpenAIEmbeddingService(BaseEmbeddingService):
    """
    OpenAI embedding service (COSTS MONEY - not recommended for free tier).
    
    Only use this if you have an OpenAI API key and are willing to pay.
    """
    
    def __init__(self, config):
        """Initialize OpenAI embedding service."""
        if not OPENAI_AVAILABLE:
            raise EmbeddingError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        self.config = config
        self.model = config.openai_embedding_model
        
        if not config.openai_api_key:
            raise EmbeddingError("OpenAI API key not configured")
        
        try:
            self.client = OpenAI(api_key=config.openai_api_key)
            logger.info("✅ OpenAI embedding service initialized")
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize OpenAI client: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents using OpenAI."""
        try:
            # OpenAI supports batch embedding
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings using OpenAI")
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI batch embedding failed: {e}")
            raise EmbeddingError(f"Failed to generate embeddings: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension for OpenAI model."""
        # text-embedding-3-small produces 1536-dimensional embeddings
        # text-embedding-ada-002 produces 1536-dimensional embeddings
        return 1536


class EmbeddingService:
    """
    Unified embedding service with automatic backend selection.
    
    Automatically selects the appropriate embedding backend based on configuration.
    """
    
    def __init__(self):
        """Initialize embedding service with configured backend."""
        self.config = get_config()
        
        # Initialize the appropriate embedding backend
        if self.config.embedding_provider == 'ollama':
            self.backend = OllamaEmbeddingService(self.config)
            logger.info("Using Ollama embedding service (FREE)")
        elif self.config.embedding_provider == 'openai':
            self.backend = OpenAIEmbeddingService(self.config)
            logger.warning("Using OpenAI embedding service (COSTS MONEY)")
        else:
            raise EmbeddingError(
                f"Unsupported embedding provider: {self.config.embedding_provider}"
            )
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text
        
        Returns:
            Embedding vector
        """
        return self.backend.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of document texts
        
        Returns:
            List of embedding vectors
        """
        return self.backend.embed_documents(texts)
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        return self.backend.get_embedding_dimension()


# Global service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the global embedding service instance.
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
        logger.info("Embedding service instance created")
    
    return _embedding_service

