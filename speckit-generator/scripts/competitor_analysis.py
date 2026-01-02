#!/usr/bin/env python3
"""
competitor_analysis.py - Analyze existing solutions in a domain

Usage: python competitor_analysis.py "<domain>" [--output-format json|markdown]

This script provides a structured template for competitor analysis.
It prompts for manual research since web search requires external tools.

Inputs:
  - domain: The project domain to analyze (e.g., "LSP implementation", "CI/CD")
  - --output-format: Output format (json or markdown, default: markdown)
  - --output: Output file path (optional, defaults to stdout)

Outputs:
  - Structured competitor analysis template

Exit Codes:
  - 0: Success
  - 1: Error
"""

import argparse
import json
import sys
from datetime import datetime

def create_analysis_template(domain: str) -> dict:
    """Create a structured competitor analysis template."""
    return {
        "domain": domain,
        "analysis_date": datetime.now().isoformat(),
        "status": "TEMPLATE",
        "search_queries": [
            f'"{domain}" open source tools',
            f'"{domain}" CLI',
            f'"{domain}" automation',
            f'"{domain}" SDK library',
            f'"{domain}" best practices',
        ],
        "search_sources": [
            {"name": "GitHub", "url": "https://github.com/search", "status": "TBD"},
            {"name": "NPM", "url": "https://www.npmjs.com/search", "status": "TBD"},
            {"name": "PyPI", "url": "https://pypi.org/search", "status": "TBD"},
            {"name": "Awesome Lists", "url": "https://github.com/topics/awesome", "status": "TBD"},
        ],
        "competitors": [
            {
                "name": "[COMPETITOR_NAME]",
                "url": "[URL]",
                "description": "[DESCRIPTION]",
                "strengths": ["[STRENGTH_1]", "[STRENGTH_2]"],
                "gaps": ["[GAP_1]", "[GAP_2]"],
                "relevance": "[HIGH/MEDIUM/LOW]",
                "evidence_status": "[VERIFIED/ASSUMPTION]",
                "last_verified": "[DATE]"
            }
        ],
        "standards_references": [
            {
                "name": "[STANDARD_NAME]",
                "organization": "[ORG]",
                "url": "[URL]",
                "relevance": "[WHY_RELEVANT]",
                "evidence_status": "[VERIFIED/ASSUMPTION]"
            }
        ],
        "design_implications": {
            "adopt_from_existing": ["[PATTERN_1]", "[PATTERN_2]"],
            "gaps_to_fill": ["[GAP_1]", "[GAP_2]"],
            "differentiation": ["[UNIQUE_VALUE_1]", "[UNIQUE_VALUE_2]"]
        },
        "assumptions": [
            {
                "id": "CA-001",
                "statement": "[ASSUMPTION]",
                "rationale": "[WHY_ASSUMED]",
                "validation_approach": "[HOW_TO_VERIFY]",
                "risk_if_wrong": "[IMPACT]"
            }
        ],
        "instructions": {
            "step_1": "Execute the search queries above using web search",
            "step_2": "Document each competitor found in the competitors array",
            "step_3": "Mark evidence_status as VERIFIED for confirmed facts",
            "step_4": "Mark evidence_status as ASSUMPTION for inferences",
            "step_5": "Update design_implications based on findings",
            "step_6": "Log any assumptions made during analysis"
        }
    }


def format_as_markdown(data: dict) -> str:
    """Convert analysis data to markdown format."""
    lines = [
        f"# Competitor Analysis: {data['domain']}",
        "",
        f"**Analysis Date**: {data['analysis_date']}",
        f"**Status**: {data['status']}",
        "",
        "## Search Strategy",
        "",
        "### Recommended Search Queries",
        ""
    ]
    
    for query in data['search_queries']:
        lines.append(f"- `{query}`")
    
    lines.extend([
        "",
        "### Search Sources",
        "",
        "| Source | URL | Status |",
        "|--------|-----|--------|"
    ])
    
    for source in data['search_sources']:
        lines.append(f"| {source['name']} | {source['url']} | {source['status']} |")
    
    lines.extend([
        "",
        "## Existing Solutions",
        "",
        "### Competitors",
        ""
    ])
    
    for comp in data['competitors']:
        lines.extend([
            f"#### {comp['name']}",
            "",
            f"- **URL**: {comp['url']}",
            f"- **Description**: {comp['description']}",
            f"- **Relevance**: {comp['relevance']}",
            f"- **Evidence Status**: {comp['evidence_status']}",
            "",
            "**Strengths**:",
            ""
        ])
        for s in comp['strengths']:
            lines.append(f"- {s}")
        lines.extend([
            "",
            "**Gaps**:",
            ""
        ])
        for g in comp['gaps']:
            lines.append(f"- {g}")
        lines.append("")
    
    lines.extend([
        "## Standards & References",
        "",
        "| Standard | Organization | Relevance | Status |",
        "|----------|--------------|-----------|--------|"
    ])
    
    for std in data['standards_references']:
        lines.append(f"| {std['name']} | {std['organization']} | {std['relevance']} | {std['evidence_status']} |")
    
    lines.extend([
        "",
        "## Design Implications",
        "",
        "### Patterns to Adopt",
        ""
    ])
    
    for pattern in data['design_implications']['adopt_from_existing']:
        lines.append(f"- {pattern}")
    
    lines.extend([
        "",
        "### Gaps to Fill",
        ""
    ])
    
    for gap in data['design_implications']['gaps_to_fill']:
        lines.append(f"- {gap}")
    
    lines.extend([
        "",
        "### Differentiation Opportunities",
        ""
    ])
    
    for diff in data['design_implications']['differentiation']:
        lines.append(f"- {diff}")
    
    lines.extend([
        "",
        "## Assumptions Log",
        "",
        "| ID | Assumption | Rationale | Validation | Risk |",
        "|----|------------|-----------|------------|------|"
    ])
    
    for assumption in data['assumptions']:
        lines.append(
            f"| {assumption['id']} | {assumption['statement']} | "
            f"{assumption['rationale']} | {assumption['validation_approach']} | "
            f"{assumption['risk_if_wrong']} |"
        )
    
    lines.extend([
        "",
        "## Next Steps",
        ""
    ])
    
    for step, instruction in data['instructions'].items():
        lines.append(f"1. {instruction}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate competitor analysis template for a domain"
    )
    parser.add_argument(
        "domain",
        help="The project domain to analyze"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Shortcut for --output-format json"
    )
    
    args = parser.parse_args()
    
    # Handle --json shortcut
    output_format = "json" if args.json else args.output_format
    
    try:
        analysis = create_analysis_template(args.domain)
        
        if output_format == "json":
            output = json.dumps({
                "success": True,
                "data": analysis
            }, indent=2)
        else:
            output = format_as_markdown(analysis)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(json.dumps({
                "success": True,
                "message": f"Analysis template written to {args.output}"
            }))
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        error_output = json.dumps({
            "success": False,
            "errors": [str(e)]
        })
        print(error_output, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
