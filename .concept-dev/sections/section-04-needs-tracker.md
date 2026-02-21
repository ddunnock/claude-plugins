Now I have all the context needed. Let me generate the section content.

# Section 04: Needs Tracker

## Overview

This section implements `needs_tracker.py`, the script responsible for managing stakeholder needs throughout the requirements development lifecycle. It also covers the `/reqdev:needs` command prompt that orchestrates needs formalization with the user.

The needs tracker provides subcommands to add, update, defer, reject, list, query, and export needs. Each need follows the INCOSE pattern: `[Stakeholder] needs [capability] [qualifier]`. Needs are stored in `needs_registry.json` with sequential NEED-xxx IDs, atomic writes, and automatic count synchronization to `state.json`.

## Dependencies

- **Section 01 (Plugin Scaffolding):** Plugin directory structure must exist, including `skills/requirements-dev/scripts/` and `skills/requirements-dev/commands/`.
- **Section 02 (State Management):** `init_session.py` and `update_state.py` must be implemented. The needs tracker reads and writes `state.json` for count synchronization. The `.requirements-dev/` workspace must be initialized before the needs tracker can operate.

## Files to Create

| File | Purpose |
|------|---------|
| `skills/requirements-dev/scripts/needs_tracker.py` | Core needs management script with CLI |
| `skills/requirements-dev/commands/reqdev.needs.md` | Command prompt for needs formalization |
| `skills/requirements-dev/tests/test_needs_tracker.py` | Unit tests |

## Tests

Write tests first in `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_needs_tracker.py`.

Tests require a `conftest.py` fixture (from section 02) that provides a temporary `.requirements-dev/` workspace with an initialized `state.json`. If not yet available, create a minimal fixture for this section's tests.

```python
# Test: add creates NEED-001 with correct fields (statement, stakeholder, source_block)
# Test: add auto-increments ID (NEED-001, NEED-002, NEED-003)
# Test: add validates uniqueness (same statement + stakeholder rejected)
# Test: add syncs needs_total count to state.json
# Test: update modifies statement and preserves other fields
# Test: defer sets status="deferred" and requires rationale
# Test: defer without rationale raises error
# Test: reject sets status="rejected" and requires rationale
# Test: list returns all needs for a given block
# Test: list with status filter returns only matching needs
# Test: query by concept_dev_refs returns needs linked to specific SRC-xxx
# Test: export produces correct JSON structure
# Test: atomic write: registry not corrupted if write is interrupted (temp file exists)
# Test: schema_version field present in registry output
```

Each test should set up a temporary workspace directory with an initialized `state.json` (matching the template from section 02), invoke needs_tracker functions or CLI subcommands, and verify the resulting `needs_registry.json` and `state.json` contents.

For the atomic write test, verify that the script writes to a temporary file first, then renames it. You can check this by mocking `os.rename` or by verifying that if the process is interrupted mid-write, the original registry file remains intact.

For the CLI tests, invoke the script via `subprocess.run` or by calling the main entry point directly, passing subcommand arguments, and checking stdout/exit codes.

## Implementation Details

### Need Dataclass

```python
@dataclass
class Need:
    id: str           # NEED-001 format
    statement: str
    stakeholder: str
    source_block: str
    source_artifacts: list[str]
    concept_dev_refs: dict  # {"sources": ["SRC-xxx"], "assumptions": ["ASN-xxx"]}
    status: str       # approved, deferred, rejected
    rationale: str | None
    registered_at: str
```

### Script: `needs_tracker.py`

File path: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/needs_tracker.py`

The script is both a CLI tool and an importable module. It operates on the `needs_registry.json` file inside the `.requirements-dev/` workspace.

**CLI subcommands via argparse:**

- `add` -- Create a new need. Required args: `--statement`, `--stakeholder`, `--source-block`. Optional: `--source-artifacts` (comma-separated), `--concept-dev-refs` (JSON string). Assigns next sequential ID (NEED-001, NEED-002, etc.). Sets `status` to `"approved"` by default. Sets `registered_at` to ISO timestamp. Validates uniqueness: rejects if an existing need has the same statement AND stakeholder (case-insensitive comparison). After writing the registry, syncs `needs_total` and `needs_approved` counts in `state.json`.

- `update` -- Modify an existing need. Required: `--id`. Optional: `--statement`, `--stakeholder`, any other field. Preserves all fields not explicitly updated. Updates `registered_at` to current timestamp if statement changes.

- `defer` -- Set need status to "deferred". Required: `--id`, `--rationale`. Raises error if `--rationale` is not provided. Updates `needs_approved` and `needs_deferred` counts in `state.json`.

- `reject` -- Set need status to "rejected". Required: `--id`, `--rationale`. Same rationale requirement as defer. Updates counts in `state.json`.

- `list` -- List needs. Optional filters: `--block` (source_block), `--status` (approved/deferred/rejected). Output: JSON array to stdout.

- `query` -- Query needs by cross-references. `--source-ref SRC-xxx` returns needs linked to that source. `--assumption-ref ASN-xxx` returns needs linked to that assumption. Output: JSON array to stdout.

- `export` -- Export the full registry to stdout as formatted JSON.

**Module interface (for use by other scripts and agents):**

```python
def add_need(workspace: str, statement: str, stakeholder: str, source_block: str,
             source_artifacts: list[str] = None, concept_dev_refs: dict = None) -> str:
    """Add a need to the registry. Returns the assigned ID (e.g., 'NEED-001')."""

def update_need(workspace: str, need_id: str, **fields) -> None:
    """Update fields on an existing need."""

def defer_need(workspace: str, need_id: str, rationale: str) -> None:
    """Set need status to deferred with rationale."""

def reject_need(workspace: str, need_id: str, rationale: str) -> None:
    """Set need status to rejected with rationale."""

def list_needs(workspace: str, block: str = None, status: str = None) -> list[dict]:
    """List needs with optional filters."""

def query_needs(workspace: str, source_ref: str = None, assumption_ref: str = None) -> list[dict]:
    """Query needs by concept-dev cross-references."""

def export_needs(workspace: str) -> dict:
    """Export full registry as dict."""
```

**Registry file format (`needs_registry.json`):**

```json
{
  "schema_version": "1.0.0",
  "needs": [
    {
      "id": "NEED-001",
      "statement": "The operator needs to monitor pipeline health in real-time",
      "stakeholder": "Pipeline Operator",
      "source_block": "monitoring-dashboard",
      "source_artifacts": ["CONCEPT-DOCUMENT.md"],
      "concept_dev_refs": {
        "sources": ["SRC-003"],
        "assumptions": ["ASN-001"]
      },
      "status": "approved",
      "rationale": null,
      "registered_at": "2026-02-20T10:30:00Z"
    }
  ]
}
```

**ID generation:** Read the current registry, find the highest existing NEED-xxx number, increment by 1, zero-pad to 3 digits. If the registry is empty, start at NEED-001.

**Atomic writes:** All mutations to `needs_registry.json` must use the temp-file-then-rename pattern:
1. Write to a temporary file in the same directory (e.g., `needs_registry.json.tmp`)
2. Call `os.replace()` (atomic on POSIX) to rename the temp file to the actual file
3. This ensures that a crash mid-write leaves the original file intact

**Count synchronization:** After any mutation that changes need counts (add, defer, reject), read the registry and update `state.json` counts:
- `needs_total`: total number of needs in registry
- `needs_approved`: count where status == "approved"
- `needs_deferred`: count where status == "deferred"

This sync can call `update_state.py` via subprocess or directly import its update function (prefer direct import for reliability).

**Path validation:** Apply `_validate_path()` on the workspace argument. Reject paths containing `..`. This follows the established codebase security pattern.

**Error handling:** Use `sys.exit(1)` with descriptive error messages for invalid input. Return exit code 0 on success with JSON output to stdout.

### Command Prompt: `/reqdev:needs`

File path: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.needs.md`

This is a markdown command prompt that instructs Claude on the needs formalization procedure. It is not a Python script. The command prompt should contain the following procedural instructions for the LLM:

1. **Gate check:** Verify the `init` gate is passed in `state.json` before proceeding. If not, instruct the user to run `/reqdev:init` first.

2. **Per-block iteration:** For each block defined in `state.json`:
   a. Present needs candidates extracted during ingestion (from `ingestion.json` if concept-dev was available) or prompt for manual entry.
   b. For each candidate, formalize into INCOSE pattern: `[Stakeholder] needs [capability] [qualifier]`.
   c. Validate the need is solution-free: needs express expectations ("should"), not obligations ("shall") and not solutions.
   d. Present a batch of 3-5 formalized needs for user review.
   e. For each need, the user can: approve, edit, defer (with rationale), or reject.
   f. Register approved needs using `needs_tracker.py add`.
   g. Deferred/rejected needs are recorded using `needs_tracker.py defer` or `reject`.

3. **Gate completion:** After all blocks have been processed and the user approves the complete needs set, pass the `needs` gate via `update_state.py pass-gate needs`.

4. **Manual mode:** If no ingestion data is available, prompt the user to describe stakeholder needs for each block. Guide them through the INCOSE formalization pattern. Present examples of well-formed need statements.

The command prompt should reference `scripts/needs_tracker.py` for all registry operations and `scripts/update_state.py` for state management. It should instruct the LLM to run these scripts via bash tool calls.

### INCOSE Need Pattern Reference

Include this guidance in the command prompt so the LLM can formalize needs correctly:

- **Pattern:** `[Stakeholder] needs [capability] [optional qualifier]`
- **Use "should"** for expectations, not "shall" (which is for requirements)
- **Solution-free:** Describe what is needed, not how to achieve it
- **Examples:**
  - Good: "The operator needs to monitor system health metrics in real-time"
  - Bad: "The operator needs a Grafana dashboard" (prescribes solution)
  - Bad: "The system shall display metrics" (uses obligation language -- this is a requirement, not a need)

## Security Considerations

- Apply `_validate_path()` to the workspace directory argument, rejecting `..` traversal
- Use `os.path.realpath()` to resolve paths before file operations (matching codebase pattern from recent security fixes)
- Atomic writes via temp-file-then-rename for all registry mutations
- All user-provided text (need statements) treated as data, never interpreted as instructions

---

## Implementation Notes (Actual)

### Files Created/Modified
- `skills/requirements-dev/scripts/needs_tracker.py` -- Full implementation with 7 subcommands and module API
- `skills/requirements-dev/commands/reqdev.needs.md` -- 6-step command prompt for `/reqdev:needs`
- `skills/requirements-dev/tests/test_needs_tracker.py` -- 13 tests

### Deviations from Plan
- **Protected fields:** Added `_PROTECTED_FIELDS` guard on `update_need()` to prevent overwriting `id`, `status`, `registered_at` (not in plan, from code review)
- **Resolved paths:** All public functions capture `_validate_dir_path` return value (security fix from code review)
- **CLI None check:** CLI update handler uses `is not None` instead of truthiness (from code review)

### Test Count: 13 tests, all passing
### Total test count across project: 42 tests, all passing