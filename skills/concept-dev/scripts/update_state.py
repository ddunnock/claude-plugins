#!/usr/bin/env python3
"""
Atomic state.json updates for concept development sessions.

Provides safe read-modify-write operations on the session state file
with timestamp tracking and validation.
"""

import os
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


def update_by_path(state_path: str, dotted_path: str, value: Any):
    """Update a value at a dotted path like 'phases.drilldown.blocks_total'."""
    state = load_state(state_path)
    keys = dotted_path.split(".")
    target = state
    for key in keys[:-1]:
        if not isinstance(target, dict) or key not in target:
            print(f"Error: Path '{dotted_path}' not found (failed at '{key}')", file=sys.stderr)
            sys.exit(1)
        target = target[key]
    final_key = keys[-1]
    if not isinstance(target, dict):
        print(f"Error: Parent of '{final_key}' is not a dict", file=sys.stderr)
        sys.exit(1)
    target[final_key] = value
    save_state(state_path, state)
    print(f"Updated {dotted_path} = {value}")


def check_gate(state_path: str, phase: str):
    """Check if the prerequisite gate for a phase has been passed. Exit 0 if yes, 1 if no."""
    phase_order = ["spitball", "problem", "blackbox", "drilldown", "document"]
    if phase not in phase_order:
        print(f"Error: Unknown phase '{phase}'", file=sys.stderr)
        sys.exit(1)
    idx = phase_order.index(phase)
    if idx == 0:
        # spitball has no prerequisite
        print(f"Gate check for '{phase}': no prerequisite needed")
        sys.exit(0)
    prev_phase = phase_order[idx - 1]
    state = load_state(state_path)
    if state["phases"].get(prev_phase, {}).get("gate_passed"):
        print(f"Gate check for '{phase}': prerequisite '{prev_phase}' gate passed")
        sys.exit(0)
    else:
        print(f"Gate check for '{phase}': prerequisite '{prev_phase}' gate NOT passed. "
              f"Run /concept:{prev_phase} first.", file=sys.stderr)
        sys.exit(1)


def sync_counts(state_path: str):
    """Read source_registry.json and assumption_registry.json, update all counters in state.json."""
    state = load_state(state_path)
    workspace = str(Path(state_path).parent)

    # Sync sources
    src_path = Path(workspace) / "source_registry.json"
    if src_path.exists():
        with open(src_path, "r") as f:
            src_reg = json.load(f)
        sources = src_reg.get("sources", [])
        state["sources"]["total"] = len(sources)
        by_conf = {"high": 0, "medium": 0, "low": 0, "ungrounded": 0}
        for s in sources:
            conf = s.get("confidence", "medium")
            if conf in by_conf:
                by_conf[conf] += 1
        state["sources"]["by_confidence"] = by_conf

    # Sync assumptions
    asn_path = Path(workspace) / "assumption_registry.json"
    if asn_path.exists():
        with open(asn_path, "r") as f:
            asn_reg = json.load(f)
        assumptions = asn_reg.get("assumptions", [])
        state["assumptions"]["total"] = len(assumptions)
        state["assumptions"]["pending"] = sum(1 for a in assumptions if a.get("status") == "pending")
        state["assumptions"]["approved"] = sum(1 for a in assumptions if a.get("status") in ("approved", "modified"))

    save_state(state_path, state)
    print(f"Synced counts — sources: {state['sources']['total']}, "
          f"assumptions: {state['assumptions']['total']} "
          f"({state['assumptions']['pending']} pending)")


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

    # update — supports dotted path (2-arg) or legacy 3-arg mode
    up = subparsers.add_parser("update", help="Update counter/value by dotted path")
    up.add_argument("path_parts", nargs="+", help="Dotted path and value, e.g. 'phases.drilldown.blocks_total 11' or legacy 'sources total 17'")

    # check-gate
    cg = subparsers.add_parser("check-gate", help="Check if prerequisite gate passed for a phase")
    cg.add_argument("phase", help="Phase name to check prerequisite for")

    # sync-counts
    subparsers.add_parser("sync-counts", help="Sync source/assumption counts from registries to state.json")

    # set-tools
    st = subparsers.add_parser("set-tools", help="Record detected tools")
    st.add_argument("--available", nargs="+", default=[], help="Available tool names")

    # show
    subparsers.add_parser("show", help="Show current state")

    args = parser.parse_args()

    args.state = _validate_path(args.state, {'.json'}, "state file")

    if args.command == "set-phase":
        set_phase(args.state, args.phase, args.status)
    elif args.command == "pass-gate":
        pass_gate(args.state, args.phase)
    elif args.command == "set-artifact":
        set_artifact(args.state, args.phase, args.path, args.key)
    elif args.command == "update":
        parts = args.path_parts
        if len(parts) == 3:
            # Legacy 3-arg mode: section key value -> section.key value
            dotted = f"{parts[0]}.{parts[1]}"
            value = parse_value(parts[2])
        elif len(parts) == 2:
            dotted = parts[0]
            value = parse_value(parts[1])
        else:
            print("Error: 'update' expects 2 args (dotted.path value) or 3 args (section key value)", file=sys.stderr)
            sys.exit(1)
        update_by_path(args.state, dotted, value)
    elif args.command == "check-gate":
        check_gate(args.state, args.phase)
    elif args.command == "sync-counts":
        sync_counts(args.state)
    elif args.command == "set-tools":
        set_tools(args.state, args.available)
    elif args.command == "show":
        show_state(args.state)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
