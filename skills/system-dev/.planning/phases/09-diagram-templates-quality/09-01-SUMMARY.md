---
phase: 09-diagram-templates-quality
plan: 01
subsystem: diagrams
tags: [jinja2, d2, mermaid, templates, determinism]

requires:
  - phase: 08-diagram-generation-core
    provides: "generate_d2, generate_mermaid, generate_diagram functions"
provides:
  - "Jinja2 template-driven diagram rendering with manifest registry"
  - "Two-tier template resolution (user override > built-in)"
  - "Deterministic output via _build_template_context() pre-sorting (DIAG-08)"
  - "Schema fields: abstraction_level, diagram_template, generation_elapsed_ms"
affects: [09-02, 09-03]

tech-stack:
  added: [jinja2]
  patterns: [manifest-driven-template-registry, two-tier-template-resolution, deterministic-sorting]

key-files:
  created:
    - templates/manifest.json
    - templates/d2-structural.j2
    - templates/d2-component.j2
    - templates/mermaid-behavioral.j2
  modified:
    - scripts/diagram_generator.py
    - schemas/view-spec.json
    - schemas/diagram.json
    - scripts/init_workspace.py
    - tests/test_diagram_generator.py
    - pyproject.toml

key-decisions:
  - "Jinja2 templates with custom filters (sanitize_id, gap_color, truncate_label) for diagram rendering"
  - "Template context pre-sorts all data (sections, edges, gaps) before rendering for determinism"
  - "d2-component.j2 initially identical to d2-structural.j2; differentiation deferred to Plan 02"
  - "generation_elapsed_ms schema update pulled into Task 1 (blocking dependency for generate_diagram)"

patterns-established:
  - "Manifest-driven template registry: templates/manifest.json maps format+type to .j2 files"
  - "Two-tier resolution: workspace_root/templates/ overrides built-in templates/ by filename"
  - "Deterministic context building: _build_template_context() sorts all iterables before template rendering"

requirements-completed: [DIAG-07, DIAG-08]

duration: 3min
completed: 2026-03-07
---

# Phase 9 Plan 01: Diagram Template Registry Summary

**Jinja2 template-driven diagram rendering with manifest registry, two-tier override resolution, and deterministic pre-sorted context (DIAG-07, DIAG-08)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-07T19:57:21Z
- **Completed:** 2026-03-07T20:01:13Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Refactored diagram generation from hardcoded string building to Jinja2 template rendering
- Created manifest-driven template registry with three .j2 templates (d2-structural, d2-component, mermaid-behavioral)
- Added two-tier template resolution allowing user overrides in .system-dev/templates/
- Deterministic output guaranteed by _build_template_context() pre-sorting all data
- Added schema fields: abstraction_level, diagram_template (view-spec), generation_elapsed_ms (diagram)
- All 82 tests pass (67 existing + 15 new)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Jinja2 templates, manifest, and template loader** - `35f824b` (feat)
2. **Task 2: Schema updates, init_workspace, and template tests** - `171fe81` (feat)

## Files Created/Modified
- `templates/manifest.json` - Template registry mapping format+type to .j2 files
- `templates/d2-structural.j2` - Jinja2 template for D2 structural diagrams
- `templates/d2-component.j2` - Jinja2 template for D2 component-detail diagrams (initially identical to structural)
- `templates/mermaid-behavioral.j2` - Jinja2 template for Mermaid behavioral diagrams
- `scripts/diagram_generator.py` - Refactored to use template rendering with _build_template_context, _load_template
- `schemas/view-spec.json` - Added abstraction_level and diagram_template optional fields
- `schemas/diagram.json` - Added generation_elapsed_ms optional field
- `scripts/init_workspace.py` - Added templates/ to registry_dirs for user overrides
- `tests/test_diagram_generator.py` - 15 new tests for templates, determinism, context, schemas, migration parity
- `pyproject.toml` - Added jinja2>=3.1 dependency

## Decisions Made
- Jinja2 templates use custom filters (sanitize_id, gap_color, truncate_label) registered on Environment
- Template context pre-sorts sections by slot_type, slots by name, edges by (source_id, target_id, relationship_type), gaps by slot_type for determinism
- d2-component.j2 starts identical to d2-structural.j2; differentiation planned for Plan 02 with abstraction layers
- generation_elapsed_ms schema update was pulled from Task 2 into Task 1 (blocking dependency for generate_diagram ingest)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Pulled generation_elapsed_ms schema update into Task 1**
- **Found during:** Task 1 (diagram_generator.py refactor)
- **Issue:** generate_diagram() now writes generation_elapsed_ms to content dict, but diagram.json schema has additionalProperties:false, causing schema validation failure on ingest
- **Fix:** Added generation_elapsed_ms field to schemas/diagram.json in Task 1 instead of Task 2
- **Files modified:** schemas/diagram.json
- **Verification:** All 82 tests pass including schema validation test
- **Committed in:** 35f824b (Task 1 commit)

**2. [Rule 1 - Bug] Fixed _load_template() missing file validation**
- **Found during:** Task 2 (template loading tests)
- **Issue:** When template_name doesn't match manifest entries, _load_template constructed a filename but didn't verify it exists, resulting in Jinja2 TemplateNotFound instead of expected ValueError
- **Fix:** Added file existence check after manifest resolution, before Jinja2 Environment load
- **Files modified:** scripts/diagram_generator.py
- **Verification:** test_load_template_missing_raises passes with ValueError
- **Committed in:** 171fe81 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Both auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Template infrastructure ready for Plan 02 (abstraction layers, component-detail differentiation)
- Two-tier resolution tested and working for user template customization
- Deterministic output verified, ready for Plan 03 quality/logging work

## Self-Check: PASSED

All 10 files verified present. Both task commits (35f824b, 171fe81) verified in git log. 82 tests passing.

---
*Phase: 09-diagram-templates-quality*
*Completed: 2026-03-07*
