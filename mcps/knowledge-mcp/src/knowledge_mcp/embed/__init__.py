# src/knowledge_mcp/embed/__init__.py
"""Embedding generation module for Knowledge MCP.

This module provides embedding services for converting text chunks
into vector representations for semantic search.

Use create_embedder(config) to get the appropriate embedder based on configuration.

Example:
    >>> from knowledge_mcp.embed import create_embedder
    >>> from knowledge_mcp.utils.config import load_config
    >>> config = load_config()
    >>> embedder = create_embedder(config)
    >>> vectors = await embedder.embed_batch(["text1", "text2"])

Available Embedders:
    - OpenAIEmbedder: Uses OpenAI text-embedding-3-small (1536 dimensions)
    - LocalEmbedder: Uses sentence-transformers (384/768 dimensions)
    - BaseEmbedder: Abstract base class for custom implementations
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from knowledge_mcp.embed.base import BaseEmbedder
from knowledge_mcp.embed.cache import EmbeddingCache
from knowledge_mcp.embed.openai_embedder import OpenAIEmbedder

if TYPE_CHECKING:
    from knowledge_mcp.utils.config import KnowledgeConfig

__all__: list[str] = ["BaseEmbedder", "EmbeddingCache", "OpenAIEmbedder", "create_embedder"]

# Conditionally export LocalEmbedder if sentence-transformers is available
try:
    from knowledge_mcp.embed.local_embedder import LocalEmbedder

    __all__.append("LocalEmbedder")
    _HAS_LOCAL = True
except ImportError:
    _HAS_LOCAL = False


def create_embedder(config: KnowledgeConfig) -> BaseEmbedder:
    """Create embedder based on configuration.

    Factory function that returns the appropriate embedder instance
    based on config.embedding_provider setting.

    Args:
        config: KnowledgeConfig instance with embedding settings.

    Returns:
        BaseEmbedder instance (OpenAIEmbedder or LocalEmbedder).

    Raises:
        ValueError: If provider is "local" but sentence-transformers not installed.
        ValueError: If provider is unknown.

    Example:
        >>> config = load_config()
        >>> embedder = create_embedder(config)
        >>> vector = await embedder.embed("test query")
    """
    if config.embedding_provider == "openai":
        return OpenAIEmbedder(
            api_key=config.openai_api_key,
            model=config.embedding_model,
            dimensions=config.embedding_dimensions,
        )
    elif config.embedding_provider == "local":
        if not _HAS_LOCAL:
            raise ValueError(
                "Local embeddings require sentence-transformers. "
                "Install with: poetry install --with local"
            )
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        return LocalEmbedder(model_name=config.local_embedding_model)
    else:
        raise ValueError(f"Unknown embedding provider: {config.embedding_provider}")
