# src/knowledge_mcp/cli/verify.py
"""Verify command for collection health checks.

Provides CLI command to validate vector store collection health,
including chunk counts, document counts, and embedding dimensions.

Example:
    >>> knowledge verify
    >>> knowledge verify --embeddings
    >>> knowledge verify --collection my_collection
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from knowledge_mcp.utils.config import KnowledgeConfig

console = Console()


def verify_command(
    collection: str = typer.Option(
        "",
        "--collection",
        "-c",
        help="Collection name to verify (uses versioned default if not specified)",
    ),
    check_embeddings: bool = typer.Option(
        False,
        "--embeddings",
        "-e",
        help="Verify embedding dimensions match configured dimensions",
    ),
) -> None:
    """Validate collection health and embeddings.

    Checks:
    - Collection exists and is accessible
    - Document and chunk counts
    - Embedding dimensions (if --embeddings flag)

    Example:
        $ knowledge verify
        $ knowledge verify --embeddings
        $ knowledge verify -c my_collection --embeddings
    """
    import asyncio

    from knowledge_mcp.utils.config import load_config

    # Load config
    config = load_config()

    # Run async verification
    asyncio.run(_verify_async(collection, check_embeddings, config))


async def _verify_async(
    collection: str,
    check_embeddings: bool,
    config: KnowledgeConfig,
) -> None:
    """Async verification logic.

    Args:
        collection: Collection name to verify (empty uses default).
        check_embeddings: Whether to validate embedding dimensions.
        config: Knowledge MCP configuration.
    """
    from knowledge_mcp.store import create_store

    # Determine collection name
    effective_collection = collection if collection else config.versioned_collection_name

    console.print(f"\n[bold]Verifying collection:[/bold] {effective_collection}\n")

    try:
        # Create store
        store = create_store(config)

        # Get collection stats
        stats = store.get_stats()

        # Display stats table
        table = Table(title="Collection Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Collection", stats.get("collection_name", effective_collection))
        table.add_row("Total Chunks", str(stats.get("total_chunks", "N/A")))
        table.add_row("Indexed Vectors", str(stats.get("indexed_vectors", "N/A")))

        # Extract vector dimensions from config section
        store_config = stats.get("config", {})
        vector_dimensions = store_config.get("vector_size", "N/A")
        table.add_row("Vector Dimensions", str(vector_dimensions))
        table.add_row("Hybrid Search", str(store_config.get("hybrid_enabled", False)))

        console.print(table)

        # Check embedding dimensions if requested
        if check_embeddings:
            console.print("\n[bold]Embedding Verification:[/bold]")
            expected_dims = config.embedding_dimensions
            actual_dims = store_config.get("vector_size")

            if actual_dims is None:
                console.print(
                    "[yellow]UNKNOWN[/yellow] Could not determine collection dimensions"
                )
            elif actual_dims == expected_dims:
                console.print(f"[green]OK[/green] Dimensions match ({actual_dims})")
            else:
                console.print(
                    f"[red]MISMATCH[/red] Expected {expected_dims}, found {actual_dims}"
                )
                console.print(
                    "[yellow]Warning:[/yellow] Dimension mismatch may cause search issues. "
                    "Consider re-ingesting with correct embedding model."
                )
                raise typer.Exit(1)

        console.print("\n[green]Verification complete.[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)
