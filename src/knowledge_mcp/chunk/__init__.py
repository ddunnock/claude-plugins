# src/knowledge_mcp/chunk/__init__.py
"""
Document chunking module for Knowledge MCP.

This module provides chunking strategies for splitting documents
into semantically coherent units suitable for embedding and retrieval.

Example:
    >>> from knowledge_mcp.chunk import HierarchicalChunker
    >>> chunker = HierarchicalChunker(max_tokens=512)
    >>> chunks = chunker.chunk(sections)
"""

from __future__ import annotations

__all__: list[str] = []
