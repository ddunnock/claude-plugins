Structured ambiguity resolution with immediate spec updates.

## Usage
- `/speckit.clarify` - Start clarification session
- `/speckit.clarify spec.md` - Clarify specific spec

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
