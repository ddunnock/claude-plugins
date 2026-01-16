---
name: requirement-patterns
description: |
  This skill should be used when writing requirements, specifications, or user stories.
  Triggers on phrases like "write requirements", "create spec", "define user stories",
  "document feature", "specify behavior", "what should the system do", or when reviewing
  specification quality. Provides patterns for clear, testable, unambiguous requirements.
---

# Requirement Writing Patterns

Write requirements that are clear, testable, and unambiguous. Good requirements prevent implementation confusion and reduce clarification cycles.

## Quick Reference

### The INVEST Criteria for User Stories

| Letter | Criterion | Test |
|--------|-----------|------|
| **I** | Independent | Can be implemented without other stories |
| **N** | Negotiable | Details can be discussed, not locked |
| **V** | Valuable | Delivers user/business value |
| **E** | Estimable | Team can estimate effort |
| **S** | Small | Fits in one sprint/iteration |
| **T** | Testable | Has clear acceptance criteria |

### Requirement Levels

| Level | Format | Use When |
|-------|--------|----------|
| **Epic** | High-level capability | Planning roadmaps |
| **Feature** | User-facing functionality | Release planning |
| **User Story** | As a [role], I want [goal], so that [benefit] | Sprint planning |
| **Acceptance Criterion** | Given/When/Then | Implementation guidance |

## Writing Testable Requirements

### The "Shall" Pattern

For formal requirements, use "shall" for mandatory and "should" for recommended:

```markdown
REQ-001: The system shall authenticate users via OAuth 2.0.
REQ-002: The system shall reject requests without valid tokens with HTTP 401.
REQ-003: The system should cache tokens for up to 1 hour.
```

### The User Story Pattern

For agile contexts, use the standard format:

```markdown
As a [specific role],
I want [concrete action],
So that [measurable benefit].
```

**Good example:**
```markdown
As a registered user,
I want to reset my password via email link,
So that I can regain access within 5 minutes without contacting support.
```

**Bad example:**
```markdown
As a user,
I want better security,
So that things work properly.
```

### Acceptance Criteria (Given/When/Then)

Every requirement needs testable acceptance criteria:

```markdown
**Given** a registered user with a valid email
**When** they request a password reset
**Then** they receive an email within 30 seconds
**And** the link expires after 24 hours
**And** clicking the link allows setting a new password
```

## Ambiguity Markers to Avoid

These words indicate vague requirements that need refinement:

| Marker | Problem | Fix |
|--------|---------|-----|
| "properly" | Undefined correctness | Specify exact behavior |
| "quickly" | No metric | Add time constraint (e.g., "<200ms") |
| "user-friendly" | Subjective | Define specific UX criteria |
| "secure" | Vague | List specific security controls |
| "etc." | Incomplete list | Enumerate all items or state "including but not limited to" |
| "appropriate" | Undefined standard | Specify the standard |
| "as needed" | Undefined trigger | Define when/what triggers |
| "may/might" | Uncertain scope | Decide: is it in scope or not? |

## Requirement Identifiers

Use consistent ID schemes for traceability:

```markdown
REQ-001      # Simple sequential
FR-001       # Functional requirement
NFR-001      # Non-functional requirement
SEC-001      # Security requirement
PERF-001     # Performance requirement
```

## Constraints vs Requirements

**Requirements** = What the system must DO
**Constraints** = Limits on HOW it's built

```markdown
## Requirements
- REQ-001: System shall support 1000 concurrent users

## Constraints
- CON-001: Must use PostgreSQL 14+
- CON-002: Must deploy to AWS
- CON-003: Budget limit $500/month infrastructure
```

## Common Anti-Patterns

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| **Solution masquerading as requirement** | "Use Redis for caching" | "Response time < 100ms for cached data" |
| **Compound requirement** | "System shall authenticate and authorize" | Split into REQ-001 (auth) and REQ-002 (authz) |
| **Unmeasurable quality** | "System shall be fast" | "95th percentile latency < 200ms" |
| **Missing actor** | "Data shall be validated" | "System shall validate user input before storage" |
| **Assumed knowledge** | "Standard security practices" | List specific practices or reference standard |

## Integration with SpecKit

When writing specs for `/speckit.plan`:

1. **Use REQ-XXX identifiers** - Enables traceability to tasks
2. **Include acceptance criteria** - Becomes task verification
3. **Mark unknowns as [TBD]** - `/speckit.clarify` will find them
4. **Group by domain** - Enables domain-specific plans

## Additional Resources

For detailed patterns and examples, see:

- **`references/anti-patterns.md`** - Common mistakes with fixes
- **`references/examples.md`** - Complete requirement examples by domain

## Verification Checklist

Before finalizing requirements:

- [ ] Every requirement has a unique identifier
- [ ] No vague adjectives (properly, quickly, appropriately)
- [ ] Each requirement is testable with clear criteria
- [ ] Requirements are independent (no hidden dependencies)
- [ ] Constraints are separated from requirements
- [ ] Unknowns are marked [TBD] for clarification
