"""
JAEGIS NexusSync - Vector Store Service

This module provides a pluggable vector store interface supporting:
- Qdrant (local Docker instance)
- ChromaDB (local file-based storage)

Both options are completely free and run locally.
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# ChromaDB
import chromadb
from chromadb.config import Settings

from ..core.config import get_config
from ..core.database import get_database

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    """Raised when vector store operations fail."""
    pass


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int) -> None:
        """Create a new collection."""
        pass
    
    @abstractmethod
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add documents with embeddings to the collection."""
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents by ID."""
        pass
    
    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        pass


class QdrantVectorStore(BaseVectorStore):
    """
    Qdrant vector store implementation.
    
    Uses local Qdrant instance running in Docker (completely free).
    """
    
    def __init__(self, config):
        """Initialize Qdrant client."""
        self.config = config
        self.collection_name = config.qdrant_collection_name
        
        try:
            # Connect to local Qdrant instance
            self.client = QdrantClient(
                url=config.qdrant_url,
                api_key=config.qdrant_api_key if config.qdrant_api_key else None
            )
            logger.info(f"✅ Connected to Qdrant at {config.qdrant_url}")
        except Exception as e:
            raise VectorStoreError(f"Failed to connect to Qdrant: {e}")
    
    def create_collection(self, collection_name: str, vector_size: int) -> None:
        """Create a new Qdrant collection."""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created Qdrant collection: {collection_name}")
            else:
                logger.info(f"Collection {collection_name} already exists")
                
        except Exception as e:
            raise VectorStoreError(f"Failed to create collection: {e}")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add documents to Qdrant."""
        try:
            points = []
            doc_ids = []
            
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                # Generate unique ID
                doc_id = f"{metadata.get('file_id', 'unknown')}_{i}"
                doc_ids.append(doc_id)
                
                # Combine document metadata with global metadata
                point_metadata = {
                    **(metadata or {}),
                    **doc.get('metadata', {}),
                    'content': doc['content']
                }
                
                # Create point
                point = PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload=point_metadata
                )
                points.append(point)
            
            # Upload points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Added {len(points)} documents to Qdrant")
            return doc_ids
            
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents: {e}")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search Qdrant for similar documents."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'content': result.payload.get('content', ''),
                    'metadata': {k: v for k, v in result.payload.items() if k != 'content'}
                })
            
            return formatted_results
            
        except Exception as e:
            raise VectorStoreError(f"Search failed: {e}")
    
    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from Qdrant."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=document_ids
            )
            logger.info(f"Deleted {len(document_ids)} documents from Qdrant")
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get Qdrant collection information."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            raise VectorStoreError(f"Failed to get collection info: {e}")


class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB vector store implementation.
    
    Uses local file-based storage (completely free, no server needed).
    """
    
    def __init__(self, config):
        """Initialize ChromaDB client."""
        self.config = config
        self.collection_name = config.chroma_collection_name
        
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=config.chroma_persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"✅ Connected to ChromaDB at {config.chroma_persist_directory}")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize ChromaDB: {e}")
    
    def create_collection(self, collection_name: str, vector_size: int) -> None:
        """Create a new ChromaDB collection."""
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✅ Created ChromaDB collection: {collection_name}")
        except Exception as e:
            raise VectorStoreError(f"Failed to create collection: {e}")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add documents to ChromaDB."""
        try:
            doc_ids = []
            doc_contents = []
            doc_embeddings = []
            doc_metadatas = []
            
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                # Generate unique ID
                doc_id = f"{metadata.get('file_id', 'unknown')}_{i}"
                doc_ids.append(doc_id)
                
                # Extract content
                doc_contents.append(doc['content'])
                doc_embeddings.append(embedding)
                
                # Combine metadata (ChromaDB requires all values to be strings, ints, or floats)
                point_metadata = {
                    **(metadata or {}),
                    **doc.get('metadata', {})
                }
                
                # Convert all metadata values to strings for ChromaDB compatibility
                point_metadata = {k: str(v) for k, v in point_metadata.items()}
                doc_metadatas.append(point_metadata)
            
            # Add to collection
            self.collection.add(
                ids=doc_ids,
                embeddings=doc_embeddings,
                documents=doc_contents,
                metadatas=doc_metadatas
            )
            
            logger.info(f"✅ Added {len(doc_ids)} documents to ChromaDB")
            return doc_ids
            
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents: {e}")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search ChromaDB for similar documents."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_dict
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })
            
            return formatted_results
            
        except Exception as e:
            raise VectorStoreError(f"Search failed: {e}")
    
    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from ChromaDB."""
        try:
            self.collection.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get ChromaDB collection information."""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'points_count': count,
                'vectors_count': count
            }
        except Exception as e:
            raise VectorStoreError(f"Failed to get collection info: {e}")

