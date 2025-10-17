"""
JAEGIS NexusSync - Adaptive RAG Engine

This module implements the Adaptive RAG (Retrieval-Augmented Generation) engine
using LangGraph for state management and conditional routing.

Key Features:
- Intelligent query routing (vector store vs web search)
- Document relevance grading
- Query transformation and rewriting
- Hallucination detection
- Answer quality grading
- Self-correcting loops

Based on the LangGraph Adaptive RAG tutorial with enhancements.
"""

import logging
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from typing_extensions import TypedDict
import operator

from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from ..core.config import get_config
from .llm_service import get_llm_service
from .vector_store import get_vector_store
from .web_search_service import get_web_search_service

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """
    State of the RAG graph.
    
    Attributes:
        question: User question
        generation: LLM generation
        web_search: Whether to perform web search
        documents: Retrieved documents
        transform_count: Number of query transformations
    """
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    transform_count: int


class AdaptiveRAGEngine:
    """
    Adaptive RAG engine with self-correction and quality control.
    
    This engine implements a sophisticated RAG pipeline with:
    1. Query routing - Decide between vector store and web search
    2. Document retrieval - Get relevant documents
    3. Relevance grading - Filter irrelevant documents
    4. Query transformation - Rewrite query if needed
    5. Answer generation - Generate response with LLM
    6. Hallucination checking - Verify answer is grounded
    7. Answer grading - Verify answer quality
    """
    
    def __init__(self):
        """Initialize Adaptive RAG engine."""
        self.config = get_config()
        self.llm = get_llm_service()
        self.vector_store = get_vector_store()
        self.web_search = get_web_search_service()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("✅ Adaptive RAG engine initialized")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for Adaptive RAG.
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("transform_query", self._transform_query)
        workflow.add_node("generate", self._generate)
        workflow.add_node("web_search", self._web_search)
        
        # Set entry point
        workflow.set_entry_point("retrieve")
        
        # Add edges
        workflow.add_edge("retrieve", "grade_documents")
        
        # Conditional edge: grade_documents -> transform_query or generate
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
                "web_search": "web_search"
            }
        )
        
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_edge("web_search", "generate")
        
        # Conditional edge: generate -> END or transform_query
        workflow.add_conditional_edges(
            "generate",
            self._grade_generation,
            {
                "useful": END,
                "not useful": "transform_query",
                "not supported": "generate"
            }
        )
        
        # Compile the graph
        return workflow.compile()
    
    def _retrieve(self, state: GraphState) -> GraphState:
        """
        Retrieve documents from vector store.
        
        Args:
            state: Current graph state
        
        Returns:
            Updated state with retrieved documents
        """
        logger.info("---RETRIEVE---")
        question = state["question"]
        
        # Retrieve documents
        results = self.vector_store.search(
            query=question,
            top_k=self.config.rag_top_k,
            min_score=self.config.rag_min_relevance_score
        )
        
        # Convert to LangChain Document format
        documents = []
        for result in results:
            doc = Document(
                page_content=result['content'],
                metadata=result['metadata']
            )
            documents.append(doc)
        
        logger.info(f"Retrieved {len(documents)} documents")
        
        return {"documents": documents, "question": question}
    
    def _grade_documents(self, state: GraphState) -> GraphState:
        """
        Grade document relevance to the question.
        
        Args:
            state: Current graph state
        
        Returns:
            Updated state with filtered documents
        """
        logger.info("---GRADE DOCUMENTS---")
        question = state["question"]
        documents = state["documents"]
        
        # Grade each document
        filtered_docs = []
        web_search = "No"
        
        for doc in documents:
            score = self._grade_document_relevance(question, doc.page_content)
            
            if score == "yes":
                logger.info("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(doc)
            else:
                logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = "Yes"
        
        return {
            "documents": filtered_docs,
            "question": question,
            "web_search": web_search
        }
    
    def _grade_document_relevance(self, question: str, document: str) -> str:
        """
        Grade if a document is relevant to the question.
        
        Args:
            question: User question
            document: Document content
        
        Returns:
            "yes" or "no"
        """
        system_prompt = """You are a grader assessing relevance of a retrieved document to a user question.
        
If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question."""
        
        prompt = f"""Question: {question}

Document: {document}

Is this document relevant to the question? Answer only 'yes' or 'no'."""
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            # Extract yes/no from response
            response_lower = response.lower().strip()
            if 'yes' in response_lower:
                return "yes"
            else:
                return "no"
                
        except Exception as e:
            logger.error(f"Document grading failed: {e}")
            return "yes"  # Default to relevant on error
    
    def _transform_query(self, state: GraphState) -> GraphState:
        """
        Transform the query to improve retrieval.
        
        Args:
            state: Current graph state
        
        Returns:
            Updated state with transformed question
        """
        logger.info("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]
        transform_count = state.get("transform_count", 0) + 1
        
        system_prompt = """You are a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval.
        
Look at the input and try to reason about the underlying semantic intent / meaning."""
        
        prompt = f"""Here is the initial question:

{question}

Formulate an improved question that will retrieve better results from a vectorstore."""
        
        try:
            better_question = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            logger.info(f"Transformed question: {better_question}")
            
            return {
                "documents": documents,
                "question": better_question,
                "transform_count": transform_count
            }
            
        except Exception as e:
            logger.error(f"Query transformation failed: {e}")
            return {
                "documents": documents,
                "question": question,
                "transform_count": transform_count
            }
    
    def _decide_to_generate(self, state: GraphState) -> str:
        """
        Decide whether to generate an answer or transform the query.
        
        Args:
            state: Current graph state
        
        Returns:
            Next node: "generate", "transform_query", or "web_search"
        """
        logger.info("---DECIDE TO GENERATE---")
        web_search = state.get("web_search", "No")
        transform_count = state.get("transform_count", 0)
        
        if web_search == "Yes":
            # Documents are not relevant, try web search
            logger.info("---DECISION: WEB SEARCH---")
            return "web_search"
        elif transform_count >= self.config.rag_max_transform_attempts:
            # Max transforms reached, generate anyway
            logger.info("---DECISION: GENERATE (max transforms)---")
            return "generate"
        elif not state.get("documents"):
            # No documents, transform query
            logger.info("---DECISION: TRANSFORM QUERY---")
            return "transform_query"
        else:
            # Documents are relevant, generate
            logger.info("---DECISION: GENERATE---")
            return "generate"

