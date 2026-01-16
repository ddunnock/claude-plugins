---
description: "Deterministic read-only audit of project artifacts for consistency"
handoffs:
  - label: Clarify Issues
    agent: clarify
    prompt: Resolve ambiguities found in analysis
  - label: Update Plan
    agent: plan
    prompt: Revise plan to address gaps
---

# Analyze

Deterministic, read-only audit of project artifacts for consistency and completeness.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Usage

```
/analyze                    # Full analysis
/analyze --verbose          # Detailed output
/analyze --category gaps    # Filter by category
```

---

## Characteristics

- **Read-only**: Never modifies files
- **Deterministic**: Same inputs = same outputs
- **Stable IDs**: Finding IDs remain stable across runs
- **Quantified**: Metrics for coverage, completeness

## Analysis Categories

| Category | Description |
|----------|-------------|
| GAPS | Missing required elements |
| INCONSISTENCIES | Contradictions between artifacts |
| AMBIGUITIES | Unclear or undefined items |
| ORPHANS | Unreferenced elements |
| ASSUMPTIONS | Untracked/unvalidated assumptions |

## Severity Levels

| Level | Meaning |
|-------|---------|
| CRITICAL | Blocks progress, must fix |
| HIGH | Significant risk, should fix |
| MEDIUM | Notable issue, plan to fix |
| LOW | Minor concern |

## Output Format

```markdown
# Analysis Report

Generated: [timestamp]
Artifacts analyzed: [count]

## Summary
| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| GAPS     | 2        | 3    | 5      | 1   |
| ...      |          |      |        |     |

## Findings

### GAP-001 [CRITICAL]
**Location**: spec.md:45
**Description**: Missing error handling specification
**Recommendation**: Define error states for API failures
```

## Idempotency
- Read-only, always safe
- Stable finding IDs across runs

---

## Outputs

| Output | Location |
|--------|----------|
| Analysis report | `.claude/resources/analysis-report.md` |
| Findings summary | Displayed to user |

---

## GATE: Present Findings

After analysis, present findings organized by severity and recommend next steps.

### Gate Response Template

```markdown
## Analysis Complete

Analyzed [N] artifacts:
- Specs: [count]
- Plans: [count]
- Tasks: [count]

### Summary
| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| GAPS     | [n]      | [n]  | [n]    | [n] |
| INCONSISTENCIES | [n] | [n] | [n]   | [n] |
| AMBIGUITIES | [n]  | [n]  | [n]    | [n] |

### Critical Findings
[List any CRITICAL findings that block progress]

### Recommended Actions
1. [Based on findings]
2. [Specific commands to run]
```

---

## Handoffs

### Clarify Issues
Resolve ambiguities and unclear items found in analysis.

Use: `/clarify`

### Update Plan
Revise the plan to address gaps or inconsistencies.

Use: `/plan`
