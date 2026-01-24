# src/knowledge_mcp/models/__init__.py
"""
Data models for Knowledge MCP.

This module defines the core data structures used throughout
the ingestion, embedding, and search pipelines.

Example:
    >>> from knowledge_mcp.models import KnowledgeChunk
    >>> chunk = KnowledgeChunk(id="...", content="...", ...)
"""

from __future__ import annotations

from knowledge_mcp.models.chunk import KnowledgeChunk

__all__: list[str] = ["KnowledgeChunk"]
