---
name: concept:resume
description: Resume an interrupted concept development session from the last known state
---

# /concept:resume

Resume a concept development session after interruption.

## Procedure

### Step 1: Load State

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show
```

If no state file exists: "No active session found. Run `/concept:init` to start a new session."

### Step 2: Identify Resume Point

Determine the current phase and gate status:

```
===================================================================
RESUMING SESSION
===================================================================

Session: [id]
Project: [name]
Last Updated: [timestamp]

Current Phase: [phase name]
Phase Status: [in_progress / completed]
Gate Status: [passed / pending]

===================================================================
```

### Step 3: Load Context

Based on current phase, load the relevant artifacts:

| Phase | Artifacts to Load |
|-------|-------------------|
| spitball | (none — session state only) |
| problem | .concept-dev/IDEAS.md |
| blackbox | .concept-dev/IDEAS.md, .concept-dev/PROBLEM-STATEMENT.md |
| drilldown | .concept-dev/BLACKBOX.md (+ prior artifacts) |
| document | All artifacts |

Read each artifact and summarize key points to the user.

### Step 4: Present Context Summary

```
===================================================================
SESSION CONTEXT
===================================================================

[For each loaded artifact, provide a 2-3 sentence summary]

Phase 1 (Spit-Ball):
  Themes selected: [list]

Phase 2 (Problem):
  Problem: [1-sentence summary]
  [if completed]

Phase 3 (Black-Box):
  Approach: [name]
  Blocks: [list]
  [if completed]

Phase 4 (Drill-Down):
  Blocks researched: [N] of [N]
  Sources: [N]  |  Gaps: [N]
  [if in progress or completed]

-------------------------------------------------------------------
RESUMPTION POINT:

Based on the state, you were in [phase] — [status].
[Specific context about where in the phase you were]

Ready to continue?
  [A] Continue from where we left off
  [B] Go back to a previous phase
  [C] Show full status dashboard (/concept:status)
===================================================================
```

### Step 5: Continue

Based on user selection:

- **Continue:** Invoke the appropriate command for the current phase, with state indicating it's a resumption (not a fresh start). The phase command should detect existing artifacts and skip completed steps.

- **Go back:** Ask which phase to return to. Warn that going back will not delete existing artifacts but will re-open the gate for that phase.

- **Dashboard:** Run `/concept:status`.

### Resumption Behavior by Phase

| Phase | Resumption Behavior |
|-------|-------------------|
| spitball (in_progress) | Summarize captured ideas so far, continue ideation |
| spitball (gate pending) | Present theme clustering and gate prompt |
| problem (in_progress) | Summarize questions answered, continue questioning |
| problem (gate pending) | Present problem statement candidates for approval |
| blackbox (in_progress) | Check which sections are approved, continue from next |
| blackbox (gate pending) | Present architecture for final approval |
| drilldown (in_progress) | Show which blocks are done, continue from next block |
| drilldown (gate pending) | Present drill-down for final approval |
| document (in_progress) | Check which sections are approved, continue from next |
| document (gate pending) | Present documents for final approval |
