---
phase: 03-self-healing
plan: 01
subsystem: schemas
tags: [zod, healing, coercion, safeParse, TDD]

# Dependency graph
requires:
  - phase: 02-schema-registry
    provides: SchemaRegistry, RegisteredSchema, ZodTypeAny schemas, types.ts
provides:
  - healData function for mapping Zod validation issues to structured fix objects
  - HealFix and HealResult types for fix representation
  - Conservative coercion helpers (string->number, string->boolean, number/boolean->string)
  - Schema default extraction via Zod _def internals
  - Nested value get/set utilities with intermediate object creation
affects: [03-02-sv-heal-tool]

# Tech tracking
tech-stack:
  added: []
  patterns: [issue-to-fix-mapping, raw-data-mutation, zod-def-introspection]

key-files:
  created:
    - schema-validator/src/schemas/healer.ts
    - schema-validator/tests/schemas/healer.test.ts
  modified:
    - schema-validator/src/schemas/types.ts

key-decisions:
  - "Proactively apply ZodDefault values to raw data even when safeParse succeeds (Zod applies defaults internally but raw data stays incomplete)"
  - "Use (any) cast for ZodObject.shape access since ZodTypeAny does not expose shape property in types"

patterns-established:
  - "Issue-to-fix mapping: ZodIssue.code determines fix strategy (invalid_type -> coerce/default, invalid_enum_value -> manual)"
  - "Raw data mutation: fixes applied directly to raw parsed data, never Zod validated output, preserving unknown fields"
  - "Schema introspection via _def: unwrap ZodDefault/ZodOptional/ZodNullable to reach structural types"

requirements-completed: [HEAL-01, HEAL-02]

# Metrics
duration: 3min
completed: 2026-03-08
---

# Phase 3 Plan 1: Healing Engine Core Summary

**healData function with conservative type coercion, ZodDefault extraction, and 14-case TDD unit test suite**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-08T21:02:39Z
- **Completed:** 2026-03-08T21:06:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 3

## Accomplishments
- Built healData() that maps Zod safeParse issues to structured HealFix objects with coerce/default/manual strategies
- Conservative coercion: string->number (Number, reject NaN), string "true"/"false"->boolean (exact match only), number/boolean->string
- ZodDefault extraction via _def internals with nested schema walking
- Unknown field preservation by mutating raw data instead of using Zod's validated output
- Full TDD cycle: 14 failing tests written first, then implementation to pass all

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing tests** - `bbfd4ae` (test)
2. **Task 1 GREEN: healData implementation + types re-export** - `4f471c0` (feat)

## Files Created/Modified
- `schema-validator/src/schemas/healer.ts` - healData function, HealFix/HealResult types, coercion helpers, nested value utilities
- `schema-validator/src/schemas/types.ts` - Re-exported HealFix and HealResult types for external consumers
- `schema-validator/tests/schemas/healer.test.ts` - 14 unit tests covering all fix strategies

## Decisions Made
- Proactively apply ZodDefault values even when safeParse succeeds: Zod applies defaults internally during parse but the raw data object remains incomplete. The healing engine detects missing-but-defaulted fields and fills them in.
- Used `(any)` cast for ZodObject.shape access: ZodTypeAny does not expose the shape property in its type definition, but it exists at runtime for ZodObject instances.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed ZodDefault not detected for valid-but-incomplete data**
- **Found during:** Task 1 GREEN phase
- **Issue:** Zod safeParse succeeds when all missing fields have ZodDefault wrappers, so healData short-circuited without applying defaults to raw data
- **Fix:** Added applyMissingDefaults() that walks ZodObject shape to find missing fields with ZodDefault wrappers, applies them even on safeParse success
- **Files modified:** schema-validator/src/schemas/healer.ts
- **Verification:** Test "applies ZodDefault value for missing required field" passes
- **Committed in:** 4f471c0

**2. [Rule 1 - Bug] Fixed TypeScript compilation errors for ZodTypeAny shape access**
- **Found during:** Task 1 GREEN phase (tsc --noEmit)
- **Issue:** TypeScript errors for .shape property on ZodTypeAny and strict index type checks on path arrays
- **Fix:** Added (any) casts for .shape access, non-null assertions for path indexing
- **Files modified:** schema-validator/src/schemas/healer.ts
- **Verification:** tsc --noEmit passes cleanly
- **Committed in:** 4f471c0

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes necessary for correctness and type safety. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- healData is ready for sv_heal tool wiring in plan 03-02
- HealFix/HealResult types exported and available for tool response construction
- Full test suite (126 tests) green with zero regressions

---
*Phase: 03-self-healing*
*Completed: 2026-03-08*
