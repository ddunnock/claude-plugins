#!/usr/bin/env python3
"""
Atomic state.json updates for concept development sessions.

Provides safe read-modify-write operations on the session state file
with timestamp tracking and validation.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import sys


def load_state(state_path: str) -> dict:
    """Load state from file."""
    path = Path(state_path)
    if not path.exists():
        print(f"Error: State file not found: {state_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)


def save_state(state_path: str, state: dict):
    """Save state to file with updated timestamp."""
    state["session"]["last_updated"] = datetime.now().isoformat()
    path = Path(state_path)
    # Write to temp then rename for atomicity
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(state, f, indent=2)
    tmp_path.rename(path)


def set_phase(state_path: str, phase: str, status: str = "in_progress"):
    """Set current phase and update phase status."""
    valid_phases = ["spitball", "problem", "blackbox", "drilldown", "document"]
    if phase not in valid_phases:
        print(f"Error: Invalid phase '{phase}'. Must be one of: {valid_phases}", file=sys.stderr)
        sys.exit(1)

    state = load_state(state_path)
    state["current_phase"] = phase

    now = datetime.now().isoformat()
    phase_data = state["phases"][phase]
    phase_data["status"] = status

    if status == "in_progress" and not phase_data.get("started_at"):
        phase_data["started_at"] = now
    elif status == "completed":
        phase_data["completed_at"] = now

    save_state(state_path, state)
    print(f"Phase '{phase}' set to '{status}'")


def pass_gate(state_path: str, phase: str):
    """Mark a phase gate as passed."""
    state = load_state(state_path)
    if phase not in state["phases"]:
        print(f"Error: Unknown phase '{phase}'", file=sys.stderr)
        sys.exit(1)

    state["phases"][phase]["gate_passed"] = True
    state["phases"][phase]["status"] = "completed"
    state["phases"][phase]["completed_at"] = datetime.now().isoformat()
    save_state(state_path, state)
    print(f"Gate passed for phase '{phase}'")


def set_artifact(state_path: str, phase: str, artifact_path: str, artifact_key: str = "artifact"):
    """Record an artifact path for a phase."""
    state = load_state(state_path)
    if phase not in state["phases"]:
        print(f"Error: Unknown phase '{phase}'", file=sys.stderr)
        sys.exit(1)

    state["phases"][phase][artifact_key] = artifact_path
    save_state(state_path, state)
    print(f"Artifact recorded for '{phase}': {artifact_path}")


def update_counters(state_path: str, section: str, key: str, value: Any):
    """Update a counter or value in a state section."""
    state = load_state(state_path)
    if section not in state:
        print(f"Error: Unknown section '{section}'", file=sys.stderr)
        sys.exit(1)

    if isinstance(state[section], dict):
        state[section][key] = value
    else:
        print(f"Error: Section '{section}' is not a dict", file=sys.stderr)
        sys.exit(1)

    save_state(state_path, state)
    print(f"Updated {section}.{key} = {value}")


def set_tools(state_path: str, available: list, tier1: Optional[list] = None, tier2: Optional[list] = None, tier3: Optional[list] = None):
    """Record detected tool availability."""
    state = load_state(state_path)
    state["tools"]["detected_at"] = datetime.now().isoformat()
    state["tools"]["available"] = available
    if tier1 is not None:
        state["tools"]["tier1"] = tier1
    if tier2 is not None:
        state["tools"]["tier2"] = tier2
    if tier3 is not None:
        state["tools"]["tier3"] = tier3
    save_state(state_path, state)
    print(f"Tools updated: {len(available)} available")


def show_state(state_path: str):
    """Print current state summary."""
    state = load_state(state_path)
    print("=" * 60)
    print(f"Session: {state['session']['id']}")
    print(f"Project: {state['session'].get('project_name') or 'unnamed'}")
    print(f"Current Phase: {state.get('current_phase') or 'none'}")
    print(f"Last Updated: {state['session'].get('last_updated', 'unknown')}")
    print("-" * 60)

    status_icons = {"not_started": " ", "in_progress": ">", "completed": "X"}
    for phase_name, phase_data in state["phases"].items():
        status = phase_data["status"]
        gate = "PASSED" if phase_data.get("gate_passed") else "pending"
        print(f"  [{status_icons.get(status, '?')}] {phase_name:12s} | {status:14s} | gate: {gate}")

    print("-" * 60)
    print(f"Sources: {state['sources']['total']}  |  "
          f"Assumptions: {state['assumptions']['total']} "
          f"({state['assumptions']['pending']} pending)")
    print(f"Skeptic: V:{state['skeptic_findings']['verified']} "
          f"U:{state['skeptic_findings']['unverified']} "
          f"D:{state['skeptic_findings']['disputed']} "
          f"?:{state['skeptic_findings']['needs_user_input']}")
    print("=" * 60)


def parse_value(raw: str) -> Any:
    """Parse a CLI string value into int, float, bool, or leave as str."""
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    return raw


def main():
    parser = argparse.ArgumentParser(description="Update concept-dev session state")
    parser.add_argument("--state", default=".concept-dev/state.json", help="Path to state.json")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # set-phase
    sp = subparsers.add_parser("set-phase", help="Set current phase")
    sp.add_argument("phase", help="Phase name")
    sp.add_argument("--status", default="in_progress", help="Phase status")

    # pass-gate
    pg = subparsers.add_parser("pass-gate", help="Mark gate as passed")
    pg.add_argument("phase", help="Phase name")

    # set-artifact
    sa = subparsers.add_parser("set-artifact", help="Record artifact path")
    sa.add_argument("phase", help="Phase name")
    sa.add_argument("path", help="Artifact file path")
    sa.add_argument("--key", default="artifact", help="Artifact key name")

    # update
    up = subparsers.add_parser("update", help="Update counter/value")
    up.add_argument("section", help="State section (sources, assumptions, skeptic_findings)")
    up.add_argument("key", help="Key to update")
    up.add_argument("value", help="New value")

    # set-tools
    st = subparsers.add_parser("set-tools", help="Record detected tools")
    st.add_argument("--available", nargs="+", default=[], help="Available tool names")

    # show
    subparsers.add_parser("show", help="Show current state")

    args = parser.parse_args()

    if args.command == "set-phase":
        set_phase(args.state, args.phase, args.status)
    elif args.command == "pass-gate":
        pass_gate(args.state, args.phase)
    elif args.command == "set-artifact":
        set_artifact(args.state, args.phase, args.path, args.key)
    elif args.command == "update":
        update_counters(args.state, args.section, args.key, parse_value(args.value))
    elif args.command == "set-tools":
        set_tools(args.state, args.available)
    elif args.command == "show":
        show_state(args.state)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
