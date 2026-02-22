#!/usr/bin/env python3
"""Needs registry management with INCOSE-pattern formalization.

Usage:
    python3 needs_tracker.py --workspace <path> add --statement "..." --stakeholder "..." --source-block "..."
    python3 needs_tracker.py --workspace <path> update --id NEED-001 --statement "..."
    python3 needs_tracker.py --workspace <path> defer --id NEED-001 --rationale "..."
    python3 needs_tracker.py --workspace <path> reject --id NEED-001 --rationale "..."
    python3 needs_tracker.py --workspace <path> list [--block <block>] [--status <status>]
    python3 needs_tracker.py --workspace <path> query [--source-ref SRC-xxx] [--assumption-ref ASN-xxx]
    python3 needs_tracker.py --workspace <path> export

All mutations use atomic write (temp-file-then-rename) and sync counts to state.json.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

REGISTRY_FILENAME = "needs_registry.json"
STATE_FILENAME = "state.json"
SCHEMA_VERSION = "1.0.0"


@dataclass
class Need:
    id: str
    statement: str
    stakeholder: str
    source_block: str
    source_artifacts: list[str] = field(default_factory=list)
    concept_dev_refs: dict = field(default_factory=lambda: {"sources": [], "assumptions": []})
    status: str = "approved"
    rationale: str | None = None
    registered_at: str = ""


def _load_registry(workspace: str) -> dict:
    """Load needs_registry.json or return empty registry."""
    path = os.path.join(workspace, REGISTRY_FILENAME)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"schema_version": SCHEMA_VERSION, "needs": []}


def _save_registry(workspace: str, registry: dict) -> None:
    """Save registry atomically."""
    path = os.path.join(workspace, REGISTRY_FILENAME)
    _atomic_write(path, registry)


def _sync_counts(workspace: str, registry: dict) -> None:
    """Update needs counts in state.json."""
    state_path = os.path.join(workspace, STATE_FILENAME)
    if not os.path.isfile(state_path):
        return
    with open(state_path) as f:
        state = json.load(f)
    needs = registry["needs"]
    state["counts"]["needs_total"] = len(needs)
    state["counts"]["needs_approved"] = sum(1 for n in needs if n.get("status") == "approved")
    state["counts"]["needs_deferred"] = sum(1 for n in needs if n.get("status") == "deferred")
    _atomic_write(state_path, state)


def _next_id(registry: dict) -> str:
    """Generate next sequential NEED-xxx ID."""
    existing = registry.get("needs", [])
    if not existing:
        return "NEED-001"
    max_num = 0
    for need in existing:
        try:
            num = int(need["id"].split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            continue
    return f"NEED-{max_num + 1:03d}"


def _find_need(registry: dict, need_id: str) -> tuple[int, dict]:
    """Find a need by ID. Returns (index, need_dict). Raises ValueError if not found."""
    for i, need in enumerate(registry["needs"]):
        if need["id"] == need_id:
            return i, need
    raise ValueError(f"Need not found: {need_id}")


def add_need(
    workspace: str,
    statement: str,
    stakeholder: str,
    source_block: str,
    source_artifacts: list[str] | None = None,
    concept_dev_refs: dict | None = None,
) -> str:
    """Add a need to the registry. Returns the assigned ID."""
    registry = _load_registry(workspace)

    # Check uniqueness (case-insensitive statement + stakeholder)
    for existing in registry["needs"]:
        if (
            existing["statement"].lower() == statement.lower()
            and existing["stakeholder"].lower() == stakeholder.lower()
        ):
            raise ValueError(f"duplicate: need with same statement and stakeholder already exists ({existing['id']})")

    need = Need(
        id=_next_id(registry),
        statement=statement,
        stakeholder=stakeholder,
        source_block=source_block,
        source_artifacts=source_artifacts or [],
        concept_dev_refs=concept_dev_refs or {"sources": [], "assumptions": []},
        registered_at=datetime.now(timezone.utc).isoformat(),
    )
    registry["needs"].append(asdict(need))
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)
    return need.id


_PROTECTED_FIELDS = {"id", "status", "registered_at"}


def update_need(workspace: str, need_id: str, **fields) -> None:
    """Update fields on an existing need. Protected fields (id, status, registered_at) cannot be changed."""
    registry = _load_registry(workspace)
    idx, need = _find_need(registry, need_id)

    for key, value in fields.items():
        if key in _PROTECTED_FIELDS:
            raise ValueError(f"Cannot update protected field: {key}")
        if key in need:
            need[key] = value

    if "statement" in fields:
        need["registered_at"] = datetime.now(timezone.utc).isoformat()

    registry["needs"][idx] = need
    _save_registry(workspace, registry)


def defer_need(workspace: str, need_id: str, rationale: str) -> None:
    """Set need status to deferred with rationale."""
    if not rationale or not rationale.strip():
        raise ValueError("rationale is required for defer")
    registry = _load_registry(workspace)
    idx, need = _find_need(registry, need_id)
    need["status"] = "deferred"
    need["rationale"] = rationale
    registry["needs"][idx] = need
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def reject_need(workspace: str, need_id: str, rationale: str) -> None:
    """Set need status to rejected with rationale."""
    if not rationale or not rationale.strip():
        raise ValueError("rationale is required for reject")
    registry = _load_registry(workspace)
    idx, need = _find_need(registry, need_id)
    need["status"] = "rejected"
    need["rationale"] = rationale
    registry["needs"][idx] = need
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def list_needs(workspace: str, block: str | None = None, status: str | None = None) -> list[dict]:
    """List needs with optional filters."""
    registry = _load_registry(workspace)
    results = registry["needs"]
    if block:
        results = [n for n in results if n.get("source_block") == block]
    if status:
        results = [n for n in results if n.get("status") == status]
    return results


def query_needs(workspace: str, source_ref: str | None = None, assumption_ref: str | None = None) -> list[dict]:
    """Query needs by concept-dev cross-references."""
    registry = _load_registry(workspace)
    results = []
    for need in registry["needs"]:
        refs = need.get("concept_dev_refs", {})
        if source_ref and source_ref in refs.get("sources", []):
            results.append(need)
        elif assumption_ref and assumption_ref in refs.get("assumptions", []):
            results.append(need)
    return results


def split_need(
    workspace: str,
    need_id: str,
    new_statements: list[str],
    rationale: str = "Split: original contained multiple concerns",
) -> dict:
    """Split a need into multiple new needs.

    Rejects the original (with rationale) and creates N new needs that
    inherit the original's stakeholder, source_block, source_artifacts,
    and concept_dev_refs. Each new need enters as 'approved'.

    Returns dict with:
      - rejected: the original need_id
      - created: list of new need_ids
    """
    if len(new_statements) < 2:
        raise ValueError("split requires at least 2 new statements")
    if not rationale or not rationale.strip():
        raise ValueError("rationale is required for split")

    registry = _load_registry(workspace)
    _idx, original = _find_need(registry, need_id)

    if original["status"] not in ("approved", "deferred"):
        raise ValueError(f"Cannot split a {original['status']} need")

    # Capture inherited fields
    inherited_stakeholder = original["stakeholder"]
    inherited_source_block = original["source_block"]
    inherited_source_artifacts = original.get("source_artifacts", [])
    inherited_concept_dev_refs = original.get("concept_dev_refs", {"sources": [], "assumptions": []})

    # Reject the original
    original["status"] = "rejected"
    original["rationale"] = rationale
    registry["needs"][_idx] = original
    _save_registry(workspace, registry)

    # Create new needs
    created_ids = []
    for stmt in new_statements:
        registry = _load_registry(workspace)
        need = Need(
            id=_next_id(registry),
            statement=stmt.strip(),
            stakeholder=inherited_stakeholder,
            source_block=inherited_source_block,
            source_artifacts=inherited_source_artifacts,
            concept_dev_refs=inherited_concept_dev_refs,
            registered_at=datetime.now(timezone.utc).isoformat(),
        )
        registry["needs"].append(asdict(need))
        _save_registry(workspace, registry)
        created_ids.append(need.id)

    # Final count sync
    registry = _load_registry(workspace)
    _sync_counts(workspace, registry)

    return {
        "rejected": need_id,
        "created": created_ids,
    }


def export_needs(workspace: str) -> dict:
    """Export full registry as dict."""
    return _load_registry(workspace)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage stakeholder needs registry")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    sp = subparsers.add_parser("add")
    sp.add_argument("--statement", required=True)
    sp.add_argument("--stakeholder", required=True)
    sp.add_argument("--source-block", required=True)
    sp.add_argument("--source-artifacts", default="")
    sp.add_argument("--concept-dev-refs", default=None)

    # update
    sp = subparsers.add_parser("update")
    sp.add_argument("--id", required=True)
    sp.add_argument("--statement", default=None)
    sp.add_argument("--stakeholder", default=None)

    # defer
    sp = subparsers.add_parser("defer")
    sp.add_argument("--id", required=True)
    sp.add_argument("--rationale", required=True)

    # reject
    sp = subparsers.add_parser("reject")
    sp.add_argument("--id", required=True)
    sp.add_argument("--rationale", required=True)

    # list
    sp = subparsers.add_parser("list")
    sp.add_argument("--block", default=None)
    sp.add_argument("--status", default=None)

    # query
    sp = subparsers.add_parser("query")
    sp.add_argument("--source-ref", default=None)
    sp.add_argument("--assumption-ref", default=None)

    # split
    sp = subparsers.add_parser("split")
    sp.add_argument("--id", required=True, help="ID of need to split")
    sp.add_argument("--statements", required=True, help="JSON array of new statement strings")
    sp.add_argument("--rationale", default="Split: original contained multiple concerns")

    # export
    subparsers.add_parser("export")

    args = parser.parse_args()

    if args.command == "add":
        refs = json.loads(args.concept_dev_refs) if args.concept_dev_refs else None
        artifacts = [a.strip() for a in args.source_artifacts.split(",") if a.strip()]
        need_id = add_need(
            args.workspace, args.statement, args.stakeholder,
            args.source_block, artifacts, refs,
        )
        print(json.dumps({"id": need_id}))
    elif args.command == "update":
        fields = {}
        if args.statement is not None:
            fields["statement"] = args.statement
        if args.stakeholder is not None:
            fields["stakeholder"] = args.stakeholder
        update_need(args.workspace, args.id, **fields)
        print(json.dumps({"updated": args.id}))
    elif args.command == "defer":
        defer_need(args.workspace, args.id, args.rationale)
        print(json.dumps({"deferred": args.id}))
    elif args.command == "reject":
        reject_need(args.workspace, args.id, args.rationale)
        print(json.dumps({"rejected": args.id}))
    elif args.command == "list":
        result = list_needs(args.workspace, args.block, args.status)
        print(json.dumps(result, indent=2))
    elif args.command == "query":
        result = query_needs(args.workspace, args.source_ref, args.assumption_ref)
        print(json.dumps(result, indent=2))
    elif args.command == "split":
        statements = json.loads(args.statements)
        result = split_need(args.workspace, args.id, statements, args.rationale)
        print(json.dumps(result, indent=2))
    elif args.command == "export":
        result = export_needs(args.workspace)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
