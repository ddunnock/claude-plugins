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

<!--
================================================================================
INIT AGENT INSTRUCTIONS
================================================================================
When copying this template to the user's project, you MUST customize:

1. MEMORY DIRECTIVES SECTION
   - Replace placeholder with actual directive files for detected tech stack
   - Example for TypeScript + React:
     ```markdown
     **Project-specific (detected: TypeScript, React, Next.js):**
     - `typescript.md` - TypeScript standards
     - `react-nextjs.md` - React/Next.js patterns
     ```

2. SEAMS LENSES SECTION
   - Enable lenses relevant to the project type
   - Web apps: Enable Security, Stakeholder (end-user UX)
   - APIs: Enable Interface, Error/Recovery heavily
   - Data pipelines: Enable Data, Traceability heavily

3. RALPH LOOP MODE SECTION
   - Check if ralph-loop plugin is installed
   - If installed: Include full autonomous mode instructions
   - If not installed: Include disabled notice with installation instructions

REMOVE all INIT comments from the final output.
================================================================================
-->

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
/clarify --ralph              # Autonomous mode (if ralph-loop installed)
```

---

## Session Constraints

- **Maximum 5 questions asked** per interactive session
- **Maximum 10 questions total** across all sessions for a spec
- **Never reveal queued questions** in advance
- **Atomic save after each answer** to prevent context loss

---

## Memory Directives

<!-- INIT: Replace this section with the actual directive files for this project -->

Load these directive files for context-aware recommendations:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific:**
<!-- INIT: List only the tech-specific files detected for this project -->
- `[DETECTED_TECH_FILE].md` - [Description]

<!-- INIT: Remove all HTML comments from final output -->

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

<!-- INIT: Enable relevant lenses based on project type -->

**Active lenses for this project:**
- [ ] **Structure**: Boundary clarity, cohesion analysis
- [ ] **Execution**: Happy paths, edge cases, failure modes
- [ ] **Assumptions**: Implicit technical/organizational assumptions
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

The agent runs detection across all 13 SEAMS categories and returns:
- Prioritized findings ranked by score
- Recommended questions for top findings
- Coverage summary by category

Use the agent's output to populate the internal coverage map:

```
Coverage Map (internal - do not output unless no questions):

| Category | Status | Candidate Questions |
|----------|--------|---------------------|
| SCOPE | Partial | 2 |
| BEHAVIOR | Missing | 3 |
| DATA | Clear | 0 |
| ERROR | Missing | 2 |
| ASSUMPTION | Partial | 1 |
| [etc.] |
```

**Status definitions:**
- **Clear**: Sufficient detail, no ambiguity
- **Partial**: Some detail but gaps remain
- **Missing**: No specification, critical gap

### Step 3: Generate Prioritized Queue

Build internal queue of candidate questions (max 5 to ask). Apply these rules:

**Prioritization formula:**
```
Priority Score = Impact × Uncertainty
```

Where:
- **Impact** (1-5): How much does this affect architecture, tasks, tests, UX, ops, compliance?
- **Uncertainty** (1-5): How unclear is this currently?

**Selection rules:**
- Only include questions whose answers **materially impact** implementation
- Favor HIGH impact categories over multiple LOW impact questions
- Ensure category coverage balance (don't ask 3 questions from same category)
- Exclude questions already answered in previous sessions
- Exclude plan-level execution details unless blocking correctness

**Do NOT reveal the queue to the user.**

### Step 4: Sequential Questioning Loop

Present **EXACTLY ONE** question at a time. Never reveal future questions.

#### For Multiple-Choice Questions (2-5 options):

1. **Analyze all options** and determine the most suitable based on:
   - Best practices for the project type
   - Risk reduction (security, performance, maintainability)
   - Alignment with project goals visible in spec

2. **Present recommendation prominently:**

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

#### For Short-Answer Questions (no meaningful discrete options):

```
CLARIFY-002 [CONSTRAINT]
Impact: MEDIUM | Affects: File upload feature

The spec mentions file uploads but doesn't specify size limits.

What is the maximum file upload size?

**Suggested:** 10 MB
Reasoning: Balances usability with server resource constraints.
Common default for web applications.

Format: Short answer (≤5 words).
Reply "yes" or "suggested" to accept, or provide your own answer.
```

### Step 5: Process Answer

After user responds:

1. **Parse response:**
   - If "yes", "recommended", or "suggested" → use your stated recommendation
   - If option letter (A, B, C...) → map to that option
   - If short text → validate ≤5 words, use as answer
   - If ambiguous → ask for quick clarification (same question, doesn't count as new)

2. **Record in working memory** (do not advance until valid answer)

3. **Immediately integrate into spec** (see Step 6)

4. **Move to next queued question** or complete if:
   - All critical ambiguities resolved early
   - User signals "done", "stop", "proceed", "no more"
   - Reached 5 questions asked

### Step 6: Incremental Spec Integration (After EACH Answer)

**Immediately after each accepted answer:**

1. **Ensure Clarifications section exists** in spec:
   ```markdown
   ## Clarifications

   ### Session YYYY-MM-DD
   - Q: [question summary] → A: [final answer]
   ```

2. **Append Q&A bullet** under today's session heading

3. **Apply clarification to appropriate section:**

   | Answer Type | Target Section | Action |
   |-------------|----------------|--------|
   | Functional behavior | Functional Requirements | Add/update bullet |
   | User interaction | User Stories or Actors | Clarify role/scenario |
   | Data shape/entity | Data Model | Add fields, types, relationships |
   | Non-functional | Quality Attributes | Convert vague adjective to metric |
   | Edge case/negative | Edge Cases / Error Handling | Add new bullet |
   | Terminology | Throughout | Normalize term, note "(formerly X)" once |

4. **Remove contradictions:** If clarification invalidates earlier text, replace it

5. **Save spec immediately** (atomic write after each integration)

### Step 7: Post-Write Validation

**After EACH write**, verify:

- [ ] Clarifications section contains exactly one bullet per accepted answer
- [ ] No duplicate question IDs
- [ ] Updated sections contain no lingering placeholders the answer resolved
- [ ] No contradictory earlier statements remain
- [ ] Markdown structure valid (only allowed new headings: `## Clarifications`, `### Session YYYY-MM-DD`)
- [ ] Terminology consistent across all updated sections

### Step 8: Loop Termination

Stop asking questions when ANY of these occur:

1. All critical ambiguities resolved (remaining queued items unnecessary)
2. User signals completion ("done", "good", "no more", "proceed")
3. Reached 5 asked questions for this session
4. No valid questions exist (full coverage)

---

## Coverage Summary (End of Session)

Report completion with four-status taxonomy:

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
| BEHAVIOR | ✓ Resolved | Was Missing, addressed in CLARIFY-002, CLARIFY-003 |
| DATA | ○ Clear | Already sufficient |
| ERROR | ◐ Deferred | Exceeds quota, better suited for planning phase |
| ASSUMPTION | ◐ Deferred | Low impact, can address post-plan |
| STAKEHOLDER | ○ Clear | Already sufficient |
| RECOVERY | ⚠ Outstanding | Still Partial, HIGH impact - recommend another session |
| [etc.] |

**Legend:**
- ✓ Resolved: Was Partial/Missing, now addressed
- ○ Clear: Already sufficient (no question needed)
- ◐ Deferred: Exceeds question quota or better for planning phase
- ⚠ Outstanding: Still Partial/Missing, remains unresolved

### Recommendation

[If Outstanding or Deferred remain with HIGH impact:]
Consider running `/clarify` again to address RECOVERY category before `/plan`.

[If all critical resolved:]
Proceed to `/plan` to create implementation plan.

### Suggested Next Command

`/plan` - Create technical implementation plan
```

---

## Question Format Reference

### Multiple-Choice Template

```
CLARIFY-[NNN] [CATEGORY]
Impact: [CRITICAL/HIGH/MEDIUM/LOW] | Affects: [components/tasks]

[Context: What the spec says and why it's ambiguous]

[Question - clear, specific, answerable]

**Recommended:** Option [X] - [brief label]
Reasoning: [1-2 sentences explaining why this is best choice]

| Option | Description |
|--------|-------------|
| A | [Option A description] |
| B | [Option B description] |
| C | [Option C description] |
| Short | Provide a different short answer (≤5 words) |

Reply with option letter, "yes"/"recommended" to accept, or short answer.
```

### Short-Answer Template

```
CLARIFY-[NNN] [CATEGORY]
Impact: [CRITICAL/HIGH/MEDIUM/LOW] | Affects: [components/tasks]

[Context: What the spec says and why it's ambiguous]

[Question - clear, specific]

**Suggested:** [your proposed answer]
Reasoning: [brief justification]

Format: Short answer (≤5 words).
Reply "yes"/"suggested" to accept, or provide your own answer.
```

---

## Pre-Question Research (High-Impact Only)

For CRITICAL/HIGH impact questions, gather context before generating recommendations:

**When to research:**
- Security decisions (authentication, authorization, encryption)
- Performance constraints (caching, scaling)
- Architecture choices (state management, API patterns)
- Integration patterns (third-party services)

**Research approach:**
1. Identify tech stack from loaded directives
2. Search: `[topic] best practices [tech stack] 2024`
3. Look for common patterns, known pitfalls
4. Note security advisories or deprecations

**Include in recommendation reasoning:**
- Current industry standard
- Known pitfalls to avoid
- Source references if available

---

## Spec Update Format

### Clarifications Section Structure

```markdown
## Clarifications

### Session 2024-01-15
- Q: Authentication method? → A: OAuth 2.0 with Google/GitHub
- Q: File upload size limit? → A: 10 MB maximum
- Q: Session timeout duration? → A: 24 hours with sliding expiry

### Session 2024-01-14
- Q: User roles scope? → A: Full RBAC with custom roles
```

### Inline Clarification Markers

When updating spec sections, add traceability:

```markdown
## Authentication

Users authenticate via OAuth 2.0 with Google and GitHub providers.
New users are created on first successful OAuth login. Sessions use
HTTP-only secure cookies with 24-hour sliding expiry.
*(Clarified: CLARIFY-001, CLARIFY-003)*
```

---

## Ralph Loop Mode (Autonomous Clarification)

<!-- INIT: Customize this section based on ralph-loop plugin detection -->

<!-- INIT: IF ralph-loop IS detected, use this content: -->
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

<!-- INIT: IF ralph-loop is NOT detected, use this content instead:
**Status**: ✗ Disabled (ralph-loop plugin not installed)

To enable autonomous clarification mode, install the ralph-loop plugin:
```
/install-plugin ralph-loop
```

Then re-run `/speckit.init` to update this command.
-->

<!-- INIT: Remove all HTML comments from final output -->

---

## Behavior Rules

1. **No spec file?** → Instruct user to run `/specify` first
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
