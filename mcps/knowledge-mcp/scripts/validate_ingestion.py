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
import re
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
    parser.add_argument(
        "--samples",
        "-n",
        type=int,
        default=3,
        help="Number of sample chunks to show (default: 3)",
    )
    parser.add_argument(
        "--all-tables",
        action="store_true",
        help="Show all table chunks (not just first few)",
    )
    parser.add_argument(
        "--tail",
        "-t",
        type=int,
        default=0,
        help="Show last N chunks (to inspect end of document)",
    )
    parser.add_argument(
        "--page",
        "-p",
        type=int,
        default=0,
        help="Show chunks from specific page number",
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


def count_normative(chunks: list[KnowledgeChunk]) -> tuple[int, int, int]:
    """Count normative vs informative vs unknown chunks."""
    normative = sum(1 for c in chunks if c.normative is True)
    informative = sum(1 for c in chunks if c.normative is False)
    unknown = sum(1 for c in chunks if c.normative is None)
    return normative, informative, unknown


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
    normative_count, informative_count, unknown_count = count_normative(chunks)

    # Collect page coverage
    all_pages: set[int] = set()
    chunks_with_pages = 0
    for chunk in chunks:
        if chunk.page_numbers:
            all_pages.update(chunk.page_numbers)
            chunks_with_pages += 1

    # Find small chunks (under 50 tokens)
    small_chunks = [c for c in chunks if c.token_count < 50]

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
    table.add_row("Small Chunks (<50 tokens)", str(len(small_chunks)))
    table.add_row("", "")
    table.add_row("Normative Chunks", str(normative_count))
    table.add_row("Informative Chunks", str(informative_count))
    table.add_row("Unknown Classification", str(unknown_count))
    table.add_row("", "")
    table.add_row("Chunks with Page Numbers", f"{chunks_with_pages}/{len(chunks)}")
    table.add_row("Page Range", f"{min(all_pages) if all_pages else 'N/A'}-{max(all_pages) if all_pages else 'N/A'}")

    console.print(table)

    # Show small chunk details if any
    if small_chunks:
        console.print(f"\n[yellow]Small chunks found ({len(small_chunks)}):[/yellow]")
        for i, chunk in enumerate(small_chunks[:5], 1):
            preview = chunk.content[:80].replace("\n", " ")
            console.print(f"  {i}. {chunk.token_count} tokens: \"{preview}...\"")
        if len(small_chunks) > 5:
            console.print(f"  ... and {len(small_chunks) - 5} more")

    # Type breakdown
    type_table = Table(title="Chunks by Type", show_header=True)
    type_table.add_column("Type", style="cyan")
    type_table.add_column("Count", style="green")

    for chunk_type, count in sorted(type_counts.items()):
        type_table.add_row(chunk_type, str(count))

    console.print(type_table)


def check_table_integrity(content: str) -> tuple[bool, str]:
    """
    Check if a table appears to have consistent row structure.

    Handles multiple table formats:
    - Markdown tables (pipes |)
    - TSV tables (tabs)
    - Docling format (--- separators with content lines)

    Returns:
        Tuple of (is_intact, message).
    """
    lines = content.strip().split("\n")

    # Check for markdown/TSV format first
    pipe_lines = [ln for ln in lines if "|" in ln]
    tab_lines = [ln for ln in lines if "\t" in ln]

    if pipe_lines:
        # Markdown table format
        col_counts: list[int] = []
        for line in pipe_lines:
            cells = [c for c in line.split("|") if c.strip() or c == ""]
            col_counts.append(len(cells))
        unique = set(col_counts)
        if len(unique) <= 2:
            return True, f"Markdown: {col_counts[0]} columns"
        return False, f"INCONSISTENT: column counts vary: {sorted(unique)}"

    if tab_lines:
        # TSV format
        col_counts = [len(ln.split("\t")) for ln in tab_lines]
        unique = set(col_counts)
        if len(unique) <= 2:
            return True, f"TSV: {col_counts[0]} columns"
        return False, f"INCONSISTENT: column counts vary: {sorted(unique)}"

    # Check for Docling format (--- separators)
    separator_count = sum(1 for ln in lines if ln.strip() == "---")
    content_lines = [ln for ln in lines if ln.strip() and ln.strip() != "---"]

    if separator_count >= 1 and content_lines:
        # Docling extracts table content as text with --- separators
        return True, f"Docling format: {len(content_lines)} content lines, {separator_count} separators"

    if content_lines:
        return True, f"Text format: {len(content_lines)} lines"

    return True, "Empty or minimal content"


def find_potential_tables(chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
    """
    Find chunks that might contain tables but aren't typed as 'table'.

    Looks for patterns like:
    - Multiple lines with consistent column alignment
    - Lines with multiple tab or pipe characters
    - Lines that look like table rows (repeated spacing patterns)
    """
    potential_tables: list[KnowledgeChunk] = []

    for chunk in chunks:
        if chunk.chunk_type == "table":
            continue  # Skip actual table chunks

        lines = chunk.content.strip().split("\n")
        if len(lines) < 2:
            continue

        # Check for patterns that suggest table content
        has_aligned_columns = False
        has_repeated_spacing = False

        # Pattern 1: Multiple lines with similar structure (tabs or multiple spaces)
        tab_lines = sum(1 for ln in lines if "\t" in ln)
        multi_space_lines = sum(1 for ln in lines if "  " in ln and len(ln.split()) > 2)

        if tab_lines >= 2 or multi_space_lines >= 3:
            has_aligned_columns = True

        # Pattern 2: Lines with consistent "cell" patterns (e.g., "Text   Text   Text")
        space_counts = []
        for ln in lines[:10]:  # Check first 10 lines
            # Count sequences of 2+ spaces
            spaces = len(re.findall(r"  +", ln))
            if spaces > 0:
                space_counts.append(spaces)

        if len(space_counts) >= 3:
            # Check if space counts are consistent (table-like)
            avg = sum(space_counts) / len(space_counts)
            if all(abs(c - avg) <= 1 for c in space_counts):
                has_repeated_spacing = True

        if has_aligned_columns or has_repeated_spacing:
            potential_tables.append(chunk)

    return potential_tables


def display_table_chunks(chunks: list[KnowledgeChunk], show_all: bool = False) -> None:
    """Display table chunks with integrity check."""
    table_chunks = [c for c in chunks if c.chunk_type == "table"]

    if not table_chunks:
        console.print("[yellow]No table chunks found (chunk_type='table')[/yellow]")

        # Look for potential tables misclassified as other types
        potential = find_potential_tables(chunks)
        if potential:
            console.print(f"[cyan]Found {len(potential)} chunks with table-like content:[/cyan]")
            for i, chunk in enumerate(potential[:3], 1):
                preview = chunk.content[:150].replace("\n", "\\n")
                console.print(f"  {i}. {chunk.chunk_type} chunk on page {chunk.page_numbers}: \"{preview}...\"")
            if len(potential) > 3:
                console.print(f"  ... and {len(potential) - 3} more")
        return

    display_chunks = table_chunks if show_all else table_chunks[:5]
    shown = len(display_chunks)
    total = len(table_chunks)

    console.print(f"\n[bold blue]Table Chunks ({shown} of {total} shown)[/bold blue]\n")

    for i, chunk in enumerate(display_chunks, 1):
        # Check table integrity
        preview = format_table_preview(chunk.content, max_rows=5)
        is_intact, integrity_msg = check_table_integrity(chunk.content)

        # Count actual rows
        lines = chunk.content.strip().split("\n")
        row_count = len([ln for ln in lines if ln.strip()])

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
        info.append(f"Row Count: ", style="bold")
        info.append(f"{row_count}\n")
        info.append(f"Integrity: ", style="bold")
        if is_intact:
            info.append(integrity_msg, style="green")
        else:
            info.append(integrity_msg, style="red bold")
        info.append(f"\n\nTable Preview:\n", style="bold")
        info.append(preview, style="dim")

        border = "green" if is_intact else "red"
        console.print(Panel(info, title=f"Table {i}", border_style=border))


def display_normative_samples(chunks: list[KnowledgeChunk], num_samples: int = 3) -> None:
    """Display sample normative chunks to verify SHALL/MUST detection."""
    normative_chunks = [c for c in chunks if c.normative]

    if not normative_chunks:
        console.print("[yellow]No normative chunks found[/yellow]")
        return

    console.print(f"\n[bold blue]Normative Chunk Samples ({num_samples} of {len(normative_chunks)})[/bold blue]\n")

    for i, chunk in enumerate(normative_chunks[:num_samples], 1):
        # Find SHALL/MUST keywords in content
        content_upper = chunk.content.upper()
        keywords_found: list[str] = []
        for kw in ["SHALL", "MUST", "REQUIRED"]:
            if kw in content_upper:
                keywords_found.append(kw)

        info = Text()
        info.append(f"Chunk ID: ", style="bold")
        info.append(f"{chunk.id[:8]}...\n")
        info.append(f"Page(s): ", style="bold")
        info.append(f"{chunk.page_numbers if chunk.page_numbers else 'N/A'}\n")
        info.append(f"Tokens: ", style="bold")
        info.append(f"{chunk.token_count}\n")
        info.append(f"Keywords Found: ", style="bold")
        info.append(f"{', '.join(keywords_found) if keywords_found else 'None detected'}\n")
        info.append(f"\nContent Preview:\n", style="bold")

        # Show content around first SHALL/MUST
        preview = chunk.content[:300]
        if len(chunk.content) > 300:
            preview += "..."
        info.append(preview, style="dim")

        console.print(Panel(info, title=f"Normative {i}", border_style="green"))


def display_sample_text_chunks(chunks: list[KnowledgeChunk], num_samples: int = 3) -> None:
    """Display sample text chunks for inspection."""
    # Include heading, list, paragraph, text, content - anything that's not a table
    text_chunks = [c for c in chunks if c.chunk_type not in ("table", "figure")]

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


def display_tail_chunks(chunks: list[KnowledgeChunk], n: int) -> None:
    """Display the last N chunks from the document."""
    tail_chunks = chunks[-n:] if n < len(chunks) else chunks
    console.print(f"\n[bold blue]Last {len(tail_chunks)} Chunks (tail)[/bold blue]\n")

    for i, chunk in enumerate(tail_chunks, len(chunks) - len(tail_chunks) + 1):
        info = Text()
        info.append(f"Index: ", style="bold")
        info.append(f"{i}/{len(chunks)}\n")
        info.append(f"Chunk Type: ", style="bold")
        info.append(f"{chunk.chunk_type}\n")
        info.append(f"Page(s): ", style="bold")
        info.append(f"{chunk.page_numbers if chunk.page_numbers else 'N/A'}\n")
        info.append(f"Tokens: ", style="bold")
        info.append(f"{chunk.token_count}\n")
        info.append(f"Section: ", style="bold")
        section = " > ".join(chunk.section_hierarchy[-3:]) if chunk.section_hierarchy else "N/A"
        info.append(f"...{section}\n")
        info.append(f"\nContent Preview:\n", style="bold")
        preview = chunk.content[:250].replace("\n", "\\n")
        if len(chunk.content) > 250:
            preview += "..."
        info.append(preview, style="dim")

        console.print(Panel(info, title=f"Chunk {i}", border_style="magenta"))


def display_page_chunks(chunks: list[KnowledgeChunk], page: int) -> None:
    """Display all chunks from a specific page."""
    page_chunks = [c for c in chunks if page in c.page_numbers]

    if not page_chunks:
        console.print(f"[yellow]No chunks found on page {page}[/yellow]")
        return

    console.print(f"\n[bold blue]Chunks from Page {page} ({len(page_chunks)} chunks)[/bold blue]\n")

    for i, chunk in enumerate(page_chunks, 1):
        info = Text()
        info.append(f"Chunk Type: ", style="bold")
        info.append(f"{chunk.chunk_type}\n")
        info.append(f"Tokens: ", style="bold")
        info.append(f"{chunk.token_count}\n")
        info.append(f"Normative: ", style="bold")
        if chunk.normative is True:
            info.append("Yes\n", style="green")
        elif chunk.normative is False:
            info.append("Informative\n", style="yellow")
        else:
            info.append("Unknown\n", style="dim")
        info.append(f"\nContent Preview:\n", style="bold")
        preview = chunk.content[:300].replace("\n", "\\n")
        if len(chunk.content) > 300:
            preview += "..."
        info.append(preview, style="dim")

        console.print(Panel(info, title=f"Page {page} - Chunk {i}", border_style="blue"))


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
    display_table_chunks(chunks, show_all=args.all_tables)
    display_normative_samples(chunks, num_samples=args.samples)

    if args.verbose and not args.tables_only:
        display_sample_text_chunks(chunks, num_samples=args.samples)

    # Show tail chunks if requested
    if args.tail > 0:
        display_tail_chunks(chunks, args.tail)

    # Show chunks from specific page if requested
    if args.page > 0:
        display_page_chunks(chunks, args.page)

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
