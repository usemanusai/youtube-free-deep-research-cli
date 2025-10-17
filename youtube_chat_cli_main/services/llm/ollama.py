"""Ollama LLM service implementation."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/llm_service.py
from ..llm_service import OllamaLLMService

__all__ = ["OllamaLLMService"]

