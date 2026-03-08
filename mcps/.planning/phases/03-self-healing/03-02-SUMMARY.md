---
phase: 03-self-healing
plan: 02
subsystem: server
tags: [mcp, tool-wiring, healData, integration-tests, auto-heal, suggest-mode]

# Dependency graph
requires:
  - phase: 03-self-healing
    provides: healData function, HealFix/HealResult types, coercion helpers
  - phase: 02-schema-registry
    provides: SchemaRegistry, format handlers, atomicWrite, validatePath
provides:
  - Working sv_heal MCP tool with auto and suggest modes
  - Integration test suite for sv_heal covering all modes and error cases
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [tool-handler-heal-pattern, suggest-vs-auto-dispatch]

key-files:
  created:
    - schema-validator/tests/server/tools-phase3.test.ts
  modified:
    - schema-validator/src/server/tools.ts
    - schema-validator/src/schemas/healer.ts

key-decisions:
  - "healData applies missing defaults after successful re-validation (not just on initial success)"
  - "Auto mode writes to disk only when applied fixes exist; already-valid files skip disk write"
  - "Suggest mode returns applied fixes as suggestions array without any disk modification"

patterns-established:
  - "sv_heal follows same error pattern as sv_validate: PathValidationError, FormatError, SchemaRegistryError, generic catch"
  - "Heal results are success responses (not isError), even partial heals"

requirements-completed: [HEAL-01, HEAL-02]

# Metrics
duration: 3min
completed: 2026-03-08
---

# Phase 3 Plan 2: sv_heal Tool Wiring Summary

**sv_heal MCP tool replacing notImplemented stub with auto/suggest heal modes, 9 integration tests, and healData default-application bug fix**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-08T21:08:30Z
- **Completed:** 2026-03-08T21:12:00Z
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments
- Replaced sv_heal notImplemented stub with full handler using healData engine
- Auto mode reads malformed files, applies fixes via healData, writes healed output with atomicWrite
- Suggest mode returns fix suggestions without modifying files on disk
- Already-valid files return clean response with no disk write
- 9 integration tests covering auto mode (fixable, valid, partial, unknown fields), suggest mode, and error cases
- 135 total tests pass with zero regressions across all phases

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire sv_heal tool handler and add integration tests** - `e0b045f` (feat)

## Files Created/Modified
- `schema-validator/src/server/tools.ts` - Replaced sv_heal stub with real handler supporting auto/suggest modes
- `schema-validator/src/schemas/healer.ts` - Fixed missing default application after re-validation
- `schema-validator/tests/server/tools-phase3.test.ts` - 9 integration tests for sv_heal tool

## Decisions Made
- healData should apply missing defaults after successful re-validation, not just on initial success path. When fixes are applied and re-validation succeeds, defaulted fields were being missed.
- Auto mode skips disk write when no fixes are applied (already-valid case), avoiding unnecessary I/O.
- Suggest mode returns `{ suggestions, remaining }` shape distinct from auto mode's `{ healed, data, applied, remaining }`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed healData not applying defaults after re-validation**
- **Found during:** Task 1 (integration test for auto mode with missing defaults)
- **Issue:** After applying coercion fixes, healData re-validates successfully but fields with ZodDefault wrappers that were missing from raw data were not filled in. The applyMissingDefaults logic only ran on the initial safeParse success path.
- **Fix:** Added applyMissingDefaults call after successful re-validation, same as initial success path
- **Files modified:** schema-validator/src/schemas/healer.ts
- **Verification:** Integration test "fixes wrong types and missing defaults, writes healed file" passes
- **Committed in:** e0b045f

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix necessary for correctness -- without it, auto-healed files would be missing default values. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 complete: self-healing engine (03-01) and tool wiring (03-02) both done
- All 135 tests pass across all 3 phases
- sv_heal is available to Claude Code skills for automatic file correction

---
*Phase: 03-self-healing*
*Completed: 2026-03-08*
