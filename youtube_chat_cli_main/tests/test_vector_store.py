"""
Unit tests for the Vector Store Service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from youtube_chat_cli_main.services.vector_store import (
    QdrantVectorStore,
    ChromaVectorStore,
    VectorStore
)


class TestQdrantVectorStore:
    """Test suite for QdrantVectorStore."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.qdrant_url = "http://localhost:6333"
        config.qdrant_collection_name = "test_collection"
        config.embedding_dimension = 768
        return config
    
    @pytest.fixture
    def mock_qdrant_client(self):
        """Mock Qdrant client."""
        with patch('youtube_chat_cli_main.services.vector_store.QdrantClient') as mock:
            client = Mock()
            mock.return_value = client
            yield client
    
    def test_initialization(self, mock_config, mock_qdrant_client):
        """Test Qdrant vector store initialization."""
        store = QdrantVectorStore(mock_config)
        
        assert store.url == "http://localhost:6333"
        assert store.collection_name == "test_collection"
        assert store.dimension == 768
    
    def test_add_documents(self, mock_config, mock_qdrant_client):
        """Test adding documents to Qdrant."""
        store = QdrantVectorStore(mock_config)
        
        documents = [
            {"content": "Test document 1", "metadata": {"source": "test"}},
            {"content": "Test document 2", "metadata": {"source": "test"}}
        ]
        
        embeddings = [
            np.random.rand(768).tolist(),
            np.random.rand(768).tolist()
        ]
        
        doc_ids = store.add_documents(documents, embeddings)
        
        assert len(doc_ids) == 2
        mock_qdrant_client.upsert.assert_called_once()
    
    def test_search(self, mock_config, mock_qdrant_client):
        """Test searching in Qdrant."""
        mock_qdrant_client.search.return_value = [
            Mock(
                id="doc1",
                score=0.9,
                payload={
                    "content": "Test document",
                    "metadata": {"source": "test"}
                }
            )
        ]
        
        store = QdrantVectorStore(mock_config)
        
        query_embedding = np.random.rand(768).tolist()
        results = store.search(query_embedding, top_k=5)
        
        assert len(results) == 1
        assert results[0]["id"] == "doc1"
        assert results[0]["score"] == 0.9
        assert results[0]["content"] == "Test document"
        mock_qdrant_client.search.assert_called_once()
    
    def test_delete_documents(self, mock_config, mock_qdrant_client):
        """Test deleting documents from Qdrant."""
        store = QdrantVectorStore(mock_config)
        
        filter_criteria = {"source": "test"}
        count = store.delete_documents(filter_criteria)
        
        mock_qdrant_client.delete.assert_called_once()
    
    def test_get_collection_info(self, mock_config, mock_qdrant_client):
        """Test getting collection info."""
        mock_qdrant_client.get_collection.return_value = Mock(
            points_count=100,
            vectors_count=100
        )
        
        store = QdrantVectorStore(mock_config)
        info = store.get_collection_info()
        
        assert info["name"] == "test_collection"
        assert "points_count" in info or "vectors_count" in info


class TestChromaVectorStore:
    """Test suite for ChromaVectorStore."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.chroma_persist_directory = "./chroma_db"
        config.chroma_collection_name = "test_collection"
        return config
    
    @pytest.fixture
    def mock_chroma_client(self):
        """Mock Chroma client."""
        with patch('youtube_chat_cli_main.services.vector_store.chromadb.PersistentClient') as mock:
            client = Mock()
            collection = Mock()
            client.get_or_create_collection.return_value = collection
            mock.return_value = client
            yield client, collection
    
    def test_initialization(self, mock_config, mock_chroma_client):
        """Test Chroma vector store initialization."""
        client, collection = mock_chroma_client
        
        store = ChromaVectorStore(mock_config)
        
        assert store.persist_directory == "./chroma_db"
        assert store.collection_name == "test_collection"
        client.get_or_create_collection.assert_called_once()
    
    def test_add_documents(self, mock_config, mock_chroma_client):
        """Test adding documents to Chroma."""
        client, collection = mock_chroma_client
        
        store = ChromaVectorStore(mock_config)
        
        documents = [
            {"content": "Test document 1", "metadata": {"source": "test"}},
            {"content": "Test document 2", "metadata": {"source": "test"}}
        ]
        
        embeddings = [
            np.random.rand(768).tolist(),
            np.random.rand(768).tolist()
        ]
        
        doc_ids = store.add_documents(documents, embeddings)
        
        assert len(doc_ids) == 2
        collection.add.assert_called_once()
    
    def test_search(self, mock_config, mock_chroma_client):
        """Test searching in Chroma."""
        client, collection = mock_chroma_client
        
        collection.query.return_value = {
            "ids": [["doc1"]],
            "distances": [[0.1]],
            "documents": [["Test document"]],
            "metadatas": [[{"source": "test"}]]
        }
        
        store = ChromaVectorStore(mock_config)
        
        query_embedding = np.random.rand(768).tolist()
        results = store.search(query_embedding, top_k=5)
        
        assert len(results) == 1
        assert results[0]["id"] == "doc1"
        assert results[0]["content"] == "Test document"
        collection.query.assert_called_once()
    
    def test_delete_documents(self, mock_config, mock_chroma_client):
        """Test deleting documents from Chroma."""
        client, collection = mock_chroma_client
        
        store = ChromaVectorStore(mock_config)
        
        filter_criteria = {"source": "test"}
        count = store.delete_documents(filter_criteria)
        
        collection.delete.assert_called_once()
    
    def test_get_collection_info(self, mock_config, mock_chroma_client):
        """Test getting collection info."""
        client, collection = mock_chroma_client
        
        collection.count.return_value = 100
        
        store = ChromaVectorStore(mock_config)
        info = store.get_collection_info()
        
        assert info["name"] == "test_collection"
        assert info["vectors_count"] == 100


class TestVectorStore:
    """Test suite for unified VectorStore."""
    
    @pytest.fixture
    def mock_config_qdrant(self):
        """Mock configuration for Qdrant."""
        config = Mock()
        config.vector_store_type = "qdrant"
        config.qdrant_url = "http://localhost:6333"
        config.qdrant_collection_name = "test_collection"
        config.embedding_dimension = 768
        return config
    
    @pytest.fixture
    def mock_config_chroma(self):
        """Mock configuration for Chroma."""
        config = Mock()
        config.vector_store_type = "chroma"
        config.chroma_persist_directory = "./chroma_db"
        config.chroma_collection_name = "test_collection"
        return config
    
    @pytest.fixture
    def mock_embedding_service(self):
        """Mock embedding service."""
        service = Mock()
        service.embed_documents.return_value = [
            np.random.rand(768).tolist(),
            np.random.rand(768).tolist()
        ]
        service.embed_query.return_value = np.random.rand(768).tolist()
        return service
    
    def test_initialization_qdrant(self, mock_config_qdrant, mock_embedding_service):
        """Test VectorStore initialization with Qdrant."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config', return_value=mock_config_qdrant), \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service', return_value=mock_embedding_service), \
             patch('youtube_chat_cli_main.services.vector_store.QdrantClient'):
            
            store = VectorStore()
            
            assert isinstance(store.backend, QdrantVectorStore)
    
    def test_initialization_chroma(self, mock_config_chroma, mock_embedding_service):
        """Test VectorStore initialization with Chroma."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config', return_value=mock_config_chroma), \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service', return_value=mock_embedding_service), \
             patch('youtube_chat_cli_main.services.vector_store.chromadb.PersistentClient'):
            
            store = VectorStore()
            
            assert isinstance(store.backend, ChromaVectorStore)
    
    def test_add_documents_with_auto_embedding(self, mock_config_qdrant, mock_embedding_service):
        """Test adding documents with automatic embedding generation."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config', return_value=mock_config_qdrant), \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service', return_value=mock_embedding_service), \
             patch('youtube_chat_cli_main.services.vector_store.QdrantClient'):
            
            store = VectorStore()
            store.backend = Mock()
            store.backend.add_documents.return_value = ["doc1", "doc2"]
            
            documents = [
                {"content": "Test document 1"},
                {"content": "Test document 2"}
            ]
            
            doc_ids = store.add_documents(documents)
            
            assert len(doc_ids) == 2
            mock_embedding_service.embed_documents.assert_called_once()
            store.backend.add_documents.assert_called_once()
    
    def test_search_with_auto_embedding(self, mock_config_qdrant, mock_embedding_service):
        """Test searching with automatic query embedding."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config', return_value=mock_config_qdrant), \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service', return_value=mock_embedding_service), \
             patch('youtube_chat_cli_main.services.vector_store.QdrantClient'):
            
            store = VectorStore()
            store.backend = Mock()
            store.backend.search.return_value = [
                {"id": "doc1", "content": "Test", "score": 0.9}
            ]
            
            results = store.search("test query", top_k=5)
            
            assert len(results) == 1
            mock_embedding_service.embed_query.assert_called_once_with("test query")
            store.backend.search.assert_called_once()
    
    def test_delete_documents_delegates_to_backend(self, mock_config_qdrant, mock_embedding_service):
        """Test that delete_documents delegates to backend."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config', return_value=mock_config_qdrant), \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service', return_value=mock_embedding_service), \
             patch('youtube_chat_cli_main.services.vector_store.QdrantClient'):
            
            store = VectorStore()
            store.backend = Mock()
            store.backend.delete_documents.return_value = 5
            
            count = store.delete_documents({"source": "test"})
            
            assert count == 5
            store.backend.delete_documents.assert_called_once()
    
    def test_get_collection_info_delegates_to_backend(self, mock_config_qdrant, mock_embedding_service):
        """Test that get_collection_info delegates to backend."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config', return_value=mock_config_qdrant), \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service', return_value=mock_embedding_service), \
             patch('youtube_chat_cli_main.services.vector_store.QdrantClient'):
            
            store = VectorStore()
            store.backend = Mock()
            store.backend.get_collection_info.return_value = {
                "name": "test",
                "vectors_count": 100
            }
            
            info = store.get_collection_info()
            
            assert info["name"] == "test"
            assert info["vectors_count"] == 100
            store.backend.get_collection_info.assert_called_once()

