---
name: concept:spitball
description: Phase 1 — Open-ended ideation session. Capture wild ideas, probe feasibility, cluster themes
---

# /concept:spitball

Phase 1 of concept development: open-ended ideation.

## Prerequisites

- Session initialized (`/concept:init`). Verify state.json exists:
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show
  ```
  If this fails, tell the user to run `/concept:init` first and stop.

## Procedure

### Step 1: Set Phase

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-phase spitball
```

### Step 2: Open the Floor

Present an open invitation — no structure, no forms:

```
===================================================================
SPIT-BALL SESSION
===================================================================

This is the wild ideas phase. There are no bad ideas here.

Tell me what you're thinking about. It can be:
- A problem you've noticed
- A capability you wish existed
- A "what if..." scenario
- Something that annoys you about how things work today
- A half-formed thought you haven't fully explored

I'll ask follow-up questions, probe feasibility where useful,
and help you explore the idea space. We'll cluster themes later.

What's on your mind?
===================================================================
```

### Step 3: Ideation Loop

Use the ideation-partner agent pattern. For each idea the user shares:

1. **Acknowledge and expand** — "Interesting — what if that also meant [extension]?"
2. **Probe feasibility** — Use WebSearch to quickly check if the general concept area has precedent. Do NOT present this as validation, just as context.
3. **Ask "what if" questions** — Push the idea further: "What if you removed [constraint]? What would that enable?"
4. **Capture with notes** — Internally track each idea with:
   - Idea summary (1-2 sentences)
   - Feasibility note (precedent found / novel / needs investigation)
   - Energy level (how excited the user seems)
   - Related themes

**Questioning approach:** See [references/questioning-heuristics.md](../references/questioning-heuristics.md) for adaptive questioning patterns. Start fully open, gradually focus as themes emerge.

**Skeptic check:** After accumulating feasibility notes, explicitly invoke the skeptic agent using the Task tool:

```
Use the Task tool with subagent_type='concept-dev:skeptic' to review all feasibility claims
gathered during ideation. Pass the claims as a structured list in the prompt.
```

Present skeptic findings to the user before theme clustering.

### Step 4: Theme Clustering

After the user has shared several ideas (or signals they're ready to move on), cluster ideas into themes:

```
===================================================================
THEME CLUSTERING
===================================================================

Based on our conversation, I see these themes emerging:

THEME A: [Name]
  - [Idea 1 summary]
  - [Idea 2 summary]
  Feasibility: [brief note]

THEME B: [Name]
  - [Idea 3 summary]
  - [Idea 4 summary]
  Feasibility: [brief note]

THEME C: [Name]
  - [Idea 5 summary]
  Feasibility: [brief note]

DEFERRED:
  - [Ideas that didn't cluster or had low energy]

===================================================================
```

### Step 5: Gate — Theme Selection

Present the gate prompt:

```
===================================================================
GATE: SELECT THEMES TO ADVANCE
===================================================================

Which themes have energy? Select the themes you want to carry
forward into problem definition.

  [A] Theme A: [name]
  [B] Theme B: [name]
  [C] Theme C: [name]
  [D] All themes
  [E] Let me refine themes first

Your selection: _______________________________________________

I will NOT proceed until you select themes to advance.
===================================================================
```

### Step 5b: Register Key Feasibility Assumptions

After the user selects themes, register any key feasibility assumptions that emerged during ideation:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --registry .concept-dev/assumption_registry.json add "[assumption description]" --category feasibility --phase spitball --basis "[source or rationale]" --impact medium
```

Register one assumption per major feasibility claim that the selected themes depend on.

### Step 6: Write IDEAS.md

Once the user selects themes, write the IDEAS.md artifact using the template:

Read the template: `${CLAUDE_PLUGIN_ROOT}/templates/ideas.md`

Write to: `.concept-dev/IDEAS.md`

Update state:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-artifact spitball ".concept-dev/IDEAS.md"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json pass-gate spitball
```

### Step 7: Transition Prompt

```
===================================================================
Phase 1 complete. IDEAS.md written to .concept-dev/

Selected themes: [list]

Next: Run /concept:problem to refine these themes into a
clear problem statement.
===================================================================
```
