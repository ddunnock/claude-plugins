---
phase: 08-diagram-generation-core
plan: 01
subsystem: diagram
tags: [d2, mermaid, diagram-generation, pure-functions, gap-placeholders]

requires:
  - phase: 07-view-quality-handoff
    provides: view handoff format (sections, edges, gaps arrays)
provides:
  - D2 structural diagram generation engine (generate_d2)
  - Mermaid behavioral diagram generation engine (generate_mermaid)
  - Diagram slot JSON Schema (schemas/diagram.json)
  - Diagram slot type registration in registry and init_workspace
  - Content-hash diagram slot ID computation
affects: [08-02, 09-diagram-templates-quality]

tech-stack:
  added: []
  patterns: [pure-function generation engines, severity-based gap coloring, content-hash slot IDs]

key-files:
  created:
    - scripts/diagram_generator.py
    - schemas/diagram.json
    - tests/test_diagram_generator.py
  modified:
    - scripts/registry.py
    - scripts/init_workspace.py
    - tests/test_schema_validator.py

key-decisions:
  - "D2 components render as rectangle containers; non-component types as labeled nodes"
  - "Mermaid direction auto-selects LR when edge count > 2x node count, otherwise TD"
  - "Unlinked slots: D2 wraps in 'Unlinked' container, Mermaid uses classDef unlinked with lighter fill"
  - "Gap nodes connect to first slot of matching section type via dashed connection"

patterns-established:
  - "Pure generation functions: generate_d2/generate_mermaid accept view dict, return string, no side effects"
  - "Severity color map: error=#dc3545, warning=#e6a117, info=#888888 (shared across D2 and Mermaid)"
  - "Content-hash slot ID: diag-{spec_name}-{sha256(source)[:12]} for deterministic identification"

requirements-completed: [DIAG-01, DIAG-02, DIAG-04, DIAG-06]

duration: 4min
completed: 2026-03-07
---

# Phase 8 Plan 01: Diagram Generation Core Summary

**D2 and Mermaid pure generation engines with gap placeholders, diagram schema, and slot type registration**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-07T18:06:23Z
- **Completed:** 2026-03-07T18:10:39Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Created `generate_d2()` and `generate_mermaid()` pure functions that transform view handoff data into valid diagram source code
- D2 renders components as containers, edges as connections, and gaps as dashed/color-coded shapes with [GAP] prefix
- Mermaid renders flowchart nodes, labeled arrows, and classDef gap styles (no commas in stroke-dasharray)
- Registered "diagram" slot type in SLOT_TYPE_DIRS, SLOT_ID_PREFIXES, and init_workspace registry_dirs
- Created schemas/diagram.json with all required fields and additionalProperties: false
- 41 tests covering schema validation, registry registration, D2 generation, Mermaid generation, gap rendering, and edge cases

## Task Commits

Each task was committed atomically:

1. **Task 1: Diagram schema, slot type registration, and test scaffolding** - `1b09663` (feat)
2. **Task 2: D2 and Mermaid pure generation functions with gap placeholders** - `e459e5f` (feat)

_Note: TDD tasks - tests written first (RED), then implementation (GREEN)_

## Files Created/Modified
- `schemas/diagram.json` - JSON Schema for diagram slot type (format, diagram_type, source, etc.)
- `scripts/diagram_generator.py` - D2 and Mermaid generation engines with _sanitize_id, _compute_diagram_slot_id
- `scripts/registry.py` - Added "diagram" to SLOT_TYPE_DIRS and SLOT_ID_PREFIXES
- `scripts/init_workspace.py` - Added "registry/diagram" to registry_dirs list
- `tests/test_diagram_generator.py` - 41 tests for schema, registry, D2, Mermaid, gaps, IDs
- `tests/test_schema_validator.py` - Updated expected schema count from 16 to 17

## Decisions Made
- D2 components render as rectangle containers; non-component types (interface, contract) as simple labeled nodes
- Mermaid direction auto-selects LR when edge count > 2x node count, otherwise TD
- Unlinked slots: D2 wraps in "Unlinked" container, Mermaid uses classDef unlinked with lighter fill (#f8f8f8)
- Gap nodes connect to first slot of matching section type via dashed connection for context
- Gap classDef names use title-cased severity: gapWarning, gapError, gapInfo

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated test_schema_validator.py expected schema list**
- **Found during:** Task 1 (schema creation)
- **Issue:** test_all_slot_types_load expected 16 schemas; adding diagram.json made it 17
- **Fix:** Added "diagram" to the expected types list and updated count in docstring
- **Files modified:** tests/test_schema_validator.py
- **Verification:** Full test suite passes (450 tests)
- **Committed in:** 1b09663 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary fix for test compatibility. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- D2 and Mermaid generation engines ready for Plan 02's orchestration layer
- Plan 02 will add SlotAPI write integration, diagram_hint on view specs, and /system-dev:diagram command
- Content-hash slot ID function ready for update-on-change-only semantics

---
*Phase: 08-diagram-generation-core*
*Completed: 2026-03-07*
