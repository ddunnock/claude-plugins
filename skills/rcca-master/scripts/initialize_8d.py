#!/usr/bin/env python3
"""
8D Session Initializer

Creates a new 8D session structure with JSON template for tracking investigation progress.

Usage:
    python initialize_8d.py --id "8D-2025-001" --title "Cracked Connector Housing"
    python initialize_8d.py --interactive
    python initialize_8d.py --output session.json
"""

import os
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

# Allowed output file extensions
_ALLOWED_OUTPUT_EXTENSIONS = {'.json'}


def _validate_output_path(filepath: str) -> Path:
    """Validate an output file path: check extension, reject traversal."""
    path = Path(filepath).resolve()
    if '..' in Path(filepath).parts:
        print(f"Error: Path traversal not allowed: {filepath}", file=sys.stderr)
        sys.exit(1)
    if path.suffix.lower() not in _ALLOWED_OUTPUT_EXTENSIONS:
        print(f"Error: Output file must be one of {_ALLOWED_OUTPUT_EXTENSIONS}, got '{path.suffix}'", file=sys.stderr)
        sys.exit(1)
    return path


@dataclass
class TeamMember:
    """Represents a team member in the 8D investigation."""
    name: str
    role: str
    function: str
    email: str = ""


@dataclass
class Containment:
    """Represents a containment action."""
    id: str
    description: str
    owner: str
    due_date: str
    status: str = "Planned"  # Planned, In Progress, Complete, Verified
    verification_result: str = ""


@dataclass
class CorrectiveAction:
    """Represents a corrective or preventive action."""
    id: str
    description: str
    type: str  # Prevention, Detection, Systemic
    owner: str
    due_date: str
    success_criteria: str
    status: str = "Planned"
    verification_result: str = ""
    revised_status: str = ""


@dataclass
class Session8D:
    """Complete 8D session data structure."""
    # Metadata
    session_id: str
    title: str
    created_date: str
    created_by: str
    status: str = "D0 - Initial Assessment"

    # D0 - Initial Assessment
    domain: str = ""
    severity: str = ""
    urgency: str = ""
    scope_single_multiple: str = ""
    scope_isolated_widespread: str = ""
    known_cause: str = ""
    occurred_before: str = ""
    complexity: str = ""  # Simple, Moderate, Complex, Critical

    # D1 - Team Formation
    team_members: list = field(default_factory=list)

    # D2 - Problem Definition
    problem_what_object: str = ""
    problem_what_defect: str = ""
    problem_where_geographic: str = ""
    problem_where_on_object: str = ""
    problem_when_calendar: str = ""
    problem_when_lifecycle: str = ""
    problem_who: str = ""
    problem_how_detected: str = ""
    problem_how_much: str = ""
    problem_expected: str = ""
    problem_actual: str = ""
    is_not_what: str = ""
    is_not_where: str = ""
    is_not_when: str = ""
    problem_statement: str = ""

    # D3 - Containment
    containment_actions: list = field(default_factory=list)

    # D4 - Root Cause Analysis
    tool_selected: str = ""  # 5 Whys, Fishbone, Pareto, KT-PA, FTA
    analysis_data: dict = field(default_factory=dict)  # Tool-specific data
    root_causes: list = field(default_factory=list)
    root_cause_verified: bool = False
    verification_method: str = ""

    # D5 - Corrective Action Selection
    corrective_actions: list = field(default_factory=list)

    # D6 - Implementation
    implementation_plan: list = field(default_factory=list)
    implementation_risks: list = field(default_factory=list)

    # D7 - Prevention
    systemic_actions: list = field(default_factory=list)
    horizontal_deployment: list = field(default_factory=list)
    documents_updated: list = field(default_factory=list)

    # D8 - Closure
    verification_period_start: str = ""
    verification_period_end: str = ""
    verification_metrics: dict = field(default_factory=dict)
    verification_result: str = ""
    containment_removal_date: str = ""
    lessons_learned: str = ""
    closure_approved_by: str = ""
    closure_date: str = ""

    # Quality Score
    scores: dict = field(default_factory=dict)
    overall_score: float = 0.0
    rating: str = ""


def create_new_session(
    session_id: str,
    title: str,
    created_by: str = ""
) -> Session8D:
    """Create a new 8D session with default structure."""
    return Session8D(
        session_id=session_id,
        title=title,
        created_date=datetime.now().strftime("%Y-%m-%d"),
        created_by=created_by,
    )


def session_to_dict(session: Session8D) -> dict:
    """Convert session to dictionary for JSON serialization."""
    data = asdict(session)
    # Convert nested dataclasses if present
    return data


def save_session(session: Session8D, filepath: str) -> None:
    """Save session to JSON file."""
    data = session_to_dict(session)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_session(filepath: str) -> Session8D:
    """Load session from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return Session8D(**data)


def print_session_summary(session: Session8D) -> None:
    """Print session summary to console."""
    print("\n" + "=" * 60)
    print("8D SESSION CREATED")
    print("=" * 60)
    print(f"\nSession ID:    {session.session_id}")
    print(f"Title:         {session.title}")
    print(f"Created:       {session.created_date}")
    print(f"Created By:    {session.created_by or 'N/A'}")
    print(f"Status:        {session.status}")
    print("\n" + "-" * 60)
    print("WORKFLOW PHASES:")
    print("-" * 60)
    phases = [
        ("D0", "Initial Assessment", "Define domain, severity, urgency, complexity"),
        ("D1", "Team Formation", "Assemble cross-functional team"),
        ("D2", "Problem Definition", "5W2H and IS/IS NOT analysis"),
        ("D3", "Containment", "Protect customer with interim actions"),
        ("D4", "Root Cause Analysis", "Select tool and identify verified root cause"),
        ("D5", "Corrective Action", "Select permanent corrective actions"),
        ("D6", "Implementation", "Plan and execute corrective actions"),
        ("D7", "Prevention", "Systemic actions and horizontal deployment"),
        ("D8", "Closure", "Verify effectiveness and close"),
    ]
    for code, name, desc in phases:
        marker = "→" if session.status.startswith(code) else " "
        print(f"  {marker} {code}: {name}")
        print(f"       {desc}")
    print("\n" + "=" * 60)


def interactive_create() -> Session8D:
    """Create session interactively."""
    print("\n8D SESSION INITIALIZER")
    print("=" * 50)
    print("Create a new 8D investigation session\n")

    # Get required fields
    session_id = input("Session ID (e.g., 8D-2025-001): ").strip()
    if not session_id:
        session_id = f"8D-{datetime.now().strftime('%Y-%m%d-%H%M')}"
        print(f"  Using auto-generated ID: {session_id}")

    title = input("Problem title/description: ").strip()
    if not title:
        title = "New 8D Investigation"

    created_by = input("Created by (name): ").strip()

    # Create session
    session = create_new_session(session_id, title, created_by)

    # Optional: Get initial assessment
    print("\n--- INITIAL ASSESSMENT (D0) ---")
    print("(Press Enter to skip any field)\n")

    print("Problem Domain:")
    print("  [A] Manufacturing/Production defect")
    print("  [B] Field failure or customer complaint")
    print("  [C] Process deviation or quality escape")
    print("  [D] Equipment/machine failure")
    print("  [E] Software/IT system failure")
    print("  [F] Safety incident or near-miss")
    print("  [G] Service delivery failure")
    print("  [H] Supply chain/supplier issue")
    domain_map = {
        'A': 'Manufacturing/Production',
        'B': 'Field failure',
        'C': 'Process deviation',
        'D': 'Equipment failure',
        'E': 'Software/IT',
        'F': 'Safety incident',
        'G': 'Service delivery',
        'H': 'Supply chain',
    }
    domain_choice = input("Select domain [A-H]: ").strip().upper()
    session.domain = domain_map.get(domain_choice, "")

    print("\nSeverity:")
    print("  [1] Critical - Safety, regulatory, major customer impact")
    print("  [2] High - Significant quality or delivery impact")
    print("  [3] Medium - Moderate impact, contained")
    print("  [4] Low - Minor impact, no immediate risk")
    severity_map = {'1': 'Critical', '2': 'High', '3': 'Medium', '4': 'Low'}
    severity_choice = input("Select severity [1-4]: ").strip()
    session.severity = severity_map.get(severity_choice, "")

    print("\nUrgency:")
    print("  [1] Immediate - Must address now")
    print("  [2] Days - Address within a few days")
    print("  [3] Weeks - Can plan properly")
    urgency_map = {'1': 'Immediate', '2': 'Days', '3': 'Weeks'}
    urgency_choice = input("Select urgency [1-3]: ").strip()
    session.urgency = urgency_map.get(urgency_choice, "")

    return session


def main():
    parser = argparse.ArgumentParser(
        description="Initialize new 8D investigation session"
    )
    parser.add_argument(
        "--id",
        type=str,
        help="Session ID (e.g., 8D-2025-001)",
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Problem title/description",
    )
    parser.add_argument(
        "--created-by",
        type=str,
        default="",
        help="Name of person creating session",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    args = parser.parse_args()

    # Create session
    if args.interactive:
        session = interactive_create()
    elif args.id and args.title:
        session = create_new_session(args.id, args.title, args.created_by)
    else:
        # Default quick creation
        session_id = args.id or f"8D-{datetime.now().strftime('%Y-%m%d-%H%M')}"
        title = args.title or "New 8D Investigation"
        session = create_new_session(session_id, title, args.created_by)

    # Output
    print_session_summary(session)

    if args.output:
        output_path = _validate_output_path(args.output)
        save_session(session, str(output_path))
        print(f"\n✓ Session saved to: {output_path}")
    else:
        # Print JSON to stdout
        print("\n--- SESSION JSON ---")
        print(json.dumps(session_to_dict(session), indent=2))


if __name__ == "__main__":
    main()
