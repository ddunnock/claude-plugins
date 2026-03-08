---
phase: 06b-view-integration-fix
plan: 01
subsystem: view-assembly
tags: [skill-md, view-command, init-workspace, view-specs]

requires:
  - phase: 06-view-assembly-core
    provides: view_assembler.py with load_view_spec(), commands/view.md, init_workspace.py
provides:
  - "/system-dev:view routable from SKILL.md command table"
  - "File-based view spec loading via load_view_spec() with schemas_dir"
  - ".system-dev/view-specs/ directory created during workspace init"
affects: [06b-02, 07-view-quality-handoff]

tech-stack:
  added: []
  patterns:
    - "3-way spec resolution: built-in name, file path, ad-hoc pattern"

key-files:
  created: []
  modified:
    - SKILL.md
    - commands/view.md
    - scripts/init_workspace.py
    - tests/test_init_workspace.py

key-decisions:
  - "File paths detected by .json suffix or / character in spec_name_or_pattern"
  - "view-specs/ added to registry_dirs list alongside registry/ subdirs"

patterns-established:
  - "File-based spec detection: ends with .json or contains / triggers load_view_spec()"

requirements-completed: []

duration: 1min
completed: 2026-03-03
---

# Phase 6b Plan 01: View Integration Fix - Command Routing & File-Based Specs Summary

**Wired /system-dev:view into SKILL.md, added 3-way spec resolution (built-in/file/ad-hoc) to view command, and created view-specs/ directory in workspace init**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-03T23:11:25Z
- **Completed:** 2026-03-03T23:12:54Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- /system-dev:view command is now discoverable and routable from SKILL.md command table
- commands/view.md workflow branches on input type: built-in spec name, file path (with schema validation), or ad-hoc scope pattern
- init_workspace() creates .system-dev/view-specs/ directory for user-authored view specifications
- 3 new tests verify view-specs/ creation; all 379 tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Add /system-dev:view to SKILL.md command table** - `f22828b` (feat)
2. **Task 2 RED: Failing tests for view-specs** - `444d0bd` (test)
3. **Task 2 GREEN: File-based spec branch and view-specs directory** - `18bd3d7` (feat)

## Files Created/Modified
- `SKILL.md` - Added /system-dev:view row to command table
- `commands/view.md` - 3-way spec resolution, file-based specs section, updated invocation docs
- `scripts/init_workspace.py` - Added view-specs/ to registry_dirs list
- `tests/test_init_workspace.py` - 3 new tests for view-specs directory creation

## Decisions Made
- File paths detected by `.json` suffix or `/` character in spec_name_or_pattern argument
- view-specs/ added to the existing registry_dirs list (despite the variable name, it holds all .system-dev/ subdirectories)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 06b-02 can proceed: schema hardening (slot required fields, format_version) and unlinked documentation
- All integration gaps from plan 01 scope are closed

## Self-Check: PASSED

All files exist, all commits found, all content checks pass.

---
*Phase: 06b-view-integration-fix*
*Completed: 2026-03-03*
