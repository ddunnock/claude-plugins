#!/usr/bin/env python3
"""Cross-cutting notes registry for observations that surface in one phase but
belong in another.

Usage:
    python3 notes_tracker.py --workspace <path> add --text "..." --origin-phase needs --target-phase requirements [--related-ids "REQ-001,NEED-003"] [--category performance]
    python3 notes_tracker.py --workspace <path> resolve --id NOTE-001 --resolution "Addressed in REQ-015" [--resolved-by "REQ-015"]
    python3 notes_tracker.py --workspace <path> dismiss --id NOTE-001 --rationale "Not applicable after design change"
    python3 notes_tracker.py --workspace <path> list [--status open] [--target-phase requirements] [--category performance]
    python3 notes_tracker.py --workspace <path> check-gate <phase>
    python3 notes_tracker.py --workspace <path> summary
    python3 notes_tracker.py --workspace <path> export

Cross-cutting notes capture observations like:
  - During functional requirements, noticing a performance concern -> note for performance pass
  - During needs formalization, realizing an interface constraint -> note for requirements
  - During validation, finding a gap that needs decomposition attention -> note for decompose

Each note has a lifecycle: open -> resolved | dismissed
Gates check that all notes targeting the current phase are resolved before advancing.

All mutations use atomic write (temp-file-then-rename) and sync counts to state.json.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

REGISTRY_FILENAME = "notes_registry.json"
STATE_FILENAME = "state.json"
SCHEMA_VERSION = "1.0.0"

# Valid phase names (matching state.json phases)
VALID_PHASES = {"init", "needs", "requirements", "deliver", "validate", "research", "decompose"}

# Valid categories for notes
VALID_CATEGORIES = {
    "functional", "performance", "interface", "constraint", "quality",
    "traceability", "security", "reliability", "scalability",
    "maintainability", "compliance", "general",
}


@dataclass
class Note:
    id: str
    text: str
    origin_phase: str          # Phase where the note was captured
    target_phase: str          # Phase where the note should be addressed
    related_ids: list[str] = field(default_factory=list)  # REQ-xxx, NEED-xxx, etc.
    category: str = "general"  # Functional area or cross-cutting concern
    status: str = "open"       # open | resolved | dismissed
    resolution: str = ""       # How it was resolved
    resolved_by: str = ""      # ID of the artifact that resolved it (e.g., REQ-015)
    dismiss_rationale: str = ""  # Why it was dismissed
    created_at: str = ""
    resolved_at: str = ""


def _load_registry(workspace: str) -> dict:
    """Load notes_registry.json or return empty registry."""
    path = os.path.join(workspace, REGISTRY_FILENAME)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"schema_version": SCHEMA_VERSION, "notes": []}


def _save_registry(workspace: str, registry: dict) -> None:
    """Save registry atomically."""
    path = os.path.join(workspace, REGISTRY_FILENAME)
    _atomic_write(path, registry)


def _sync_counts(workspace: str, registry: dict) -> None:
    """Update notes counts in state.json."""
    state_path = os.path.join(workspace, STATE_FILENAME)
    if not os.path.isfile(state_path):
        return
    with open(state_path) as f:
        state = json.load(f)
    notes = registry["notes"]
    if "notes" not in state.get("counts", {}):
        state.setdefault("counts", {})["notes_total"] = 0
        state["counts"]["notes_open"] = 0
        state["counts"]["notes_resolved"] = 0
        state["counts"]["notes_dismissed"] = 0
    state["counts"]["notes_total"] = len(notes)
    state["counts"]["notes_open"] = sum(1 for n in notes if n.get("status") == "open")
    state["counts"]["notes_resolved"] = sum(1 for n in notes if n.get("status") == "resolved")
    state["counts"]["notes_dismissed"] = sum(1 for n in notes if n.get("status") == "dismissed")
    _atomic_write(state_path, state)


def _next_id(registry: dict) -> str:
    """Generate next sequential NOTE-xxx ID."""
    existing = registry.get("notes", [])
    if not existing:
        return "NOTE-001"
    max_num = 0
    for note in existing:
        try:
            num = int(note["id"].split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            continue
    return f"NOTE-{max_num + 1:03d}"


def _find_note(registry: dict, note_id: str) -> tuple[int, dict]:
    """Find a note by ID. Returns (index, note_dict). Raises ValueError if not found."""
    for i, note in enumerate(registry["notes"]):
        if note["id"] == note_id:
            return i, note
    raise ValueError(f"Note not found: {note_id}")


def add_note(
    workspace: str,
    text: str,
    origin_phase: str,
    target_phase: str,
    related_ids: list[str] | None = None,
    category: str = "general",
) -> str:
    """Add a cross-cutting note. Returns the assigned ID."""
    if origin_phase not in VALID_PHASES:
        raise ValueError(f"Invalid origin_phase: {origin_phase}. Must be one of: {', '.join(sorted(VALID_PHASES))}")
    if target_phase not in VALID_PHASES:
        raise ValueError(f"Invalid target_phase: {target_phase}. Must be one of: {', '.join(sorted(VALID_PHASES))}")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}")

    registry = _load_registry(workspace)
    note = Note(
        id=_next_id(registry),
        text=text,
        origin_phase=origin_phase,
        target_phase=target_phase,
        related_ids=related_ids or [],
        category=category,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    registry["notes"].append(asdict(note))
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)
    return note.id


def resolve_note(workspace: str, note_id: str, resolution: str, resolved_by: str = "") -> None:
    """Mark a note as resolved with explanation."""
    if not resolution or not resolution.strip():
        raise ValueError("resolution text is required")
    registry = _load_registry(workspace)
    idx, note = _find_note(registry, note_id)
    if note["status"] != "open":
        raise ValueError(f"Note {note_id} is already {note['status']}, cannot resolve")
    note["status"] = "resolved"
    note["resolution"] = resolution
    note["resolved_by"] = resolved_by
    note["resolved_at"] = datetime.now(timezone.utc).isoformat()
    registry["notes"][idx] = note
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def dismiss_note(workspace: str, note_id: str, rationale: str) -> None:
    """Dismiss a note as not applicable."""
    if not rationale or not rationale.strip():
        raise ValueError("rationale is required for dismiss")
    registry = _load_registry(workspace)
    idx, note = _find_note(registry, note_id)
    if note["status"] != "open":
        raise ValueError(f"Note {note_id} is already {note['status']}, cannot dismiss")
    note["status"] = "dismissed"
    note["dismiss_rationale"] = rationale
    note["resolved_at"] = datetime.now(timezone.utc).isoformat()
    registry["notes"][idx] = note
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def list_notes(
    workspace: str,
    status: str | None = None,
    target_phase: str | None = None,
    category: str | None = None,
) -> list[dict]:
    """List notes with optional filters."""
    registry = _load_registry(workspace)
    results = registry["notes"]
    if status:
        results = [n for n in results if n.get("status") == status]
    if target_phase:
        results = [n for n in results if n.get("target_phase") == target_phase]
    if category:
        results = [n for n in results if n.get("category") == category]
    return results


def check_gate(workspace: str, phase: str) -> dict:
    """Check if all notes targeting this phase are resolved.

    Returns dict with:
      - ready: bool (True if no open notes block the gate)
      - open_notes: list of open note dicts targeting this phase
      - total_targeting: count of all notes targeting this phase
      - resolved_count: count of resolved notes targeting this phase
    """
    registry = _load_registry(workspace)
    targeting = [n for n in registry["notes"] if n.get("target_phase") == phase]
    open_notes = [n for n in targeting if n.get("status") == "open"]
    resolved = [n for n in targeting if n.get("status") == "resolved"]

    return {
        "ready": len(open_notes) == 0,
        "open_notes": open_notes,
        "total_targeting": len(targeting),
        "resolved_count": len(resolved),
    }


def summary(workspace: str) -> dict:
    """Generate a summary of all notes grouped by target phase."""
    registry = _load_registry(workspace)
    notes = registry["notes"]

    by_target = {}
    for note in notes:
        target = note.get("target_phase", "unknown")
        if target not in by_target:
            by_target[target] = {"open": 0, "resolved": 0, "dismissed": 0, "notes": []}
        by_target[target][note.get("status", "open")] += 1
        if note.get("status") == "open":
            by_target[target]["notes"].append(note)

    return {
        "total": len(notes),
        "open": sum(1 for n in notes if n.get("status") == "open"),
        "resolved": sum(1 for n in notes if n.get("status") == "resolved"),
        "dismissed": sum(1 for n in notes if n.get("status") == "dismissed"),
        "by_target_phase": by_target,
    }


def export_notes(workspace: str) -> dict:
    """Export full registry as dict."""
    return _load_registry(workspace)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage cross-cutting notes registry")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    sp = subparsers.add_parser("add")
    sp.add_argument("--text", required=True, help="The observation or note text")
    sp.add_argument("--origin-phase", required=True, help="Phase where this was observed")
    sp.add_argument("--target-phase", required=True, help="Phase where this should be addressed")
    sp.add_argument("--related-ids", default="", help="Comma-separated related IDs (REQ-xxx, NEED-xxx)")
    sp.add_argument("--category", default="general", help="Category (functional, performance, etc.)")

    # resolve
    sp = subparsers.add_parser("resolve")
    sp.add_argument("--id", required=True)
    sp.add_argument("--resolution", required=True, help="How the note was addressed")
    sp.add_argument("--resolved-by", default="", help="ID of artifact that resolved it")

    # dismiss
    sp = subparsers.add_parser("dismiss")
    sp.add_argument("--id", required=True)
    sp.add_argument("--rationale", required=True)

    # list
    sp = subparsers.add_parser("list")
    sp.add_argument("--status", default=None, help="Filter by status (open, resolved, dismissed)")
    sp.add_argument("--target-phase", default=None, help="Filter by target phase")
    sp.add_argument("--category", default=None, help="Filter by category")

    # check-gate
    sp = subparsers.add_parser("check-gate")
    sp.add_argument("phase", help="Phase to check readiness for")

    # summary
    subparsers.add_parser("summary")

    # export
    subparsers.add_parser("export")

    args = parser.parse_args()

    if args.command == "add":
        related = [r.strip() for r in args.related_ids.split(",") if r.strip()]
        note_id = add_note(
            args.workspace, args.text, args.origin_phase,
            args.target_phase, related, args.category,
        )
        print(json.dumps({"id": note_id}))
    elif args.command == "resolve":
        resolve_note(args.workspace, args.id, args.resolution, args.resolved_by)
        print(json.dumps({"resolved": args.id}))
    elif args.command == "dismiss":
        dismiss_note(args.workspace, args.id, args.rationale)
        print(json.dumps({"dismissed": args.id}))
    elif args.command == "list":
        result = list_notes(args.workspace, args.status, args.target_phase, args.category)
        print(json.dumps(result, indent=2))
    elif args.command == "check-gate":
        result = check_gate(args.workspace, args.phase)
        print(json.dumps(result, indent=2))
        if not result["ready"]:
            sys.exit(1)
    elif args.command == "summary":
        result = summary(args.workspace)
        print(json.dumps(result, indent=2))
    elif args.command == "export":
        result = export_notes(args.workspace)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
