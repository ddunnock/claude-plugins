# Problem Definition & Root Cause Analysis

Workflow guide for Steps 1-2 of the DAU 9-Step Trade Study Process.

---

## MANDATORY BEHAVIORAL REQUIREMENTS

Before proceeding with ANY action in this workflow:

1. **ASK, don't assume** — Every piece of information must come from explicit user input
2. **No confidence-based shortcuts** — Even if context seems clear, ask for confirmation
3. **Document all sources** — Every statement about the problem must cite its origin
4. **Track assumptions explicitly** — Any inference requires user approval

---

## Phase 1: Initial Context Gathering

### MANDATORY QUESTIONS — Do NOT proceed without answers

```
═══════════════════════════════════════════════════════════════════════════════
❓ PROBLEM DEFINITION — Initial Questions
═══════════════════════════════════════════════════════════════════════════════

I need to understand your situation before we define the problem statement.
Please answer ALL questions below.

───────────────────────────────────────────────────────────────────────────────
QUESTION 1: What triggered this trade study?

  [A] Performance issue observed in testing
  [B] Operational failure or degradation  
  [C] Stakeholder complaint or requirement
  [D] Technology obsolescence
  [E] Cost/schedule pressure
  [F] Regulatory or compliance need
  [G] Proactive capability improvement
  [H] Other (please describe): _______________________________________

Your selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 2: What is the domain/technical area?

Examples: RF Communications, Data Processing, Power Systems, Software, etc.

Your answer: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 3: What system or subsystem is affected?

Your answer: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 4: Who are the primary stakeholders?

List all affected parties (end users, operators, maintainers, etc.):

Your answer: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 5: Who has decision authority for the outcome?

Your answer: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 6: What are the known constraints?

  □ Budget limit: $_________________
  □ Schedule deadline: _________________
  □ Technical constraints: _________________
  □ Regulatory requirements: _________________
  □ Interface constraints: _________________
  □ Other: _________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 7: Do you have any documents to provide as context?

  [A] Yes — I will upload/describe them now
  [B] No — I will provide information verbally
  [C] I have some but not all needed documents

Your selection: _______________________________________________

⚠️  I will NOT proceed until you answer all questions above.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 2: Source Registration for Problem Context

### MANDATORY — Execute before analyzing any documents

```
═══════════════════════════════════════════════════════════════════════════════
📚 PROBLEM CONTEXT — SOURCE REGISTRATION
═══════════════════════════════════════════════════════════════════════════════

List all documents/sources informing the problem definition:

SOURCE 1:
  Name: _______________________________________________
  Type: [Requirements Doc / Issue Report / Stakeholder Input / Other]
  Date/Version: _______________________________________________
  Relevant sections: _______________________________________________
  How to access: [Uploaded / Described verbally / Reference only]

SOURCE 2:
  Name: _______________________________________________
  Type: _______________________________________________
  Date/Version: _______________________________________________
  Relevant sections: _______________________________________________
  How to access: _______________________________________________

[Add more as needed]

───────────────────────────────────────────────────────────────────────────────
MISSING SOURCES — What information do you need but don't have?

  □ Requirements documentation
  □ Test/performance data showing the problem
  □ Stakeholder input/feedback
  □ Historical analysis of similar issues
  □ Other: _______________________________________________

⚠️  Missing sources will be flagged as DATA GAPS in the analysis.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 3: Initial Problem Description Capture

### MANDATORY QUESTIONS — Capture user's understanding

```
═══════════════════════════════════════════════════════════════════════════════
❓ INITIAL PROBLEM CAPTURE
═══════════════════════════════════════════════════════════════════════════════

QUESTION 8: In your own words, describe the problem you're trying to solve.
            (2-4 sentences — what's happening and why it matters)

Your description:
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 9: How long has this problem existed?

  [A] Just discovered (days)
  [B] Weeks
  [C] Months  
  [D] Years
  [E] Since system inception
  [F] Unknown

Your selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 10: Have any solutions been attempted before?

  [A] No previous attempts
  [B] Yes — temporary fixes (describe): _______________________________
  [C] Yes — permanent fix attempted but failed (describe): _____________
  [D] Yes — currently under investigation

Your selection and details: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 11: What alternatives are you already considering?

Alternative 1: _______________________________________________
Alternative 2: _______________________________________________
Alternative 3: _______________________________________________
Additional: _______________________________________________

⚠️  I will NOT proceed until you answer all questions above.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 4: Root Cause Analysis

### MANDATORY — User must select analysis method

```
═══════════════════════════════════════════════════════════════════════════════
❓ ROOT CAUSE ANALYSIS — Method Selection
═══════════════════════════════════════════════════════════════════════════════

I can help identify the root cause using structured techniques.

Which method(s) would you like to use?

  [A] 5 WHYS ANALYSIS
      Best for: Linear cause-effect chains
      Process: Iteratively ask "Why?" until reaching root cause
      
  [B] FISHBONE (ISHIKAWA) ANALYSIS
      Best for: Complex problems with multiple contributing factors
      Process: Categorize causes across 6 dimensions
      
  [C] BOTH METHODS (recommended for complex problems)
      Process: Fishbone first to identify categories, then 5 Whys on key branches

Your selection: _______________________________________________

⚠️  I will NOT proceed until you select an analysis method.
═══════════════════════════════════════════════════════════════════════════════
```

### 5 Whys Process — MANDATORY user input at each level

```
═══════════════════════════════════════════════════════════════════════════════
🔬 5 WHYS ANALYSIS — Level [N]
═══════════════════════════════════════════════════════════════════════════════

PREVIOUS ANSWER: "[Previous user response]"
SOURCE: [Source cited by user, or "User-provided (no document)"]

───────────────────────────────────────────────────────────────────────────────

❓ WHY does "[previous answer]" occur?

Your answer: _______________________________________________

What source supports this answer?
  [A] [List registered sources for selection]
  [B] This is my direct knowledge/experience (no document)
  [C] I don't know — this is an assumption that needs verification

Source selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
DEPTH CHECK:

Have we reached the root cause?

  [A] YES — This is the fundamental cause; addressing it would prevent recurrence
  [B] NO — There's still a deeper "why" to explore
  [C] UNSURE — I need help determining if this is root cause

Your selection: _______________________________________________

⚠️  I will NOT proceed until you provide your answer and source.
═══════════════════════════════════════════════════════════════════════════════
```

### Fishbone Process — MANDATORY user input for each category

```
═══════════════════════════════════════════════════════════════════════════════
🔬 FISHBONE ANALYSIS — Category: [CATEGORY NAME]
═══════════════════════════════════════════════════════════════════════════════

CATEGORY: [Methods/Machines/Materials/Measurements/Environment/People]
DESCRIPTION: [Category description]

───────────────────────────────────────────────────────────────────────────────

What factors in this category contribute to the problem?

Factor 1: _______________________________________________
  Source: _______________________________________________

Factor 2: _______________________________________________
  Source: _______________________________________________

Factor 3: _______________________________________________
  Source: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
  [A] I have identified all relevant factors in this category
  [B] No factors in this category apply
  [C] I need help identifying factors — please ask clarifying questions

Your selection: _______________________________________________

⚠️  I will NOT proceed to the next category until you respond.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 5: Root Cause Confirmation

### MANDATORY — User must explicitly confirm root cause

```
═══════════════════════════════════════════════════════════════════════════════
✓ ROOT CAUSE CONFIRMATION
═══════════════════════════════════════════════════════════════════════════════

Based on our analysis, the identified root cause is:

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  [ROOT CAUSE STATEMENT]                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

SUPPORTING EVIDENCE:
  • [Evidence 1] (Source: [source])
  • [Evidence 2] (Source: [source])
  • [Evidence 3] (Source: [source])

ASSUMPTIONS MADE DURING ANALYSIS:
  • A-001: [Assumption] — Status: PENDING
  • A-002: [Assumption] — Status: PENDING

───────────────────────────────────────────────────────────────────────────────
CONFIRMATION REQUIRED:

  [A] CONFIRM — This root cause is correct
  [B] MODIFY — The root cause should be adjusted: _______________________
  [C] REJECT — This is not the root cause; let's re-analyze
  [D] ADD CONTEXT — I have additional information to provide

Your selection: _______________________________________________

⚠️  I will NOT proceed to problem statement generation until you confirm.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 6: Problem Statement Generation

### MANDATORY — Present options and await selection

```
═══════════════════════════════════════════════════════════════════════════════
📝 PROBLEM STATEMENT CANDIDATES
═══════════════════════════════════════════════════════════════════════════════

Based on the confirmed root cause, here are three candidate problem statements.
Each uses a different framing approach.

═══════════════════════════════════════════════════════════════════════════════
CANDIDATE #1: Technical Focus
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  [PROBLEM STATEMENT TEXT]                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Grounding:
  • "[Claim 1]" — Source: [source, section]
  • "[Claim 2]" — Source: [source, section]
  • "[Claim 3]" — Source: [source, section] OR "UNGROUNDED—user-provided"

Score: [XX/16]

═══════════════════════════════════════════════════════════════════════════════
CANDIDATE #2: Capability Gap Focus
═══════════════════════════════════════════════════════════════════════════════

[Same format as Candidate #1]

═══════════════════════════════════════════════════════════════════════════════
CANDIDATE #3: Stakeholder Impact Focus  
═══════════════════════════════════════════════════════════════════════════════

[Same format as Candidate #1]

═══════════════════════════════════════════════════════════════════════════════
SELECTION REQUIRED:
═══════════════════════════════════════════════════════════════════════════════

  [A] Select Candidate #1
  [B] Select Candidate #2
  [C] Select Candidate #3
  [D] Request modifications to a candidate: _______________________
  [E] Combine elements from multiple candidates: _______________________
  [F] None are acceptable — provide your own: _______________________

Your selection: _______________________________________________

⚠️  I will NOT proceed until you make a selection.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 7: Final Problem Statement Confirmation

### MANDATORY — Explicit approval required

```
═══════════════════════════════════════════════════════════════════════════════
✅ PROBLEM STATEMENT — FINAL CONFIRMATION
═══════════════════════════════════════════════════════════════════════════════

FINAL PROBLEM STATEMENT:

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  [FINAL PROBLEM STATEMENT TEXT]                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────────────
SOURCE GROUNDING:
───────────────────────────────────────────────────────────────────────────────

  • "[Element 1]" — Source: [source]
  • "[Element 2]" — Source: [source]  
  • "[Element 3]" — Source: [source] OR "User-provided"

───────────────────────────────────────────────────────────────────────────────
ASSUMPTIONS IN THIS STATEMENT:
───────────────────────────────────────────────────────────────────────────────

  • A-001: [Description] — Status: [PENDING/APPROVED]
  • A-002: [Description] — Status: [PENDING/APPROVED]

───────────────────────────────────────────────────────────────────────────────
QUALITY SCORE: [XX/16]
  Required criteria: [X/11] ✓
  Preferred criteria: [X/5]
───────────────────────────────────────────────────────────────────────────────

FINAL CONFIRMATION:

  [A] APPROVE — This problem statement is correct and complete
  [B] REVISE — Make these changes: _______________________
  [C] RESTART — Begin problem definition process again

Your selection: _______________________________________________

⚠️  Steps 3-12 are BLOCKED until you approve the problem statement.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Assumption Tracking

Every assumption made during problem definition must be logged:

```json
{
  "assumption_id": "A-001",
  "phase": "root_cause_analysis",
  "description": "The observed throughput degradation is caused by modem limitations rather than antenna issues",
  "basis": "User stated antenna was recently calibrated (verbal)",
  "source": "User-provided, no document",
  "impact_if_wrong": "Would invalidate modem-focused alternatives",
  "status": "pending",
  "user_response": null
}
```

---

## Prohibited Behaviors in This Workflow

| ❌ DO NOT | ✅ INSTEAD |
|-----------|-----------|
| Infer problem domain from context | Ask: "What is the domain/technical area?" |
| Assume stakeholders from system type | Ask: "Who are the primary stakeholders?" |
| Suggest root causes without user input | Ask: "Why does [X] occur?" and wait |
| Generate problem statement variations without confirmation | Present options and wait for selection |
| Proceed past any phase without explicit confirmation | Display confirmation prompt and wait |
| State facts without source citation | Always cite: "(Source: [document])" or "(User-provided)" |
| Fill in missing information | Flag as: "DATA GAP — requires user input" |
