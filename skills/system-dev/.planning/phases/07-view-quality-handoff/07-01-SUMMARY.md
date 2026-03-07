---
phase: 07-view-quality-handoff
plan: 01
subsystem: view-assembly
tags: [ranking, density, determinism, content-hash, performance, sha256]

# Dependency graph
requires:
  - phase: 06-view-assembly-core
    provides: view_assembler.py with assemble_view(), capture_snapshot(), _organize_hierarchically()
  - phase: 06b-view-integration-fix
    provides: format_version "1.0", tightened slot schema, view-spec validation
provides:
  - _compute_density_scores() for relationship density ranking
  - _rank_slots() with density/alphabetical/none methods
  - Content-hash deterministic snapshot_id (SHA-256)
  - Performance instrumentation (elapsed_ms in metadata)
  - Extended view.json schema with edges and metadata fields
  - Optional ranking field in view-spec.json
  - format_version bumped to "1.1"
affects: [07-02-handoff-logging, 08-diagram-generation]

# Tech tracking
tech-stack:
  added: [hashlib, time.perf_counter]
  patterns: [density-scoring-from-full-snapshot, content-hash-ids, stable-sort-ranking]

key-files:
  created: []
  modified:
    - scripts/view_assembler.py
    - schemas/view.json
    - schemas/view-spec.json
    - tests/test_view_assembler.py

key-decisions:
  - "SHA-256 truncated to 16 hex chars for content-hash snapshot_id"
  - "Density scores computed from full snapshot, not just matched view slots (Pitfall 4)"
  - "Ranking tiebreak: density desc, version desc, name asc"
  - "Edges array added as empty placeholder for Plan 02 to populate"
  - "Traceability-link density test uses manual snapshot (avoids slot_id pattern mismatch)"

patterns-established:
  - "Density scoring: separate {slot_id: score} dict, never mutate snapshot"
  - "Ranking method: per-spec override via optional ranking field, default density"
  - "Content-hash: json.dumps(sort_keys=True, separators=(',',':')) for canonical serialization"

requirements-completed: [VIEW-03, VIEW-09, VIEW-12]

# Metrics
duration: 4min
completed: 2026-03-07
---

# Phase 7 Plan 01: Ranking & Determinism Summary

**Density-based relevance ranking with content-hash determinism and performance instrumentation for view assembler**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-07T16:19:36Z
- **Completed:** 2026-03-07T16:24:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Relationship density ranking sorts hub components (most connections) to top of views
- Content-hash snapshot_id guarantees deterministic output for same registry state
- Assembly of 100-slot registries completes well under 500ms target
- Extended schemas ready for Plan 02 handoff format (edges, metadata)
- 19 new tests covering ranking, determinism, and performance

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend schemas and add ranking + determinism to view assembler** - `e66c5b1` (feat)
2. **Task 2: Add tests for ranking, determinism, and performance** - `8f943c4` (test)

## Files Created/Modified
- `scripts/view_assembler.py` - Added _compute_density_scores(), _rank_slots(), content-hash snapshot_id, timing/metadata in assemble_view()
- `schemas/view.json` - Added edges array and metadata object to required fields
- `schemas/view-spec.json` - Added optional ranking field (density/alphabetical/none)
- `tests/test_view_assembler.py` - 19 new tests in TestRanking, TestDeterminism, TestPerformance classes

## Decisions Made
- SHA-256 truncated to 16 hex chars for snapshot_id (sufficient uniqueness within a project)
- Density scores computed from FULL snapshot (not just matched view slots) so same component gets same rank regardless of view
- Ranking tiebreak order: density descending, version descending, name ascending
- Edges array included as empty placeholder -- Plan 02 will populate via _extract_edges()
- Traceability-link density test uses manually constructed snapshot to avoid pre-existing slot_id pattern mismatch (trace- vs trace:)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Traceability-link test adjusted for schema compatibility**
- **Found during:** Task 2 (TDD test writing)
- **Issue:** Traceability-link schema requires slot_id matching `^trace:.+$` but registry generates `trace-{uuid}`. Creating traceability-links via API fails validation.
- **Fix:** Used manually constructed snapshot dict for traceability-link density test instead of API creation
- **Files modified:** tests/test_view_assembler.py
- **Verification:** All 19 new tests pass
- **Committed in:** 8f943c4 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug workaround)
**Impact on plan:** Test approach adjusted to work around pre-existing schema inconsistency. No scope creep.

## Issues Encountered
- Pre-existing inconsistency: traceability-link schema requires `^trace:.+$` pattern but registry generates `trace-{uuid}`. Logged as pre-existing -- not in scope for this plan.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Ranking and determinism foundation complete for Plan 02
- Plan 02 can implement _extract_edges() to populate the edges array
- Plan 02 can add structured logging using the existing logger
- Metadata object in output ready for additional fields

---
*Phase: 07-view-quality-handoff*
*Completed: 2026-03-07*
