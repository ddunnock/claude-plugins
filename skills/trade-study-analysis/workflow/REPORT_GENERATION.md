# Report Generation Workflow

Workflow guide for Steps 10-12 of the trade study process (finalization).

---

## MANDATORY BEHAVIORAL REQUIREMENTS

**Report generation CANNOT proceed without:**
1. All prior workflow gates completed and approved
2. Complete assumption review and approval
3. Explicit diagram selection by user
4. Final report structure approval

**PROHIBITED:**
- Generating reports with pending assumptions
- Auto-including all diagrams
- Making recommendations not supported by sources
- Including any ungrounded claims

---

## Phase 1: Pre-Finalization Gate Check

### MANDATORY — Verify all prerequisites

```
═══════════════════════════════════════════════════════════════════════════════
🔒 PRE-FINALIZATION GATE CHECK
═══════════════════════════════════════════════════════════════════════════════

Verifying all prerequisites for report generation:

───────────────────────────────────────────────────────────────────────────────
WORKFLOW COMPLETION STATUS:
───────────────────────────────────────────────────────────────────────────────

  □ Step 1: Problem Statement         [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 2: Root Cause Analysis       [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 3: Source Registration       [✓ COMPLETE / ⚠️ GAPS EXIST]
  □ Step 4: Alternative Data          [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 5: Criteria Definition       [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 6: Weight Assignment         [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 7: Normalization             [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 8: Scoring Results           [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]
  □ Step 9: Sensitivity Analysis      [✓ APPROVED / ⚠️ PENDING / ❌ BLOCKED]

───────────────────────────────────────────────────────────────────────────────
BLOCKING ISSUES (must resolve before proceeding):
───────────────────────────────────────────────────────────────────────────────

  [List any blocking issues here]

───────────────────────────────────────────────────────────────────────────────

⛔ If ANY step shows PENDING or BLOCKED, I CANNOT proceed to report generation.
   Please complete all prior steps first.

═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 2: Comprehensive Assumption Review

### MANDATORY — ALL assumptions must be resolved before report

```
═══════════════════════════════════════════════════════════════════════════════
⚠️  MANDATORY ASSUMPTION REVIEW
═══════════════════════════════════════════════════════════════════════════════

Before generating the report, you MUST review and approve all assumptions.

───────────────────────────────────────────────────────────────────────────────
ASSUMPTION SUMMARY:
───────────────────────────────────────────────────────────────────────────────

  TOTAL ASSUMPTIONS: [N]
  
  By Category:
    • Data Assumptions: [n]
    • Methodology Assumptions: [n]
    • Scope Assumptions: [n]
    • Source Interpretation: [n]
    • Weight Rationale: [n]
    • Sensitivity Parameters: [n]

  By Status:
    • APPROVED: [n]
    • PENDING: [n] ⚠️ MUST RESOLVE
    • REJECTED: [n]

═══════════════════════════════════════════════════════════════════════════════
DETAILED ASSUMPTION LIST:
═══════════════════════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────────────────────
DATA ASSUMPTIONS:
───────────────────────────────────────────────────────────────────────────────

A-001: [Description]
  Category: Data
  Made during: Data Collection (Step 4)
  Basis: [Source or "User judgment"]
  Impact if wrong: [Low/Medium/High] — [explanation]
  Status: [APPROVED ✓ / PENDING ⚠️]
  
  Your action: [A] Approve  [B] Reject  [C] Modify: _______________

A-002: [Description]
  Category: Data
  Made during: [Step]
  Basis: [Source or basis]
  Impact if wrong: [assessment]
  Status: [status]
  
  Your action: [A] Approve  [B] Reject  [C] Modify: _______________

[Continue for all data assumptions]

───────────────────────────────────────────────────────────────────────────────
METHODOLOGY ASSUMPTIONS:
───────────────────────────────────────────────────────────────────────────────

A-010: [Description]
  Category: Methodology
  Made during: [Step]
  Basis: [Source or basis]
  Impact if wrong: [assessment]
  Status: [status]
  
  Your action: [A] Approve  [B] Reject  [C] Modify: _______________

[Continue for all methodology assumptions]

───────────────────────────────────────────────────────────────────────────────
WEIGHT RATIONALE ASSUMPTIONS:
───────────────────────────────────────────────────────────────────────────────

A-020: [Description]
  Category: Weight Rationale
  Made during: Weight Assignment (Step 6)
  Basis: [Source or basis]
  Impact if wrong: [assessment]
  Status: [status]
  
  Your action: [A] Approve  [B] Reject  [C] Modify: _______________

[Continue for all weight assumptions]

───────────────────────────────────────────────────────────────────────────────
SOURCE INTERPRETATION ASSUMPTIONS:
───────────────────────────────────────────────────────────────────────────────

A-030: [Description]
  Category: Source Interpretation
  Made during: [Step]
  Source being interpreted: [Source name]
  Interpretation: [What was assumed about source content]
  Impact if wrong: [assessment]
  Status: [status]
  
  Your action: [A] Approve  [B] Reject  [C] Modify: _______________

[Continue for all interpretation assumptions]

═══════════════════════════════════════════════════════════════════════════════
UNGROUNDED CLAIMS:
═══════════════════════════════════════════════════════════════════════════════

The following statements in the analysis lack source documentation:

1. "[Claim text]"
   Used in: [Where this appears]
   Action required:
     [A] Provide source: _______________________________________________
     [B] Remove from report
     [C] Accept as user-provided assertion

2. "[Claim text]"
   Used in: [Where this appears]
   Action required: [A/B/C] _______________________________________________

═══════════════════════════════════════════════════════════════════════════════
FINAL ASSUMPTION CONFIRMATION:
═══════════════════════════════════════════════════════════════════════════════

PENDING ASSUMPTIONS REMAINING: [N]

To proceed, you must either:
  [A] APPROVE ALL PENDING — Accept all remaining assumptions as stated
  [B] ADDRESS INDIVIDUALLY — Respond to each pending assumption above
  [C] CANCEL — Return to analysis to reduce assumptions

Your selection: _______________________________________________

If [A], confirm: "I accept responsibility for all approved assumptions" [Y/N]

⛔ I CANNOT generate the report until ALL assumptions are resolved.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 3: Diagram Selection

### MANDATORY — User must explicitly select diagrams to include

```
═══════════════════════════════════════════════════════════════════════════════
📊 OUTPUT DIAGRAM SELECTION — Required
═══════════════════════════════════════════════════════════════════════════════

Select which diagrams to include in the final report.

I will ONLY generate the diagrams you select.

═══════════════════════════════════════════════════════════════════════════════
AVAILABLE DIAGRAMS:
═══════════════════════════════════════════════════════════════════════════════

DECISION ANALYSIS DIAGRAMS:
───────────────────────────────────────────────────────────────────────────────
  □ [1] DECISION MATRIX HEATMAP
        Shows: All scores in colored grid format
        Best for: Executive summary, quick overview
        
  □ [2] SCORE COMPARISON BAR CHART
        Shows: Horizontal bars comparing alternatives
        Best for: Clear ranking visualization
        
  □ [3] RADAR/SPIDER CHART
        Shows: Multi-dimensional comparison overlay
        Best for: Showing strengths/weaknesses across criteria

WEIGHT ANALYSIS DIAGRAMS:
───────────────────────────────────────────────────────────────────────────────
  □ [4] CRITERIA WEIGHT PIE CHART
        Shows: Weight distribution as pie segments
        Best for: Showing relative importance
        
  □ [5] WEIGHT COMPARISON BAR CHART
        Shows: Side-by-side weight bars
        Best for: Comparing weights directly

SENSITIVITY ANALYSIS DIAGRAMS:
───────────────────────────────────────────────────────────────────────────────
  □ [6] TORNADO DIAGRAM
        Shows: Sensitivity ranking by parameter
        Best for: Identifying decision drivers
        Requires: Tornado analysis was performed
        
  □ [7] MONTE CARLO WIN FREQUENCY CHART
        Shows: Win probability histogram
        Best for: Showing confidence in decision
        Requires: Monte Carlo analysis was performed
        
  □ [8] BREAKEVEN ANALYSIS CHART
        Shows: Weight thresholds to flip decision
        Best for: Showing decision robustness
        Requires: Breakeven analysis was performed

ROOT CAUSE ANALYSIS DIAGRAMS:
───────────────────────────────────────────────────────────────────────────────
  □ [9] FISHBONE (ISHIKAWA) DIAGRAM
        Shows: Cause categories from fishbone analysis
        Requires: Fishbone analysis was performed
        
  □ [10] 5 WHYS CHAIN DIAGRAM
        Shows: Causal chain visualization
        Requires: 5 Whys analysis was performed

DATA QUALITY DIAGRAMS:
───────────────────────────────────────────────────────────────────────────────
  □ [11] SOURCE COVERAGE MATRIX
        Shows: Which data points have documented sources
        Best for: Audit trail, data quality transparency
        
  □ [12] CONFIDENCE LEVEL HEATMAP
        Shows: Data reliability by alternative/criterion
        Best for: Highlighting data uncertainty

═══════════════════════════════════════════════════════════════════════════════
SELECTION:
═══════════════════════════════════════════════════════════════════════════════

Enter diagram numbers to include (comma-separated): _______________

Example: 1, 2, 4, 6, 11

───────────────────────────────────────────────────────────────────────────────
DIAGRAM FORMAT OPTIONS:

  Output format:
    [A] PNG (high resolution images)
    [B] SVG (scalable vector graphics)
    [C] Both PNG and SVG

  Color scheme:
    [A] Default (blue/green/red)
    [B] Colorblind-friendly
    [C] Grayscale (for printing)
    [D] Custom: _______________________________________________

Your selections:
  Diagrams: _______________________________________________
  Format: _______________________________________________
  Colors: _______________________________________________

⚠️  I will ONLY generate the diagrams you select above.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 4: Report Structure Selection

### MANDATORY — User must confirm report structure

```
═══════════════════════════════════════════════════════════════════════════════
📄 REPORT STRUCTURE — Selection Required
═══════════════════════════════════════════════════════════════════════════════

Select the report structure and sections to include.

═══════════════════════════════════════════════════════════════════════════════
STANDARD SECTIONS:
═══════════════════════════════════════════════════════════════════════════════

  □ [A] EXECUTIVE SUMMARY (1-2 pages)
        Recommendation, key findings, decision confidence
        
  □ [B] INTRODUCTION
        Purpose, scope, methodology overview
        
  □ [C] PROBLEM STATEMENT
        Approved problem statement with root cause analysis
        
  □ [D] ALTERNATIVES DESCRIPTION
        Overview of each alternative evaluated
        
  □ [E] EVALUATION METHODOLOGY
        Criteria definitions, weights, scoring approach
        
  □ [F] DATA COLLECTION SUMMARY
        Sources used, data quality assessment, gaps noted
        
  □ [G] ANALYSIS RESULTS
        Decision matrix, scores, rankings
        
  □ [H] SENSITIVITY ANALYSIS
        Robustness assessment, key findings
        
  □ [I] FINDINGS AND RECOMMENDATION
        Conclusions based on analysis
        
  □ [J] ASSUMPTIONS AND LIMITATIONS
        Complete assumption list with status
        
  □ [K] SOURCE REFERENCES
        Complete bibliography of sources used
        
  □ [L] APPENDICES
        Detailed calculations, raw data, audit trail

═══════════════════════════════════════════════════════════════════════════════
SELECTION:
═══════════════════════════════════════════════════════════════════════════════

Which sections should be included?

  [1] FULL REPORT — Include all sections (A through L)
  [2] STANDARD REPORT — Sections A, C, E, G, H, I, J, K
  [3] EXECUTIVE BRIEF — Sections A, G, I only
  [4] CUSTOM — Select specific sections: _______________________________________________

Your selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
OUTPUT FORMAT:

  [A] Microsoft Word (.docx)
  [B] PDF
  [C] Markdown (.md)
  [D] HTML
  [E] Multiple formats (specify): _______________________________________________

Your selection: _______________________________________________

⚠️  I will NOT generate the report until you confirm structure and format.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 5: Source List Review

### MANDATORY — Present complete source list for verification

```
═══════════════════════════════════════════════════════════════════════════════
📚 SOURCE LIST — Final Review
═══════════════════════════════════════════════════════════════════════════════

The following sources will be cited in the report:

═══════════════════════════════════════════════════════════════════════════════
REGISTERED SOURCES:
═══════════════════════════════════════════════════════════════════════════════

[SRC-001] [Document Name]
  Type: [Datasheet/Test Report/Requirements/etc.]
  Version/Date: [version info]
  Used for: [List criteria/sections where cited]
  Citation count: [N] references in report

[SRC-002] [Document Name]
  Type: [type]
  Version/Date: [version info]
  Used for: [usage]
  Citation count: [N] references

[Continue for all sources]

═══════════════════════════════════════════════════════════════════════════════
USER-PROVIDED INFORMATION (no document):
═══════════════════════════════════════════════════════════════════════════════

[USR-001] User verbal input: [Description]
  Used for: [Where used]
  Citation: "User-provided, [date]"

[Continue for all user-provided items]

═══════════════════════════════════════════════════════════════════════════════
SOURCE COVERAGE SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

  Total sources: [N]
  Documented sources: [N] ([X]%)
  User-provided: [N] ([X]%)
  
  Claims with High confidence sources: [N]%
  Claims with Medium confidence sources: [N]%
  Claims with Low confidence sources: [N]%

═══════════════════════════════════════════════════════════════════════════════
CONFIRMATION:
═══════════════════════════════════════════════════════════════════════════════

  [A] SOURCE LIST APPROVED — Proceed with report generation
  [B] ADD SOURCES — I have additional sources to provide: _______________
  [C] CORRECT SOURCES — Fix these source entries: _______________
  [D] REMOVE SOURCES — Remove these sources: _______________

Your selection: _______________________________________________

⚠️  I will NOT generate the report until you approve the source list.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 6: Final Report Generation

### MANDATORY — Final confirmation before generation

```
═══════════════════════════════════════════════════════════════════════════════
✅ FINAL REPORT GENERATION — Confirmation
═══════════════════════════════════════════════════════════════════════════════

Ready to generate the trade study report.

═══════════════════════════════════════════════════════════════════════════════
REPORT SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

  Report Title: [Title]
  Report Structure: [Full/Standard/Executive/Custom]
  Sections Included: [List]
  Output Format: [Format(s)]
  
  Diagrams Selected: [N] diagrams
    [List selected diagrams]
  
  Diagram Format: [PNG/SVG/Both]
  Color Scheme: [Selection]

═══════════════════════════════════════════════════════════════════════════════
CONTENT SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

  Problem Statement: [First 50 chars...]
  Alternatives Evaluated: [N]
  Criteria Used: [N]
  
  Leading Alternative: [Name] (Score: [X.XX])
  Decision Confidence: [High/Medium/Low]

═══════════════════════════════════════════════════════════════════════════════
QUALITY METRICS:
═══════════════════════════════════════════════════════════════════════════════

  Assumptions: [N] total ([N] approved)
  Sources: [N] documented, [N] user-provided
  Data Confidence: [N]% high, [N]% medium, [N]% low
  Sensitivity Robustness: [High/Medium/Low]

═══════════════════════════════════════════════════════════════════════════════
FINAL CONFIRMATION:
═══════════════════════════════════════════════════════════════════════════════

By approving, you confirm:
  ✓ All assumptions have been reviewed and approved
  ✓ All sources have been verified
  ✓ The methodology and results are acceptable
  ✓ You take responsibility for the analysis conclusions

  [A] GENERATE REPORT — Create the final trade study report
  [B] MAKE CHANGES — Return to previous step: _______________
  [C] CANCEL — Do not generate report

Your selection: _______________________________________________

═══════════════════════════════════════════════════════════════════════════════
```

---

## Report Content Requirements

### Source Citation Format (MANDATORY in all report sections)

Every factual claim must include source attribution:

```
[Claim or data point]¹

───────────────────
¹ Source: [Document Name], [Section/Page], [Date]. Confidence: [High/Medium/Low]
```

Or inline:
```
Alternative A provides 150 Mbps throughput (Source: Vendor A Datasheet v2.3, 
Section 4.2, 2024-03-15; Confidence: High).
```

### Assumption Disclosure (MANDATORY)

The Assumptions and Limitations section must include:

```
ASSUMPTIONS MADE IN THIS ANALYSIS:

1. [Assumption ID]: [Full description]
   Basis: [Source or rationale]
   Impact if incorrect: [Assessment]
   Status: Approved by [user] on [date]

2. [Continue for all assumptions]

LIMITATIONS:

1. [Limitation description]
   Impact on conclusions: [Assessment]
   Mitigation: [How addressed or acknowledged]
```

---

## Prohibited Behaviors in This Workflow

| ❌ DO NOT | ✅ INSTEAD |
|-----------|-----------|
| Generate report with pending assumptions | Require all assumptions resolved first |
| Auto-include all diagrams | Present selection menu and await choice |
| Include recommendations without sources | Ensure all recommendations cite basis |
| Skip assumption summary | Always include complete assumption section |
| Omit source list | Always include full bibliography |
| State conclusions as facts | Qualify with confidence levels |
| Proceed without final confirmation | Require explicit approval to generate |
