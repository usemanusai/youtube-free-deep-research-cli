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

    def _web_search(self, state: GraphState) -> GraphState:
        """
        Perform web search to supplement knowledge.

        Args:
            state: Current graph state

        Returns:
            Updated state with web search results
        """
        logger.info("---WEB SEARCH---")
        question = state["question"]

        # Perform web search
        try:
            search_results = self.web_search.search(
                query=question,
                max_results=3
            )

            # Convert to Document format
            web_documents = []
            for result in search_results:
                doc = Document(
                    page_content=result['content'],
                    metadata={
                        'title': result['title'],
                        'url': result['url'],
                        'source': 'web_search'
                    }
                )
                web_documents.append(doc)

            logger.info(f"Web search returned {len(web_documents)} results")

            return {
                "documents": web_documents,
                "question": question
            }

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "documents": [],
                "question": question
            }

    def _generate(self, state: GraphState) -> GraphState:
        """
        Generate answer based on retrieved documents.

        Args:
            state: Current graph state

        Returns:
            Updated state with generated answer
        """
        logger.info("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        # Format documents as context
        context = "\n\n".join([doc.page_content for doc in documents])

        system_prompt = """You are an assistant for question-answering tasks.

Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise."""

        prompt = f"""Question: {question}

Context:
{context}

Answer:"""

        try:
            generation = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )

            logger.info(f"Generated answer: {generation[:100]}...")

            return {
                "documents": documents,
                "question": question,
                "generation": generation
            }

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return {
                "documents": documents,
                "question": question,
                "generation": f"Error generating answer: {e}"
            }

    def _grade_generation(self, state: GraphState) -> str:
        """
        Grade the generated answer for hallucinations and usefulness.

        Args:
            state: Current graph state

        Returns:
            Next node: "useful", "not useful", or "not supported"
        """
        logger.info("---GRADE GENERATION---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        # Check for hallucinations (if enabled)
        if self.config.rag_hallucination_check:
            is_grounded = self._check_hallucination(documents, generation)

            if not is_grounded:
                logger.info("---DECISION: GENERATION NOT GROUNDED, RE-GENERATE---")
                return "not supported"

        # Check answer quality (if enabled)
        if self.config.rag_answer_check:
            is_useful = self._check_answer_quality(question, generation)

            if is_useful:
                logger.info("---DECISION: GENERATION USEFUL---")
                return "useful"
            else:
                logger.info("---DECISION: GENERATION NOT USEFUL---")
                return "not useful"

        # Default to useful if checks are disabled
        return "useful"

    def _check_hallucination(self, documents: List[Document], generation: str) -> bool:
        """
        Check if the generation is grounded in the documents.

        Args:
            documents: Retrieved documents
            generation: Generated answer

        Returns:
            True if grounded, False if hallucinated
        """
        context = "\n\n".join([doc.page_content for doc in documents])

        system_prompt = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts.

Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

        prompt = f"""Facts:
{context}

LLM generation: {generation}

Is the generation grounded in the facts? Answer only 'yes' or 'no'."""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )

            response_lower = response.lower().strip()
            return 'yes' in response_lower

        except Exception as e:
            logger.error(f"Hallucination check failed: {e}")
            return True  # Default to grounded on error

    def _check_answer_quality(self, question: str, generation: str) -> bool:
        """
        Check if the generation answers the question.

        Args:
            question: User question
            generation: Generated answer

        Returns:
            True if useful, False otherwise
        """
        system_prompt = """You are a grader assessing whether an answer addresses / resolves a question.

Give a binary score 'yes' or 'no'. 'Yes' means that the answer resolves the question."""

        prompt = f"""Question: {question}

Answer: {generation}

Does the answer address the question? Answer only 'yes' or 'no'."""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )

            response_lower = response.lower().strip()
            return 'yes' in response_lower

        except Exception as e:
            logger.error(f"Answer quality check failed: {e}")
            return True  # Default to useful on error

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG engine with a question.

        Args:
            question: User question

        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"RAG query: {question}")

        # Initialize state
        initial_state = {
            "question": question,
            "generation": "",
            "web_search": "No",
            "documents": [],
            "transform_count": 0
        }

        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)

            return {
                "answer": final_state.get("generation", "No answer generated"),
                "question": final_state.get("question"),
                "documents": final_state.get("documents", []),
                "web_search_used": final_state.get("web_search") == "Yes",
                "transform_count": final_state.get("transform_count", 0)
            }

        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "answer": f"Error processing query: {e}",
                "question": question,
                "documents": [],
                "web_search_used": False,
                "transform_count": 0
            }


# Global service instance
_rag_engine: Optional[AdaptiveRAGEngine] = None


def get_rag_engine() -> AdaptiveRAGEngine:
    """
    Get the global RAG engine instance.

    Returns:
        AdaptiveRAGEngine instance
    """
    global _rag_engine

    if _rag_engine is None:
        _rag_engine = AdaptiveRAGEngine()
        logger.info("RAG engine instance created")

    return _rag_engine

