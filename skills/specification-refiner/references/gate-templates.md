# Phase Gate Templates

Detailed templates for each phase gate. Use these exact formats when presenting phase completions.

## Table of Contents
- [Phase 0: ASSESS Gate](#phase-0-assess-gate)
- [Phase 1: INGEST Gate](#phase-1-ingest-gate)
- [Phase 2: ANALYZE Gate](#phase-2-analyze-gate)
- [Phase 3: CLARIFY Gate](#phase-3-clarify-gate)
- [Phase 4: PRESENT Gate](#phase-4-present-gate)
- [Phase 5: ITERATE Gate](#phase-5-iterate-gate)
- [Phase 6: SYNTHESIZE Gate](#phase-6-synthesize-gate)
- [Phase 7: OUTPUT Completion](#phase-7-output-completion)
- [Phase 8: VALIDATE Gate](#phase-8-validate-gate)

---

## Phase 0: ASSESS Gate

### Mode Selection Dialog

```
Based on initial assessment:
- Document size: [X pages / Y words]
- Domains identified: [list domains]
- Stakeholder count: [N stakeholders]
- Scope clarity: [Clear/Moderate/Ambiguous]

Recommended mode: [SIMPLE/COMPLEX]

Options:
1. Proceed with recommended mode
2. Override to SIMPLE mode
3. Override to COMPLEX mode
4. Explain the modes in more detail

Your choice:
```

### Gate Summary

```
PHASE 0 COMPLETE: ASSESSMENT

Mode selected: [SIMPLE/COMPLEX]
Document: [title]
Initial domains: [list]
Analysis approach: [description based on mode]

Questions raised: [count]
[List any initial questions]

Ready to proceed to Phase 1 (INGEST)?
```

---

## Phase 1: INGEST Gate

```
PHASE 1 COMPLETE: INGESTION

Document: [title]
Type: [spec/requirements/architecture/plan]
Mode: [SIMPLE/COMPLEX]
Sections identified: [count]
- [Section 1]
- [Section 2]
- ...

Key entities/components: [list]
Dependencies noted: [count]

QUESTIONS STATUS:
- Unanswered: [count]
  [List each with ID and brief text]
- Answered this phase: [count]
- New questions raised: [count]
  [List each new question]

Ready to proceed to Phase 2 (ANALYZE)?
```

---

## Phase 2: ANALYZE Gate

```
PHASE 2 COMPLETE: ANALYSIS

Analysis approach: [SEAMS only / SEAMS + Critical Path]

PRELIMINARY FINDINGS:
- Critical: [count]
- High: [count]
- Medium: [count]
- Low: [count]

Top issues identified:
1. [Brief description of most critical]
2. [Brief description of second]
3. [Brief description of third]

QUESTIONS STATUS:
- Unanswered: [count]
  [List with ID, question, and what it blocks]
- Answered this phase: [count]
- New questions raised: [count]
  [List each new question]

Blocked findings: [count findings waiting on question answers]

Ready to proceed to Phase 3 (CLARIFY) for ambiguity resolution?
```

---

## Phase 3: CLARIFY Gate

### Sequential Question Format

Present ONE question at a time using constrained answer formats:

```
CLARIFY-[NNN] [CATEGORY]

[Context: 1-2 sentences explaining what triggered this question]

**Question**: [The specific question]

**Recommended:** Option [X] - [1-2 sentence reasoning based on best practices, risk reduction, or project context]

| Option | Description |
|--------|-------------|
| A | [Option A description] |
| B | [Option B description] |
| C | [Option C description] |
| D | [Option D description] (if needed) |
| Short | Provide a different short answer (≤5 words) |

Reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.
```

### After Each Answer

```
✓ Integrated: [Brief description of how answer was applied]

[Question count] of 5 this session | [Total count] of 10 total
```

### Coverage Map (After Each Question)

```
COVERAGE MAP:
| Category | Status | Notes |
|----------|--------|-------|
| Functional Scope | [Clear/Partial/Missing] | [Brief note] |
| Domain & Data | [Clear/Partial/Missing] | [Brief note] |
| Interaction & UX | [Clear/Partial/Missing] | [Brief note] |
| Non-Functional | [Clear/Partial/Missing] | [Brief note] |
| Integration | [Clear/Partial/Missing] | [Brief note] |
| Edge Cases | [Clear/Partial/Missing] | [Brief note] |
| Constraints | [Clear/Partial/Missing] | [Brief note] |
| Terminology | [Clear/Partial/Missing] | [Brief note] |
| Completion Signals | [Clear/Partial/Missing] | [Brief note] |
| Assumptions | [Clear/Partial/Missing] | [Brief note] |
| Misc | [Clear/Partial/Missing] | [Brief note] |
```

### Gate Summary

```
PHASE 3 COMPLETE: CLARIFICATION

Questions asked this session: [count] / 5
Total questions across analysis: [count] / 10

COVERAGE STATUS:
- Clear: [count] categories
- Partial: [count] categories
- Missing: [count] categories

KEY CLARIFICATIONS:
1. [CLARIFY-001]: [Question summary] → [Answer]
2. [CLARIFY-002]: [Question summary] → [Answer]
...

REMAINING AMBIGUITIES:
[List any unresolved items with category and severity]

Options:
1. Proceed to Phase 4 (PRESENT) with current clarity
2. Ask additional questions (if quota remains)
3. Mark remaining ambiguities as assumptions

Your choice:
```

---

## Phase 4: PRESENT Gate

```
PHASE 4 COMPLETE: PRESENTATION

FINDINGS SUMMARY:
- Critical: [count] ([resolved count] have remediations selected)
- High: [count]
- Medium: [count]
- Low: [count]
Total: [count]

QUESTIONS STATUS:
- Unanswered: [count]
  [List remaining unanswered]
- Answered this phase: [count]
- Deferred: [count]

ASSUMPTIONS MADE: [count]
[List key assumptions with risk levels]

Options:
1. Proceed to Phase 5 (ITERATE) with new input/constraints
2. Skip to Phase 6 (SYNTHESIZE) if analysis is complete
3. Return to Phase 3 (CLARIFY) for more questions
4. Review specific findings in detail

Your choice:
```

---

## Phase 5: ITERATE Gate

```
PHASE 5 COMPLETE: ITERATION

Changes incorporated: [summary of user input]

DELTA ANALYSIS:
- New findings: [count]
- Modified findings: [count]
- Resolved findings: [count]
- Unchanged: [count]

Key changes:
1. [Most significant change]
2. [Second change]
3. [Third change]

QUESTIONS STATUS:
- Unanswered: [count]
- Answered this phase: [count]
- New questions raised: [count]

Options:
1. Continue iterating (more changes to incorporate)
2. Proceed to Phase 6 (SYNTHESIZE)
3. Return to Phase 4 to review updated findings
4. Return to Phase 3 (CLARIFY) for additional questions

Your choice:
```

---

## Phase 6: SYNTHESIZE Gate

### Full Summary Template

```
PHASE 6: SYNTHESIS SUMMARY

=== DOCUMENT OVERVIEW ===
Title: [document title]
Mode: [SIMPLE/COMPLEX]
Analysis iterations: [count]

=== FINDINGS RESOLUTION ===
Total findings: [count]

By severity:
- Critical: [count] → [resolved/unresolved breakdown]
- High: [count] → [resolved/unresolved breakdown]
- Medium: [count] → [resolved/unresolved breakdown]
- Low: [count] → [resolved/unresolved breakdown]

Key resolutions:
1. [Finding]: [Selected remediation]
2. [Finding]: [Selected remediation]
...

Unresolved findings: [count]
[List any critical/high that remain unresolved]

=== QUESTIONS STATUS ===
Total questions raised: [count]

Answered: [count]
[List key Q&A pairs]

Unanswered: [count]
[List with impact assessment]

Deferred: [count]
[List with deferral reason]

=== ASSUMPTIONS ===
Confirmed: [count]
Unverified (proceeding with): [count]
[List critical unverified assumptions]

=== PROPOSED OUTPUT STRUCTURE ===
[For SIMPLE]: Single refined specification document with sections listed
[For COMPLEX]: List of separate specification files per domain
```

### Approval Dialog

```
Ready to generate output?

Options:
1. Approve and proceed to Phase 7 (OUTPUT)
2. Return to Phase 5 to address unresolved items
3. Modify the proposed output structure
4. Return to Phase 3 (CLARIFY) for remaining questions

Your choice:
```

---

## Phase 7: OUTPUT Completion

```
PHASE 7 COMPLETE: OUTPUT GENERATED

Mode: [SIMPLE/COMPLEX]
All specifications generated with status: **Draft**

=== FILES CREATED ===

[For SIMPLE]:
- refined-specification.md (A-Spec with [N] requirements)

[For COMPLEX]:
A-Spec files:
- [domain1]-a-spec.md ([N] requirements)
- [domain2]-a-spec.md ([N] requirements)

B-Spec files:
- [domain1]-[subsystem1]-b-spec.md ([N] requirements)
- [domain1]-[subsystem2]-b-spec.md ([N] requirements)
- [domain2]-[subsystem1]-b-spec.md ([N] requirements)

Supporting files:
- traceability-matrix.md
- cross-cutting-concerns.md (if applicable)
- open-items.md

=== RTM SUMMARY === (COMPLEX mode)
- A-Spec requirements: [count]
- B-Spec requirements: [count]
- Coverage: [X]%
- Gaps identified: [count]

Analysis state saved to: analysis-state.md

Summary:
- Findings addressed: [count]
- Assumptions documented: [count]
- Open items for future: [count]

Ready to proceed to Phase 8 (VALIDATE) for final review and status advancement?
```

---

## Phase 8: VALIDATE Gate

### Validation Summary Template

```
PHASE 8: VALIDATION SUMMARY

=== SPECIFICATION STATUS ===
Current status: [Draft | Reviewed | Approved | Baselined]

Status by specification:
| Specification | Type | Status |
|---------------|------|--------|
| [spec-name] | A-Spec | [status] |
| [spec-name] | B-Spec | [status] |

Status history:
- Draft: [timestamp] - Generated in Phase 6
- [Subsequent status changes with timestamps and approvers]

=== TRACEABILITY VALIDATION === (COMPLEX mode)
A-Spec requirements: [count]
B-Spec requirements: [count]
Coverage: [X]%

Coverage breakdown:
| Category | Count | Percentage |
|----------|-------|------------|
| Fully covered | [count] | [X]% |
| Partially covered | [count] | [X]% |
| Not covered (GAP) | [count] | [X]% |

Gaps identified:
[List A-Spec requirements with no/partial B-Spec coverage]

=== COMPLETENESS CHECK ===
- [ ] All required sections present
- [ ] Cross-references valid
- [ ] Assumptions documented
- [ ] Open items captured
- [ ] Requirement IDs consistent
- [ ] Traces verified (COMPLEX mode)

Issues found: [count]
[List any completeness issues]

=== CONSISTENCY CHECK ===
- [ ] Terminology consistent across specs
- [ ] Formatting consistent
- [ ] Priority/severity scales aligned
- [ ] No conflicting requirements

Issues found: [count]
[List any consistency issues]

=== VALIDATION FINDINGS ===
Critical issues: [count]
[List any blocking issues that prevent status advancement]

Recommendations: [count]
[List suggested improvements]

=== STATUS ADVANCEMENT ===
Current status: [status]
Eligible for: [next status]

Requirements for advancement:
[For Draft → Reviewed]:
- No critical gaps in RTM coverage
- All completeness checks pass
- Technical review completed

[For Reviewed → Approved]:
- All high-priority issues resolved
- Stakeholder review completed
- No outstanding blockers

[For Approved → Baselined]:
- Formal approval documented
- Change control process established
- All specs finalized

Options:
1. Advance status to [next status]
2. Return to Phase 7 to regenerate specs
3. Return to Phase 5 to iterate on findings
4. Return to Phase 3 (CLARIFY) for remaining questions
5. Review specific findings in detail
6. Export validation report

Your choice:
```

### Status Change Confirmation

```
STATUS CHANGE CONFIRMATION

Changing status:
- Specification(s): [list]
- From: [current status]
- To: [new status]
- Reason: [user-provided or default reason]
- Approved by: [user identifier]
- Timestamp: [date/time]

Confirm status change? (Yes/No)
```

### Validation Complete Template

```
PHASE 8 COMPLETE: VALIDATION FINISHED

Final specification status: [Reviewed | Approved | Baselined]

Specifications:
[List all specs with final status]

RTM Coverage: [X]% (COMPLEX mode)
Validation findings addressed: [count]

Analysis complete. Specifications are [status] and ready for [next step based on status].

Output files:
- Specifications: [list]
- Traceability matrix: traceability-matrix.md (COMPLEX mode)
- Analysis state: analysis-state.md
```

---

## Finding Format Template

For EACH identified issue in Phase 3:

```markdown
## [ISSUE-ID]: [Brief Title]

**Category**: [Gap | Weakness | Inefficiency | Complication | Risk]
**Severity**: [Critical | High | Medium | Low]
**Confidence**: [High | Medium | Low]
**Blocked by**: [Question ID if applicable, or "None"]

### Description
[What the issue is and why it matters]

### Evidence
[Specific references to the source material]

### Impact
[What happens if unaddressed]

### Remediation Options
1. [Option A with trade-offs]
2. [Option B with trade-offs]
3. [Option C with trade-offs]

### Related Issues
[Cross-references to connected findings]
```
