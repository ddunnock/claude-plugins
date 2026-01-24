# src/knowledge_mcp/store/__init__.py
"""
Vector store backends for Knowledge MCP.

This module provides vector storage implementations for
Qdrant Cloud (primary) and ChromaDB (fallback).

Example:
    >>> from knowledge_mcp.store import create_store
    >>> store = create_store(config)
    >>> store.add_chunks(chunks)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union

from knowledge_mcp.store.base import BaseStore
from knowledge_mcp.store.qdrant_store import QdrantStore

if TYPE_CHECKING:
    from knowledge_mcp.store.chromadb_store import ChromaDBStore
    from knowledge_mcp.utils.config import KnowledgeConfig

logger = logging.getLogger(__name__)


def create_store(config: KnowledgeConfig) -> BaseStore:
    """
    Create a vector store based on configuration with automatic fallback.

    Attempts to create the configured vector store (Qdrant by default).
    If Qdrant is configured but unavailable, automatically falls back
    to ChromaDB for local operation.

    Args:
        config: Knowledge MCP configuration.

    Returns:
        A vector store instance (QdrantStore or ChromaDBStore).

    Raises:
        ConnectionError: When no vector store is available.

    Example:
        >>> config = load_config()
        >>> store = create_store(config)  # Returns QdrantStore or ChromaDBStore
        >>> store.add_chunks(chunks)
    """
    if config.vector_store == "chromadb":
        # Explicitly configured for ChromaDB
        from knowledge_mcp.store.chromadb_store import ChromaDBStore
        store = ChromaDBStore(config)
        if store.health_check():
            return store
        raise ConnectionError("ChromaDB initialization failed")

    # Default: try Qdrant first, fallback to ChromaDB
    try:
        store = QdrantStore(config)
        if store.health_check():
            logger.info("Connected to Qdrant Cloud: %s", config.qdrant_url)
            return store
        logger.warning("Qdrant health check failed")
    except Exception as e:
        logger.warning("Qdrant connection failed: %s", e)

    # Fallback to ChromaDB
    logger.warning("Qdrant unavailable, falling back to ChromaDB")
    try:
        from knowledge_mcp.store.chromadb_store import ChromaDBStore
        store = ChromaDBStore(config)
        if store.health_check():
            logger.info("Using ChromaDB fallback at: %s", config.chromadb_path)
            return store
    except Exception as e:
        logger.error("ChromaDB fallback also failed: %s", e)

    raise ConnectionError(
        f"No vector store available. "
        f"Qdrant at {config.qdrant_url} is unreachable and "
        f"ChromaDB at {config.chromadb_path} failed to initialize."
    )


__all__: list[str] = ["BaseStore", "QdrantStore", "create_store"]
