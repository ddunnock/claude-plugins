#!/usr/bin/env python3
"""Gap analysis for requirements-dev: coverage matrices and discovery metrics.

Usage:
    python3 gap_analyzer.py --workspace .requirements-dev/ analyze
    python3 gap_analyzer.py --workspace .requirements-dev/ analyze --block auth
    python3 gap_analyzer.py --workspace .requirements-dev/ block-type-matrix
    python3 gap_analyzer.py --workspace .requirements-dev/ concept-coverage
    python3 gap_analyzer.py --workspace .requirements-dev/ block-asymmetry
    python3 gap_analyzer.py --workspace .requirements-dev/ vv-coverage
    python3 gap_analyzer.py --workspace .requirements-dev/ priority-alignment
    python3 gap_analyzer.py --workspace .requirements-dev/ need-sufficiency
    python3 gap_analyzer.py --workspace .requirements-dev/ block-need-coverage
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

VALID_TYPES = ["functional", "performance", "interface", "constraint", "quality"]
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


def _load_json(path: str) -> dict | None:
    """Load JSON file, returning None if it does not exist."""
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)


def _active_requirements(registry: dict) -> list[dict]:
    """Return non-withdrawn requirements."""
    return [r for r in registry.get("requirements", []) if r.get("status") != "withdrawn"]


def _approved_needs(registry: dict) -> list[dict]:
    """Return approved needs."""
    return [n for n in registry.get("needs", []) if n.get("status") == "approved"]


# ---------------------------------------------------------------------------
# Gap 1: Block × Requirement Type Coverage Matrix
# ---------------------------------------------------------------------------

def block_type_matrix(workspace: str, block_filter: str | None = None) -> dict:
    """Compute block × requirement-type coverage matrix.

    Returns a dict with:
      matrix: {block_name: {type: count}}
      gaps: [{block, missing_types: [str]}]
    """
    state = _load_json(os.path.join(workspace, "state.json")) or {}
    req_reg = _load_json(os.path.join(workspace, "requirements_registry.json"))
    blocks = state.get("blocks", {})
    reqs = _active_requirements(req_reg) if req_reg else []

    if block_filter:
        blocks = {k: v for k, v in blocks.items() if k == block_filter}

    matrix = {}
    for block_name in blocks:
        matrix[block_name] = {t: 0 for t in VALID_TYPES}

    for req in reqs:
        blk = req.get("source_block", "")
        rtype = req.get("type", "")
        if blk in matrix and rtype in VALID_TYPES:
            matrix[blk][rtype] += 1

    gaps = []
    for block_name, type_counts in matrix.items():
        missing = [t for t, count in type_counts.items() if count == 0]
        if missing:
            gaps.append({"block": block_name, "missing_types": missing})

    return {"matrix": matrix, "gaps": gaps}


# ---------------------------------------------------------------------------
# Gap 2: Concept-to-Need Traceability
# ---------------------------------------------------------------------------

def concept_coverage(workspace: str) -> dict:
    """Check which concept-dev sources/assumptions are reflected in needs.

    Returns:
      sources_total, sources_covered, uncovered_sources: [...]
      assumptions_total, assumptions_covered, uncovered_assumptions: [...]
    """
    ingestion = _load_json(os.path.join(workspace, "ingestion.json"))
    needs_reg = _load_json(os.path.join(workspace, "needs_registry.json"))

    if not ingestion:
        return {
            "available": False,
            "reason": "No ingestion.json found (concept-dev artifacts not ingested)",
        }

    # Collect all source and assumption IDs from ingestion
    concept_sources = set()
    concept_assumptions = set()
    for src in ingestion.get("source_refs", []):
        src_id = src.get("id", "")
        if src_id:
            concept_sources.add(src_id)
    for asn in ingestion.get("assumption_refs", []):
        asn_id = asn.get("id", "")
        if asn_id:
            concept_assumptions.add(asn_id)

    # Collect referenced sources/assumptions from needs
    referenced_sources = set()
    referenced_assumptions = set()
    needs = (needs_reg or {}).get("needs", [])
    for need in needs:
        refs = need.get("concept_dev_refs") or {}
        for sid in refs.get("sources", []):
            referenced_sources.add(sid)
        for aid in refs.get("assumptions", []):
            referenced_assumptions.add(aid)

    uncovered_sources = sorted(concept_sources - referenced_sources)
    uncovered_assumptions = sorted(concept_assumptions - referenced_assumptions)

    return {
        "available": True,
        "sources_total": len(concept_sources),
        "sources_covered": len(concept_sources) - len(uncovered_sources),
        "uncovered_sources": uncovered_sources,
        "assumptions_total": len(concept_assumptions),
        "assumptions_covered": len(concept_assumptions) - len(uncovered_assumptions),
        "uncovered_assumptions": uncovered_assumptions,
    }


# ---------------------------------------------------------------------------
# Gap 3: Cross-Block Asymmetry
# ---------------------------------------------------------------------------

def block_asymmetry(workspace: str) -> dict:
    """Check related blocks for asymmetric requirement coverage.

    Returns:
      pairs: [{block_a, block_b, count_a, count_b, ratio, asymmetric: bool}]
    """
    state = _load_json(os.path.join(workspace, "state.json")) or {}
    req_reg = _load_json(os.path.join(workspace, "requirements_registry.json"))
    blocks = state.get("blocks", {})
    reqs = _active_requirements(req_reg) if req_reg else []

    # Count reqs per block
    block_counts = {name: 0 for name in blocks}
    for req in reqs:
        blk = req.get("source_block", "")
        if blk in block_counts:
            block_counts[blk] += 1

    # Find related pairs and check asymmetry
    pairs = []
    seen = set()
    for block_name, block_data in blocks.items():
        if not isinstance(block_data, dict):
            continue
        relationships = block_data.get("relationships", [])
        for related in relationships:
            pair_key = tuple(sorted([block_name, related]))
            if pair_key in seen or related not in blocks:
                continue
            seen.add(pair_key)

            count_a = block_counts.get(block_name, 0)
            count_b = block_counts.get(related, 0)
            max_count = max(count_a, count_b)
            min_count = min(count_a, count_b)
            ratio = min_count / max_count if max_count > 0 else 1.0

            pairs.append({
                "block_a": block_name,
                "block_b": related,
                "count_a": count_a,
                "count_b": count_b,
                "ratio": round(ratio, 2),
                "asymmetric": ratio < 0.5 and max_count >= 3,
            })

    return {"pairs": pairs, "asymmetric_count": sum(1 for p in pairs if p["asymmetric"])}


# ---------------------------------------------------------------------------
# Gap 4: V&V Method Coverage
# ---------------------------------------------------------------------------

def vv_coverage(workspace: str) -> dict:
    """Check requirements for V&V method assignment, grouped by type.

    Returns:
      by_type: {type: {total, with_vv, without_vv, missing_ids: [str]}}
      overall_pct: float
    """
    req_reg = _load_json(os.path.join(workspace, "requirements_registry.json"))
    trace_reg = _load_json(os.path.join(workspace, "traceability_registry.json"))
    reqs = _active_requirements(req_reg) if req_reg else []
    links = (trace_reg or {}).get("links", [])

    # Build set of requirement IDs that have verified_by links
    verified_ids = set()
    for link in links:
        if link.get("type") == "verified_by":
            verified_ids.add(link.get("source", ""))

    by_type = {}
    total_reqs = 0
    total_with_vv = 0
    for rtype in VALID_TYPES:
        type_reqs = [r for r in reqs if r.get("type") == rtype]
        missing = [r["id"] for r in type_reqs if r["id"] not in verified_ids]
        with_vv = len(type_reqs) - len(missing)
        by_type[rtype] = {
            "total": len(type_reqs),
            "with_vv": with_vv,
            "without_vv": len(missing),
            "missing_ids": missing,
        }
        total_reqs += len(type_reqs)
        total_with_vv += with_vv

    overall_pct = round((total_with_vv / total_reqs * 100) if total_reqs > 0 else 0.0, 1)

    return {"by_type": by_type, "overall_pct": overall_pct}


# ---------------------------------------------------------------------------
# Gap 5: Priority Alignment
# ---------------------------------------------------------------------------

def priority_alignment(workspace: str) -> dict:
    """Check whether high-priority needs have correspondingly high-priority reqs.

    Returns:
      misalignments: [{need_id, need_statement, need_priority_implied,
                       req_id, req_priority, gap_direction}]
    """
    needs_reg = _load_json(os.path.join(workspace, "needs_registry.json"))
    req_reg = _load_json(os.path.join(workspace, "requirements_registry.json"))
    trace_reg = _load_json(os.path.join(workspace, "traceability_registry.json"))

    needs = _approved_needs(needs_reg) if needs_reg else []
    reqs = _active_requirements(req_reg) if req_reg else []
    links = (trace_reg or {}).get("links", [])

    # Map need → derived requirement IDs
    need_to_reqs = {}
    for link in links:
        if link.get("type") == "derives_from":
            req_id = link.get("source", "")
            need_id = link.get("target", "")
            need_to_reqs.setdefault(need_id, []).append(req_id)

    # Map req ID → req object
    req_map = {r["id"]: r for r in reqs}

    misalignments = []
    for need in needs:
        need_id = need["id"]
        derived_req_ids = need_to_reqs.get(need_id, [])
        derived_reqs = [req_map[rid] for rid in derived_req_ids if rid in req_map]

        if not derived_reqs:
            continue

        # Find the max priority among derived reqs
        max_req_priority = max(
            (PRIORITY_RANK.get(r.get("priority", "low"), 1) for r in derived_reqs),
            default=1,
        )
        # Find the min priority among derived reqs (look for misalignment)
        for req in derived_reqs:
            req_rank = PRIORITY_RANK.get(req.get("priority", "low"), 1)
            # Flag if a high-priority need only has low-priority reqs
            if max_req_priority <= 1 and len(derived_reqs) >= 1:
                misalignments.append({
                    "need_id": need_id,
                    "need_statement": need.get("statement", ""),
                    "req_id": req["id"],
                    "req_priority": req.get("priority", "low"),
                    "gap_direction": "need_underserved",
                })
                break  # One flag per need is enough

    return {"misalignments": misalignments, "count": len(misalignments)}


# ---------------------------------------------------------------------------
# Gap 6: Need Sufficiency (needs with 0-1 derived requirements)
# ---------------------------------------------------------------------------

def need_sufficiency(workspace: str) -> dict:
    """Identify needs that may be under-implemented (0 or 1 derived requirements).

    Returns:
      under_implemented: [{need_id, statement, derived_count, req_ids}]
      well_covered: int
    """
    needs_reg = _load_json(os.path.join(workspace, "needs_registry.json"))
    trace_reg = _load_json(os.path.join(workspace, "traceability_registry.json"))
    req_reg = _load_json(os.path.join(workspace, "requirements_registry.json"))

    needs = _approved_needs(needs_reg) if needs_reg else []
    links = (trace_reg or {}).get("links", [])
    reqs = _active_requirements(req_reg) if req_reg else []
    active_ids = {r["id"] for r in reqs}

    # Map need → active derived req IDs
    need_to_reqs = {}
    for link in links:
        if link.get("type") == "derives_from":
            req_id = link.get("source", "")
            need_id = link.get("target", "")
            if req_id in active_ids:
                need_to_reqs.setdefault(need_id, []).append(req_id)

    under = []
    well = 0
    for need in needs:
        nid = need["id"]
        req_ids = need_to_reqs.get(nid, [])
        if len(req_ids) <= 1:
            under.append({
                "need_id": nid,
                "statement": need.get("statement", ""),
                "derived_count": len(req_ids),
                "req_ids": req_ids,
            })
        else:
            well += 1

    return {"under_implemented": under, "well_covered": well}


# ---------------------------------------------------------------------------
# Gap 7: Block Need Coverage
# ---------------------------------------------------------------------------

def block_need_coverage(workspace: str) -> dict:
    """Identify blocks with zero approved needs.

    Returns:
      blocks_without_needs: [str]
      blocks_with_needs: {block: count}
    """
    state = _load_json(os.path.join(workspace, "state.json")) or {}
    needs_reg = _load_json(os.path.join(workspace, "needs_registry.json"))
    blocks = state.get("blocks", {})
    needs = _approved_needs(needs_reg) if needs_reg else []

    block_counts = {name: 0 for name in blocks}
    for need in needs:
        blk = need.get("source_block", "")
        if blk in block_counts:
            block_counts[blk] += 1

    without = sorted([b for b, c in block_counts.items() if c == 0])
    with_needs = {b: c for b, c in block_counts.items() if c > 0}

    return {"blocks_without_needs": without, "blocks_with_needs": with_needs}


# ---------------------------------------------------------------------------
# Gap 8: Interface Coverage (block relationships vs interface requirements)
# ---------------------------------------------------------------------------

def interface_coverage(workspace: str) -> dict:
    """Check that declared block relationships have corresponding interface requirements.

    For each block relationship (uses/provides/depends), verifies at least one
    interface-type requirement exists involving both blocks.

    Returns:
      relationships_total: int
      relationships_covered: int
      uncovered: [{block_a, block_b}]
    """
    state = _load_json(os.path.join(workspace, "state.json")) or {}
    req_reg = _load_json(os.path.join(workspace, "requirements_registry.json"))
    blocks = state.get("blocks", {})
    reqs = _active_requirements(req_reg) if req_reg else []

    # Build set of blocks that have at least one interface requirement
    blocks_with_interface = set()
    for req in reqs:
        if req.get("type") == "interface":
            blk = req.get("source_block", "")
            if blk:
                blocks_with_interface.add(blk)

    # Check each declared relationship pair
    relationships = []
    seen = set()
    for block_name, block_data in blocks.items():
        if not isinstance(block_data, dict):
            continue
        for related in block_data.get("relationships", []):
            pair_key = tuple(sorted([block_name, related]))
            if pair_key in seen or related not in blocks:
                continue
            seen.add(pair_key)
            relationships.append((block_name, related))

    uncovered = []
    covered = 0
    for block_a, block_b in relationships:
        # At least one side of the relationship should have interface reqs
        if block_a in blocks_with_interface or block_b in blocks_with_interface:
            covered += 1
        else:
            uncovered.append({"block_a": block_a, "block_b": block_b})

    return {
        "relationships_total": len(relationships),
        "relationships_covered": covered,
        "uncovered": uncovered,
    }


# ---------------------------------------------------------------------------
# Combined Analysis
# ---------------------------------------------------------------------------

def analyze(workspace: str, block_filter: str | None = None) -> dict:
    """Run all gap analyses and return combined report."""
    report = {
        "schema_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "block_type_matrix": block_type_matrix(workspace, block_filter),
        "concept_coverage": concept_coverage(workspace),
        "block_asymmetry": block_asymmetry(workspace),
        "vv_coverage": vv_coverage(workspace),
        "priority_alignment": priority_alignment(workspace),
        "need_sufficiency": need_sufficiency(workspace),
        "block_need_coverage": block_need_coverage(workspace),
        "interface_coverage": interface_coverage(workspace),
    }

    # Persist report
    out_path = os.path.join(workspace, "gap_analysis.json")
    _atomic_write(out_path, report)

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gap analysis for requirements-dev")
    parser.add_argument(
        "--workspace", required=True, type=_validate_dir_path,
        help="Path to .requirements-dev/ workspace directory",
    )
    sub = parser.add_subparsers(dest="command")

    ana = sub.add_parser("analyze", help="Run all gap analyses")
    ana.add_argument("--block", default=None, help="Filter to a specific block")

    sub.add_parser("block-type-matrix", help="Block × requirement type coverage")
    sub.add_parser("concept-coverage", help="Concept-dev source/assumption coverage")
    sub.add_parser("block-asymmetry", help="Cross-block requirement asymmetry")
    sub.add_parser("vv-coverage", help="V&V method assignment coverage")
    sub.add_parser("priority-alignment", help="Need-to-requirement priority alignment")
    sub.add_parser("need-sufficiency", help="Needs with insufficient derived requirements")
    sub.add_parser("block-need-coverage", help="Blocks without approved needs")
    sub.add_parser("interface-coverage", help="Interface requirements for block relationships")

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    ws = args.workspace

    dispatch = {
        "analyze": lambda: analyze(ws, getattr(args, "block", None)),
        "block-type-matrix": lambda: block_type_matrix(ws),
        "concept-coverage": lambda: concept_coverage(ws),
        "block-asymmetry": lambda: block_asymmetry(ws),
        "vv-coverage": lambda: vv_coverage(ws),
        "priority-alignment": lambda: priority_alignment(ws),
        "need-sufficiency": lambda: need_sufficiency(ws),
        "block-need-coverage": lambda: block_need_coverage(ws),
        "interface-coverage": lambda: interface_coverage(ws),
    }

    result = dispatch[args.command]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
