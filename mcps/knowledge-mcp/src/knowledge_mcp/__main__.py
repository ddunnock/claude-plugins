# src/knowledge_mcp/__main__.py
"""
Entry point for running package as a module.

Usage:
    python -m knowledge_mcp [options]

Examples:
    python -m knowledge_mcp --help
    python -m knowledge_mcp ingest docs ./data/sources
"""

from __future__ import annotations

import sys


def cli() -> None:
    """
    Command-line interface entry point.

    Delegates to the Typer CLI application.
    """
    from knowledge_mcp.cli.main import cli as typer_cli

    typer_cli()


if __name__ == "__main__":
    cli()