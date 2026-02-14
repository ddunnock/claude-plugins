#!/usr/bin/env python3
"""
Detect available MCP research tools for concept development.

Probes for various research tools and reports availability by tier.
Results are stored in state.json for research agents to adapt strategy.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional


# Tool definitions by tier
TOOL_TIERS = {
    "always": {
        "WebSearch": "Built-in web search",
        "WebFetch": "Built-in URL fetching",
    },
    "tier1": {
        "mcp__crawl4ai": "crawl4ai deep web crawling",
        "mcp__jina": "Jina Reader document parsing",
        "mcp__paper_search": "Academic paper search",
        "mcp__fetch": "MCP fetch tool",
    },
    "tier2": {
        "mcp__tavily": "Tavily AI search",
        "mcp__semantic_scholar": "Semantic Scholar API",
        "mcp__context7": "Context7 documentation search",
    },
    "tier3": {
        "mcp__exa": "Exa neural search",
        "mcp__perplexity": "Perplexity Sonar",
    },
}


def check_tools(state_path: Optional[str] = None) -> dict:
    """
    Report tool tier definitions for display.

    Actual MCP tool detection happens at runtime within Claude.
    This script provides the tier structure for the init command to display.

    Args:
        state_path: Optional path to state.json to update

    Returns:
        Tool availability report
    """
    report = {
        "detected_at": datetime.now().isoformat(),
        "always_available": list(TOOL_TIERS["always"].keys()),
        "tier1_tools": TOOL_TIERS["tier1"],
        "tier2_tools": TOOL_TIERS["tier2"],
        "tier3_tools": TOOL_TIERS["tier3"],
        "note": "MCP tool detection occurs at runtime. Use /concept:init to probe availability."
    }

    if state_path:
        path = Path(state_path)
        if path.exists():
            with open(path, "r") as f:
                state = json.load(f)
            state["tools"]["detected_at"] = report["detected_at"]
            with open(path, "w") as f:
                json.dump(state, f, indent=2)

    return report


# Tier display labels and status icons
_TIER_DISPLAY = [
    ("always", "ALWAYS AVAILABLE", "+"),
    ("tier1",  "TIER 1 (Free MCP tools -- detect at init)", "?"),
    ("tier2",  "TIER 2 (Configurable)", "?"),
    ("tier3",  "TIER 3 (Premium, optional)", "?"),
]


def print_report():
    """Print formatted tool availability report."""
    print("=" * 70)
    print("RESEARCH TOOL AVAILABILITY")
    print("=" * 70)

    for tier_key, label, icon in _TIER_DISPLAY:
        print(f"\n{label}:")
        for tool, desc in TOOL_TIERS[tier_key].items():
            print(f"  [{icon}] {tool} -- {desc}")

    print("\n" + "=" * 70)
    print("Run /concept:init to detect which MCP tools are available.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Check available research tools")
    parser.add_argument("--state", help="Path to state.json to update")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    report = check_tools(args.state)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report()


if __name__ == "__main__":
    main()
