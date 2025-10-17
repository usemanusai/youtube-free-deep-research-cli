"""
JAEGIS NexusSync - LLM Service

This module provides a unified LLM interface supporting:
- Ollama (local, free, unlimited)
- OpenRouter (free tier available)
- OpenAI (costs money, not recommended)

Includes streaming support and structured output generation.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Iterator, Union
from abc import ABC, abstractmethod

# Ollama
import requests

# OpenRouter/OpenAI (optional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.config import get_config

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when LLM operations fail."""
    pass


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a structured JSON response."""
        pass
    
    @abstractmethod
    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """Stream response tokens from the LLM."""
        pass


class OllamaLLMService(BaseLLMService):
    """
    Ollama LLM service (FREE, local, unlimited).
    
    Uses local Ollama instance running in Docker.
    """
    
    def __init__(self, config):
        """Initialize Ollama LLM service."""
        self.config = config
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model
        
        # Verify Ollama is accessible
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Connected to Ollama at {self.base_url}")
        except Exception as e:
            raise LLMError(
                f"Failed to connect to Ollama at {self.base_url}: {e}\n"
                f"Make sure Ollama is running: docker ps | grep ollama"
            )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using Ollama."""
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make request
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens if max_tokens else -1
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result['message']['content']
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise LLMError(f"Failed to generate response: {e}")
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a structured JSON response using Ollama."""
        # Add JSON instruction to system prompt
        json_instruction = "\n\nYou must respond with valid JSON only. No other text."
        if response_format:
            json_instruction += f"\n\nExpected format:\n{json.dumps(response_format, indent=2)}"
        
        full_system_prompt = (system_prompt or "") + json_instruction
        
        # Generate response
        response = self.generate(
            prompt=prompt,
            system_prompt=full_system_prompt,
            temperature=0.1  # Lower temperature for structured output
        )
        
        # Parse JSON
        try:
            # Extract JSON from response (in case there's extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise LLMError(f"Failed to parse structured response: {e}")
    
    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """Stream response tokens from Ollama."""
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make streaming request
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {"temperature": temperature}
                },
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            # Stream tokens
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'message' in chunk and 'content' in chunk['message']:
                        yield chunk['message']['content']
                        
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise LLMError(f"Failed to stream response: {e}")


class OpenRouterLLMService(BaseLLMService):
    """
    OpenRouter LLM service (FREE tier available).
    
    Supports multiple free models including Llama 3.1 and Gemini Flash.
    """
    
    def __init__(self, config):
        """Initialize OpenRouter LLM service."""
        if not OPENAI_AVAILABLE:
            raise LLMError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        self.config = config
        self.model = config.llm_model
        
        if not config.openrouter_api_key:
            raise LLMError("OpenRouter API key not configured")
        
        try:
            self.client = OpenAI(
                api_key=config.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info("✅ OpenRouter LLM service initialized")
        except Exception as e:
            raise LLMError(f"Failed to initialize OpenRouter client: {e}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using OpenRouter."""
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter generation failed: {e}")
            raise LLMError(f"Failed to generate response: {e}")
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a structured JSON response using OpenRouter."""
        # Add JSON instruction to system prompt
        json_instruction = "\n\nYou must respond with valid JSON only. No other text."
        if response_format:
            json_instruction += f"\n\nExpected format:\n{json.dumps(response_format, indent=2)}"
        
        full_system_prompt = (system_prompt or "") + json_instruction
        
        # Generate response
        response = self.generate(
            prompt=prompt,
            system_prompt=full_system_prompt,
            temperature=0.1
        )
        
        # Parse JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise LLMError(f"Failed to parse structured response: {e}")
    
    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """Stream response tokens from OpenRouter."""
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make streaming request
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            # Stream tokens
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenRouter streaming failed: {e}")
            raise LLMError(f"Failed to stream response: {e}")


class LLMService:
    """
    Unified LLM service with automatic backend selection.

    Automatically selects the appropriate LLM backend based on configuration.
    Provides a consistent interface for all LLM operations.
    """

    def __init__(self):
        """Initialize LLM service with configured backend."""
        self.config = get_config()

        # Determine which backend to use
        # Priority: Ollama (if configured) > OpenRouter > OpenAI
        if self.config.ollama_base_url and self.config.ollama_model:
            self.backend = OllamaLLMService(self.config)
            logger.info("Using Ollama LLM service (FREE)")
        elif self.config.openrouter_api_key:
            self.backend = OpenRouterLLMService(self.config)
            logger.info("Using OpenRouter LLM service")
        else:
            raise LLMError(
                "No LLM backend configured. Please configure either:\n"
                "- Ollama (OLLAMA_BASE_URL and OLLAMA_MODEL)\n"
                "- OpenRouter (OPENROUTER_API_KEY and LLM_MODEL)"
            )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """
        return self.backend.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            response_format: Expected JSON structure

        Returns:
            Parsed JSON response
        """
        return self.backend.generate_structured(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format
        )

    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """
        Stream response tokens from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature

        Yields:
            Response tokens
        """
        return self.backend.stream(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat with the LLM using a conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """
        # Extract system prompt if present
        system_prompt = None
        user_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
            else:
                user_messages.append(f"{msg['role']}: {msg['content']}")

        # Combine user messages into a single prompt
        prompt = "\n\n".join(user_messages)

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get the global LLM service instance.

    Returns:
        LLMService instance
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService()
        logger.info("LLM service instance created")

    return _llm_service

