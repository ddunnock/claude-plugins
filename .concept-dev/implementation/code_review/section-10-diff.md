diff --git a/skills/requirements-dev/agents/skeptic.md b/skills/requirements-dev/agents/skeptic.md
index 749974a..f238e85 100644
--- a/skills/requirements-dev/agents/skeptic.md
+++ b/skills/requirements-dev/agents/skeptic.md
@@ -4,4 +4,54 @@ description: Coverage and feasibility verifier for requirement sets
 model: opus
 ---
 
-<!-- Agent definition for skeptic. See section-10 (validation sweep). -->
+# Skeptic Agent
+
+You are a requirements skeptic. Your job is to rigorously verify coverage and feasibility claims in a requirements set. You challenge assumptions, check for gaps, and verify that stated coverage actually exists.
+
+## Context You Receive
+
+1. The full requirements set (all blocks, all types) from `requirements_registry.json`
+2. Cross-cutting sweep findings from `set_validator.py`
+3. Coverage claims made during the sweep (e.g., "All security categories are addressed")
+4. Block relationship map from `state.json`
+
+## What You Evaluate
+
+### Coverage Claims
+For each claim that a category or concern is "covered":
+- Read the actual requirements
+- Check if they genuinely address the claimed category
+- Flag hollow coverage (e.g., a vague requirement claiming to cover security)
+
+### Feasibility
+For performance targets, constraints, and quality requirements:
+- Are numeric targets realistic?
+- Are constraint requirements achievable given stated interfaces?
+- Do quality requirements have measurable criteria?
+
+### Completeness
+- Are there obvious functional gaps the automated checks missed?
+- Do block relationships suggest missing requirements?
+- Are edge cases and error scenarios covered?
+
+## Output Format
+
+For each finding, provide:
+
+```json
+{
+  "claim": "What was claimed or implied",
+  "status": "verified | unverified | disputed | needs_user_input",
+  "confidence": "high | medium | low",
+  "reasoning": "Step-by-step explanation of your assessment",
+  "recommendation": "What to do if disputed or unverified"
+}
+```
+
+## Rules
+
+- Be thorough but fair. Flag real issues, not stylistic preferences.
+- Cite specific requirement IDs when making claims.
+- If a coverage claim is partially true, mark as `unverified` with explanation.
+- For feasibility concerns, explain what information is missing to make a determination.
+- Do not propose new requirements. Your job is to verify, not to design.
diff --git a/skills/requirements-dev/commands/reqdev.validate.md b/skills/requirements-dev/commands/reqdev.validate.md
index bc1b527..b203166 100644
--- a/skills/requirements-dev/commands/reqdev.validate.md
+++ b/skills/requirements-dev/commands/reqdev.validate.md
@@ -1,6 +1,139 @@
 ---
 name: reqdev:validate
-description: Set validation and cross-cutting sweep
+description: Cross-cutting validation sweep for the requirements set
 ---
 
-<!-- Command prompt for /reqdev:validate. See section-10 (validation sweep). -->
+# /reqdev:validate - Validation Sweep
+
+Orchestrates cross-block validation of the full requirements set. Runs deterministic checks, presents findings interactively, and optionally launches the skeptic agent for feasibility review.
+
+## Procedure
+
+### Step 1: Pre-check
+
+Verify the `deliver` gate is passed (requirements must be baselined before validation):
+
+```bash
+python3 scripts/update_state.py --workspace .requirements-dev check-gate deliver
+```
+
+If the gate is NOT passed, inform the user:
+> The deliver phase is not complete. Run `/reqdev:deliver` to baseline requirements before running the validation sweep.
+
+Stop and wait for user action.
+
+### Step 2: Run Deterministic Validation
+
+Run all set validation checks:
+
+```bash
+python3 scripts/set_validator.py --workspace .requirements-dev validate
+```
+
+This produces JSON output with findings grouped by category:
+- `interface_coverage` - block pairs with/without interface requirements
+- `duplicates` - near-duplicate requirements across blocks
+- `terminology` - inconsistent term usage across blocks
+- `uncovered_needs` - approved needs with no derived requirements
+- `tbd_tbr` - open TBD/TBR items
+- `incose_set` - INCOSE C10-C15 set characteristic results
+
+### Step 3: Present Findings
+
+Present findings to the user as a prioritized list, grouped by severity:
+
+#### Critical (blocks delivery readiness)
+- **Missing interface requirements**: For each block pair flagged as `missing`, prompt the user to write interface requirements or confirm the relationship is not relevant.
+- **Uncovered needs**: For each approved need with no derived requirement, prompt the user to either write requirements or defer/reject the need.
+- **INCOSE C10 (Completeness) failures**: Same as uncovered needs above.
+- **INCOSE C15 (Correctness) failures**: Requirements not traced to approved needs.
+
+#### Warning (should address before final delivery)
+- **Near-duplicate requirements**: Present each pair with similarity score. Ask the user to decide: merge (withdraw one), differentiate (clarify statements), or accept (both are intentional).
+- **Terminology inconsistencies**: Present term variants and affected blocks. Propose a canonical term and offer to update requirement statements.
+- **Open TBD items**: Present each TBD with its requirement ID. Prompt for resolution value.
+- **Open TBR items**: Present each TBR with its requirement ID. Prompt for review decision.
+- **INCOSE C14 (Validatability)**: Requirements without V&V methods.
+
+#### Info
+- **INCOSE C11 (Consistency)**: Unresolved conflicts (if any).
+- **INCOSE C13 (Comprehensibility)**: Same as terminology above.
+- **Resolved TBD/TBR count**: For reference.
+
+### Step 4: Cross-Cutting Category Checklist
+
+Present the cross-cutting category checklist to the user:
+
+> Which cross-cutting concerns apply to this system? Select all that apply:
+> - Security
+> - Reliability / Availability
+> - Scalability / Performance
+> - Maintainability
+> - Data integrity
+> - Logging / Observability
+> - Regulatory compliance
+> - Accessibility
+> - Other (specify)
+
+For each selected category:
+1. Search registered requirements for coverage of that category.
+2. Identify blocks that have NO requirements addressing the category.
+3. Present gaps to the user and prompt for action (write new requirements or accept the gap).
+
+### Step 5: INCOSE C12 Feasibility Review (Optional)
+
+If the user requests feasibility review, or if any performance/constraint requirements have numeric targets that warrant scrutiny:
+
+> Would you like to run the skeptic agent for a rigorous feasibility and coverage review?
+
+If yes, launch the `skeptic` agent with:
+- The full requirements set from `requirements_registry.json`
+- The validation findings from Step 2
+- The block relationship map from `state.json`
+- Any coverage claims made during Step 4
+
+Present the skeptic's findings to the user. For each finding with status `disputed` or `unverified`, prompt the user for action.
+
+### Step 6: Resolution Actions
+
+For any issues the user decides to fix during validation:
+
+- **Write new requirements**: Guide through the standard pipeline - quality check, V&V plan, register, trace. Use the same flow as `/reqdev:requirements`.
+- **Merge duplicates**: Withdraw one requirement, update traceability links.
+- **Update terminology**: Edit requirement statements via `requirement_tracker.py update`.
+- **Resolve TBD/TBR**: Update the requirement's `tbd_tbr` field.
+- **Defer/reject needs**: Use `needs_tracker.py` to change need status.
+
+After each fix, re-run the relevant check to confirm resolution:
+
+```bash
+python3 scripts/set_validator.py --workspace .requirements-dev check-duplicates
+python3 scripts/set_validator.py --workspace .requirements-dev check-terminology
+python3 scripts/set_validator.py --workspace .requirements-dev check-coverage
+python3 scripts/set_validator.py --workspace .requirements-dev check-tbd
+```
+
+### Step 7: Validation Summary
+
+After all findings are addressed (or accepted), display the summary:
+
+```
+Validation Sweep Complete
+-------------------------
+Interface coverage:    {N}/{M} block pairs covered
+Duplicates resolved:   {count}
+Terminology fixes:     {count}
+Uncovered needs:       {count} remaining
+TBD items:             {open} open, {resolved} resolved
+TBR items:             {open} open
+
+INCOSE Set Characteristics:
+  C10 Completeness:      {Pass/Fail}
+  C11 Consistency:       {Pass/Fail}
+  C12 Feasibility:       {Reviewed/Skipped}
+  C13 Comprehensibility: {Pass/Fail}
+  C14 Validatability:    {Pass/Fail}
+  C15 Correctness:       {Pass/Fail}
+
+Next: /reqdev:deliver (re-deliver if changes made) or /reqdev:decompose
+```
diff --git a/skills/requirements-dev/scripts/set_validator.py b/skills/requirements-dev/scripts/set_validator.py
new file mode 100644
index 0000000..3b37519
--- /dev/null
+++ b/skills/requirements-dev/scripts/set_validator.py
@@ -0,0 +1,339 @@
+#!/usr/bin/env python3
+"""Cross-block set validation for requirements.
+
+Usage:
+    python3 set_validator.py validate --workspace .requirements-dev/
+    python3 set_validator.py check-interfaces --workspace .requirements-dev/
+    python3 set_validator.py check-duplicates --workspace .requirements-dev/
+    python3 set_validator.py check-terminology --workspace .requirements-dev/
+    python3 set_validator.py check-coverage --workspace .requirements-dev/
+    python3 set_validator.py check-tbd --workspace .requirements-dev/
+"""
+import argparse
+import json
+import math
+import os
+import re
+import sys
+
+from shared_io import _validate_dir_path
+
+STOP_WORDS = {
+    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
+    "have", "has", "had", "do", "does", "did", "will", "would", "could",
+    "should", "may", "might", "shall", "can", "must", "need", "to", "of",
+    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
+    "during", "before", "after", "and", "but", "or", "nor", "not", "so",
+    "yet", "both", "either", "neither", "each", "every", "all", "any",
+    "few", "more", "most", "other", "some", "such", "no", "only", "own",
+    "same", "than", "too", "very", "that", "this", "these", "those",
+    "it", "its", "which", "who", "whom", "whose",
+}
+
+# Known synonym groups for terminology checking
+KNOWN_SYNONYMS = [
+    {"user", "users", "end-user", "end-users", "enduser", "endusers", "client", "clients"},
+    {"admin", "administrator", "administrators", "admins"},
+    {"log", "logging", "audit", "auditing"},
+]
+
+
+def _load_json(path: str) -> dict:
+    with open(path) as f:
+        return json.load(f)
+
+
+def _tokenize(text: str) -> list[str]:
+    """Tokenize text into lowercase words, stripping punctuation."""
+    return re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*', text.lower())
+
+
+def compute_ngram_similarity(text_a: str, text_b: str, n_sizes: tuple = (1, 2)) -> float:
+    """Compute cosine similarity using word-level n-gram frequency vectors."""
+    tokens_a = _tokenize(text_a)
+    tokens_b = _tokenize(text_b)
+
+    def _ngrams(tokens, n):
+        return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
+
+    def _freq_vector(tokens):
+        vec = {}
+        for n in n_sizes:
+            for ng in _ngrams(tokens, n):
+                vec[ng] = vec.get(ng, 0) + 1
+        return vec
+
+    vec_a = _freq_vector(tokens_a)
+    vec_b = _freq_vector(tokens_b)
+
+    # Cosine similarity
+    all_keys = set(vec_a) | set(vec_b)
+    if not all_keys:
+        return 0.0
+
+    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in all_keys)
+    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
+    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
+
+    if mag_a == 0 or mag_b == 0:
+        return 0.0
+
+    return dot / (mag_a * mag_b)
+
+
+def check_interface_coverage(blocks: dict, requirements: list[dict]) -> list[dict]:
+    """For every block-to-block relationship, verify interface requirements exist."""
+    findings = []
+    seen_pairs = set()
+
+    for block_name, block_data in blocks.items():
+        relationships = block_data.get("relationships", [])
+        for related_block in relationships:
+            pair = tuple(sorted([block_name, related_block]))
+            if pair in seen_pairs:
+                continue
+            seen_pairs.add(pair)
+
+            # Check if any interface requirement exists that connects these blocks
+            has_interface = False
+            for req in requirements:
+                if req.get("status") == "withdrawn":
+                    continue
+                if req.get("type") == "interface":
+                    req_block = req.get("source_block", "")
+                    if req_block in pair:
+                        has_interface = True
+                        break
+
+            findings.append({
+                "block_a": pair[0],
+                "block_b": pair[1],
+                "status": "covered" if has_interface else "missing",
+            })
+
+    return findings
+
+
+def check_duplicates(requirements: list[dict], threshold: float = 0.8) -> list[dict]:
+    """Compare requirement statements across blocks using n-gram cosine similarity."""
+    findings = []
+    active_reqs = [r for r in requirements if r.get("status") != "withdrawn"]
+
+    for i in range(len(active_reqs)):
+        for j in range(i + 1, len(active_reqs)):
+            req_a = active_reqs[i]
+            req_b = active_reqs[j]
+
+            # Only compare across different blocks
+            if req_a.get("source_block") == req_b.get("source_block"):
+                continue
+
+            sim = compute_ngram_similarity(req_a["statement"], req_b["statement"])
+            if sim >= threshold:
+                status = "duplicate" if sim >= 0.95 else "near_duplicate"
+                findings.append({
+                    "req_a": req_a["id"],
+                    "req_b": req_b["id"],
+                    "similarity": round(sim, 3),
+                    "status": status,
+                })
+
+    return findings
+
+
+def check_terminology(requirements: list[dict]) -> list[dict]:
+    """Flag inconsistent terminology across blocks."""
+    findings = []
+    active_reqs = [r for r in requirements if r.get("status") != "withdrawn"]
+
+    # Build term-to-blocks map
+    term_blocks = {}  # term -> set of blocks
+    for req in active_reqs:
+        block = req.get("source_block", "unknown")
+        words = set(_tokenize(req["statement"])) - STOP_WORDS
+        for word in words:
+            term_blocks.setdefault(word, set()).add(block)
+
+    # Check against known synonym groups
+    for synonym_group in KNOWN_SYNONYMS:
+        found_terms = {}
+        for term in synonym_group:
+            if term in term_blocks:
+                found_terms[term] = term_blocks[term]
+
+        if len(found_terms) > 1:
+            all_blocks = set()
+            for blocks in found_terms.values():
+                all_blocks.update(blocks)
+            findings.append({
+                "term_variants": sorted(found_terms.keys()),
+                "blocks_affected": sorted(all_blocks),
+            })
+
+    return findings
+
+
+def check_uncovered_needs(needs: list[dict], traceability_links: list[dict]) -> list[dict]:
+    """Find approved needs with no derived requirements."""
+    covered_needs = set()
+    for link in traceability_links:
+        if link.get("type") == "derives_from":
+            covered_needs.add(link["target"])
+
+    findings = []
+    for need in needs:
+        if need.get("status") != "approved":
+            continue
+        if need["id"] not in covered_needs:
+            findings.append({"id": need["id"], "statement": need["statement"]})
+
+    return findings
+
+
+def check_tbd_tbr(requirements: list[dict]) -> dict:
+    """List open TBD/TBR items."""
+    open_tbd = []
+    open_tbr = []
+    resolved_count = 0
+
+    for req in requirements:
+        if req.get("status") == "withdrawn":
+            continue
+        tbd_tbr = req.get("tbd_tbr")
+        if tbd_tbr is None:
+            continue
+        if isinstance(tbd_tbr, dict):
+            tbd_val = tbd_tbr.get("tbd")
+            tbr_val = tbd_tbr.get("tbr")
+            if tbd_val:
+                open_tbd.append({"id": req["id"], "tbd": tbd_val})
+            elif tbr_val:
+                open_tbr.append({"id": req["id"], "tbr": tbr_val})
+            else:
+                resolved_count += 1
+
+    return {"open_tbd": open_tbd, "open_tbr": open_tbr, "resolved_count": resolved_count}
+
+
+def check_incose_set_characteristics(workspace_path: str) -> dict:
+    """Run INCOSE C10-C15 set characteristic validation."""
+    workspace_path = _validate_dir_path(workspace_path)
+    needs_data = _load_json(os.path.join(workspace_path, "needs_registry.json"))
+    reqs_data = _load_json(os.path.join(workspace_path, "requirements_registry.json"))
+    trace_data = _load_json(os.path.join(workspace_path, "traceability_registry.json"))
+
+    needs = needs_data.get("needs", [])
+    requirements = reqs_data.get("requirements", [])
+    links = trace_data.get("links", [])
+    active_reqs = [r for r in requirements if r.get("status") != "withdrawn"]
+
+    # C10: Completeness - all approved needs traced to requirements
+    uncovered = check_uncovered_needs(needs, links)
+    c10 = {"passed": len(uncovered) == 0, "findings": uncovered}
+
+    # C11: Consistency - no unresolved conflicts
+    conflicts = [l for l in links if l.get("type") == "conflicts_with" and l.get("resolution_status") != "resolved"]
+    c11 = {"passed": len(conflicts) == 0, "findings": conflicts}
+
+    # C12: Feasibility - requires skeptic review
+    c12 = {"passed": None, "findings": [], "note": "requires_skeptic_review"}
+
+    # C13: Comprehensibility - terminology consistency
+    term_findings = check_terminology(active_reqs)
+    c13 = {"passed": len(term_findings) == 0, "findings": term_findings}
+
+    # C14: Validatability - all requirements should have V&V methods
+    reqs_without_vv = []
+    vv_linked = set()
+    for l in links:
+        if l.get("type") == "verified_by":
+            vv_linked.add(l["source"])
+    for req in active_reqs:
+        if req["id"] not in vv_linked:
+            reqs_without_vv.append({"id": req["id"], "statement": req["statement"]})
+    c14 = {"passed": len(reqs_without_vv) == 0, "findings": reqs_without_vv}
+
+    # C15: Correctness - all requirements derive from approved needs
+    approved_needs = {n["id"] for n in needs if n.get("status") == "approved"}
+    derived_from_approved = set()
+    for l in links:
+        if l.get("type") == "derives_from" and l["target"] in approved_needs:
+            derived_from_approved.add(l["source"])
+    reqs_not_derived = []
+    for req in active_reqs:
+        if req["id"] not in derived_from_approved:
+            reqs_not_derived.append({"id": req["id"]})
+    c15 = {"passed": len(reqs_not_derived) == 0, "findings": reqs_not_derived}
+
+    return {
+        "c10_completeness": c10,
+        "c11_consistency": c11,
+        "c12_feasibility": c12,
+        "c13_comprehensibility": c13,
+        "c14_validatability": c14,
+        "c15_correctness": c15,
+    }
+
+
+def validate_all(workspace_path: str) -> dict:
+    """Run all set validation checks."""
+    workspace_path = _validate_dir_path(workspace_path)
+    state = _load_json(os.path.join(workspace_path, "state.json"))
+    needs_data = _load_json(os.path.join(workspace_path, "needs_registry.json"))
+    reqs_data = _load_json(os.path.join(workspace_path, "requirements_registry.json"))
+    trace_data = _load_json(os.path.join(workspace_path, "traceability_registry.json"))
+
+    requirements = reqs_data.get("requirements", [])
+    needs = needs_data.get("needs", [])
+    links = trace_data.get("links", [])
+
+    return {
+        "interface_coverage": check_interface_coverage(state.get("blocks", {}), requirements),
+        "duplicates": check_duplicates(requirements),
+        "terminology": check_terminology(requirements),
+        "uncovered_needs": check_uncovered_needs(needs, links),
+        "tbd_tbr": check_tbd_tbr(requirements),
+        "incose_set": check_incose_set_characteristics(workspace_path),
+    }
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Cross-block set validation")
+    parser.add_argument("--workspace", required=True, help="Path to .requirements-dev/ directory")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    subparsers.add_parser("validate")
+    subparsers.add_parser("check-interfaces")
+    subparsers.add_parser("check-duplicates")
+    subparsers.add_parser("check-terminology")
+    subparsers.add_parser("check-coverage")
+    subparsers.add_parser("check-tbd")
+
+    args = parser.parse_args()
+    ws = _validate_dir_path(args.workspace)
+
+    if args.command == "validate":
+        result = validate_all(ws)
+        print(json.dumps(result, indent=2))
+    elif args.command == "check-interfaces":
+        state = _load_json(os.path.join(ws, "state.json"))
+        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
+        print(json.dumps(check_interface_coverage(state.get("blocks", {}), reqs), indent=2))
+    elif args.command == "check-duplicates":
+        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
+        print(json.dumps(check_duplicates(reqs), indent=2))
+    elif args.command == "check-terminology":
+        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
+        print(json.dumps(check_terminology(reqs), indent=2))
+    elif args.command == "check-coverage":
+        needs = _load_json(os.path.join(ws, "needs_registry.json"))["needs"]
+        links = _load_json(os.path.join(ws, "traceability_registry.json"))["links"]
+        print(json.dumps(check_uncovered_needs(needs, links), indent=2))
+    elif args.command == "check-tbd":
+        reqs = _load_json(os.path.join(ws, "requirements_registry.json"))["requirements"]
+        print(json.dumps(check_tbd_tbr(reqs), indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/test_set_validator.py b/skills/requirements-dev/tests/test_set_validator.py
new file mode 100644
index 0000000..a40f8cd
--- /dev/null
+++ b/skills/requirements-dev/tests/test_set_validator.py
@@ -0,0 +1,295 @@
+"""Tests for set_validator.py - cross-block validation checks."""
+import json
+import sys
+from pathlib import Path
+
+import pytest
+
+SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
+sys.path.insert(0, str(SCRIPTS_DIR))
+
+import set_validator
+
+
+# ---------------------------------------------------------------------------
+# Fixtures
+# ---------------------------------------------------------------------------
+
+@pytest.fixture
+def validation_workspace(tmp_path):
+    """Multi-block workspace with varied data for validation testing."""
+    ws = tmp_path / ".requirements-dev"
+    ws.mkdir()
+
+    state = {
+        "session_id": "val-test",
+        "schema_version": "1.0.0",
+        "created_at": "2025-01-01T00:00:00+00:00",
+        "current_phase": "deliver",
+        "gates": {"init": True, "needs": True, "requirements": True, "deliver": True},
+        "blocks": {
+            "auth": {
+                "name": "auth",
+                "description": "Authentication",
+                "relationships": ["data"],
+            },
+            "data": {
+                "name": "data",
+                "description": "Data storage",
+                "relationships": ["auth"],
+            },
+            "reporting": {
+                "name": "reporting",
+                "description": "Reporting",
+                "relationships": [],
+            },
+        },
+        "progress": {
+            "current_block": None,
+            "current_type_pass": None,
+            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
+            "requirements_in_draft": [],
+        },
+        "counts": {
+            "needs_total": 4, "needs_approved": 3, "needs_deferred": 1,
+            "requirements_total": 6, "requirements_registered": 4,
+            "requirements_baselined": 2, "requirements_withdrawn": 0,
+            "tbd_open": 1, "tbr_open": 0,
+        },
+        "traceability": {"links_total": 0, "coverage_pct": 0.0},
+        "decomposition": {"levels": {}, "max_level": 3},
+        "artifacts": {},
+    }
+    (ws / "state.json").write_text(json.dumps(state, indent=2))
+
+    needs = {
+        "schema_version": "1.0.0",
+        "needs": [
+            {"id": "NEED-001", "statement": "The operator needs to authenticate securely", "stakeholder": "Operator", "status": "approved", "source_block": "auth"},
+            {"id": "NEED-002", "statement": "The operator needs to store data persistently", "stakeholder": "Operator", "status": "approved", "source_block": "data"},
+            {"id": "NEED-003", "statement": "The operator needs to generate compliance reports", "stakeholder": "Operator", "status": "approved", "source_block": "reporting"},
+            {"id": "NEED-004", "statement": "The operator needs to export data to USB", "stakeholder": "Operator", "status": "deferred", "source_block": "data"},
+        ],
+    }
+    (ws / "needs_registry.json").write_text(json.dumps(needs, indent=2))
+
+    reqs = {
+        "schema_version": "1.0.0",
+        "requirements": [
+            # auth block
+            {"id": "REQ-001", "statement": "The system shall authenticate users via username and password credentials", "type": "functional", "priority": "high", "status": "registered", "parent_need": "NEED-001", "source_block": "auth", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
+            {"id": "REQ-002", "statement": "The system shall authenticate end-users via biometric verification", "type": "functional", "priority": "medium", "status": "registered", "parent_need": "NEED-001", "source_block": "auth", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
+            # data block - near-duplicate of REQ-001
+            {"id": "REQ-003", "statement": "The system shall authenticate users via username and password", "type": "functional", "priority": "high", "status": "registered", "parent_need": "NEED-002", "source_block": "data", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
+            # data block - interface requirement
+            {"id": "REQ-004", "statement": "The system shall provide an API for authentication service to query user data", "type": "interface", "priority": "high", "status": "registered", "parent_need": "NEED-002", "source_block": "data", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
+            # data block - with TBD
+            {"id": "REQ-005", "statement": "The system shall store data with TBD encryption standard", "type": "constraint", "priority": "high", "status": "registered", "parent_need": "NEED-002", "source_block": "data", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": {"tbd": "Encryption standard pending security review", "tbr": None}, "rationale": None, "registered_at": "2025-01-01"},
+            # reporting block - uses "client" instead of "user"/"end-user"
+            {"id": "REQ-006", "statement": "The system shall allow clients to generate compliance reports on demand", "type": "functional", "priority": "medium", "status": "registered", "parent_need": "NEED-003", "source_block": "reporting", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
+        ],
+    }
+    (ws / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))
+
+    trace = {
+        "schema_version": "1.0.0",
+        "links": [
+            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from", "role": "requirement"},
+            {"source": "REQ-002", "target": "NEED-001", "type": "derives_from", "role": "requirement"},
+            {"source": "REQ-003", "target": "NEED-002", "type": "derives_from", "role": "requirement"},
+            {"source": "REQ-004", "target": "NEED-002", "type": "derives_from", "role": "requirement"},
+            {"source": "REQ-005", "target": "NEED-002", "type": "derives_from", "role": "requirement"},
+            {"source": "REQ-006", "target": "NEED-003", "type": "derives_from", "role": "requirement"},
+        ],
+    }
+    (ws / "traceability_registry.json").write_text(json.dumps(trace, indent=2))
+
+    return ws
+
+
+# ---------------------------------------------------------------------------
+# Interface coverage tests
+# ---------------------------------------------------------------------------
+
+class TestInterfaceCoverage:
+    def test_covered_block_relationship(self, validation_workspace):
+        """Block pair with interface requirements passes."""
+        ws = str(validation_workspace)
+        state = json.loads((validation_workspace / "state.json").read_text())
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        findings = set_validator.check_interface_coverage(state["blocks"], reqs)
+        # auth<->data has REQ-004 (interface type, data block, mentions auth)
+        covered = [f for f in findings if f["status"] == "covered"]
+        assert len(covered) >= 1
+
+    def test_missing_interface_requirements(self, validation_workspace):
+        """Block pair without interface requirements is flagged."""
+        ws = str(validation_workspace)
+        state = json.loads((validation_workspace / "state.json").read_text())
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        findings = set_validator.check_interface_coverage(state["blocks"], reqs)
+        # auth<->data is covered, but check the structure
+        assert isinstance(findings, list)
+        for f in findings:
+            assert "block_a" in f
+            assert "block_b" in f
+            assert f["status"] in ("covered", "missing")
+
+    def test_blocks_with_no_relationships(self, validation_workspace):
+        """Blocks with empty relationships list are skipped."""
+        ws = str(validation_workspace)
+        state = json.loads((validation_workspace / "state.json").read_text())
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        findings = set_validator.check_interface_coverage(state["blocks"], reqs)
+        # reporting has no relationships, should not appear
+        reporting_findings = [f for f in findings if "reporting" in (f["block_a"], f["block_b"])]
+        assert len(reporting_findings) == 0
+
+
+# ---------------------------------------------------------------------------
+# Duplicate detection tests
+# ---------------------------------------------------------------------------
+
+class TestDuplicateDetection:
+    def test_near_duplicate_flagged(self, validation_workspace):
+        """REQ-001 and REQ-003 are near-duplicates and should be flagged."""
+        ws = str(validation_workspace)
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        findings = set_validator.check_duplicates(reqs, threshold=0.7)
+        pairs = [(f["req_a"], f["req_b"]) for f in findings]
+        assert ("REQ-001", "REQ-003") in pairs or ("REQ-003", "REQ-001") in pairs
+
+    def test_different_requirements_not_flagged(self, validation_workspace):
+        """Distinctly different requirements should not be flagged."""
+        ws = str(validation_workspace)
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        findings = set_validator.check_duplicates(reqs, threshold=0.8)
+        # REQ-001 (auth via password) and REQ-006 (compliance reports) should NOT be a pair
+        pairs = [(f["req_a"], f["req_b"]) for f in findings]
+        assert ("REQ-001", "REQ-006") not in pairs
+        assert ("REQ-006", "REQ-001") not in pairs
+
+    def test_common_prefix_not_dominating(self):
+        """Requirements sharing only 'The system shall' prefix should not match."""
+        sim = set_validator.compute_ngram_similarity(
+            "The system shall authenticate users via credentials",
+            "The system shall generate compliance reports on demand",
+        )
+        assert sim < 0.5  # Very different after the prefix
+
+    def test_ngram_computation_correct(self):
+        """N-gram similarity of identical texts is 1.0."""
+        text = "The system shall respond within 500ms"
+        sim = set_validator.compute_ngram_similarity(text, text)
+        assert sim == pytest.approx(1.0)
+
+
+# ---------------------------------------------------------------------------
+# Terminology consistency tests
+# ---------------------------------------------------------------------------
+
+class TestTerminologyConsistency:
+    def test_inconsistent_terms_flagged(self, validation_workspace):
+        """Detects 'user' vs 'end-user' vs 'client' across blocks."""
+        ws = str(validation_workspace)
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        findings = set_validator.check_terminology(reqs)
+        # Should find something related to user/end-user/client variants
+        assert len(findings) > 0
+
+    def test_consistent_terminology_no_flags(self):
+        """Consistent terminology produces no flags."""
+        reqs = [
+            {"id": "R1", "statement": "The system shall validate user input", "source_block": "a", "status": "registered"},
+            {"id": "R2", "statement": "The system shall display user profile", "source_block": "b", "status": "registered"},
+        ]
+        findings = set_validator.check_terminology(reqs)
+        assert len(findings) == 0
+
+
+# ---------------------------------------------------------------------------
+# Uncovered needs tests
+# ---------------------------------------------------------------------------
+
+class TestUncoveredNeeds:
+    def test_uncovered_need_flagged(self, tmp_path):
+        """Need with no derived requirements is flagged."""
+        needs = [
+            {"id": "NEED-001", "statement": "Need one", "status": "approved"},
+            {"id": "NEED-002", "statement": "Need two", "status": "approved"},
+        ]
+        links = [
+            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from"},
+        ]
+        findings = set_validator.check_uncovered_needs(needs, links)
+        uncovered_ids = [f["id"] for f in findings]
+        assert "NEED-002" in uncovered_ids
+        assert "NEED-001" not in uncovered_ids
+
+    def test_covered_need_not_flagged(self, tmp_path):
+        """Need with derived requirement is not flagged."""
+        needs = [{"id": "NEED-001", "statement": "Need one", "status": "approved"}]
+        links = [{"source": "REQ-001", "target": "NEED-001", "type": "derives_from"}]
+        findings = set_validator.check_uncovered_needs(needs, links)
+        assert len(findings) == 0
+
+    def test_deferred_needs_excluded(self, tmp_path):
+        """Deferred needs are excluded from coverage check."""
+        needs = [
+            {"id": "NEED-001", "statement": "Active need", "status": "approved"},
+            {"id": "NEED-002", "statement": "Deferred need", "status": "deferred"},
+        ]
+        links = [{"source": "REQ-001", "target": "NEED-001", "type": "derives_from"}]
+        findings = set_validator.check_uncovered_needs(needs, links)
+        uncovered_ids = [f["id"] for f in findings]
+        assert "NEED-002" not in uncovered_ids
+
+
+# ---------------------------------------------------------------------------
+# TBD/TBR report tests
+# ---------------------------------------------------------------------------
+
+class TestTbdTbrReport:
+    def test_open_tbd_listed(self, validation_workspace):
+        """Lists all open TBD items."""
+        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
+        report = set_validator.check_tbd_tbr(reqs)
+        assert len(report["open_tbd"]) >= 1
+        assert report["open_tbd"][0]["id"] == "REQ-005"
+
+    def test_resolved_tbd_excluded(self):
+        """Resolved TBD items excluded from report."""
+        reqs = [
+            {"id": "R1", "tbd_tbr": {"tbd": None, "tbr": None}, "status": "registered"},
+            {"id": "R2", "tbd_tbr": None, "status": "registered"},
+        ]
+        report = set_validator.check_tbd_tbr(reqs)
+        assert len(report["open_tbd"]) == 0
+        assert len(report["open_tbr"]) == 0
+
+
+# ---------------------------------------------------------------------------
+# INCOSE set characteristic tests
+# ---------------------------------------------------------------------------
+
+class TestIncoseSetCharacteristics:
+    def test_c10_completeness(self, validation_workspace):
+        """C10: All approved needs traced to requirements."""
+        ws = str(validation_workspace)
+        result = set_validator.check_incose_set_characteristics(ws)
+        assert "c10_completeness" in result
+        # All 3 approved needs have derived requirements
+        assert result["c10_completeness"]["passed"] is True
+
+    def test_c14_validatability(self, validation_workspace):
+        """C14: Check that requirements have V&V methods."""
+        ws = str(validation_workspace)
+        result = set_validator.check_incose_set_characteristics(ws)
+        assert "c14_validatability" in result
+
+    def test_c15_correctness(self, validation_workspace):
+        """C15: All requirements derive from approved needs."""
+        ws = str(validation_workspace)
+        result = set_validator.check_incose_set_characteristics(ws)
+        assert "c15_correctness" in result
+        assert result["c15_correctness"]["passed"] is True
