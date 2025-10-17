"""
Integration tests for JAEGIS NexusSync RAG system.

These tests verify end-to-end workflows and integration between components.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import os

from youtube_chat_cli_main.core.database import Database
from youtube_chat_cli_main.services.content_processor import ContentProcessor
from youtube_chat_cli_main.services.vector_store import VectorStore
from youtube_chat_cli_main.services.rag_engine import AdaptiveRAGEngine


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def test_document(self, temp_dir):
        """Create a test document."""
        doc_path = Path(temp_dir) / "test_document.txt"
        doc_path.write_text("""
# Test Document

This is a test document for integration testing.

## Section 1

Content for section 1 with important information.

## Section 2

Content for section 2 with more details.
""")
        return str(doc_path)
    
    @pytest.mark.integration
    def test_document_ingestion_workflow(self, test_document):
        """Test complete document ingestion workflow."""
        # Mock all dependencies
        with patch('youtube_chat_cli_main.services.content_processor.get_config') as mock_config, \
             patch('youtube_chat_cli_main.services.content_processor.get_database') as mock_db, \
             patch('youtube_chat_cli_main.services.content_processor.get_vector_store') as mock_vs:
            
            # Setup mocks
            mock_config.return_value.chunk_size = 1000
            mock_config.return_value.chunk_overlap = 200
            mock_config.return_value.ocr_provider = "tesseract"
            
            mock_db.return_value.get_queue_item.return_value = {
                "id": 1,
                "file_id": test_document,
                "file_name": "test_document.txt",
                "source": "local",
                "status": "pending"
            }
            
            mock_vs.return_value.add_documents.return_value = ["doc1", "doc2"]
            
            # Create processor
            processor = ContentProcessor()
            
            # Process the document
            success = processor.process_queue_item(1)
            
            # Verify processing
            assert success is True
            mock_db.return_value.update_queue_status.assert_called_with(1, "completed")
            mock_vs.return_value.add_documents.assert_called_once()
    
    @pytest.mark.integration
    def test_rag_query_workflow(self):
        """Test complete RAG query workflow."""
        # Mock all external dependencies
        with patch('youtube_chat_cli_main.services.rag_engine.get_config') as mock_config, \
             patch('youtube_chat_cli_main.services.rag_engine.get_llm_service') as mock_llm, \
             patch('youtube_chat_cli_main.services.rag_engine.get_vector_store') as mock_vs, \
             patch('youtube_chat_cli_main.services.rag_engine.get_web_search_service') as mock_ws:
            
            # Setup config
            mock_config.return_value.rag_top_k = 5
            mock_config.return_value.rag_min_relevance_score = 0.7
            mock_config.return_value.rag_max_transform_attempts = 3
            mock_config.return_value.rag_hallucination_check = True
            mock_config.return_value.rag_answer_check = True
            
            # Setup vector store mock
            mock_vs.return_value.search.return_value = [
                {
                    'content': 'Test document content about AI',
                    'metadata': {'file_name': 'test.txt'},
                    'score': 0.9
                }
            ]
            
            # Setup LLM mock
            mock_llm.return_value.generate.side_effect = [
                "yes",  # Document grading
                "This is an answer about AI based on the test document.",  # Generation
                "yes",  # Hallucination check
                "yes"   # Answer quality check
            ]
            
            # Create RAG engine
            rag = AdaptiveRAGEngine()
            
            # Query
            result = rag.query("What is this about?")
            
            # Verify result
            assert "answer" in result
            assert "AI" in result["answer"]
            assert result["web_search_used"] is False
            assert len(result["documents"]) > 0


class TestServiceIntegration:
    """Test integration between services."""
    
    @pytest.mark.integration
    def test_vector_store_and_embeddings_integration(self):
        """Test vector store and embedding service integration."""
        with patch('youtube_chat_cli_main.services.vector_store.get_config') as mock_config, \
             patch('youtube_chat_cli_main.services.vector_store.get_embedding_service') as mock_emb, \
             patch('youtube_chat_cli_main.services.vector_store.QdrantClient'):
            
            # Setup config
            mock_config.return_value.vector_store_type = "qdrant"
            mock_config.return_value.qdrant_url = "http://localhost:6333"
            mock_config.return_value.qdrant_collection_name = "test"
            mock_config.return_value.embedding_dimension = 768
            
            # Setup mock embeddings
            mock_emb.return_value.embed_documents.return_value = [
                [0.1] * 768,
                [0.2] * 768
            ]
            mock_emb.return_value.embed_query.return_value = [0.15] * 768
            
            vs = VectorStore()
            
            # Add documents
            documents = [
                {"content": "Test doc 1"},
                {"content": "Test doc 2"}
            ]
            
            with patch.object(vs.backend, 'add_documents', return_value=["id1", "id2"]):
                doc_ids = vs.add_documents(documents)
            
            assert len(doc_ids) == 2
            mock_emb.return_value.embed_documents.assert_called_once()
            
            # Search
            with patch.object(vs.backend, 'search', return_value=[
                {"id": "id1", "content": "Test doc 1", "score": 0.9}
            ]):
                results = vs.search("test query")
            
            assert len(results) == 1
            mock_emb.return_value.embed_query.assert_called_once()
    
    @pytest.mark.integration
    def test_content_processor_and_vector_store_integration(self):
        """Test content processor and vector store integration."""
        with patch('youtube_chat_cli_main.services.content_processor.get_config') as mock_config, \
             patch('youtube_chat_cli_main.services.content_processor.get_vector_store') as mock_vs, \
             patch('youtube_chat_cli_main.services.content_processor.get_database') as mock_db:
            
            # Setup config
            mock_config.return_value.chunk_size = 1000
            mock_config.return_value.chunk_overlap = 200
            mock_config.return_value.ocr_provider = "tesseract"
            
            # Setup mocks
            mock_vs.return_value.add_documents.return_value = ["doc1", "doc2"]
            mock_db.return_value.get_queue_item.return_value = {
                "id": 1,
                "file_id": "test.txt",
                "file_name": "test.txt",
                "source": "local",
                "status": "pending"
            }
            
            processor = ContentProcessor()
            
            # Process a document
            with patch.object(processor, '_process_file', return_value="Test content"), \
                 patch.object(processor, '_split_by_markdown_headings', return_value=[
                     {"content": "Chunk 1", "metadata": {}},
                     {"content": "Chunk 2", "metadata": {}}
                 ]):
                
                success = processor.process_queue_item(1)
            
            assert success is True
            mock_vs.return_value.add_documents.assert_called_once()
            mock_db.return_value.update_queue_status.assert_called_with(1, "completed")


class TestDatabaseIntegration:
    """Test database operations."""
    
    @pytest.fixture
    def test_db(self):
        """Create test database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create database with test path
        with patch('youtube_chat_cli_main.core.database.get_config') as mock_config:
            mock_config.return_value.database_path = db_path
            db = Database()
            yield db
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_queue_operations(self, test_db):
        """Test queue CRUD operations."""
        # Add to queue
        queue_id = test_db.add_to_queue(
            file_id="test.pdf",
            file_name="test.pdf",
            source="local",
            priority=1
        )
        
        assert queue_id is not None
        
        # Get queue item
        item = test_db.get_queue_item(queue_id)
        assert item is not None
        assert item["file_name"] == "test.pdf"
        assert item["status"] == "pending"
        
        # Update status
        test_db.update_queue_status(queue_id, "processing")
        item = test_db.get_queue_item(queue_id)
        assert item["status"] == "processing"
        
        # Get pending items
        pending = test_db.get_pending_queue_items(limit=10)
        assert len(pending) == 0  # Item is processing, not pending
        
        # Complete processing
        test_db.update_queue_status(queue_id, "completed")
        item = test_db.get_queue_item(queue_id)
        assert item["status"] == "completed"
    
    def test_queue_statistics(self, test_db):
        """Test queue statistics."""
        # Add multiple items
        test_db.add_to_queue("file1.pdf", "file1.pdf", "local", 0)
        test_db.add_to_queue("file2.pdf", "file2.pdf", "local", 0)
        test_db.add_to_queue("file3.pdf", "file3.pdf", "local", 0)
        
        # Get statistics
        stats = test_db.get_queue_statistics()
        
        assert stats["total"] == 3
        assert stats["by_status"]["pending"] == 3
    
    def test_retry_logic(self, test_db):
        """Test queue retry logic."""
        # Add item
        queue_id = test_db.add_to_queue("test.pdf", "test.pdf", "local", 0)
        
        # Increment retry count
        test_db.increment_queue_retry(queue_id)
        item = test_db.get_queue_item(queue_id)
        assert item["retry_count"] == 1
        
        # Increment again
        test_db.increment_queue_retry(queue_id)
        item = test_db.get_queue_item(queue_id)
        assert item["retry_count"] == 2


class TestMCPServerIntegration:
    """Test MCP server integration."""
    
    @pytest.mark.integration
    def test_mcp_tool_execution(self):
        """Test MCP tool execution."""
        from youtube_chat_cli_main.mcp.server import MCPTools
        
        # Test system_info tool
        with patch('youtube_chat_cli_main.mcp.server.get_config') as mock_config, \
             patch('youtube_chat_cli_main.mcp.server.get_database') as mock_db, \
             patch('youtube_chat_cli_main.mcp.server.get_vector_store') as mock_vs:
            
            # Setup mocks
            mock_config.return_value.llm_model = "llama3.1:8b"
            mock_config.return_value.embedding_provider = "ollama"
            mock_config.return_value.vector_store_type = "qdrant"
            mock_config.return_value.ocr_provider = "tesseract"
            mock_config.return_value.rag_top_k = 5
            mock_config.return_value.rag_min_relevance_score = 0.7
            mock_config.return_value.rag_max_transform_attempts = 3
            mock_config.return_value.rag_hallucination_check = True
            mock_config.return_value.rag_answer_check = True
            
            mock_db.return_value.get_queue_statistics.return_value = {
                "total": 10,
                "by_status": {"pending": 5, "completed": 5}
            }
            
            mock_vs.return_value.get_collection_info.return_value = {
                "name": "test",
                "vectors_count": 100
            }
            
            # Execute tool
            result = MCPTools.execute_tool("system_info", {})
            
            # Verify result
            assert "configuration" in result
            assert "database" in result
            assert "vector_store" in result
            assert result["configuration"]["llm_model"] == "llama3.1:8b"

