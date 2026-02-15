---
name: concept:blackbox
description: Phase 3 — Define concept at functional level with blocks, relationships, principles, and ASCII diagrams. No implementation details.
---

# /concept:blackbox

Phase 3 of concept development: black-box architecture.

## Prerequisites

Run the prerequisite gate check:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json check-gate blackbox
```

If this exits non-zero, stop and tell the user to complete the previous phase first.

Then load context:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show`
- Read: `.concept-dev/PROBLEM-STATEMENT.md`

## Procedure

### Step 1: Set Phase

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-phase blackbox
```

### Step 2: Context Loading

Read `.concept-dev/PROBLEM-STATEMENT.md` and present:

```
===================================================================
BLACK-BOX ARCHITECTURE
===================================================================

Problem: [1-2 sentence summary]
Scope: [IN scope summary]
Key Constraints: [List]

I'll propose 2-3 high-level approaches to solving this problem.
Each approach describes WHAT the concept does at a functional level
— not HOW it's implemented.

For each approach, I'll describe:
  - Functional blocks and their responsibilities
  - Relationships between blocks
  - Guiding principles
  - Capabilities this architecture enables
  - Trade-offs

===================================================================
```

### Step 3: Propose Approaches

Use the concept-architect agent. Present 2-3 distinct architectural approaches:

```
===================================================================
APPROACH 1: [Name]
===================================================================

CONCEPT: [2-3 sentence description]

FUNCTIONAL BLOCKS:
  [Block A] — [What it does, not how]
  [Block B] — [What it does, not how]
  [Block C] — [What it does, not how]

RELATIONSHIPS:
  [Block A] → [Block B]: [What flows between them]
  [Block B] ↔ [Block C]: [Bidirectional relationship]

PRINCIPLES:
  1. [Guiding principle]
  2. [Guiding principle]

ENABLES:
  - [Capability this approach uniquely enables]
  - [Capability]

TRADE-OFFS:
  + [Advantage]
  + [Advantage]
  - [Disadvantage]
  - [Disadvantage]

===================================================================
APPROACH 2: [Name]
===================================================================
[Same structure]

===================================================================
APPROACH 3: [Name]
===================================================================
[Same structure]
```

### Step 4: Gate — Approach Selection

```
===================================================================
GATE: SELECT APPROACH
===================================================================

  [A] Approach 1: [name]
  [B] Approach 2: [name]
  [C] Approach 3: [name]
  [D] Combine elements from multiple approaches
  [E] None — let me describe what I want

Your selection: _______________________________________________

I will NOT proceed until you select an approach.
===================================================================
```

### Step 5: Elaborate Selected Approach

Once the user selects an approach, elaborate it section by section with ASCII diagrams. Each section requires user approval before proceeding.

**Section 1: Functional Block Diagram**

Create an ASCII diagram showing all blocks and their relationships:

```
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   Block A    │────▶│   Block B    │────▶│   Block C    │
  │  [function]  │     │  [function]  │     │  [function]  │
  └──────────────┘     └──────┬───────┘     └──────────────┘
                              │
                       ┌──────▼───────┐
                       │   Block D    │
                       │  [function]  │
                       └──────────────┘
```

Ask: "Does this block structure capture the concept correctly? Any blocks missing or misplaced?"

**Section 2: Principles and Constraints**

List the architectural principles derived from the problem statement and user input. These are design rules, not implementation choices.

Ask: "Do these principles accurately reflect your priorities?"

**Section 3: Enabled Capabilities**

Describe what becomes possible with this architecture that isn't possible today. Reference the problem statement's desired state. Model on the "emergent capabilities" framing from concept documents.

Ask: "Are these the capabilities you're most interested in? Any missing?"

**Section 4: Concept of Operations (ConOps) Sketch**

Brief narrative of how the concept operates in practice. Walk through 1-2 representative scenarios.

Ask: "Does this operational picture match your vision?"

### Step 6: Write BLACKBOX.md

After all sections are approved, read the template using the Read tool:
```
Read file: ${CLAUDE_PLUGIN_ROOT}/templates/blackbox.md
```

Write to: `.concept-dev/BLACKBOX.md`

### Step 6b: Register Architecture Assumptions

Register any architectural assumptions made during this phase:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --registry .concept-dev/assumption_registry.json add "[architecture assumption]" --category architecture --phase blackbox --basis "[rationale from approach selection]"
```

Register assumptions about block responsibilities, relationships, and design principles.

### Step 6c: Update State

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-artifact blackbox ".concept-dev/BLACKBOX.md"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json pass-gate blackbox
```

### Step 7: Transition

```
===================================================================
Phase 3 complete. BLACKBOX.md written to .concept-dev/

Functional blocks defined: [N]
Next: Run /concept:drilldown to decompose each block,
research domains, and identify solution approaches.
===================================================================
```
