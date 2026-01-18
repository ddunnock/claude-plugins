# Clarify Workflow Reference

Detailed workflow for the `/speckit.clarify` command with SEAMS-enhanced taxonomy, sequential questioning loop, and incremental spec updates.

## Purpose

Structured ambiguity resolution through targeted Q&A with immediate specification updates. Uses the SEAMS framework (Structure, Execution, Assumptions, Mismatches, Stakeholders) to systematically detect gaps. Each answer is validated and integrated atomically to prevent context loss.

## Key Characteristics

- **One question at a time**: Never reveal the queue
- **Multiple choice with recommendations**: Table format, prominently featured suggestion
- **"yes"/"recommended" acceptance**: Quick acceptance of suggested answers
- **5-question maximum per session**: Prevents fatigue (10 total across all sessions)
- **Atomic saves after each answer**: No context loss
- **Post-write validation**: 6-point checklist after each integration
- **13-category SEAMS-enhanced taxonomy**: Comprehensive coverage
- **Four-status coverage model**: Resolved/Deferred/Clear/Outstanding
- **Impact × Uncertainty prioritization**: Quantified selection formula

---

## Session Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Max questions per session | 5 | Prevent fatigue |
| Max questions total per spec | 10 | Diminishing returns |
| Answer format | ≤5 words OR option letter | Quick, focused answers |
| Queue visibility | Hidden | Prevent bias, maintain focus |
| Save frequency | After each answer | Prevent context loss |

---

## SEAMS Framework Integration

### What is SEAMS?

SEAMS is a gap analysis methodology examining specifications through five lenses:

| Lens | Focus | Detection Target |
|------|-------|------------------|
| **S**tructure | System boundaries, component cohesion | Unclear scope, undefined modules |
| **E**xecution | Runtime behavior, failure modes | Missing error handling, recovery strategies |
| **A**ssumptions | Implicit beliefs, unstated constraints | Hidden dependencies, organizational assumptions |
| **M**ismatches | Gaps between requirements and design | Orphan tasks, uncovered requirements |
| **S**takeholders | Different user perspectives | Missing operator, security, end-user views |

### 13-Category Taxonomy

The taxonomy maps SEAMS lenses to specific detection categories:

| Category | Group | SEAMS Lens | Status Markers |
|----------|-------|------------|----------------|
| SCOPE | Functional | Structure | `[TBD]`, "etc.", "might include" |
| BEHAVIOR | Functional | Execution | "should", "might", "probably" |
| SEQUENCE | Functional | - | "before/after" ambiguity |
| AUTHORITY | Functional | - | "someone", "appropriate person" |
| DATA | Data/Integration | Mismatch | Undefined formats, missing rules |
| INTERFACE | Data/Integration | Stakeholder | Missing contracts, protocols |
| CONSTRAINT | Data/Integration | Assumption | Undefined limits, implicit bounds |
| TEMPORAL | Data/Integration | - | "soon", "quickly", "periodically" |
| ERROR | Quality/Ops | Execution | Missing error handling |
| RECOVERY | Quality/Ops | Execution | No fallback specified |
| ASSUMPTION | Quality/Ops | Assumption | Unstated dependencies |
| STAKEHOLDER | Quality/Ops | Stakeholder | Missing viewpoints |
| TRACEABILITY | Quality/Ops | Mismatch | Orphan tasks, uncovered reqs |

---

## Prerequisites

This workflow expects:

1. **Spec file exists** - If missing, instruct user to run `/specify` first
2. **Memory directives loaded** - From `/speckit.init`
3. **Git clean state** - Warn if uncommitted changes exist

---

## Detailed Workflow Steps

### Step 1: Initialize Context

**Actions:**
1. Load spec file into memory (maintain in-memory representation)
2. Load directive files from `.claude/memory/`
3. Check for existing `## Clarifications` section in spec
4. Count previously answered questions (toward 10 total limit)

**Context Loading Output:**
```
Loading clarification context...

Spec: speckit/spec.md (145 lines)
Existing clarifications: 3 (from 2024-01-14 session)
Questions remaining: 7 of 10 total

Directives loaded:
- constitution.md ✓
- security.md ✓
- typescript.md ✓
- react-nextjs.md ✓

SEAMS lenses activated: Structure, Execution, Stakeholders
```

### Step 2: SEAMS Coverage Scan

Run detection across all 13 categories. Produce internal coverage map:

```
Coverage Map (INTERNAL - do not output to user):

| Category | Status | Candidate Qs | Impact | Uncertainty | Score |
|----------|--------|--------------|--------|-------------|-------|
| SCOPE | Partial | 2 | 4 | 3 | 12 |
| BEHAVIOR | Missing | 3 | 5 | 5 | 25 |
| DATA | Clear | 0 | - | - | - |
| ERROR | Missing | 2 | 4 | 4 | 16 |
| ASSUMPTION | Partial | 1 | 3 | 4 | 12 |
| RECOVERY | Missing | 1 | 5 | 5 | 25 |
| [etc.] |
```

**Status definitions:**
- **Clear**: Sufficient detail, no ambiguity detected
- **Partial**: Some detail exists but gaps remain
- **Missing**: No specification, critical gap

### Step 3: Generate Prioritized Queue

Build internal queue (max 5 questions). **Never reveal queue to user.**

**Prioritization Formula:**
```
Priority Score = Impact × Uncertainty
```

| Factor | Scale | Meaning |
|--------|-------|---------|
| Impact | 1-5 | Effect on architecture, tasks, tests, UX, ops, compliance |
| Uncertainty | 1-5 | Current ambiguity level |

**Selection Rules:**
1. Only include questions whose answers **materially impact** implementation
2. Favor HIGH impact categories over multiple LOW impact questions
3. Ensure category balance (max 2 questions per category)
4. Exclude questions already answered in previous sessions
5. Exclude plan-level execution details unless blocking correctness
6. If >5 candidates, select top 5 by Priority Score

**Example Queue (internal):**
```
Priority Queue (5 questions):

1. [BEHAVIOR] Authentication method - Score: 25
2. [RECOVERY] Payment failure handling - Score: 25
3. [ERROR] API timeout behavior - Score: 16
4. [SCOPE] User management boundaries - Score: 12
5. [ASSUMPTION] Deployment environment - Score: 12
```

### Step 4: Sequential Questioning Loop

Present **EXACTLY ONE** question at a time. Wait for answer before proceeding.

#### For Multiple-Choice Questions (2-5 options)

1. **Analyze all options** based on:
   - Best practices for project type
   - Risk reduction (security, performance, maintainability)
   - Alignment with project goals in spec
   - Loaded directive requirements

2. **Determine recommended option** with reasoning

3. **Present using table format:**

```
CLARIFY-004 [BEHAVIOR]
Impact: HIGH | Affects: Authentication architecture, TASK-001 through TASK-005

The specification states "users can authenticate" but doesn't specify
the authentication method. This decision affects security posture,
user experience, and multiple implementation tasks.

Which authentication method should be used?

**Recommended:** Option A - OAuth 2.0 with Google/GitHub
Reasoning: Industry standard for web apps, eliminates password management
burden, well-documented patterns for Next.js stack. Aligns with security.md
requirement for "proven authentication."

| Option | Description |
|--------|-------------|
| A | OAuth 2.0 with Google/GitHub providers |
| B | Email/password with JWT tokens |
| C | Magic link (passwordless) |
| Short | Provide a different short answer (≤5 words) |

Reply with the option letter (e.g., "A"), accept the recommendation
by saying "yes" or "recommended", or provide your own short answer.
```

#### For Short-Answer Questions (no discrete options)

```
CLARIFY-005 [CONSTRAINT]
Impact: MEDIUM | Affects: File upload feature, storage costs

The spec mentions file uploads but doesn't specify size limits.

What is the maximum file upload size?

**Suggested:** 10 MB
Reasoning: Balances usability with server resource constraints.
Common default for web applications. Can be increased later if needed.

Format: Short answer (≤5 words).
Reply "yes" or "suggested" to accept, or provide your own answer.
```

### Step 5: Process Answer

After user responds:

#### 5.1 Parse Response

| User Says | Interpretation |
|-----------|----------------|
| "yes", "recommended", "suggested" | Use stated recommendation |
| "A", "B", "C" (letter) | Map to that option |
| Short text (≤5 words) | Use as custom answer |
| Ambiguous/unclear | Ask for clarification (same question, doesn't count as new) |
| "done", "stop", "proceed" | End session |

#### 5.2 Validate Answer

- If option letter, verify it exists in presented options
- If short text, verify ≤5 words
- If invalid, request clarification without incrementing question count

#### 5.3 Record in Working Memory

Store validated answer for spec integration.

### Step 6: Incremental Spec Integration

**Immediately after each accepted answer**, update spec atomically.

#### 6.1 Ensure Clarifications Section

If first answer in this session and section doesn't exist:

```markdown
## Clarifications

### Session 2024-01-15
- Q: Authentication method? → A: OAuth 2.0 with Google/GitHub
```

If section exists, append under today's date heading (create if new date).

#### 6.2 Append Q&A Bullet

```markdown
- Q: [question summary] → A: [final answer]
```

#### 6.3 Apply to Appropriate Section

| Answer Type | Target Section | Action |
|-------------|----------------|--------|
| Functional behavior | Functional Requirements | Add/update bullet |
| User interaction | User Stories or Actors | Clarify role/scenario |
| Data shape/entity | Data Model | Add fields, types, relationships |
| Non-functional | Quality Attributes | Convert vague → metric |
| Edge case/negative | Edge Cases / Error Handling | Add new bullet |
| Terminology | Throughout | Normalize, note "(formerly X)" once |

#### 6.4 Remove Contradictions

If clarification invalidates earlier text, **replace** it. Do not leave contradictory statements.

#### 6.5 Save Atomically

Write spec file immediately after integration. Do not batch saves.

### Step 7: Post-Write Validation

**After EACH write**, verify:

```
Post-Write Validation Checklist:

- [ ] Clarifications section: exactly one bullet per accepted answer
- [ ] Question IDs: no duplicates
- [ ] Placeholders: updated sections have no lingering [TBD] the answer resolved
- [ ] Contradictions: no earlier statement conflicts with new clarification
- [ ] Markdown: valid structure, only allowed headings (## Clarifications, ### Session YYYY-MM-DD)
- [ ] Terminology: consistent across all updated sections
```

If any check fails, correct before proceeding to next question.

### Step 8: Loop Continuation/Termination

**Continue** to next question if:
- Queue has remaining questions
- Session limit (5) not reached
- User hasn't signaled completion

**Terminate** when ANY of these occur:
1. All critical ambiguities resolved (remaining queue unnecessary)
2. User signals "done", "stop", "proceed", "no more", "good"
3. Reached 5 questions for this session
4. No valid questions existed (full coverage from start)

---

## Coverage Summary (End of Session)

Report using four-status taxonomy:

### Status Definitions

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✓ | Resolved | Was Partial/Missing, now addressed by this session |
| ○ | Clear | Already sufficient, no question needed |
| ◐ | Deferred | Exceeds quota or better suited for planning phase |
| ⚠ | Outstanding | Still Partial/Missing, HIGH impact, needs attention |

### Summary Template

```markdown
## Clarification Session Complete

### Session Statistics
- Questions asked: 5
- Path to updated spec: speckit/spec.md
- Sections touched: Authentication, Data Model, Error Handling

### Coverage Summary

| Category | Status | Notes |
|----------|--------|-------|
| SCOPE | ✓ Resolved | Was Partial, addressed in CLARIFY-004 |
| BEHAVIOR | ✓ Resolved | Was Missing, addressed in CLARIFY-004, CLARIFY-006 |
| DATA | ○ Clear | Already sufficient |
| ERROR | ◐ Deferred | Exceeds quota, address in next session |
| ASSUMPTION | ○ Clear | Already sufficient |
| STAKEHOLDER | ○ Clear | Already sufficient |
| RECOVERY | ⚠ Outstanding | Still Missing, HIGH impact |

**Legend:**
- ✓ Resolved: Was Partial/Missing, now addressed
- ○ Clear: Already sufficient
- ◐ Deferred: Exceeds quota or better for planning
- ⚠ Outstanding: Still unresolved, needs attention

### Recommendation

[If Outstanding with HIGH impact:]
⚠ RECOVERY category remains unresolved with HIGH impact.
Consider running `/clarify` again before `/plan`.

[If all critical resolved:]
All critical ambiguities resolved. Proceed to `/plan`.

### Suggested Next Command
`/plan` - Create technical implementation plan
```

---

## Pre-Question Research

### When to Research

| Trigger | Research Focus |
|---------|----------------|
| CRITICAL + Security | CVEs, OWASP guidelines, compliance |
| CRITICAL + Performance | Benchmarks, scaling patterns |
| HIGH + Architecture | Design patterns, framework recommendations |
| HIGH + Integration | API standards, protocol versions |

### Research Process

1. Identify tech stack from loaded directives
2. Formulate query: `[topic] best practices [tech stack] 2024`
3. Look for:
   - Industry standard approaches
   - Known pitfalls and anti-patterns
   - Security advisories
   - Performance benchmarks

### Incorporating Research

Include in recommendation reasoning:

```
**Recommended:** Option A - OAuth 2.0 with PKCE
Reasoning: Current OAuth 2.0 security best practice (RFC 7636) recommends
PKCE for public clients. Next.js auth libraries have built-in support.
OWASP recommends this for SPA authentication.
```

---

## Spec Update Format

### Clarifications Section

```markdown
## Clarifications

### Session 2024-01-15
- Q: Authentication method? → A: OAuth 2.0 with Google/GitHub
- Q: File upload size limit? → A: 10 MB maximum
- Q: Session timeout? → A: 24 hours with sliding expiry

### Session 2024-01-14
- Q: User roles scope? → A: Full RBAC with custom roles
- Q: Data retention period? → A: 7 years for compliance
```

### Inline Traceability

When updating spec sections:

```markdown
## Authentication

Users authenticate via OAuth 2.0 with Google and GitHub providers.
New users are created on first successful OAuth login. Sessions use
HTTP-only secure cookies with 24-hour sliding expiry.
*(Clarified: CLARIFY-004, CLARIFY-006)*
```

---

## Ralph Loop Mode

### Autonomous Clarification

When `--ralph` flag is used:

```
/clarify --ralph                    # Until CRITICAL/HIGH resolved
/clarify --ralph --confidence 90    # Until 90% coverage
/clarify --ralph --categories "SECURITY,DATA"
```

### Exit Criteria

Loop exits when ANY condition met:
1. All CRITICAL and HIGH ambiguities resolved
2. Coverage confidence reaches threshold
3. All specified category ambiguities resolved
4. Hard limit of 10 questions reached

### Ralph Loop Prompt

```
/ralph-loop "Perform structured ambiguity resolution.

For each iteration:
1. Scan spec (SEAMS taxonomy)
2. Select highest priority (Impact × Uncertainty)
3. Research if HIGH/CRITICAL
4. Present ONE question (table format, recommendation)
5. Wait for user answer
6. Parse: 'yes'/'recommended' → use suggestion
7. Validate answer
8. Integrate into spec immediately
9. Save atomically
10. Run 6-point validation

Exit when:
- All CRITICAL/HIGH resolved, OR
- Coverage >= threshold, OR
- 10 questions asked

Output: <promise>SPEC_CLARITY_ACHIEVED</promise>"
--completion-promise "SPEC_CLARITY_ACHIEVED" --max-iterations 15
```

---

## Idempotency

### Question Tracking

Questions tracked by content hash to prevent re-asking:

```
hash = sha256(category + location + question_text_normalized)
```

### Skip Logic

On subsequent runs:
1. Load Clarifications section from spec
2. Build set of answered question hashes
3. Exclude from candidate queue
4. Only present new/changed ambiguities

### Re-ask Conditions

Re-ask when:
- Content at location changed significantly
- User explicitly requests (`--force`)
- Category reclassified

---

## Integration Points

### From /speckit.analyze

```
Analysis found 15 ambiguities (3 CRITICAL, 5 HIGH).
Run /speckit.clarify to resolve before implementation? [Y/n]
```

### To /speckit.plan

Clarifications enable planning:
```
All CRITICAL ambiguities resolved.
Ready for /speckit.plan
```

### To Spec File

Direct updates with traceability:
```markdown
## Clarifications
### Session 2024-01-15
- Q: Auth method? → A: OAuth 2.0
```

---

## Behavior Rules Summary

| Condition | Action |
|-----------|--------|
| No spec file | Instruct: run `/specify` first |
| No ambiguities | Report "No critical ambiguities", suggest proceeding |
| Full coverage | Output compact summary (all Clear), suggest `/plan` |
| User says "skip" | Warn rework risk increases, allow proceeding |
| Quota reached + HIGH unresolved | Flag as Deferred, recommend another session |
| Ambiguous answer | Request clarification (same question, no count increment) |

---

## Command Options

```bash
# Interactive mode (default)
/speckit.clarify

# Clarify specific spec
/speckit.clarify spec.md

# Focus on category
/speckit.clarify --category SECURITY
/speckit.clarify --category BEHAVIOR,DATA

# Autonomous mode
/speckit.clarify --ralph
/speckit.clarify --ralph --confidence 90
/speckit.clarify --ralph --categories "SECURITY,DATA"

# Force re-ask answered questions
/speckit.clarify --force

# Show coverage without asking
/speckit.clarify --status
```

---

## Continuation Format

See [continuation-format.md](../continuation-format.md) for the standard format template.

### Next Step Logic for /clarify

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| All CRITICAL resolved | `/plan` | Create implementation plan |
| Outstanding HIGH items | `/clarify` (another session) | Continue clarification |
| Deferred items only | `/plan` | Can proceed, revisit later |
| No ambiguities | `/plan` | Spec is clear |

### Example Output

```markdown
## ▶ Next Up
**plan: Create Plan** — Generate implementation plan with ADRs from clarified spec
`/plan`
<sub>`/clear` first → fresh context window</sub>
```
