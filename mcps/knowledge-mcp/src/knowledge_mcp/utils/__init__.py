# src/knowledge_mcp/utils/__init__.py
"""
Utility modules for Knowledge MCP.

This module provides configuration management, logging,
hashing, and tokenization utilities.

Example:
    >>> from knowledge_mcp.utils import load_config
    >>> config = load_config()
"""

from __future__ import annotations

from knowledge_mcp.utils.config import KnowledgeConfig, load_config
from knowledge_mcp.utils.hashing import compute_content_hash
from knowledge_mcp.utils.logging import get_logger, setup_logging
from knowledge_mcp.utils.normative import NormativeIndicator, detect_normative
from knowledge_mcp.utils.tokenizer import TokenizerConfig, count_tokens, truncate_to_tokens

__all__: list[str] = [
    "KnowledgeConfig",
    "load_config",
    "setup_logging",
    "get_logger",
    "compute_content_hash",
    "NormativeIndicator",
    "detect_normative",
    "TokenizerConfig",
    "count_tokens",
    "truncate_to_tokens",
]
