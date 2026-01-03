# Clarify Workflow Reference

Detailed workflow for the `/speckit.clarify` command.

## Purpose

Structured ambiguity resolution through targeted Q&A with immediate specification updates. Reduces uncertainty systematically.

## Key Characteristics

- **One question at a time**: Focused, not overwhelming
- **Multiple choice or short phrase**: Quick to answer
- **5-question maximum per session**: Prevents fatigue
- **Immediate updates**: Specs updated after each answer
- **9-category taxonomy**: Structured classification
- **Session logging**: Full traceability

---

## Workflow Steps

### Step 1: Scan for Ambiguities

Detect ambiguity patterns:

| Pattern | Category | Priority |
|---------|----------|----------|
| `[TBD]` marker | Any | HIGH |
| `[TODO]` marker | Any | HIGH |
| `[NEEDS CLARIFICATION]` | Any | HIGH |
| "should" (without "must") | BEHAVIOR | MEDIUM |
| "might", "probably", "possibly" | BEHAVIOR | MEDIUM |
| "etc.", "and so on" | SCOPE | MEDIUM |
| Missing error handling | ERROR | HIGH |
| Undefined limits | CONSTRAINT | MEDIUM |
| Vague time references | TEMPORAL | MEDIUM |

```
Ambiguities found: 15

By category:
- SCOPE: 3
- BEHAVIOR: 5
- ERROR: 4
- CONSTRAINT: 2
- SEQUENCE: 1

By priority:
- HIGH: 8
- MEDIUM: 7
```

### Step 2: Prioritize Questions

Rank by impact on implementation:

1. **Blocking implementation**: Must know to proceed
2. **Affects architecture**: Changes design decisions
3. **Affects multiple tasks**: Wide impact
4. **Affects single task**: Narrow impact
5. **Nice to know**: Low urgency

### Step 3: Present Questions (One at a Time)

Format each question:

```
CLARIFY-001 [BEHAVIOR]

Location: spec.md:45

The specification states "users can authenticate" but doesn't specify
the authentication method.

**Context**: This affects the authentication architecture (AD-001) and
multiple tasks in Phase 1.

Which authentication method should be used?

1. OAuth 2.0 with Google/GitHub (Recommended)
   - Pros: Secure, no password management
   - Cons: Requires OAuth setup

2. Email/password with JWT
   - Pros: Full control, simpler setup
   - Cons: Password security responsibility

3. Magic link (passwordless)
   - Pros: Very secure, good UX
   - Cons: Email dependency

4. Other (please specify)

Your choice:
```

### Step 4: Process Answer

Based on answer:

1. **Update specification immediately**
2. **Log the Q&A**
3. **Update related documents if needed**

```markdown
# In spec.md, replace:
"users can authenticate"

# With:
"users authenticate via OAuth 2.0 with Google and GitHub providers
(decided in clarify session 2024-01-15, CLARIFY-001)"
```

### Step 5: Continue or Complete

After each question:

```
Question 1 of 5 answered.
Spec updated: spec.md:45

Remaining ambiguities by priority:
- HIGH: 7
- MEDIUM: 7

Options:
1. Continue to next question
2. End session (progress saved)
3. Skip to specific category
```

### Step 6: Session Summary

After 5 questions or user ends:

```
Clarify Session Complete

Questions answered: 5
Specs updated: 3 files

Updates made:
1. spec.md:45 - Authentication method defined
2. spec.md:78 - Error handling specified
3. plan.md:AD-001 - Updated with auth decision

Remaining ambiguities: 10
- HIGH: 3
- MEDIUM: 7

Session logged: .claude/resources/clarify-sessions/2024-01-15-session-1.md

Run /speckit.clarify again to continue resolving ambiguities.
```

---

## 9-Category Taxonomy

### SCOPE
**What it covers**: Boundaries of functionality

**Example questions**:
- "Should the search feature include fuzzy matching?"
- "Does 'user management' include role assignment?"
- "Are guest users in scope?"

**Update format**:
```markdown
**Scope clarification**: Search includes fuzzy matching with configurable
threshold (decided: CLARIFY-XXX)
```

### BEHAVIOR
**What it covers**: How things work

**Example questions**:
- "What happens when a user submits an invalid form?"
- "Should changes auto-save or require explicit save?"
- "How does the system handle concurrent edits?"

**Update format**:
```markdown
**Behavior**: Invalid form submissions display inline errors without
page reload. Form state is preserved. (decided: CLARIFY-XXX)
```

### DATA
**What it covers**: Data formats, storage, structure

**Example questions**:
- "What date format should be used for display?"
- "How long should session data be retained?"
- "What's the maximum file upload size?"

**Update format**:
```markdown
**Data format**: Dates displayed as "MMM DD, YYYY" (e.g., "Jan 15, 2024")
internally stored as ISO 8601. (decided: CLARIFY-XXX)
```

### ERROR
**What it covers**: Error handling and recovery

**Example questions**:
- "How should network errors be displayed to users?"
- "Should failed operations retry automatically?"
- "What's the fallback if the external API is unavailable?"

**Update format**:
```markdown
**Error handling**: Network errors show toast notification with retry
button. Auto-retry after 5 seconds, max 3 attempts. (decided: CLARIFY-XXX)
```

### SEQUENCE
**What it covers**: Order of operations

**Example questions**:
- "Does email verification happen before or after profile creation?"
- "Should validation run on blur or on submit?"
- "What's the order of middleware execution?"

**Update format**:
```markdown
**Sequence**: Email verification required before profile creation.
User cannot access dashboard until verified. (decided: CLARIFY-XXX)
```

### CONSTRAINT
**What it covers**: Limits and boundaries

**Example questions**:
- "What's the maximum number of items in a list?"
- "What are the password complexity requirements?"
- "How many concurrent sessions are allowed?"

**Update format**:
```markdown
**Constraint**: Maximum 1000 items per list. Pagination required beyond
100 items. (decided: CLARIFY-XXX)
```

### INTERFACE
**What it covers**: Integration and API contracts

**Example questions**:
- "What authentication does the external API require?"
- "What format should webhook payloads use?"
- "How do components communicate state changes?"

**Update format**:
```markdown
**Interface**: External API uses Bearer token auth. Tokens refreshed
via OAuth 2.0 refresh flow. (decided: CLARIFY-XXX)
```

### AUTHORITY
**What it covers**: Permissions and approval

**Example questions**:
- "Who can approve budget changes?"
- "What role is required to delete users?"
- "Who owns the data migration decision?"

**Update format**:
```markdown
**Authority**: Only Admin role can delete users. Deletion requires
confirmation with reason. (decided: CLARIFY-XXX)
```

### TEMPORAL
**What it covers**: Time-related aspects

**Example questions**:
- "How long should the password reset link be valid?"
- "What's the session timeout duration?"
- "How often should data be synced?"

**Update format**:
```markdown
**Temporal**: Password reset links valid for 24 hours. One-time use.
New link invalidates previous. (decided: CLARIFY-XXX)
```

---

## Session Logging

Each session creates a log file:

```markdown
# Clarify Session Log

Session: 2024-01-15-session-1
Started: 2024-01-15T10:30:00Z
Completed: 2024-01-15T10:45:00Z
Questions: 5

## Questions & Answers

### CLARIFY-001 [BEHAVIOR]
**Location**: spec.md:45
**Question**: Which authentication method should be used?
**Answer**: Option 1 - OAuth 2.0 with Google/GitHub
**Updated**: spec.md:45
**Timestamp**: 2024-01-15T10:32:00Z

### CLARIFY-002 [ERROR]
...

## Files Updated
- spec.md (3 changes)
- plan.md (1 change)

## Remaining Ambiguities
[List of unresolved items]
```

---

## Idempotency

- **Skip answered**: Questions with existing answers skipped
- **Track by location**: Same location = same question
- **Session continuity**: Can resume previous sessions
- **No duplicate updates**: Already-clarified items not re-asked

---

## Integration Points

### From /speckit.analyze

Ambiguity findings trigger clarify:
```
analyze found 15 ambiguities.
Run /speckit.clarify to resolve?
```

### To Specification Updates

Direct spec modifications with traceability:
```markdown
Feature supports fuzzy search (decided: CLARIFY-001)
```

### To Plan Updates

May require plan revision:
```
Answer affects architecture decision AD-001.
Update plan.md?
```
