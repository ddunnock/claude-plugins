# src/knowledge_mcp/search/__init__.py
"""
Search and retrieval module for Knowledge MCP.

This module provides search functionality including semantic search,
hybrid search, and metadata filtering for the knowledge base.

Example:
    >>> from knowledge_mcp.search import HybridSearcher
    >>> searcher = HybridSearcher(store, embedder)
    >>> results = searcher.search("system requirements", n_results=10)
"""

from __future__ import annotations

__all__: list[str] = []
