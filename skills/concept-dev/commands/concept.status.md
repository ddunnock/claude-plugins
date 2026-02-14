---
name: concept:status
description: Display session status dashboard showing current phase, progress metrics, source coverage, gaps, and skeptic findings
---

# /concept:status

Display the current session status dashboard.

## Procedure

### Step 1: Load State

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show
```

If no state file exists, inform the user: "No active session. Run `/concept:init` to start."

### Step 2: Load Tracker Summaries

If registries exist, load summaries:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/source_tracker.py --registry .concept-dev/source_registry.json summary
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --registry .concept-dev/assumption_registry.json summary
```

### Step 3: Display Dashboard

```
===================================================================
CONCEPT DEVELOPMENT STATUS
===================================================================

Session: [id]
Project: [name or "unnamed"]
Last Updated: [timestamp]

-------------------------------------------------------------------
PHASES
-------------------------------------------------------------------

  [X] 1. Spit-Ball        COMPLETED   [date]
  [>] 2. Problem           IN PROGRESS
  [ ] 3. Black-Box         NOT STARTED
  [ ] 4. Drill-Down        NOT STARTED
  [ ] 5. Document          NOT STARTED

Current Phase: [phase name]
Gate Status: [passed / pending]

-------------------------------------------------------------------
ARTIFACTS
-------------------------------------------------------------------

  [+/-] .concept-dev/IDEAS.md
  [+/-] .concept-dev/PROBLEM-STATEMENT.md
  [+/-] .concept-dev/BLACKBOX.md
  [+/-] .concept-dev/DRILLDOWN.md
  [+/-] .concept-dev/CONCEPT-DOCUMENT.md
  [+/-] .concept-dev/SOLUTION-LANDSCAPE.md

-------------------------------------------------------------------
SOURCES
-------------------------------------------------------------------

  Total: [N]
  By confidence: HIGH=[N]  MEDIUM=[N]  LOW=[N]  UNGROUNDED=[N]
  Open gaps: [N]

-------------------------------------------------------------------
ASSUMPTIONS
-------------------------------------------------------------------

  Total: [N]
  Pending: [N]    Approved: [N]
  Ready for document: [YES/NO]

-------------------------------------------------------------------
SKEPTIC FINDINGS
-------------------------------------------------------------------

  Verified: [N]
  Unverified Claims: [N]
  Disputed Claims: [N]
  Needs User Input: [N]

-------------------------------------------------------------------
RESEARCH TOOLS
-------------------------------------------------------------------

  Available: [list of detected tools]

===================================================================
Next action: [suggested command based on current state]
===================================================================
```

### Step 4: Suggest Next Action

Based on current state, suggest the appropriate next command:

| State | Suggestion |
|-------|-----------|
| No session | `/concept:init` |
| Phase 1 not started | `/concept:spitball` |
| Phase 1 complete | `/concept:problem` |
| Phase 2 complete | `/concept:blackbox` |
| Phase 3 complete | `/concept:drilldown` |
| Phase 4 complete | `/concept:document` |
| Phase 5 complete | "Concept development complete!" |
| Phase in progress | "Continue current phase or `/concept:resume`" |
