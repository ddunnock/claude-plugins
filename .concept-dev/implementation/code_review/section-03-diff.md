diff --git a/skills/requirements-dev/commands/reqdev.init.md b/skills/requirements-dev/commands/reqdev.init.md
index 76ace13..1379a46 100644
--- a/skills/requirements-dev/commands/reqdev.init.md
+++ b/skills/requirements-dev/commands/reqdev.init.md
@@ -3,4 +3,177 @@ name: reqdev:init
 description: Initialize requirements-dev session and ingest concept-dev artifacts
 ---
 
-<!-- Command prompt for /reqdev:init. See section-03 (concept ingestion). -->
+# /reqdev:init -- Initialize Requirements Development Session
+
+This command initializes the requirements development workspace and ingests concept-dev artifacts.
+
+## Step 1: Initialize Workspace
+
+Run the session initialization script:
+
+```bash
+uv run scripts/init_session.py <project_path>
+```
+
+Where `<project_path>` is the project root (typically the current working directory).
+
+- If workspace already exists, the script prints the existing session ID and suggests `/reqdev:resume`
+- If creating new, the script creates `.requirements-dev/` with `state.json`
+
+## Step 2: Ingest Concept-Dev Artifacts
+
+Run the concept ingestion script:
+
+```bash
+uv run scripts/ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json
+```
+
+Check the returned JSON output:
+- `artifact_inventory`: Which concept-dev files exist
+- `gate_status`: Whether all concept-dev gates were passed
+- `source_refs`: Sources from concept-dev (carried forward)
+- `assumption_refs`: Assumptions from concept-dev (carried forward)
+
+If `gate_status.warnings` has entries, display them to the user with a note that proceeding without all gates passed may result in incomplete ingestion.
+
+## Step 3: Branch on Concept-Dev Availability
+
+### If concept-dev artifacts found
+
+Check `artifact_inventory` for `CONCEPT-DOCUMENT.md` and `BLACKBOX.md`.
+
+If both exist, read and extract structured data:
+
+1. **Read `BLACKBOX.md`** and extract:
+   - Block names and descriptions
+   - Block-to-block relationships (uses, provides, depends)
+   - Interface descriptions between blocks
+
+2. **Read `CONCEPT-DOCUMENT.md`** and extract:
+   - Capabilities per block
+   - ConOps scenarios
+   - Stakeholder needs candidates (statements beginning with "The user needs...", "The system shall...", or similar requirement-like patterns)
+
+3. **Read `SOLUTION-LANDSCAPE.md`** if present for additional context (alternatives, trade-offs)
+
+Format extracted data as:
+
+```json
+{
+  "blocks": [
+    {
+      "name": "block-name",
+      "description": "One-line description",
+      "relationships": [{"target": "other-block", "type": "uses|provides|depends"}],
+      "interfaces": ["interface description"],
+      "capabilities": ["capability 1", "capability 2"]
+    }
+  ],
+  "needs_candidates": [
+    {
+      "source_block": "block-name",
+      "statement": "The user needs...",
+      "source_artifact": "CONCEPT-DOCUMENT.md",
+      "source_section": "Section heading where found"
+    }
+  ]
+}
+```
+
+4. **Update `ingestion.json`**: Read the existing `.requirements-dev/ingestion.json` (written by `ingest_concept.py`), add the `blocks` and `needs_candidates` keys, and write it back.
+
+5. **Present extraction summary** to user:
+
+```
+CONCEPT INGESTION SUMMARY
+=========================
+Blocks found:          {N}
+Needs candidates:      {M}
+Sources carried:       {S}
+Assumptions carried:   {A}
+Gate warnings:         {W}
+
+Blocks:
+  - block-1: description...
+  - block-2: description...
+
+Needs candidates (first 5):
+  1. "The user needs..." (from block-1, CONCEPT-DOCUMENT.md)
+  2. ...
+```
+
+Ask user to confirm before proceeding.
+
+### If concept-dev artifacts NOT found (manual mode)
+
+Inform the user:
+
+```
+No concept-dev artifacts found. Entering manual mode.
+You'll define the system's functional blocks and capabilities directly.
+```
+
+Guide through manual block definition:
+
+1. Ask: "How many functional blocks does your system have?"
+2. For each block, collect:
+   - Name (short identifier, kebab-case)
+   - Description (1-2 sentences)
+   - 3-5 key capabilities
+3. After all blocks, ask about inter-block interfaces
+4. Present complete summary table for approval
+5. Only proceed after explicit user confirmation
+
+Write manual entries to `.requirements-dev/ingestion.json` using the same JSON structure as the automated path (with `source_artifact: "manual"` in needs_candidates).
+
+## Step 4: Detect Research Tools
+
+Run the tool availability checker:
+
+```bash
+uv run scripts/check_tools.py --state .requirements-dev/state.json --json
+```
+
+Display available tools summary to the user. Note which tools are available for Phase 2 TPM research.
+
+## Step 5: Update State
+
+Use `update_state.py` to record initialization completion:
+
+```bash
+# Set phase
+uv run scripts/update_state.py --state .requirements-dev/state.json set-phase init
+
+# Pass the init gate
+uv run scripts/update_state.py --state .requirements-dev/state.json pass-gate init
+
+# Record blocks (one per block discovered/defined)
+# For each block, use the update command to add to blocks dict:
+uv run scripts/update_state.py --state .requirements-dev/state.json update blocks.<block-name> "<description>"
+```
+
+## Step 6: Display Final Summary
+
+```
+REQUIREMENTS-DEV SESSION INITIALIZED
+=====================================
+Session ID:       {session_id}
+Workspace:        .requirements-dev/
+Ingestion source: {concept-dev | manual}
+
+Blocks:           {N} defined
+Needs candidates: {M} extracted
+Sources:          {S} carried from concept-dev
+Assumptions:      {A} carried from concept-dev
+Research tools:   {T} detected
+
+Next steps:
+  /reqdev:needs    -- Formalize needs from candidates
+  /reqdev:status   -- View current session status
+```
+
+## Important Notes
+
+- **JSON parsing in scripts, markdown extraction by LLM**: The split is intentional. `ingest_concept.py` handles structured JSON data (deterministic, testable). Markdown reading and extraction is done by Claude directly (adaptive to format variations).
+- **Atomic writes**: All JSON file writes use temp-file-then-rename pattern via `shared_io._atomic_write`.
+- **Path validation**: All paths are validated to reject `..` traversal.
diff --git a/skills/requirements-dev/scripts/check_tools.py b/skills/requirements-dev/scripts/check_tools.py
index 44d6f2b..cb3c9a5 100644
--- a/skills/requirements-dev/scripts/check_tools.py
+++ b/skills/requirements-dev/scripts/check_tools.py
@@ -1 +1,184 @@
-"""Detect available research tools (WebSearch, crawl4ai, MCP)."""
+"""Detect available research tools (WebSearch, crawl4ai, MCP).
+
+Probes for various research tools and reports availability by tier.
+Results are stored in state.json for research agents to adapt strategy.
+
+Adapted from concept-dev check_tools.py for requirements-dev context.
+"""
+import argparse
+import json
+import subprocess
+from datetime import datetime
+from pathlib import Path
+from typing import Optional
+
+from shared_io import _atomic_write, _validate_path
+
+
+# Tool definitions by tier
+TOOL_TIERS = {
+    "always": {
+        "WebSearch": "Built-in web search",
+        "WebFetch": "Built-in URL fetching",
+    },
+    "python_packages": {
+        "crawl4ai": "Deep web crawling (Python package)",
+    },
+    "tier1": {
+        "mcp__jina": "Jina Reader document parsing",
+        "mcp__paper_search": "Academic paper search",
+        "mcp__fetch": "MCP fetch tool",
+    },
+    "tier2": {
+        "mcp__tavily": "Tavily AI search",
+        "mcp__semantic_scholar": "Semantic Scholar API",
+        "mcp__context7": "Context7 documentation search",
+    },
+    "tier3": {
+        "mcp__exa": "Exa neural search",
+        "mcp__perplexity": "Perplexity Sonar",
+    },
+}
+
+
+def detect_python_package(package_name: str) -> dict:
+    """Check if a Python package is importable, including in pipx venvs.
+
+    Returns:
+        dict with 'available' (bool) and 'python' (str path to interpreter)
+    """
+    # Try system Python first
+    try:
+        result = subprocess.run(
+            ["python3", "-c", f"import {package_name}"],
+            capture_output=True,
+            timeout=10,
+        )
+        if result.returncode == 0:
+            return {"available": True, "python": "python3"}
+    except (subprocess.TimeoutExpired, FileNotFoundError):
+        pass
+
+    # Try pipx venv
+    pipx_python = (
+        Path.home()
+        / ".local"
+        / "pipx"
+        / "venvs"
+        / package_name
+        / "bin"
+        / "python3"
+    )
+    if pipx_python.exists():
+        try:
+            result = subprocess.run(
+                [str(pipx_python), "-c", f"import {package_name}"],
+                capture_output=True,
+                timeout=10,
+            )
+            if result.returncode == 0:
+                return {"available": True, "python": str(pipx_python)}
+        except (subprocess.TimeoutExpired, FileNotFoundError):
+            pass
+
+    return {"available": False, "python": None}
+
+
+def check_tools(state_path: Optional[str] = None) -> dict:
+    """Report tool tier definitions and detect Python packages.
+
+    Python package detection (crawl4ai) happens here via import check.
+    MCP tool detection happens at runtime within Claude via ToolSearch.
+
+    Args:
+        state_path: Optional path to state.json to update
+
+    Returns:
+        Tool availability report
+    """
+    # Detect Python packages
+    python_results = {}
+    for pkg in TOOL_TIERS["python_packages"]:
+        python_results[pkg] = detect_python_package(pkg)
+
+    report = {
+        "detected_at": datetime.now().isoformat(),
+        "always_available": list(TOOL_TIERS["always"].keys()),
+        "python_packages": python_results,
+        "tier1_tools": TOOL_TIERS["tier1"],
+        "tier2_tools": TOOL_TIERS["tier2"],
+        "tier3_tools": TOOL_TIERS["tier3"],
+    }
+
+    if state_path:
+        path = Path(state_path)
+        if path.exists():
+            with open(path) as f:
+                state = json.load(f)
+            # Create tools key if absent (requirements-dev template doesn't include it)
+            if "tools" not in state:
+                state["tools"] = {}
+            state["tools"]["detected_at"] = report["detected_at"]
+            # Record detected Python packages as available tools
+            detected = list(TOOL_TIERS["always"].keys())
+            for pkg, info in python_results.items():
+                if info["available"]:
+                    detected.append(pkg)
+            state["tools"]["available"] = detected
+            state["tools"]["python_packages"] = python_results
+            _atomic_write(state_path, state)
+
+    return report
+
+
+# Tier display labels and status icons
+_TIER_DISPLAY = [
+    ("always", "ALWAYS AVAILABLE", "+"),
+    ("python_packages", "PYTHON PACKAGES (detected via import)", "?"),
+    ("tier1", "TIER 1 (Free MCP tools -- detect at init)", "?"),
+    ("tier2", "TIER 2 (Configurable)", "?"),
+    ("tier3", "TIER 3 (Premium, optional)", "?"),
+]
+
+
+def print_report():
+    """Print formatted tool availability report."""
+    print("=" * 70)
+    print("RESEARCH TOOL AVAILABILITY")
+    print("=" * 70)
+
+    for tier_key, label, icon in _TIER_DISPLAY:
+        print(f"\n{label}:")
+        for tool, tool_desc in TOOL_TIERS[tier_key].items():
+            if tier_key == "python_packages":
+                info = detect_python_package(tool)
+                status = "+" if info["available"] else "-"
+                via = f" (via {info['python']})" if info["available"] else ""
+                print(f"  [{status}] {tool} -- {tool_desc}{via}")
+            else:
+                print(f"  [{icon}] {tool} -- {tool_desc}")
+
+    print("\n" + "=" * 70)
+    print("Run /reqdev:init to detect which MCP tools are available.")
+    print("=" * 70)
+
+
+def main():
+    parser = argparse.ArgumentParser(description="Check available research tools")
+    parser.add_argument("--state", help="Path to state.json to update")
+    parser.add_argument("--json", action="store_true", help="Output as JSON")
+
+    args = parser.parse_args()
+
+    if args.state:
+        args.state = _validate_path(args.state, allowed_extensions=[".json"])
+    report = check_tools(args.state)
+
+    if args.json:
+        print(json.dumps(report, indent=2))
+    else:
+        print_report()
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/scripts/ingest_concept.py b/skills/requirements-dev/scripts/ingest_concept.py
index 5c662b3..3652432 100644
--- a/skills/requirements-dev/scripts/ingest_concept.py
+++ b/skills/requirements-dev/scripts/ingest_concept.py
@@ -1 +1,137 @@
-"""Parse concept-dev JSON registries and validate artifacts."""
+"""Parse concept-dev JSON registries and validate artifacts.
+
+Usage: python3 ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json
+
+Parses JSON registries (source_registry.json, assumption_registry.json, state.json)
+and validates artifact presence. Markdown extraction is LLM-assisted via the
+/reqdev:init command prompt.
+"""
+import argparse
+import json
+import os
+from datetime import datetime, timezone
+
+from shared_io import _atomic_write, _validate_dir_path, _validate_path
+
+# Artifacts to check for presence
+EXPECTED_ARTIFACTS = [
+    "CONCEPT-DOCUMENT.md",
+    "BLACKBOX.md",
+    "SOLUTION-LANDSCAPE.md",
+    "source_registry.json",
+    "assumption_registry.json",
+    "state.json",
+]
+
+
+def ingest(concept_path: str, output_path: str) -> dict:
+    """Parse concept-dev JSON registries and validate artifact presence.
+
+    Args:
+        concept_path: Path to .concept-dev/ directory
+        output_path: Path to write ingestion.json output
+
+    Returns:
+        dict with keys: source_refs, assumption_refs, gate_status,
+        artifact_inventory, ingested_at
+    """
+    # Validate paths
+    resolved_concept = _validate_dir_path(concept_path)
+    _validate_path(output_path, allowed_extensions=[".json"])
+
+    now = datetime.now(timezone.utc).isoformat()
+
+    # Check if concept_path exists; if not, return fallback dict
+    if not os.path.isdir(resolved_concept):
+        fallback = {
+            "ingested_at": now,
+            "concept_path": None,
+            "source_refs": [],
+            "assumption_refs": [],
+            "gate_status": {
+                "all_passed": False,
+                "gates": {},
+                "warnings": ["No .concept-dev/ directory found"],
+            },
+            "artifact_inventory": {},
+        }
+        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
+        _atomic_write(output_path, fallback)
+        return fallback
+
+    # Build artifact_inventory
+    artifact_inventory = {}
+    for artifact in EXPECTED_ARTIFACTS:
+        artifact_inventory[artifact] = os.path.isfile(
+            os.path.join(resolved_concept, artifact)
+        )
+
+    # Parse source_registry.json
+    source_refs = []
+    source_path = os.path.join(resolved_concept, "source_registry.json")
+    if os.path.isfile(source_path):
+        with open(source_path) as f:
+            source_data = json.load(f)
+        source_refs = source_data.get("sources", [])
+
+    # Parse assumption_registry.json
+    assumption_refs = []
+    assumption_path = os.path.join(resolved_concept, "assumption_registry.json")
+    if os.path.isfile(assumption_path):
+        with open(assumption_path) as f:
+            assumption_data = json.load(f)
+        assumption_refs = assumption_data.get("assumptions", [])
+
+    # Parse state.json for gate status
+    gate_status = {"all_passed": False, "gates": {}, "warnings": []}
+    state_path = os.path.join(resolved_concept, "state.json")
+    if os.path.isfile(state_path):
+        with open(state_path) as f:
+            state_data = json.load(f)
+        gates = state_data.get("gates", {})
+        gate_status["gates"] = gates
+        failed = [name for name, passed in gates.items() if not passed]
+        if failed:
+            gate_status["all_passed"] = False
+            for name in failed:
+                gate_status["warnings"].append(f"Gate '{name}' not passed")
+        else:
+            gate_status["all_passed"] = True
+    else:
+        gate_status["warnings"].append("No state.json found in concept-dev directory")
+
+    result = {
+        "ingested_at": now,
+        "concept_path": resolved_concept,
+        "source_refs": source_refs,
+        "assumption_refs": assumption_refs,
+        "gate_status": gate_status,
+        "artifact_inventory": artifact_inventory,
+    }
+
+    # Write output
+    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
+    _atomic_write(output_path, result)
+
+    return result
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(
+        description="Ingest concept-dev artifacts for requirements development"
+    )
+    parser.add_argument(
+        "--concept-dir", required=True, help="Path to .concept-dev/ directory"
+    )
+    parser.add_argument(
+        "--output", required=True, help="Path to write ingestion.json"
+    )
+    args = parser.parse_args()
+
+    result = ingest(args.concept_dir, args.output)
+    print(json.dumps(result, indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/test_ingest_concept.py b/skills/requirements-dev/tests/test_ingest_concept.py
new file mode 100644
index 0000000..e803bb1
--- /dev/null
+++ b/skills/requirements-dev/tests/test_ingest_concept.py
@@ -0,0 +1,146 @@
+"""Tests for ingest_concept.py -- concept-dev artifact ingestion."""
+import json
+
+import pytest
+
+from ingest_concept import ingest
+
+
+@pytest.fixture
+def concept_dev_dir(tmp_path):
+    """Create a mock .concept-dev/ directory with valid artifacts."""
+    cd = tmp_path / ".concept-dev"
+    cd.mkdir()
+
+    # state.json with all gates passed
+    state = {
+        "session": {"id": "test-abc"},
+        "current_phase": "complete",
+        "gates": {"problem": True, "concept": True, "architecture": True, "landscape": True},
+    }
+    (cd / "state.json").write_text(json.dumps(state))
+
+    # source_registry.json
+    sources = {
+        "schema_version": "1.0.0",
+        "sources": [{"id": "SRC-001", "title": "Test Source", "type": "document"}],
+    }
+    (cd / "source_registry.json").write_text(json.dumps(sources))
+
+    # assumption_registry.json
+    assumptions = {
+        "schema_version": "1.0.0",
+        "assumptions": [
+            {"id": "ASN-001", "statement": "Test assumption", "status": "approved"}
+        ],
+    }
+    (cd / "assumption_registry.json").write_text(json.dumps(assumptions))
+
+    # Markdown artifacts (presence checked, not parsed by script)
+    (cd / "CONCEPT-DOCUMENT.md").write_text("# Concept Document\n")
+    (cd / "BLACKBOX.md").write_text("# Blackbox\n")
+
+    return tmp_path
+
+
+def test_ingest_valid_directory_returns_source_refs(concept_dev_dir, tmp_path):
+    """ingest() with valid concept-dev directory returns source_refs."""
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert len(result["source_refs"]) == 1
+    assert result["source_refs"][0]["id"] == "SRC-001"
+
+
+def test_ingest_valid_directory_returns_assumption_refs(concept_dev_dir, tmp_path):
+    """ingest() with valid concept-dev directory returns assumption_refs."""
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert len(result["assumption_refs"]) == 1
+    assert result["assumption_refs"][0]["id"] == "ASN-001"
+
+
+def test_ingest_reports_correct_gate_status(concept_dev_dir, tmp_path):
+    """ingest() with all gates passed reports correct gate_status."""
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert result["gate_status"]["all_passed"] is True
+    assert result["gate_status"]["warnings"] == []
+
+
+def test_ingest_missing_source_registry(concept_dev_dir, tmp_path):
+    """ingest() with missing source_registry.json returns empty source_refs."""
+    (concept_dev_dir / ".concept-dev" / "source_registry.json").unlink()
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert result["source_refs"] == []
+
+
+def test_ingest_missing_assumption_registry(concept_dev_dir, tmp_path):
+    """ingest() with missing assumption_registry.json returns empty assumption_refs."""
+    (concept_dev_dir / ".concept-dev" / "assumption_registry.json").unlink()
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert result["assumption_refs"] == []
+
+
+def test_ingest_failed_gates_reports_warnings(concept_dev_dir, tmp_path):
+    """ingest() with failed gates includes warnings in gate_status."""
+    state_path = concept_dev_dir / ".concept-dev" / "state.json"
+    state = json.loads(state_path.read_text())
+    state["gates"]["architecture"] = False
+    state_path.write_text(json.dumps(state))
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert result["gate_status"]["all_passed"] is False
+    assert any("architecture" in w for w in result["gate_status"]["warnings"])
+
+
+def test_ingest_missing_concept_dev_returns_fallback(tmp_path):
+    """ingest() with no .concept-dev/ returns graceful fallback dict."""
+    nonexistent = str(tmp_path / "does-not-exist")
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(nonexistent, str(output))
+    assert result["source_refs"] == []
+    assert result["assumption_refs"] == []
+    assert result["gate_status"]["all_passed"] is False
+    assert len(result["gate_status"]["warnings"]) > 0
+    assert result["artifact_inventory"] == {}
+
+
+def test_ingest_validates_path_rejects_traversal(tmp_path):
+    """ingest() rejects paths containing '..' traversal."""
+    bad_path = str(tmp_path / ".." / "escape")
+    output = str(tmp_path / "ingestion.json")
+    with pytest.raises(SystemExit):
+        ingest(bad_path, output)
+
+
+def test_ingest_output_contains_artifact_inventory(concept_dev_dir, tmp_path):
+    """ingest() output includes artifact_inventory listing which files exist."""
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    inv = result["artifact_inventory"]
+    assert inv["CONCEPT-DOCUMENT.md"] is True
+    assert inv["BLACKBOX.md"] is True
+    assert inv["SOLUTION-LANDSCAPE.md"] is False
+    assert inv["source_registry.json"] is True
+    assert inv["assumption_registry.json"] is True
+    assert inv["state.json"] is True
+
+
+def test_ingest_writes_output_file(concept_dev_dir, tmp_path):
+    """ingest() writes the result to the specified output path."""
+    output = tmp_path / "out" / "ingestion.json"
+    output.parent.mkdir(parents=True, exist_ok=True)
+    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
+    assert output.exists()
+    written = json.loads(output.read_text())
+    assert written["source_refs"] == result["source_refs"]
