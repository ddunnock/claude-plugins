---
phase: 02-requirements-ingestion-pipeline
plan: 01
subsystem: registry
tags: [json-schema, field-mapping, ingestion, gap-markers, sha256]

# Dependency graph
requires:
  - phase: 01-design-registry-core-skill-scaffold
    provides: "SlotAPI, SchemaValidator, SlotStorageEngine, atomic_write, init_workspace"
provides:
  - "5 new ingestion slot schemas (need, requirement, source, assumption, traceability-link)"
  - "SlotAPI.ingest() method for deterministic-ID bulk ingestion"
  - "upstream_schemas.py field mapping layer isolating all upstream-schema knowledge"
  - "Gap marker definitions for CROSS-SKILL-ANALYSIS findings"
  - "Gate status checker resilient to BUG-1/BUG-3"
affects: [02-02, phase-03, phase-05]

# Tech tracking
tech-stack:
  added: [hashlib-sha256]
  patterns: [deterministic-slot-ids, field-mapping-layer, gap-marker-injection, upstream-gate-resilience]

key-files:
  created:
    - schemas/need.json
    - schemas/requirement.json
    - schemas/source.json
    - schemas/assumption.json
    - schemas/traceability-link.json
    - scripts/upstream_schemas.py
    - tests/test_upstream_schemas.py
  modified:
    - scripts/registry.py
    - scripts/init_workspace.py
    - tests/test_schema_validator.py

key-decisions:
  - "Ingested slot IDs use type:upstream-id convention with colon separator (e.g., need:NEED-001)"
  - "SlotAPI.ingest() is a separate method from create() -- does not journal per-item, accepts pre-determined IDs"
  - "content_hash excludes timestamps by default for delta-detection stability"
  - "Gap markers are structured JSON matching CROSS-SKILL-ANALYSIS finding IDs"

patterns-established:
  - "Deterministic slot IDs: ingested slots use prefix:upstream-id, design artifacts use prefix-uuid"
  - "Field mapping isolation: all upstream schema knowledge in upstream_schemas.py"
  - "Explicit KeyError for required fields: never use silent .get() with empty defaults"
  - "Gap marker format: {type, finding_ref, severity, description} on every ingested slot"

requirements-completed: [INGS-01, INGS-02, INGS-04]

# Metrics
duration: 4min
completed: 2026-03-01
---

# Phase 2 Plan 01: Ingestion Slot Types and Upstream Mapping Summary

**5 new JSON schemas for ingestion slot types, SlotAPI.ingest() with conflict detection, upstream field mapping layer with gap markers and BUG-1/BUG-3-resilient gate checker**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-01T14:29:21Z
- **Completed:** 2026-03-01T14:33:02Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Extended Design Registry from 4 to 9 slot types with full Draft 2020-12 JSON schemas
- SlotAPI.ingest() method accepts deterministic IDs, detects conflicts with locally edited slots
- upstream_schemas.py isolates all upstream field mapping, gap markers, and gate status logic
- 24 new tests (93 total) covering field mapping, hashing, gate resilience, provenance

## Task Commits

Each task was committed atomically:

1. **Task 1: Create 5 new slot type schemas and extend registry type maps** - `4bd6770` (feat)
2. **Task 2: Create upstream field mapping module with gap markers and tests** - `df610b6` (feat)

## Files Created/Modified
- `schemas/need.json` - Need slot type schema with provenance and gap_markers
- `schemas/requirement.json` - Requirement slot type schema with derives_from cross-refs
- `schemas/source.json` - Source slot type schema with confidence enum (GAP-4)
- `schemas/assumption.json` - Assumption slot type schema with related_requirements
- `schemas/traceability-link.json` - Traceability link slot type schema with link_type, from_id, to_id
- `scripts/registry.py` - Extended SLOT_TYPE_DIRS/SLOT_ID_PREFIXES (9 entries), added SlotAPI.ingest()
- `scripts/init_workspace.py` - Extended registry_dirs to create 9 subdirectories
- `scripts/upstream_schemas.py` - Field maps, content_hash, gap markers, gate checker, registry loader
- `tests/test_upstream_schemas.py` - 24 tests for field mapping, hashing, gates, provenance, slot IDs
- `tests/test_schema_validator.py` - Updated slot type count assertion from 4 to 9

## Decisions Made
- Ingested slot IDs use colon separator (need:NEED-001) -- deterministic for delta detection
- SlotAPI.ingest() separate from create() to avoid journaling per-item and to accept pre-determined IDs
- content_hash excludes timestamps by default so re-ingestion only detects content changes
- Gap markers reference CROSS-SKILL-ANALYSIS finding IDs for machine-readable downstream processing

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test_all_four_slot_types_load assertion**
- **Found during:** Task 1 (extending registry type maps)
- **Issue:** Existing test asserted exactly 4 supported slot types; now there are 9
- **Fix:** Updated assertion to expect all 9 types in sorted order
- **Files modified:** tests/test_schema_validator.py
- **Verification:** All 69 existing tests pass
- **Committed in:** 4bd6770 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary update to existing test that hard-coded the slot type count. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- 9 slot types with schemas ready for ingestion engine (02-02-PLAN.md)
- Field mapping layer ready to translate upstream registries to slot content
- Gap markers defined and ready for injection during ingestion
- SlotAPI.ingest() ready for bulk ingestion with conflict detection

---
*Phase: 02-requirements-ingestion-pipeline*
*Completed: 2026-03-01*
