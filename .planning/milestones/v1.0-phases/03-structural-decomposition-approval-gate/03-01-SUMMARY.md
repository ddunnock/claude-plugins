---
phase: 03-structural-decomposition-approval-gate
plan: 01
subsystem: approval-gate
tags: [approval-gate, state-machine, json-schema, slot-api, proposals]

# Dependency graph
requires:
  - phase: 01-foundation-scaffold
    provides: SlotAPI CRUD with schema validation, atomic writes, journaling
  - phase: 02-requirements-ingestion-pipeline
    provides: Ingested requirements as slot IDs for proposal requirement_ids
provides:
  - component-proposal slot type with full JSON Schema
  - Declarative approval-rules.json state-transition config
  - Generic ApprovalGate engine (accept/reject/modify/batch/pending)
  - Registered component-proposal type in SlotAPI
affects: [03-02-structural-decomposition, 04-interface-definition, 05-contract-specification]

# Tech tracking
tech-stack:
  added: []
  patterns: [declarative-state-machine, atomic-ordering-create-before-update, generic-proposal-gate]

key-files:
  created:
    - schemas/component-proposal.json
    - data/approval-rules.json
    - scripts/approval_gate.py
    - tests/test_approval_gate.py
  modified:
    - scripts/registry.py
    - scripts/init_workspace.py
    - tests/test_schema_validator.py

key-decisions:
  - "Accept creates committed slot BEFORE updating proposal for atomic ordering (Pitfall 2 prevention)"
  - "Gate is generic: uses proposal_type parameter, derives committed type by stripping '-proposal' suffix"
  - "Shallow merge for modify operation -- does not allow overwriting system fields"
  - "batch_decide stops on first error and returns partial results for caller control"

patterns-established:
  - "Declarative state machine: transitions driven by JSON config, not code branches"
  - "Proposal-to-committed convention: strip '-proposal' suffix for committed slot type"
  - "Atomic ordering: create downstream artifact before updating source proposal"

requirements-completed: [APPR-01, APPR-02, APPR-03, APPR-04]

# Metrics
duration: 3min
completed: 2026-03-01
---

# Phase 3 Plan 1: Approval Gate Engine Summary

**Generic approval gate with declarative JSON state transitions, component-proposal schema, and atomic accept/reject/modify operations through SlotAPI**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-01T15:14:11Z
- **Completed:** 2026-03-01T15:17:16Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Component-proposal schema with proposal-specific fields (rationale, gap_markers, relationships, decision)
- Declarative approval-rules.json with 4 states and 6 transitions driving all gate logic
- Generic ApprovalGate engine that works with any proposal type, no decomposition coupling
- 23 new tests + 124 existing all passing (147 total)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create component-proposal schema, approval-rules config, and register new slot type** - `e72cb69` (feat)
2. **Task 2: Build generic approval gate engine and comprehensive tests** - `1857416` (feat)

## Files Created/Modified
- `schemas/component-proposal.json` - JSON Schema for component-proposal slot type with decision, rationale, gap_markers fields
- `data/approval-rules.json` - Declarative state-transition config (4 states, 6 transitions, required fields, side effects)
- `scripts/approval_gate.py` - ApprovalGate class with decide/batch_decide/get_pending, plus load_approval_rules and validate_transition
- `tests/test_approval_gate.py` - 23 tests covering all operations, batch processing, atomic ordering, performance
- `scripts/registry.py` - Added component-proposal to SLOT_TYPE_DIRS and SLOT_ID_PREFIXES
- `scripts/init_workspace.py` - Added component-proposals to registry_dirs
- `tests/test_schema_validator.py` - Updated slot type count from 9 to 10

## Decisions Made
- Accept creates committed slot BEFORE updating proposal -- ensures committed component exists even if proposal update fails (Pitfall 2 from research)
- Gate derives committed type by convention: strip "-proposal" suffix (component-proposal -> component)
- Modify applies shallow merge on proposal fields, explicitly blocking system field overwrites
- batch_decide stops on first error and returns partial results, giving callers control over error handling
- re_propose action clears all decision fields back to null, resetting proposal to initial state

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Approval gate ready for use by decomposition agent in plan 03-02
- Component-proposal slot type registered and validated
- All 147 tests passing, no regressions

## Self-Check: PASSED

- All 4 created files found on disk
- Commits e72cb69 and 1857416 verified in git log
- 147 tests passing (124 existing + 23 new)

---
*Phase: 03-structural-decomposition-approval-gate*
*Completed: 2026-03-01*
