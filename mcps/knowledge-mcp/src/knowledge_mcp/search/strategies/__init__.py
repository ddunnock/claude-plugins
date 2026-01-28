"""Workflow-specific search strategies.

This module provides the strategy pattern implementation for specialized
retrieval across different systems engineering workflows.

Example:
    >>> from knowledge_mcp.search.strategies import SearchStrategy, SearchQuery
    >>> from knowledge_mcp.search.strategies.explore import ExploreStrategy
    >>> from knowledge_mcp.search.strategies.rcca import RCCAStrategy
"""

from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy
from knowledge_mcp.search.strategies.explore import ExploreStrategy
from knowledge_mcp.search.strategies.rcca import RCCAStrategy

__all__ = ["SearchStrategy", "SearchQuery", "ExploreStrategy", "RCCAStrategy"]
