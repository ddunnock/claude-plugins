#!/usr/bin/env python3
"""
Problem Definition Report Generator

Generates formatted 5W2H and IS/IS NOT reports from problem definition data.
Outputs HTML or Markdown reports suitable for documentation.

Usage:
    python generate_report.py --file definition.json --format html
    python generate_report.py --file definition.json --format markdown
    python generate_report.py --interactive
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from pathlib import Path


@dataclass
class ProblemDefinition:
    """Complete problem definition data structure."""
    # Metadata
    title: str = ""
    created_date: str = ""
    created_by: str = ""

    # 5W2H Analysis
    what_object: str = ""
    what_defect: str = ""
    where_geographic: str = ""
    where_on_object: str = ""
    when_calendar: str = ""
    when_lifecycle: str = ""
    who_affected: str = ""
    how_detected: str = ""
    how_much_magnitude: str = ""
    how_much_frequency: str = ""

    # IS / IS NOT Analysis
    is_what: str = ""
    is_not_what: str = ""
    is_where: str = ""
    is_not_where: str = ""
    is_when: str = ""
    is_not_when: str = ""
    is_who: str = ""
    is_not_who: str = ""

    # Deviation statement
    expected_condition: str = ""
    actual_condition: str = ""

    # Final problem statement
    problem_statement: str = ""

    # Quality assessment
    score: Optional[float] = None
    rating: str = ""


def load_definition(filepath: str) -> ProblemDefinition:
    """Load problem definition from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return ProblemDefinition(**{k: v for k, v in data.items() if k in ProblemDefinition.__dataclass_fields__})


def generate_html_report(definition: ProblemDefinition) -> str:
    """Generate HTML report from problem definition."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Problem Definition Report - {definition.title or 'Untitled'}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #0066cc; margin-top: 30px; }}
        h3 {{ color: #444; margin-top: 20px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: 600;
            width: 30%;
        }}
        .is-is-not th {{ width: 20%; }}
        .is-is-not td {{ width: 40%; }}
        .is-column {{ background-color: #e8f5e9; }}
        .is-not-column {{ background-color: #ffebee; }}
        .statement-box {{
            background-color: #e3f2fd;
            border-left: 4px solid #1976d2;
            padding: 15px 20px;
            margin: 20px 0;
            font-size: 1.1em;
        }}
        .deviation-box {{
            background-color: #fff3e0;
            border-left: 4px solid #f57c00;
            padding: 15px 20px;
            margin: 20px 0;
        }}
        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .score-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .score-excellent {{ background-color: #4caf50; color: white; }}
        .score-good {{ background-color: #8bc34a; color: white; }}
        .score-acceptable {{ background-color: #ffc107; color: black; }}
        .score-marginal {{ background-color: #ff9800; color: white; }}
        .score-inadequate {{ background-color: #f44336; color: white; }}
    </style>
</head>
<body>
    <h1>Problem Definition Report</h1>

    <div class="metadata">
        <p><strong>Title:</strong> {definition.title or 'N/A'}</p>
        <p><strong>Date:</strong> {definition.created_date or datetime.now().strftime('%Y-%m-%d')}</p>
        <p><strong>Created By:</strong> {definition.created_by or 'N/A'}</p>
        {f'<p><strong>Quality Score:</strong> {definition.score}/100 <span class="score-badge score-{definition.rating.lower()}">{definition.rating}</span></p>' if definition.score else ''}
    </div>

    <h2>5W2H Analysis</h2>
    <table>
        <tr>
            <th>Dimension</th>
            <th>Finding</th>
        </tr>
        <tr>
            <th>WHAT (Object)</th>
            <td>{definition.what_object or '—'}</td>
        </tr>
        <tr>
            <th>WHAT (Defect)</th>
            <td>{definition.what_defect or '—'}</td>
        </tr>
        <tr>
            <th>WHERE (Geographic)</th>
            <td>{definition.where_geographic or '—'}</td>
        </tr>
        <tr>
            <th>WHERE (On Object)</th>
            <td>{definition.where_on_object or '—'}</td>
        </tr>
        <tr>
            <th>WHEN (Calendar)</th>
            <td>{definition.when_calendar or '—'}</td>
        </tr>
        <tr>
            <th>WHEN (Lifecycle)</th>
            <td>{definition.when_lifecycle or '—'}</td>
        </tr>
        <tr>
            <th>WHO (Affected)</th>
            <td>{definition.who_affected or '—'}</td>
        </tr>
        <tr>
            <th>HOW (Detected)</th>
            <td>{definition.how_detected or '—'}</td>
        </tr>
        <tr>
            <th>HOW MUCH (Magnitude)</th>
            <td>{definition.how_much_magnitude or '—'}</td>
        </tr>
        <tr>
            <th>HOW MUCH (Frequency)</th>
            <td>{definition.how_much_frequency or '—'}</td>
        </tr>
    </table>

    <h2>IS / IS NOT Analysis</h2>
    <table class="is-is-not">
        <tr>
            <th>Dimension</th>
            <th class="is-column">IS</th>
            <th class="is-not-column">IS NOT</th>
        </tr>
        <tr>
            <th>WHAT</th>
            <td class="is-column">{definition.is_what or '—'}</td>
            <td class="is-not-column">{definition.is_not_what or '—'}</td>
        </tr>
        <tr>
            <th>WHERE</th>
            <td class="is-column">{definition.is_where or '—'}</td>
            <td class="is-not-column">{definition.is_not_where or '—'}</td>
        </tr>
        <tr>
            <th>WHEN</th>
            <td class="is-column">{definition.is_when or '—'}</td>
            <td class="is-not-column">{definition.is_not_when or '—'}</td>
        </tr>
        <tr>
            <th>WHO</th>
            <td class="is-column">{definition.is_who or '—'}</td>
            <td class="is-not-column">{definition.is_not_who or '—'}</td>
        </tr>
    </table>

    <h2>Deviation Statement</h2>
    <div class="deviation-box">
        <p><strong>Expected:</strong> {definition.expected_condition or '—'}</p>
        <p><strong>Actual:</strong> {definition.actual_condition or '—'}</p>
    </div>

    <h2>Problem Statement</h2>
    <div class="statement-box">
        {definition.problem_statement or '<em>Problem statement not yet defined</em>'}
    </div>

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em;">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Problem Definition Skill
    </footer>
</body>
</html>
"""
    return html


def generate_markdown_report(definition: ProblemDefinition) -> str:
    """Generate Markdown report from problem definition."""
    score_section = ""
    if definition.score:
        score_section = f"**Quality Score:** {definition.score}/100 ({definition.rating})\n"

    md = f"""# Problem Definition Report

**Title:** {definition.title or 'N/A'}
**Date:** {definition.created_date or datetime.now().strftime('%Y-%m-%d')}
**Created By:** {definition.created_by or 'N/A'}
{score_section}
---

## 5W2H Analysis

| Dimension | Finding |
|-----------|---------|
| WHAT (Object) | {definition.what_object or '—'} |
| WHAT (Defect) | {definition.what_defect or '—'} |
| WHERE (Geographic) | {definition.where_geographic or '—'} |
| WHERE (On Object) | {definition.where_on_object or '—'} |
| WHEN (Calendar) | {definition.when_calendar or '—'} |
| WHEN (Lifecycle) | {definition.when_lifecycle or '—'} |
| WHO (Affected) | {definition.who_affected or '—'} |
| HOW (Detected) | {definition.how_detected or '—'} |
| HOW MUCH (Magnitude) | {definition.how_much_magnitude or '—'} |
| HOW MUCH (Frequency) | {definition.how_much_frequency or '—'} |

---

## IS / IS NOT Analysis

| Dimension | IS | IS NOT |
|-----------|-------|--------|
| WHAT | {definition.is_what or '—'} | {definition.is_not_what or '—'} |
| WHERE | {definition.is_where or '—'} | {definition.is_not_where or '—'} |
| WHEN | {definition.is_when or '—'} | {definition.is_not_when or '—'} |
| WHO | {definition.is_who or '—'} | {definition.is_not_who or '—'} |

---

## Deviation Statement

> **Expected:** {definition.expected_condition or '—'}
>
> **Actual:** {definition.actual_condition or '—'}

---

## Problem Statement

> {definition.problem_statement or '*Problem statement not yet defined*'}

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Problem Definition Skill*
"""
    return md


def interactive_create() -> ProblemDefinition:
    """Create problem definition interactively."""
    print("\nPROBLEM DEFINITION GENERATOR")
    print("=" * 50)
    print("Enter information for each dimension (press Enter to skip)\n")

    definition = ProblemDefinition()

    # Metadata
    definition.title = input("Problem title: ").strip()
    definition.created_by = input("Created by: ").strip()
    definition.created_date = datetime.now().strftime('%Y-%m-%d')

    # 5W2H
    print("\n--- 5W2H ANALYSIS ---\n")
    definition.what_object = input("WHAT object/product is affected? ").strip()
    definition.what_defect = input("WHAT defect/failure is observed? ").strip()
    definition.where_geographic = input("WHERE geographically does it occur? ").strip()
    definition.where_on_object = input("WHERE on the object is it located? ").strip()
    definition.when_calendar = input("WHEN did it first occur (date/time)? ").strip()
    definition.when_lifecycle = input("WHEN in the lifecycle does it occur? ").strip()
    definition.who_affected = input("WHO is affected? ").strip()
    definition.how_detected = input("HOW was it detected? ").strip()
    definition.how_much_magnitude = input("HOW MUCH (magnitude/extent)? ").strip()
    definition.how_much_frequency = input("HOW MUCH (frequency/trend)? ").strip()

    # IS / IS NOT
    print("\n--- IS / IS NOT ANALYSIS ---\n")
    definition.is_what = input("WHAT IS the problem (specifically)? ").strip()
    definition.is_not_what = input("WHAT IS NOT the problem (but could be)? ").strip()
    definition.is_where = input("WHERE IS it occurring? ").strip()
    definition.is_not_where = input("WHERE IS it NOT occurring? ").strip()
    definition.is_when = input("WHEN IS it occurring? ").strip()
    definition.is_not_when = input("WHEN IS it NOT occurring? ").strip()
    definition.is_who = input("WHO IS affected? ").strip()
    definition.is_not_who = input("WHO IS NOT affected? ").strip()

    # Deviation
    print("\n--- DEVIATION STATEMENT ---\n")
    definition.expected_condition = input("Expected condition: ").strip()
    definition.actual_condition = input("Actual condition: ").strip()

    # Problem statement
    print("\n--- PROBLEM STATEMENT ---\n")
    definition.problem_statement = input("Final problem statement: ").strip()

    return definition




def _validate_path(filepath: str, allowed_extensions: set, label: str) -> None:
    """Validate file path: reject traversal and restrict extensions."""
    if ".." in filepath:
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = Path(filepath).suffix.lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Problem Definition Report"
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="Input JSON file with problem definition",
    )
    parser.add_argument(
        "--format",
        choices=["html", "markdown", "md"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Create definition interactively",
    )

    args = parser.parse_args()

    if args.file:
        _validate_path(args.file, {'.json'}, "input file")
    if args.output:
        _validate_path(args.output, {'.htm', '.md', '.html'}, "output file")

    # Get definition from input source
    if args.file:
        try:
            definition = load_definition(args.file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.interactive:
        definition = interactive_create()
    else:
        print("Error: Please provide --file or use --interactive mode", file=sys.stderr)
        sys.exit(1)

    # Generate report
    if args.format == "html":
        report = generate_html_report(definition)
    else:
        report = generate_markdown_report(definition)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
