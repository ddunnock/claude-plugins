# src/knowledge_mcp/store/__init__.py
"""
Vector store backends for Knowledge MCP.

This module provides vector storage implementations for
Qdrant Cloud (primary) and ChromaDB (fallback).

Example:
    >>> from knowledge_mcp.store import QdrantStore
    >>> store = QdrantStore(config)
    >>> store.add_chunks(chunks)
"""

from __future__ import annotations

from knowledge_mcp.store.base import BaseStore
from knowledge_mcp.store.qdrant_store import QdrantStore

__all__: list[str] = ["BaseStore", "QdrantStore"]
