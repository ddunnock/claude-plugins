---
phase: 08-diagram-generation-core
plan: 02
subsystem: diagram
tags: [orchestration, slot-api-write, diagram-hint, command-spec]

requires:
  - phase: 08-diagram-generation-core
    plan: 01
    provides: D2/Mermaid pure generation engines, diagram schema, slot type registration
provides:
  - generate_diagram() orchestration pipeline (view assembly -> generation -> SlotAPI write)
  - /system-dev:diagram command specification
  - diagram_hint on built-in view specs
  - Optional diagram_hint field in view-spec.json schema
affects: [09-diagram-templates-quality]

tech-stack:
  added: []
  patterns: [orchestration pipeline, format hint resolution, content-hash update-on-change]

key-files:
  created:
    - commands/diagram.md
  modified:
    - scripts/diagram_generator.py
    - scripts/view_assembler.py
    - schemas/view-spec.json
    - tests/test_diagram_generator.py

key-decisions:
  - "Format resolution: format_override > spec.diagram_hint > ValueError"
  - "Hint mapping: structural->D2, behavioral->Mermaid; literal d2/mermaid also accepted"
  - "Diagrams are intentional artifacts from named specs only -- no ad-hoc pattern support"
  - "gap-report has no diagram_hint (requires explicit --format)"

requirements-completed: [DIAG-03, DIAG-09]

duration: 4min
completed: 2026-03-07
---

# Phase 8 Plan 02: Diagram Orchestration Layer Summary

**generate_diagram() pipeline wiring view assembly to SlotAPI writes, with diagram_hint on built-in specs and /system-dev:diagram command**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-07T18:13:01Z
- **Completed:** 2026-03-07T18:16:53Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Created `generate_diagram()` orchestrator that pipes view assembly -> format selection -> D2/Mermaid generation -> schema validation -> SlotAPI.ingest() write
- Added `diagram_hint` field to 4 of 5 BUILTIN_SPECS (system-overview/component-detail/interface-map: structural, traceability-chain: behavioral, gap-report: none)
- Added optional `diagram_hint` property to `schemas/view-spec.json` (backward compatible, not in required array)
- Created `commands/diagram.md` command specification following established view.md pattern
- 17 new integration tests covering orchestration flow, format override, error handling, DIAG-09 slot type enforcement

## Task Commits

Each task was committed atomically:

1. **Task 1: Orchestration layer, diagram_hint, and view-spec schema update** - `55d8d27` (feat, TDD)
2. **Task 2: Create /system-dev:diagram command specification** - `a38b1b9` (feat)

## Files Created/Modified
- `scripts/diagram_generator.py` - Added generate_diagram() orchestrator with full pipeline
- `scripts/view_assembler.py` - Added diagram_hint to BUILTIN_SPECS entries
- `schemas/view-spec.json` - Added optional diagram_hint property (enum: structural, behavioral)
- `tests/test_diagram_generator.py` - 17 new tests (58 total in file, 450 total suite)
- `commands/diagram.md` - Full command spec with invocation, workflow, built-in specs table, error handling

## Decisions Made
- Format resolution priority: format_override > spec.diagram_hint > ValueError
- Hint mapping: "structural" and "d2" both produce D2 output; "behavioral" and "mermaid" both produce Mermaid
- Diagrams are intentional artifacts -- ad-hoc patterns rejected with guidance to create named specs
- gap-report intentionally omits diagram_hint to require explicit --format choice

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 08 (Diagram Generation Core) is now complete
- Phase 09 (Diagram Templates & Quality) can begin with all diagram infrastructure in place
- generate_diagram() provides the integration point for template-based generation

---
*Phase: 08-diagram-generation-core*
*Completed: 2026-03-07*
