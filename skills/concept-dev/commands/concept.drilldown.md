---
name: concept:drilldown
description: Phase 4 — Decompose functional blocks, research domains, identify gaps, and list solution approaches with cited sources
---

# /concept:drilldown

Phase 4 of concept development: drill-down and gap analysis.

## Prerequisites

- Phase 3 gate passed (black-box architecture approved)
- Load state: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show`
- Read: `.concept-dev/BLACKBOX.md`

## Procedure

### Step 1: Set Phase

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-phase drilldown
```

### Step 2: Enumerate Blocks

Read BLACKBOX.md and list all functional blocks to the user:

```
===================================================================
DRILL-DOWN & GAP ANALYSIS
===================================================================

Functional blocks from the architecture:

  1. [Block A] — [brief responsibility]
  2. [Block B] — [brief responsibility]
  3. [Block C] — [brief responsibility]
  4. [Block D] — [brief responsibility]

For each block, I will:
  a) Decompose it to sub-functions
  b) Research the domain for each sub-function
  c) Identify gaps (what we don't know)
  d) List potential solution APPROACHES (not pick them)
  e) Run skeptic review on findings

-------------------------------------------------------------------
MODE SELECTION:

  [A] INTERACTIVE — We work through each block together.
      I research, present findings, you review per block.

  [B] AUTO — I research all blocks autonomously, then present
      the complete drill-down for your review.

  [C] SELECTIVE — Choose specific blocks to drill into.
      Blocks: _______________________________________________

Your selection: _______________________________________________
===================================================================
```

Update state with block count:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json update phases.drilldown blocks_total [N]
```

### Step 3: Per-Block Drill-Down

For each block (in selected mode), execute the following sequence:

#### 3a: Decompose to Sub-Functions

Break the functional block into sub-functions:

```
-------------------------------------------------------------------
BLOCK: [Block Name]
-------------------------------------------------------------------

Sub-functions:
  1. [Sub-function A] — [What it must do]
  2. [Sub-function B] — [What it must do]
  3. [Sub-function C] — [What it must do]

Does this decomposition capture the block's responsibilities?
-------------------------------------------------------------------
```

#### 3b: Research Domains

For each sub-function, use the domain-researcher agent to:
- Search for relevant domains, standards, and prior art
- Use available research tools (check state.json for detected tools)
- Register sources using source_tracker.py:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/source_tracker.py --registry .concept-dev/source_registry.json add "[source name]" --type web_research --url "[url]" --confidence medium --phase drilldown
```

#### 3c: Identify Gaps

Use the gap-analyst agent to identify:
- What's unknown or uncertain for this block
- What needs further investigation
- What domain expertise is required

Register gaps:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/source_tracker.py --registry .concept-dev/source_registry.json gap "[gap description]" --required-for "[block name]" --source-type web_research --phase drilldown
```

#### 3d: List Solution Approaches

For each sub-function, list potential solution APPROACHES (not recommendations):

```
-------------------------------------------------------------------
SOLUTION APPROACHES: [Sub-function Name]
-------------------------------------------------------------------

Approach 1: [Name]
  Description: [What this approach does]
  Pros: [Advantages]
  Cons: [Disadvantages]
  Maturity: [Mature / Emerging / Experimental]
  Sources: [SRC-xxx, SRC-yyy]

Approach 2: [Name]
  Description: [What this approach does]
  Pros: [Advantages]
  Cons: [Disadvantages]
  Maturity: [tag]
  Sources: [SRC-xxx]

Approach 3: [Name]
  [Same structure]

NOTE: These are OPTIONS, not recommendations. Selection
happens during implementation planning, not concept development.
-------------------------------------------------------------------
```

#### 3e: Skeptic Review

After completing research for each block, invoke the skeptic agent:
- Submit all feasibility claims and solution descriptions
- Review skeptic findings
- Adjust confidence levels as needed
- Present skeptic summary to user

#### 3f: Block Checkpoint (Interactive mode)

```
-------------------------------------------------------------------
CHECKPOINT: [Block Name]
-------------------------------------------------------------------

Sub-functions: [N]
Sources registered: [N]
Gaps identified: [N]
Solution approaches documented: [N]

Skeptic findings:
  Verified: [N]  |  Unverified: [N]  |  Disputed: [N]

Questions for you:
  1. [Question from skeptic or gap analysis]
  2. [Question]

Does this block drill-down look correct?
  [A] Approve and continue to next block
  [B] Revise — [specify what to change]
-------------------------------------------------------------------
```

### Step 4: Write DRILLDOWN.md

After all blocks are drilled into:

Read template: `${CLAUDE_PLUGIN_ROOT}/templates/drilldown.md`
Write to: `.concept-dev/DRILLDOWN.md`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-artifact drilldown ".concept-dev/DRILLDOWN.md"
```

### Step 5: Gate — Drill-Down Review

```
===================================================================
GATE: APPROVE DRILL-DOWN
===================================================================

Blocks analyzed: [N]
Total sub-functions: [N]
Sources registered: [N]
Gaps identified: [N]
Solution approaches documented: [N]

Skeptic summary:
  Verified: [N]  |  Unverified: [N]  |  Disputed: [N]

Review .concept-dev/DRILLDOWN.md for the complete analysis.

  [A] APPROVE — Drill-down is complete and accurate
  [B] REVISE — Specific blocks need more work: ___
  [C] ADD RESEARCH — I have additional information: ___

I will NOT proceed until you approve the drill-down.
===================================================================
```

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json pass-gate drilldown
```

### Step 6: Transition

```
===================================================================
Phase 4 complete. DRILLDOWN.md written to .concept-dev/

Next: Run /concept:document to generate the Concept Document
and Solution Landscape.
===================================================================
```
