---
description: "Scan code for anti-patterns and code smells with tech-specific detection and remediation guidance"
argument-hint: "[path] [--severity=HIGH|MEDIUM|LOW] [--tech=typescript|python|rust|react|tailwind]"
---

Scan code for anti-patterns that indicate inexperience or potential bugs, providing actionable remediation guidance.

## Workflow

1. **Parse arguments** - Extract path, severity threshold, tech stack override
2. **Detect tech stack** - Auto-detect from file extensions or use override
3. **Load anti-pattern definitions** - Select relevant patterns for detected stacks
4. **Scan files** - Search for detection patterns in code
5. **Filter results** - Apply severity threshold and skip rules
6. **Generate report** - Output findings with remediation guidance

---

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `path` | `.` or `src/` | File or directory to scan |
| `--severity` | `LOW` | Minimum severity: CRITICAL, HIGH, MEDIUM, LOW |
| `--tech` | auto | Override tech stack detection |
| `--fix` | false | Show detailed remediation for each finding |
| `--summary` | false | Show only summary, no detailed findings |

## Examples

```bash
# Scan current directory for all anti-patterns
/speckit.lint

# Scan src/ for HIGH severity only
/speckit.lint src/ --severity=HIGH

# Scan specific file with remediation guidance
/speckit.lint src/api/handler.ts --fix

# Scan with specific tech stack
/speckit.lint components/ --tech=react

# Quick summary only
/speckit.lint --summary
```

---

## Tech Stack Detection

| File Pattern | Tech Stack | Patterns |
|--------------|------------|----------|
| `*.ts`, `*.tsx` | TypeScript | AP-TS-01 through AP-TS-10 |
| `*.py` | Python | AP-PY-01 through AP-PY-10 |
| `*.rs` | Rust | AP-RS-01 through AP-RS-10 |
| `*.jsx`, `app/`, `pages/` | React/Next.js | AP-RN-01 through AP-RN-10 |
| `tailwind.config.*` | Tailwind/shadcn | AP-TW-01 through AP-TW-10 |

**Note**: Multiple tech stacks can be detected for a project. Each file is scanned with relevant patterns.

---

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| CRITICAL | Security vulnerability or data loss | Block merge |
| HIGH | Significant bug risk | Require fix |
| MEDIUM | Code smell or performance | Recommend fix |
| LOW | Style or minor improvement | Suggest fix |

---

## Anti-Pattern Categories

### TypeScript (AP-TS)

| Code | Name | Severity |
|------|------|----------|
| AP-TS-01 | `any` Escape Hatch | HIGH |
| AP-TS-02 | Type Assertion Abuse | MEDIUM |
| AP-TS-03 | Stringly-Typed Code | MEDIUM |
| AP-TS-04 | Interface Duplication | LOW |
| AP-TS-05 | Type Ignorance (@ts-ignore) | HIGH |
| AP-TS-06 | Promise Chain Confusion | MEDIUM |
| AP-TS-07 | Generic Abuse | LOW |
| AP-TS-08 | Inconsistent Nullability | MEDIUM |
| AP-TS-09 | Type Safety Illusion | HIGH |
| AP-TS-10 | Inconsistent Naming | LOW |

### Python (AP-PY)

| Code | Name | Severity |
|------|------|----------|
| AP-PY-01 | Mutable Default Arguments | HIGH |
| AP-PY-02 | Bare `except` Clauses | HIGH |
| AP-PY-03 | `type()` vs `isinstance()` | MEDIUM |
| AP-PY-04 | Manual Resource Management | MEDIUM |
| AP-PY-05 | String Concatenation in Loops | MEDIUM |
| AP-PY-06 | Wildcard Imports | MEDIUM |
| AP-PY-07 | Nested Try/Except | LOW |
| AP-PY-08 | Ignoring Return Values | MEDIUM |
| AP-PY-09 | God Objects | HIGH |
| AP-PY-10 | Dynamic Code Execution | CRITICAL |

### Rust (AP-RS)

| Code | Name | Severity |
|------|------|----------|
| AP-RS-01 | `.unwrap()` in Library Code | HIGH |
| AP-RS-02 | Ignoring Clippy Lints | MEDIUM |
| AP-RS-03 | `clone()` for Borrow Checker | MEDIUM |
| AP-RS-04 | `String` vs `&str` | LOW |
| AP-RS-05 | Manual Error Types | LOW |
| AP-RS-06 | `Box<dyn Error>` Everywhere | MEDIUM |
| AP-RS-07 | Blocking in Async | HIGH |
| AP-RS-08 | Not Using `?` Operator | LOW |
| AP-RS-09 | Mutable Global State | HIGH |
| AP-RS-10 | Ignoring `#[must_use]` | HIGH |

### React/Next.js (AP-RN)

| Code | Name | Severity |
|------|------|----------|
| AP-RN-01 | useEffect for Derived State | MEDIUM |
| AP-RN-02 | Missing Dependency Array | HIGH |
| AP-RN-03 | Prop Drilling | MEDIUM |
| AP-RN-04 | Inline Function Props | LOW |
| AP-RN-05 | Direct DOM Manipulation | HIGH |
| AP-RN-06 | No Memoization | MEDIUM |
| AP-RN-07 | Index as Key | HIGH |
| AP-RN-08 | State Updates in Render | HIGH |
| AP-RN-09 | Server/Client Boundary | MEDIUM |
| AP-RN-10 | Fetch Without Cleanup | MEDIUM |

### Tailwind/shadcn (AP-TW)

| Code | Name | Severity |
|------|------|----------|
| AP-TW-01 | Inline Styles | LOW |
| AP-TW-02 | Hardcoded Colors | MEDIUM |
| AP-TW-03 | Rebuilding shadcn Components | HIGH |
| AP-TW-04 | Inconsistent Spacing | LOW |
| AP-TW-05 | !important Overuse | MEDIUM |
| AP-TW-06 | Missing Dark Mode | MEDIUM |
| AP-TW-07 | Excessive Classes | LOW |
| AP-TW-08 | Not Using CVA | LOW |
| AP-TW-09 | Missing Responsive | MEDIUM |
| AP-TW-10 | Ignoring Accessibility | HIGH |

---

## Output Format

### Summary Mode (--summary)

```markdown
## Anti-Pattern Scan Summary

**Path**: src/
**Files Scanned**: 42
**Total Findings**: 15

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 3 |
| MEDIUM | 8 |
| LOW | 4 |

**Action Required**: 3 HIGH severity findings need attention
```

### Standard Mode

```markdown
## Anti-Pattern Scan Results

**Path**: src/
**Tech Stacks**: TypeScript, React/Next.js, Tailwind
**Files Scanned**: 42
**Findings**: 15

### HIGH Severity (3)

#### AP-TS-01: `any` Escape Hatch
- `src/api/handler.ts:45` - `function processData(data: any)`
- `src/utils/parser.ts:12` - `return result as any`

#### AP-RN-02: Missing Dependency Array
- `src/components/UserProfile.tsx:23` - useEffect missing `userId`

### MEDIUM Severity (8)

#### AP-TW-02: Hardcoded Colors
- `src/components/Button.tsx:12` - `bg-[#3b82f6]`
- `src/components/Card.tsx:8` - `border-[#e5e7eb]`

[...]

### Recommendation

Fix HIGH severity findings before code review.
Run with `--fix` for detailed remediation guidance.
```

### Fix Mode (--fix)

Includes detailed remediation for each finding:

```markdown
#### AP-TS-01: `any` Escape Hatch

**src/api/handler.ts:45**
```typescript
// Current
function processData(data: any): any {
  return data.results.map(item => item.value);
}
```

**Remediation**:
```typescript
// Fixed
interface DataItem { value: string; }
interface DataResponse { results: DataItem[]; }

function processData(data: DataResponse): string[] {
  return data.results.map(item => item.value);
}
```

**Reference**: See `memory/antipatterns/typescript-antipatterns.md` §AP-TS-01
```

---

## Skip Rules

Files automatically skipped:

| Pattern | Reason |
|---------|--------|
| `*.test.*`, `*.spec.*` | Test files (unless CRITICAL) |
| `*.gen.*`, `*_generated.*` | Generated files |
| `node_modules/`, `vendor/` | Dependencies |
| `.git/`, `dist/`, `build/` | Build artifacts |

## Exception Markers

Suppress specific findings with documented reasons:

```typescript
// @antipattern-ok: AP-TS-01 - Type from untyped external library
function processExternalData(data: any) { ... }
```

```python
# @antipattern-ok: AP-PY-02 - Intentional catch-all for cleanup
try:
    risky_operation()
except:
    cleanup()
```

---

## Integration

### With /implement

Run `/speckit.lint` after completing implementation:

```bash
/implement TASK-001
/speckit.lint src/ --severity=HIGH
```

### With Code Review

Include anti-pattern scan in PR review process:

```bash
/speckit.lint --summary  # Quick overview
/speckit.lint --fix      # Detailed findings with fixes
```

### Automated Checks

Add to CI pipeline:

```yaml
- name: Anti-pattern scan
  run: claude /speckit.lint src/ --severity=HIGH
```

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/speckit.analyze` | Validate spec quality and SMART criteria |
| `/speckit.implement` | Implement tasks with quality checks |

---

## Antipattern Reference

Full anti-pattern documentation available in:
- `${CLAUDE_PLUGIN_ROOT}/skills/speckit-generator/assets/memory/antipatterns/`

Each file contains:
- Detection patterns (regex/AST)
- Severity classification
- Why the pattern is wrong
- Multiple remediation approaches
- When exceptions are acceptable
- Tool configuration (ESLint, Clippy, Ruff)
