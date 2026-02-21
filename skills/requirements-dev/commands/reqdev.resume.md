---
name: reqdev:resume
description: Resume an interrupted requirements development session from the last known state, including mid-block and mid-type-pass positions
---

# /reqdev:resume -- Resume Interrupted Session

## Step 1: Load State

```bash
uv run scripts/update_state.py --state .requirements-dev show
```

If no state file exists:
```
No active session found. Run /reqdev:init to start a new session.
```

## Step 2: Identify Resume Point

Read `state.json` to determine exact position:

```bash
cat .requirements-dev/state.json
```

Key fields:
- `current_phase`: which phase was active
- `progress.current_block`: which block was being worked on (null if between blocks)
- `progress.current_type_pass`: which type pass was active (null if between passes)
- `progress.type_pass_order`: fixed ordering `["functional", "performance", "interface", "constraint", "quality"]`
- `progress.requirements_in_draft`: list of quality-checked but unregistered requirement IDs

## Step 3: Display Resume Summary

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

[Use the appropriate pattern based on state:]
```

**Pattern A -- Between blocks:**
```
All type passes complete for [previous block].
Next block: [block-name]. Ready to begin functional requirements.
```

**Pattern B -- Mid-type-pass:**
```
Block: [block-name]
Completed types: [list]
Current type: [type] (in progress)
[N] requirements registered for this block so far.
```

**Pattern C -- Draft requirements pending:**
```
Block: [block-name], Type: [type]
[N] requirements in draft (passed quality check, not yet registered):
  - [REQ-xxx]: [first 60 chars of statement]...
  - [REQ-yyy]: [first 60 chars of statement]...
These need confirmation before proceeding.
```

**Pattern D -- Needs phase:**
```
[N] needs approved. [N] blocks have completed needs formalization.
[N] blocks remaining.
```

**Pattern E -- Init phase incomplete:**
```
Initialization started but not complete. Re-run /reqdev:init.
```

```
-------------------------------------------------------------------

Ready to continue?
  [A] Continue from where we left off
  [B] Show full status dashboard (/reqdev:status)
  [C] Start a different phase

===================================================================
```

## Step 4: Load Context for Resume

Based on current phase, read relevant artifacts:

| Phase | Artifacts to Load |
|-------|-------------------|
| init | (state only) |
| needs | `needs_registry.json`, `ingestion.json` (block list) |
| requirements | `needs_registry.json`, `requirements_registry.json`, `traceability_registry.json` |
| deliver | All registries + any existing deliverable drafts |

Read each artifact and provide a brief context summary.

## Step 5: Handle Draft Requirements

**CRITICAL:** When `progress.requirements_in_draft` is non-empty, handle drafts before continuing.

Read each draft requirement from `requirements_registry.json`:

```
===================================================================
DRAFT REQUIREMENTS TO RESOLVE
===================================================================

[For each draft REQ-xxx]:
  REQ-xxx: "[statement]"
    Type: [type]  Priority: [priority]  Block: [source-block]
    Quality check: Passed (Tier 1)

  Action:
    [A] Register now (with parent need assignment)
    [B] Discard (remove from registry)
===================================================================
```

For registrations:
```bash
uv run scripts/requirement_tracker.py --workspace .requirements-dev register \
  --id <REQ-xxx> --parent-need <NEED-xxx>
```

For discards:
```bash
uv run scripts/requirement_tracker.py --workspace .requirements-dev withdraw \
  --id <REQ-xxx> --rationale "Discarded during resume"
```

After resolving all drafts, clear the list:
```bash
uv run scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'
```

## Step 6: Continue

Based on user selection:

- **Continue**: Invoke the appropriate command for the current phase. If in requirements phase mid-type-pass, `/reqdev:requirements` detects `progress.current_block` and `progress.current_type_pass` and skips completed passes.
- **Dashboard**: Run `/reqdev:status`
- **Different phase**: Ask which phase; verify gate prerequisites are met using:
  ```bash
  uv run scripts/update_state.py --state .requirements-dev check-gate <phase>
  ```
  Warn if prerequisites are not met.
