Now I have all the context. Let me generate the section content.

# Section 02: State Management

## Overview

This section implements the two core state management scripts for the requirements-dev plugin: `init_session.py` (workspace creation and state initialization) and `update_state.py` (state mutation operations). These scripts are the foundation for all subsequent sections -- every tracker, command, and engine depends on state.json existing and being correctly maintained.

**Dependencies:** Section 01 (plugin scaffolding) must be complete. Specifically, the `templates/state.json` template file and the `.requirements-dev/` workspace convention must exist.

**Blocks:** Sections 03 (concept ingestion), 04 (needs tracker), 05 (quality checker), and 08 (status/resume) all depend on this section.

## File Locations

All files are relative to the plugin root `skills/requirements-dev/`:

- `scripts/init_session.py` -- workspace initialization script
- `scripts/update_state.py` -- state mutation script
- `tests/test_init_session.py` -- tests for init_session
- `tests/test_update_state.py` -- tests for update_state
- `templates/state.json` -- state template (created in section-01, referenced here)

## Tests First

### `skills/requirements-dev/tests/test_init_session.py`

```python
"""Tests for init_session.py workspace initialization."""
import json
import os
import pytest

# Test: init creates .requirements-dev/ directory
def test_init_creates_workspace_directory(tmp_path):
    """Calling init with a project path creates .requirements-dev/ under that path."""

# Test: init creates state.json from template with session_id and schema_version
def test_init_creates_state_json_from_template(tmp_path):
    """state.json is created with a non-empty session_id and schema_version '1.0.0'."""

# Test: init state.json has correct initial counts (all zeros)
def test_init_state_has_zero_counts(tmp_path):
    """All count fields in the initialized state.json must be zero."""

# Test: init state.json has correct initial progress (current_block=null, current_type_pass=null)
def test_init_state_has_null_progress(tmp_path):
    """progress.current_block and progress.current_type_pass must be null on init."""

# Test: init with existing .requirements-dev/ does not overwrite (resume scenario)
def test_init_does_not_overwrite_existing_workspace(tmp_path):
    """If .requirements-dev/ already exists with a state.json, init must not overwrite it.
    This supports the resume scenario where a user re-runs init after interruption."""

# Test: init validates path argument
def test_init_validates_path_rejects_traversal(tmp_path):
    """Path arguments containing '..' must be rejected for security."""
```

### `skills/requirements-dev/tests/test_update_state.py`

```python
"""Tests for update_state.py state mutation operations."""
import json
import os
import pytest

# Test: set-phase updates current_phase
def test_set_phase_updates_current_phase(tmp_path):
    """set-phase 'needs' should change current_phase from 'init' to 'needs'."""

# Test: pass-gate sets gate to true
def test_pass_gate_sets_gate_true(tmp_path):
    """pass-gate 'init' should set gates.init to true."""

# Test: pass-gate on already-passed gate is idempotent
def test_pass_gate_idempotent(tmp_path):
    """Passing a gate that is already true should not error or change anything."""

# Test: check-gate returns 0 when gate passed, 1 when not
def test_check_gate_returns_correct_exit_code(tmp_path):
    """check-gate should return exit code 0 for passed gates, 1 for unpassed gates."""

# Test: set-artifact stores path under artifacts
def test_set_artifact_stores_path(tmp_path):
    """set-artifact 'deliver' 'REQUIREMENTS-SPECIFICATION.md' should store the path
    in state.artifacts under the phase key."""

# Test: update with dotted path (e.g., "counts.needs_total") updates nested field
def test_update_dotted_path(tmp_path):
    """update 'counts.needs_total' '5' should set state['counts']['needs_total'] to 5."""

# Test: sync-counts reads registries and updates all count fields
def test_sync_counts_from_registries(tmp_path):
    """sync-counts should read needs_registry.json and requirements_registry.json,
    count entries by status, and update all count fields in state.json."""

# Test: show returns human-readable summary
def test_show_returns_summary(tmp_path, capsys):
    """show should print current phase, gate status, and counts."""

# Test: atomic write on all mutations
def test_atomic_write_uses_temp_file(tmp_path, monkeypatch):
    """All state mutations must write to a temp file first, then rename.
    This prevents corruption if the process is interrupted mid-write."""
```

## Implementation Details

### `init_session.py`

**Purpose:** Create the `.requirements-dev/` workspace directory and initialize `state.json` from the template. Generate a unique session ID. Follow the same pattern as concept-dev's init_session.py.

**Script interface:**

```python
"""Initialize requirements-dev workspace.

Usage: python3 init_session.py <project_path>

Creates .requirements-dev/ directory under project_path with an initialized
state.json. If workspace already exists, prints a message and exits without
overwriting (supports resume).
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile


WORKSPACE_DIR = ".requirements-dev"
TEMPLATE_FILENAME = "state.json"


def _validate_path(path: str, allowed_extensions: list[str] | None = None) -> str:
    """Validate and resolve a path argument. Reject '..' traversal.
    Returns os.path.realpath() resolved path."""

def _validate_dir_path(path: str) -> str:
    """Validate and resolve a directory path argument. Reject '..' traversal.
    Returns os.path.realpath() resolved path."""

def _get_template_path() -> str:
    """Return absolute path to templates/state.json relative to this script's location."""

def _atomic_write(filepath: str, data: dict) -> None:
    """Write JSON data atomically using temp-file-then-rename pattern."""

def init_workspace(project_path: str) -> dict:
    """Create workspace and initialize state.json.

    1. Resolve and validate project_path
    2. Check if .requirements-dev/ already exists
       - If state.json exists: print resume message, return existing state
       - If dir exists but no state.json: proceed with init
    3. Create .requirements-dev/ directory
    4. Read templates/state.json
    5. Populate: session_id (uuid4), created_at (ISO 8601 UTC), schema_version
    6. Write state.json atomically
    7. Return initialized state dict
    """

def main():
    """CLI entry point. Parse args, call init_workspace, print summary."""
```

**Key behaviors:**

- Session ID is generated via `uuid.uuid4().hex` (32 hex chars, no dashes)
- `created_at` uses ISO 8601 format with UTC timezone: `datetime.now(timezone.utc).isoformat()`
- The template path is resolved relative to the script file location using `__file__`, navigating to `../templates/state.json`
- Resume detection: if `state.json` already exists in the workspace, print "Workspace already initialized (session: {id}). Use /reqdev:resume to continue." and return the existing state without modification
- All path arguments pass through `_validate_dir_path()` which calls `os.path.realpath()` and rejects paths containing `..`

### `update_state.py`

**Purpose:** Provide all state mutation operations as CLI subcommands. Used by commands, hooks, and tracker scripts to modify state.json consistently with atomic writes.

**Script interface:**

```python
"""Update requirements-dev session state.

Usage:
    python3 update_state.py set-phase <phase>
    python3 update_state.py pass-gate <phase>
    python3 update_state.py check-gate <phase>
    python3 update_state.py set-artifact <phase> <path>
    python3 update_state.py update <dotted.path> <value>
    python3 update_state.py sync-counts
    python3 update_state.py show

All mutations use atomic write (temp-file-then-rename).
"""
import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


WORKSPACE_DIR = ".requirements-dev"
STATE_FILENAME = "state.json"


def _validate_path(path: str, allowed_extensions: list[str] | None = None) -> str:
    """Validate and resolve a path argument."""

def _atomic_write(filepath: str, data: dict) -> None:
    """Write JSON data atomically using temp-file-then-rename pattern.

    1. Create NamedTemporaryFile in same directory as target (same filesystem for rename)
    2. Write JSON with indent=2
    3. Flush and fsync
    4. os.rename(temp, target) -- atomic on POSIX
    """

def _load_state(workspace_path: str) -> dict:
    """Load state.json from workspace. Raise FileNotFoundError if missing."""

def _save_state(workspace_path: str, state: dict) -> None:
    """Save state.json atomically."""

def set_phase(workspace_path: str, phase: str) -> None:
    """Set current_phase to the given phase name.
    Valid phases: init, needs, requirements, validate, deliver, decompose."""

def pass_gate(workspace_path: str, phase: str) -> None:
    """Mark a phase gate as passed (set gates.<phase> to true).
    Idempotent -- passing an already-passed gate is a no-op."""

def check_gate(workspace_path: str, phase: str) -> bool:
    """Check if a phase gate has been passed. Returns True/False.
    CLI: exits with code 0 if passed, 1 if not."""

def set_artifact(workspace_path: str, phase: str, artifact_path: str) -> None:
    """Record a deliverable artifact path under artifacts.<phase>."""

def update_field(workspace_path: str, dotted_path: str, value: str) -> None:
    """Update a nested field using dot notation.

    Example: update_field(ws, "counts.needs_total", "5")

    The value string is parsed as: int if all digits, float if contains '.',
    bool if 'true'/'false', null if 'null', otherwise kept as string.
    Dotted path is split on '.' and traversed to set the nested value.
    """

def sync_counts(workspace_path: str) -> None:
    """Read needs_registry.json and requirements_registry.json from workspace.
    Count entries by status and update all count fields in state.json.

    Counts computed:
    - needs_total: total entries in needs registry
    - needs_approved: entries with status 'approved'
    - needs_deferred: entries with status 'deferred'
    - requirements_total: total entries in requirements registry
    - requirements_registered: entries with status 'registered'
    - requirements_baselined: entries with status 'baselined'
    - requirements_withdrawn: entries with status 'withdrawn'
    - tbd_open: requirements with non-null tbd_tbr having unresolved TBD
    - tbr_open: requirements with non-null tbd_tbr having unresolved TBR

    Missing registry files are treated as empty (counts = 0).
    """

def show(workspace_path: str) -> str:
    """Return a human-readable summary of current state.

    Includes: session_id, current_phase, gate status, counts,
    traceability coverage, current progress position.
    """

def main():
    """CLI entry point with argparse subcommands."""
```

**Key behaviors:**

- The `_atomic_write` function creates the temp file in the same directory as the target file to ensure the `os.rename` is atomic (same filesystem). Uses `NamedTemporaryFile(dir=target_dir, delete=False)` followed by `json.dump`, `flush`, `fsync`, and `os.rename`.
- The `update_field` function splits the dotted path on `.` and walks the state dict to set the leaf value. It coerces the value string to the appropriate Python type (int, float, bool, None, or string).
- The `sync_counts` function is critical for keeping state.json in sync with the actual registry contents. It is called by tracker scripts after mutations and by the hook script after artifact writes.
- The `show` function formats output for terminal display: phase, gates (checkmarks/crosses), counts table, and progress position.
- All subcommands that mutate state load the JSON, modify in memory, and save atomically. No partial writes.

### State Template Reference

The `templates/state.json` template (created in section-01) that `init_session.py` reads:

```json
{
  "session_id": "",
  "schema_version": "1.0.0",
  "created_at": "",
  "current_phase": "init",
  "gates": { "init": false, "needs": false, "requirements": false, "deliver": false },
  "blocks": {},
  "progress": {
    "current_block": null,
    "current_type_pass": null,
    "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
    "requirements_in_draft": []
  },
  "counts": {
    "needs_total": 0, "needs_approved": 0, "needs_deferred": 0,
    "requirements_total": 0, "requirements_registered": 0, "requirements_baselined": 0, "requirements_withdrawn": 0,
    "tbd_open": 0, "tbr_open": 0
  },
  "traceability": { "links_total": 0, "coverage_pct": 0.0 },
  "decomposition": { "levels": {}, "max_level": 3 },
  "artifacts": {}
}
```

The `progress` section enables granular resume: `current_block` and `current_type_pass` track exactly where the user left off within type-guided passes. `requirements_in_draft` holds requirement IDs that passed quality checking but were not yet registered when the session was interrupted -- these are presented for confirmation on resume rather than lost.

All registry JSON files include a `schema_version` field (initially "1.0.0"); `init_session.py` checks this on resume and logs a warning if the version is older than the current code expects, enabling future migrations.

## Security Requirements

Following established codebase patterns:

1. **Path validation:** `_validate_path()` and `_validate_dir_path()` on all CLI file arguments -- reject `..` traversal, call `os.path.realpath()` to resolve symlinks, restrict to expected extensions where applicable
2. **Atomic writes:** All state mutations use temp-file-then-rename via `_atomic_write()` to prevent corruption on interrupted writes
3. **No network calls:** Both scripts are purely local filesystem operations

## Test Fixtures

Create a shared `conftest.py` (or add to existing) with fixtures for state management tests:

```python
"""Shared fixtures for requirements-dev tests."""
import json
import os
import pytest


@pytest.fixture
def workspace(tmp_path):
    """Create a minimal .requirements-dev/ workspace with initialized state.json."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    state = {
        "session_id": "abc123",
        "schema_version": "1.0.0",
        "created_at": "2025-01-01T00:00:00+00:00",
        "current_phase": "init",
        "gates": {"init": False, "needs": False, "requirements": False, "deliver": False},
        "blocks": {},
        "progress": {
            "current_block": None,
            "current_type_pass": None,
            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
            "requirements_in_draft": []
        },
        "counts": {
            "needs_total": 0, "needs_approved": 0, "needs_deferred": 0,
            "requirements_total": 0, "requirements_registered": 0,
            "requirements_baselined": 0, "requirements_withdrawn": 0,
            "tbd_open": 0, "tbr_open": 0
        },
        "traceability": {"links_total": 0, "coverage_pct": 0.0},
        "decomposition": {"levels": {}, "max_level": 3},
        "artifacts": {}
    }
    (ws / "state.json").write_text(json.dumps(state, indent=2))
    return ws
```

The `workspace` fixture provides a pre-initialized workspace for `update_state.py` tests. The `init_session.py` tests use `tmp_path` directly (testing creation from scratch).

## Implementation Notes

**Files created/modified:**
- `scripts/shared_io.py` (NEW) -- Shared I/O utilities extracted during code review
- `scripts/init_session.py` -- Workspace initialization with schema version check on resume
- `scripts/update_state.py` -- State mutation operations with gate validation
- `tests/conftest.py` -- Updated with inline state dict fixture (renamed to `tmp_workspace`)
- `tests/test_init_session.py` -- 6 tests for init_session
- `tests/test_update_state.py` -- 13 tests for update_state (19 total)
- `pyproject.toml` (NEW) -- Added for uv/pytest support

**Deviations from plan:**
1. `_atomic_write`, `_validate_path`, and `_validate_dir_path` extracted to `scripts/shared_io.py` (per code review -- user chose DRY over self-contained). Both scripts import from it.
2. `pass_gate()` now raises `ValueError` for unknown gate names instead of silently ignoring.
3. `show()` includes traceability coverage line (was missing from initial implementation).
4. Path validation uses `Path.parts` instead of `str.split(os.sep)` for safer traversal detection.
5. CLI argparse for `pass-gate` and `check-gate` now constrain to `VALID_GATES` choices.

**Test count:** 19 tests (6 init + 13 update), all passing.