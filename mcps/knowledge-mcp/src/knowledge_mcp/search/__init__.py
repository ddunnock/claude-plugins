# src/knowledge_mcp/search/__init__.py
"""
Search and retrieval module for Knowledge MCP.

This module provides search functionality including semantic search,
hybrid search, and metadata filtering for the knowledge base.

Example:
    >>> from knowledge_mcp.search import SemanticSearcher, SearchResult
    >>> from knowledge_mcp.embed import OpenAIEmbedder
    >>> from knowledge_mcp.store import QdrantStore
    >>>
    >>> embedder = OpenAIEmbedder(api_key="...")
    >>> store = QdrantStore(config)
    >>> searcher = SemanticSearcher(embedder, store)
    >>> results = await searcher.search("system requirements", n_results=10)
"""

from __future__ import annotations

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.semantic_search import SemanticSearcher

__all__: list[str] = [
    "SearchResult",
    "SemanticSearcher",
]
