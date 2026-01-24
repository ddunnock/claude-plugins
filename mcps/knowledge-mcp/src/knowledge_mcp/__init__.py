# src/knowledge_mcp/__init__.py
"""
Knowledge MCP - Semantic search over technical reference documents.

This package provides MCP (Model Context Protocol) tools for searching
IEEE standards, INCOSE guides, NASA handbooks, and other systems
engineering reference materials.

Example:
    >>> from knowledge_mcp import KnowledgeMCPServer
    >>> server = KnowledgeMCPServer()
    >>> results = await server.search("system requirements review")

Attributes:
    __version__: Package version string.
"""

from knowledge_mcp.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    InternalError,
    KnowledgeMCPError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from knowledge_mcp.server import KnowledgeMCPServer

__version__ = "0.1.0"
__all__ = [
    # Server
    "KnowledgeMCPServer",
    # Exceptions
    "KnowledgeMCPError",
    "ConfigurationError",
    "ConnectionError",
    "TimeoutError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "InternalError",
    # Metadata
    "__version__",
]