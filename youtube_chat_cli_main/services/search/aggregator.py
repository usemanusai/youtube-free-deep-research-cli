"""Search aggregator."""

# This module re-exports from the legacy location for backward compatibility
# The actual implementation is in services/search_aggregator.py
from ..search_aggregator import SearchAggregator

__all__ = ["SearchAggregator"]

