# src/knowledge_mcp/cli/validate.py
"""
Validation CLI commands for RCCA standards ingestion.

Provides CLI commands to validate that critical RCCA tables (AP matrix,
severity scales, CAPA templates) are retrievable from the knowledge base.

Example:
    >>> knowledge validate collection rcca_standards
    >>> knowledge validate collection rcca_standards --verbose
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk
    from knowledge_mcp.utils.config import KnowledgeConfig
    from knowledge_mcp.validation.table_validator import ValidationResult

validate_app = typer.Typer(help="Validation commands for RCCA standards")
console = Console()


def _validate_collection_name(value: str) -> str:
    """Validate collection name format.

    Args:
        value: Collection name to validate.

    Returns:
        Validated collection name.

    Raises:
        typer.BadParameter: If collection name is invalid.
    """
    import re

    # Allow alphanumeric, underscores, hyphens
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", value):
        raise typer.BadParameter(
            "Collection name must start with a letter and contain only "
            "letters, numbers, underscores, and hyphens"
        )
    if len(value) > 100:
        raise typer.BadParameter("Collection name must be 100 characters or less")
    return value


@validate_app.command("collection")
def validate_collection(
    collection: str = typer.Argument(
        ...,
        help="Name of the collection to validate",
        callback=_validate_collection_name,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed results for each validation check",
    ),
) -> None:
    """Validate critical RCCA tables in a collection.

    Runs query-based validation to verify that critical RCCA lookup tables
    (AP matrix, severity categories, CAPA templates) are retrievable.

    Exit codes:
      0 - All validations passed
      1 - One or more validations failed

    Example:
        $ knowledge validate collection rcca_standards
        $ knowledge validate collection rcca_standards --verbose
    """
    asyncio.run(_validate_collection_async(collection, verbose))


async def _validate_collection_async(collection: str, verbose: bool) -> None:
    """Async validation logic.

    Args:
        collection: Name of the collection to validate.
        verbose: Whether to show detailed results.
    """
    from knowledge_mcp.utils.config import load_config
    from knowledge_mcp.validation import TableValidator, ValidationReport

    config = load_config()

    console.print(f"\n[bold]Validating collection:[/bold] {collection}\n")

    try:
        # Create searcher adapter and validator
        searcher = _create_searcher_adapter(config, collection)
        validator = TableValidator(searcher, collection)

        # Run validation with spinner
        with console.status("[bold blue]Running table validations...[/bold blue]"):
            results = await validator.validate_all()

        # Create report
        report = ValidationReport(collection=collection, results=results)

        # Display results
        _display_results(results, verbose)

        # Display summary
        console.print()
        if report.all_passed:
            console.print(
                f"[bold green]PASSED:[/bold green] {report.passed_count}/{len(results)} "
                "validations passed"
            )
        else:
            console.print(
                f"[bold red]FAILED:[/bold red] {report.failed_count}/{len(results)} "
                "validations failed"
            )

            # Show recommendations
            recommendations = report.get_recommendations()
            if recommendations:
                console.print("\n[bold yellow]Recommendations:[/bold yellow]")
                for rec in recommendations:
                    console.print(f"  - {rec}")

            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)


class _SearcherAdapter:
    """Adapter to satisfy SearcherProtocol for TableValidator.

    Wraps vector store to provide the collection-based search interface
    expected by TableValidator's SearcherProtocol.

    Note: The collection is fixed at construction time based on config.
    The collection parameter in search() is for interface compatibility.
    """

    def __init__(self, config: KnowledgeConfig, collection: str) -> None:
        """Initialize adapter with config and collection.

        Args:
            config: Knowledge MCP configuration.
            collection: Collection name to search (for validation/logging).
        """
        from knowledge_mcp.embed import OpenAIEmbedder
        from knowledge_mcp.store import create_store

        self._embedder = OpenAIEmbedder(api_key=config.openai_api_key)
        self._store = create_store(config)
        self._collection = collection

    async def search(
        self,
        query: str,
        collection: str,
        n_results: int = 10,
    ) -> list[KnowledgeChunk]:
        """Search for chunks matching query.

        Args:
            query: Search query string.
            collection: Collection name (must match adapter's collection).
            n_results: Maximum number of results.

        Returns:
            List of KnowledgeChunk objects with id and content attributes.

        Raises:
            ValueError: If collection doesn't match adapter's collection.
        """
        import logging

        from knowledge_mcp.models.chunk import KnowledgeChunk

        logger = logging.getLogger(__name__)

        if collection != self._collection:
            logger.warning(
                "Search requested for collection '%s' but adapter configured for '%s'",
                collection,
                self._collection,
            )

        query_embedding = await self._embedder.embed(query)
        raw_results = self._store.search(
            query_embedding=query_embedding,
            n_results=n_results,
        )

        chunks: list[KnowledgeChunk] = []
        for r in raw_results:
            metadata = r.get("metadata", {})
            chunk = KnowledgeChunk(
                id=str(r["id"]),
                document_id=str(metadata.get("document_id", "")),
                document_title=str(metadata.get("document_title", "")),
                document_type=str(metadata.get("document_type", "")),
                content=str(r["content"]),
                content_hash="",  # Not needed for validation
                token_count=0,  # Not needed for validation
            )
            chunks.append(chunk)

        return chunks


def _create_searcher_adapter(
    config: KnowledgeConfig,
    collection: str,
) -> _SearcherAdapter:
    """Create a searcher adapter for validation.

    Args:
        config: Knowledge MCP configuration.
        collection: Collection name to validate.

    Returns:
        SearcherAdapter instance satisfying SearcherProtocol.
    """
    return _SearcherAdapter(config, collection)


def _display_results(results: list[ValidationResult], verbose: bool) -> None:
    """Display validation results.

    Args:
        results: List of validation results.
        verbose: Whether to show detailed check results.
    """
    table = Table(title="Validation Results")
    table.add_column("Table", style="cyan", width=35)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Chunks", justify="right", width=8)

    for result in results:
        if result.passed:
            status = "[green]PASS[/green]"
        else:
            status = "[red]FAIL[/red]"

        table.add_row(result.table_name, status, str(result.chunks_retrieved))

    console.print(table)

    # Verbose output
    if verbose:
        console.print("\n[bold]Detailed Results:[/bold]")
        for result in results:
            console.print(f"\n  [cyan]{result.table_name}[/cyan]")
            for check_name, check_passed in result.details.items():
                if check_passed:
                    icon = "[green]OK[/green]"
                else:
                    icon = "[red]X[/red]"
                console.print(f"    {icon} {check_name}")


async def run_validation_for_ingest(
    collection: str,
    config: KnowledgeConfig,
) -> tuple[bool, list[ValidationResult]]:
    """Run validation for use by ingest command.

    This is a helper function for ingest_docs --validate flag.

    Args:
        collection: Name of the collection to validate.
        config: Knowledge MCP configuration.

    Returns:
        Tuple of (all_passed, results).
    """
    from knowledge_mcp.validation import TableValidator

    searcher = _create_searcher_adapter(config, collection)
    validator = TableValidator(searcher, collection)
    results = await validator.validate_all()
    all_passed = all(r.passed for r in results)
    return (all_passed, results)


def display_validation_summary(
    results: list[ValidationResult],
    collection: str,
) -> None:
    """Display condensed validation summary for ingest command.

    Args:
        results: List of validation results.
        collection: Name of the validated collection.
    """
    passed = sum(1 for r in results if r.passed)
    total = len(results)

    console.print(f"\n[bold]Validation ({collection}):[/bold]")

    for result in results:
        if result.passed:
            console.print(f"  [green]OK[/green] {result.table_name}")
        else:
            console.print(f"  [red]X[/red] {result.table_name}")
            if result.recommendation:
                console.print(f"      [dim]{result.recommendation}[/dim]")

    if passed == total:
        console.print(f"\n[green]All {total} validations passed.[/green]")
    else:
        console.print(f"\n[yellow]{total - passed} of {total} validations failed.[/yellow]")


def main() -> None:
    """Backwards-compatible entry point."""
    validate_app()
