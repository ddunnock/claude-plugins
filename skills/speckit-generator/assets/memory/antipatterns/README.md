# Anti-Patterns Reference Directory

> **Purpose**: Comprehensive anti-pattern detection and remediation guides
> **Usage**: Referenced by antipattern-detector agent and /lint command

---

## Available Anti-Pattern Files

| File | Tech Stack | Patterns | Parent |
|------|------------|----------|--------|
| `typescript-antipatterns.md` | TypeScript | 10 | typescript.md §10 |
| `python-antipatterns.md` | Python | 10 | python.md §13 |
| `rust-antipatterns.md` | Rust | 10 | rust.md §9 |
| `react-nextjs-antipatterns.md` | React/Next.js | 10 | react-nextjs.md §11 |
| `tailwind-shadcn-antipatterns.md` | Tailwind/shadcn | 10 | tailwind-shadcn.md §14 |

---

## Pattern Code System

Each anti-pattern has a unique code for tracking and reference:

- **AP-TS-XX**: TypeScript patterns
- **AP-PY-XX**: Python patterns
- **AP-RS-XX**: Rust patterns
- **AP-RN-XX**: React/Next.js patterns
- **AP-TW-XX**: Tailwind/shadcn patterns

---

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| CRITICAL | Security vulnerability or data loss risk | Block merge |
| HIGH | Significant bug risk or maintainability issue | Require fix |
| MEDIUM | Code smell or performance concern | Recommend fix |
| LOW | Style issue or minor improvement | Suggest fix |

---

## Usage

### In Code Review

1. Identify tech stack from file extensions
2. Load relevant anti-pattern file(s)
3. Scan for detection patterns
4. Report findings with severity and remediation

### In /lint Command

```markdown
## Anti-Pattern Report

### HIGH Severity
- AP-TS-01: Found 3 uses of `any` type
  - src/api/handler.ts:45
  - src/utils/parser.ts:12
  - src/models/user.ts:78

### MEDIUM Severity
- AP-RN-02: Missing dependency in useEffect
  - src/components/UserProfile.tsx:23

### Remediation
[Link to specific pattern remediation guidance]
```

---

## Integration with Memory Files

Each anti-pattern file corresponds to a compact section in its parent memory file:

- **Memory file**: Quick reference during development (~10-15 lines per pattern)
- **Anti-pattern file**: Deep dive for review and education (~50+ lines per pattern)

The memory file section provides:
- Pattern code and name
- ❌ Bad / ✅ Good examples
- MUST/MUST NOT directives

The anti-pattern file provides:
- Detection regex patterns
- Severity classification
- Detailed "why it's wrong" explanation
- Multiple remediation approaches
- When exceptions are acceptable
- Tool configuration (ESLint, Clippy, etc.)
