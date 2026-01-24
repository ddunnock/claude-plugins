# src/knowledge_mcp/__main__.py
"""
Entry point for running package as a module.

Usage:
    python -m knowledge_mcp [options]

Examples:
    python -m knowledge_mcp --help
    python -m knowledge_mcp serve
    python -m knowledge_mcp ingest --source ./data/sources
"""

from __future__ import annotations

import sys


def cli() -> int:
    """
    Command-line interface entry point.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    import asyncio

    from knowledge_mcp.server import main as server_main

    try:
        asyncio.run(server_main())
        return 0
    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted by user\n")
        return 130
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(cli())