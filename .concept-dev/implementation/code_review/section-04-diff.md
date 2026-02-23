diff --git a/skills/requirements-dev/commands/reqdev.needs.md b/skills/requirements-dev/commands/reqdev.needs.md
index 2c9efad..2218c59 100644
--- a/skills/requirements-dev/commands/reqdev.needs.md
+++ b/skills/requirements-dev/commands/reqdev.needs.md
@@ -3,4 +3,127 @@ name: reqdev:needs
 description: Formalize stakeholder needs per functional block
 ---
 
-<!-- Command prompt for /reqdev:needs. See section-04 (needs tracker). -->
+# /reqdev:needs -- Formalize Stakeholder Needs
+
+This command guides needs formalization from ingestion candidates into INCOSE-pattern need statements.
+
+## Prerequisites
+
+Before starting, verify the `init` gate is passed:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev/state.json check-gate init
+```
+
+If the gate check fails (exit code 1), inform the user:
+```
+The init gate has not been passed. Please run /reqdev:init first.
+```
+
+## Step 1: Load Context
+
+Read the ingestion data and current state:
+
+```bash
+cat .requirements-dev/ingestion.json
+```
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev/state.json show
+```
+
+Extract:
+- `blocks`: the list of functional blocks to process
+- `needs_candidates`: pre-extracted need candidates (if concept-dev was used)
+- Current `needs_total` count (to know if resuming)
+
+## Step 2: Per-Block Iteration
+
+For each block defined in state.json `blocks`:
+
+### If needs_candidates exist for this block (from ingestion):
+
+1. Present the candidates in a numbered list
+2. For each candidate, formalize into INCOSE pattern:
+
+**INCOSE Need Pattern:**
+- Pattern: `[Stakeholder] needs [capability] [optional qualifier]`
+- Use "should" for expectations, not "shall" (which is for requirements)
+- Solution-free: describe what is needed, not how to achieve it
+
+**Examples:**
+- Good: "The operator needs to monitor system health metrics in real-time"
+- Bad: "The operator needs a Grafana dashboard" (prescribes solution)
+- Bad: "The system shall display metrics" (uses obligation language -- this is a requirement, not a need)
+
+3. Present a batch of 3-5 formalized needs for user review
+4. For each need, ask the user to: approve, edit, defer (with rationale), or reject
+
+### If no needs_candidates (manual mode):
+
+1. Ask the user to describe stakeholder needs for this block
+2. Guide them through the INCOSE formalization pattern
+3. Present formalized versions for approval
+
+## Step 3: Register Approved Needs
+
+For each approved need:
+
+```bash
+uv run scripts/needs_tracker.py --workspace .requirements-dev add \
+  --statement "The [stakeholder] needs [capability]" \
+  --stakeholder "[Stakeholder Name]" \
+  --source-block "[block-name]" \
+  --source-artifacts "CONCEPT-DOCUMENT.md" \
+  --concept-dev-refs '{"sources": ["SRC-xxx"], "assumptions": []}'
+```
+
+For deferred needs:
+
+```bash
+uv run scripts/needs_tracker.py --workspace .requirements-dev defer \
+  --id NEED-xxx --rationale "User rationale here"
+```
+
+For rejected needs:
+
+```bash
+uv run scripts/needs_tracker.py --workspace .requirements-dev reject \
+  --id NEED-xxx --rationale "User rationale here"
+```
+
+## Step 4: Block Summary
+
+After processing each block, display:
+
+```
+BLOCK: [block-name]
+  Approved:  N needs
+  Deferred:  M needs
+  Rejected:  R needs
+```
+
+## Step 5: Gate Completion
+
+After all blocks have been processed and the user approves the complete needs set:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev/state.json set-phase needs
+uv run scripts/update_state.py --state .requirements-dev/state.json pass-gate needs
+```
+
+## Step 6: Final Summary
+
+```
+NEEDS FORMALIZATION COMPLETE
+============================
+Total needs:     N
+  Approved:      A
+  Deferred:      D
+  Rejected:      R
+Blocks covered:  B
+
+Next steps:
+  /reqdev:requirements -- Develop requirements from approved needs
+  /reqdev:status       -- View current session status
+```
diff --git a/skills/requirements-dev/scripts/needs_tracker.py b/skills/requirements-dev/scripts/needs_tracker.py
index fd9f73c..ec56749 100644
--- a/skills/requirements-dev/scripts/needs_tracker.py
+++ b/skills/requirements-dev/scripts/needs_tracker.py
@@ -1 +1,286 @@
-"""Needs registry management with INCOSE-pattern formalization."""
+#!/usr/bin/env python3
+"""Needs registry management with INCOSE-pattern formalization.
+
+Usage:
+    python3 needs_tracker.py --workspace <path> add --statement "..." --stakeholder "..." --source-block "..."
+    python3 needs_tracker.py --workspace <path> update --id NEED-001 --statement "..."
+    python3 needs_tracker.py --workspace <path> defer --id NEED-001 --rationale "..."
+    python3 needs_tracker.py --workspace <path> reject --id NEED-001 --rationale "..."
+    python3 needs_tracker.py --workspace <path> list [--block <block>] [--status <status>]
+    python3 needs_tracker.py --workspace <path> query [--source-ref SRC-xxx] [--assumption-ref ASN-xxx]
+    python3 needs_tracker.py --workspace <path> export
+
+All mutations use atomic write (temp-file-then-rename) and sync counts to state.json.
+"""
+import argparse
+import json
+import os
+import sys
+from dataclasses import asdict, dataclass, field
+from datetime import datetime, timezone
+
+from shared_io import _atomic_write, _validate_dir_path
+
+REGISTRY_FILENAME = "needs_registry.json"
+STATE_FILENAME = "state.json"
+SCHEMA_VERSION = "1.0.0"
+
+
+@dataclass
+class Need:
+    id: str
+    statement: str
+    stakeholder: str
+    source_block: str
+    source_artifacts: list[str] = field(default_factory=list)
+    concept_dev_refs: dict = field(default_factory=lambda: {"sources": [], "assumptions": []})
+    status: str = "approved"
+    rationale: str | None = None
+    registered_at: str = ""
+
+
+def _load_registry(workspace: str) -> dict:
+    """Load needs_registry.json or return empty registry."""
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    if os.path.isfile(path):
+        with open(path) as f:
+            return json.load(f)
+    return {"schema_version": SCHEMA_VERSION, "needs": []}
+
+
+def _save_registry(workspace: str, registry: dict) -> None:
+    """Save registry atomically."""
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    _atomic_write(path, registry)
+
+
+def _sync_counts(workspace: str, registry: dict) -> None:
+    """Update needs counts in state.json."""
+    state_path = os.path.join(workspace, STATE_FILENAME)
+    if not os.path.isfile(state_path):
+        return
+    with open(state_path) as f:
+        state = json.load(f)
+    needs = registry["needs"]
+    state["counts"]["needs_total"] = len(needs)
+    state["counts"]["needs_approved"] = sum(1 for n in needs if n.get("status") == "approved")
+    state["counts"]["needs_deferred"] = sum(1 for n in needs if n.get("status") == "deferred")
+    _atomic_write(state_path, state)
+
+
+def _next_id(registry: dict) -> str:
+    """Generate next sequential NEED-xxx ID."""
+    existing = registry.get("needs", [])
+    if not existing:
+        return "NEED-001"
+    max_num = 0
+    for need in existing:
+        try:
+            num = int(need["id"].split("-")[1])
+            if num > max_num:
+                max_num = num
+        except (IndexError, ValueError):
+            continue
+    return f"NEED-{max_num + 1:03d}"
+
+
+def _find_need(registry: dict, need_id: str) -> tuple[int, dict]:
+    """Find a need by ID. Returns (index, need_dict). Raises ValueError if not found."""
+    for i, need in enumerate(registry["needs"]):
+        if need["id"] == need_id:
+            return i, need
+    raise ValueError(f"Need not found: {need_id}")
+
+
+def add_need(
+    workspace: str,
+    statement: str,
+    stakeholder: str,
+    source_block: str,
+    source_artifacts: list[str] | None = None,
+    concept_dev_refs: dict | None = None,
+) -> str:
+    """Add a need to the registry. Returns the assigned ID."""
+    _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+
+    # Check uniqueness (case-insensitive statement + stakeholder)
+    for existing in registry["needs"]:
+        if (
+            existing["statement"].lower() == statement.lower()
+            and existing["stakeholder"].lower() == stakeholder.lower()
+        ):
+            raise ValueError(f"duplicate: need with same statement and stakeholder already exists ({existing['id']})")
+
+    need = Need(
+        id=_next_id(registry),
+        statement=statement,
+        stakeholder=stakeholder,
+        source_block=source_block,
+        source_artifacts=source_artifacts or [],
+        concept_dev_refs=concept_dev_refs or {"sources": [], "assumptions": []},
+        registered_at=datetime.now(timezone.utc).isoformat(),
+    )
+    registry["needs"].append(asdict(need))
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+    return need.id
+
+
+def update_need(workspace: str, need_id: str, **fields) -> None:
+    """Update fields on an existing need."""
+    _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, need = _find_need(registry, need_id)
+
+    for key, value in fields.items():
+        if key in need:
+            need[key] = value
+
+    if "statement" in fields:
+        need["registered_at"] = datetime.now(timezone.utc).isoformat()
+
+    registry["needs"][idx] = need
+    _save_registry(workspace, registry)
+
+
+def defer_need(workspace: str, need_id: str, rationale: str) -> None:
+    """Set need status to deferred with rationale."""
+    if not rationale or not rationale.strip():
+        raise ValueError("rationale is required for defer")
+    _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, need = _find_need(registry, need_id)
+    need["status"] = "deferred"
+    need["rationale"] = rationale
+    registry["needs"][idx] = need
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+
+
+def reject_need(workspace: str, need_id: str, rationale: str) -> None:
+    """Set need status to rejected with rationale."""
+    if not rationale or not rationale.strip():
+        raise ValueError("rationale is required for reject")
+    _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, need = _find_need(registry, need_id)
+    need["status"] = "rejected"
+    need["rationale"] = rationale
+    registry["needs"][idx] = need
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+
+
+def list_needs(workspace: str, block: str | None = None, status: str | None = None) -> list[dict]:
+    """List needs with optional filters."""
+    _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    results = registry["needs"]
+    if block:
+        results = [n for n in results if n.get("source_block") == block]
+    if status:
+        results = [n for n in results if n.get("status") == status]
+    return results
+
+
+def query_needs(workspace: str, source_ref: str | None = None, assumption_ref: str | None = None) -> list[dict]:
+    """Query needs by concept-dev cross-references."""
+    _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    results = []
+    for need in registry["needs"]:
+        refs = need.get("concept_dev_refs", {})
+        if source_ref and source_ref in refs.get("sources", []):
+            results.append(need)
+        elif assumption_ref and assumption_ref in refs.get("assumptions", []):
+            results.append(need)
+    return results
+
+
+def export_needs(workspace: str) -> dict:
+    """Export full registry as dict."""
+    _validate_dir_path(workspace)
+    return _load_registry(workspace)
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Manage stakeholder needs registry")
+    parser.add_argument("--workspace", required=True, help="Path to .requirements-dev/ directory")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    # add
+    sp = subparsers.add_parser("add")
+    sp.add_argument("--statement", required=True)
+    sp.add_argument("--stakeholder", required=True)
+    sp.add_argument("--source-block", required=True)
+    sp.add_argument("--source-artifacts", default="")
+    sp.add_argument("--concept-dev-refs", default=None)
+
+    # update
+    sp = subparsers.add_parser("update")
+    sp.add_argument("--id", required=True)
+    sp.add_argument("--statement", default=None)
+    sp.add_argument("--stakeholder", default=None)
+
+    # defer
+    sp = subparsers.add_parser("defer")
+    sp.add_argument("--id", required=True)
+    sp.add_argument("--rationale", required=True)
+
+    # reject
+    sp = subparsers.add_parser("reject")
+    sp.add_argument("--id", required=True)
+    sp.add_argument("--rationale", required=True)
+
+    # list
+    sp = subparsers.add_parser("list")
+    sp.add_argument("--block", default=None)
+    sp.add_argument("--status", default=None)
+
+    # query
+    sp = subparsers.add_parser("query")
+    sp.add_argument("--source-ref", default=None)
+    sp.add_argument("--assumption-ref", default=None)
+
+    # export
+    subparsers.add_parser("export")
+
+    args = parser.parse_args()
+
+    if args.command == "add":
+        refs = json.loads(args.concept_dev_refs) if args.concept_dev_refs else None
+        artifacts = [a.strip() for a in args.source_artifacts.split(",") if a.strip()]
+        need_id = add_need(
+            args.workspace, args.statement, args.stakeholder,
+            args.source_block, artifacts, refs,
+        )
+        print(json.dumps({"id": need_id}))
+    elif args.command == "update":
+        fields = {}
+        if args.statement:
+            fields["statement"] = args.statement
+        if args.stakeholder:
+            fields["stakeholder"] = args.stakeholder
+        update_need(args.workspace, args.id, **fields)
+        print(json.dumps({"updated": args.id}))
+    elif args.command == "defer":
+        defer_need(args.workspace, args.id, args.rationale)
+        print(json.dumps({"deferred": args.id}))
+    elif args.command == "reject":
+        reject_need(args.workspace, args.id, args.rationale)
+        print(json.dumps({"rejected": args.id}))
+    elif args.command == "list":
+        result = list_needs(args.workspace, args.block, args.status)
+        print(json.dumps(result, indent=2))
+    elif args.command == "query":
+        result = query_needs(args.workspace, args.source_ref, args.assumption_ref)
+        print(json.dumps(result, indent=2))
+    elif args.command == "export":
+        result = export_needs(args.workspace)
+        print(json.dumps(result, indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/test_needs_tracker.py b/skills/requirements-dev/tests/test_needs_tracker.py
new file mode 100644
index 0000000..3a43eb2
--- /dev/null
+++ b/skills/requirements-dev/tests/test_needs_tracker.py
@@ -0,0 +1,178 @@
+"""Tests for needs_tracker.py -- stakeholder needs management."""
+import json
+
+import pytest
+
+from needs_tracker import (
+    add_need,
+    defer_need,
+    export_needs,
+    list_needs,
+    query_needs,
+    reject_need,
+    update_need,
+)
+
+
+@pytest.fixture
+def workspace(tmp_path):
+    """Create a workspace with state.json and empty needs registry."""
+    ws = tmp_path / ".requirements-dev"
+    ws.mkdir()
+    state = {
+        "session_id": "test-abc",
+        "schema_version": "1.0.0",
+        "created_at": "2025-01-01T00:00:00+00:00",
+        "current_phase": "needs",
+        "gates": {"init": True, "needs": False, "requirements": False, "deliver": False},
+        "blocks": {"monitoring": "Dashboard block"},
+        "progress": {
+            "current_block": None,
+            "current_type_pass": None,
+            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
+            "requirements_in_draft": [],
+        },
+        "counts": {
+            "needs_total": 0,
+            "needs_approved": 0,
+            "needs_deferred": 0,
+            "requirements_total": 0,
+            "requirements_registered": 0,
+            "requirements_baselined": 0,
+            "requirements_withdrawn": 0,
+            "tbd_open": 0,
+            "tbr_open": 0,
+        },
+        "traceability": {"links_total": 0, "coverage_pct": 0.0},
+        "decomposition": {"levels": {}, "max_level": 3},
+        "artifacts": {},
+    }
+    (ws / "state.json").write_text(json.dumps(state, indent=2))
+    return str(ws)
+
+
+def test_add_creates_need_with_correct_fields(workspace):
+    """add creates NEED-001 with correct fields."""
+    need_id = add_need(
+        workspace,
+        statement="The operator needs to monitor pipeline health",
+        stakeholder="Pipeline Operator",
+        source_block="monitoring",
+    )
+    assert need_id == "NEED-001"
+    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
+    need = registry["needs"][0]
+    assert need["id"] == "NEED-001"
+    assert need["statement"] == "The operator needs to monitor pipeline health"
+    assert need["stakeholder"] == "Pipeline Operator"
+    assert need["source_block"] == "monitoring"
+    assert need["status"] == "approved"
+
+
+def test_add_auto_increments_id(workspace):
+    """add auto-increments ID (NEED-001, NEED-002, NEED-003)."""
+    id1 = add_need(workspace, "Need one", "User", "block-a")
+    id2 = add_need(workspace, "Need two", "User", "block-a")
+    id3 = add_need(workspace, "Need three", "Admin", "block-b")
+    assert id1 == "NEED-001"
+    assert id2 == "NEED-002"
+    assert id3 == "NEED-003"
+
+
+def test_add_validates_uniqueness(workspace):
+    """add rejects duplicate statement+stakeholder combination."""
+    add_need(workspace, "The user needs X", "User", "block-a")
+    with pytest.raises(ValueError, match="duplicate"):
+        add_need(workspace, "the user needs x", "user", "block-a")  # case-insensitive
+
+
+def test_add_syncs_counts_to_state(workspace):
+    """add syncs needs_total count to state.json."""
+    add_need(workspace, "Need one", "User", "block-a")
+    add_need(workspace, "Need two", "Admin", "block-b")
+    state = json.loads(open(f"{workspace}/state.json").read())
+    assert state["counts"]["needs_total"] == 2
+    assert state["counts"]["needs_approved"] == 2
+
+
+def test_update_modifies_statement(workspace):
+    """update modifies statement and preserves other fields."""
+    add_need(workspace, "Original statement", "User", "block-a")
+    update_need(workspace, "NEED-001", statement="Updated statement")
+    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
+    need = registry["needs"][0]
+    assert need["statement"] == "Updated statement"
+    assert need["stakeholder"] == "User"
+    assert need["source_block"] == "block-a"
+
+
+def test_defer_sets_status_with_rationale(workspace):
+    """defer sets status='deferred' and requires rationale."""
+    add_need(workspace, "Need one", "User", "block-a")
+    defer_need(workspace, "NEED-001", rationale="Not in scope for MVP")
+    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
+    assert registry["needs"][0]["status"] == "deferred"
+    assert registry["needs"][0]["rationale"] == "Not in scope for MVP"
+
+
+def test_defer_without_rationale_raises_error(workspace):
+    """defer without rationale raises error."""
+    add_need(workspace, "Need one", "User", "block-a")
+    with pytest.raises(ValueError, match="rationale"):
+        defer_need(workspace, "NEED-001", rationale="")
+
+
+def test_reject_sets_status_with_rationale(workspace):
+    """reject sets status='rejected' and requires rationale."""
+    add_need(workspace, "Need one", "User", "block-a")
+    reject_need(workspace, "NEED-001", rationale="Out of scope")
+    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
+    assert registry["needs"][0]["status"] == "rejected"
+
+
+def test_list_returns_needs_for_block(workspace):
+    """list returns all needs for a given block."""
+    add_need(workspace, "Need A", "User", "block-a")
+    add_need(workspace, "Need B", "User", "block-b")
+    add_need(workspace, "Need C", "Admin", "block-a")
+    result = list_needs(workspace, block="block-a")
+    assert len(result) == 2
+    assert all(n["source_block"] == "block-a" for n in result)
+
+
+def test_list_with_status_filter(workspace):
+    """list with status filter returns only matching needs."""
+    add_need(workspace, "Need A", "User", "block-a")
+    add_need(workspace, "Need B", "Admin", "block-a")
+    defer_need(workspace, "NEED-001", rationale="Later")
+    result = list_needs(workspace, status="deferred")
+    assert len(result) == 1
+    assert result[0]["id"] == "NEED-001"
+
+
+def test_query_by_source_ref(workspace):
+    """query by concept_dev_refs returns needs linked to specific SRC-xxx."""
+    add_need(
+        workspace, "Need A", "User", "block-a",
+        concept_dev_refs={"sources": ["SRC-001"], "assumptions": []},
+    )
+    add_need(workspace, "Need B", "Admin", "block-b")
+    result = query_needs(workspace, source_ref="SRC-001")
+    assert len(result) == 1
+    assert result[0]["id"] == "NEED-001"
+
+
+def test_export_produces_correct_structure(workspace):
+    """export produces correct JSON structure."""
+    add_need(workspace, "Need A", "User", "block-a")
+    result = export_needs(workspace)
+    assert "schema_version" in result
+    assert "needs" in result
+    assert len(result["needs"]) == 1
+
+
+def test_schema_version_in_registry(workspace):
+    """schema_version field present in registry output."""
+    add_need(workspace, "Need A", "User", "block-a")
+    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
+    assert registry["schema_version"] == "1.0.0"
