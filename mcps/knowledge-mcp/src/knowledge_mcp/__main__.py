# src/knowledge_mcp/__main__.py
"""
Entry point for running package as a module.

Usage:
    python -m knowledge_mcp           # Start MCP server (default)
    python -m knowledge_mcp cli ...   # Run CLI commands

Examples:
    python -m knowledge_mcp                      # Start MCP server
    python -m knowledge_mcp cli --help           # Show CLI help
    python -m knowledge_mcp cli ingest docs ./data/sources
"""

from __future__ import annotations

import asyncio
import sys


def main() -> None:
    """
    Main entry point.

    - No args or empty: Start the MCP server
    - 'cli' subcommand: Run the CLI
    """
    # If 'cli' is first argument, run CLI
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Remove 'cli' from argv so typer sees correct args
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from knowledge_mcp.cli.main import cli as typer_cli
        typer_cli()
    else:
        # Default: run MCP server
        from knowledge_mcp.server import main as server_main
        asyncio.run(server_main())


if __name__ == "__main__":
    main()