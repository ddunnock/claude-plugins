---
phase: 06-view-assembly-core
plan: 02
subsystem: views
tags: [view-assembly, tree-renderer, builtin-specs, hierarchical-org, gap-indicators]

requires:
  - phase: 06-view-assembly-core/01
    provides: view-spec.json, view.json schemas, scope matcher, snapshot capture, gap builder
provides:
  - assemble_view() end-to-end assembly engine with schema validation
  - 5 built-in view specs (system-overview, traceability-chain, component-detail, interface-map, gap-report)
  - render_tree() human-readable tree output with [GAP] markers
  - create_ad_hoc_spec() for transient inline scope patterns
  - get_builtin_spec() with parameter resolution and deep-copy safety
  - /system-dev:view command workflow
  - Hierarchical organization (components > interfaces > contracts)
  - Field selection with system field preservation
affects: [07-view-quality, 08-diagram-generation-core]

tech-stack:
  added: []
  patterns: [hierarchical-view-organization, field-selection, builtin-spec-registry, ad-hoc-spec-parsing, tree-rendering]

key-files:
  created:
    - commands/view.md
    - tests/test_view_integration.py
  modified:
    - scripts/view_assembler.py
    - tests/test_view_assembler.py
    - tests/test_schema_validator.py

key-decisions:
  - "Hierarchical org flattens back to sections format (view.json compatible) with logical grouping"
  - "System fields (slot_id, slot_type, name, version) always preserved in field selection"
  - "Orphan slots (no parent component in view) go in unlinked section rather than being dropped"
  - "get_builtin_spec returns deep copies to prevent mutation of BUILTIN_SPECS"
  - "Ad-hoc patterns require colon separator (slot_type:name_glob) for explicit typing"

patterns-established:
  - "Built-in specs are static dicts in BUILTIN_SPECS, resolved at call time"
  - "Tree output uses +-- connectors with section headings like component/ (N)"
  - "Gap markers rendered as [GAP] [SEVERITY] with suggestion on next line"

requirements-completed: [VIEW-01, VIEW-02, VIEW-05, VIEW-06, VIEW-07, VIEW-08, VIEW-10]

duration: 6min
completed: 2026-03-02
---

# Phase 6 Plan 2: View Assembly Engine Summary

**Complete view assembly pipeline with 5 built-in specs, hierarchical slot organization, tree renderer, and /system-dev:view command**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-02T20:28:55Z
- **Completed:** 2026-03-02T20:35:14Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- assemble_view() function wiring snapshot capture, scope matching, gap building, hierarchical organization, and schema validation into a single pipeline
- 5 built-in view specs covering system overview, traceability chains, component detail, interface maps, and gap reports
- Human-readable tree renderer with Unicode connectors, [GAP] markers, severity labels, and gap summary
- Ad-hoc spec creation from inline patterns and parameterized spec resolution
- Integration test suite verifying end-to-end assembly, slot preservation (VIEW-10), and schema conformance (VIEW-06)
- 43 new tests (25 unit + 8 integration + 10 renderer/spec tests) bringing view test total to 65

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement assemble_view with hierarchical org and gap handling** - `4b39b2e` (test RED) + `ae9b7c6` (feat GREEN)
2. **Task 2: Built-in specs, tree renderer, view command** - `ef5fdca` (feat)

_Note: Task 1 used TDD (test -> feat). Task 2 was standard auto._

## Files Created/Modified
- `scripts/view_assembler.py` - Added assemble_view(), _apply_field_selection(), _organize_hierarchically(), BUILTIN_SPECS, get_builtin_spec(), create_ad_hoc_spec(), render_tree()
- `commands/view.md` - /system-dev:view command workflow with invocation, built-in spec table, output examples, error handling
- `tests/test_view_assembler.py` - 43 new unit tests for assembly, field selection, hierarchy, built-in specs, ad-hoc specs, tree rendering
- `tests/test_view_integration.py` - 8 integration tests for full pipeline including slot preservation and schema validation
- `tests/test_schema_validator.py` - Updated expected schema count to include view/view-spec schemas from Plan 01

## Decisions Made
- Hierarchical organization keeps view.json-compatible flat sections format but groups logically (components first, then linked interfaces, then linked contracts, then unlinked)
- System fields always preserved in field selection to maintain slot identity
- Orphan slots (interfaces/contracts without parent in view scope) go in "unlinked" section rather than being silently dropped
- Built-in specs use deep copy on access to prevent mutation of the static registry

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated schema validator test for view schemas**
- **Found during:** Task 2 (full regression)
- **Issue:** test_all_slot_types_load in test_schema_validator.py expected 14 schemas but view.json and view-spec.json from Plan 01 added 2 more, causing regression failure
- **Fix:** Updated expected list to include "view" and "view-spec" (16 total)
- **Files modified:** tests/test_schema_validator.py
- **Verification:** Full regression (368 tests) passes
- **Committed in:** ef5fdca (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Test data correction from prior plan. No scope creep.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Complete view assembly engine ready for Phase 7 (View Quality & Handoff)
- All public API exported: assemble_view, render_tree, BUILTIN_SPECS, get_builtin_spec, create_ad_hoc_spec
- 368 tests passing across entire test suite
- View output format established for diagram generation pipeline (Phase 8)

---
*Phase: 06-view-assembly-core*
*Completed: 2026-03-02*
