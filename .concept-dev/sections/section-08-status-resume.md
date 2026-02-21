Now I have all the context needed. Let me produce the section content.

# Section 08: Status and Resume Commands

## Overview

This section implements two command prompts -- `/reqdev:status` and `/reqdev:resume` -- that give users a dashboard view of their requirements development session and allow them to resume interrupted sessions at the exact point they left off. These commands are purely conversational (Markdown command files that instruct Claude); no new Python scripts are needed beyond what section-02 (state management) already provides.

## Dependencies

- **section-01-plugin-scaffolding**: Plugin directory structure must exist (specifically `skills/requirements-dev/commands/`)
- **section-02-state-management**: `update_state.py` with its `show` and `sync-counts` subcommands, and the `state.json` template with the `progress` section (`current_block`, `current_type_pass`, `requirements_in_draft`)

No other sections are required. The status and resume commands read existing registries and state but do not depend on the tracker scripts themselves -- they read JSON files directly or call `update_state.py show`.

## Files to Create

1. `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.status.md`
2. `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.resume.md`

## Tests

Tests for this section live in `tests/test_integration.py` and focus on the resume flow. The status command is purely display (no mutations) and is validated through manual inspection rather than unit tests.

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_integration.py`**

Add the following test stubs to the integration test file (this file may already exist from section-07; append these if so):

```python
# --- Resume flow ---

def test_resume_after_need_registration(tmp_workspace):
    """Interrupt after need registration, resume, state shows correct position.

    Setup: Create workspace with state.json showing current_phase='needs',
    gates.init=True, needs_registry with 3 approved needs, progress.current_block=null.
    Assert: Reading state shows 'needs' phase, counts.needs_approved=3,
    and resume point is 'needs formalization complete for registered needs'.
    """

def test_resume_mid_type_pass(tmp_workspace):
    """Interrupt mid-type-pass, resume, state shows current_block and current_type_pass.

    Setup: Create workspace with state.json showing current_phase='requirements',
    progress.current_block='block-api-gateway',
    progress.current_type_pass='performance',
    counts.requirements_registered=5.
    Assert: Reading state shows exact position: block name and type pass.
    The resume point message includes 'Block: block-api-gateway, Type: performance'.
    """

def test_resume_preserves_requirements_in_draft(tmp_workspace):
    """requirements_in_draft preserved across interruption.

    Setup: Create workspace with state.json showing
    progress.requirements_in_draft=['REQ-006', 'REQ-007'],
    requirements_registry containing REQ-006 and REQ-007 with status='draft'.
    Assert: State correctly reports 2 requirements in draft.
    Resume flow should present these for confirmation rather than losing them.
    """
```

**Shared fixture** (in `conftest.py` or inline):

```python
import json
import os
import pytest

@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a minimal .requirements-dev workspace for testing."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    return ws
```

The tests validate state reading and interpretation. They create state.json files with specific progress values, then call `update_state.py show` (via subprocess) and verify the output contains the expected position information.

## Implementation Details

### Command: `/reqdev:status`

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.status.md`

This command file follows the same pattern as concept-dev's `concept.status.md`. It instructs Claude to:

**Frontmatter:**

```yaml
---
name: reqdev:status
description: Display session status dashboard showing current phase, block progress, requirement counts, traceability coverage, TBD/TBR counts, and quality check pass rate
---
```

**Procedure:**

1. **Load State** -- Run `update_state.py --state .requirements-dev/state.json show`. If no state file exists, inform the user: "No active session. Run `/reqdev:init` to start."

2. **Sync Counts** -- Run `update_state.py --state .requirements-dev/state.json sync-counts` to ensure counts reflect current registry contents.

3. **Load Registry Summaries** -- If registries exist, read `needs_registry.json`, `requirements_registry.json`, and `traceability_registry.json` to extract summary statistics.

4. **Display Dashboard** -- Render a formatted dashboard:

```
===================================================================
REQUIREMENTS DEVELOPMENT STATUS
===================================================================

Session: [id]
Last Updated: [timestamp]

-------------------------------------------------------------------
PHASES
-------------------------------------------------------------------

  [X] 1. Init              COMPLETED   [date]
  [>] 2. Needs             IN PROGRESS
  [ ] 3. Requirements      NOT STARTED
  [ ] 4. Deliver           NOT STARTED

Current Phase: [phase name]
Gate Status: [passed / pending]

-------------------------------------------------------------------
BLOCK PROGRESS
-------------------------------------------------------------------

  Block: [block-name]
    Types completed: [list, e.g., functional, performance]
    Types remaining: [list, e.g., interface, constraint, quality]
    Requirements: [N] registered

  Block: [block-name]
    [not started]

  ...

-------------------------------------------------------------------
REQUIREMENT COUNTS
-------------------------------------------------------------------

  Needs:        Total=[N]  Approved=[N]  Deferred=[N]
  Requirements: Total=[N]  Registered=[N]  Baselined=[N]  Withdrawn=[N]
  TBD open: [N]    TBR open: [N]

-------------------------------------------------------------------
TRACEABILITY
-------------------------------------------------------------------

  Links: [N]
  Coverage: [N]% of needs have derived requirements

-------------------------------------------------------------------
DECOMPOSITION
-------------------------------------------------------------------

  Levels active: [list or "none"]
  Max level: [N]

===================================================================
Next action: [suggested command based on current state]
===================================================================
```

5. **Suggest Next Action** -- Based on current state:

| State | Suggestion |
|-------|-----------|
| No session | `/reqdev:init` |
| Init complete, no needs | `/reqdev:needs` |
| Needs complete | `/reqdev:requirements` |
| Requirements in progress | "Continue with `/reqdev:requirements` or `/reqdev:resume`" |
| Requirements complete | `/reqdev:deliver` |
| Delivered, wants validation | `/reqdev:validate` |
| Delivered, wants research | `/reqdev:research` |
| Baselined, wants decomposition | `/reqdev:decompose` |
| All phases complete | "Requirements development complete!" |

### Command: `/reqdev:resume`

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.resume.md`

This command is more complex than status because it must reconstruct the exact session position from `state.json`'s `progress` section and present actionable resumption options.

**Frontmatter:**

```yaml
---
name: reqdev:resume
description: Resume an interrupted requirements development session from the last known state, including mid-block and mid-type-pass positions
---
```

**Procedure:**

1. **Load State** -- Run `update_state.py --state .requirements-dev/state.json show`. If no state file exists: "No active session found. Run `/reqdev:init` to start a new session."

2. **Identify Resume Point** -- Read the `progress` section of `state.json` to determine exact position. The key fields are:
   - `current_block`: which block was being worked on (null if between blocks or not yet started)
   - `current_type_pass`: which requirement type pass was active (null if between passes; one of "functional", "performance", "interface", "constraint", "quality")
   - `type_pass_order`: the fixed ordering of type passes
   - `requirements_in_draft`: list of requirement IDs that passed quality checking but were not yet registered when the session was interrupted

3. **Display Resume Summary** -- Show a concise summary of where the session left off:

```
===================================================================
RESUMING SESSION
===================================================================

Session: [id]
Last Updated: [timestamp]

Current Phase: [phase name]

Progress Summary:
  [N] needs approved across [N] blocks
  [N] requirements registered ([N] baselined, [N] withdrawn)
  Traceability coverage: [N]%

-------------------------------------------------------------------
RESUMPTION POINT:
-------------------------------------------------------------------

[One of the following patterns based on state:]

Pattern A (between blocks):
  "All type passes complete for [previous block].
   Next block: [block-name]. Ready to begin functional requirements."

Pattern B (mid-type-pass):
  "Block: [block-name]
   Completed types: [list]
   Current type: [type] (in progress)
   [N] requirements registered for this block so far."

Pattern C (draft requirements pending):
  "Block: [block-name], Type: [type]
   [N] requirements in draft (passed quality check, not yet registered):
     - [REQ-xxx]: [first 60 chars of statement]...
     - [REQ-yyy]: [first 60 chars of statement]...
   These need confirmation before proceeding."

Pattern D (needs phase):
  "[N] needs approved. [N] blocks have completed needs formalization.
   [N] blocks remaining."

Pattern E (init phase):
  "Initialization started but not complete. Re-run /reqdev:init."

-------------------------------------------------------------------

Ready to continue?
  [A] Continue from where we left off
  [B] Show full status dashboard (/reqdev:status)
  [C] Start a different phase

===================================================================
```

4. **Load Context for Resume** -- Based on current phase, read relevant artifacts:

| Phase | Artifacts to Load |
|-------|-------------------|
| init | (state only) |
| needs | needs_registry.json, ingestion.json (block list) |
| requirements | needs_registry.json, requirements_registry.json, traceability_registry.json |
| deliver | All registries + any existing deliverable drafts |

Read each artifact and provide a brief context summary so the user has working memory of what was accomplished.

5. **Handle Draft Requirements** -- This is the critical resume feature that distinguishes this from concept-dev's simpler resume. When `requirements_in_draft` is non-empty:
   - Read each draft requirement from `requirements_registry.json`
   - Present them to the user with their quality check results
   - Ask the user to confirm registration (via `requirement_tracker.py register`) or discard
   - Only after drafts are resolved does the normal flow continue

6. **Continue** -- Based on user selection:
   - **Continue**: Invoke the appropriate command for the current phase. If mid-type-pass, the `/reqdev:requirements` command should detect `progress.current_block` and `progress.current_type_pass` and skip completed passes.
   - **Dashboard**: Run `/reqdev:status`
   - **Different phase**: Ask which phase; warn about skipping if prerequisites are not met (check gates)

### Resumption Behavior by Phase

| Phase | Resumption Behavior |
|-------|-------------------|
| init (in_progress) | Re-run `/reqdev:init`; it detects existing workspace and does not overwrite |
| needs (in_progress) | Show which blocks have completed needs; continue from next block |
| needs (gate pending) | Present needs set for final block approval |
| requirements (in_progress) | Identify current_block + current_type_pass; handle drafts; continue |
| requirements (gate pending) | Present block requirements for final approval |
| deliver (in_progress) | Check which deliverables are generated; continue from next |
| deliver (gate pending) | Present deliverables for final approval and baselining |

### Key Design Decisions

1. **No new Python scripts**: Both commands are purely command prompt files. They rely on `update_state.py show` for state reading and direct JSON file reads (which Claude can do natively) for registry summaries. This keeps the implementation minimal.

2. **Draft requirement recovery**: The `requirements_in_draft` field in state.json is the mechanism for preventing data loss on interruption. When the `/reqdev:requirements` command flow creates a requirement (adds it to the registry with status "draft") and runs quality checks, the requirement ID is appended to `requirements_in_draft`. It is removed from this list only after successful registration. On resume, any IDs remaining in this list represent work that was quality-checked but not finalized.

3. **Granular position tracking**: Unlike concept-dev which tracks only phase-level progress, requirements-dev tracks block-level and type-pass-level position. This is necessary because the requirements phase can span many blocks with 5 type passes each -- losing position would mean significant rework.

4. **State mutations during resume**: The resume command itself does not mutate state. It only reads and displays. State mutations happen when the user chooses to continue and the appropriate phase command takes over.

## Implementation Notes

- Both command files use `--state .requirements-dev` (directory form) consistently.
- Status suggestion table includes all 9 next-action rows from the plan.
- 3 resume flow integration tests added to `test_integration.py` (total: 11 integration tests, 125 overall).
- Resume patterns A and E are purely conversational (no code path to test); patterns B, C, D are covered by integration tests.
- `requirements_in_draft` population is done by the `/reqdev:requirements` command prompt, not by Python scripts — this is by design.
- Code review fixed a vacuously true assertion that would never fail due to `or "Phase" in summary` always being true.