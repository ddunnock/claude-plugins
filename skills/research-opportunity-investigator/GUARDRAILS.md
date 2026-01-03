# Research & Opportunity Investigator Guardrails

This document defines the strict behavioral guardrails that MUST be followed when executing this skill.

---

## Core Principle

**Evidence-Based, User-Validated Research**

Every claim, analysis, and recommendation MUST be grounded in verifiable sources and validated by the user at explicit checkpoints. The assistant NEVER assumes, NEVER proceeds without confirmation, and NEVER generates ungrounded output.

---

## Mandatory Behavioral Rules

### Rule 1: NEVER Proceed Without Explicit User Confirmation

**Prohibited:**
- Proceeding to the next phase without explicit user approval
- Assuming user agreement from silence
- Auto-advancing through gates based on confidence levels
- Making decisions on behalf of the user

**Required:**
- Present findings/analysis at each gate
- Ask explicit confirmation questions
- Wait for user response before proceeding
- If unclear, ask for clarification

**Gate Points Requiring Confirmation:**
1. Research scope definition
2. Source coverage sufficiency
3. Analysis accuracy
4. ACP summary approval
5. Opportunity assessment
6. RFC content approval
7. Final deliverables

---

### Rule 2: NEVER Make Ungrounded Claims

**Prohibited:**
- Stating facts without source citation
- Inferring capabilities without evidence
- Making claims marked as [UNGROUNDED] in final outputs
- Using phrases like "presumably," "likely," "probably" without evidence

**Required:**
- Every claim MUST reference a specific source: `[SRC-XXX]`
- Every source MUST have: URL, type, access date, relevance
- Unverifiable claims MUST be marked: `[UNGROUNDED—requires verification]`
- Assumptions MUST be marked: `[ASSUMED]` and require user validation

**Source Citation Format:**
```
[Statement]
  └─ Source: [SRC-XXX], [specific section/page/line]
  └─ Evidence Type: [VERIFIED|INFERRED|ASSUMED]
  └─ Confidence: [HIGH|MEDIUM|LOW]
```

---

### Rule 3: NEVER Generate RFC Without ACP Summary

**Prohibited:**
- Drafting RFC proposals before ACP summary is created
- Drafting RFC proposals before ACP summary is approved by user
- Creating RFCs that don't reference existing spec sections
- Proposing changes without showing compatibility with current design

**Required:**
- Generate comprehensive ACP summary FIRST
- Summary MUST cover: existing RFCs, schemas, spec chapters
- User MUST explicitly approve summary
- RFC MUST trace to summary for validation

**ACP Summary Requirements:**
1. Current ACP version
2. All existing RFCs with summaries
3. All schemas with key fields
4. Relevant spec chapters with summaries
5. Integration points identified
6. Design principles extracted

---

### Rule 4: ALL Evidence Must Be Categorized

**Evidence Categories:**

| Category | Definition | Usage |
|----------|------------|-------|
| `[VERIFIED]` | Directly confirmed from primary source | Official docs, source code, announcements |
| `[INFERRED]` | Logically derived from verified facts | Architectural implications, reasonable deductions |
| `[ASSUMED]` | Reasonable assumption requiring validation | User MUST confirm before proceeding |
| `[UNGROUNDED]` | Cannot find source | Flag for investigation, do not use in final output |

**Rules:**
- Every technical claim MUST have a category
- `[ASSUMED]` claims MUST be presented to user for validation
- `[UNGROUNDED]` claims MUST NOT appear in final deliverables
- Final deliverables should be predominantly `[VERIFIED]`

---

### Rule 5: NEVER Skip Phases

**Prohibited:**
- Jumping from scoping directly to RFC generation
- Skipping ACP summary phase
- Omitting opportunity assessment
- Bypassing source registration

**Required Phase Sequence:**
```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
```

**Exception Handling:**
- If user explicitly requests to skip a phase, note the skip with rationale
- Document what was skipped and potential impact
- Never skip Phase 4 (ACP Summary) before Phase 6 (RFC Generation)

---

### Rule 6: RFCs MUST Trace to Existing Specification

**Prohibited:**
- Proposing changes without referencing affected spec sections
- Creating new features that conflict with existing RFCs
- Ignoring ACP design principles

**Required RFC Elements:**
- Affected Components table with spec references
- Existing State quotes from current specification
- Proposed State with clear diff from existing
- Rationale tracing to research gaps
- Compatibility analysis with existing RFCs
- Adherence to ACP design principles

---

## Interaction Templates

### Gate Confirmation Template

```
═══════════════════════════════════════════════════════════════════════════════
✓ PHASE [N] COMPLETE — [Phase Name]
═══════════════════════════════════════════════════════════════════════════════

SUMMARY:
[Brief summary of what was accomplished]

KEY FINDINGS:
• [Finding 1]
• [Finding 2]

ASSUMPTIONS REQUIRING CONFIRMATION:
• [ASSUMED] [Assumption 1] — Is this correct? [Y/N]
• [ASSUMED] [Assumption 2] — Is this correct? [Y/N]

NEXT PHASE: [Phase N+1 Name]
• [What will be done next]

───────────────────────────────────────────────────────────────────────────────
⚠️  Please confirm:
  [A] Proceed to next phase
  [B] Revise current phase findings
  [C] Request additional information
═══════════════════════════════════════════════════════════════════════════════
```

### Assumption Validation Template

```
═══════════════════════════════════════════════════════════════════════════════
📋 ASSUMPTION VALIDATION REQUIRED
═══════════════════════════════════════════════════════════════════════════════

The following assumptions require your confirmation:

ASSUMPTION A-001: [Description]
  └─ Basis: [Why this was assumed]
  └─ Impact if wrong: [What changes if incorrect]
  └─ Confidence: [LOW/MEDIUM]
  
  Response: [A] Confirm [B] Reject [C] Need more info

ASSUMPTION A-002: [Description]
  └─ Basis: [Why this was assumed]
  └─ Impact if wrong: [What changes if incorrect]
  └─ Confidence: [LOW/MEDIUM]
  
  Response: [A] Confirm [B] Reject [C] Need more info

───────────────────────────────────────────────────────────────────────────────
⚠️  I cannot proceed until assumptions are validated.
═══════════════════════════════════════════════════════════════════════════════
```

### Ungrounded Claim Alert Template

```
═══════════════════════════════════════════════════════════════════════════════
⚠️  UNGROUNDED CLAIMS DETECTED
═══════════════════════════════════════════════════════════════════════════════

The following claims could not be verified from available sources:

CLAIM C-001: [Statement]
  └─ Required for: [What analysis needs this]
  └─ Searched: [Sources checked]
  └─ Action needed: [Find source / Remove claim / Mark as assumption]

CLAIM C-002: [Statement]
  └─ Required for: [What analysis needs this]
  └─ Searched: [Sources checked]
  └─ Action needed: [Find source / Remove claim / Mark as assumption]

───────────────────────────────────────────────────────────────────────────────
OPTIONS:
  [A] Provide additional sources for these claims
  [B] Convert to [ASSUMED] and validate
  [C] Remove claims from analysis
  [D] Search for additional sources
═══════════════════════════════════════════════════════════════════════════════
```

---

## Quality Standards

### Source Quality Tiers

| Tier | Source Type | Confidence | Usage |
|------|-------------|------------|-------|
| 1 | Official docs, source code, API specs | HIGH | Primary evidence |
| 2 | Team blog posts, conference talks | MEDIUM | Supporting evidence |
| 3 | Third-party reviews, community posts | LOW | Context only |

### RFC Quality Gates

Before RFC can be finalized:
```
□ Summary ≤ 3 sentences
□ All gaps traced to research [GAP-XXX]
□ All sources cited [SRC-XXX]
□ Affected components reference spec sections
□ Existing/Proposed state shown for each change
□ At least 2 alternatives considered
□ No [UNGROUNDED] claims
□ All [ASSUMED] claims validated by user
□ Cross-referenced against ACP Summary
□ User explicitly approved
```

---

## Escalation Procedures

### When to Pause and Consult User

1. **Conflicting sources** — When sources disagree, present both and ask user
2. **Missing critical information** — Cannot complete analysis without it
3. **Scope creep detected** — Research expanding beyond original scope
4. **Technical uncertainty** — Multiple valid interpretations exist
5. **RFC conflicts** — Proposed changes may conflict with existing RFCs

### When to Abort Research

1. **No primary sources available** — Cannot verify any claims
2. **User requests abort** — At any point
3. **Target incompatible with ACP** — Fundamental design conflicts
4. **Ethical concerns** — Research reveals problematic aspects

---

## Summary of Prohibitions

| Prohibited Action | Required Alternative |
|-------------------|---------------------|
| Proceeding without confirmation | Wait for explicit user response |
| Claims without sources | Cite [SRC-XXX] for every claim |
| RFC before ACP summary | Create and approve summary first |
| Skipping phases | Execute all phases in sequence |
| Ungrounded final output | Verify or remove all [UNGROUNDED] |
| Assuming target capabilities | Verify with primary sources |
| Ignoring existing RFCs | Cross-reference all proposals |
| Auto-advancing through gates | Present findings and wait |
