Now I have all the context. Let me generate the section content.

# Section 06: Requirements Engine

## Overview

This section implements the core requirements tracking and traceability infrastructure: `requirement_tracker.py`, `traceability.py`, and `source_tracker.py`. These scripts manage requirement lifecycle (draft, registered, baselined, withdrawn), bidirectional traceability links between needs, requirements, sources, and assumptions, and source registration for research findings.

**Dependencies:**
- Section 04 (needs_tracker.py) -- requirement registration requires parent needs to exist
- Section 05 (quality_rules.py) -- quality check results are stored in requirement records

**Blocks:**
- Section 07 (requirements command) -- the command prompt orchestrating requirements workflow depends on these scripts

---

## Tests First

All test files live at `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/`.

### File: `tests/test_requirement_tracker.py`

```python
# Test: add creates REQ-001 with minimal fields (statement, type, priority)
# Test: add auto-increments ID across multiple additions
# Test: add validates type is one of: functional, performance, interface, constraint, quality
# Test: add validates priority is one of: high, medium, low
# Test: register transitions status from "draft" to "registered"
# Test: register requires parent_need to be set
# Test: baseline transitions status from "registered" to "baselined"
# Test: baseline on non-registered requirement raises error
# Test: withdraw sets status="withdrawn" with rationale
# Test: withdraw without rationale raises error
# Test: withdraw preserves requirement in registry (not deleted)
# Test: list excludes withdrawn requirements from default output
# Test: list with include_withdrawn=True shows all requirements
# Test: query by type returns correct subset
# Test: query by source_block returns correct subset
# Test: query by level returns correct subset (system=0, subsystem=1+)
# Test: update modifies attributes dict without overwriting other fields
# Test: export produces correct JSON structure
# Test: sync-counts updates state.json with correct registered/baselined/withdrawn counts
```

Tests should use a `tmp_path` fixture to create a temporary workspace with a `state.json` (from the template defined in section 02) and an empty `requirements_registry.json`. For tests that validate `register` requiring a parent need, create a minimal `needs_registry.json` with at least one approved need entry.

### File: `tests/test_traceability.py`

```python
# --- Link creation ---
# Test: link(REQ-001, NEED-001, "derives_from", "requirement") creates valid link
# Test: link validates source_id exists in requirements registry
# Test: link validates target_id exists in needs registry
# Test: link with non-existent source raises referential integrity error
# Test: link with non-existent target raises referential integrity error
# Test: link creates conflicts_with link type with resolution_status field

# --- Query ---
# Test: query(REQ-001, "forward") returns all forward links
# Test: query(NEED-001, "backward") returns all requirements deriving from this need
# Test: query(REQ-001, "both") returns forward and backward links
# Test: query on entity with no links returns empty list

# --- Coverage ---
# Test: coverage_report() returns percentage of needs with at least one requirement
# Test: coverage_report() with full coverage returns 100%
# Test: coverage_report() with partial coverage returns correct percentage
# Test: coverage_report() excludes withdrawn requirements

# --- Orphan detection ---
# Test: orphan_check() finds needs with no derived requirements
# Test: orphan_check() finds requirements with no parent need
# Test: orphan_check() with no orphans returns empty lists

# --- Atomic writes ---
# Test: registry not corrupted on interrupted write
# Test: schema_version present in output
```

Tests should set up a workspace directory containing `needs_registry.json` (with 2-3 approved needs), `requirements_registry.json` (with 2-3 registered requirements), and `traceability_registry.json` (initially empty or with a few seed links). The traceability module needs to read these registries to validate referential integrity.

---

## Implementation: `requirement_tracker.py`

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/requirement_tracker.py`

### Purpose

Manages the full requirement lifecycle. Each requirement has a sequential ID (REQ-001, REQ-002, ...), a status that progresses through draft -> registered -> baselined, and an optional withdrawal path. The script reads/writes `requirements_registry.json` and syncs counts to `state.json`.

### Data Model

```python
@dataclass
class Requirement:
    id: str            # REQ-001 format
    statement: str
    type: str          # functional, performance, interface, constraint, quality
    priority: str      # high, medium, low
    status: str        # draft, registered, baselined, withdrawn
    parent_need: str   # NEED-xxx
    source_block: str
    level: int         # 0 = system, 1+ = subsystem
    attributes: dict   # A1-A13 INCOSE attributes (populated on demand)
    quality_checks: dict
    tbd_tbr: dict | None
    registered_at: str
```

### Subcommands (CLI via argparse)

- **add** -- Create a new requirement in "draft" status. Requires statement, type, priority. Assigns next sequential ID. Validates type is one of the five allowed types and priority is high/medium/low.
- **update** -- Modify fields on an existing requirement by ID. Merges into `attributes` dict without overwriting unrelated fields.
- **register** -- Transition a draft requirement to "registered" status. Validates that `parent_need` is set and refers to an existing approved need in `needs_registry.json`. Sets `registered_at` timestamp.
- **baseline** -- Transition a registered requirement to "baselined" status. Raises error if current status is not "registered".
- **withdraw** -- Set status to "withdrawn". Requires a rationale string (error if missing). The requirement stays in the registry for audit trail.
- **list** -- Return all requirements, defaulting to exclude withdrawn. Accept `--include-withdrawn` flag to show all.
- **query** -- Filter requirements by type, source_block, level, or status. Return matching subset.
- **export** -- Write the full registry as formatted JSON.

### CLI interface

```bash
python3 requirement_tracker.py add --statement "The API shall respond within 200ms" --type performance --priority high --source-block api-gateway --workspace .requirements-dev/
python3 requirement_tracker.py register --id REQ-001 --parent-need NEED-003 --workspace .requirements-dev/
python3 requirement_tracker.py baseline --id REQ-001 --workspace .requirements-dev/
python3 requirement_tracker.py withdraw --id REQ-002 --rationale "Superseded by REQ-005" --workspace .requirements-dev/
python3 requirement_tracker.py list --workspace .requirements-dev/
python3 requirement_tracker.py query --type functional --workspace .requirements-dev/
```

### Registry format (`requirements_registry.json`)

```json
{
  "schema_version": "1.0.0",
  "requirements": [
    {
      "id": "REQ-001",
      "statement": "...",
      "type": "functional",
      "priority": "high",
      "status": "registered",
      "parent_need": "NEED-001",
      "source_block": "api-gateway",
      "level": 0,
      "attributes": {},
      "quality_checks": {},
      "tbd_tbr": null,
      "registered_at": "2026-02-20T..."
    }
  ]
}
```

### Key behaviors

- **Atomic writes:** All registry mutations use temp-file-then-rename pattern (write to a tempfile in the same directory, then `os.replace()` to the target path).
- **Count sync:** After every mutation, update `state.json` counts: `requirements_total`, `requirements_registered`, `requirements_baselined`, `requirements_withdrawn`, `tbd_open`, `tbr_open`.
- **Path validation:** Apply `_validate_path()` to all CLI file path arguments (reject `..` traversal, restrict to `.json` extension).
- **ID generation:** Read existing registry, find the highest numeric suffix, increment by 1. Format as `REQ-{n:03d}`.

---

## Implementation: `traceability.py`

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/traceability.py`

### Purpose

Maintains bidirectional traceability links between all entities (needs, requirements, sources, assumptions, V&V methods, sub-blocks). Links are stored as tuples in `traceability_registry.json`. Inverse traversal is computed at query time rather than stored redundantly.

### Link Types

| Link Type | Source | Target | Description |
|-----------|--------|--------|-------------|
| `derives_from` | REQ-xxx | NEED-xxx | Requirement traces to parent need |
| `verified_by` | REQ-xxx | V&V method ref | Requirement has verification method |
| `sources` | REQ-xxx | SRC-xxx | Requirement references a source |
| `informed_by` | REQ-xxx | ASN-xxx | Requirement informed by assumption |
| `allocated_to` | REQ-xxx | sub-block ID | Phase 3: requirement allocated to sub-block |
| `parent_of` | REQ-xxx | REQ-yyy | Parent-child requirement relationship |
| `conflicts_with` | REQ-xxx | REQ-yyy | Identified conflict with resolution status/rationale |

### Functions

```python
def link(source_id: str, target_id: str, link_type: str, role: str) -> None:
    """Create a traceability link. Validates both IDs exist in their registries.

    Args:
        source_id: The originating entity ID (e.g., REQ-001)
        target_id: The target entity ID (e.g., NEED-001)
        link_type: One of the defined link types above
        role: Context label for the link (e.g., "requirement", "verification")

    Raises:
        ValueError: If source_id or target_id not found in their respective registries
    """

def query(entity_id: str, direction: str = "both") -> list[dict]:
    """Find all links for an entity.

    Args:
        entity_id: The entity to query (e.g., REQ-001, NEED-003)
        direction: "forward" (entity as source), "backward" (entity as target), or "both"

    Returns:
        List of link dicts with source, target, type, role fields
    """

def coverage_report() -> dict:
    """Compute traceability coverage statistics.

    Returns dict with:
        - needs_covered: int (needs with at least one derives_from link)
        - needs_total: int (all approved, non-deferred needs)
        - coverage_pct: float
        - requirements_with_vv: int (requirements with verified_by links)
    Excludes withdrawn requirements from all calculations.
    """

def orphan_check() -> dict:
    """Find needs with no requirements and requirements with no needs.

    Returns dict with:
        - orphan_needs: list of NEED IDs with no derives_from links targeting them
        - orphan_requirements: list of REQ IDs with no derives_from links sourcing them
    """
```

### Registry format (`traceability_registry.json`)

```json
{
  "schema_version": "1.0.0",
  "links": [
    {
      "source": "REQ-001",
      "target": "NEED-001",
      "type": "derives_from",
      "role": "requirement",
      "created_at": "2026-02-20T..."
    }
  ]
}
```

### Referential integrity validation

On every `link()` call, the module must:

1. Parse the source ID prefix to determine its registry (REQ -> `requirements_registry.json`, NEED -> `needs_registry.json`, SRC -> `source_registry.json`, ASN -> assumption registry).
2. Parse the target ID prefix similarly.
3. Verify both IDs exist in their respective registries.
4. Raise `ValueError` with a clear message if either ID is not found.

For `conflicts_with` links, the link dict includes additional fields: `resolution_status` (one of "open", "resolved", "accepted") and `rationale` (string, may be null initially).

### CLI interface

```bash
python3 traceability.py link --source REQ-001 --target NEED-001 --type derives_from --role requirement --workspace .requirements-dev/
python3 traceability.py query --entity REQ-001 --direction both --workspace .requirements-dev/
python3 traceability.py coverage --workspace .requirements-dev/
python3 traceability.py orphans --workspace .requirements-dev/
```

---

## Implementation: `source_tracker.py`

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/source_tracker.py`

### Purpose

Adapted from the concept-dev plugin's source tracker with minimal changes. Manages `source_registry.json` for registering sources found during TPM research (Phase 2) and cross-referencing concept-dev sources. Sources use sequential IDs (SRC-001, SRC-002, ...).

This is a lightweight adaptation -- the concept-dev source tracker pattern should be followed closely. The primary additions for requirements-dev are:

- Sources registered during TPM research get a `research_context` field linking them to the requirement that triggered the research
- Cross-references to concept-dev sources are stored as `concept_dev_ref` field pointing to the original SRC-xxx ID in the concept-dev registry

### CLI interface

```bash
python3 source_tracker.py add --title "Performance Benchmark Study" --url "https://example.com" --type research --workspace .requirements-dev/
python3 source_tracker.py list --workspace .requirements-dev/
```

---

## V&V Planner Integration

The V&V Planner is not a separate script -- it is a conversational flow within the `/reqdev:requirements` command (Section 07). However, the **type-to-method mapping** is data that this section should establish as it is used by `requirement_tracker.py` when storing V&V attributes.

The mapping is:

| Requirement Type | Default V&V Method | Alternative |
|-----------------|-------------------|-------------|
| functional | system test | unit test |
| performance | load test | benchmark test |
| interface | integration test | contract test |
| constraint | inspection | analysis |
| quality | demonstration | analysis |

V&V attributes are stored in the requirement's `attributes` dict under INCOSE attribute keys A6-A9:
- `A6_verification_method`: The selected verification method
- `A7_success_criteria`: Measurable pass/fail criteria derived from the requirement statement
- `A8_responsible_party`: developer, QA, or reviewer
- `A9_verification_status`: planned, in_progress, complete

---

## Security Considerations

Following established codebase patterns:

- **Path validation:** `_validate_path()` on all CLI file path arguments in both `requirement_tracker.py` and `traceability.py`. Reject `..` traversal, restrict to expected extensions (`.json`). Return `os.path.realpath()` resolved paths.
- **Atomic writes:** All registry mutations use temp-file-then-rename (`tempfile.NamedTemporaryFile` in same directory, then `os.replace()`).
- **Input as data:** Requirement statement text is stored as data, never interpreted as code or instructions.
- **HTML escaping:** Not needed in these scripts (they produce JSON, not HTML). HTML escaping is applied downstream in deliverable generation (Section 09).

---

## Dependencies Summary

| What this section needs | Provided by |
|------------------------|-------------|
| `state.json` template and `update_state.py` for count sync | Section 02 |
| `needs_registry.json` with approved needs for `register` validation | Section 04 |
| `quality_checks` dict format populated by quality rules | Section 05 |
| Word list data files (indirectly, via quality_checks stored in requirements) | Section 01 |

| What this section provides | Used by |
|---------------------------|---------|
| `requirement_tracker.py` (add, register, baseline, withdraw, query) | Section 07 (requirements command) |
| `traceability.py` (link, query, coverage, orphans) | Section 07, Section 09 (deliverables), Section 10 (validation) |
| `source_tracker.py` (add, list) | Section 11 (TPM research) |
| `requirements_registry.json` schema | Section 09 (deliverables), Section 10 (validation), Section 12 (decomposition) |
| `traceability_registry.json` schema | Section 09 (deliverables), Section 10 (validation) |

---

## Implementation Notes (Actual)

### Files Created/Modified
- `skills/requirements-dev/scripts/requirement_tracker.py` -- Full lifecycle: add, register, baseline, withdraw, list, query, update, export
- `skills/requirements-dev/scripts/traceability.py` -- Bidirectional links with referential integrity, coverage report, orphan detection
- `skills/requirements-dev/scripts/source_tracker.py` -- Source registration with research_context and concept_dev_ref fields
- `skills/requirements-dev/tests/test_requirement_tracker.py` -- 19 tests
- `skills/requirements-dev/tests/test_traceability.py` -- 15 tests
- `skills/requirements-dev/tests/test_source_tracker.py` -- 6 tests

### Deviations from Plan
- **register_requirement enforces approved status:** Plan said "existing approved need" but didn't call out the approved check explicitly. Added filter for `status == "approved"` on parent need validation.
- **register_requirement requires needs_registry:** Plan's code had `if os.path.isfile` silently skipping validation. Changed to raise ValueError when file missing.
- **Link type validation added:** Plan defined VALID_LINK_TYPES but didn't require validation. Added check in link() function.
- **Duplicate link prevention:** Not in plan. Added no-op dedup to prevent registry inflation.
- **_PROTECTED_FIELDS added:** Consistent with needs_tracker pattern. Prevents status bypass via update_requirement.
- **V&V mapping data deferred:** Plan said "this section should establish" the type-to-method mapping, but it's conversational data for section-07, not a data file. Deferred to section-07.
- **tbd_open/tbr_open sync deferred:** No TBD/TBR items exist yet. Will add sync logic when items are created.
- **Source tracker tests added:** Plan didn't specify source_tracker tests, but code review flagged the gap.

### Test Count: 40 new tests, all passing
### Total test count across project: 114 tests, all passing