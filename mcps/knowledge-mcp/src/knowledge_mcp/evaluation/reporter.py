"""CLI reporting for evaluation results."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from knowledge_mcp.evaluation.golden_set import GoldenTestResult


def print_evaluation_summary(results: dict[str, float], threshold: float = 0.8) -> None:
    """
    Print formatted RAG evaluation summary to terminal.

    Args:
        results: Dict with metric names and scores.
        threshold: Pass threshold for status display.
    """
    console = Console()

    # RAG metrics table
    table = Table(title="RAG Evaluation Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Status", justify="center")

    for metric, score in results.items():
        if isinstance(score, (int, float)):
            status = "[green]PASS[/green]" if score >= threshold else "[red]FAIL[/red]"
            table.add_row(
                metric.replace("_", " ").title(),
                f"{score:.2%}" if score <= 1.0 else str(score),
                status,
            )

    console.print(table)

    # Warning if any metric below threshold
    failed = [m for m, s in results.items() if isinstance(s, float) and s < threshold]
    if failed:
        console.print(
            f"\n[bold red]WARNING: {len(failed)} metric(s) below {threshold:.0%} threshold[/bold red]"
        )


def print_golden_results(
    results: list[GoldenTestResult],
    summary: dict[str, float | int],
    verbose: bool = False,
) -> None:
    """
    Print golden test results to terminal.

    Args:
        results: List of test results.
        summary: Summary statistics.
        verbose: Whether to show individual test details.
    """
    console = Console()

    # Summary table
    summary_table = Table(title="Golden Test Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", justify="right")

    summary_table.add_row("Total Tests", str(summary["total"]))
    summary_table.add_row("Passed", f"[green]{summary['passed']}[/green]")
    summary_table.add_row("Failed", f"[red]{summary['failed']}[/red]")
    summary_table.add_row("Pass Rate", f"{summary['pass_rate']:.1%}")
    summary_table.add_row("Avg Recall@k", f"{summary['avg_recall']:.2%}")

    console.print(summary_table)

    # Verbose: show all results
    if verbose:
        console.print("\n[bold]Individual Test Results:[/bold]\n")

        details_table = Table()
        details_table.add_column("Query", max_width=50)
        details_table.add_column("Recall", justify="right")
        details_table.add_column("Status", justify="center")

        for result in results:
            status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
            query_short = result.query[:47] + "..." if len(result.query) > 50 else result.query
            details_table.add_row(
                query_short,
                f"{result.recall:.0%}",
                status,
            )

        console.print(details_table)

    # Show failing tests
    failed = [r for r in results if not r.passed]
    if failed and not verbose:
        console.print(f"\n[yellow]Failing tests ({len(failed)}):[/yellow]")
        for r in failed[:5]:  # Show first 5
            console.print(f"  - {r.query[:60]}...")
        if len(failed) > 5:
            console.print(f"  ... and {len(failed) - 5} more")

    # Overall status
    if summary["pass_rate"] >= 0.8:
        console.print("\n[bold green]EVALUATION PASSED[/bold green]")
    else:
        console.print("\n[bold red]EVALUATION FAILED[/bold red]")
