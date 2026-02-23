#!/usr/bin/env python3
"""Assumption lifecycle tracker for requirements development.

Usage:
    python3 assumption_tracker.py --workspace .requirements-dev/ import-from-ingestion
    python3 assumption_tracker.py --workspace .requirements-dev/ add --statement "..." --category feasibility --impact high --basis "..."
    python3 assumption_tracker.py --workspace .requirements-dev/ challenge --id ASN-001 --reason "..." --evidence "..."
    python3 assumption_tracker.py --workspace .requirements-dev/ invalidate --id ASN-001 --reason "..."
    python3 assumption_tracker.py --workspace .requirements-dev/ reaffirm --id ASN-001 --notes "..."
    python3 assumption_tracker.py --workspace .requirements-dev/ list [--status active] [--origin concept-dev]
    python3 assumption_tracker.py --workspace .requirements-dev/ summary

Manages assumptions throughout requirements development, including those
imported from concept-dev and new ones discovered during requirements work.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

REGISTRY_FILENAME = "assumptions_registry.json"
SCHEMA_VERSION = "1.0.0"

VALID_CATEGORIES = [
    "scope", "feasibility", "architecture", "technology", "constraint", "other",
]
VALID_IMPACTS = ["low", "medium", "high", "critical"]
VALID_STATUSES = ["active", "challenged", "invalidated", "reaffirmed"]
VALID_ORIGINS = ["concept-dev", "requirements-dev"]


def _load_registry(workspace: str) -> dict:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"schema_version": SCHEMA_VERSION, "assumptions": []}


def _save_registry(workspace: str, registry: dict) -> None:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    _atomic_write(path, registry)


def _next_id(registry: dict) -> str:
    existing = registry.get("assumptions", [])
    if not existing:
        return "ASN-001"
    max_num = 0
    for a in existing:
        try:
            num = int(a["id"].split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            continue
    return f"ASN-{max_num + 1:03d}"


def _find(registry: dict, asn_id: str) -> dict | None:
    for a in registry.get("assumptions", []):
        if a["id"] == asn_id:
            return a
    return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def import_from_ingestion(workspace: str) -> dict:
    """Import concept-dev assumptions from ingestion.json into local registry.

    Creates local copies with origin='concept-dev' and original_id linking
    back to the concept-dev assumption ID.

    Returns:
        dict with imported_count and skipped_count
    """
    ingestion_path = os.path.join(workspace, "ingestion.json")
    if not os.path.isfile(ingestion_path):
        return {"imported_count": 0, "skipped_count": 0, "warning": "No ingestion.json found"}

    with open(ingestion_path) as f:
        ingestion = json.load(f)

    assumption_refs = ingestion.get("assumption_refs", [])
    if not assumption_refs:
        return {"imported_count": 0, "skipped_count": 0}

    registry = _load_registry(workspace)
    existing_originals = {
        a.get("original_id") for a in registry["assumptions"] if a.get("origin") == "concept-dev"
    }

    imported = 0
    skipped = 0
    now = _now()

    for ref in assumption_refs:
        original_id = ref.get("id", "")
        if original_id in existing_originals:
            skipped += 1
            continue

        # Map concept-dev fields to local schema
        statement = ref.get("description", ref.get("statement", ""))
        category = ref.get("category", "other")
        if category not in VALID_CATEGORIES:
            category = "other"
        impact = ref.get("impact_level", ref.get("impact", "medium"))
        if impact not in VALID_IMPACTS:
            impact = "medium"
        basis = ref.get("basis", "")

        assumption = {
            "id": _next_id(registry),
            "statement": statement,
            "origin": "concept-dev",
            "original_id": original_id,
            "category": category,
            "impact": impact,
            "basis": basis,
            "status": "active",
            "challenge_reason": None,
            "challenge_evidence": None,
            "related_needs": [],
            "related_requirements": [],
            "registered_at": now,
            "updated_at": now,
        }
        registry["assumptions"].append(assumption)
        imported += 1

    _save_registry(workspace, registry)
    return {"imported_count": imported, "skipped_count": skipped}


def add_assumption(
    workspace: str,
    statement: str,
    category: str,
    impact: str,
    basis: str,
) -> str:
    """Add a new assumption discovered during requirements development.

    Returns the assigned ID.
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Must be one of: {VALID_CATEGORIES}")
    if impact not in VALID_IMPACTS:
        raise ValueError(f"Invalid impact. Must be one of: {VALID_IMPACTS}")

    registry = _load_registry(workspace)
    now = _now()

    assumption = {
        "id": _next_id(registry),
        "statement": statement,
        "origin": "requirements-dev",
        "original_id": None,
        "category": category,
        "impact": impact,
        "basis": basis,
        "status": "active",
        "challenge_reason": None,
        "challenge_evidence": None,
        "related_needs": [],
        "related_requirements": [],
        "registered_at": now,
        "updated_at": now,
    }
    registry["assumptions"].append(assumption)
    _save_registry(workspace, registry)
    return assumption["id"]


def challenge_assumption(
    workspace: str,
    asn_id: str,
    reason: str,
    evidence: str = "",
) -> None:
    """Mark an assumption as challenged with rationale."""
    registry = _load_registry(workspace)
    a = _find(registry, asn_id)
    if not a:
        raise ValueError(f"Assumption {asn_id} not found")
    a["status"] = "challenged"
    a["challenge_reason"] = reason
    a["challenge_evidence"] = evidence
    a["updated_at"] = _now()
    _save_registry(workspace, registry)


def invalidate_assumption(workspace: str, asn_id: str, reason: str) -> None:
    """Mark an assumption as invalidated."""
    registry = _load_registry(workspace)
    a = _find(registry, asn_id)
    if not a:
        raise ValueError(f"Assumption {asn_id} not found")
    a["status"] = "invalidated"
    a["challenge_reason"] = reason
    a["updated_at"] = _now()
    _save_registry(workspace, registry)


def reaffirm_assumption(workspace: str, asn_id: str, notes: str = "") -> None:
    """Reaffirm an assumption (typically after challenge review)."""
    registry = _load_registry(workspace)
    a = _find(registry, asn_id)
    if not a:
        raise ValueError(f"Assumption {asn_id} not found")
    a["status"] = "reaffirmed"
    a["challenge_reason"] = notes if notes else a.get("challenge_reason")
    a["updated_at"] = _now()
    _save_registry(workspace, registry)


def list_assumptions(
    workspace: str,
    status: str | None = None,
    origin: str | None = None,
) -> list[dict]:
    """List assumptions with optional filtering."""
    registry = _load_registry(workspace)
    results = registry["assumptions"]
    if status:
        results = [a for a in results if a["status"] == status]
    if origin:
        results = [a for a in results if a["origin"] == origin]
    return results


def summary(workspace: str) -> dict:
    """Get assumption status summary."""
    registry = _load_registry(workspace)
    assumptions = registry["assumptions"]
    total = len(assumptions)

    by_status = {}
    for s in VALID_STATUSES:
        by_status[s] = sum(1 for a in assumptions if a["status"] == s)

    by_origin = {}
    for o in VALID_ORIGINS:
        by_origin[o] = sum(1 for a in assumptions if a["origin"] == o)

    by_impact = {}
    for i in VALID_IMPACTS:
        by_impact[i] = sum(1 for a in assumptions if a["impact"] == i)

    high_impact_active = sum(
        1 for a in assumptions
        if a["impact"] in ("high", "critical") and a["status"] == "active"
    )

    return {
        "total": total,
        "by_status": by_status,
        "by_origin": by_origin,
        "by_impact": by_impact,
        "high_impact_active": high_impact_active,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage assumptions for requirements development")
    parser.add_argument(
        "--workspace", required=True, type=_validate_dir_path,
        help="Path to .requirements-dev/ directory",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # import-from-ingestion
    subparsers.add_parser("import-from-ingestion")

    # add
    sp = subparsers.add_parser("add")
    sp.add_argument("--statement", required=True)
    sp.add_argument("--category", required=True, choices=VALID_CATEGORIES)
    sp.add_argument("--impact", required=True, choices=VALID_IMPACTS)
    sp.add_argument("--basis", required=True)

    # challenge
    sp = subparsers.add_parser("challenge")
    sp.add_argument("--id", required=True)
    sp.add_argument("--reason", required=True)
    sp.add_argument("--evidence", default="")

    # invalidate
    sp = subparsers.add_parser("invalidate")
    sp.add_argument("--id", required=True)
    sp.add_argument("--reason", required=True)

    # reaffirm
    sp = subparsers.add_parser("reaffirm")
    sp.add_argument("--id", required=True)
    sp.add_argument("--notes", default="")

    # list
    sp = subparsers.add_parser("list")
    sp.add_argument("--status", choices=VALID_STATUSES)
    sp.add_argument("--origin", choices=VALID_ORIGINS)

    # summary
    subparsers.add_parser("summary")

    args = parser.parse_args()

    if args.command == "import-from-ingestion":
        result = import_from_ingestion(args.workspace)
        print(json.dumps(result, indent=2))
    elif args.command == "add":
        asn_id = add_assumption(
            args.workspace, args.statement, args.category, args.impact, args.basis,
        )
        print(json.dumps({"id": asn_id}))
    elif args.command == "challenge":
        challenge_assumption(args.workspace, args.id, args.reason, args.evidence)
        print(json.dumps({"status": "challenged", "id": args.id}))
    elif args.command == "invalidate":
        invalidate_assumption(args.workspace, args.id, args.reason)
        print(json.dumps({"status": "invalidated", "id": args.id}))
    elif args.command == "reaffirm":
        reaffirm_assumption(args.workspace, args.id, args.notes)
        print(json.dumps({"status": "reaffirmed", "id": args.id}))
    elif args.command == "list":
        result = list_assumptions(args.workspace, args.status, args.origin)
        print(json.dumps(result, indent=2))
    elif args.command == "summary":
        result = summary(args.workspace)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
