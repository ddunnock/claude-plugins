# src/knowledge_mcp/cli/main.py
"""
Main CLI application for Knowledge MCP.

This module provides the root Typer application that serves as the entry point
for all CLI commands. Subcommands are registered via add_typer().

Example:
    >>> knowledge --help
    >>> knowledge ingest docs /path/to/documents
    >>> knowledge validate collection my_standards
"""

from __future__ import annotations

import typer

from knowledge_mcp.cli.ingest import ingest_app
from knowledge_mcp.cli.validate import validate_app
from knowledge_mcp.cli.verify import verify_command

app = typer.Typer(
    name="knowledge",
    no_args_is_help=True,
    help="Knowledge MCP - Semantic search over technical documents",
)

# Register ingest subcommand group
app.add_typer(ingest_app, name="ingest")

# Register validate subcommand group
app.add_typer(validate_app, name="validate")

# Register verify command
app.command("verify")(verify_command)


def cli() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
