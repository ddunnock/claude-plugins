diff --git a/skills/requirements-dev/pyproject.toml b/skills/requirements-dev/pyproject.toml
new file mode 100644
index 0000000..1d111c6
--- /dev/null
+++ b/skills/requirements-dev/pyproject.toml
@@ -0,0 +1,10 @@
+[project]
+name = "requirements-dev"
+version = "1.0.0"
+description = "INCOSE-compliant requirements development plugin"
+requires-python = ">=3.11"
+
+[tool.uv]
+dev-dependencies = [
+    "pytest>=7.0",
+]
diff --git a/skills/requirements-dev/scripts/init_session.py b/skills/requirements-dev/scripts/init_session.py
index d30b61a..14fd9b3 100644
--- a/skills/requirements-dev/scripts/init_session.py
+++ b/skills/requirements-dev/scripts/init_session.py
@@ -1 +1,116 @@
-"""Initialize requirements-dev workspace and state.json."""
+"""Initialize requirements-dev workspace and state.json.
+
+Usage: python3 init_session.py <project_path>
+
+Creates .requirements-dev/ directory under project_path with an initialized
+state.json. If workspace already exists, prints a message and exits without
+overwriting (supports resume).
+"""
+import argparse
+import json
+import os
+import sys
+import uuid
+from datetime import datetime, timezone
+from pathlib import Path
+from tempfile import NamedTemporaryFile
+
+
+WORKSPACE_DIR = ".requirements-dev"
+TEMPLATE_FILENAME = "state.json"
+
+
+def _validate_dir_path(path: str) -> str:
+    """Validate and resolve a directory path argument. Reject '..' traversal.
+
+    Returns os.path.realpath() resolved path.
+    """
+    if ".." in path.split(os.sep):
+        print(f"Error: Path contains '..' traversal: {path}", file=sys.stderr)
+        sys.exit(1)
+    resolved = os.path.realpath(path)
+    return resolved
+
+
+def _get_template_path() -> str:
+    """Return absolute path to templates/state.json relative to this script's location."""
+    script_dir = Path(__file__).resolve().parent
+    return str(script_dir.parent / "templates" / TEMPLATE_FILENAME)
+
+
+def _atomic_write(filepath: str, data: dict) -> None:
+    """Write JSON data atomically using temp-file-then-rename pattern."""
+    target_dir = os.path.dirname(os.path.abspath(filepath))
+    fd = NamedTemporaryFile(
+        mode="w",
+        dir=target_dir,
+        suffix=".tmp",
+        delete=False,
+    )
+    try:
+        json.dump(data, fd, indent=2)
+        fd.write("\n")
+        fd.flush()
+        os.fsync(fd.fileno())
+        fd.close()
+        os.rename(fd.name, filepath)
+    except Exception:
+        fd.close()
+        try:
+            os.unlink(fd.name)
+        except OSError:
+            pass
+        raise
+
+
+def init_workspace(project_path: str) -> dict:
+    """Create workspace and initialize state.json.
+
+    Returns the initialized (or existing) state dict.
+    """
+    resolved_path = _validate_dir_path(project_path)
+    ws_path = os.path.join(resolved_path, WORKSPACE_DIR)
+    state_path = os.path.join(ws_path, "state.json")
+
+    # Check for existing workspace (resume scenario)
+    if os.path.isfile(state_path):
+        with open(state_path) as f:
+            existing_state = json.load(f)
+        session_id = existing_state.get("session_id", "unknown")
+        print(
+            f"Workspace already initialized (session: {session_id}). "
+            "Use /reqdev:resume to continue."
+        )
+        return existing_state
+
+    # Create workspace directory
+    os.makedirs(ws_path, exist_ok=True)
+
+    # Read template
+    template_path = _get_template_path()
+    with open(template_path) as f:
+        state = json.load(f)
+
+    # Populate session fields
+    state["session_id"] = uuid.uuid4().hex
+    state["created_at"] = datetime.now(timezone.utc).isoformat()
+
+    # Write state atomically
+    _atomic_write(state_path, state)
+
+    print(f"Initialized requirements-dev workspace at {ws_path}")
+    print(f"Session ID: {state['session_id']}")
+    return state
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Initialize requirements-dev workspace")
+    parser.add_argument("project_path", help="Path to the project root directory")
+    args = parser.parse_args()
+
+    init_workspace(args.project_path)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/scripts/update_state.py b/skills/requirements-dev/scripts/update_state.py
index cc127ff..0c77498 100644
--- a/skills/requirements-dev/scripts/update_state.py
+++ b/skills/requirements-dev/scripts/update_state.py
@@ -1 +1,297 @@
-"""State management with atomic writes."""
+"""Update requirements-dev session state.
+
+Usage:
+    python3 update_state.py --state <state_file> set-phase <phase>
+    python3 update_state.py --state <state_file> pass-gate <phase>
+    python3 update_state.py --state <state_file> check-gate <phase>
+    python3 update_state.py --state <state_file> set-artifact <phase> <path> [--key <key>]
+    python3 update_state.py --state <state_file> update <dotted.path> <value>
+    python3 update_state.py --state <state_file> sync-counts
+    python3 update_state.py --state <state_file> show
+
+All mutations use atomic write (temp-file-then-rename).
+"""
+import argparse
+import json
+import os
+import sys
+from pathlib import Path
+from tempfile import NamedTemporaryFile
+
+
+VALID_PHASES = ("init", "needs", "requirements", "validate", "deliver", "decompose")
+STATE_FILENAME = "state.json"
+
+
+def _validate_path(path: str, allowed_extensions: list[str] | None = None) -> str:
+    """Validate and resolve a path argument. Reject '..' traversal."""
+    if ".." in path.split(os.sep):
+        print(f"Error: Path contains '..' traversal: {path}", file=sys.stderr)
+        sys.exit(1)
+    resolved = os.path.realpath(path)
+    if allowed_extensions:
+        ext = os.path.splitext(resolved)[1].lower()
+        if ext not in allowed_extensions:
+            print(f"Error: Extension '{ext}' not in {allowed_extensions}", file=sys.stderr)
+            sys.exit(1)
+    return resolved
+
+
+def _atomic_write(filepath: str, data: dict) -> None:
+    """Write JSON data atomically using temp-file-then-rename pattern."""
+    target_dir = os.path.dirname(os.path.abspath(filepath))
+    fd = NamedTemporaryFile(
+        mode="w",
+        dir=target_dir,
+        suffix=".tmp",
+        delete=False,
+    )
+    try:
+        json.dump(data, fd, indent=2)
+        fd.write("\n")
+        fd.flush()
+        os.fsync(fd.fileno())
+        fd.close()
+        os.rename(fd.name, filepath)
+    except Exception:
+        fd.close()
+        try:
+            os.unlink(fd.name)
+        except OSError:
+            pass
+        raise
+
+
+def _load_state(workspace_path: str) -> dict:
+    """Load state.json from workspace. Raise FileNotFoundError if missing."""
+    state_file = os.path.join(workspace_path, STATE_FILENAME)
+    if not os.path.isfile(state_file):
+        raise FileNotFoundError(f"State file not found: {state_file}")
+    with open(state_file) as f:
+        return json.load(f)
+
+
+def _save_state(workspace_path: str, state: dict) -> None:
+    """Save state.json atomically."""
+    state_file = os.path.join(workspace_path, STATE_FILENAME)
+    _atomic_write(state_file, state)
+
+
+def set_phase(workspace_path: str, phase: str) -> None:
+    """Set current_phase to the given phase name."""
+    state = _load_state(workspace_path)
+    state["current_phase"] = phase
+    _save_state(workspace_path, state)
+
+
+def pass_gate(workspace_path: str, phase: str) -> None:
+    """Mark a phase gate as passed. Idempotent."""
+    state = _load_state(workspace_path)
+    if phase in state.get("gates", {}):
+        state["gates"][phase] = True
+    _save_state(workspace_path, state)
+
+
+def check_gate(workspace_path: str, phase: str) -> bool:
+    """Check if a phase gate has been passed."""
+    state = _load_state(workspace_path)
+    return state.get("gates", {}).get(phase, False)
+
+
+def set_artifact(workspace_path: str, phase: str, artifact_path: str, key: str | None = None) -> None:
+    """Record a deliverable artifact path under artifacts.<phase>."""
+    state = _load_state(workspace_path)
+    if "artifacts" not in state:
+        state["artifacts"] = {}
+
+    if key:
+        # Store under artifacts.<phase>.<key>
+        if phase not in state["artifacts"] or not isinstance(state["artifacts"].get(phase), dict):
+            state["artifacts"][phase] = {}
+        state["artifacts"][phase][key] = artifact_path
+    else:
+        # Store directly under artifacts.<phase>
+        state["artifacts"][phase] = artifact_path
+
+    _save_state(workspace_path, state)
+
+
+def _parse_value(value_str: str):
+    """Parse a string value to the appropriate Python type."""
+    if value_str == "null":
+        return None
+    if value_str == "true":
+        return True
+    if value_str == "false":
+        return False
+    try:
+        return int(value_str)
+    except ValueError:
+        pass
+    try:
+        return float(value_str)
+    except ValueError:
+        pass
+    return value_str
+
+
+def update_field(workspace_path: str, dotted_path: str, value: str) -> None:
+    """Update a nested field using dot notation."""
+    state = _load_state(workspace_path)
+    parts = dotted_path.split(".")
+    target = state
+    for part in parts[:-1]:
+        target = target[part]
+    target[parts[-1]] = _parse_value(value)
+    _save_state(workspace_path, state)
+
+
+def sync_counts(workspace_path: str) -> None:
+    """Read registries and update all count fields in state.json."""
+    state = _load_state(workspace_path)
+
+    # Read needs registry
+    needs_file = os.path.join(workspace_path, "needs_registry.json")
+    if os.path.isfile(needs_file):
+        with open(needs_file) as f:
+            needs = json.load(f)
+    else:
+        needs = []
+
+    # Read requirements registry
+    reqs_file = os.path.join(workspace_path, "requirements_registry.json")
+    if os.path.isfile(reqs_file):
+        with open(reqs_file) as f:
+            reqs = json.load(f)
+    else:
+        reqs = []
+
+    # Compute needs counts
+    state["counts"]["needs_total"] = len(needs)
+    state["counts"]["needs_approved"] = sum(1 for n in needs if n.get("status") == "approved")
+    state["counts"]["needs_deferred"] = sum(1 for n in needs if n.get("status") == "deferred")
+
+    # Compute requirements counts
+    state["counts"]["requirements_total"] = len(reqs)
+    state["counts"]["requirements_registered"] = sum(
+        1 for r in reqs if r.get("status") == "registered"
+    )
+    state["counts"]["requirements_baselined"] = sum(
+        1 for r in reqs if r.get("status") == "baselined"
+    )
+    state["counts"]["requirements_withdrawn"] = sum(
+        1 for r in reqs if r.get("status") == "withdrawn"
+    )
+
+    # Compute TBD/TBR counts
+    tbd_count = 0
+    tbr_count = 0
+    for r in reqs:
+        tbd_tbr = r.get("tbd_tbr")
+        if tbd_tbr:
+            if tbd_tbr.get("tbd"):
+                tbd_count += 1
+            if tbd_tbr.get("tbr"):
+                tbr_count += 1
+    state["counts"]["tbd_open"] = tbd_count
+    state["counts"]["tbr_open"] = tbr_count
+
+    _save_state(workspace_path, state)
+
+
+def show(workspace_path: str) -> str:
+    """Return a human-readable summary of current state."""
+    state = _load_state(workspace_path)
+    lines = []
+    lines.append(f"Session: {state.get('session_id', 'unknown')}")
+    lines.append(f"Phase:   {state.get('current_phase', 'unknown')}")
+    lines.append("")
+
+    # Gates
+    lines.append("Gates:")
+    for gate, passed in state.get("gates", {}).items():
+        mark = "+" if passed else "-"
+        lines.append(f"  [{mark}] {gate}")
+    lines.append("")
+
+    # Counts
+    lines.append("Counts:")
+    for key, val in state.get("counts", {}).items():
+        lines.append(f"  {key}: {val}")
+    lines.append("")
+
+    # Progress
+    progress = state.get("progress", {})
+    block = progress.get("current_block") or "none"
+    type_pass = progress.get("current_type_pass") or "none"
+    lines.append(f"Progress: block={block}, type_pass={type_pass}")
+
+    result = "\n".join(lines)
+    print(result)
+    return result
+
+
+def main():
+    """CLI entry point with argparse subcommands."""
+    parser = argparse.ArgumentParser(description="Update requirements-dev session state")
+    parser.add_argument("--state", required=True, help="Path to state.json or workspace directory")
+
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    # set-phase
+    sp = subparsers.add_parser("set-phase")
+    sp.add_argument("phase", choices=VALID_PHASES)
+
+    # pass-gate
+    sp = subparsers.add_parser("pass-gate")
+    sp.add_argument("phase")
+
+    # check-gate
+    sp = subparsers.add_parser("check-gate")
+    sp.add_argument("phase")
+
+    # set-artifact
+    sp = subparsers.add_parser("set-artifact")
+    sp.add_argument("phase")
+    sp.add_argument("path")
+    sp.add_argument("--key", default=None)
+
+    # update
+    sp = subparsers.add_parser("update")
+    sp.add_argument("dotted_path")
+    sp.add_argument("value")
+
+    # sync-counts
+    subparsers.add_parser("sync-counts")
+
+    # show
+    subparsers.add_parser("show")
+
+    args = parser.parse_args()
+
+    # Resolve workspace path from --state
+    state_path = args.state
+    if os.path.isfile(state_path) and state_path.endswith(".json"):
+        workspace = os.path.dirname(state_path)
+    else:
+        workspace = state_path
+
+    if args.command == "set-phase":
+        set_phase(workspace, args.phase)
+    elif args.command == "pass-gate":
+        pass_gate(workspace, args.phase)
+    elif args.command == "check-gate":
+        passed = check_gate(workspace, args.phase)
+        sys.exit(0 if passed else 1)
+    elif args.command == "set-artifact":
+        set_artifact(workspace, args.phase, args.path, key=args.key)
+    elif args.command == "update":
+        update_field(workspace, args.dotted_path, args.value)
+    elif args.command == "sync-counts":
+        sync_counts(workspace)
+    elif args.command == "show":
+        show(workspace)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/conftest.py b/skills/requirements-dev/tests/conftest.py
index 065041d..06bc6c8 100644
--- a/skills/requirements-dev/tests/conftest.py
+++ b/skills/requirements-dev/tests/conftest.py
@@ -1,8 +1,14 @@
 """Shared test fixtures for requirements-dev tests."""
 import json
+import sys
+from pathlib import Path
 
 import pytest
 
+# Add scripts directory to path for imports
+SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
+sys.path.insert(0, str(SCRIPTS_DIR))
+
 
 @pytest.fixture
 def tmp_workspace(tmp_path):
@@ -10,20 +16,35 @@ def tmp_workspace(tmp_path):
 
     Returns the path to the .requirements-dev/ directory.
     """
-    workspace = tmp_path / ".requirements-dev"
-    workspace.mkdir()
-
-    # Load state template and initialize
-    template_path = (
-        pytest.importorskip("pathlib").Path(__file__).parent.parent
-        / "templates"
-        / "state.json"
-    )
-    state = json.loads(template_path.read_text())
-    state["session_id"] = "test-session-001"
-    state["created_at"] = "2025-01-01T00:00:00Z"
-
-    state_file = workspace / "state.json"
-    state_file.write_text(json.dumps(state, indent=2))
-
-    return workspace
+    ws = tmp_path / ".requirements-dev"
+    ws.mkdir()
+    state = {
+        "session_id": "abc123",
+        "schema_version": "1.0.0",
+        "created_at": "2025-01-01T00:00:00+00:00",
+        "current_phase": "init",
+        "gates": {"init": False, "needs": False, "requirements": False, "deliver": False},
+        "blocks": {},
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
+    return ws
diff --git a/skills/requirements-dev/tests/test_init_session.py b/skills/requirements-dev/tests/test_init_session.py
new file mode 100644
index 0000000..0a56305
--- /dev/null
+++ b/skills/requirements-dev/tests/test_init_session.py
@@ -0,0 +1,64 @@
+"""Tests for init_session.py workspace initialization."""
+import json
+
+import pytest
+
+from init_session import init_workspace
+
+
+def test_init_creates_workspace_directory(tmp_path):
+    """Calling init with a project path creates .requirements-dev/ under that path."""
+    result = init_workspace(str(tmp_path))
+    ws = tmp_path / ".requirements-dev"
+    assert ws.is_dir()
+
+
+def test_init_creates_state_json_from_template(tmp_path):
+    """state.json is created with a non-empty session_id and schema_version '1.0.0'."""
+    result = init_workspace(str(tmp_path))
+    state_file = tmp_path / ".requirements-dev" / "state.json"
+    assert state_file.exists()
+
+    state = json.loads(state_file.read_text())
+    assert state["session_id"] != ""
+    assert len(state["session_id"]) == 32  # uuid4 hex
+    assert state["schema_version"] == "1.0.0"
+    assert state["created_at"] != ""
+
+
+def test_init_state_has_zero_counts(tmp_path):
+    """All count fields in the initialized state.json must be zero."""
+    init_workspace(str(tmp_path))
+    state = json.loads((tmp_path / ".requirements-dev" / "state.json").read_text())
+
+    for key, value in state["counts"].items():
+        assert value == 0, f"counts.{key} should be 0, got {value}"
+
+
+def test_init_state_has_null_progress(tmp_path):
+    """progress.current_block and progress.current_type_pass must be null on init."""
+    init_workspace(str(tmp_path))
+    state = json.loads((tmp_path / ".requirements-dev" / "state.json").read_text())
+
+    assert state["progress"]["current_block"] is None
+    assert state["progress"]["current_type_pass"] is None
+
+
+def test_init_does_not_overwrite_existing_workspace(tmp_path):
+    """If .requirements-dev/ already exists with a state.json, init must not overwrite it."""
+    # First init
+    init_workspace(str(tmp_path))
+    state_file = tmp_path / ".requirements-dev" / "state.json"
+    original_state = json.loads(state_file.read_text())
+    original_session_id = original_state["session_id"]
+
+    # Second init -- should preserve original
+    result = init_workspace(str(tmp_path))
+    state = json.loads(state_file.read_text())
+    assert state["session_id"] == original_session_id
+
+
+def test_init_validates_path_rejects_traversal(tmp_path):
+    """Path arguments containing '..' must be rejected for security."""
+    with pytest.raises(SystemExit):
+        init_workspace(str(tmp_path / ".." / "evil"))
diff --git a/skills/requirements-dev/tests/test_update_state.py b/skills/requirements-dev/tests/test_update_state.py
new file mode 100644
index 0000000..b5c5bc5
--- /dev/null
+++ b/skills/requirements-dev/tests/test_update_state.py
@@ -0,0 +1,118 @@
+"""Tests for update_state.py state mutation operations."""
+import json
+
+import pytest
+
+from update_state import (
+    check_gate,
+    pass_gate,
+    set_artifact,
+    set_phase,
+    show,
+    sync_counts,
+    update_field,
+)
+
+
+def test_set_phase_updates_current_phase(tmp_workspace):
+    """set-phase 'needs' should change current_phase from 'init' to 'needs'."""
+    set_phase(str(tmp_workspace), "needs")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert state["current_phase"] == "needs"
+
+
+def test_pass_gate_sets_gate_true(tmp_workspace):
+    """pass-gate 'init' should set gates.init to true."""
+    pass_gate(str(tmp_workspace), "init")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert state["gates"]["init"] is True
+
+
+def test_pass_gate_idempotent(tmp_workspace):
+    """Passing a gate that is already true should not error or change anything."""
+    pass_gate(str(tmp_workspace), "init")
+    pass_gate(str(tmp_workspace), "init")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert state["gates"]["init"] is True
+
+
+def test_check_gate_returns_correct_value(tmp_workspace):
+    """check-gate should return True for passed gates, False for unpassed gates."""
+    assert check_gate(str(tmp_workspace), "init") is False
+    pass_gate(str(tmp_workspace), "init")
+    assert check_gate(str(tmp_workspace), "init") is True
+
+
+def test_set_artifact_stores_path(tmp_workspace):
+    """set-artifact 'deliver' 'REQUIREMENTS-SPECIFICATION.md' should store the path."""
+    set_artifact(str(tmp_workspace), "deliver", "REQUIREMENTS-SPECIFICATION.md")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert "deliver" in state["artifacts"]
+    assert state["artifacts"]["deliver"] == "REQUIREMENTS-SPECIFICATION.md"
+
+
+def test_set_artifact_with_key(tmp_workspace):
+    """set-artifact with --key should store under artifacts.<phase>.<key>."""
+    set_artifact(str(tmp_workspace), "deliver", "/path/to/SPEC.md", key="specification_artifact")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert state["artifacts"]["deliver"]["specification_artifact"] == "/path/to/SPEC.md"
+
+
+def test_update_dotted_path(tmp_workspace):
+    """update 'counts.needs_total' '5' should set state['counts']['needs_total'] to 5."""
+    update_field(str(tmp_workspace), "counts.needs_total", "5")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert state["counts"]["needs_total"] == 5
+
+
+def test_sync_counts_from_registries(tmp_workspace):
+    """sync-counts should read registries and update count fields."""
+    # Create a needs registry
+    needs = [
+        {"id": "NEED-001", "status": "approved"},
+        {"id": "NEED-002", "status": "approved"},
+        {"id": "NEED-003", "status": "deferred"},
+    ]
+    (tmp_workspace / "needs_registry.json").write_text(json.dumps(needs, indent=2))
+
+    # Create a requirements registry
+    reqs = [
+        {"id": "REQ-001", "status": "registered", "tbd_tbr": None},
+        {"id": "REQ-002", "status": "baselined", "tbd_tbr": None},
+        {"id": "REQ-003", "status": "registered", "tbd_tbr": {"tbd": ["value TBD"]}},
+    ]
+    (tmp_workspace / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))
+
+    sync_counts(str(tmp_workspace))
+    state = json.loads((tmp_workspace / "state.json").read_text())
+
+    assert state["counts"]["needs_total"] == 3
+    assert state["counts"]["needs_approved"] == 2
+    assert state["counts"]["needs_deferred"] == 1
+    assert state["counts"]["requirements_total"] == 3
+    assert state["counts"]["requirements_registered"] == 2
+    assert state["counts"]["requirements_baselined"] == 1
+    assert state["counts"]["tbd_open"] == 1
+
+
+def test_show_returns_summary(tmp_workspace, capsys):
+    """show should print current phase, gate status, and counts."""
+    result = show(str(tmp_workspace))
+    assert "init" in result
+    assert "session_id" in result.lower() or "abc123" in result
+
+
+def test_atomic_write_uses_temp_file(tmp_workspace, monkeypatch):
+    """All state mutations must use atomic write pattern."""
+    import update_state
+
+    writes = []
+    original_atomic = update_state._atomic_write
+
+    def tracking_atomic(filepath, data):
+        writes.append(filepath)
+        original_atomic(filepath, data)
+
+    monkeypatch.setattr(update_state, "_atomic_write", tracking_atomic)
+    set_phase(str(tmp_workspace), "needs")
+    assert len(writes) == 1
