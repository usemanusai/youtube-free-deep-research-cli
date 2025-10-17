"""
Unit tests for the Adaptive RAG Engine.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

from youtube_chat_cli_main.services.rag_engine import AdaptiveRAGEngine, GraphState


class TestAdaptiveRAGEngine:
    """Test suite for AdaptiveRAGEngine."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.rag_top_k = 5
        config.rag_min_relevance_score = 0.7
        config.rag_max_transform_attempts = 3
        config.rag_hallucination_check = True
        config.rag_answer_check = True
        return config
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM service."""
        llm = Mock()
        llm.generate = Mock(return_value="This is a test answer.")
        return llm
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        vs = Mock()
        vs.search = Mock(return_value=[
            {
                'content': 'Test document content',
                'metadata': {'file_name': 'test.pdf'},
                'score': 0.9
            }
        ])
        return vs
    
    @pytest.fixture
    def mock_web_search(self):
        """Mock web search service."""
        ws = Mock()
        ws.search = Mock(return_value=[
            {
                'title': 'Test Result',
                'url': 'https://example.com',
                'content': 'Test web content',
                'score': 0.8
            }
        ])
        return ws
    
    @pytest.fixture
    def rag_engine(self, mock_config, mock_llm, mock_vector_store, mock_web_search):
        """Create RAG engine with mocked dependencies."""
        with patch('youtube_chat_cli_main.services.rag_engine.get_config', return_value=mock_config), \
             patch('youtube_chat_cli_main.services.rag_engine.get_llm_service', return_value=mock_llm), \
             patch('youtube_chat_cli_main.services.rag_engine.get_vector_store', return_value=mock_vector_store), \
             patch('youtube_chat_cli_main.services.rag_engine.get_web_search_service', return_value=mock_web_search):
            engine = AdaptiveRAGEngine()
            return engine
    
    def test_initialization(self, rag_engine):
        """Test RAG engine initialization."""
        assert rag_engine is not None
        assert rag_engine.graph is not None
        assert rag_engine.llm is not None
        assert rag_engine.vector_store is not None
        assert rag_engine.web_search is not None
    
    def test_retrieve_node(self, rag_engine, mock_vector_store):
        """Test the retrieve node."""
        state = {
            "question": "What is the test about?",
            "documents": [],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        result = rag_engine._retrieve(state)
        
        assert "documents" in result
        assert len(result["documents"]) > 0
        assert isinstance(result["documents"][0], Document)
        mock_vector_store.search.assert_called_once()
    
    def test_grade_documents_relevant(self, rag_engine, mock_llm):
        """Test document grading with relevant documents."""
        mock_llm.generate.return_value = "yes"
        
        state = {
            "question": "What is the test about?",
            "documents": [
                Document(page_content="Test content", metadata={})
            ],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        result = rag_engine._grade_documents(state)
        
        assert len(result["documents"]) == 1
        assert result["web_search"] == "No"
    
    def test_grade_documents_irrelevant(self, rag_engine, mock_llm):
        """Test document grading with irrelevant documents."""
        mock_llm.generate.return_value = "no"
        
        state = {
            "question": "What is the test about?",
            "documents": [
                Document(page_content="Irrelevant content", metadata={})
            ],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        result = rag_engine._grade_documents(state)
        
        assert len(result["documents"]) == 0
        assert result["web_search"] == "Yes"
    
    def test_transform_query(self, rag_engine, mock_llm):
        """Test query transformation."""
        mock_llm.generate.return_value = "What is the improved test question?"
        
        state = {
            "question": "What is the test about?",
            "documents": [],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        result = rag_engine._transform_query(state)
        
        assert result["question"] != state["question"]
        assert result["transform_count"] == 1
        mock_llm.generate.assert_called_once()
    
    def test_decide_to_generate_with_documents(self, rag_engine):
        """Test decision to generate with good documents."""
        state = {
            "question": "What is the test about?",
            "documents": [Document(page_content="Test", metadata={})],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        decision = rag_engine._decide_to_generate(state)
        
        assert decision == "generate"
    
    def test_decide_to_generate_web_search(self, rag_engine):
        """Test decision to use web search."""
        state = {
            "question": "What is the test about?",
            "documents": [],
            "generation": "",
            "web_search": "Yes",
            "transform_count": 0
        }
        
        decision = rag_engine._decide_to_generate(state)
        
        assert decision == "web_search"
    
    def test_decide_to_generate_transform(self, rag_engine):
        """Test decision to transform query."""
        state = {
            "question": "What is the test about?",
            "documents": [],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        decision = rag_engine._decide_to_generate(state)
        
        assert decision == "transform_query"
    
    def test_decide_to_generate_max_transforms(self, rag_engine):
        """Test decision when max transforms reached."""
        state = {
            "question": "What is the test about?",
            "documents": [],
            "generation": "",
            "web_search": "No",
            "transform_count": 3
        }
        
        decision = rag_engine._decide_to_generate(state)
        
        assert decision == "generate"
    
    def test_web_search_node(self, rag_engine, mock_web_search):
        """Test web search node."""
        state = {
            "question": "What is the test about?",
            "documents": [],
            "generation": "",
            "web_search": "Yes",
            "transform_count": 0
        }
        
        result = rag_engine._web_search(state)
        
        assert "documents" in result
        assert len(result["documents"]) > 0
        assert result["documents"][0].metadata.get("source") == "web_search"
        mock_web_search.search.assert_called_once()
    
    def test_generate_node(self, rag_engine, mock_llm):
        """Test answer generation node."""
        mock_llm.generate.return_value = "This is the answer."
        
        state = {
            "question": "What is the test about?",
            "documents": [Document(page_content="Test content", metadata={})],
            "generation": "",
            "web_search": "No",
            "transform_count": 0
        }
        
        result = rag_engine._generate(state)
        
        assert result["generation"] == "This is the answer."
        mock_llm.generate.assert_called_once()
    
    def test_check_hallucination_grounded(self, rag_engine, mock_llm):
        """Test hallucination check with grounded answer."""
        mock_llm.generate.return_value = "yes"
        
        documents = [Document(page_content="Test content", metadata={})]
        generation = "This is based on test content."
        
        is_grounded = rag_engine._check_hallucination(documents, generation)
        
        assert is_grounded is True
    
    def test_check_hallucination_not_grounded(self, rag_engine, mock_llm):
        """Test hallucination check with hallucinated answer."""
        mock_llm.generate.return_value = "no"
        
        documents = [Document(page_content="Test content", metadata={})]
        generation = "This is completely made up."
        
        is_grounded = rag_engine._check_hallucination(documents, generation)
        
        assert is_grounded is False
    
    def test_check_answer_quality_useful(self, rag_engine, mock_llm):
        """Test answer quality check with useful answer."""
        mock_llm.generate.return_value = "yes"
        
        question = "What is the test about?"
        generation = "The test is about checking functionality."
        
        is_useful = rag_engine._check_answer_quality(question, generation)
        
        assert is_useful is True
    
    def test_check_answer_quality_not_useful(self, rag_engine, mock_llm):
        """Test answer quality check with non-useful answer."""
        mock_llm.generate.return_value = "no"
        
        question = "What is the test about?"
        generation = "I don't know."
        
        is_useful = rag_engine._check_answer_quality(question, generation)
        
        assert is_useful is False
    
    def test_query_end_to_end(self, rag_engine, mock_llm, mock_vector_store):
        """Test complete query flow."""
        # Mock LLM responses for different stages
        mock_llm.generate.side_effect = [
            "yes",  # Document grading
            "This is the final answer.",  # Generation
            "yes",  # Hallucination check
            "yes"   # Answer quality check
        ]
        
        result = rag_engine.query("What is the test about?")
        
        assert "answer" in result
        assert "documents" in result
        assert "web_search_used" in result
        assert "transform_count" in result
        assert result["answer"] == "This is the final answer."

