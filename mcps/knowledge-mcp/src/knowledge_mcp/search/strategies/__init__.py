"""Workflow-specific search strategies.

This module provides the strategy pattern implementation for specialized
retrieval across different systems engineering workflows.

Example:
    >>> from knowledge_mcp.search.strategies import SearchStrategy, SearchQuery
    >>> from knowledge_mcp.search.strategies.rcca import RCCAStrategy
"""

from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy

__all__ = ["SearchStrategy", "SearchQuery"]
