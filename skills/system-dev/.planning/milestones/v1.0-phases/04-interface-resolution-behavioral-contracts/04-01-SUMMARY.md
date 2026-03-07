---
phase: 04-interface-resolution-behavioral-contracts
plan: 01
subsystem: registry
tags: [json-schema, approval-gate, vv-rules, incose, interface-proposal, contract-proposal]

requires:
  - phase: 03-structural-decomposition-approval-gate
    provides: ApprovalGate engine, component-proposal schema, registry CRUD
provides:
  - interface-proposal and contract-proposal slot types registered in registry
  - Generalized ApprovalGate accept handler for any proposal type
  - V&V rules config with INCOSE method defaults
  - Extended interface.json and contract.json with structured fields
affects: [04-02, 04-03, phase-05, phase-06]

tech-stack:
  added: []
  patterns: [generic-field-copy-for-proposal-acceptance, vv-rules-declarative-config]

key-files:
  created:
    - schemas/interface-proposal.json
    - schemas/contract-proposal.json
    - data/vv-rules.json
  modified:
    - schemas/interface.json
    - schemas/contract.json
    - schemas/component.json
    - scripts/registry.py
    - scripts/approval_gate.py
    - scripts/decomposition_agent.py
    - tests/test_approval_gate.py
    - tests/test_schema_validator.py
    - tests/test_decomposition_integration.py

key-decisions:
  - "Generic field-copy in ApprovalGate: SYSTEM_FIELDS and PROPOSAL_ONLY_FIELDS exclusion sets replace hardcoded mapping"
  - "Committed schemas extended with gap_markers, requirement_ids, object rationale to support generic copy passthrough"
  - "component.json updated to accept both parent_requirements (legacy) and requirement_ids (new) for backward compat"
  - "decomposition_agent updated to check requirement_ids before parent_requirements"

patterns-established:
  - "Generic field-copy pattern: proposal acceptance copies all fields except system and proposal-lifecycle fields"
  - "V&V rules as declarative JSON config following approval-rules.json pattern (XCUT-03)"

requirements-completed: [INTF-01, INTF-02, BHVR-01, BHVR-04]

duration: 4min
completed: 2026-03-01
---

# Phase 4 Plan 01: Registry Extension Summary

**Interface-proposal and contract-proposal schemas with generalized ApprovalGate field-copy and INCOSE V&V rules config**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-01T15:59:43Z
- **Completed:** 2026-03-01T16:03:55Z
- **Tasks:** 2
- **Files modified:** 12

## Accomplishments
- Created interface-proposal.json and contract-proposal.json schemas following component-proposal pattern
- Extended interface.json and contract.json with optional structured fields (direction, obligations, vv_assignments, etc.)
- Generalized ApprovalGate._handle_accept to use generic field-copy instead of hardcoded component-specific mapping
- Created vv-rules.json with 8 INCOSE V&V method defaults and ai_with_rationale override policy
- 182 tests passing (5 new + 177 existing), zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create proposal schemas, extend committed schemas, register types** - `e480aab` (feat)
2. **Task 2: Generalize ApprovalGate accept handler and update tests** - `f79cd19` (feat)

## Files Created/Modified
- `schemas/interface-proposal.json` - Interface proposal schema with direction, data_format_schema, error_categories
- `schemas/contract-proposal.json` - Contract proposal schema with obligations, vv_assignments
- `schemas/interface.json` - Extended with direction, data_format_schema, error_categories, rationale, requirement_ids, gap_markers
- `schemas/contract.json` - Extended with structured obligations, vv_assignments, rationale, requirement_ids, gap_markers
- `schemas/component.json` - Extended with requirement_ids, object rationale, gap_markers, relationships for generic copy compat
- `scripts/registry.py` - Registered interface-proposal and contract-proposal in SLOT_TYPE_DIRS and SLOT_ID_PREFIXES
- `scripts/approval_gate.py` - Generalized _handle_accept with SYSTEM_FIELDS/PROPOSAL_ONLY_FIELDS exclusion
- `scripts/decomposition_agent.py` - Updated stale check to use requirement_ids before parent_requirements
- `data/vv-rules.json` - Declarative V&V method defaults per obligation type
- `tests/test_approval_gate.py` - 5 new tests for interface/contract proposal acceptance and field exclusion
- `tests/test_schema_validator.py` - Updated to expect 12 slot types
- `tests/test_decomposition_integration.py` - Updated for requirement_ids field naming

## Decisions Made
- Generic field-copy in ApprovalGate: SYSTEM_FIELDS and PROPOSAL_ONLY_FIELDS exclusion sets replace hardcoded mapping -- enables any proposal type to work without code changes
- Committed schemas extended with gap_markers, requirement_ids, object rationale to support generic copy passthrough from proposals
- component.json accepts both parent_requirements (legacy) and requirement_ids (new) for backward compatibility
- decomposition_agent updated to prefer requirement_ids over parent_requirements

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated test_schema_validator for new slot type count**
- **Found during:** Task 1 (schema creation)
- **Issue:** test_all_slot_types_load hardcoded expectation of 10 types, now 12
- **Fix:** Updated assertion to include contract-proposal and interface-proposal
- **Files modified:** tests/test_schema_validator.py
- **Committed in:** e480aab (Task 1 commit)

**2. [Rule 1 - Bug] Added gap_markers, relationships, requirement_ids to component.json**
- **Found during:** Task 2 (generic field-copy)
- **Issue:** Generic copy passes through gap_markers and relationships from component-proposal but component.json had additionalProperties:false
- **Fix:** Added gap_markers, relationships, requirement_ids as optional fields; made rationale accept string or object
- **Files modified:** schemas/component.json
- **Committed in:** f79cd19 (Task 2 commit)

**3. [Rule 1 - Bug] Added gap_markers to interface.json and contract.json**
- **Found during:** Task 2 (interface-proposal acceptance test)
- **Issue:** Generic copy passes gap_markers from proposal but committed schemas lacked the field
- **Fix:** Added gap_markers as optional array field to both schemas
- **Files modified:** schemas/interface.json, schemas/contract.json
- **Committed in:** f79cd19 (Task 2 commit)

**4. [Rule 1 - Bug] Updated decomposition_agent and integration test for requirement_ids**
- **Found during:** Task 2 (full test suite run)
- **Issue:** check_stale_components looked for parent_requirements; generic copy produces requirement_ids
- **Fix:** Updated to check requirement_ids first, falling back to parent_requirements
- **Files modified:** scripts/decomposition_agent.py, tests/test_decomposition_integration.py
- **Committed in:** f79cd19 (Task 2 commit)

---

**Total deviations:** 4 auto-fixed (3 bug fixes, 1 blocking)
**Impact on plan:** All auto-fixes necessary for correctness with the generic field-copy approach. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Interface-proposal and contract-proposal types ready for 04-02 (interface resolution agent) and 04-03 (behavioral contracts agent)
- ApprovalGate works generically for all proposal types
- V&V rules config ready for contract agent to assign verification methods

---
*Phase: 04-interface-resolution-behavioral-contracts*
*Completed: 2026-03-01*
