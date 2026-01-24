#!/usr/bin/env python3
"""
Validation script for visual inspection of document ingestion.

This script runs the IngestionPipeline on a document and outputs
a detailed report for manual verification of:
- Document metadata extraction
- Chunk statistics (token counts, types)
- Table integrity (no mid-row splits)
- Section hierarchy preservation
- Normative/informative classification

Usage:
    python -m scripts.validate_ingestion path/to/document.pdf [--verbose] [--tables-only]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import mean, stdev

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from knowledge_mcp.ingest.pipeline import IngestionPipeline
from knowledge_mcp.models.chunk import KnowledgeChunk


console = Console()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="validate_ingestion",
        description="Validate document ingestion with visual inspection",
        epilog="Example: python -m scripts.validate_ingestion document.pdf --verbose",
    )
    parser.add_argument(
        "document_path",
        type=Path,
        help="Path to document file (PDF or DOCX)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output including sample text chunks",
    )
    parser.add_argument(
        "--tables-only",
        action="store_true",
        help="Only show table chunks (skip text chunks)",
    )
    return parser.parse_args()


def format_token_stats(chunks: list[KnowledgeChunk]) -> dict[str, int | float]:
    """Calculate token statistics for chunks."""
    if not chunks:
        return {"min": 0, "max": 0, "avg": 0.0, "total": 0, "std": 0.0}

    token_counts = [c.token_count for c in chunks]
    return {
        "min": min(token_counts),
        "max": max(token_counts),
        "avg": round(mean(token_counts), 1),
        "total": sum(token_counts),
        "std": round(stdev(token_counts), 1) if len(token_counts) > 1 else 0.0,
    }


def count_by_type(chunks: list[KnowledgeChunk]) -> dict[str, int]:
    """Count chunks by type."""
    counts: dict[str, int] = {}
    for chunk in chunks:
        chunk_type = chunk.chunk_type
        counts[chunk_type] = counts.get(chunk_type, 0) + 1
    return counts


def count_normative(chunks: list[KnowledgeChunk]) -> tuple[int, int]:
    """Count normative vs informative chunks."""
    normative = sum(1 for c in chunks if c.normative)
    informative = len(chunks) - normative
    return normative, informative


def format_table_preview(content: str, max_rows: int = 3) -> str:
    """
    Format table content for preview.

    Returns first N rows plus indicator if truncated.
    """
    lines = content.strip().split("\n")

    # Find actual table rows (skip caption if present)
    table_start = 0
    for i, line in enumerate(lines):
        if "|" in line or "\t" in line:
            table_start = i
            break

    table_lines = lines[table_start:]

    if len(table_lines) <= max_rows:
        return "\n".join(table_lines)

    preview_lines = table_lines[:max_rows]
    return "\n".join(preview_lines) + f"\n... (+ {len(table_lines) - max_rows} more rows)"


def display_document_metadata(chunks: list[KnowledgeChunk]) -> None:
    """Display document metadata from first chunk."""
    if not chunks:
        console.print("[red]No chunks generated[/red]")
        return

    first = chunks[0]

    # Create metadata panel
    metadata_text = Text()
    metadata_text.append("Title: ", style="bold")
    metadata_text.append(f"{first.document_title}\n")
    metadata_text.append("Type: ", style="bold")
    metadata_text.append(f"{first.document_type}\n")
    metadata_text.append("Document ID: ", style="bold")
    metadata_text.append(f"{first.document_id}\n")

    console.print(Panel(metadata_text, title="Document Metadata", border_style="blue"))


def display_chunk_statistics(chunks: list[KnowledgeChunk]) -> None:
    """Display chunk statistics."""
    token_stats = format_token_stats(chunks)
    type_counts = count_by_type(chunks)
    normative_count, informative_count = count_normative(chunks)

    # Summary table
    table = Table(title="Chunk Statistics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Chunks", str(len(chunks)))
    table.add_row("Token Count (min)", str(token_stats["min"]))
    table.add_row("Token Count (max)", str(token_stats["max"]))
    table.add_row("Token Count (avg)", str(token_stats["avg"]))
    table.add_row("Token Count (std)", str(token_stats["std"]))
    table.add_row("Total Tokens", str(token_stats["total"]))
    table.add_row("", "")
    table.add_row("Normative Chunks", str(normative_count))
    table.add_row("Informative Chunks", str(informative_count))

    console.print(table)

    # Type breakdown
    type_table = Table(title="Chunks by Type", show_header=True)
    type_table.add_column("Type", style="cyan")
    type_table.add_column("Count", style="green")

    for chunk_type, count in sorted(type_counts.items()):
        type_table.add_row(chunk_type, str(count))

    console.print(type_table)


def display_table_chunks(chunks: list[KnowledgeChunk]) -> None:
    """Display table chunks with integrity check."""
    table_chunks = [c for c in chunks if c.chunk_type == "table"]

    if not table_chunks:
        console.print("[yellow]No table chunks found[/yellow]")
        return

    console.print(f"\n[bold blue]Table Chunks ({len(table_chunks)} total)[/bold blue]\n")

    for i, chunk in enumerate(table_chunks, 1):
        # Check table integrity
        preview = format_table_preview(chunk.content)

        # Build info text
        info = Text()
        info.append(f"Chunk ID: ", style="bold")
        info.append(f"{chunk.id[:8]}...\n")
        info.append(f"Page(s): ", style="bold")
        info.append(f"{chunk.page_numbers if chunk.page_numbers else 'N/A'}\n")
        info.append(f"Section: ", style="bold")
        info.append(f"{' > '.join(chunk.section_hierarchy) if chunk.section_hierarchy else 'N/A'}\n")
        info.append(f"Clause: ", style="bold")
        info.append(f"{chunk.clause_number or 'N/A'}\n")
        info.append(f"Tokens: ", style="bold")
        info.append(f"{chunk.token_count}\n")
        info.append(f"\nTable Preview:\n", style="bold")
        info.append(preview, style="dim")

        console.print(Panel(info, title=f"Table {i}", border_style="green"))


def display_sample_text_chunks(chunks: list[KnowledgeChunk], num_samples: int = 3) -> None:
    """Display sample text chunks for inspection."""
    text_chunks = [c for c in chunks if c.chunk_type in ("text", "content")]

    if not text_chunks:
        console.print("[yellow]No text chunks found[/yellow]")
        return

    samples = text_chunks[:num_samples]
    console.print(f"\n[bold blue]Sample Text Chunks ({num_samples} of {len(text_chunks)})[/bold blue]\n")

    for i, chunk in enumerate(samples, 1):
        # Build info text
        info = Text()
        info.append(f"Chunk ID: ", style="bold")
        info.append(f"{chunk.id[:8]}...\n")
        info.append(f"Section Hierarchy: ", style="bold")
        info.append(f"{chunk.section_hierarchy if chunk.section_hierarchy else 'N/A'}\n")
        info.append(f"Clause Number: ", style="bold")
        info.append(f"{chunk.clause_number or 'N/A'}\n")
        info.append(f"Normative: ", style="bold")

        if chunk.normative:
            info.append("Yes", style="green bold")
        else:
            info.append("No", style="yellow")

        info.append(f"\nPage(s): ", style="bold")
        info.append(f"{chunk.page_numbers if chunk.page_numbers else 'N/A'}\n")
        info.append(f"Tokens: ", style="bold")
        info.append(f"{chunk.token_count}\n")

        # Check for overlap indicator
        has_overlap = "---" in chunk.content[:100]
        info.append(f"Has Overlap: ", style="bold")
        info.append("Yes\n" if has_overlap else "No\n")

        info.append(f"\nContent Preview (first 200 chars):\n", style="bold")
        preview = chunk.content[:200]
        if len(chunk.content) > 200:
            preview += "..."
        info.append(preview, style="dim")

        console.print(Panel(info, title=f"Text Chunk {i}", border_style="cyan"))


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Check file exists
    if not args.document_path.exists():
        console.print(f"[red]Error: File not found: {args.document_path}[/red]")
        return 1

    # Check file extension
    supported = [".pdf", ".docx"]
    if args.document_path.suffix.lower() not in supported:
        console.print(
            f"[red]Error: Unsupported file type '{args.document_path.suffix}'. "
            f"Supported: {', '.join(supported)}[/red]"
        )
        return 1

    console.print(f"\n[bold]Validating: {args.document_path}[/bold]\n")

    # Run ingestion
    try:
        console.print("[dim]Running ingestion pipeline...[/dim]")
        pipeline = IngestionPipeline()
        chunks = pipeline.ingest(args.document_path)
        console.print(f"[green]Success: Generated {len(chunks)} chunks[/green]\n")
    except Exception as e:
        console.print(f"[red]Error during ingestion: {e}[/red]")
        return 1

    # Display results
    display_document_metadata(chunks)
    display_chunk_statistics(chunks)
    display_table_chunks(chunks)

    if args.verbose and not args.tables_only:
        display_sample_text_chunks(chunks)

    # Summary
    console.print("\n[bold]Validation Checklist:[/bold]")
    console.print("  [ ] Document metadata is correctly extracted")
    console.print("  [ ] Chunks have reasonable token counts (most 300-600, none over 1000)")
    console.print("  [ ] Section hierarchy shows clause numbers")
    console.print("  [ ] Tables show with column headers intact")
    console.print("  [ ] No table appears to be split mid-row")
    console.print("  [ ] Normative chunks correctly identified (contain SHALL/MUST)")
    console.print("  [ ] Page numbers are present\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
