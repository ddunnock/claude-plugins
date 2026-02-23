diff --git a/skills/requirements-dev/commands/reqdev.decompose.md b/skills/requirements-dev/commands/reqdev.decompose.md
index 0b75546..19a1b9c 100644
--- a/skills/requirements-dev/commands/reqdev.decompose.md
+++ b/skills/requirements-dev/commands/reqdev.decompose.md
@@ -1,6 +1,131 @@
 ---
 name: reqdev:decompose
-description: Subsystem decomposition
+description: Decompose baselined blocks into sub-blocks with requirement allocation
 ---
 
-<!-- Command prompt for /reqdev:decompose. See section-12 (decomposition). -->
+# /reqdev:decompose - Subsystem Decomposition
+
+Decomposes a baselined system-level block into sub-blocks, allocates parent requirements to sub-blocks, and validates allocation coverage. Sub-blocks then become available for requirements development via `/reqdev:requirements`.
+
+## Prerequisites
+
+- Block requirements must be baselined (run `/reqdev:deliver` first)
+- Read `references/decomposition-guide.md` for guidance on decomposition patterns
+
+## Procedure
+
+### Step 1: Select Block to Decompose
+
+Ask the user which block to decompose. Show available blocks from `state.json`:
+
+```bash
+python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev validate-baseline --block <block-name>
+```
+
+If the block is NOT fully baselined, inform the user:
+> Block "{block-name}" has requirements that are not baselined. Run `/reqdev:deliver` to baseline all requirements before decomposing.
+
+### Step 2: Check Decomposition Level
+
+Determine the current level of the block (from `state.json blocks[block-name].level`, default 0) and verify further decomposition is allowed:
+
+```bash
+python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev check-level --level <current-level>
+```
+
+If NOT allowed (would exceed max_level=3):
+> Block "{block-name}" is at level {current-level}. Further decomposition would exceed the maximum depth of 3 levels. You can override this limit in state.json if needed.
+
+If at max_level - 1, warn:
+> Note: This will create level {current-level + 1} sub-blocks. One more level of decomposition remains after this.
+
+### Step 3: Identify Sub-Blocks
+
+Guide the user through identifying sub-functions within the block. Reference `decomposition-guide.md` for patterns:
+
+> Looking at the requirements for "{block-name}", let's identify distinct sub-functions.
+> Consider: processing stages, data domains, independent failure modes, or API boundaries.
+
+For each sub-block, capture:
+- **Name:** Short identifier (e.g., "graph-engine")
+- **Description:** What this sub-block is responsible for
+
+Present a summary table for user approval:
+
+```
+Proposed Sub-Blocks for "{block-name}":
+| # | Name | Description |
+|---|------|-------------|
+| 1 | graph-engine | Graph data structure and traversal |
+| 2 | cycle-detector | Circular dependency detection |
+| 3 | critical-path-calc | Critical path computation |
+
+Approve? (yes/edit/add more)
+```
+
+### Step 4: Register Sub-Blocks
+
+```bash
+python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev register-sub-blocks \
+    --parent <block-name> \
+    --sub-blocks '[{"name": "graph-engine", "description": "..."}, ...]' \
+    --level <current-level + 1>
+```
+
+### Step 5: Allocate Requirements
+
+For each parent requirement in the block, present it and ask which sub-block(s) it allocates to:
+
+> **REQ-001:** "The system shall track dependency graphs"
+> Allocate to which sub-block(s)? [graph-engine / cycle-detector / critical-path-calc / multiple]
+
+For each allocation:
+
+```bash
+python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev allocate \
+    --requirement REQ-001 --sub-block graph-engine \
+    --rationale "Graph traversal is the core capability of this sub-block"
+```
+
+A requirement can be allocated to multiple sub-blocks if it spans concerns.
+
+### Step 6: Validate Allocation Coverage
+
+```bash
+python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev validate-coverage --block <block-name>
+```
+
+If coverage < 100%:
+> The following requirements are not allocated to any sub-block:
+> - REQ-xxx: "statement"
+> - REQ-yyy: "statement"
+> Please allocate these requirements before proceeding.
+
+Loop back to Step 5 for unallocated requirements.
+
+### Step 7: Update Decomposition State
+
+After 100% coverage:
+
+```bash
+# State is updated by register-sub-blocks and allocation commands
+```
+
+### Step 8: Summary
+
+```
+Decomposition Complete
+----------------------
+Parent block:    {block-name} (level {current-level})
+Sub-blocks:      {count} created at level {current-level + 1}
+  - {sub-block-1}: {description}
+  - {sub-block-2}: {description}
+  - ...
+Allocation:      {count}/{total} requirements allocated (100%)
+
+Sub-blocks are now available as blocks in /reqdev:requirements.
+Next: Run /reqdev:requirements to develop requirements for each sub-block.
+```
+
+Offer to start requirements development for a sub-block immediately:
+> Would you like to start developing requirements for one of the sub-blocks now?
diff --git a/skills/requirements-dev/scripts/decompose.py b/skills/requirements-dev/scripts/decompose.py
new file mode 100644
index 0000000..1f16cd2
--- /dev/null
+++ b/skills/requirements-dev/scripts/decompose.py
@@ -0,0 +1,204 @@
+#!/usr/bin/env python3
+"""Subsystem decomposition logic for requirements-dev plugin.
+
+Manages block decomposition into sub-blocks, requirement allocation
+to sub-blocks, coverage validation, and decomposition state tracking.
+
+Usage:
+    python3 decompose.py --workspace .requirements-dev/ validate-baseline --block block-name
+    python3 decompose.py --workspace .requirements-dev/ register-sub-blocks --parent block-name --sub-blocks '[...]' --level 1
+    python3 decompose.py --workspace .requirements-dev/ allocate --requirement REQ-001 --sub-block graph-engine --rationale "..."
+    python3 decompose.py --workspace .requirements-dev/ validate-coverage --block block-name
+    python3 decompose.py --workspace .requirements-dev/ check-level --level 2
+"""
+import argparse
+import json
+import os
+import sys
+from datetime import datetime, timezone
+
+from shared_io import _atomic_write, _validate_dir_path
+
+
+def _load_json(path: str) -> dict:
+    with open(path) as f:
+        return json.load(f)
+
+
+def validate_baseline(workspace: str, block_name: str) -> bool:
+    """Check that all requirements for the given block have status 'baselined'.
+
+    Returns True if all are baselined, False otherwise.
+    Raises ValueError if block has no requirements.
+    """
+    workspace = _validate_dir_path(workspace)
+    reqs = _load_json(os.path.join(workspace, "requirements_registry.json"))
+    block_reqs = [r for r in reqs["requirements"]
+                  if r.get("source_block") == block_name and r.get("status") != "withdrawn"]
+    if not block_reqs:
+        raise ValueError(f"Block '{block_name}' has no requirements")
+    return all(r["status"] == "baselined" for r in block_reqs)
+
+
+def check_max_level(workspace: str, current_level: int) -> bool:
+    """Check whether decomposition at current_level + 1 would exceed max_level.
+
+    Returns True if allowed, False if would exceed.
+    """
+    workspace = _validate_dir_path(workspace)
+    state = _load_json(os.path.join(workspace, "state.json"))
+    max_level = state.get("decomposition", {}).get("max_level", 3)
+    return current_level + 1 <= max_level
+
+
+def register_sub_blocks(workspace: str, parent_block: str,
+                        sub_blocks: list[dict], level: int) -> None:
+    """Register sub-blocks in state.json.
+
+    Each sub_block dict has: name, description.
+    Adds each sub-block to blocks dict with level and parent_block fields.
+    """
+    workspace = _validate_dir_path(workspace)
+    state_path = os.path.join(workspace, "state.json")
+    state = _load_json(state_path)
+
+    for sb in sub_blocks:
+        state["blocks"][sb["name"]] = {
+            "name": sb["name"],
+            "description": sb["description"],
+            "relationships": [],
+            "level": level,
+            "parent_block": parent_block,
+        }
+
+    _atomic_write(state_path, state)
+
+
+def allocate_requirement(workspace: str, requirement_id: str,
+                         sub_block_name: str, rationale: str) -> None:
+    """Allocate a parent requirement to a sub-block.
+
+    Creates an allocated_to link in the traceability registry.
+    """
+    workspace = _validate_dir_path(workspace)
+    trace_path = os.path.join(workspace, "traceability_registry.json")
+    trace = _load_json(trace_path)
+
+    # Check for duplicate
+    for existing in trace["links"]:
+        if (existing["source"] == requirement_id
+                and existing["target"] == sub_block_name
+                and existing["type"] == "allocated_to"):
+            return  # Already allocated
+
+    link_entry = {
+        "source": requirement_id,
+        "target": sub_block_name,
+        "type": "allocated_to",
+        "role": "requirement",
+        "rationale": rationale,
+        "created_at": datetime.now(timezone.utc).isoformat(),
+    }
+    trace["links"].append(link_entry)
+    _atomic_write(trace_path, trace)
+
+
+def validate_allocation_coverage(workspace: str, parent_block: str) -> dict:
+    """Check that every baselined requirement of parent_block is allocated.
+
+    Returns dict with coverage, allocated, unallocated, and total.
+    """
+    workspace = _validate_dir_path(workspace)
+    reqs = _load_json(os.path.join(workspace, "requirements_registry.json"))
+    trace = _load_json(os.path.join(workspace, "traceability_registry.json"))
+
+    block_reqs = [r for r in reqs["requirements"]
+                  if r.get("source_block") == parent_block
+                  and r.get("status") == "baselined"]
+
+    allocated_ids = set()
+    for link in trace["links"]:
+        if link["type"] == "allocated_to":
+            allocated_ids.add(link["source"])
+
+    allocated = [r["id"] for r in block_reqs if r["id"] in allocated_ids]
+    unallocated = [r["id"] for r in block_reqs if r["id"] not in allocated_ids]
+    total = len(block_reqs)
+    coverage = len(allocated) / total if total > 0 else 0.0
+
+    return {
+        "coverage": coverage,
+        "allocated": allocated,
+        "unallocated": unallocated,
+        "total": total,
+    }
+
+
+def update_decomposition_state(workspace: str, level: int,
+                               parent_block: str, sub_blocks: list[str],
+                               coverage: float) -> None:
+    """Update the decomposition section in state.json."""
+    workspace = _validate_dir_path(workspace)
+    state_path = os.path.join(workspace, "state.json")
+    state = _load_json(state_path)
+
+    if "decomposition" not in state:
+        state["decomposition"] = {"levels": {}, "max_level": 3}
+
+    state["decomposition"]["levels"][str(level)] = {
+        "parent_block": parent_block,
+        "sub_blocks": sub_blocks,
+        "allocation_coverage": coverage,
+    }
+
+    _atomic_write(state_path, state)
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Subsystem decomposition")
+    parser.add_argument("--workspace", required=True, help="Path to .requirements-dev/ directory")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    sp = subparsers.add_parser("validate-baseline")
+    sp.add_argument("--block", required=True)
+
+    sp = subparsers.add_parser("register-sub-blocks")
+    sp.add_argument("--parent", required=True)
+    sp.add_argument("--sub-blocks", required=True, help="JSON array of sub-block objects")
+    sp.add_argument("--level", type=int, required=True)
+
+    sp = subparsers.add_parser("allocate")
+    sp.add_argument("--requirement", required=True)
+    sp.add_argument("--sub-block", required=True)
+    sp.add_argument("--rationale", required=True)
+
+    sp = subparsers.add_parser("validate-coverage")
+    sp.add_argument("--block", required=True)
+
+    sp = subparsers.add_parser("check-level")
+    sp.add_argument("--level", type=int, required=True)
+
+    args = parser.parse_args()
+    ws = _validate_dir_path(args.workspace)
+
+    if args.command == "validate-baseline":
+        result = validate_baseline(ws, args.block)
+        print(json.dumps({"valid": result}))
+    elif args.command == "register-sub-blocks":
+        sub_blocks = json.loads(args.sub_blocks)
+        register_sub_blocks(ws, args.parent, sub_blocks, args.level)
+        print(json.dumps({"registered": len(sub_blocks)}))
+    elif args.command == "allocate":
+        allocate_requirement(ws, args.requirement, args.sub_block, args.rationale)
+        print(json.dumps({"allocated": args.requirement, "to": args.sub_block}))
+    elif args.command == "validate-coverage":
+        result = validate_allocation_coverage(ws, args.block)
+        print(json.dumps(result, indent=2))
+    elif args.command == "check-level":
+        allowed = check_max_level(ws, args.level)
+        print(json.dumps({"allowed": allowed, "requested_level": args.level + 1}))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/test_decomposition.py b/skills/requirements-dev/tests/test_decomposition.py
new file mode 100644
index 0000000..02139a4
--- /dev/null
+++ b/skills/requirements-dev/tests/test_decomposition.py
@@ -0,0 +1,208 @@
+"""Tests for subsystem decomposition logic."""
+import json
+import sys
+from pathlib import Path
+
+import pytest
+
+SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
+sys.path.insert(0, str(SCRIPTS_DIR))
+
+import decompose
+
+
+# ---------------------------------------------------------------------------
+# Fixtures
+# ---------------------------------------------------------------------------
+
+@pytest.fixture
+def decomposition_workspace(tmp_path):
+    """Workspace with baselined requirements ready for decomposition."""
+    ws = tmp_path / ".requirements-dev"
+    ws.mkdir()
+
+    state = {
+        "session_id": "decomp-test",
+        "schema_version": "1.0.0",
+        "created_at": "2025-01-01T00:00:00+00:00",
+        "current_phase": "deliver",
+        "gates": {"init": True, "needs": True, "requirements": True, "deliver": True},
+        "blocks": {
+            "dependency-tracker": {
+                "name": "dependency-tracker",
+                "description": "Dependency tracking subsystem",
+                "relationships": [],
+                "level": 0,
+            },
+        },
+        "progress": {
+            "current_block": None,
+            "current_type_pass": None,
+            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
+            "requirements_in_draft": [],
+        },
+        "counts": {
+            "needs_total": 1, "needs_approved": 1, "needs_deferred": 0,
+            "requirements_total": 3, "requirements_registered": 0,
+            "requirements_baselined": 3, "requirements_withdrawn": 0,
+            "tbd_open": 0, "tbr_open": 0,
+        },
+        "traceability": {"links_total": 0, "coverage_pct": 0.0},
+        "decomposition": {"levels": {}, "max_level": 3},
+        "artifacts": {},
+    }
+    (ws / "state.json").write_text(json.dumps(state, indent=2))
+
+    reqs = {
+        "schema_version": "1.0.0",
+        "requirements": [
+            {"id": "REQ-001", "statement": "The system shall track dependency graphs", "type": "functional", "priority": "high", "status": "baselined", "source_block": "dependency-tracker", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01", "baselined_at": "2025-01-02"},
+            {"id": "REQ-002", "statement": "The system shall detect circular dependencies", "type": "functional", "priority": "high", "status": "baselined", "source_block": "dependency-tracker", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01", "baselined_at": "2025-01-02"},
+            {"id": "REQ-003", "statement": "The system shall compute critical path", "type": "functional", "priority": "medium", "status": "baselined", "source_block": "dependency-tracker", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01", "baselined_at": "2025-01-02"},
+        ],
+    }
+    (ws / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))
+
+    trace = {"schema_version": "1.0.0", "links": []}
+    (ws / "traceability_registry.json").write_text(json.dumps(trace, indent=2))
+
+    needs = {"schema_version": "1.0.0", "needs": [
+        {"id": "NEED-001", "statement": "Track dependencies", "stakeholder": "Dev", "status": "approved"},
+    ]}
+    (ws / "needs_registry.json").write_text(json.dumps(needs, indent=2))
+
+    return ws
+
+
+# ---------------------------------------------------------------------------
+# Baseline validation tests
+# ---------------------------------------------------------------------------
+
+class TestValidateBaseline:
+    def test_baselined_block_passes(self, decomposition_workspace):
+        """Block with all baselined requirements passes validation."""
+        ws = str(decomposition_workspace)
+        assert decompose.validate_baseline(ws, "dependency-tracker") is True
+
+    def test_non_baselined_block_fails(self, decomposition_workspace):
+        """Block with registered (not baselined) requirements fails."""
+        ws = str(decomposition_workspace)
+        reqs = json.loads((decomposition_workspace / "requirements_registry.json").read_text())
+        reqs["requirements"][0]["status"] = "registered"
+        (decomposition_workspace / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))
+        assert decompose.validate_baseline(ws, "dependency-tracker") is False
+
+
+# ---------------------------------------------------------------------------
+# Allocation tests
+# ---------------------------------------------------------------------------
+
+class TestAllocation:
+    def test_allocate_creates_traces(self, decomposition_workspace):
+        """Allocation creates allocated_to links in traceability registry."""
+        ws = str(decomposition_workspace)
+        # Register sub-blocks first
+        decompose.register_sub_blocks(ws, "dependency-tracker", [
+            {"name": "graph-engine", "description": "Graph processing"},
+            {"name": "cycle-detector", "description": "Cycle detection"},
+        ], level=1)
+
+        decompose.allocate_requirement(ws, "REQ-001", "graph-engine", "Graph traversal core")
+        decompose.allocate_requirement(ws, "REQ-002", "cycle-detector", "Cycle detection core")
+
+        trace = json.loads((decomposition_workspace / "traceability_registry.json").read_text())
+        alloc_links = [l for l in trace["links"] if l["type"] == "allocated_to"]
+        assert len(alloc_links) == 2
+        targets = {l["target"] for l in alloc_links}
+        assert "graph-engine" in targets
+        assert "cycle-detector" in targets
+
+    def test_allocation_coverage_incomplete(self, decomposition_workspace):
+        """Coverage validation flags unallocated requirements."""
+        ws = str(decomposition_workspace)
+        decompose.register_sub_blocks(ws, "dependency-tracker", [
+            {"name": "graph-engine", "description": "Graph processing"},
+        ], level=1)
+        decompose.allocate_requirement(ws, "REQ-001", "graph-engine", "Graph core")
+        # REQ-002 and REQ-003 not allocated
+
+        result = decompose.validate_allocation_coverage(ws, "dependency-tracker")
+        assert result["coverage"] < 1.0
+        assert "REQ-002" in result["unallocated"]
+        assert "REQ-003" in result["unallocated"]
+
+    def test_allocation_coverage_complete(self, decomposition_workspace):
+        """Coverage validation passes when all requirements allocated."""
+        ws = str(decomposition_workspace)
+        decompose.register_sub_blocks(ws, "dependency-tracker", [
+            {"name": "graph-engine", "description": "Graph processing"},
+            {"name": "cycle-detector", "description": "Cycle detection"},
+        ], level=1)
+        decompose.allocate_requirement(ws, "REQ-001", "graph-engine", "Graph core")
+        decompose.allocate_requirement(ws, "REQ-002", "cycle-detector", "Cycle detection")
+        decompose.allocate_requirement(ws, "REQ-003", "graph-engine", "Critical path uses graph")
+
+        result = decompose.validate_allocation_coverage(ws, "dependency-tracker")
+        assert result["coverage"] == pytest.approx(1.0)
+        assert result["unallocated"] == []
+
+
+# ---------------------------------------------------------------------------
+# Sub-block registration tests
+# ---------------------------------------------------------------------------
+
+class TestSubBlockRegistration:
+    def test_sub_blocks_registered_with_level(self, decomposition_workspace):
+        """Sub-blocks are registered in state.json with correct level."""
+        ws = str(decomposition_workspace)
+        decompose.register_sub_blocks(ws, "dependency-tracker", [
+            {"name": "graph-engine", "description": "Graph processing"},
+            {"name": "cycle-detector", "description": "Cycle detection"},
+            {"name": "critical-path-calc", "description": "Critical path"},
+        ], level=1)
+
+        state = json.loads((decomposition_workspace / "state.json").read_text())
+        assert "graph-engine" in state["blocks"]
+        assert state["blocks"]["graph-engine"]["level"] == 1
+        assert "cycle-detector" in state["blocks"]
+        assert "critical-path-calc" in state["blocks"]
+
+
+# ---------------------------------------------------------------------------
+# Max level tests
+# ---------------------------------------------------------------------------
+
+class TestMaxLevel:
+    def test_max_level_prevents_deep_decomposition(self, decomposition_workspace):
+        """Decomposition beyond max_level=3 is blocked."""
+        ws = str(decomposition_workspace)
+        assert decompose.check_max_level(ws, 3) is False
+
+    def test_within_max_level_allowed(self, decomposition_workspace):
+        """Decomposition within max_level is allowed."""
+        ws = str(decomposition_workspace)
+        assert decompose.check_max_level(ws, 0) is True
+        assert decompose.check_max_level(ws, 2) is True
+
+
+# ---------------------------------------------------------------------------
+# Decomposition state tests
+# ---------------------------------------------------------------------------
+
+class TestDecompositionState:
+    def test_state_tracks_decomposition(self, decomposition_workspace):
+        """Decomposition state tracks parent_block and sub_blocks."""
+        ws = str(decomposition_workspace)
+        decompose.register_sub_blocks(ws, "dependency-tracker", [
+            {"name": "graph-engine", "description": "Graph processing"},
+            {"name": "cycle-detector", "description": "Cycle detection"},
+            {"name": "critical-path-calc", "description": "Critical path"},
+        ], level=1)
+        decompose.update_decomposition_state(ws, 1, "dependency-tracker",
+            ["graph-engine", "cycle-detector", "critical-path-calc"], 1.0)
+
+        state = json.loads((decomposition_workspace / "state.json").read_text())
+        level_1 = state["decomposition"]["levels"]["1"]
+        assert level_1["parent_block"] == "dependency-tracker"
+        assert level_1["sub_blocks"] == ["graph-engine", "cycle-detector", "critical-path-calc"]
+        assert level_1["allocation_coverage"] == pytest.approx(1.0)
