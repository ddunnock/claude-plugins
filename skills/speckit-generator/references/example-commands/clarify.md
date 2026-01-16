SEAMS-enhanced ambiguity resolution with sequential questioning, recommendations, and atomic spec updates.

## Usage
- `/speckit.clarify` - Start clarification session
- `/speckit.clarify spec.md` - Clarify specific spec
- `/speckit.clarify --category SECURITY` - Focus on specific category
- `/speckit.clarify --ralph` - Autonomous clarification mode (if ralph-loop installed)
- `/speckit.clarify --status` - Show coverage without asking questions

## Session Constraints

- **5 questions max** per interactive session
- **10 questions max** total across all sessions for a spec
- **Never reveal queued questions** in advance
- **Atomic save after each answer** to prevent context loss
- **Answer format**: Option letter OR ≤5 words

## Sequential Questioning Loop

Present **ONE question at a time**. Never reveal future questions.

### Question Format (Table-Based)

```
CLARIFY-001 [BEHAVIOR]
Impact: HIGH | Affects: Authentication, 5 tasks

The spec says "users can authenticate" but doesn't specify the method.

Which authentication method should be used?

**Recommended:** Option A - OAuth 2.0 with Google/GitHub
Reasoning: Industry standard, eliminates password management.

| Option | Description |
|--------|-------------|
| A | OAuth 2.0 with Google/GitHub providers |
| B | Email/password with JWT tokens |
| C | Magic link (passwordless) |
| Short | Provide a different answer (≤5 words) |

Reply with option letter, "yes"/"recommended" to accept, or short answer.
```

### User Response Handling

| User Says | Action |
|-----------|--------|
| "yes", "recommended", "suggested" | Accept your recommendation |
| "A", "B", "C" | Use that option |
| Short text (≤5 words) | Use as custom answer |
| "done", "stop", "proceed" | End session |
| Ambiguous | Ask for clarification (same question) |

## SEAMS-Enhanced Taxonomy (13 Categories)

| Category | Group | Focus |
|----------|-------|-------|
| SCOPE | Functional | Feature boundaries, in/out scope |
| BEHAVIOR | Functional | User actions, state transitions |
| SEQUENCE | Functional | Order of operations |
| AUTHORITY | Functional | Decision makers, permissions |
| DATA | Data/Integration | Entities, formats, validation |
| INTERFACE | Data/Integration | API contracts, protocols |
| CONSTRAINT | Data/Integration | Limits, bounds |
| TEMPORAL | Data/Integration | Timing, duration |
| ERROR | Quality/Ops | Error handling, failure modes |
| RECOVERY | Quality/Ops | Degradation, retry, fallback |
| ASSUMPTION | Quality/Ops | Implicit beliefs |
| STAKEHOLDER | Quality/Ops | Operator, security, user views |
| TRACEABILITY | Quality/Ops | Req ↔ design coverage |

## Prioritization Formula

```
Priority Score = Impact × Uncertainty
```
- **Impact** (1-5): Effect on architecture, tasks, tests, UX, ops
- **Uncertainty** (1-5): Current ambiguity level

## Spec Update Format

### Clarifications Section (in spec file)

```markdown
## Clarifications

### Session 2024-01-15
- Q: Authentication method? → A: OAuth 2.0 with Google/GitHub
- Q: File upload size limit? → A: 10 MB maximum
```

### Inline Traceability

```markdown
Users authenticate via OAuth 2.0 with Google and GitHub providers.
*(Clarified: CLARIFY-001)*
```

## Coverage Summary (Four-Status)

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✓ | Resolved | Was Partial/Missing, now addressed |
| ○ | Clear | Already sufficient |
| ◐ | Deferred | Exceeds quota, better for planning |
| ⚠ | Outstanding | Still unresolved, HIGH impact |

## Workflow

1. **Load context** - Spec + directives + previous sessions
2. **SEAMS coverage scan** - Status: Clear/Partial/Missing for each category
3. **Build priority queue** - Impact × Uncertainty, max 5 questions
4. **Sequential loop** - One question → answer → validate → save → next
5. **Post-write validation** - 6-point checklist after each save
6. **Coverage summary** - Report with four-status taxonomy

## Idempotency

- Tracks answered questions by content hash
- Skips already-clarified items
- Session history in `## Clarifications` section
- Use `--force` to re-ask previous questions
