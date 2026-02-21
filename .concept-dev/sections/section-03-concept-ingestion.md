Now I have all the context needed. Let me generate the section content.

# Section 03: Concept Ingestion

## Overview

This section covers the concept ingestion pipeline: `ingest_concept.py` (JSON registry parsing), `check_tools.py` (research tool availability detection), and the `/reqdev:init` command prompt (LLM-assisted extraction from concept-dev markdown artifacts plus manual mode fallback).

**Dependencies:** Section 02 (State Management) must be complete -- `init_session.py` and `update_state.py` are prerequisites. The `state.json` template from Section 01 (Plugin Scaffolding) must exist.

**Blocks:** Section 07 (Requirements Command) depends on this section's output (`ingestion.json`).

---

## Files to Create

| File | Purpose |
|------|---------|
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/ingest_concept.py` | Parse concept-dev JSON registries, validate gates, produce ingestion summary |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/check_tools.py` | Detect available research tools (WebSearch, crawl4ai, MCP servers) |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.init.md` | Command prompt for `/reqdev:init` |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_ingest_concept.py` | Tests for ingest_concept.py |

---

## Tests (implement first)

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_ingest_concept.py`**

```python
# Test: ingest() with valid concept-dev directory returns source_refs and assumption_refs
# Test: ingest() with valid directory reports correct gate_status (all gates passed)
# Test: ingest() with missing source_registry.json returns empty source_refs, no error
# Test: ingest() with missing assumption_registry.json returns empty assumption_refs, no error
# Test: ingest() with state.json showing failed gates reports gate_status warnings
# Test: ingest() with completely missing .concept-dev/ returns graceful fallback dict
# Test: ingest() validates path (rejects .. traversal)
# Test: ingest() output JSON contains artifact_inventory listing which files exist
```

Test structure and fixtures:

```python
import pytest
import json
import os
from pathlib import Path

@pytest.fixture
def concept_dev_dir(tmp_path):
    """Create a mock .concept-dev/ directory with valid artifacts."""
    cd = tmp_path / ".concept-dev"
    cd.mkdir()

    # state.json with all gates passed
    state = {
        "session": {"id": "test-abc"},
        "current_phase": "complete",
        "gates": {"problem": True, "concept": True, "architecture": True, "landscape": True}
    }
    (cd / "state.json").write_text(json.dumps(state))

    # source_registry.json
    sources = {
        "schema_version": "1.0.0",
        "sources": [
            {"id": "SRC-001", "title": "Test Source", "type": "document"}
        ]
    }
    (cd / "source_registry.json").write_text(json.dumps(sources))

    # assumption_registry.json
    assumptions = {
        "schema_version": "1.0.0",
        "assumptions": [
            {"id": "ASN-001", "statement": "Test assumption", "status": "approved"}
        ]
    }
    (cd / "assumption_registry.json").write_text(json.dumps(assumptions))

    # Markdown artifacts (presence checked, not parsed by script)
    (cd / "CONCEPT-DOCUMENT.md").write_text("# Concept Document\n")
    (cd / "BLACKBOX.md").write_text("# Blackbox\n")

    return tmp_path


def test_ingest_valid_directory_returns_source_refs(concept_dev_dir):
    """ingest() with valid concept-dev directory returns source_refs."""
    # Call ingest() with concept_dev_dir, assert source_refs contains SRC-001

def test_ingest_valid_directory_returns_assumption_refs(concept_dev_dir):
    """ingest() with valid concept-dev directory returns assumption_refs."""
    # Assert assumption_refs contains ASN-001

def test_ingest_reports_correct_gate_status(concept_dev_dir):
    """ingest() with all gates passed reports correct gate_status."""
    # Assert gate_status shows all gates passed, no warnings

def test_ingest_missing_source_registry(concept_dev_dir):
    """ingest() with missing source_registry.json returns empty source_refs."""
    (concept_dev_dir / ".concept-dev" / "source_registry.json").unlink()
    # Call ingest(), assert source_refs is empty list, no exception raised

def test_ingest_missing_assumption_registry(concept_dev_dir):
    """ingest() with missing assumption_registry.json returns empty assumption_refs."""
    (concept_dev_dir / ".concept-dev" / "assumption_registry.json").unlink()
    # Call ingest(), assert assumption_refs is empty list, no exception raised

def test_ingest_failed_gates_reports_warnings(concept_dev_dir):
    """ingest() with failed gates includes warnings in gate_status."""
    state_path = concept_dev_dir / ".concept-dev" / "state.json"
    state = json.loads(state_path.read_text())
    state["gates"]["architecture"] = False
    state_path.write_text(json.dumps(state))
    # Call ingest(), assert gate_status contains warning about architecture gate

def test_ingest_missing_concept_dev_returns_fallback(tmp_path):
    """ingest() with no .concept-dev/ returns graceful fallback dict."""
    # Call ingest() with tmp_path (no .concept-dev), assert returns dict with
    # empty source_refs, empty assumption_refs, gate_status indicating not found,
    # artifact_inventory showing no files

def test_ingest_validates_path_rejects_traversal(tmp_path):
    """ingest() rejects paths containing '..' traversal."""
    # Call ingest() with path containing "..", assert raises SystemExit or ValueError

def test_ingest_output_contains_artifact_inventory(concept_dev_dir):
    """ingest() output includes artifact_inventory listing which files exist."""
    # Call ingest(), assert artifact_inventory has entries for CONCEPT-DOCUMENT.md,
    # BLACKBOX.md, source_registry.json, etc. with boolean presence flags
```

---

## Implementation: `ingest_concept.py`

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/ingest_concept.py`**

### Purpose

Parse concept-dev JSON registries and validate artifact presence. This script handles only the deterministic, structured data (JSON files). Markdown extraction (blocks, capabilities, needs candidates) is handled by the `/reqdev:init` command prompt via LLM-assisted reading.

### Function Signature

```python
#!/usr/bin/env python3
"""
Ingest concept-dev artifacts for requirements development.

Parses JSON registries (source_registry.json, assumption_registry.json, state.json)
and validates artifact presence. Markdown extraction is LLM-assisted via the
/reqdev:init command prompt.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime


def _validate_path(filepath: str, allowed_extensions: set, label: str) -> str:
    """Validate file path: reject traversal and restrict extensions. Returns resolved path."""
    # Same pattern as concept-dev scripts: os.path.realpath, check for ".." in relpath,
    # validate extension

def _validate_dir_path(dirpath: str, label: str) -> str:
    """Validate directory path: reject traversal. Returns resolved path."""
    # Same pattern as concept-dev init_session.py


# Artifacts to check for presence
EXPECTED_ARTIFACTS = [
    "CONCEPT-DOCUMENT.md",
    "BLACKBOX.md",
    "SOLUTION-LANDSCAPE.md",
    "source_registry.json",
    "assumption_registry.json",
    "state.json",
]


def ingest(concept_path: str, output_path: str) -> dict:
    """Parse concept-dev JSON registries and validate artifact presence.

    Args:
        concept_path: Path to .concept-dev/ directory
        output_path: Path to write ingestion.json output

    Returns:
        dict with keys: source_refs, assumption_refs, gate_status,
        artifact_inventory, ingested_at
    """
    # 1. Check if concept_path exists; if not, return fallback dict
    # 2. Build artifact_inventory: for each EXPECTED_ARTIFACTS, check file exists
    # 3. Parse source_registry.json if present -> extract source list
    #    If missing, source_refs = []
    # 4. Parse assumption_registry.json if present -> extract assumption list
    #    If missing, assumption_refs = []
    # 5. Parse state.json if present -> check gate completion
    #    Build gate_status with warnings for any failed gates
    # 6. Assemble result dict
    # 7. Write to output_path as JSON
    # 8. Return result dict
```

### Output JSON Structure

The `ingest()` function writes `ingestion.json` to the output path with this structure:

```json
{
  "ingested_at": "2026-02-20T10:00:00",
  "concept_path": ".concept-dev/",
  "source_refs": [
    {"id": "SRC-001", "title": "...", "type": "..."}
  ],
  "assumption_refs": [
    {"id": "ASN-001", "statement": "...", "status": "approved"}
  ],
  "gate_status": {
    "all_passed": true,
    "gates": {"problem": true, "concept": true, "architecture": true, "landscape": true},
    "warnings": []
  },
  "artifact_inventory": {
    "CONCEPT-DOCUMENT.md": true,
    "BLACKBOX.md": true,
    "SOLUTION-LANDSCAPE.md": false,
    "source_registry.json": true,
    "assumption_registry.json": true,
    "state.json": true
  }
}
```

### CLI Interface

```bash
python3 ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json
```

The argparse setup should accept `--concept-dir` (required) and `--output` (required). Both paths must be validated: `--concept-dir` uses `_validate_dir_path`, `--output` uses `_validate_path` with `{'.json'}` extension.

### Fallback Behavior

When `.concept-dev/` does not exist, the function returns a fallback dict rather than raising an error:

```python
{
    "ingested_at": "...",
    "concept_path": None,
    "source_refs": [],
    "assumption_refs": [],
    "gate_status": {"all_passed": False, "gates": {}, "warnings": ["No .concept-dev/ directory found"]},
    "artifact_inventory": {}
}
```

This fallback enables manual mode in the `/reqdev:init` command prompt.

---

## Implementation: `check_tools.py`

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/check_tools.py`**

### Purpose

Detect available research tools for Phase 2 TPM research. This is adapted from the concept-dev version at `/Users/dunnock/projects/claude-plugins/skills/concept-dev/scripts/check_tools.py` with minimal changes.

### Adaptation Notes

The concept-dev `check_tools.py` (shown above) is the reference implementation. The requirements-dev version should:

1. Copy the same `TOOL_TIERS` dictionary, `detect_python_package()`, `check_tools()`, `print_report()`, and `_validate_path()` functions.
2. Update the final print message from "Run /concept:init" to "Run /reqdev:init".
3. When updating state.json, use the requirements-dev state structure. The concept-dev version writes to `state["tools"]` -- the requirements-dev state.json does not have a `tools` key in the template, so `check_tools()` should create it if absent:

```python
if "tools" not in state:
    state["tools"] = {}
state["tools"]["detected_at"] = report["detected_at"]
# ... rest of tool recording
```

4. Use atomic write (temp-file-then-rename) when updating state.json, consistent with the project convention.

No separate tests are specified for `check_tools.py` in this section -- it is a direct adaptation of the existing tested pattern. If needed, tests can be added as part of integration testing.

---

## Implementation: `/reqdev:init` Command Prompt

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.init.md`**

### Purpose

This command prompt orchestrates the full initialization flow. It is a markdown file that instructs Claude on what to do when the user invokes `/reqdev:init`.

### Command Flow

The command prompt should instruct Claude to perform these steps in order:

1. **Run `init_session.py`** to create the `.requirements-dev/` workspace and `state.json`. If workspace already exists, report existing session and offer to resume.

2. **Run `ingest_concept.py`** to parse concept-dev JSON registries. Check the returned `artifact_inventory` and `gate_status`.

3. **Branch on concept-dev availability:**

   **If concept-dev artifacts found (artifact_inventory shows CONCEPT-DOCUMENT.md and BLACKBOX.md exist):**
   - Read `BLACKBOX.md` and extract: block names, descriptions, block-to-block relationships, interfaces
   - Read `CONCEPT-DOCUMENT.md` and extract: capabilities per block, ConOps scenarios, stakeholder needs candidates
   - Read `SOLUTION-LANDSCAPE.md` if present for additional context
   - Write extracted data to `.requirements-dev/ingestion.json` (augmenting the file already created by `ingest_concept.py` with `blocks` and `needs_candidates` keys)
   - Present extraction summary table to user for confirmation

   **If concept-dev artifacts NOT found (manual mode):**
   - Inform user that no concept-dev artifacts were found
   - Guide user through manual block definition:
     - Ask user to name each functional block with a 1-2 sentence description
     - Ask for 3-5 capabilities per block
     - Ask to describe key interfaces between blocks
   - Present a summary table for user approval before proceeding
   - Write manual entries to `.requirements-dev/ingestion.json`

4. **Run `check_tools.py`** to detect research tool availability for Phase 2. Display available tools summary.

5. **Update state.json** via `update_state.py`:
   - Set phase to "init"
   - Pass the init gate
   - Record blocks in state.json `blocks` field

6. **Display summary:** blocks found/defined, needs candidates count, sources available, assumptions carried forward, research tools detected.

### LLM-Assisted Extraction Format

When reading markdown artifacts, the command prompt should specify the extraction output format:

```json
{
  "blocks": [
    {
      "name": "block-name",
      "description": "One-line description",
      "relationships": [{"target": "other-block", "type": "uses/provides/depends"}],
      "interfaces": ["interface description"],
      "capabilities": ["capability 1", "capability 2"]
    }
  ],
  "needs_candidates": [
    {
      "source_block": "block-name",
      "statement": "The user needs...",
      "source_artifact": "CONCEPT-DOCUMENT.md",
      "source_section": "Section heading where found"
    }
  ]
}
```

### Manual Mode Interaction Pattern

The manual mode fallback should follow a structured interaction to prevent improvisation drift across sessions:

1. Ask: "How many functional blocks does your system have?"
2. For each block, collect: name, description, 3-5 capabilities
3. After all blocks defined, ask about interfaces between blocks
4. Present complete summary table for approval
5. Only proceed after explicit user confirmation

### Key Prompt Content Notes

The command prompt should reference:
- `scripts/ingest_concept.py` for JSON registry parsing
- `scripts/init_session.py` for workspace creation
- `scripts/check_tools.py` for tool detection
- `scripts/update_state.py` for state mutations
- The state.json `blocks` field structure for recording discovered/defined blocks

The prompt should make clear that markdown parsing is done by Claude directly (reading files), not by Python scripts. The split is intentional: JSON parsing in scripts (deterministic, testable), markdown extraction by LLM (adaptive to format variations).

---

## Integration Notes

### How This Section Connects to Others

- **From Section 02 (State Management):** Uses `init_session.py` to create workspace and `update_state.py` to record init phase completion and block definitions.
- **To Section 07 (Requirements Command):** The `ingestion.json` file produced here is the input for the requirements development workflow. It provides the block list, needs candidates, and cross-references to concept-dev sources and assumptions.
- **To Section 04 (Needs Tracker):** Needs candidates extracted here are formalized during `/reqdev:needs`.
- **To Section 11 (TPM Research):** `check_tools.py` output stored in state.json is used by the TPM researcher agent to adapt its research strategy.

### Security Patterns

Following established codebase conventions (see concept-dev `init_session.py` and `check_tools.py`):

- `_validate_path()` on all file path CLI arguments -- reject `..` traversal, restrict to expected extensions
- `_validate_dir_path()` on directory path arguments
- `os.path.realpath()` to resolve paths before use
- Atomic writes (temp-file-then-rename) when writing JSON output

---

## Implementation Notes (Actual)

### Files Created/Modified
- `skills/requirements-dev/scripts/ingest_concept.py` -- Full implementation with `ingest()` function and CLI
- `skills/requirements-dev/scripts/check_tools.py` -- Adapted from concept-dev version with atomic writes and UTC timestamps
- `skills/requirements-dev/commands/reqdev.init.md` -- Complete command prompt with 6-step flow
- `skills/requirements-dev/tests/test_ingest_concept.py` -- 10 tests (9 from plan + 1 output file test)

### Deviations from Plan
- **Shared imports:** Plan showed `_validate_path` and `_validate_dir_path` defined locally in `ingest_concept.py`. Implementation imports from `shared_io.py` (DRY).
- **Relative concept_path:** Plan's example output showed relative path. Implementation initially used resolved absolute; changed to original input path per code review.
- **JSON error handling:** Added try/except around `json.load()` calls for concept-dev files (not in original plan). These files come from a different plugin and may be malformed.
- **UTC timestamps:** `check_tools.py` updated to use `datetime.now(timezone.utc)` instead of `datetime.now()` from concept-dev version, for consistency with `ingest_concept.py` and `init_session.py`.

### Test Count: 10 tests, all passing
### Total test count across project: 29 tests, all passing