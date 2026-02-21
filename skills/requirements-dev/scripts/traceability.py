#!/usr/bin/env python3
"""Bidirectional traceability link management.

Usage:
    python3 traceability.py --workspace <path> link --source REQ-001 --target NEED-001 --type derives_from --role requirement
    python3 traceability.py --workspace <path> query --entity REQ-001 --direction both
    python3 traceability.py --workspace <path> coverage
    python3 traceability.py --workspace <path> orphans

All mutations use atomic write (temp-file-then-rename).
"""
import argparse
import json
import os
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

REGISTRY_FILENAME = "traceability_registry.json"
SCHEMA_VERSION = "1.0.0"

VALID_LINK_TYPES = {
    "derives_from", "verified_by", "sources", "informed_by",
    "allocated_to", "parent_of", "conflicts_with",
}

# Maps ID prefixes to their registry files and list keys
_ID_REGISTRY_MAP = {
    "REQ": ("requirements_registry.json", "requirements"),
    "NEED": ("needs_registry.json", "needs"),
    "SRC": ("source_registry.json", "sources"),
    "ASN": ("assumption_registry.json", "assumptions"),
}


def _load_registry(workspace: str) -> dict:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"schema_version": SCHEMA_VERSION, "links": []}


def _save_registry(workspace: str, registry: dict) -> None:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    _atomic_write(path, registry)


def _entity_exists(workspace: str, entity_id: str) -> bool:
    """Check if an entity ID exists in its corresponding registry."""
    prefix = entity_id.split("-")[0]
    entry = _ID_REGISTRY_MAP.get(prefix)
    if entry is None:
        return False
    filename, list_key = entry
    path = os.path.join(workspace, filename)
    if not os.path.isfile(path):
        return False
    with open(path) as f:
        data = json.load(f)
    return any(item["id"] == entity_id for item in data.get(list_key, []))


def link(workspace: str, source_id: str, target_id: str, link_type: str, role: str) -> None:
    """Create a traceability link with referential integrity validation."""


    if link_type not in VALID_LINK_TYPES:
        raise ValueError(f"Invalid link type '{link_type}'. Must be one of: {sorted(VALID_LINK_TYPES)}")
    if not _entity_exists(workspace, source_id):
        raise ValueError(f"Source entity not found: {source_id}")
    if not _entity_exists(workspace, target_id):
        raise ValueError(f"Target entity not found: {target_id}")

    registry = _load_registry(workspace)

    # Check for duplicate links
    for existing in registry["links"]:
        if (existing["source"] == source_id and existing["target"] == target_id
                and existing["type"] == link_type):
            return  # Already exists, no-op
    link_entry = {
        "source": source_id,
        "target": target_id,
        "type": link_type,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if link_type == "conflicts_with":
        link_entry["resolution_status"] = "open"
        link_entry["rationale"] = None

    registry["links"].append(link_entry)
    _save_registry(workspace, registry)


def query(workspace: str, entity_id: str, direction: str = "both") -> list[dict]:
    """Find all links for an entity."""

    registry = _load_registry(workspace)
    results = []
    for lnk in registry["links"]:
        if direction in ("forward", "both") and lnk["source"] == entity_id:
            results.append(lnk)
        elif direction in ("backward", "both") and lnk["target"] == entity_id:
            results.append(lnk)
    return results


def coverage_report(workspace: str) -> dict:
    """Compute traceability coverage: percentage of needs with requirements."""

    registry = _load_registry(workspace)

    # Load needs
    needs_path = os.path.join(workspace, "needs_registry.json")
    if not os.path.isfile(needs_path):
        return {"needs_covered": 0, "needs_total": 0, "coverage_pct": 0.0, "requirements_with_vv": 0}
    with open(needs_path) as f:
        needs_data = json.load(f)
    approved_needs = [n for n in needs_data.get("needs", []) if n.get("status") == "approved"]

    # Load requirements to check withdrawn status
    reqs_path = os.path.join(workspace, "requirements_registry.json")
    withdrawn_reqs = set()
    if os.path.isfile(reqs_path):
        with open(reqs_path) as f:
            reqs_data = json.load(f)
        withdrawn_reqs = {r["id"] for r in reqs_data.get("requirements", []) if r.get("status") == "withdrawn"}

    # Find needs covered by non-withdrawn requirements
    covered_needs = set()
    vv_reqs = set()
    for lnk in registry["links"]:
        if lnk["type"] == "derives_from" and lnk["source"] not in withdrawn_reqs:
            covered_needs.add(lnk["target"])
        if lnk["type"] == "verified_by" and lnk["source"] not in withdrawn_reqs:
            vv_reqs.add(lnk["source"])

    need_ids = {n["id"] for n in approved_needs}
    covered = len(covered_needs & need_ids)
    total = len(need_ids)
    pct = (covered / total * 100.0) if total > 0 else 0.0

    return {
        "needs_covered": covered,
        "needs_total": total,
        "coverage_pct": pct,
        "requirements_with_vv": len(vv_reqs),
    }


def orphan_check(workspace: str) -> dict:
    """Find needs with no requirements and requirements with no parent needs."""

    registry = _load_registry(workspace)

    # Load needs
    needs_path = os.path.join(workspace, "needs_registry.json")
    need_ids = set()
    if os.path.isfile(needs_path):
        with open(needs_path) as f:
            needs_data = json.load(f)
        need_ids = {n["id"] for n in needs_data.get("needs", []) if n.get("status") == "approved"}

    # Load requirements
    reqs_path = os.path.join(workspace, "requirements_registry.json")
    req_ids = set()
    if os.path.isfile(reqs_path):
        with open(reqs_path) as f:
            reqs_data = json.load(f)
        req_ids = {r["id"] for r in reqs_data.get("requirements", []) if r.get("status") != "withdrawn"}

    # Find covered needs and linked requirements via derives_from
    covered_needs = set()
    linked_reqs = set()
    for lnk in registry["links"]:
        if lnk["type"] == "derives_from":
            covered_needs.add(lnk["target"])
            linked_reqs.add(lnk["source"])

    orphan_needs = sorted(need_ids - covered_needs)
    orphan_requirements = sorted(req_ids - linked_reqs)

    return {
        "orphan_needs": orphan_needs,
        "orphan_requirements": orphan_requirements,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage traceability links")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # link
    sp = subparsers.add_parser("link")
    sp.add_argument("--source", required=True)
    sp.add_argument("--target", required=True)
    sp.add_argument("--type", required=True)
    sp.add_argument("--role", required=True)

    # query
    sp = subparsers.add_parser("query")
    sp.add_argument("--entity", required=True)
    sp.add_argument("--direction", default="both", choices=["forward", "backward", "both"])

    # coverage
    subparsers.add_parser("coverage")

    # orphans
    subparsers.add_parser("orphans")

    args = parser.parse_args()

    if args.command == "link":
        link(args.workspace, args.source, args.target, args.type, args.role)
        print(json.dumps({"linked": f"{args.source} -> {args.target}"}))
    elif args.command == "query":
        result = query(args.workspace, args.entity, args.direction)
        print(json.dumps(result, indent=2))
    elif args.command == "coverage":
        result = coverage_report(args.workspace)
        print(json.dumps(result, indent=2))
    elif args.command == "orphans":
        result = orphan_check(args.workspace)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
