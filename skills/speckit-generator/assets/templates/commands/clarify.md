---
description: "Structured ambiguity resolution with immediate spec updates"
handoffs:
  - label: Re-analyze
    agent: analyze
    prompt: Check if clarifications resolved issues
  - label: Continue Planning
    agent: plan
    prompt: Update plan with clarified requirements
---

# Clarify

Structured ambiguity resolution with immediate spec updates.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Usage

```
/clarify                # Start clarification session
/clarify spec.md        # Clarify specific spec
```

---

## Characteristics

- **One question at a time**: Focused, manageable
- **Multiple choice or short phrase**: Quick answers
- **5-question maximum per session**: Avoid fatigue
- **Immediate updates**: Specs updated after each answer
- **9-category taxonomy**: Structured classification

## Ambiguity Categories

| Category | Example Question |
|----------|-----------------|
| SCOPE | "Should X include Y functionality?" |
| BEHAVIOR | "What happens when user does X?" |
| DATA | "What format should X be stored in?" |
| ERROR | "How should X error be handled?" |
| SEQUENCE | "Does X happen before or after Y?" |
| CONSTRAINT | "What are the limits for X?" |
| INTERFACE | "How does X communicate with Y?" |
| AUTHORITY | "Who approves X?" |
| TEMPORAL | "How long should X take?" |

## Workflow

1. **Scan for ambiguity** - Find [TBD], [NEEDS CLARIFICATION], vague language
2. **Prioritize** - Rank by impact on implementation
3. **Present question** - One at a time with options
4. **Update spec** - Apply answer immediately
5. **Log session** - Record Q&A for traceability

## Question Format

```
CLARIFY-001 [BEHAVIOR]

The spec mentions "user authentication" but doesn't specify the method.

Which authentication method should be used?
1. OAuth 2.0 with Google/GitHub (Recommended)
2. Email/password with JWT
3. Magic link (passwordless)
4. Other (please specify)

Your choice:
```

## Idempotency
- Tracks answered questions
- Skips already-clarified items
- Session history preserved

---

## Outputs

| Output | Location |
|--------|----------|
| Updated specs | `.claude/resources/*.md` |
| Session log | `.claude/resources/clarify-session-[date].md` |

---

## GATE: After Session Complete

After completing clarification session, summarize what was resolved.

### Gate Response Template

```markdown
## Clarification Session Complete

Resolved [N] ambiguities:

| ID | Category | Question | Answer |
|----|----------|----------|--------|
| CLARIFY-001 | BEHAVIOR | Auth method? | OAuth 2.0 |
| CLARIFY-002 | DATA | Storage format? | JSON |
| [etc.] |

### Specs Updated
- spec.md: [N] clarifications applied
- [other specs if applicable]

### Remaining Ambiguities
- [Any [TBD] items still unresolved]

### Recommended Next Steps
1. Run `/analyze` to verify clarifications resolved issues
2. Run `/plan` to update plan with clarified requirements
```

---

## Handoffs

### Re-analyze
Check if clarifications resolved the issues found in previous analysis.

Use: `/analyze`

### Continue Planning
Update the plan with newly clarified requirements.

Use: `/plan`
