diff --git a/skills/requirements-dev/commands/reqdev.requirements.md b/skills/requirements-dev/commands/reqdev.requirements.md
index 09cb3ff..96bfaf7 100644
--- a/skills/requirements-dev/commands/reqdev.requirements.md
+++ b/skills/requirements-dev/commands/reqdev.requirements.md
@@ -1,6 +1,298 @@
 ---
 name: reqdev:requirements
-description: Block requirements engine with quality checking
+description: Main workflow — develop requirements block-by-block with type-guided passes, quality checking, V&V planning, and traceability
 ---
 
-<!-- Command prompt for /reqdev:requirements. See section-07 (requirements command). -->
+# /reqdev:requirements -- Develop Requirements
+
+This command guides block-by-block, type-guided requirements development with quality checking, V&V planning, and traceability linking.
+
+## Prerequisites
+
+Verify the `needs` gate is passed:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev check-gate needs
+```
+
+If the gate check fails (exit code 1), inform the user:
+```
+The needs gate has not been passed. Please run /reqdev:needs first to formalize stakeholder needs.
+```
+
+## Step 1: Load Context
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev show
+```
+
+Read registries:
+
+```bash
+cat .requirements-dev/needs_registry.json
+cat .requirements-dev/requirements_registry.json
+cat .requirements-dev/state.json
+```
+
+Extract:
+- `blocks`: the list of functional blocks to process
+- Approved needs per block (from `needs_registry.json`)
+- Existing requirements (for resume)
+- `progress.current_block` and `progress.current_type_pass` (resume position)
+- `progress.requirements_in_draft` (unregistered drafts from previous session)
+
+## Step 2: Set Phase
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev set-phase requirements
+```
+
+## Step 3: Handle Resume
+
+If `progress.requirements_in_draft` contains IDs, present them for confirmation before continuing:
+
+```
+===================================================================
+RESUME: Found draft requirements from previous session
+===================================================================
+
+[List each draft REQ-xxx with its statement]
+
+For each draft:
+  [A] Register now (proceed to quality check + registration)
+  [B] Discard (remove the draft)
+===================================================================
+```
+
+After handling drafts, clear the list:
+```bash
+uv run scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'
+```
+
+## Step 4: Block-by-Block, Type-Guided Passes
+
+For each block that has approved needs, iterate over requirement types in this fixed order:
+
+1. **Functional** -- what the block must do
+2. **Performance** -- measurable behavior targets
+3. **Interface** -- how the block communicates with other blocks
+4. **Constraint** -- limitations from environment, standards, or technology
+5. **Quality** -- non-functional characteristics (reliability, maintainability, etc.)
+
+### For Each Type Pass Within a Block
+
+#### 4a. Update Progress Tracking
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev update progress.current_block "<block-name>"
+uv run scripts/update_state.py --state .requirements-dev update progress.current_type_pass "<type>"
+```
+
+#### 4b. Seed Draft Requirements
+
+Read the block's approved needs from `needs_registry.json` and the block context. Propose 2-3 draft requirement statements for the current type.
+
+Use the INCOSE pattern: **"The [subject] shall [action] [measurable criterion]."**
+
+#### 4c. Present Drafts for User Refinement
+
+```
+===================================================================
+BLOCK: [block-name] | TYPE: [functional/performance/...]
+===================================================================
+
+Draft 1: The [subject] shall [action].
+  Parent Need: NEED-xxx
+  Priority: [suggested]
+
+Draft 2: The [subject] shall [action].
+  Parent Need: NEED-xxx
+  Priority: [suggested]
+
+-------------------------------------------------------------------
+Review each draft:
+  [A] Accept as-is
+  [B] Edit (provide your revision)
+  [C] Skip (don't create this requirement)
+  [D] Add a new requirement not shown above
+===================================================================
+```
+
+#### 4d. Collect Minimal Attributes
+
+For each accepted/edited requirement, confirm:
+- **Statement** (the requirement text)
+- **Type** (pre-set from the current pass)
+- **Priority** (high/medium/low)
+
+Optionally offer expansion to full 13 INCOSE attributes (rationale, risk, stability, source, allocation, etc.) via `references/attribute-schema.md`. Do not force expansion.
+
+#### 4e. Quality Check -- Tier 1 (Deterministic)
+
+```bash
+uv run scripts/quality_rules.py check "<requirement statement>"
+```
+
+Parse the JSON output. If violations are found, present them with suggested rewrites. The user resolves each violation (accept rewrite, provide own rewrite, or justify and override). Re-run the check on revised text until it passes.
+
+#### 4f. Quality Check -- Tier 2 (LLM Semantic)
+
+If Tier 1 passes, invoke the **quality-checker** agent with:
+- The requirement statement
+- Context: block name, requirement type, parent need statement
+- Existing requirements (for terminology consistency via R36)
+
+Reference: `agents/quality-checker.md`
+
+Present both tiers' results together. Only **high-confidence flags** block registration; medium/low flags are informational.
+
+#### 4g. V&V Planning
+
+Suggest verification method based on type-to-method mapping:
+
+| Type | Suggested V&V Method |
+|------|---------------------|
+| Functional | System test / unit test |
+| Performance | Load test / benchmark test |
+| Interface | Integration test / contract test |
+| Constraint | Inspection / analysis |
+| Quality | Demonstration / analysis |
+
+Reference: `references/vv-methods.md`
+
+Present suggested method, draft success criteria derived from the requirement statement, and suggested responsible party. User confirms or modifies. Store as INCOSE attributes A6-A9.
+
+#### 4h. Register the Requirement
+
+```bash
+uv run scripts/requirement_tracker.py --workspace .requirements-dev add \
+  --statement "<statement>" --type <type> --priority <priority> \
+  --source-block "<block-name>" --level 0
+```
+
+Then register (transition from draft to registered):
+
+```bash
+uv run scripts/requirement_tracker.py --workspace .requirements-dev register \
+  --id <REQ-xxx> --parent-need <NEED-xxx>
+```
+
+#### 4i. Create Traceability Links
+
+```bash
+uv run scripts/traceability.py --workspace .requirements-dev link \
+  --source <REQ-xxx> --target <NEED-xxx> --type derives_from --role requirement
+```
+
+If concept-dev sources are referenced:
+
+```bash
+uv run scripts/traceability.py --workspace .requirements-dev link \
+  --source <REQ-xxx> --target <SRC-xxx> --type sources --role requirement
+```
+
+#### 4j. Sync Counts
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev sync-counts
+```
+
+### Metered Interaction Checkpoint
+
+After registering each batch of 2-3 requirements, checkpoint with the user:
+
+```
+===================================================================
+CHECKPOINT: [N] requirements registered for [block-name], [type] type.
+
+  [A] Continue with more [type] requirements for this block
+  [B] Move to [next-type] requirements
+  [C] Review what we have so far (/reqdev:status)
+  [D] Pause session (progress saved -- use /reqdev:resume to continue)
+===================================================================
+```
+
+**CRITICAL: Do NOT generate more than 3 requirements without user confirmation.**
+
+If the user chooses [D] (Pause), save any quality-checked but unregistered drafts:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '["REQ-xxx"]'
+```
+
+### Type Pass Completion
+
+When the user signals no more requirements for a given type, transition:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev update progress.current_type_pass "<next-type>"
+```
+
+### Block Completion
+
+When all five type passes are complete for a block:
+
+```
+===================================================================
+BLOCK COMPLETE: [block-name]
+===================================================================
+
+Requirements registered: [count by type]
+  Functional:   [n]
+  Performance:  [n]
+  Interface:    [n]
+  Constraint:   [n]
+  Quality:      [n]
+
+Traceability: [n] needs covered out of [total]
+Quality check pass rate: [n]%
+
+Proceed to next block? [Y/N]
+===================================================================
+```
+
+## Step 5: Gate Completion
+
+After all blocks have completed all type passes:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev pass-gate requirements
+```
+
+## Step 6: Transition Message
+
+```
+===================================================================
+Requirements phase complete.
+
+Total requirements registered: [N]
+  By type: functional=[n], performance=[n], interface=[n],
+           constraint=[n], quality=[n]
+Traceability coverage: [n]%
+Open TBD items: [n]
+Open TBR items: [n]
+
+Next steps:
+  /reqdev:validate -- Run set validation (recommended)
+  /reqdev:deliver  -- Generate deliverable documents
+  /reqdev:status   -- View full dashboard
+===================================================================
+```
+
+## Behavioral Rules
+
+1. **Never skip quality checking.** Every requirement statement must pass through `quality_rules.py` before registration. No exceptions.
+
+2. **Never auto-register.** Always present requirements for user review before registration. The user must explicitly approve each requirement.
+
+3. **Respect the type order.** Process types in the fixed order (functional, performance, interface, constraint, quality). Do not skip types unless the user explicitly requests it.
+
+4. **Meter the output.** Present at most 2-3 draft requirements per round. Wait for user response before generating more.
+
+5. **Track position precisely.** Update `progress.current_block` and `progress.current_type_pass` in state.json at every transition so `/reqdev:resume` can restore exact position.
+
+6. **Handle TBD/TBR values.** When a requirement has a value that cannot be determined yet (e.g., a performance target needing research), mark it as TBD with a closure tracking field. Suggest `/reqdev:research` for TPM investigation.
+
+7. **Offer attribute expansion.** After the minimal 3 attributes (statement, type, priority), offer to expand to the full 13 INCOSE attributes. Reference `references/attribute-schema.md` for the schema. Do not force expansion on every requirement.
+
+8. **Use the quality-checker agent for semantic checks.** After Tier 1 deterministic checks pass, invoke the quality-checker agent for the 9 semantic rules. Present both tiers' results together.
diff --git a/skills/requirements-dev/scripts/update_state.py b/skills/requirements-dev/scripts/update_state.py
index 1ca4c8b..e986b37 100644
--- a/skills/requirements-dev/scripts/update_state.py
+++ b/skills/requirements-dev/scripts/update_state.py
@@ -117,7 +117,8 @@ def sync_counts(workspace_path: str) -> None:
     needs_file = os.path.join(workspace_path, "needs_registry.json")
     if os.path.isfile(needs_file):
         with open(needs_file) as f:
-            needs = json.load(f)
+            needs_data = json.load(f)
+        needs = needs_data.get("needs", []) if isinstance(needs_data, dict) else needs_data
     else:
         needs = []
 
@@ -125,7 +126,8 @@ def sync_counts(workspace_path: str) -> None:
     reqs_file = os.path.join(workspace_path, "requirements_registry.json")
     if os.path.isfile(reqs_file):
         with open(reqs_file) as f:
-            reqs = json.load(f)
+            reqs_data = json.load(f)
+        reqs = reqs_data.get("requirements", []) if isinstance(reqs_data, dict) else reqs_data
     else:
         reqs = []
 
diff --git a/skills/requirements-dev/tests/test_integration.py b/skills/requirements-dev/tests/test_integration.py
new file mode 100644
index 0000000..3f23563
--- /dev/null
+++ b/skills/requirements-dev/tests/test_integration.py
@@ -0,0 +1,256 @@
+"""Integration tests for the requirements pipeline.
+
+Tests owned by section-07 (requirements command): full pipeline flows.
+Tests owned by section-08 (status/resume): TBD.
+Tests owned by section-09 (deliverables): TBD.
+"""
+import json
+import sys
+from pathlib import Path
+
+import pytest
+
+SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
+sys.path.insert(0, str(SCRIPTS_DIR))
+
+import needs_tracker
+import quality_rules
+import requirement_tracker
+import traceability
+import update_state
+
+
+# ---------------------------------------------------------------------------
+# Fixtures
+# ---------------------------------------------------------------------------
+
+@pytest.fixture
+def pipeline_workspace(tmp_path):
+    """Workspace with init+needs gates passed and 2 approved needs."""
+    ws = tmp_path / ".requirements-dev"
+    ws.mkdir()
+    state = {
+        "session_id": "integ-test",
+        "schema_version": "1.0.0",
+        "created_at": "2025-01-01T00:00:00+00:00",
+        "current_phase": "needs",
+        "gates": {"init": True, "needs": True, "requirements": False, "deliver": False},
+        "blocks": {"auth": {"name": "auth", "description": "Authentication block"}},
+        "progress": {
+            "current_block": None,
+            "current_type_pass": None,
+            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
+            "requirements_in_draft": [],
+        },
+        "counts": {
+            "needs_total": 2,
+            "needs_approved": 2,
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
+
+    needs_reg = {
+        "schema_version": "1.0.0",
+        "needs": [
+            {
+                "id": "NEED-001",
+                "statement": "The operator needs to authenticate via secure credentials",
+                "stakeholder": "Operator",
+                "status": "approved",
+                "source_block": "auth",
+                "source_artifacts": [],
+                "concept_dev_refs": {"sources": [], "assumptions": []},
+                "rationale": None,
+                "registered_at": "2025-01-01T00:00:00+00:00",
+            },
+            {
+                "id": "NEED-002",
+                "statement": "The operator needs to reset their password without admin help",
+                "stakeholder": "Operator",
+                "status": "approved",
+                "source_block": "auth",
+                "source_artifacts": [],
+                "concept_dev_refs": {"sources": [], "assumptions": []},
+                "rationale": None,
+                "registered_at": "2025-01-01T00:00:00+00:00",
+            },
+        ],
+    }
+    (ws / "needs_registry.json").write_text(json.dumps(needs_reg, indent=2))
+
+    reqs_reg = {"schema_version": "1.0.0", "requirements": []}
+    (ws / "requirements_registry.json").write_text(json.dumps(reqs_reg, indent=2))
+
+    trace_reg = {"schema_version": "1.0.0", "links": []}
+    (ws / "traceability_registry.json").write_text(json.dumps(trace_reg, indent=2))
+
+    return ws
+
+
+# ---------------------------------------------------------------------------
+# Section 07: Full pipeline tests
+# ---------------------------------------------------------------------------
+
+class TestFullPipeline:
+    """Verify need -> requirement -> quality check -> register -> trace -> coverage."""
+
+    def test_full_pipeline_need_to_traced_requirement(self, pipeline_workspace):
+        """Complete flow: quality check -> add -> register -> trace -> coverage."""
+        ws = str(pipeline_workspace)
+
+        # 1. Quality check on a clean requirement statement
+        statement = "The system shall authenticate users via username and password credentials"
+        violations = quality_rules.check_requirement(statement)
+        assert len(violations) == 0, f"Unexpected violations: {[v.rule_id for v in violations]}"
+
+        # 2. Add requirement (draft)
+        req_id = requirement_tracker.add_requirement(
+            ws, statement, "functional", "high", "auth", level=0,
+        )
+        assert req_id.startswith("REQ-")
+
+        # Verify draft status
+        reg = requirement_tracker._load_registry(ws)
+        req = next(r for r in reg["requirements"] if r["id"] == req_id)
+        assert req["status"] == "draft"
+
+        # 3. Register (transition to registered)
+        requirement_tracker.register_requirement(ws, req_id, "NEED-001")
+        reg = requirement_tracker._load_registry(ws)
+        req = next(r for r in reg["requirements"] if r["id"] == req_id)
+        assert req["status"] == "registered"
+        assert req["parent_need"] == "NEED-001"
+
+        # 4. Create traceability link
+        traceability.link(ws, req_id, "NEED-001", "derives_from", "requirement")
+
+        # 5. Check coverage
+        report = traceability.coverage_report(ws)
+        assert report["coverage_pct"] > 0
+        assert report["needs_covered"] >= 1
+
+    def test_pipeline_quality_violation_then_resolve(self, pipeline_workspace):
+        """Violation blocks registration; resolution allows it."""
+        ws = str(pipeline_workspace)
+
+        # 1. Check a statement with ambiguous language (R7 - "appropriate")
+        bad_statement = "The system shall provide appropriate handling of errors"
+        violations = quality_rules.check_requirement(bad_statement)
+        assert len(violations) > 0, "Expected violations for ambiguous language"
+        rule_ids = {v.rule_id for v in violations}
+        assert "R7" in rule_ids, f"Expected R7 violation, got: {rule_ids}"
+
+        # 2. Check a clean replacement
+        good_statement = "The system shall return structured JSON error responses with HTTP status codes"
+        violations = quality_rules.check_requirement(good_statement)
+        assert len(violations) == 0, f"Unexpected violations: {[v.rule_id for v in violations]}"
+
+        # 3. Proceed with registration using the clean statement
+        req_id = requirement_tracker.add_requirement(
+            ws, good_statement, "functional", "high", "auth", level=0,
+        )
+        requirement_tracker.register_requirement(ws, req_id, "NEED-001")
+
+        reg = requirement_tracker._load_registry(ws)
+        req = next(r for r in reg["requirements"] if r["id"] == req_id)
+        assert req["status"] == "registered"
+
+    def test_pipeline_tbd_tracking(self, pipeline_workspace):
+        """TBD values are tracked through registration and reflected in counts."""
+        ws = str(pipeline_workspace)
+
+        # 1. Add requirement
+        statement = "The system shall respond to authentication requests within TBD milliseconds"
+        req_id = requirement_tracker.add_requirement(
+            ws, statement, "performance", "high", "auth", level=0,
+        )
+
+        # 2. Set TBD field on the requirement
+        requirement_tracker.update_requirement(
+            ws, req_id,
+            tbd_tbr={"tbd": "Response time target pending load testing", "tbr": None},
+        )
+
+        # 3. Register
+        requirement_tracker.register_requirement(ws, req_id, "NEED-001")
+
+        # 4. Sync counts
+        update_state.sync_counts(ws)
+
+        # 5. Verify state reflects TBD
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+        assert state["counts"]["tbd_open"] >= 1
+
+
+class TestMeteredInteractionState:
+    """Verify state tracking for metered interaction flow."""
+
+    def test_progress_tracking_after_registration(self, pipeline_workspace):
+        """After registering requirements, state.json progress reflects position."""
+        ws = str(pipeline_workspace)
+
+        # Set progress tracking fields
+        update_state.update_field(ws, "progress.current_block", "auth")
+        update_state.update_field(ws, "progress.current_type_pass", "functional")
+
+        # Add and register 2 requirements
+        for i, stmt in enumerate([
+            "The system shall validate user credentials against the identity store",
+            "The system shall lock accounts after 5 consecutive failed login attempts",
+        ]):
+            req_id = requirement_tracker.add_requirement(
+                ws, stmt, "functional", "high", "auth",
+            )
+            requirement_tracker.register_requirement(ws, req_id, "NEED-001")
+
+        # Sync and check
+        update_state.sync_counts(ws)
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+
+        assert state["progress"]["current_block"] == "auth"
+        assert state["progress"]["current_type_pass"] == "functional"
+        assert state["counts"]["requirements_registered"] == 2
+        assert state["counts"]["requirements_total"] == 2
+
+    def test_type_pass_transition(self, pipeline_workspace):
+        """Current type pass updates correctly when transitioning."""
+        ws = str(pipeline_workspace)
+
+        # Start at functional
+        update_state.update_field(ws, "progress.current_block", "auth")
+        update_state.update_field(ws, "progress.current_type_pass", "functional")
+
+        # Transition to performance
+        update_state.update_field(ws, "progress.current_type_pass", "performance")
+
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+        assert state["progress"]["current_type_pass"] == "performance"
+
+    def test_requirements_in_draft_tracking(self, pipeline_workspace):
+        """Draft requirement IDs are tracked in state for session resume."""
+        ws = str(pipeline_workspace)
+
+        # Add a requirement (stays draft)
+        req_id = requirement_tracker.add_requirement(
+            ws,
+            "The system shall issue JWT tokens upon successful authentication",
+            "functional", "high", "auth",
+        )
+
+        # Track draft in progress
+        update_state.update_field(
+            ws, "progress.requirements_in_draft", json.dumps([req_id]),
+        )
+
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+        assert req_id in state["progress"]["requirements_in_draft"]
