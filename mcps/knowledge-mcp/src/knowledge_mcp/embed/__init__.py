# src/knowledge_mcp/embed/__init__.py
"""
Embedding generation module for Knowledge MCP.

This module provides embedding services for converting text chunks
into vector representations for semantic search.

Example:
    >>> from knowledge_mcp.embed import OpenAIEmbedder
    >>> embedder = OpenAIEmbedder(api_key="...")
    >>> vectors = await embedder.embed_batch(["text1", "text2"])

Available Embedders:
    - OpenAIEmbedder: Uses OpenAI text-embedding-3-small (1536 dimensions)
    - BaseEmbedder: Abstract base class for custom implementations
"""

from __future__ import annotations

from knowledge_mcp.embed.base import BaseEmbedder
from knowledge_mcp.embed.cache import EmbeddingCache
from knowledge_mcp.embed.openai_embedder import OpenAIEmbedder

__all__: list[str] = ["BaseEmbedder", "EmbeddingCache", "OpenAIEmbedder"]
