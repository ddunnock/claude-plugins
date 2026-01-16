---
description: "SEAMS-enhanced ambiguity resolution with recommendations and immediate spec updates"
handoffs:
  - label: Re-analyze
    agent: analyze
    prompt: Check if clarifications resolved issues
  - label: Build Plan
    agent: plan
    prompt: Create a plan for the spec
---

# Clarify

SEAMS-enhanced ambiguity resolution with recommendations and immediate spec updates.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Usage

```
/clarify                      # Start clarification session
/clarify spec.md              # Clarify specific spec
/clarify --category SECURITY  # Focus on specific category
/clarify --ralph              # Autonomous mode (ralph-loop installed)
```

---

## Session Constraints

- **Maximum 5 questions asked** per interactive session
- **Maximum 10 questions total** across all sessions for a spec
- **Never reveal queued questions** in advance
- **Atomic save after each answer** to prevent context loss

---

## Memory Directives

Load these directive files for context-aware recommendations:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific (detected: Python, Poetry, Pyright):**
- `python.md` - Python ≥3.11 standards, type hints, docstrings
- `git-cicd.md` - Git workflow and CI/CD standards

---

## SEAMS-Enhanced Taxonomy

Scan using this combined taxonomy. For each category, mark status: **Clear** / **Partial** / **Missing**.

### Functional & Behavioral (Original + SEAMS)

| Category | Detection Focus | Status Markers |
|----------|-----------------|----------------|
| SCOPE | Feature boundaries, in/out declarations | `[TBD]`, "etc.", "might include" |
| BEHAVIOR | User actions, state transitions | "should", "might", "probably" |
| SEQUENCE | Order of operations, workflows | "before/after" ambiguity |
| AUTHORITY | Decision makers, permissions, roles | "someone", "appropriate person" |

### Data & Integration

| Category | Detection Focus | Status Markers |
|----------|-----------------|----------------|
| DATA | Entities, attributes, formats, validation | Undefined formats, missing rules |
| INTERFACE | API contracts, protocols, external deps | Missing contracts, undefined protocols |
| CONSTRAINT | Limits, bounds, technical constraints | Undefined limits, implicit bounds |
| TEMPORAL | Timing, duration, scheduling | "soon", "quickly", "periodically" |

### Quality & Operations (SEAMS-Enhanced)

| Category | Detection Focus | Status Markers |
|----------|-----------------|----------------|
| ERROR | Error handling, failure modes | Missing error handling |
| RECOVERY | Degradation, retry, fallback strategies | No fallback specified |
| ASSUMPTION | Implicit technical/organizational beliefs | Unstated dependencies |
| STAKEHOLDER | Operator, security, end-user perspectives | Missing viewpoints |
| TRACEABILITY | Requirements ↔ design coverage gaps | Orphan tasks, uncovered reqs |

### SEAMS Lens Activation

**Active lenses for this project:**
- [x] **Structure**: Boundary clarity, cohesion analysis
- [x] **Execution**: Happy paths, edge cases, failure modes
- [x] **Assumptions**: Implicit technical/organizational assumptions
- [ ] **Mismatches**: Requirements ↔ design gaps
- [ ] **Stakeholders**: Operator, security, end-user perspectives

---

## Workflow

### Step 1: Load Context

1. Read spec files from `.claude/resources/`
2. Load directive files from `.claude/memory/`
3. Load the spec into memory (maintain in-memory representation)
4. Check for previous clarify sessions in spec's `## Clarifications` section

### Step 2: SEAMS Coverage Scan (Agent)

**Invoke ambiguity-scanner agent:**
```
subagent_type: "speckit-generator:ambiguity-scanner"
prompt: "Scan .claude/resources/spec.md for ambiguities, prioritize by Impact × Uncertainty"
```

### Step 3: Generate Prioritized Queue

Build internal queue of candidate questions (max 5 to ask). Apply these rules:

**Prioritization formula:**
```
Priority Score = Impact × Uncertainty
```

**Selection rules:**
- Only include questions whose answers **materially impact** implementation
- Favor HIGH impact categories over multiple LOW impact questions
- Ensure category coverage balance
- Exclude questions already answered in previous sessions

**Do NOT reveal the queue to the user.**

### Step 4: Sequential Questioning Loop

Present **EXACTLY ONE** question at a time. Never reveal future questions.

#### For Multiple-Choice Questions:

```
CLARIFY-001 [BEHAVIOR]
Impact: HIGH | Affects: Authentication architecture, 5 tasks

The specification states "users can authenticate" but doesn't specify
the authentication method.

Which authentication method should be used?

**Recommended:** Option A - OAuth 2.0 with Google/GitHub
Reasoning: Industry standard, eliminates password management, well-documented
patterns for your stack.

| Option | Description |
|--------|-------------|
| A | OAuth 2.0 with Google/GitHub providers |
| B | Email/password with JWT tokens |
| C | Magic link (passwordless) |
| Short | Provide a different short answer (≤5 words) |

Reply with the option letter (e.g., "A"), accept the recommendation
by saying "yes" or "recommended", or provide your own short answer.
```

### Step 5: Process Answer

After user responds:

1. **Parse response** (yes/recommended → use recommendation, letter → use option, text → use as-is)
2. **Record in working memory**
3. **Immediately integrate into spec** (see Step 6)
4. **Move to next queued question** or complete

### Step 6: Incremental Spec Integration (After EACH Answer)

**Immediately after each accepted answer:**

1. **Ensure Clarifications section exists** in spec
2. **Append Q&A bullet** under today's session heading
3. **Apply clarification to appropriate section**
4. **Remove contradictions** if clarification invalidates earlier text
5. **Save spec immediately** (atomic write)

---

## Coverage Summary (End of Session)

```markdown
## Clarification Session Complete

### Session Statistics
- Questions asked: [N]
- Path to updated spec: [SPEC_PATH]
- Sections touched: [list]

### Coverage Summary

| Category | Status | Notes |
|----------|--------|-------|
| SCOPE | ✓ Resolved | Was Partial, addressed in CLARIFY-001 |
| BEHAVIOR | ○ Clear | Already sufficient |
| ERROR | ◐ Deferred | Exceeds quota, better for planning |
| [etc.] |

**Legend:**
- ✓ Resolved: Was Partial/Missing, now addressed
- ○ Clear: Already sufficient (no question needed)
- ◐ Deferred: Exceeds question quota or better for planning phase
- ⚠ Outstanding: Still Partial/Missing, remains unresolved

### Suggested Next Command

`/plan` - Create technical implementation plan
```

---

## Ralph Loop Mode (Autonomous Clarification)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous clarification:

```
/clarify --ralph                    # Until all CRITICAL/HIGH resolved
/clarify --ralph --confidence 90    # Until 90% coverage confidence
/clarify --ralph --categories "SECURITY,DATA"  # Focus on specific categories
```

### Exit Criteria

The loop exits when ANY condition is met:
- All CRITICAL and HIGH impact ambiguities resolved
- Coverage confidence reaches threshold (if `--confidence` specified)
- All ambiguities in specified categories resolved
- Hard limit of 10 questions reached

### Ralph Loop Prompt

```
/ralph-loop "Perform structured ambiguity resolution on the spec.

For each iteration:
1. Scan spec for remaining ambiguities (SEAMS taxonomy)
2. Select highest priority unresolved (Impact × Uncertainty)
3. Research best practices if HIGH/CRITICAL
4. Present ONE question with recommendation (table format)
5. Wait for user answer
6. Validate answer, integrate into spec immediately
7. Save spec atomically
8. Run post-write validation

Exit when:
- All CRITICAL/HIGH resolved, OR
- Coverage confidence >= threshold, OR
- 10 questions asked

Output: <promise>SPEC_CLARITY_ACHIEVED</promise>" --completion-promise "SPEC_CLARITY_ACHIEVED" --max-iterations 15
```

---

## Behavior Rules

1. **No spec file?** → Instruct user to add specifications to `.claude/resources/`
2. **No meaningful ambiguities?** → Report "No critical ambiguities detected" and suggest proceeding
3. **Full coverage from start?** → Output compact coverage summary (all Clear), suggest advancing
4. **User says "skip"?** → Warn that downstream rework risk increases, allow proceeding
5. **Quota reached with unresolved HIGH?** → Flag as Deferred with rationale, recommend another session

---

## Outputs

| Output | Location |
|--------|----------|
| Updated spec | Original spec file with `## Clarifications` section |
| Coverage summary | Displayed to user at session end |

---

## Handoffs

### Re-analyze
Check if clarifications resolved issues found in previous analysis.

Use: `/analyze`

### Build Plan
Create technical implementation plan from clarified spec.

Use: `/plan`