---
phase: 06-view-assembly-core
plan: 01
subsystem: views
tags: [json-schema, fnmatch, snapshot, gap-indicator, view-assembly]

requires:
  - phase: 05-traceability-core
    provides: SlotAPI, SchemaValidator, registry patterns
provides:
  - View-spec JSON schema for declarative view specifications
  - View output JSON schema with sections and gap indicators
  - Scope pattern matcher using fnmatch glob syntax
  - Snapshot reader capturing consistent state via SlotAPI
  - Gap indicator builder with configurable severity (XCUT-03)
  - Gap rules loader with externalized config
affects: [06-02-view-assembly-core, 07-view-quality]

tech-stack:
  added: [fnmatch, copy.deepcopy]
  patterns: [scope-pattern-matching, snapshot-capture, gap-indicators, externalized-gap-rules]

key-files:
  created:
    - schemas/view-spec.json
    - schemas/view.json
    - scripts/view_assembler.py
  modified:
    - tests/test_view_assembler.py

key-decisions:
  - "Scope patterns use fnmatch glob syntax (*, ?) on slot name field"
  - "Snapshots deep-copy all data for immutability isolation"
  - "Gap severity defaults to warning, overridable via gap-rules.json (XCUT-03)"
  - "All registry reads go through SlotAPI.query(), never direct file I/O (XCUT-04)"

patterns-established:
  - "Scope pattern syntax: <slot_type>:<name_glob> parsed by colon split"
  - "Snapshot structure: {snapshot_id, captured_at, slots_by_type}"
  - "Gap indicator structure: {scope_pattern, slot_type, severity, reason, suggestion}"
  - "View specs are JSON files validated against view-spec.json schema"

requirements-completed: [VIEW-02, VIEW-05, VIEW-06, VIEW-07, VIEW-08]

duration: 3min
completed: 2026-03-02
---

# Phase 6 Plan 1: View Schemas & Core Engine Summary

**View-spec and view-output JSON schemas with fnmatch scope matching, snapshot capture, and configurable gap indicators**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-02T20:20:41Z
- **Completed:** 2026-03-02T20:24:19Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Two Draft 2020-12 JSON schemas: view-spec.json (declarative input) and view.json (structured output with gap_summary)
- Scope pattern matcher using fnmatch glob syntax against slot name field, supporting wildcard, prefix, and exact matching
- Snapshot reader that deep-copies all registry data via SlotAPI.query() for immutable, consistent snapshots
- Gap indicator builder with configurable severity from externalized gap-rules.json config (XCUT-03)
- Parameter resolution in view specs with {variable} substitution and missing-parameter validation
- 22 unit tests covering schemas, matching, snapshots, gaps, spec loading, and rules loading

## Task Commits

Each task was committed atomically:

1. **Task 1: Create view-spec and view output JSON schemas** - `7885c73` (test) + `c21e905` (feat)
2. **Task 2: Implement scope pattern matcher, snapshot reader, and gap builder** - `87a6af3` (test) + `86f56ef` (feat)

_Note: TDD tasks have two commits each (test RED -> feat GREEN)_

## Files Created/Modified
- `schemas/view-spec.json` - JSON Schema for declarative view specification files (name, scope_patterns, parameters, fields)
- `schemas/view.json` - JSON Schema for assembled view output (sections, gaps, gap_summary)
- `scripts/view_assembler.py` - Core engine: load_view_spec, match_scope_pattern, capture_snapshot, build_gap_indicator, load_gap_rules
- `tests/test_view_assembler.py` - 22 unit tests for schemas and all engine functions

## Decisions Made
- Used fnmatch for scope pattern matching -- simple, stdlib, supports * and ? globs
- Scope pattern syntax is `<slot_type>:<name_glob>` with colon as separator
- Snapshots iterate all SLOT_TYPE_DIRS via api.query() rather than reading index directly
- Gap suggestions reference existing skill commands (e.g., "/system-dev:decompose")
- Default gap severity is "warning" for most slot types, "info" for contracts and traceability-links

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed interface fixture fields in tests**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** Test fixture used `provided_by`/`consumed_by` fields which don't exist in interface schema; correct fields are `source_component`/`target_component`
- **Fix:** Updated populated_api fixture to use correct interface schema fields
- **Files modified:** tests/test_view_assembler.py
- **Verification:** All 22 tests pass
- **Committed in:** 86f56ef (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Test data correction only. No scope creep.

## Issues Encountered
None beyond the fixture field name correction noted above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Both schemas ready for Plan 02's full assembler to build on
- All five core functions exported: load_view_spec, match_scope_pattern, capture_snapshot, build_gap_indicator, load_gap_rules
- Plan 02 can import these directly and wire them into the assembly pipeline

---
*Phase: 06-view-assembly-core*
*Completed: 2026-03-02*
