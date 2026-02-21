#!/usr/bin/env python3
"""Requirements registry management with type-guided tracking.

Usage:
    python3 requirement_tracker.py --workspace <path> add --statement "..." --type functional --priority high --source-block blk
    python3 requirement_tracker.py --workspace <path> register --id REQ-001 --parent-need NEED-001
    python3 requirement_tracker.py --workspace <path> baseline --id REQ-001
    python3 requirement_tracker.py --workspace <path> withdraw --id REQ-001 --rationale "..."
    python3 requirement_tracker.py --workspace <path> list [--include-withdrawn]
    python3 requirement_tracker.py --workspace <path> query [--type X] [--source-block Y] [--level N]
    python3 requirement_tracker.py --workspace <path> export

All mutations use atomic write (temp-file-then-rename) and sync counts to state.json.
"""
import argparse
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

REGISTRY_FILENAME = "requirements_registry.json"
NEEDS_REGISTRY_FILENAME = "needs_registry.json"
STATE_FILENAME = "state.json"
SCHEMA_VERSION = "1.0.0"

VALID_TYPES = {"functional", "performance", "interface", "constraint", "quality"}
VALID_PRIORITIES = {"high", "medium", "low"}


@dataclass
class Requirement:
    id: str
    statement: str
    type: str
    priority: str
    status: str = "draft"
    parent_need: str = ""
    source_block: str = ""
    level: int = 0
    attributes: dict = field(default_factory=dict)
    quality_checks: dict = field(default_factory=dict)
    tbd_tbr: dict | None = None
    rationale: str | None = None
    registered_at: str = ""


def _load_registry(workspace: str) -> dict:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"schema_version": SCHEMA_VERSION, "requirements": []}


def _save_registry(workspace: str, registry: dict) -> None:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    _atomic_write(path, registry)


def _sync_counts(workspace: str, registry: dict) -> None:
    state_path = os.path.join(workspace, STATE_FILENAME)
    if not os.path.isfile(state_path):
        return
    with open(state_path) as f:
        state = json.load(f)
    reqs = registry["requirements"]
    state["counts"]["requirements_total"] = len(reqs)
    state["counts"]["requirements_registered"] = sum(1 for r in reqs if r.get("status") == "registered")
    state["counts"]["requirements_baselined"] = sum(1 for r in reqs if r.get("status") == "baselined")
    state["counts"]["requirements_withdrawn"] = sum(1 for r in reqs if r.get("status") == "withdrawn")
    _atomic_write(state_path, state)


def _next_id(registry: dict) -> str:
    existing = registry.get("requirements", [])
    if not existing:
        return "REQ-001"
    max_num = 0
    for req in existing:
        try:
            num = int(req["id"].split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            continue
    return f"REQ-{max_num + 1:03d}"


def _find_requirement(registry: dict, req_id: str) -> tuple[int, dict]:
    for i, req in enumerate(registry["requirements"]):
        if req["id"] == req_id:
            return i, req
    raise ValueError(f"Requirement not found: {req_id}")


def add_requirement(
    workspace: str,
    statement: str,
    type: str,
    priority: str,
    source_block: str,
    level: int = 0,
) -> str:
    """Add a requirement in draft status. Returns the assigned ID."""

    if type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type}'. Must be one of: {sorted(VALID_TYPES)}")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}")

    registry = _load_registry(workspace)
    req = Requirement(
        id=_next_id(registry),
        statement=statement,
        type=type,
        priority=priority,
        source_block=source_block,
        level=level,
        registered_at=datetime.now(timezone.utc).isoformat(),
    )
    registry["requirements"].append(asdict(req))
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)
    return req.id


def register_requirement(workspace: str, req_id: str, parent_need: str) -> None:
    """Transition a draft requirement to registered status."""
    if not parent_need or not parent_need.strip():
        raise ValueError("parent_need is required for registration")

    registry = _load_registry(workspace)
    idx, req = _find_requirement(registry, req_id)

    # Validate parent need exists and is approved
    needs_path = os.path.join(workspace, NEEDS_REGISTRY_FILENAME)
    if not os.path.isfile(needs_path):
        raise ValueError(f"Needs registry not found; cannot validate parent_need: {parent_need}")
    with open(needs_path) as f:
        needs_reg = json.load(f)
    approved_ids = {n["id"] for n in needs_reg.get("needs", []) if n.get("status") == "approved"}
    if parent_need not in approved_ids:
        raise ValueError(f"Parent need not found or not approved: {parent_need}")

    if req["status"] != "draft":
        raise ValueError(f"Can only register a draft requirement (current status: {req['status']})")

    req["status"] = "registered"
    req["parent_need"] = parent_need
    req["registered_at"] = datetime.now(timezone.utc).isoformat()
    registry["requirements"][idx] = req
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def baseline_requirement(workspace: str, req_id: str) -> None:
    """Transition a registered requirement to baselined status."""

    registry = _load_registry(workspace)
    idx, req = _find_requirement(registry, req_id)
    if req["status"] != "registered":
        raise ValueError(f"Can only baseline a registered requirement (current status: {req['status']})")
    req["status"] = "baselined"
    req["baselined_at"] = datetime.now(timezone.utc).isoformat()
    registry["requirements"][idx] = req
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def baseline_all(workspace: str) -> dict:
    """Baseline all registered requirements. Returns summary."""

    registry = _load_registry(workspace)
    baselined = []
    skipped_draft = []
    now = datetime.now(timezone.utc).isoformat()
    for req in registry["requirements"]:
        if req["status"] == "registered":
            req["status"] = "baselined"
            req["baselined_at"] = now
            baselined.append(req["id"])
        elif req["status"] == "draft":
            skipped_draft.append(req["id"])
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)
    return {"baselined": baselined, "skipped_draft": skipped_draft}


def withdraw_requirement(workspace: str, req_id: str, rationale: str) -> None:
    """Withdraw a requirement with rationale."""
    if not rationale or not rationale.strip():
        raise ValueError("rationale is required for withdrawal")

    registry = _load_registry(workspace)
    idx, req = _find_requirement(registry, req_id)
    req["status"] = "withdrawn"
    req["rationale"] = rationale
    registry["requirements"][idx] = req
    _save_registry(workspace, registry)
    _sync_counts(workspace, registry)


def list_requirements(workspace: str, include_withdrawn: bool = False) -> list[dict]:
    """List requirements, excluding withdrawn by default."""

    registry = _load_registry(workspace)
    results = registry["requirements"]
    if not include_withdrawn:
        results = [r for r in results if r.get("status") != "withdrawn"]
    return results


def query_requirements(
    workspace: str,
    type: str | None = None,
    source_block: str | None = None,
    level: int | None = None,
    status: str | None = None,
) -> list[dict]:
    """Query requirements with filters."""

    registry = _load_registry(workspace)
    results = registry["requirements"]
    if type is not None:
        results = [r for r in results if r.get("type") == type]
    if source_block is not None:
        results = [r for r in results if r.get("source_block") == source_block]
    if level is not None:
        results = [r for r in results if r.get("level") == level]
    if status is not None:
        results = [r for r in results if r.get("status") == status]
    return results


_PROTECTED_FIELDS = {"id", "status", "registered_at"}


def update_requirement(workspace: str, req_id: str, **fields) -> None:
    """Update fields on an existing requirement. Merges into attributes dict."""

    registry = _load_registry(workspace)
    idx, req = _find_requirement(registry, req_id)

    for key, value in fields.items():
        if key in _PROTECTED_FIELDS:
            raise ValueError(f"Cannot update protected field: {key}")
        if key == "attributes" and isinstance(value, dict):
            req.setdefault("attributes", {}).update(value)
        elif key in req:
            req[key] = value
        else:
            raise ValueError(f"Unknown field: {key}")

    registry["requirements"][idx] = req
    _save_registry(workspace, registry)


def export_requirements(workspace: str) -> dict:
    """Export full registry as dict."""

    return _load_registry(workspace)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage requirements registry")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    sp = subparsers.add_parser("add")
    sp.add_argument("--statement", required=True)
    sp.add_argument("--type", required=True, choices=sorted(VALID_TYPES))
    sp.add_argument("--priority", required=True, choices=sorted(VALID_PRIORITIES))
    sp.add_argument("--source-block", required=True)
    sp.add_argument("--level", type=int, default=0)

    # register
    sp = subparsers.add_parser("register")
    sp.add_argument("--id", required=True)
    sp.add_argument("--parent-need", required=True)

    # baseline
    sp = subparsers.add_parser("baseline")
    group = sp.add_mutually_exclusive_group(required=True)
    group.add_argument("--id")
    group.add_argument("--all", action="store_true")

    # withdraw
    sp = subparsers.add_parser("withdraw")
    sp.add_argument("--id", required=True)
    sp.add_argument("--rationale", required=True)

    # list
    sp = subparsers.add_parser("list")
    sp.add_argument("--include-withdrawn", action="store_true")

    # query
    sp = subparsers.add_parser("query")
    sp.add_argument("--type", default=None, choices=sorted(VALID_TYPES))
    sp.add_argument("--source-block", default=None)
    sp.add_argument("--level", type=int, default=None)
    sp.add_argument("--status", default=None)

    # export
    subparsers.add_parser("export")

    args = parser.parse_args()

    if args.command == "add":
        req_id = add_requirement(
            args.workspace, args.statement, args.type, args.priority,
            args.source_block, args.level,
        )
        print(json.dumps({"id": req_id}))
    elif args.command == "register":
        register_requirement(args.workspace, args.id, args.parent_need)
        print(json.dumps({"registered": args.id}))
    elif args.command == "baseline":
        if getattr(args, "all", False):
            result = baseline_all(args.workspace)
            print(json.dumps(result, indent=2))
        else:
            baseline_requirement(args.workspace, args.id)
            print(json.dumps({"baselined": args.id}))
    elif args.command == "withdraw":
        withdraw_requirement(args.workspace, args.id, args.rationale)
        print(json.dumps({"withdrawn": args.id}))
    elif args.command == "list":
        result = list_requirements(args.workspace, args.include_withdrawn)
        print(json.dumps(result, indent=2))
    elif args.command == "query":
        result = query_requirements(args.workspace, args.type, args.source_block, args.level, args.status)
        print(json.dumps(result, indent=2))
    elif args.command == "export":
        result = export_requirements(args.workspace)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
