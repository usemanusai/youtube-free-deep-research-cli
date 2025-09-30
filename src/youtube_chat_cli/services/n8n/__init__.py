"""
n8n integration services.

Provides integration with n8n workflows for:
- RAG (Retrieval-Augmented Generation) processing
- Webhook communication
- Video data forwarding
- Retry logic and error handling
"""

from .client import N8nClient, get_n8n_client

__all__ = ['N8nClient', 'get_n8n_client']
