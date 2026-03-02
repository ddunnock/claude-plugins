---
phase: 03-structural-decomposition-approval-gate
plan: 02
subsystem: decomposition-agent
tags: [decomposition, gap-detection, stale-components, component-proposals, slot-api, agent-pattern]

# Dependency graph
requires:
  - phase: 01-foundation-scaffold
    provides: SlotAPI CRUD with schema validation, atomic writes, journaling
  - phase: 02-requirements-ingestion-pipeline
    provides: Ingested requirements and needs as slot IDs for decomposition input
  - phase: 03-structural-decomposition-approval-gate (plan 01)
    provides: ApprovalGate engine, component-proposal schema, approval-rules.json
provides:
  - DecompositionAgent with data preparation, gap detection, stale component flagging, proposal creation
  - detect_requirement_gaps() for pre-decomposition completeness analysis
  - check_stale_components() for proactive flagging when requirements change
  - Command workflows for decompose and approve user flows
  - Agent definition for Claude's structural analysis
affects: [04-interface-definition, 05-contract-specification, 07-orchestration]

# Tech tracking
tech-stack:
  added: []
  patterns: [data-prep-then-ai-reasoning, proactive-stale-detection, gap-before-decompose]

key-files:
  created:
    - scripts/decomposition_agent.py
    - agents/structural-decomposition.md
    - commands/decompose.md
    - commands/approve.md
    - tests/test_decomposition_agent.py
    - tests/test_decomposition_integration.py
  modified: []

key-decisions:
  - "Agent does NOT call Claude -- it prepares data and formats output; AI reasoning happens in command workflow"
  - "Gap detection runs BEFORE decomposition with severity-based proceed/warn/block decision"
  - "Stale component detection checks at START of decompose workflow, before creating new proposals"
  - "String rationale auto-converted to dict with narrative key for schema compatibility"

patterns-established:
  - "Data-prep-then-AI-reasoning: agent prepares structured data, command workflow invokes Claude, agent validates output"
  - "Proactive stale detection: check accepted components against changed requirements before creating new proposals"
  - "Coverage summary: mapped/unmapped requirement counts with gap marker tracking"

requirements-completed: [STRC-01, STRC-02, STRC-03]

# Metrics
duration: 6min
completed: 2026-03-01
---

# Phase 3 Plan 2: Structural Decomposition Agent Summary

**Decomposition agent with pre-decomposition gap detection, stale component flagging, proposal creation through SlotAPI, and command workflows for decompose/approve flows**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-01T15:19:42Z
- **Completed:** 2026-03-01T15:25:38Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- DecompositionAgent that prepares requirement data, detects gaps, creates validated proposals, and formats coverage summaries
- Stale component detection flags accepted components when their referenced requirements change
- Command workflows document decompose and approve user flows for Claude
- 30 new tests (24 unit + 6 integration) + 147 existing all passing (177 total)

## Task Commits

Each task was committed atomically:

1. **Task 1: Build decomposition agent with gap detection and proposal creation** - `f5163c0` (feat)
2. **Task 2: Create command workflows, agent definition, and integration tests** - `4143dbb` (feat)

## Files Created/Modified
- `scripts/decomposition_agent.py` - DecompositionAgent class, detect_requirement_gaps, check_stale_components, prepare_requirement_data
- `agents/structural-decomposition.md` - Agent definition with Claude instructions for requirement analysis and component grouping
- `commands/decompose.md` - Decompose command workflow: stale check, gap check, prepare, analyze, propose
- `commands/approve.md` - Approve command workflow: batch review, accept/reject/modify, conversational re-proposal loop
- `tests/test_decomposition_agent.py` - 24 unit tests covering gap detection, stale detection, data prep, proposals, formatting, performance
- `tests/test_decomposition_integration.py` - 6 integration tests proving full decompose-approve lifecycle

## Decisions Made
- Agent does NOT call Claude -- it prepares data and formats output; AI reasoning happens in the command workflow (decompose.md)
- Gap detection runs BEFORE decomposition with severity thresholds (none/medium/high) to warn or block
- Stale component detection runs at START of decompose workflow so users see outdated components before creating new proposals
- String rationale auto-converted to dict with narrative key to handle both AI output formats

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test assertions for gap severity thresholds**
- **Found during:** Task 1 (unit tests)
- **Issue:** Tests used only 2-3 requirements making 1 gap exceed 20% threshold, causing "high" instead of expected "medium" severity
- **Fix:** Added more requirements to test data so 1 gap is below 20% threshold
- **Files modified:** tests/test_decomposition_agent.py
- **Verification:** All 24 unit tests pass
- **Committed in:** f5163c0 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Test data adjustment only, no logic changes needed.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Decomposition agent ready for use in actual project decomposition workflows
- Approval gate + decomposition agent integration proven end-to-end
- Pattern established for future agents (data-prep + AI reasoning + structured output)
- All 177 tests passing, no regressions

## Self-Check: PASSED

- All 6 created files found on disk
- Commits f5163c0 and 4143dbb verified in git log
- 177 tests passing (147 existing + 30 new)
