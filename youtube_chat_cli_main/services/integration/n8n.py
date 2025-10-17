"""n8n integration."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in n8n_client.py
from ...n8n_client import N8nClient

__all__ = ["N8nClient"]

