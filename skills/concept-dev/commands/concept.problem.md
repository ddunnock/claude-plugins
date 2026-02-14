---
name: concept:problem
description: Phase 2 — Refine viable ideas into a clear, bounded problem statement using adapted 5W2H questioning
---

# /concept:problem

Phase 2 of concept development: problem definition.

## Prerequisites

- Phase 1 gate passed (spit-ball themes selected)
- Load state and verify: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show`
- Read IDEAS.md: `.concept-dev/IDEAS.md`

If Phase 1 is not complete, inform the user and suggest `/concept:spitball`.

## Procedure

### Step 1: Set Phase

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-phase problem
```

### Step 2: Context Loading

Read `.concept-dev/IDEAS.md` and present a summary:

```
===================================================================
PROBLEM DEFINITION
===================================================================

Starting from your selected themes:

  1. [Theme A] — [brief summary]
  2. [Theme B] — [brief summary]

I'll ask questions to refine these into a clear problem statement.
We'll work in batches of 3-4 questions with checkpoints between.

IMPORTANT: If you think of specific solutions or technologies,
I'll note them for Phase 4 (Drill-Down) and keep us focused on
the problem itself.
===================================================================
```

### Step 3: Metered Questioning

Use the problem-analyst agent pattern. Follow the metered questioning approach from [references/questioning-heuristics.md](../references/questioning-heuristics.md).

**Questioning Framework (adapted from 5W2H for concept development):**

**Batch 1: Current State**
1. What is the current situation? How do things work today?
2. Who is affected by this situation? (stakeholders, users, operators)
3. What are the consequences of the current state? What's the cost of inaction?
4. How long has this been the case?

**Checkpoint** — Summarize understanding, confirm.

**Batch 2: Desired State**
1. What does "solved" look like? What capabilities should exist that don't today?
2. What would success enable that isn't possible now?
3. Are there constraints we need to respect? (budget, timeline, regulatory, organizational)
4. What is explicitly OUT of scope?

**Checkpoint** — Summarize understanding, confirm.

**Batch 3: Gap Characterization (if needed)**
1. What's the gap between current state and desired state?
2. How would you measure whether the gap has been closed?
3. Are there partial solutions that address some but not all of the problem?
4. What has been tried before? What worked and what didn't?

**Checkpoint** — Summarize understanding, confirm.

### Scope Guardrail

When the user offers a specific solution or technology during questioning:

```
Good thought — I'm noting "[solution idea]" for the drill-down phase
(Phase 4), where we'll research solution approaches systematically.

For now, let's stay with the problem: [redirect to next question]
```

Track deferred solutions in the problem statement's "Deferred Solutions" section.

### Step 4: Problem Statement Synthesis

After sufficient questioning, synthesize a problem statement. Present 2-3 candidates with different framings:

```
===================================================================
PROBLEM STATEMENT CANDIDATES
===================================================================

CANDIDATE 1: Capability Gap Framing
-------------------------------------------------------------------
[Problem statement text — focuses on what capability is missing]

CANDIDATE 2: Consequence Framing
-------------------------------------------------------------------
[Problem statement text — focuses on the cost/impact of the current state]

CANDIDATE 3: Stakeholder Impact Framing
-------------------------------------------------------------------
[Problem statement text — focuses on who is affected and how]

===================================================================
SELECTION:
  [A] Candidate 1
  [B] Candidate 2
  [C] Candidate 3
  [D] Combine elements from multiple candidates
  [E] None — let me provide my own

Your selection: _______________________________________________
===================================================================
```

### Step 5: Validation

Before presenting for final approval, validate the selected statement:

- [ ] No embedded cause ("due to...", "caused by...")
- [ ] No embedded solution ("need to build...", "should use...")
- [ ] Describes gap between current and desired state
- [ ] Scope bounded (what IS and IS NOT included)
- [ ] Consequences quantified where possible
- [ ] Stakeholders identified

### Step 6: Gate — Problem Statement Approval

```
===================================================================
GATE: APPROVE PROBLEM STATEMENT
===================================================================

PROBLEM STATEMENT:

  [Final problem statement text]

SCOPE:
  IN:  [What's included]
  OUT: [What's excluded]

STAKEHOLDERS: [List]

CONSEQUENCES OF INACTION: [Summary]

DEFERRED SOLUTIONS (for Phase 4):
  - [Solution idea 1]
  - [Solution idea 2]

-------------------------------------------------------------------
  [A] APPROVE — This problem statement is correct
  [B] REVISE — Make these changes: ___
  [C] RESTART — Begin problem definition again

I will NOT proceed until you approve the problem statement.
===================================================================
```

### Step 7: Write PROBLEM-STATEMENT.md

Read the template: `${CLAUDE_PLUGIN_ROOT}/templates/problem-statement.md`
Write to: `.concept-dev/PROBLEM-STATEMENT.md`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-artifact problem ".concept-dev/PROBLEM-STATEMENT.md"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json pass-gate problem
```

### Step 8: Transition

```
===================================================================
Phase 2 complete. PROBLEM-STATEMENT.md written to .concept-dev/

Next: Run /concept:blackbox to define the functional architecture.
===================================================================
```
