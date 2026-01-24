"""CLI command for token usage summary."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from knowledge_mcp.monitoring.token_tracker import TokenTracker

if TYPE_CHECKING:
    pass


def token_summary_command(
    log_file: Path | None = None,
    days: int = 7,
    weekly_budget: float = 10.0,
) -> None:
    """
    Display token usage and cost summary.

    Args:
        log_file: Path to token usage log (default: data/token_usage.json).
        days: Number of days to display.
        weekly_budget: Weekly budget in USD for warning threshold.
    """
    log_file = log_file or Path("data/token_usage.json")
    console = Console()

    if not log_file.exists():
        console.print("[yellow]No token usage data found.[/yellow]")
        console.print(f"Expected file: {log_file}")
        return

    tracker = TokenTracker(log_file)

    # Create summary table
    table = Table(title=f"Token Usage (Last {days} Days)")
    table.add_column("Date", style="cyan")
    table.add_column("Requests", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Cache Hits", justify="right", style="green")
    table.add_column("Cost (USD)", justify="right", style="yellow")

    total_cost = 0.0
    total_tokens = 0
    total_cache_hits = 0

    for i in range(days):
        day = str(date.today() - timedelta(days=i))
        summary = tracker.get_daily_summary(day)

        if summary:
            cost = tracker.estimate_cost(day)
            total_cost += cost
            total_tokens += summary.get("embedding_tokens", 0)
            total_cache_hits += summary.get("cache_hits", 0)

            table.add_row(
                day,
                str(summary.get("embedding_requests", 0)),
                f"{summary.get('embedding_tokens', 0):,}",
                str(summary.get("cache_hits", 0)),
                f"${cost:.4f}",
            )

    console.print(table)
    console.print()
    console.print(f"[bold]Total Cost ({days} days):[/bold] ${total_cost:.4f}")
    console.print(f"[bold]Total Tokens:[/bold] {total_tokens:,}")
    console.print(f"[bold]Total Cache Hits:[/bold] {total_cache_hits:,}")

    if total_tokens > 0:
        cache_hit_rate = total_cache_hits / (total_cache_hits + total_tokens / 100) * 100
        console.print(f"[bold]Cache Efficiency:[/bold] ~{cache_hit_rate:.1f}%")

    # Warn if approaching budget
    if total_cost > weekly_budget * 0.8:
        console.print(
            f"\n[yellow]Warning: Approaching weekly budget (${weekly_budget:.2f})[/yellow]"
        )


def main() -> None:
    """Entry point for CLI command."""
    import argparse

    parser = argparse.ArgumentParser(description="Token usage summary")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Path to token usage log",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to display",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=10.0,
        help="Weekly budget in USD",
    )

    args = parser.parse_args()
    token_summary_command(args.log_file, args.days, args.budget)


if __name__ == "__main__":
    main()
