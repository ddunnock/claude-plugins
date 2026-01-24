# src/knowledge_mcp/chunk/__init__.py
"""
Document chunking module for Knowledge MCP.

This module provides chunking strategies for splitting documents
into semantically coherent units suitable for embedding and retrieval.

Example:
    >>> from knowledge_mcp.chunk import HierarchicalChunker, ChunkConfig
    >>> config = ChunkConfig(target_tokens=500, max_tokens=1000)
    >>> chunker = HierarchicalChunker(config)
    >>> chunks = chunker.chunk(elements, metadata)
"""

from __future__ import annotations

from knowledge_mcp.chunk.base import (
    BaseChunker,
    ChunkConfig,
    ChunkResult,
    DocumentMetadata,
    ParsedElement,
)
from knowledge_mcp.chunk.hierarchical import HierarchicalChunker

__all__ = [
    "BaseChunker",
    "ChunkConfig",
    "ChunkResult",
    "DocumentMetadata",
    "ParsedElement",
    "HierarchicalChunker",
]
