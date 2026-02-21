#!/usr/bin/env python3
"""Subsystem decomposition logic for requirements-dev plugin.

Manages block decomposition into sub-blocks, requirement allocation
to sub-blocks, coverage validation, and decomposition state tracking.

Usage:
    python3 decompose.py --workspace .requirements-dev/ validate-baseline --block block-name
    python3 decompose.py --workspace .requirements-dev/ register-sub-blocks --parent block-name --sub-blocks '[...]' --level 1
    python3 decompose.py --workspace .requirements-dev/ allocate --requirement REQ-001 --sub-block graph-engine --rationale "..."
    python3 decompose.py --workspace .requirements-dev/ validate-coverage --block block-name
    python3 decompose.py --workspace .requirements-dev/ check-level --level 2
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def validate_baseline(workspace: str, block_name: str) -> bool:
    """Check that all requirements for the given block have status 'baselined'.

    Returns True if all are baselined, False otherwise.
    Raises ValueError if block has no requirements.
    """

    reqs = _load_json(os.path.join(workspace, "requirements_registry.json"))
    block_reqs = [r for r in reqs["requirements"]
                  if r.get("source_block") == block_name and r.get("status") != "withdrawn"]
    if not block_reqs:
        raise ValueError(f"Block '{block_name}' has no requirements")
    return all(r["status"] == "baselined" for r in block_reqs)


def check_max_level(workspace: str, current_level: int) -> bool:
    """Check whether decomposition at current_level + 1 would exceed max_level.

    Returns True if allowed, False if would exceed.
    """

    state = _load_json(os.path.join(workspace, "state.json"))
    max_level = state.get("decomposition", {}).get("max_level", 3)
    return current_level + 1 <= max_level


def register_sub_blocks(workspace: str, parent_block: str,
                        sub_blocks: list[dict], level: int) -> None:
    """Register sub-blocks in state.json.

    Each sub_block dict has: name, description.
    Adds each sub-block to blocks dict with level and parent_block fields.
    """

    state_path = os.path.join(workspace, "state.json")
    state = _load_json(state_path)

    for sb in sub_blocks:
        state["blocks"][sb["name"]] = {
            "name": sb["name"],
            "description": sb["description"],
            "relationships": [],
            "level": level,
            "parent_block": parent_block,
        }

    _atomic_write(state_path, state)


def allocate_requirement(workspace: str, requirement_id: str,
                         sub_block_name: str, rationale: str) -> None:
    """Allocate a parent requirement to a sub-block.

    Creates an allocated_to link in the traceability registry.
    Validates that the requirement exists and is baselined.
    """


    # Validate requirement exists and is baselined
    reqs = _load_json(os.path.join(workspace, "requirements_registry.json"))
    req = next((r for r in reqs["requirements"] if r["id"] == requirement_id), None)
    if req is None:
        raise ValueError(f"Requirement '{requirement_id}' not found")
    if req["status"] != "baselined":
        raise ValueError(f"Requirement '{requirement_id}' is not baselined (status: {req['status']})")

    trace_path = os.path.join(workspace, "traceability_registry.json")
    trace = _load_json(trace_path)

    # Check for duplicate
    for existing in trace["links"]:
        if (existing["source"] == requirement_id
                and existing["target"] == sub_block_name
                and existing["type"] == "allocated_to"):
            return  # Already allocated

    link_entry = {
        "source": requirement_id,
        "target": sub_block_name,
        "type": "allocated_to",
        "role": "requirement",
        "rationale": rationale,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    trace["links"].append(link_entry)
    _atomic_write(trace_path, trace)


def validate_allocation_coverage(workspace: str, parent_block: str) -> dict:
    """Check that every baselined requirement of parent_block is allocated.

    Returns dict with coverage, allocated, unallocated, and total.
    """

    reqs = _load_json(os.path.join(workspace, "requirements_registry.json"))
    trace = _load_json(os.path.join(workspace, "traceability_registry.json"))

    block_reqs = [r for r in reqs["requirements"]
                  if r.get("source_block") == parent_block
                  and r.get("status") == "baselined"]

    allocated_ids = set()
    for link in trace["links"]:
        if link["type"] == "allocated_to":
            allocated_ids.add(link["source"])

    allocated = [r["id"] for r in block_reqs if r["id"] in allocated_ids]
    unallocated = [r["id"] for r in block_reqs if r["id"] not in allocated_ids]
    total = len(block_reqs)
    coverage = len(allocated) / total if total > 0 else 0.0

    return {
        "coverage": coverage,
        "allocated": allocated,
        "unallocated": unallocated,
        "total": total,
    }


def update_decomposition_state(workspace: str, level: int,
                               parent_block: str, sub_blocks: list[str],
                               coverage: float) -> None:
    """Update the decomposition section in state.json."""

    state_path = os.path.join(workspace, "state.json")
    state = _load_json(state_path)

    if "decomposition" not in state:
        state["decomposition"] = {"levels": {}, "max_level": 3}

    state["decomposition"]["levels"][str(level)] = {
        "parent_block": parent_block,
        "sub_blocks": sub_blocks,
        "allocation_coverage": coverage,
    }

    _atomic_write(state_path, state)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Subsystem decomposition")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("validate-baseline")
    sp.add_argument("--block", required=True)

    sp = subparsers.add_parser("register-sub-blocks")
    sp.add_argument("--parent", required=True)
    sp.add_argument("--sub-blocks", required=True, help="JSON array of sub-block objects")
    sp.add_argument("--level", type=int, required=True)

    sp = subparsers.add_parser("allocate")
    sp.add_argument("--requirement", required=True)
    sp.add_argument("--sub-block", required=True)
    sp.add_argument("--rationale", required=True)

    sp = subparsers.add_parser("validate-coverage")
    sp.add_argument("--block", required=True)

    sp = subparsers.add_parser("check-level")
    sp.add_argument("--level", type=int, required=True)

    args = parser.parse_args()
    ws = args.workspace

    if args.command == "validate-baseline":
        result = validate_baseline(ws, args.block)
        print(json.dumps({"valid": result}))
    elif args.command == "register-sub-blocks":
        sub_blocks = json.loads(args.sub_blocks)
        register_sub_blocks(ws, args.parent, sub_blocks, args.level)
        print(json.dumps({"registered": len(sub_blocks)}))
    elif args.command == "allocate":
        allocate_requirement(ws, args.requirement, args.sub_block, args.rationale)
        print(json.dumps({"allocated": args.requirement, "to": args.sub_block}))
    elif args.command == "validate-coverage":
        result = validate_allocation_coverage(ws, args.block)
        print(json.dumps(result, indent=2))
    elif args.command == "check-level":
        allowed = check_max_level(ws, args.level)
        print(json.dumps({"allowed": allowed, "requested_level": args.level + 1}))


if __name__ == "__main__":
    main()
