Now I have all the context needed. Let me generate the section content.

# Section 09: Deliverables

## Overview

This section implements the deliverable assembly pipeline: the **document-writer agent**, the **/reqdev:deliver command**, and **reqif_export.py**. Together these components read from the JSON registries (needs, requirements, traceability), validate traceability completeness, generate Markdown deliverable documents from templates, export ReqIF XML, and manage the baselining workflow.

## Dependencies

- **Section 07 (Requirements Command):** The `/reqdev:requirements` command must be implemented first. Deliverable generation reads from `requirements_registry.json`, `needs_registry.json`, and `traceability_registry.json` that are populated during the requirements workflow.
- **Section 02 (State Management):** Uses `update_state.py` for phase/gate/artifact tracking and atomic writes.
- **Section 06 (Requirements Engine):** Uses `requirement_tracker.py` for baselining status transitions and `traceability.py` for coverage reports and orphan checks.

## File Inventory

| File | Action | Purpose |
|------|--------|---------|
| `skills/requirements-dev/scripts/reqif_export.py` | Create | ReqIF XML export from JSON registries |
| `skills/requirements-dev/agents/document-writer.md` | Create | Agent prompt for deliverable generation |
| `skills/requirements-dev/commands/reqdev.deliver.md` | Create | Command prompt for `/reqdev:deliver` |
| `skills/requirements-dev/templates/requirements-specification.md` | Create | Template for specification document |
| `skills/requirements-dev/templates/traceability-matrix.md` | Create | Template for traceability matrix |
| `skills/requirements-dev/templates/verification-matrix.md` | Create | Template for verification matrix |
| `tests/test_reqif_export.py` | Create | Tests for ReqIF export |
| `tests/test_integration.py` | Modify | Add deliverable generation and baselining tests |

## Tests (Write First)

### File: `skills/requirements-dev/tests/test_reqif_export.py`

```python
"""Tests for ReqIF XML export functionality."""
import json
import os
import pytest
from unittest.mock import patch


# Test: export_reqif generates valid XML structure
def test_export_generates_valid_xml(tmp_path):
    """Export with sample registries produces well-formed XML with ReqIF root element."""


# Test: export maps each requirement to a SPEC-OBJECT
def test_export_maps_requirements_to_spec_objects(tmp_path):
    """Each requirement in registry becomes a SPEC-OBJECT in ReqIF output."""


# Test: export maps traceability links to SPEC-RELATIONS
def test_export_maps_links_to_spec_relations(tmp_path):
    """Each traceability link becomes a SPEC-RELATION in ReqIF output."""


# Test: export maps requirement types to SPEC-TYPES
def test_export_maps_types_to_spec_types(tmp_path):
    """Each requirement type (functional, performance, etc.) maps to a SPEC-TYPE."""


# Test: export handles empty requirements registry (produces minimal valid ReqIF)
def test_export_empty_registry(tmp_path):
    """Empty registries produce a minimal but valid ReqIF document (no SPEC-OBJECTS)."""


# Test: export with missing reqif package prints install message and exits 0
def test_export_missing_reqif_package(tmp_path):
    """When reqif package is not installed, prints install instructions and exits 0."""


# Test: export escapes XML special characters in requirement statements
def test_export_escapes_xml_special_chars(tmp_path):
    """Requirement text containing <, >, &, quotes is properly escaped in XML output."""
```

### File: `skills/requirements-dev/tests/test_integration.py` (additions)

```python
"""Integration tests for deliverable generation and baselining.

These tests are ADDED to the existing test_integration.py file created in section-07.
"""


# --- Deliverable generation ---

# Test: generate specification with 3 blocks, 10 requirements -> correct markdown structure
def test_generate_specification_structure(workspace):
    """Specification markdown has block headings, type sub-sections, and requirement entries."""


# Test: generate traceability matrix -> all links present
def test_generate_traceability_matrix(workspace):
    """Traceability matrix includes all need-to-requirement-to-VV chains."""


# Test: generate verification matrix -> all requirements have V&V entries
def test_generate_verification_matrix(workspace):
    """Verification matrix lists every registered requirement with method and criteria."""


# Test: baselining after delivery -> all requirements status="baselined"
def test_baselining_transitions_all_requirements(workspace):
    """After deliverables approved, all registered requirements become baselined."""


# --- Withdrawal ---

# Test: withdraw requirement -> excluded from coverage -> preserved in registry
def test_withdrawn_excluded_from_coverage(workspace):
    """Withdrawn requirements remain in registry but do not count in coverage metrics."""


# Test: withdraw requirement -> deliverable regeneration excludes it
def test_withdrawn_excluded_from_deliverables(workspace):
    """Regenerated deliverables omit withdrawn requirements."""
```

## Implementation Details

### 1. ReqIF Export Script (`skills/requirements-dev/scripts/reqif_export.py`)

This is the only script in the plugin with an external dependency (the `reqif` package by strictdoc). It must handle `ImportError` gracefully.

```python
"""ReqIF XML export from JSON registries.

Requires: pip install reqif (strictdoc's reqif package)
Gracefully handles missing package - prints install instructions and exits 0.
"""
import json
import sys
import os
import argparse


def _validate_path(path: str, allowed_extensions: list[str]) -> str:
    """Validate path: reject traversal, restrict extensions, return resolved path."""


def export_reqif(requirements_path: str, needs_path: str,
                 traceability_path: str, output_path: str) -> None:
    """Generate ReqIF XML from JSON registries.

    Mapping:
    - Each requirement type (functional, performance, interface, constraint, quality)
      maps to a ReqIF SPEC-TYPE with type-specific attribute definitions.
    - INCOSE attributes (A1-A13) map to ReqIF ATTRIBUTE-DEFINITION entries on each SPEC-TYPE.
    - Each requirement becomes a SPEC-OBJECT referencing its SPEC-TYPE.
    - Each traceability link becomes a SPEC-RELATION.
    - Block hierarchy maps to SPEC-HIERARCHY for nested specification structure.

    If the reqif package is not installed, prints a user-friendly install message
    and returns (exits 0, does not raise).

    XML special characters in requirement statements (<, >, &, quotes) are escaped
    via the reqif library's built-in handling.
    """


def main():
    """CLI entry point.

    Usage:
        python3 reqif_export.py \\
            --requirements .requirements-dev/requirements_registry.json \\
            --needs .requirements-dev/needs_registry.json \\
            --traceability .requirements-dev/traceability_registry.json \\
            --output .requirements-dev/exports/requirements.reqif
    """
```

Key implementation notes:
- Import `reqif` inside the function body, not at module top level, so the `ImportError` can be caught per-invocation.
- The `reqif` package provides `ReqIFBundle`, `ReqIFContent`, `ReqIFSpecObject`, `ReqIFSpecRelation`, `ReqIFSpecType`, etc.
- Create the `exports/` subdirectory if it does not exist.
- Use `_validate_path()` following codebase security patterns (reject `..` traversal, restrict to `.json` for inputs and `.reqif` for output).
- All writes use atomic temp-file-then-rename pattern.

### 2. Document-Writer Agent (`skills/requirements-dev/agents/document-writer.md`)

The document-writer is a **sonnet model** agent that generates deliverable documents from the JSON registries and Markdown templates.

The agent prompt should instruct the agent to:

1. Read the three template files from `templates/` (requirements-specification.md, traceability-matrix.md, verification-matrix.md).
2. Read the three registry files from `.requirements-dev/` (needs_registry.json, requirements_registry.json, traceability_registry.json).
3. For the **requirements specification**: organize by block, then by requirement type within each block. Each requirement entry shows ID, statement, priority, V&V method, and parent need. Exclude withdrawn requirements.
4. For the **traceability matrix**: build the full chain from concept-dev source to need to requirement to V&V method. Highlight orphans and gaps.
5. For the **verification matrix**: list all registered requirements with their verification method, success criteria, and responsible party.
6. Use `html.escape()` equivalent care: treat all registry content as data, never as formatting instructions.
7. Present each generated document section to the user for review before finalizing.

The agent does NOT call Python scripts directly. It reads registries, applies templates, and produces Markdown output.

### 3. `/reqdev:deliver` Command (`skills/requirements-dev/commands/reqdev.deliver.md`)

The command prompt orchestrates the full deliverable assembly process:

**Procedure encoded in the command prompt:**

1. **Pre-check:** Verify `requirements` gate is passed in `state.json` (run `python3 scripts/update_state.py check-gate requirements`). If not passed, instruct user to complete requirements first.

2. **Validate traceability:** Run `python3 scripts/traceability.py orphan_check` and `python3 scripts/traceability.py coverage_report`. Present any gaps or orphans to the user. Warn but do not block delivery (gaps are reported in the traceability matrix).

3. **Generate deliverables** (invoke document-writer agent for each):
   - REQUIREMENTS-SPECIFICATION.md
   - TRACEABILITY-MATRIX.md
   - VERIFICATION-MATRIX.md

4. **User approval:** Present each deliverable for user review. User can request edits or approve. All three must be approved before proceeding.

5. **ReqIF export:** Run `python3 scripts/reqif_export.py` with the registry paths. If the `reqif` package is not installed, inform the user and continue (ReqIF is optional).

6. **Baselining:** After all deliverables are approved:
   - Transition all registered requirements to `status: "baselined"` by running `python3 scripts/requirement_tracker.py baseline --all`.
   - This is the formal baseline. Baselined requirements can only be modified through a change request workflow (out of scope for Phase 1, but enables Phase 3 decomposition which requires baselined parent requirements).

7. **State updates:**
   - `python3 scripts/update_state.py set-artifact deliver REQUIREMENTS-SPECIFICATION.md`
   - `python3 scripts/update_state.py set-artifact deliver TRACEABILITY-MATRIX.md`
   - `python3 scripts/update_state.py set-artifact deliver VERIFICATION-MATRIX.md`
   - `python3 scripts/update_state.py pass-gate deliver`
   - `python3 scripts/update_state.py set-phase deliver`

8. **Summary:** Display delivery summary with counts (requirements baselined, deliverables generated, ReqIF export status).

### 4. Templates

#### `skills/requirements-dev/templates/requirements-specification.md`

The template provides the document skeleton. The document-writer agent fills in the content from registries. Structure:

```
# Requirements Specification

## Document Info
- Session: {session_id}
- Generated: {timestamp}
- Requirements baselined: {count}

## {Block Name}

### {Block Description}

#### Functional Requirements
| ID | Statement | Priority | V&V Method | Parent Need |
|----|-----------|----------|------------|-------------|
| REQ-xxx | ... | ... | ... | NEED-xxx |

#### Performance Requirements
...

#### Interface Requirements
...

#### Constraint Requirements
...

#### Quality Requirements
...

(repeat for each block)
```

#### `skills/requirements-dev/templates/traceability-matrix.md`

```
# Traceability Matrix

## Full Chain: Source -> Need -> Requirement -> V&V

| Source | Need | Requirement | V&V Method | Status |
|--------|------|-------------|------------|--------|

## Orphans and Gaps

### Needs with no derived requirements
### Requirements with no parent need
### Requirements with no V&V method
```

#### `skills/requirements-dev/templates/verification-matrix.md`

```
# Verification Matrix

| Req ID | Statement | Type | Method | Success Criteria | Responsible |
|--------|-----------|------|--------|-----------------|-------------|
```

### 5. Baselining Logic

The baselining step uses `requirement_tracker.py`'s existing `baseline` subcommand (from section-06). The `/reqdev:deliver` command calls it with a `--all` flag that transitions every requirement with `status: "registered"` to `status: "baselined"`. The `baseline` subcommand must:

- Reject any requirement not in "registered" status.
- Set `baselined_at` timestamp on each requirement.
- Update state.json counts via `sync-counts`.
- Withdrawn requirements are unaffected (they remain "withdrawn").
- Draft requirements are flagged as warnings (should have been registered before delivery).

### 6. Security Considerations

Following codebase patterns:

- **Path validation:** `_validate_path()` on all CLI file arguments in `reqif_export.py`. Reject `..` traversal, restrict to expected extensions (`.json` input, `.reqif` output).
- **HTML escaping:** The document-writer agent treats all registry content as data. Requirement statements containing characters like `<`, `>`, `&` are preserved literally in Markdown output (Markdown does not interpret HTML entities the same way).
- **XML escaping:** `reqif_export.py` ensures XML special characters in requirement text are properly escaped in the ReqIF output (handled by the reqif library, but verify in tests).
- **Atomic writes:** All file writes (deliverables, ReqIF export) use temp-file-then-rename.
- **No network:** `reqif_export.py` is local-only. No network calls in any deliverable generation script.

## Implementation Checklist

1. Write tests in `tests/test_reqif_export.py` (7 test stubs)
2. Add deliverable/baselining tests to `tests/test_integration.py` (6 test stubs)
3. Create `skills/requirements-dev/scripts/reqif_export.py` with `export_reqif()` function and CLI
4. Create `skills/requirements-dev/agents/document-writer.md` agent prompt (sonnet model)
5. Create the three template files in `skills/requirements-dev/templates/`
6. Create `skills/requirements-dev/commands/reqdev.deliver.md` command prompt
7. Verify `requirement_tracker.py` (section-06) supports `baseline --all` flag; if not, add it
8. Run tests: `cd /Users/dunnock/projects/claude-plugins && uv run pytest skills/requirements-dev/tests/test_reqif_export.py -v`
9. Run integration tests: `cd /Users/dunnock/projects/claude-plugins && uv run pytest skills/requirements-dev/tests/test_integration.py -v -k deliverable`

## Implementation Notes (Post-Build)

### Deviations from Plan

1. **ReqIF export uses strictdoc `reqif` package directly** - The implementation constructs `ReqIFBundle` with `ReqIFSpecObject`, `ReqIFSpecRelation`, `ReqIFSpecType`, and `ReqIFSpecification` models, then uses `ReqIFUnparser.unparse()` to generate XML. The `ReqIFObjectLookup` required manual dictionary construction (not a simple content wrapper).

2. **Needs added as SPEC-OBJECTs in ReqIF** - The original plan only mapped requirements to SPEC-OBJECTs. During code review, dangling references were found in SPEC-RELATIONs where `derives_from` links pointed to NEED-xxx IDs that had no corresponding SPEC-OBJECT. Fixed by also exporting needs as SPEC-OBJECTs with a `SPEC-TYPE-NEED` type.

3. **`baseline_all()` function added to `requirement_tracker.py`** - The plan mentioned `baseline --all` CLI flag but the function didn't exist. Added `baseline_all()` that transitions all registered requirements atomically, reports skipped drafts, and sets `baselined_at` timestamp.

4. **Templates created in section-01 scaffolding** - The three template files (requirements-specification.md, traceability-matrix.md, verification-matrix.md) were already created with Handlebars-style placeholders during section-01 scaffolding.

### Actual Files Created/Modified

| File | Action | Notes |
|------|--------|-------|
| `skills/requirements-dev/scripts/reqif_export.py` | Implemented | Full ReqIF export with graceful ImportError handling |
| `skills/requirements-dev/scripts/requirement_tracker.py` | Modified | Added `baseline_all()`, `baselined_at` timestamp, `--all` CLI flag |
| `skills/requirements-dev/agents/document-writer.md` | Implemented | Sonnet agent for deliverable generation |
| `skills/requirements-dev/commands/reqdev.deliver.md` | Implemented | 8-step delivery orchestration |
| `skills/requirements-dev/tests/test_reqif_export.py` | Created | 7 tests (XML validity, mapping, empty, missing pkg, escaping) |
| `skills/requirements-dev/tests/test_integration.py` | Modified | Added 7 tests (baselining, baseline_all, withdrawal, coverage, orphans) |

### Test Results

- 139 total tests passing (up from 131)
- 7 new ReqIF export tests
- 7 new deliverable/baselining integration tests (including `baseline_all` coverage)