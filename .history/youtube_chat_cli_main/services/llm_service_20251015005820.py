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
import os
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

    Uses local Ollama instance via OpenAI-compatible API.
    """

    def __init__(self, config):
        """Initialize Ollama LLM service."""
        if not OPENAI_AVAILABLE:
            raise LLMError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self.config = config
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model
        logger.info(f"🔧 Ollama model configured: {self.model}")

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

        # Initialize OpenAI client pointing to Ollama
        try:
            self.client = OpenAI(
                api_key="ollama",  # Ollama doesn't need a real API key
                base_url=f"{self.base_url}/v1",
                timeout=120.0  # 2 minutes timeout for local Ollama
            )
            logger.info("✅ Ollama OpenAI-compatible client initialized")
        except Exception as e:
            raise LLMError(f"Failed to initialize Ollama client: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using Ollama via OpenAI-compatible API."""
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Make request using OpenAI client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens if max_tokens else 2000
            )

            return response.choices[0].message.content

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
    OpenRouter LLM service (FREE tier available) with intelligent API key rotation.

    Supports multiple free models including Llama 3.1 and Gemini Flash.
    Automatically rotates between multiple API keys to handle rate limits.
    """

    def __init__(self, config):
        """Initialize OpenRouter LLM service with multi-key rotation support."""
        if not OPENAI_AVAILABLE:
            raise LLMError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self.config = config
        self.model = config.llm_model

        # Get all available API keys
        self.api_keys = config.openrouter_api_keys
        if not self.api_keys:
            raise LLMError("No OpenRouter API keys configured")

        # Initialize rotation state
        self.current_key_index = 0
        self.rate_limit_tracker = {}  # {key_index: {'last_429_time': timestamp, 'cooldown_until': timestamp}}
        self._lock = None  # Will be initialized on first use for thread safety

        # Create initial client with first key
        try:
            self.client = self._create_client(self.api_keys[0])
            logger.info(f"✅ OpenRouter LLM service initialized with {len(self.api_keys)} API key(s)")
        except Exception as e:
            raise LLMError(f"Failed to initialize OpenRouter client: {e}")

    def _create_client(self, api_key: str):
        """Create an OpenAI client with the given API key."""
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def _get_next_available_key(self) -> tuple[int, str]:
        """
        Get the next available API key that is not rate-limited.

        Returns:
            Tuple of (key_index, api_key)

        Raises:
            LLMError: If all keys are rate-limited
        """
        import time

        current_time = time.time()
        available_keys = []

        # Check all keys for availability
        for i, key in enumerate(self.api_keys):
            if i in self.rate_limit_tracker:
                cooldown_until = self.rate_limit_tracker[i].get('cooldown_until', 0)
                if current_time < cooldown_until:
                    # Key is still in cooldown
                    continue
            available_keys.append((i, key))

        if not available_keys:
            # All keys are rate-limited, find the one with shortest cooldown
            min_cooldown = float('inf')
            for i in self.rate_limit_tracker:
                cooldown_until = self.rate_limit_tracker[i].get('cooldown_until', 0)
                if cooldown_until < min_cooldown:
                    min_cooldown = cooldown_until

            wait_time = max(0, min_cooldown - current_time)
            raise LLMError(
                f"All {len(self.api_keys)} OpenRouter API keys are rate-limited. "
                f"Retry in {wait_time:.1f} seconds."
            )

        # Return the next available key (round-robin)
        for idx, key in available_keys:
            if idx > self.current_key_index:
                return idx, key

        # Wrap around to the first available key
        return available_keys[0]

    def _mark_key_rate_limited(self, key_index: int, cooldown_seconds: int = 60):
        """Mark a key as rate-limited with a cooldown period."""
        import time

        current_time = time.time()
        self.rate_limit_tracker[key_index] = {
            'last_429_time': current_time,
            'cooldown_until': current_time + cooldown_seconds
        }
        logger.warning(
            f"🔄 API key {key_index + 1}/{len(self.api_keys)} rate-limited. "
            f"Cooldown: {cooldown_seconds}s"
        )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response using OpenRouter with automatic key rotation on rate limits.

        Automatically rotates to the next available API key if a 429 rate limit error occurs.
        """
        from openai import RateLimitError

        max_retries = len(self.api_keys)
        last_error = None

        for attempt in range(max_retries):
            try:
                # Build messages
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                # Log which key we're using
                logger.debug(f"Using API key {self.current_key_index + 1}/{len(self.api_keys)}")

                # Make request
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                if not response or not response.choices:
                    logger.error(f"OpenRouter returned empty response: {response}")
                    raise LLMError("OpenRouter returned empty response")

                content = response.choices[0].message.content
                if not content:
                    logger.error(f"OpenRouter returned empty content: {response}")
                    raise LLMError("OpenRouter returned empty content")

                return content

            except RateLimitError as e:
                # Mark current key as rate-limited
                self._mark_key_rate_limited(self.current_key_index, cooldown_seconds=60)
                last_error = e

                # Try to get next available key
                try:
                    next_index, next_key = self._get_next_available_key()
                    logger.info(f"🔄 Rotating to API key {next_index + 1}/{len(self.api_keys)}")

                    # Update client with new key
                    self.current_key_index = next_index
                    self.client = self._create_client(next_key)

                    # Continue to next attempt
                    continue

                except LLMError as rotation_error:
                    # All keys are rate-limited
                    logger.error(f"All API keys exhausted: {rotation_error}")
                    raise rotation_error

            except Exception as e:
                # Non-rate-limit errors (502, 500, network issues, etc.)
                logger.error(f"OpenRouter generation failed (key {self.current_key_index + 1}/{len(self.api_keys)}): {e}")

                # For non-429 errors, we don't rotate immediately
                # But if we have multiple keys, we can try one more time with a different key
                if len(self.api_keys) > 1 and attempt == 0:
                    try:
                        next_index, next_key = self._get_next_available_key()
                        logger.info(f"🔄 Trying different API key {next_index + 1}/{len(self.api_keys)} after error")
                        self.current_key_index = next_index
                        self.client = self._create_client(next_key)
                        last_error = e
                        continue
                    except:
                        pass

                raise LLMError(f"Failed to generate response: {e}")

        # If we exhausted all retries
        raise LLMError(f"Failed after {max_retries} attempts with all API keys: {last_error}")
    
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


class PlaceholderLLMService(BaseLLMService):
    """Non-networking placeholder LLM implementation for tests and offline mode."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        return system_prompt or "LLM_PLACEHOLDER"

    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, response_format: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"ok": True, "placeholder": True}

    def stream(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> Iterator[str]:
        yield "LLM_PLACEHOLDER_STREAM"


class LLMService:
    """
    Unified LLM service with automatic backend selection.

    Automatically selects the appropriate LLM backend based on configuration.
    Provides a consistent interface for all LLM operations.
    """

    def __init__(self):
        """Initialize LLM service with configured backend."""
        self.config = get_config()

        # Explicit override for tests/offline mode
        backend_override = os.getenv("NEXUS_LLM_BACKEND", "").strip().lower()
        if backend_override == "placeholder":
            self.backend = PlaceholderLLMService()
            logger.info("Using Placeholder LLM service (offline/test mode)")
            return

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

    def generate_podcast_script(self, context: str) -> str:
        """
        Generate a podcast script discussing the content.

        Args:
            context: The text content to analyze

        Returns:
            Podcast script with 2 speakers
        """
        prompt = f"""Provide a brief podcast script with 2 speakers (Host and Expert) discussing the content.
Keep it concise and friendly, approximately 1 minute long.

Content to discuss:
{context}"""

        try:
            return self.generate(prompt=prompt, temperature=0.7, max_tokens=500)
        except Exception as e:
            raise LLMError(f"Failed to generate podcast script: {e}")


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

