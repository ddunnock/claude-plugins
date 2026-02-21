#!/usr/bin/env python3
"""Detect available research tools (WebSearch, crawl4ai, MCP).

Probes for various research tools and reports availability by tier.
Results are stored in state.json for research agents to adapt strategy.

Adapted from concept-dev check_tools.py for requirements-dev context.
"""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from shared_io import _atomic_write, _validate_path


# Tool definitions by tier
TOOL_TIERS = {
    "always": {
        "WebSearch": "Built-in web search",
        "WebFetch": "Built-in URL fetching",
    },
    "python_packages": {
        "crawl4ai": "Deep web crawling (Python package)",
    },
    "tier1": {
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


def detect_python_package(package_name: str) -> dict:
    """Check if a Python package is importable, including in pipx venvs.

    Returns:
        dict with 'available' (bool) and 'python' (str path to interpreter)
    """
    # Try system Python first
    try:
        result = subprocess.run(
            ["python3", "-c", f"import {package_name}"],
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"available": True, "python": "python3"}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Try pipx venv
    pipx_python = (
        Path.home()
        / ".local"
        / "pipx"
        / "venvs"
        / package_name
        / "bin"
        / "python3"
    )
    if pipx_python.exists():
        try:
            result = subprocess.run(
                [str(pipx_python), "-c", f"import {package_name}"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return {"available": True, "python": str(pipx_python)}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return {"available": False, "python": None}


def check_tools(state_path: Optional[str] = None) -> dict:
    """Report tool tier definitions and detect Python packages.

    Python package detection (crawl4ai) happens here via import check.
    MCP tool detection happens at runtime within Claude via ToolSearch.

    Args:
        state_path: Optional path to state.json to update

    Returns:
        Tool availability report
    """
    # Detect Python packages
    python_results = {}
    for pkg in TOOL_TIERS["python_packages"]:
        python_results[pkg] = detect_python_package(pkg)

    report = {
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "always_available": list(TOOL_TIERS["always"].keys()),
        "python_packages": python_results,
        "tier1_tools": TOOL_TIERS["tier1"],
        "tier2_tools": TOOL_TIERS["tier2"],
        "tier3_tools": TOOL_TIERS["tier3"],
    }

    if state_path:
        path = Path(state_path)
        if path.exists():
            with open(path) as f:
                state = json.load(f)
            # Create tools key if absent (requirements-dev template doesn't include it)
            if "tools" not in state:
                state["tools"] = {}
            state["tools"]["detected_at"] = report["detected_at"]
            # Record detected Python packages as available tools
            detected = list(TOOL_TIERS["always"].keys())
            for pkg, info in python_results.items():
                if info["available"]:
                    detected.append(pkg)
            state["tools"]["available"] = detected
            state["tools"]["python_packages"] = python_results
            _atomic_write(state_path, state)

    return report


# Tier display labels and status icons
_TIER_DISPLAY = [
    ("always", "ALWAYS AVAILABLE", "+"),
    ("python_packages", "PYTHON PACKAGES (detected via import)", "?"),
    ("tier1", "TIER 1 (Free MCP tools -- detect at init)", "?"),
    ("tier2", "TIER 2 (Configurable)", "?"),
    ("tier3", "TIER 3 (Premium, optional)", "?"),
]


def print_report():
    """Print formatted tool availability report."""
    print("=" * 70)
    print("RESEARCH TOOL AVAILABILITY")
    print("=" * 70)

    for tier_key, label, icon in _TIER_DISPLAY:
        print(f"\n{label}:")
        for tool, tool_desc in TOOL_TIERS[tier_key].items():
            if tier_key == "python_packages":
                info = detect_python_package(tool)
                status = "+" if info["available"] else "-"
                via = f" (via {info['python']})" if info["available"] else ""
                print(f"  [{status}] {tool} -- {tool_desc}{via}")
            else:
                print(f"  [{icon}] {tool} -- {tool_desc}")

    print("\n" + "=" * 70)
    print("Run /reqdev:init to detect which MCP tools are available.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Check available research tools")
    parser.add_argument("--state", help="Path to state.json to update")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.state:
        args.state = _validate_path(args.state, allowed_extensions=[".json"])
    report = check_tools(args.state)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report()


if __name__ == "__main__":
    main()
