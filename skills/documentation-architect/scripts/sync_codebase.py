#!/usr/bin/env python3
"""
Codebase Sync Script

Walks the codebase to extract documentation-relevant information
and compares against existing documentation to find discrepancies.

Usage:
    python sync_codebase.py [project_path] [--walkthrough] [--json]

Features:
- Extract module structure and entry points
- Identify public APIs and their signatures
- Detect configuration options
- Find code comments and docstrings
- Compare against existing docs
- Generate sync report
"""

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict


class CodeElement(TypedDict):
    """Represents an extracted code element."""
    type: str  # module, class, function, constant, config
    name: str
    location: str  # file:line
    signature: str | None
    docstring: str | None
    visibility: str  # public, private, internal


class SyncFinding(TypedDict):
    """Represents a discrepancy between code and docs."""
    id: str
    severity: str  # HIGH, MEDIUM, LOW
    category: str  # MISSING, OUTDATED, INCORRECT, UNDOCUMENTED
    code_location: str
    doc_location: str | None
    description: str
    suggestion: str


@dataclass
class CodebaseSnapshot:
    """Point-in-time snapshot of codebase structure."""
    project_path: str
    timestamp: str
    modules: list[CodeElement] = field(default_factory=list)
    classes: list[CodeElement] = field(default_factory=list)
    functions: list[CodeElement] = field(default_factory=list)
    constants: list[CodeElement] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)


@dataclass
class SyncReport:
    """Report comparing code to documentation."""
    findings: list[SyncFinding] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


def extract_python_elements(file_path: Path) -> list[CodeElement]:
    """Extract code elements from a Python file."""
    elements = []

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except Exception:
        return elements

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            visibility = "private" if node.name.startswith("_") else "public"
            elements.append({
                "type": "class",
                "name": node.name,
                "location": f"{file_path}:{node.lineno}",
                "signature": None,
                "docstring": ast.get_docstring(node),
                "visibility": visibility,
            })
        elif isinstance(node, ast.FunctionDef):
            visibility = "private" if node.name.startswith("_") else "public"
            # Build signature
            args = []
            for arg in node.args.args:
                arg_str = arg.arg
                if arg.annotation:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                args.append(arg_str)
            signature = f"({', '.join(args)})"
            if node.returns:
                signature += f" -> {ast.unparse(node.returns)}"

            elements.append({
                "type": "function",
                "name": node.name,
                "location": f"{file_path}:{node.lineno}",
                "signature": signature,
                "docstring": ast.get_docstring(node),
                "visibility": visibility,
            })

    return elements


def extract_typescript_elements(file_path: Path) -> list[CodeElement]:
    """Extract code elements from a TypeScript/JavaScript file."""
    elements = []
    content = file_path.read_text()

    # Simple regex-based extraction (full implementation would use parser)
    # Export patterns
    export_pattern = r"export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+(\w+)"
    for match in re.finditer(export_pattern, content):
        name = match.group(1)
        line = content[:match.start()].count('\n') + 1
        elements.append({
            "type": "export",
            "name": name,
            "location": f"{file_path}:{line}",
            "signature": None,
            "docstring": None,
            "visibility": "public",
        })

    return elements


def walk_codebase(project_path: Path) -> CodebaseSnapshot:
    """Walk the codebase and extract documentation-relevant elements."""
    from datetime import datetime, timezone

    snapshot = CodebaseSnapshot(
        project_path=str(project_path),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    # Determine project type and relevant files
    ignore_dirs = {".git", "node_modules", "__pycache__", ".next", "dist", "build", ".venv", "venv"}

    for root, dirs, files in os.walk(project_path):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        root_path = Path(root)
        rel_path = root_path.relative_to(project_path)

        for file in files:
            file_path = root_path / file

            # Python files
            if file.endswith(".py"):
                elements = extract_python_elements(file_path)
                for elem in elements:
                    if elem["type"] == "class":
                        snapshot.classes.append(elem)
                    elif elem["type"] == "function":
                        snapshot.functions.append(elem)

            # TypeScript/JavaScript files
            elif file.endswith((".ts", ".tsx", ".js", ".jsx")):
                elements = extract_typescript_elements(file_path)
                for elem in elements:
                    snapshot.functions.append(elem)

            # Config files
            if file in ["package.json", "tsconfig.json", "pyproject.toml",
                       "Cargo.toml", ".env.example", "config.yaml", "config.json"]:
                snapshot.config_files.append(str(file_path.relative_to(project_path)))

    # Identify entry points
    entry_point_patterns = [
        "main.py", "app.py", "index.ts", "index.js", "main.ts", "main.rs",
        "cli.py", "cli.ts", "__main__.py"
    ]
    for pattern in entry_point_patterns:
        matches = list(project_path.glob(f"**/{pattern}"))
        for match in matches:
            if not any(ignore in str(match) for ignore in ignore_dirs):
                snapshot.entry_points.append(str(match.relative_to(project_path)))

    return snapshot


def compare_to_docs(snapshot: CodebaseSnapshot, docs_path: Path) -> SyncReport:
    """Compare codebase snapshot to existing documentation."""
    report = SyncReport()

    # Check if docs exist
    if not docs_path.exists():
        report.findings.append({
            "id": "SYNC-001",
            "severity": "HIGH",
            "category": "MISSING",
            "code_location": snapshot.project_path,
            "doc_location": None,
            "description": "No documentation directory found",
            "suggestion": "Run /docs.init to create documentation structure",
        })
        return report

    # Check for API documentation
    api_doc_path = docs_path / "developer" / "reference" / "api"
    if snapshot.classes or snapshot.functions:
        public_elements = [e for e in snapshot.classes + snapshot.functions
                         if e["visibility"] == "public"]

        if public_elements and not api_doc_path.exists():
            report.findings.append({
                "id": "SYNC-002",
                "severity": "HIGH",
                "category": "MISSING",
                "code_location": "Multiple locations",
                "doc_location": str(api_doc_path),
                "description": f"Found {len(public_elements)} public APIs but no API documentation",
                "suggestion": "Create API reference documentation for public interfaces",
            })

    # Check for undocumented public functions
    for func in snapshot.functions:
        if func["visibility"] == "public" and not func["docstring"]:
            report.findings.append({
                "id": f"SYNC-{len(report.findings)+1:03d}",
                "severity": "MEDIUM",
                "category": "UNDOCUMENTED",
                "code_location": func["location"],
                "doc_location": None,
                "description": f"Public function '{func['name']}' has no docstring",
                "suggestion": "Add docstring to function or document in API reference",
            })

    # Calculate coverage
    total_public = len([e for e in snapshot.classes + snapshot.functions
                       if e["visibility"] == "public"])
    documented = len([e for e in snapshot.classes + snapshot.functions
                     if e["visibility"] == "public" and e["docstring"]])

    report.coverage = {
        "total_public_apis": total_public,
        "with_docstrings": documented,
        "docstring_coverage": round(documented / total_public * 100) if total_public else 0,
    }

    report.summary = {
        "total_findings": len(report.findings),
        "high_severity": len([f for f in report.findings if f["severity"] == "HIGH"]),
        "medium_severity": len([f for f in report.findings if f["severity"] == "MEDIUM"]),
        "low_severity": len([f for f in report.findings if f["severity"] == "LOW"]),
    }

    return report


def generate_snapshot_markdown(snapshot: CodebaseSnapshot) -> str:
    """Generate markdown representation of codebase snapshot."""
    lines = [
        "# Codebase Snapshot",
        "",
        f"**Generated**: {snapshot.timestamp}",
        f"**Project**: {snapshot.project_path}",
        "",
        "## Entry Points",
        "",
    ]

    for entry in snapshot.entry_points:
        lines.append(f"- `{entry}`")

    lines.extend(["", "## Public Classes", ""])
    for cls in snapshot.classes:
        if cls["visibility"] == "public":
            lines.append(f"### {cls['name']}")
            lines.append(f"**Location**: `{cls['location']}`")
            if cls["docstring"]:
                lines.append(f"\n{cls['docstring']}\n")
            lines.append("")

    lines.extend(["", "## Public Functions", ""])
    for func in snapshot.functions:
        if func["visibility"] == "public":
            lines.append(f"### {func['name']}")
            lines.append(f"**Location**: `{func['location']}`")
            if func["signature"]:
                lines.append(f"**Signature**: `{func['signature']}`")
            if func["docstring"]:
                lines.append(f"\n{func['docstring']}\n")
            lines.append("")

    lines.extend(["", "## Configuration Files", ""])
    for config in snapshot.config_files:
        lines.append(f"- `{config}`")

    return "\n".join(lines)


def generate_report_markdown(report: SyncReport) -> str:
    """Generate markdown sync report."""
    lines = [
        "# Documentation Sync Report",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Findings | {report.summary.get('total_findings', 0)} |",
        f"| High Severity | {report.summary.get('high_severity', 0)} |",
        f"| Medium Severity | {report.summary.get('medium_severity', 0)} |",
        f"| Low Severity | {report.summary.get('low_severity', 0)} |",
        "",
        "## Coverage",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Public APIs | {report.coverage.get('total_public_apis', 0)} |",
        f"| With Docstrings | {report.coverage.get('with_docstrings', 0)} |",
        f"| Coverage | {report.coverage.get('docstring_coverage', 0)}% |",
        "",
        "## Findings",
        "",
    ]

    if not report.findings:
        lines.append("No discrepancies found.")
    else:
        for finding in report.findings:
            lines.extend([
                f"### {finding['id']} [{finding['severity']}]",
                f"**Category**: {finding['category']}",
                f"**Code Location**: `{finding['code_location']}`",
                f"**Doc Location**: `{finding['doc_location'] or 'N/A'}`",
                "",
                f"**Description**: {finding['description']}",
                "",
                f"**Suggestion**: {finding['suggestion']}",
                "",
                "---",
                "",
            ])

    return "\n".join(lines)



def _validate_path(filepath: str, allowed_extensions: set, label: str) -> str:
    """Validate file path: reject traversal and restrict extensions. Returns resolved path."""
    resolved = os.path.realpath(filepath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = os.path.splitext(resolved)[1].lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)
    return resolved



def _validate_dir_path(dirpath: str, label: str) -> str:
    """Validate directory path: reject traversal. Returns resolved path."""
    resolved = os.path.realpath(dirpath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {dirpath}")
        sys.exit(1)
    return resolved

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync codebase with documentation"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=os.getcwd(),
        help="Path to project root (default: current directory)"
    )
    parser.add_argument(
        "--walkthrough",
        action="store_true",
        help="Full walkthrough mode - generate complete snapshot"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--output",
        help="Output directory for reports (default: docs/_meta/)"
    )

    args = parser.parse_args()

    if args.source:
        args.source = _validate_dir_path(args.source, "source directory")

    args.output = _validate_path(args.output, {'.htm', '.html', '.json', '.md', '.svg', '.txt'}, "output")
    project_path = Path(args.project_path).resolve()

    print(f"Analyzing codebase: {project_path}")

    # Walk codebase
    snapshot = walk_codebase(project_path)

    print(f"  Found {len(snapshot.classes)} classes")
    print(f"  Found {len(snapshot.functions)} functions")
    print(f"  Found {len(snapshot.entry_points)} entry points")
    print(f"  Found {len(snapshot.config_files)} config files")

    # Determine output path
    output_path = Path(args.output) if args.output else project_path / "docs" / "_meta"

    if args.walkthrough:
        # Full walkthrough - just generate snapshot
        if args.json:
            output = {
                "project_path": snapshot.project_path,
                "timestamp": snapshot.timestamp,
                "modules": snapshot.modules,
                "classes": snapshot.classes,
                "functions": snapshot.functions,
                "entry_points": snapshot.entry_points,
                "config_files": snapshot.config_files,
            }
            print(json.dumps(output, indent=2))
        else:
            print("\n" + generate_snapshot_markdown(snapshot))
    else:
        # Compare to docs
        docs_path = project_path / "docs"
        report = compare_to_docs(snapshot, docs_path)

        if args.json:
            output = {
                "findings": report.findings,
                "coverage": report.coverage,
                "summary": report.summary,
            }
            print(json.dumps(output, indent=2))
        else:
            print("\n" + generate_report_markdown(report))


if __name__ == "__main__":
    main()
