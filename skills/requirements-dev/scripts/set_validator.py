#!/usr/bin/env python3
"""Cross-block set validation for requirements.

Usage:
    python3 set_validator.py --workspace .requirements-dev/ validate
    python3 set_validator.py --workspace .requirements-dev/ check-interfaces
    python3 set_validator.py --workspace .requirements-dev/ check-duplicates
    python3 set_validator.py --workspace .requirements-dev/ check-terminology
    python3 set_validator.py --workspace .requirements-dev/ check-coverage
    python3 set_validator.py --workspace .requirements-dev/ check-tbd
"""
import argparse
import json
import math
import os
import re
import sys

from shared_io import _validate_dir_path

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "must", "need", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "during", "before", "after", "and", "but", "or", "nor", "not", "so",
    "yet", "both", "either", "neither", "each", "every", "all", "any",
    "few", "more", "most", "other", "some", "such", "no", "only", "own",
    "same", "than", "too", "very", "that", "this", "these", "those",
    "it", "its", "which", "who", "whom", "whose",
}

# Known synonym groups for terminology checking
KNOWN_SYNONYMS = [
    {"user", "users", "end-user", "end-users", "enduser", "endusers", "client", "clients"},
    {"admin", "administrator", "administrators", "admins"},
    {"log", "logging", "audit", "auditing"},
]


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words, stripping punctuation."""
    return re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*', text.lower())


def compute_ngram_similarity(text_a: str, text_b: str, n_sizes: tuple = (1, 2)) -> float:
    """Compute cosine similarity using word-level n-gram frequency vectors."""
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)

    def _ngrams(tokens, n):
        return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

    def _freq_vector(tokens):
        vec = {}
        for n in n_sizes:
            for ng in _ngrams(tokens, n):
                vec[ng] = vec.get(ng, 0) + 1
        return vec

    vec_a = _freq_vector(tokens_a)
    vec_b = _freq_vector(tokens_b)

    # Cosine similarity
    all_keys = set(vec_a) | set(vec_b)
    if not all_keys:
        return 0.0

    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in all_keys)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


def check_interface_coverage(blocks: dict, requirements: list[dict]) -> list[dict]:
    """For every block-to-block relationship, verify interface requirements exist."""
    findings = []
    seen_pairs = set()

    for block_name, block_data in blocks.items():
        relationships = block_data.get("relationships", [])
        for related_block in relationships:
            pair = tuple(sorted([block_name, related_block]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            # Check if any interface requirement connects these specific blocks
            has_interface = False
            for req in requirements:
                if req.get("status") == "withdrawn":
                    continue
                if req.get("type") == "interface":
                    req_block = req.get("source_block", "")
                    if req_block in pair:
                        # Verify the requirement references the OTHER block
                        other_block = pair[1] if req_block == pair[0] else pair[0]
                        statement_lower = req.get("statement", "").lower()
                        if other_block.lower() in statement_lower:
                            has_interface = True
                            break

            findings.append({
                "block_a": pair[0],
                "block_b": pair[1],
                "status": "covered" if has_interface else "missing",
            })

    return findings


def check_duplicates(requirements: list[dict], threshold: float = 0.8) -> list[dict]:
    """Compare requirement statements across blocks using n-gram cosine similarity."""
    findings = []
    active_reqs = [r for r in requirements if r.get("status") != "withdrawn"]

    for i in range(len(active_reqs)):
        for j in range(i + 1, len(active_reqs)):
            req_a = active_reqs[i]
            req_b = active_reqs[j]

            # Only compare across different blocks
            if req_a.get("source_block") == req_b.get("source_block"):
                continue

            sim = compute_ngram_similarity(req_a["statement"], req_b["statement"])
            if sim >= threshold:
                status = "duplicate" if sim >= 0.95 else "near_duplicate"
                findings.append({
                    "req_a": req_a["id"],
                    "req_b": req_b["id"],
                    "similarity": round(sim, 3),
                    "status": status,
                })

    return findings


def check_terminology(requirements: list[dict]) -> list[dict]:
    """Flag inconsistent terminology across blocks."""
    findings = []
    active_reqs = [r for r in requirements if r.get("status") != "withdrawn"]

    # Build term-to-blocks map
    term_blocks = {}  # term -> set of blocks
    for req in active_reqs:
        block = req.get("source_block", "unknown")
        words = set(_tokenize(req["statement"])) - STOP_WORDS
        for word in words:
            term_blocks.setdefault(word, set()).add(block)

    # Check against known synonym groups
    for synonym_group in KNOWN_SYNONYMS:
        found_terms = {}
        for term in synonym_group:
            if term in term_blocks:
                found_terms[term] = term_blocks[term]

        if len(found_terms) > 1:
            all_blocks = set()
            for blocks in found_terms.values():
                all_blocks.update(blocks)
            findings.append({
                "term_variants": sorted(found_terms.keys()),
                "blocks_affected": sorted(all_blocks),
            })

    return findings


def check_uncovered_needs(needs: list[dict], traceability_links: list[dict]) -> list[dict]:
    """Find approved needs with no derived requirements."""
    covered_needs = set()
    for link in traceability_links:
        if link.get("type") == "derives_from":
            covered_needs.add(link["target"])

    findings = []
    for need in needs:
        if need.get("status") != "approved":
            continue
        if need["id"] not in covered_needs:
            findings.append({"id": need["id"], "statement": need["statement"]})

    return findings


def check_tbd_tbr(requirements: list[dict]) -> dict:
    """List open TBD/TBR items."""
    open_tbd = []
    open_tbr = []
    resolved_count = 0

    for req in requirements:
        if req.get("status") == "withdrawn":
            continue
        tbd_tbr = req.get("tbd_tbr")
        if tbd_tbr is None:
            continue
        if isinstance(tbd_tbr, dict):
            tbd_val = tbd_tbr.get("tbd")
            tbr_val = tbd_tbr.get("tbr")
            if tbd_val:
                open_tbd.append({"id": req["id"], "tbd": tbd_val})
            if tbr_val:
                open_tbr.append({"id": req["id"], "tbr": tbr_val})
            if not tbd_val and not tbr_val:
                resolved_count += 1

    return {"open_tbd": open_tbd, "open_tbr": open_tbr, "resolved_count": resolved_count}


def check_incose_set_characteristics(workspace_path: str) -> dict:
    """Run INCOSE C10-C15 set characteristic validation."""
    needs_data = _load_json(os.path.join(workspace_path, "needs_registry.json"))
    reqs_data = _load_json(os.path.join(workspace_path, "requirements_registry.json"))
    trace_data = _load_json(os.path.join(workspace_path, "traceability_registry.json"))

    needs = needs_data.get("needs", [])
    requirements = reqs_data.get("requirements", [])
    links = trace_data.get("links", [])
    active_reqs = [r for r in requirements if r.get("status") != "withdrawn"]

    # C10: Completeness - all approved needs traced to requirements
    uncovered = check_uncovered_needs(needs, links)
    c10 = {"passed": len(uncovered) == 0, "findings": uncovered}

    # C11: Consistency - no unresolved conflicts
    conflicts = [l for l in links if l.get("type") == "conflicts_with" and l.get("resolution_status") != "resolved"]
    c11 = {"passed": len(conflicts) == 0, "findings": conflicts}

    # C12: Feasibility - requires skeptic review
    c12 = {"passed": None, "findings": [], "note": "requires_skeptic_review"}

    # C13: Comprehensibility - terminology consistency
    term_findings = check_terminology(active_reqs)
    c13 = {"passed": len(term_findings) == 0, "findings": term_findings}

    # C14: Validatability - all requirements should have V&V methods
    reqs_without_vv = []
    vv_linked = set()
    for l in links:
        if l.get("type") == "verified_by":
            vv_linked.add(l["source"])
    for req in active_reqs:
        if req["id"] not in vv_linked:
            reqs_without_vv.append({"id": req["id"], "statement": req["statement"]})
    c14 = {"passed": len(reqs_without_vv) == 0, "findings": reqs_without_vv}

    # C15: Correctness - all requirements derive from approved needs
    approved_needs = {n["id"] for n in needs if n.get("status") == "approved"}
    derived_from_approved = set()
    for l in links:
        if l.get("type") == "derives_from" and l["target"] in approved_needs:
            derived_from_approved.add(l["source"])
    reqs_not_derived = []
    for req in active_reqs:
        if req["id"] not in derived_from_approved:
            reqs_not_derived.append({"id": req["id"]})
    c15 = {"passed": len(reqs_not_derived) == 0, "findings": reqs_not_derived}

    return {
        "c10_completeness": c10,
        "c11_consistency": c11,
        "c12_feasibility": c12,
        "c13_comprehensibility": c13,
        "c14_validatability": c14,
        "c15_correctness": c15,
    }


def validate_all(workspace_path: str) -> dict:
    """Run all set validation checks."""
    state = _load_json(os.path.join(workspace_path, "state.json"))
    needs_data = _load_json(os.path.join(workspace_path, "needs_registry.json"))
    reqs_data = _load_json(os.path.join(workspace_path, "requirements_registry.json"))
    trace_data = _load_json(os.path.join(workspace_path, "traceability_registry.json"))

    requirements = reqs_data.get("requirements", [])
    needs = needs_data.get("needs", [])
    links = trace_data.get("links", [])

    return {
        "interface_coverage": check_interface_coverage(state.get("blocks", {}), requirements),
        "duplicates": check_duplicates(requirements),
        "terminology": check_terminology(requirements),
        "uncovered_needs": check_uncovered_needs(needs, links),
        "tbd_tbr": check_tbd_tbr(requirements),
        "incose_set": check_incose_set_characteristics(workspace_path),
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Cross-block set validation")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate")
    subparsers.add_parser("check-interfaces")
    subparsers.add_parser("check-duplicates")
    subparsers.add_parser("check-terminology")
    subparsers.add_parser("check-coverage")
    subparsers.add_parser("check-tbd")

    args = parser.parse_args()
    ws = args.workspace

    if args.command == "validate":
        result = validate_all(ws)
        print(json.dumps(result, indent=2))
    elif args.command == "check-interfaces":
        state = _load_json(os.path.join(ws, "state.json"))
        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
        print(json.dumps(check_interface_coverage(state.get("blocks", {}), reqs), indent=2))
    elif args.command == "check-duplicates":
        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
        print(json.dumps(check_duplicates(reqs), indent=2))
    elif args.command == "check-terminology":
        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
        print(json.dumps(check_terminology(reqs), indent=2))
    elif args.command == "check-coverage":
        needs = _load_json(os.path.join(ws, "needs_registry.json"))["needs"]
        links = _load_json(os.path.join(ws, "traceability_registry.json"))["links"]
        print(json.dumps(check_uncovered_needs(needs, links), indent=2))
    elif args.command == "check-tbd":
        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
        print(json.dumps(check_tbd_tbr(reqs), indent=2))


if __name__ == "__main__":
    main()
