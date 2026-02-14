---
name: concept:document
description: Phase 5 — Generate Concept Document and Solution Landscape with section-by-section approval and mandatory assumption review
---

# /concept:document

Phase 5 of concept development: document generation.

## Prerequisites

- Phase 4 gate passed (drill-down approved)
- Load state: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show`
- Read all artifacts:
  - `.concept-dev/IDEAS.md`
  - `.concept-dev/PROBLEM-STATEMENT.md`
  - `.concept-dev/BLACKBOX.md`
  - `.concept-dev/DRILLDOWN.md`

## Procedure

### Step 1: Set Phase

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-phase document
```

### Step 2: Pre-Generation Review

Present a summary of all inputs:

```
===================================================================
DOCUMENT GENERATION
===================================================================

Inputs:
  IDEAS.md          — [N] themes, [N] ideas
  PROBLEM-STATEMENT — [1-sentence summary]
  BLACKBOX.md       — [N] functional blocks, [Approach name]
  DRILLDOWN.md      — [N] sub-functions, [N] sources, [N] gaps

I will generate two documents:

  1. CONCEPT DOCUMENT
     Modeled on engineering concept papers:
     Exec Summary → Problem → Concept → Capabilities →
     ConOps → Maturation Path → Glossary

  2. SOLUTION LANDSCAPE
     Per-domain approaches with pros/cons, citations,
     confidence ratings, and unresolved gaps

Each section will be presented for your approval before
being included in the final document.

Ready to begin?
===================================================================
```

### Step 3: Mandatory Assumption Review

Before generating any document content, run the assumption review gate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --registry .concept-dev/assumption_registry.json review
```

Present the assumption review to the user:

```
===================================================================
MANDATORY ASSUMPTION REVIEW
===================================================================

Before generating final documents, review all assumptions
made across all phases.

[Display assumption_tracker review output]

-------------------------------------------------------------------
REQUIRED ACTION:

  [A] Approve all pending assumptions
  [B] Review individually — I'll present each one
  [C] Reject/modify specific assumptions: ___

I will NOT generate documents until assumptions are resolved.
===================================================================
```

### Step 4: Generate Concept Document (Section by Section)

Use the document-writer agent. For each section:

1. Generate the section content
2. Present to user for review
3. Wait for approval or revision
4. Only proceed to next section after approval

**Sections (from [references/concept-doc-structure.md](../references/concept-doc-structure.md)):**

1. Executive Summary
2. The Problem (from PROBLEM-STATEMENT.md)
3. The Concept (from BLACKBOX.md)
4. Enabled Capabilities (from BLACKBOX.md)
5. Concept of Operations (from BLACKBOX.md)
6. Maturation Path (synthesized from DRILLDOWN.md)
7. Glossary

Per section:
```
-------------------------------------------------------------------
SECTION: [Section Name]
-------------------------------------------------------------------

[Generated content]

-------------------------------------------------------------------
  [A] Approve this section
  [B] Revise: ___
-------------------------------------------------------------------
```

Write to: `.concept-dev/CONCEPT-DOCUMENT.md`

### Step 5: Generate Solution Landscape

Use the document-writer agent for the second document.
Follow the presentation rules in [references/solution-landscape-guide.md](../references/solution-landscape-guide.md).

Before presenting, invoke the skeptic agent on the complete Solution Landscape content.

**Sections:**
1. Overview (scope, methodology, tool availability)
2. Per-domain solution approaches (from DRILLDOWN.md)
3. Cross-cutting considerations
4. Unresolved gaps and next research steps
5. Source bibliography

Per section, same approval flow as Step 4.

Write to: `.concept-dev/SOLUTION-LANDSCAPE.md`

### Step 6: Skeptic Final Review

Run skeptic on the Solution Landscape before final approval:

```
===================================================================
SKEPTIC REVIEW: SOLUTION LANDSCAPE
===================================================================

[Skeptic summary]

Claims reviewed: [N]
  VERIFIED:         [N]
  UNVERIFIED_CLAIM: [N]
  DISPUTED_CLAIM:   [N]
  NEEDS_USER_INPUT: [N]

[High-priority flags if any]

===================================================================
```

### Step 7: Gate — Final Approval

```
===================================================================
GATE: APPROVE FINAL DOCUMENTS
===================================================================

Two documents generated:

  1. CONCEPT-DOCUMENT.md
     Sections: [list]
     Sources cited: [N]

  2. SOLUTION-LANDSCAPE.md
     Domains covered: [N]
     Approaches documented: [N]
     Sources cited: [N]
     Unresolved gaps: [N]

Assumptions: [N] total, [N] approved
Skeptic: [N] verified, [N] unverified, [N] disputed

-------------------------------------------------------------------
  [A] APPROVE BOTH — Documents are complete
  [B] REVISE CONCEPT DOCUMENT — Specific changes: ___
  [C] REVISE SOLUTION LANDSCAPE — Specific changes: ___
  [D] REVISE BOTH — Changes: ___

I will NOT finalize until you approve.
===================================================================
```

### Step 8: Finalize

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-artifact document ".concept-dev/CONCEPT-DOCUMENT.md" --key concept_doc_artifact
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-artifact document ".concept-dev/SOLUTION-LANDSCAPE.md" --key solution_landscape_artifact
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json pass-gate document
```

### Step 9: Completion Summary

```
===================================================================
CONCEPT DEVELOPMENT COMPLETE
===================================================================

Deliverables:
  .concept-dev/CONCEPT-DOCUMENT.md
  .concept-dev/SOLUTION-LANDSCAPE.md

Supporting artifacts:
  .concept-dev/IDEAS.md
  .concept-dev/PROBLEM-STATEMENT.md
  .concept-dev/BLACKBOX.md
  .concept-dev/DRILLDOWN.md
  .concept-dev/source_registry.json
  .concept-dev/assumption_registry.json

Run /concept:status for a complete dashboard.
===================================================================
```
