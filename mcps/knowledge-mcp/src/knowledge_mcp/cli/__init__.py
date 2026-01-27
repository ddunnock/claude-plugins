# src/knowledge_mcp/cli/__init__.py
"""
Command-line interface module for Knowledge MCP.

This module provides CLI commands for document ingestion,
server management, and configuration validation.

Example:
    >>> from knowledge_mcp.cli import cli
    >>> cli()  # Runs the CLI application
"""

from __future__ import annotations

from knowledge_mcp.cli.main import app, cli

__all__: list[str] = ["app", "cli"]
