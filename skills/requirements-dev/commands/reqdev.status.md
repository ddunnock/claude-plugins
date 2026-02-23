---
name: reqdev:status
description: Display session status dashboard showing current phase, block progress, requirement counts, traceability coverage, TBD/TBR counts, and quality check pass rate
---

# /reqdev:status -- Session Status Dashboard

## Step 1: Load State

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev show
```

If no state file exists, inform the user:
```
No active session. Run /reqdev:init to start.
```

## Step 2: Sync Counts

Ensure counts reflect current registry contents:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev sync-counts
```

## Step 3: Load Registry Summaries

Read the registries to extract summary statistics:

```bash
cat .requirements-dev/state.json
```

If they exist, also read:
- `cat .requirements-dev/needs_registry.json`
- `cat .requirements-dev/requirements_registry.json`
- `cat .requirements-dev/traceability_registry.json`

Check cross-cutting notes:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev summary
```

Check assumption status:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --workspace .requirements-dev/ summary
```

## Step 4: Display Dashboard

```
===================================================================
REQUIREMENTS DEVELOPMENT STATUS
===================================================================

Session: [id]
Last Updated: [timestamp from state.json created_at]

-------------------------------------------------------------------
PHASES
-------------------------------------------------------------------

  [X/>/  ] 1. Init              [COMPLETED / IN PROGRESS / NOT STARTED]
  [X/>/  ] 2. Needs             [COMPLETED / IN PROGRESS / NOT STARTED]
  [X/>/  ] 3. Requirements      [COMPLETED / IN PROGRESS / NOT STARTED]
  [X/>/  ] 4. Deliver           [COMPLETED / IN PROGRESS / NOT STARTED]

Current Phase: [phase name]
Gate Status: [passed / pending for each gate]

-------------------------------------------------------------------
BLOCK PROGRESS
-------------------------------------------------------------------

  Block: [block-name]
    Types completed: [list, e.g., functional, performance]
    Types remaining: [list, e.g., interface, constraint, quality]
    Requirements: [N] registered

  Block: [block-name]
    [not started]

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
ASSUMPTIONS (GtWR §5.3)
-------------------------------------------------------------------

  Total: [N]  Active: [N]  Challenged: [N]  Invalidated: [N]  Reaffirmed: [N]
  Origin: [N] concept-dev, [N] requirements-dev
  High-impact active: [N] (require monitoring)

-------------------------------------------------------------------
CROSS-CUTTING NOTES
-------------------------------------------------------------------

  Total: [N]  Open: [N]  Resolved: [N]  Dismissed: [N]

  [If open notes exist, show by target phase]:
  Targeting requirements: [N] open
  Targeting validate:     [N] open
  Targeting research:     [N] open

-------------------------------------------------------------------
GAP ANALYSIS
-------------------------------------------------------------------

  [If .requirements-dev/gap_analysis.json exists]:
  Last run: [timestamp]
  Findings: [N] total ([critical] critical, [high] high, [medium] medium)

  [If gap_analysis.json does not exist]:
  Not yet run. Use /reqdev:gaps to analyze coverage.

-------------------------------------------------------------------
DECOMPOSITION
-------------------------------------------------------------------

  Levels active: [list or "none"]
  Max level: [N]

===================================================================
Next action: [suggested command based on current state]
===================================================================
```

## Step 5: Suggest Next Action

Based on the current state, suggest the most logical next step:

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
