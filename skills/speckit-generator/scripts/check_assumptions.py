#!/usr/bin/env python3
"""
check_assumptions.py - Audit assumption coverage in SpecKit package

Usage: python check_assumptions.py <dir> [--report] [--json]

Scans all files for assumption markers and compares against
the assumptions log to identify unlogged assumptions.

Inputs:
  - dir: Path to the .claude directory to audit
  - --report: Generate detailed report
  - --fix: Create entries for unlogged assumptions
  - --json: Output as JSON

Outputs:
  - Assumption audit report

Exit Codes:
  - 0: All assumptions logged
  - 1: Unlogged assumptions found
  - 2: Input error
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def find_assumption_markers(content: str, file_path: str) -> List[Dict]:
    """Find all assumption markers in content."""
    assumptions = []
    
    # Pattern: [ASSUMPTION: rationale] or [ASSUMPTION]
    pattern = r'\[ASSUMPTION(?::\s*([^\]]+))?\](?:\s*([^\[]+))?'
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for match in re.finditer(pattern, line):
            rationale = match.group(1) or "No rationale provided"
            context = match.group(2).strip() if match.group(2) else ""
            
            assumptions.append({
                "file": file_path,
                "line": line_num,
                "rationale": rationale.strip(),
                "context": context[:100] if context else "",
                "full_match": match.group(0)
            })
    
    return assumptions


def parse_assumptions_log(log_path: Path) -> List[Dict]:
    """Parse the assumptions log to get logged assumptions."""
    if not log_path.exists():
        return []
    
    content = log_path.read_text()
    logged = []
    
    # Pattern for table rows: | A-XXX | ... |
    pattern = r'\|\s*(A-\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|'
    
    for match in re.finditer(pattern, content):
        logged.append({
            "id": match.group(1).strip(),
            "category": match.group(2).strip(),
            "assumption": match.group(3).strip(),
            "rationale": match.group(4).strip(),
            "validation": match.group(5).strip(),
            "status": match.group(6).strip() if match.group(6) else "OPEN"
        })
    
    return logged


def generate_assumption_id(existing_ids: List[str]) -> str:
    """Generate the next assumption ID."""
    max_num = 0
    for id in existing_ids:
        try:
            num = int(id.split('-')[1])
            max_num = max(max_num, num)
        except (IndexError, ValueError):
            continue
    return f"A-{max_num + 1:03d}"


def audit_assumptions(base_dir: Path) -> Dict:
    """Audit all assumptions in the package."""
    result = {
        "total_markers": 0,
        "logged_assumptions": 0,
        "unlogged_count": 0,
        "found_in_files": [],
        "logged": [],
        "unlogged": [],
        "files_scanned": 0
    }
    
    # Find all markdown files
    md_files = list(base_dir.rglob('*.md'))
    result["files_scanned"] = len(md_files)
    
    # Collect all assumption markers
    all_markers = []
    for md_file in md_files:
        content = md_file.read_text()
        markers = find_assumption_markers(content, str(md_file))
        all_markers.extend(markers)
        if markers:
            result["found_in_files"].append({
                "file": str(md_file),
                "count": len(markers)
            })
    
    result["total_markers"] = len(all_markers)
    
    # Parse assumptions log
    log_path = base_dir / 'memory' / 'assumptions-log.md'
    logged = parse_assumptions_log(log_path)
    result["logged_assumptions"] = len(logged)
    result["logged"] = logged
    
    # Compare - simple heuristic: check if rationale/context appears in log
    logged_texts = set()
    for log_entry in logged:
        logged_texts.add(log_entry["assumption"].lower())
        logged_texts.add(log_entry["rationale"].lower())
    
    for marker in all_markers:
        marker_text = f"{marker['rationale']} {marker['context']}".lower()
        is_logged = any(text in marker_text or marker_text in text 
                       for text in logged_texts if text)
        
        if not is_logged:
            result["unlogged"].append(marker)
    
    result["unlogged_count"] = len(result["unlogged"])
    
    return result


def generate_log_entries(unlogged: List[Dict], existing_ids: List[str]) -> str:
    """Generate markdown table rows for unlogged assumptions."""
    lines = []
    current_ids = existing_ids.copy()
    
    for assumption in unlogged:
        new_id = generate_assumption_id(current_ids)
        current_ids.append(new_id)
        
        # Truncate long values
        rationale = assumption["rationale"][:50]
        context = assumption["context"][:50]
        
        lines.append(
            f"| {new_id} | [CAT] | {rationale} | {context} | [VALIDATION] | [RISK] | OPEN |"
        )
    
    return "\n".join(lines)


def format_report(result: Dict) -> str:
    """Format the audit result as a text report."""
    lines = [
        "",
        "=" * 60,
        "Assumption Audit Report",
        "=" * 60,
        "",
        f"Files Scanned: {result['files_scanned']}",
        f"Total Assumption Markers: {result['total_markers']}",
        f"Logged Assumptions: {result['logged_assumptions']}",
        f"Unlogged Assumptions: {result['unlogged_count']}",
        ""
    ]
    
    if result["found_in_files"]:
        lines.append("Files with Assumptions:")
        for entry in result["found_in_files"]:
            lines.append(f"  - {entry['file']}: {entry['count']} markers")
        lines.append("")
    
    if result["unlogged"]:
        lines.append("⚠️ UNLOGGED ASSUMPTIONS:")
        lines.append("")
        for i, assumption in enumerate(result["unlogged"], 1):
            lines.append(f"  {i}. {assumption['file']}:{assumption['line']}")
            lines.append(f"     Rationale: {assumption['rationale']}")
            if assumption['context']:
                lines.append(f"     Context: {assumption['context'][:80]}...")
            lines.append("")
    else:
        lines.append("✅ All assumptions are logged")
    
    lines.append("=" * 60)
    
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


def main():
    parser = argparse.ArgumentParser(
        description="Audit assumption coverage in SpecKit package"
    )
    parser.add_argument(
        "dir",
        help="Path to the .claude directory to audit"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Generate log entries for unlogged assumptions"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()

    if args.dir:
        args.dir = os.path.realpath(args.dir)
    
    try:
        base_dir = Path(args.dir)
        
        if not base_dir.exists():
            raise FileNotFoundError(f"Directory not found: {base_dir}")
        
        result = audit_assumptions(base_dir)
        
        if args.json:
            print(json.dumps({
                "success": result["unlogged_count"] == 0,
                "data": result
            }, indent=2))
        else:
            print(format_report(result))
            
            if args.fix and result["unlogged"]:
                existing_ids = [log["id"] for log in result["logged"]]
                entries = generate_log_entries(result["unlogged"], existing_ids)
                print("\n📝 Suggested Log Entries:")
                print("-" * 60)
                print(entries)
                print("-" * 60)
                print("\nAdd these to memory/assumptions-log.md")
        
        return 0 if result["unlogged_count"] == 0 else 1
        
    except Exception as e:
        if args.json:
            print(json.dumps({
                "success": False,
                "errors": [str(e)]
            }))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
