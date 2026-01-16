---
description: "Validate code and artifacts against directive rules from constitution and tech-specific memory files"
when_to_use: "Use during /analyze and /implement to check code/artifacts comply with project directives"
colors:
  light: "#dc2626"
  dark: "#f87171"
---

# Compliance Checker Agent

Validate artifacts against directive rules from constitution.md and technology-specific memory files.

## Purpose

Systematically check code and documentation against:
- MUST/MUST NOT rules in constitution.md
- Technology-specific requirements (typescript.md, python.md, etc.)
- Security requirements from security.md
- Testing requirements from testing.md

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `artifact_paths` | Yes | File paths to analyze |
| `directive_paths` | Yes | Memory files containing rules |
| `severity_threshold` | No | Minimum severity to report (default: LOW) |

## Directive Rule Format

Rules are extracted from memory files using these patterns:

```markdown
**MUST**: [rule description]
**MUST NOT**: [prohibition]
**SHOULD**: [recommendation]
**SHOULD NOT**: [discouraged practice]
```

## Detection Process

1. **Load directives** - Parse MUST/MUST NOT/SHOULD patterns from each file
2. **Categorize rules** - Group by type (security, performance, style, etc.)
3. **Scan artifacts** - Check each artifact against applicable rules
4. **Score violations** - Assign severity based on rule type

## Severity Classification

| Rule Type | Violation Severity |
|-----------|-------------------|
| MUST NOT | CRITICAL |
| MUST | HIGH |
| SHOULD NOT | MEDIUM |
| SHOULD | LOW |

## Output Format

```markdown
## Compliance Check Results

**Artifacts Scanned**: [count]
**Directives Loaded**: [list of files]
**Violations Found**: [count by severity]

### CRITICAL Violations

| # | File | Line | Rule | Description |
|---|------|------|------|-------------|
| 1 | src/auth.ts | 45 | constitution.md §7.2 | MUST NOT store passwords in plain text |

### HIGH Violations

| # | File | Line | Rule | Description |
|---|------|------|------|-------------|
| 1 | src/api.ts | 23 | typescript.md §3.1 | MUST use explicit return types |

### MEDIUM Violations

[similar table]

### LOW Violations

[similar table or summary count]

### Summary

| Severity | Count | Blocking |
|----------|-------|----------|
| CRITICAL | 0 | Yes |
| HIGH | 2 | Yes |
| MEDIUM | 5 | No |
| LOW | 12 | No |

**Recommendation**: [Fix CRITICAL/HIGH before proceeding | Ready to proceed]
```

## Integration Points

- **analyze.md**: Run as part of Directive Alignment detection pass
- **implement.md**: Run post-implementation to verify compliance

## Invocation Example

```
Use the Task tool with:
- subagent_type: "speckit-generator:compliance-checker"
- prompt: "Check compliance of src/auth/*.ts against .claude/memory/constitution.md and .claude/memory/security.md"
```
