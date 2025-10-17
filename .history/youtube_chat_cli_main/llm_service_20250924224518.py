"""
LLM service module for interacting with OpenRouter.ai API.
"""

import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class LLMService:
    """Service for interacting with LLM APIs via OpenRouter.ai."""

    def __init__(self, api_key: str = None, model: str = "z-ai/glm-4.5-air:free"):
        """Initialize the LLM service.

        Args:
            api_key: OpenRouter API key. If None, attempts to load from environment.
            model: Model name for OpenRouter API.
        """
        if api_key is None:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable not set. Please configure your .env file.")

        self.api_key = api_key
        self.model = model

        # Initialize langchain ChatOpenAI client pointing to OpenRouter
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=2000
        )

    def _format_chat_history(self, chat_history: List[Dict]) -> List:
        """Convert chat history dict to langchain message objects."""
        messages = []
        for entry in chat_history:
            role = entry.get('role')
            content = entry.get('content', '')

            if role == 'user':
                messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                messages.append(AIMessage(content=content))
            elif role == 'system':
                messages.append(SystemMessage(content=content))

        return messages

    def generate_response(self, context: str, user_query: str, chat_history: List[Dict] = None) -> str:
        """Generate a response from the LLM with context and chat history.

        Args:
            context: The source text/content as context
            user_query: The user's question or prompt
            chat_history: Previous conversation history

        Returns:
            The LLM's response as a string
        """
        # Create system message with context instructions
        system_message = SystemMessage(content=f"""You are an expert assistant answering based on the provided context text.

CONTEXT:
{context}

Instructions:
- Answer questions using ONLY the information in the provided context.
- If the question cannot be answered from the context, respond with: "I'm sorry, I can't answer that question as the answer is not present in the provided context."
- If the question is irrelevant to the context, respond with: "I'm sorry, I can't answer that question as it is not relevant to the provided content."
- Provide detailed, accurate answers based on the context.
- If you need to quote from the context, do so accurately.""")

        # Add chat history if provided
        messages = [system_message]

        if chat_history:
            messages.extend(self._format_chat_history(chat_history))

        # Add the current user query
        messages.append(HumanMessage(content=user_query))

        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to get response from LLM service: {e}")

    def summarize_content(self, context: str) -> str:
        """Generate a concise summary of the provided content.

        Args:
            context: The text content to summarize

        Returns:
            Summary of the content
        """
        prompt = f"Please provide a concise summary of the following content:\n\n{context}"

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {e}")

    def generate_faq(self, context: str) -> str:
        """Generate a 5-question FAQ based on the content.

        Args:
            context: The text content to analyze

        Returns:
            FAQ in Q&A format
        """
        prompt = f"Based on the following content, generate a FAQ (Frequently Asked Questions) with 5 questions and their answers:\n\n{context}"

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate FAQ: {e}")

    def generate_toc(self, context: str) -> str:
        """Generate a table of contents for the content.

        Args:
            context: The text content to analyze

        Returns:
            Table of contents/outline
        """
        prompt = f"Please create a table of contents or structured outline for the following content:\n\n{context}"

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate table of contents: {e}")

    def generate_podcast_script(self, context: str) -> str:
        """Generate a podcast script discussing the content.

        Args:
            context: The text content to analyze

        Returns:
            Podcast script with 2 speakers
        """
        prompt = f"""Provide a podcast script with 2 speakers (Host and Expert) discussing the video content.
Keep a friendly tone with a bit of professionalism.
Structure it as a natural conversation approximately 2-3 minutes long.

Content to discuss:
{context}"""

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate podcast script: {e}")


# Global LLM service instance (when environment is properly set up)
_llm_service = None

def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
