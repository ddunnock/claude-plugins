# src/knowledge_mcp/cli/ingest.py
"""
Ingest subcommand group for document ingestion.

This module provides CLI commands for ingesting documents into the knowledge base.
Supports PDF and DOCX files with progress tracking and error handling.

Example:
    >>> knowledge ingest docs /path/to/documents
    >>> knowledge ingest docs /path/to/file.pdf --collection my_collection
    >>> knowledge ingest docs /path/to/standards --validate
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.progress import track

from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.pipeline import IngestionPipeline

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk

ingest_app = typer.Typer(help="Document ingestion commands")
console = Console()

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


@ingest_app.command("docs")
def ingest_docs(
    path: Path = typer.Argument(
        ...,
        help="Path to document file or directory",
        exists=True,
        resolve_path=True,
    ),
    collection: str = typer.Option(
        "knowledge",
        "--collection",
        "-c",
        help="Vector store collection name",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recursively process directories",
    ),
    validate: bool = typer.Option(
        False,
        "--validate",
        help="Run RCCA table validation after ingestion",
    ),
) -> None:
    """Ingest local documents into the knowledge base."""

    # Collect files to process
    files: list[Path] = []
    if path.is_file():
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
        else:
            console.print(
                f"[red]Error:[/red] Unsupported file type: {path.suffix}. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
            raise typer.Exit(1)
    else:
        # Directory - glob for supported files
        pattern = "**/*" if recursive else "*"
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(path.glob(f"{pattern}{ext}"))

    if not files:
        console.print(f"[yellow]Warning:[/yellow] No PDF or DOCX files found in {path}")
        raise typer.Exit(0)

    console.print(f"\n[bold]Ingesting {len(files)} document(s)...[/bold]\n")

    # Initialize pipeline
    pipeline = IngestionPipeline()

    # Track results
    total_chunks = 0
    successful = 0
    failed: list[tuple[Path, str]] = []

    # Process files with progress bar
    for file_path in track(files, description="Processing..."):
        try:
            chunks: list[KnowledgeChunk] = pipeline.ingest(file_path)
            total_chunks += len(chunks)
            successful += 1
            console.print(f"  [green]OK[/green] {file_path.name}: {len(chunks)} chunks")
        except IngestionError as e:
            failed.append((file_path, str(e)))
            console.print(f"  [red]FAIL[/red] {file_path.name}: {e}")
        except Exception as e:
            failed.append((file_path, str(e)))
            console.print(f"  [red]FAIL[/red] {file_path.name}: {e}")

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Processed: {successful}/{len(files)} documents")
    console.print(f"  Total chunks: {total_chunks}")

    if failed:
        console.print(f"\n[red]Failed files ({len(failed)}):[/red]")
        for fp, err in failed:
            console.print(f"  - {fp.name}: {err}")
        raise typer.Exit(1)

    console.print("\n[green]Ingestion complete.[/green]")

    # Run validation if requested
    if validate:
        _run_post_ingest_validation(collection)


def _run_post_ingest_validation(collection: str) -> None:
    """Run RCCA table validation after ingestion.

    Args:
        collection: Name of the collection to validate.

    Raises:
        typer.Exit: With code 1 if validation fails.
    """
    import asyncio

    # Import validation helpers locally to avoid circular imports
    from knowledge_mcp.cli.validate import (
        display_validation_summary,
        run_validation_for_ingest,
    )
    from knowledge_mcp.utils.config import load_config

    config = load_config()

    console.print("\n[bold]Running RCCA table validation...[/bold]")

    try:
        all_passed, results = asyncio.run(
            run_validation_for_ingest(collection, config)
        )

        display_validation_summary(results, collection)

        if not all_passed:
            console.print(
                "\n[yellow]Note:[/yellow] Ingestion completed but validation failed. "
                "Some RCCA skills may not work correctly until missing tables are ingested."
            )
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[yellow]Warning:[/yellow] Validation failed: {e}")
        console.print("Ingestion was successful but validation could not be completed.")


def main() -> None:
    """Backwards-compatible entry point."""
    ingest_app()
