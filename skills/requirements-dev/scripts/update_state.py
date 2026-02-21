"""Update requirements-dev session state.

Usage:
    python3 update_state.py --state <state_file> set-phase <phase>
    python3 update_state.py --state <state_file> pass-gate <phase>
    python3 update_state.py --state <state_file> check-gate <phase>
    python3 update_state.py --state <state_file> set-artifact <phase> <path> [--key <key>]
    python3 update_state.py --state <state_file> update <dotted.path> <value>
    python3 update_state.py --state <state_file> sync-counts
    python3 update_state.py --state <state_file> show

All mutations use atomic write (temp-file-then-rename).
"""
import argparse
import json
import os
import sys

from shared_io import _atomic_write, _validate_path


VALID_PHASES = ("init", "needs", "requirements", "validate", "deliver", "decompose")
VALID_GATES = ("init", "needs", "requirements", "deliver")
STATE_FILENAME = "state.json"


def _load_state(workspace_path: str) -> dict:
    """Load state.json from workspace. Raise FileNotFoundError if missing."""
    state_file = os.path.join(workspace_path, STATE_FILENAME)
    if not os.path.isfile(state_file):
        raise FileNotFoundError(f"State file not found: {state_file}")
    with open(state_file) as f:
        return json.load(f)


def _save_state(workspace_path: str, state: dict) -> None:
    """Save state.json atomically."""
    state_file = os.path.join(workspace_path, STATE_FILENAME)
    _atomic_write(state_file, state)


def set_phase(workspace_path: str, phase: str) -> None:
    """Set current_phase to the given phase name."""
    state = _load_state(workspace_path)
    state["current_phase"] = phase
    _save_state(workspace_path, state)


def pass_gate(workspace_path: str, phase: str) -> None:
    """Mark a phase gate as passed. Idempotent."""
    state = _load_state(workspace_path)
    if phase not in state.get("gates", {}):
        raise ValueError(f"Unknown gate: {phase}. Valid gates: {VALID_GATES}")
    state["gates"][phase] = True
    _save_state(workspace_path, state)


def check_gate(workspace_path: str, phase: str) -> bool:
    """Check if a phase gate has been passed."""
    state = _load_state(workspace_path)
    return state.get("gates", {}).get(phase, False)


def set_artifact(workspace_path: str, phase: str, artifact_path: str, key: str | None = None) -> None:
    """Record a deliverable artifact path under artifacts.<phase>."""
    state = _load_state(workspace_path)
    if "artifacts" not in state:
        state["artifacts"] = {}

    if key:
        # Store under artifacts.<phase>.<key>
        if phase not in state["artifacts"] or not isinstance(state["artifacts"].get(phase), dict):
            state["artifacts"][phase] = {}
        state["artifacts"][phase][key] = artifact_path
    else:
        # Store directly under artifacts.<phase>
        state["artifacts"][phase] = artifact_path

    _save_state(workspace_path, state)


def _parse_value(value_str: str):
    """Parse a string value to the appropriate Python type."""
    if value_str == "null":
        return None
    if value_str == "true":
        return True
    if value_str == "false":
        return False
    try:
        return int(value_str)
    except ValueError:
        pass
    try:
        return float(value_str)
    except ValueError:
        pass
    return value_str


def update_field(workspace_path: str, dotted_path: str, value: str) -> None:
    """Update a nested field using dot notation."""
    state = _load_state(workspace_path)
    parts = dotted_path.split(".")
    target = state
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = _parse_value(value)
    _save_state(workspace_path, state)


def sync_counts(workspace_path: str) -> None:
    """Read registries and update all count fields in state.json."""
    state = _load_state(workspace_path)

    # Read needs registry
    needs_file = os.path.join(workspace_path, "needs_registry.json")
    if os.path.isfile(needs_file):
        with open(needs_file) as f:
            needs = json.load(f)
    else:
        needs = []

    # Read requirements registry
    reqs_file = os.path.join(workspace_path, "requirements_registry.json")
    if os.path.isfile(reqs_file):
        with open(reqs_file) as f:
            reqs = json.load(f)
    else:
        reqs = []

    # Compute needs counts
    state["counts"]["needs_total"] = len(needs)
    state["counts"]["needs_approved"] = sum(1 for n in needs if n.get("status") == "approved")
    state["counts"]["needs_deferred"] = sum(1 for n in needs if n.get("status") == "deferred")

    # Compute requirements counts
    state["counts"]["requirements_total"] = len(reqs)
    state["counts"]["requirements_registered"] = sum(
        1 for r in reqs if r.get("status") == "registered"
    )
    state["counts"]["requirements_baselined"] = sum(
        1 for r in reqs if r.get("status") == "baselined"
    )
    state["counts"]["requirements_withdrawn"] = sum(
        1 for r in reqs if r.get("status") == "withdrawn"
    )

    # Compute TBD/TBR counts
    tbd_count = 0
    tbr_count = 0
    for r in reqs:
        tbd_tbr = r.get("tbd_tbr")
        if tbd_tbr:
            if tbd_tbr.get("tbd"):
                tbd_count += 1
            if tbd_tbr.get("tbr"):
                tbr_count += 1
    state["counts"]["tbd_open"] = tbd_count
    state["counts"]["tbr_open"] = tbr_count

    _save_state(workspace_path, state)


def show(workspace_path: str) -> str:
    """Return a human-readable summary of current state."""
    state = _load_state(workspace_path)
    lines = []
    lines.append(f"Session: {state.get('session_id', 'unknown')}")
    lines.append(f"Phase:   {state.get('current_phase', 'unknown')}")
    lines.append("")

    # Gates
    lines.append("Gates:")
    for gate, passed in state.get("gates", {}).items():
        mark = "+" if passed else "-"
        lines.append(f"  [{mark}] {gate}")
    lines.append("")

    # Counts
    lines.append("Counts:")
    for key, val in state.get("counts", {}).items():
        lines.append(f"  {key}: {val}")
    lines.append("")

    # Traceability
    trace = state.get("traceability", {})
    lines.append(f"Traceability: {trace.get('links_total', 0)} links, {trace.get('coverage_pct', 0.0)}% coverage")
    lines.append("")

    # Progress
    progress = state.get("progress", {})
    block = progress.get("current_block") or "none"
    type_pass = progress.get("current_type_pass") or "none"
    lines.append(f"Progress: block={block}, type_pass={type_pass}")

    result = "\n".join(lines)
    print(result)
    return result


def main():
    """CLI entry point with argparse subcommands."""
    parser = argparse.ArgumentParser(description="Update requirements-dev session state")
    parser.add_argument("--state", required=True, help="Path to state.json or workspace directory")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # set-phase
    sp = subparsers.add_parser("set-phase")
    sp.add_argument("phase", choices=VALID_PHASES)

    # pass-gate
    sp = subparsers.add_parser("pass-gate")
    sp.add_argument("phase", choices=VALID_GATES)

    # check-gate
    sp = subparsers.add_parser("check-gate")
    sp.add_argument("phase", choices=VALID_GATES)

    # set-artifact
    sp = subparsers.add_parser("set-artifact")
    sp.add_argument("phase")
    sp.add_argument("path")
    sp.add_argument("--key", default=None)

    # update
    sp = subparsers.add_parser("update")
    sp.add_argument("dotted_path")
    sp.add_argument("value")

    # sync-counts
    subparsers.add_parser("sync-counts")

    # show
    subparsers.add_parser("show")

    args = parser.parse_args()

    # Resolve and validate workspace path from --state
    state_path = args.state
    if os.path.isfile(state_path) and state_path.endswith(".json"):
        state_path = _validate_path(state_path, allowed_extensions=[".json"])
        workspace = os.path.dirname(state_path)
    else:
        workspace = os.path.realpath(state_path)

    if args.command == "set-phase":
        set_phase(workspace, args.phase)
    elif args.command == "pass-gate":
        pass_gate(workspace, args.phase)
    elif args.command == "check-gate":
        passed = check_gate(workspace, args.phase)
        sys.exit(0 if passed else 1)
    elif args.command == "set-artifact":
        set_artifact(workspace, args.phase, args.path, key=args.key)
    elif args.command == "update":
        update_field(workspace, args.dotted_path, args.value)
    elif args.command == "sync-counts":
        sync_counts(workspace)
    elif args.command == "show":
        show(workspace)


if __name__ == "__main__":
    main()
