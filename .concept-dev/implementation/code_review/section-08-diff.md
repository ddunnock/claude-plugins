diff --git a/skills/requirements-dev/commands/reqdev.resume.md b/skills/requirements-dev/commands/reqdev.resume.md
index 8ab79e0..acb8eed 100644
--- a/skills/requirements-dev/commands/reqdev.resume.md
+++ b/skills/requirements-dev/commands/reqdev.resume.md
@@ -1,6 +1,165 @@
 ---
 name: reqdev:resume
-description: Resume interrupted session
+description: Resume an interrupted requirements development session from the last known state, including mid-block and mid-type-pass positions
 ---
 
-<!-- Command prompt for /reqdev:resume. See section-08 (status/resume). -->
+# /reqdev:resume -- Resume Interrupted Session
+
+## Step 1: Load State
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev show
+```
+
+If no state file exists:
+```
+No active session found. Run /reqdev:init to start a new session.
+```
+
+## Step 2: Identify Resume Point
+
+Read `state.json` to determine exact position:
+
+```bash
+cat .requirements-dev/state.json
+```
+
+Key fields:
+- `current_phase`: which phase was active
+- `progress.current_block`: which block was being worked on (null if between blocks)
+- `progress.current_type_pass`: which type pass was active (null if between passes)
+- `progress.type_pass_order`: fixed ordering `["functional", "performance", "interface", "constraint", "quality"]`
+- `progress.requirements_in_draft`: list of quality-checked but unregistered requirement IDs
+
+## Step 3: Display Resume Summary
+
+```
+===================================================================
+RESUMING SESSION
+===================================================================
+
+Session: [id]
+Last Updated: [timestamp]
+
+Current Phase: [phase name]
+
+Progress Summary:
+  [N] needs approved across [N] blocks
+  [N] requirements registered ([N] baselined, [N] withdrawn)
+  Traceability coverage: [N]%
+
+-------------------------------------------------------------------
+RESUMPTION POINT:
+-------------------------------------------------------------------
+
+[Use the appropriate pattern based on state:]
+```
+
+**Pattern A -- Between blocks:**
+```
+All type passes complete for [previous block].
+Next block: [block-name]. Ready to begin functional requirements.
+```
+
+**Pattern B -- Mid-type-pass:**
+```
+Block: [block-name]
+Completed types: [list]
+Current type: [type] (in progress)
+[N] requirements registered for this block so far.
+```
+
+**Pattern C -- Draft requirements pending:**
+```
+Block: [block-name], Type: [type]
+[N] requirements in draft (passed quality check, not yet registered):
+  - [REQ-xxx]: [first 60 chars of statement]...
+  - [REQ-yyy]: [first 60 chars of statement]...
+These need confirmation before proceeding.
+```
+
+**Pattern D -- Needs phase:**
+```
+[N] needs approved. [N] blocks have completed needs formalization.
+[N] blocks remaining.
+```
+
+**Pattern E -- Init phase incomplete:**
+```
+Initialization started but not complete. Re-run /reqdev:init.
+```
+
+```
+-------------------------------------------------------------------
+
+Ready to continue?
+  [A] Continue from where we left off
+  [B] Show full status dashboard (/reqdev:status)
+  [C] Start a different phase
+
+===================================================================
+```
+
+## Step 4: Load Context for Resume
+
+Based on current phase, read relevant artifacts:
+
+| Phase | Artifacts to Load |
+|-------|-------------------|
+| init | (state only) |
+| needs | `needs_registry.json`, `ingestion.json` (block list) |
+| requirements | `needs_registry.json`, `requirements_registry.json`, `traceability_registry.json` |
+| deliver | All registries + any existing deliverable drafts |
+
+Read each artifact and provide a brief context summary.
+
+## Step 5: Handle Draft Requirements
+
+**CRITICAL:** When `progress.requirements_in_draft` is non-empty, handle drafts before continuing.
+
+Read each draft requirement from `requirements_registry.json`:
+
+```
+===================================================================
+DRAFT REQUIREMENTS TO RESOLVE
+===================================================================
+
+[For each draft REQ-xxx]:
+  REQ-xxx: "[statement]"
+    Type: [type]  Priority: [priority]  Block: [source-block]
+    Quality check: Passed (Tier 1)
+
+  Action:
+    [A] Register now (with parent need assignment)
+    [B] Discard (remove from registry)
+===================================================================
+```
+
+For registrations:
+```bash
+uv run scripts/requirement_tracker.py --workspace .requirements-dev register \
+  --id <REQ-xxx> --parent-need <NEED-xxx>
+```
+
+For discards:
+```bash
+uv run scripts/requirement_tracker.py --workspace .requirements-dev withdraw \
+  --id <REQ-xxx> --rationale "Discarded during resume"
+```
+
+After resolving all drafts, clear the list:
+```bash
+uv run scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'
+```
+
+## Step 6: Continue
+
+Based on user selection:
+
+- **Continue**: Invoke the appropriate command for the current phase. If in requirements phase mid-type-pass, `/reqdev:requirements` detects `progress.current_block` and `progress.current_type_pass` and skips completed passes.
+- **Dashboard**: Run `/reqdev:status`
+- **Different phase**: Ask which phase; verify gate prerequisites are met using:
+  ```bash
+  uv run scripts/update_state.py --state .requirements-dev check-gate <phase>
+  ```
+  Warn if prerequisites are not met.
diff --git a/skills/requirements-dev/commands/reqdev.status.md b/skills/requirements-dev/commands/reqdev.status.md
index 87aa1b4..f677a1f 100644
--- a/skills/requirements-dev/commands/reqdev.status.md
+++ b/skills/requirements-dev/commands/reqdev.status.md
@@ -1,6 +1,113 @@
 ---
 name: reqdev:status
-description: Session status dashboard
+description: Display session status dashboard showing current phase, block progress, requirement counts, traceability coverage, TBD/TBR counts, and quality check pass rate
 ---
 
-<!-- Command prompt for /reqdev:status. See section-08 (status/resume). -->
+# /reqdev:status -- Session Status Dashboard
+
+## Step 1: Load State
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev show
+```
+
+If no state file exists, inform the user:
+```
+No active session. Run /reqdev:init to start.
+```
+
+## Step 2: Sync Counts
+
+Ensure counts reflect current registry contents:
+
+```bash
+uv run scripts/update_state.py --state .requirements-dev sync-counts
+```
+
+## Step 3: Load Registry Summaries
+
+Read the registries to extract summary statistics:
+
+```bash
+cat .requirements-dev/state.json
+```
+
+If they exist, also read:
+- `cat .requirements-dev/needs_registry.json`
+- `cat .requirements-dev/requirements_registry.json`
+- `cat .requirements-dev/traceability_registry.json`
+
+## Step 4: Display Dashboard
+
+```
+===================================================================
+REQUIREMENTS DEVELOPMENT STATUS
+===================================================================
+
+Session: [id]
+Last Updated: [timestamp from state.json created_at]
+
+-------------------------------------------------------------------
+PHASES
+-------------------------------------------------------------------
+
+  [X/>/  ] 1. Init              [COMPLETED / IN PROGRESS / NOT STARTED]
+  [X/>/  ] 2. Needs             [COMPLETED / IN PROGRESS / NOT STARTED]
+  [X/>/  ] 3. Requirements      [COMPLETED / IN PROGRESS / NOT STARTED]
+  [X/>/  ] 4. Deliver           [COMPLETED / IN PROGRESS / NOT STARTED]
+
+Current Phase: [phase name]
+Gate Status: [passed / pending for each gate]
+
+-------------------------------------------------------------------
+BLOCK PROGRESS
+-------------------------------------------------------------------
+
+  Block: [block-name]
+    Types completed: [list, e.g., functional, performance]
+    Types remaining: [list, e.g., interface, constraint, quality]
+    Requirements: [N] registered
+
+  Block: [block-name]
+    [not started]
+
+-------------------------------------------------------------------
+REQUIREMENT COUNTS
+-------------------------------------------------------------------
+
+  Needs:        Total=[N]  Approved=[N]  Deferred=[N]
+  Requirements: Total=[N]  Registered=[N]  Baselined=[N]  Withdrawn=[N]
+  TBD open: [N]    TBR open: [N]
+
+-------------------------------------------------------------------
+TRACEABILITY
+-------------------------------------------------------------------
+
+  Links: [N]
+  Coverage: [N]% of needs have derived requirements
+
+-------------------------------------------------------------------
+DECOMPOSITION
+-------------------------------------------------------------------
+
+  Levels active: [list or "none"]
+  Max level: [N]
+
+===================================================================
+Next action: [suggested command based on current state]
+===================================================================
+```
+
+## Step 5: Suggest Next Action
+
+Based on the current state, suggest the most logical next step:
+
+| State | Suggestion |
+|-------|-----------|
+| No session | `/reqdev:init` |
+| Init complete, no needs | `/reqdev:needs` |
+| Needs complete | `/reqdev:requirements` |
+| Requirements in progress | "Continue with `/reqdev:requirements` or `/reqdev:resume`" |
+| Requirements complete | `/reqdev:deliver` |
+| Delivered, wants validation | `/reqdev:validate` |
+| All phases complete | "Requirements development complete!" |
diff --git a/skills/requirements-dev/tests/test_integration.py b/skills/requirements-dev/tests/test_integration.py
index 826aa45..cb4f95c 100644
--- a/skills/requirements-dev/tests/test_integration.py
+++ b/skills/requirements-dev/tests/test_integration.py
@@ -288,3 +288,87 @@ class TestMeteredInteractionState:
         drafts = state["progress"]["requirements_in_draft"]
         assert isinstance(drafts, list), f"Expected list, got {type(drafts)}"
         assert req_id in drafts
+
+
+# ---------------------------------------------------------------------------
+# Section 08: Resume flow tests
+# ---------------------------------------------------------------------------
+
+class TestResumeFlow:
+    """Verify state reading for resume after interruptions."""
+
+    def test_resume_after_need_registration(self, pipeline_workspace):
+        """After needs registered, state shows correct phase and counts."""
+        ws = str(pipeline_workspace)
+
+        # State already has init+needs gates passed, 2 approved needs
+        summary = update_state.show(ws)
+        assert "needs" in summary.lower() or "Phase" in summary
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+        assert state["counts"]["needs_approved"] == 2
+        assert state["gates"]["needs"] is True
+
+    def test_resume_mid_type_pass(self, pipeline_workspace):
+        """Mid-type-pass state shows current block and type."""
+        ws = str(pipeline_workspace)
+
+        # Set phase and progress
+        update_state.set_phase(ws, "requirements")
+        update_state.update_field(ws, "progress.current_block", "auth")
+        update_state.update_field(ws, "progress.current_type_pass", "performance")
+
+        # Add some requirements
+        for stmt in (
+            "The system shall authenticate in under 500ms",
+            "The system shall support 100 concurrent login sessions",
+        ):
+            req_id = requirement_tracker.add_requirement(
+                ws, stmt, "performance", "high", "auth",
+            )
+            requirement_tracker.register_requirement(ws, req_id, "NEED-001")
+
+        update_state.sync_counts(ws)
+
+        # Verify resume state
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+        assert state["progress"]["current_block"] == "auth"
+        assert state["progress"]["current_type_pass"] == "performance"
+        assert state["counts"]["requirements_registered"] == 2
+
+        # Show output includes position
+        summary = update_state.show(ws)
+        assert "auth" in summary
+        assert "performance" in summary
+
+    def test_resume_preserves_requirements_in_draft(self, pipeline_workspace):
+        """Draft requirements are preserved and readable for resume."""
+        ws = str(pipeline_workspace)
+
+        # Add drafts (not registered)
+        ids = []
+        for stmt in (
+            "The system shall encrypt passwords using bcrypt",
+            "The system shall enforce minimum password length of 12 characters",
+        ):
+            req_id = requirement_tracker.add_requirement(
+                ws, stmt, "functional", "high", "auth",
+            )
+            ids.append(req_id)
+
+        # Save drafts to state
+        update_state.update_field(
+            ws, "progress.requirements_in_draft", json.dumps(ids),
+        )
+
+        # Verify state correctly reports drafts
+        state = json.loads((pipeline_workspace / "state.json").read_text())
+        drafts = state["progress"]["requirements_in_draft"]
+        assert isinstance(drafts, list)
+        assert len(drafts) == 2
+        assert all(d.startswith("REQ-") for d in drafts)
+
+        # Verify draft requirements exist in registry with draft status
+        reg = requirement_tracker._load_registry(ws)
+        for req_id in drafts:
+            req = next(r for r in reg["requirements"] if r["id"] == req_id)
+            assert req["status"] == "draft"
