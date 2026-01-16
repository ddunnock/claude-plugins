---
description: "Detect specification ambiguities using SEAMS taxonomy across 13 categories"
when_to_use: "Use during /clarify to identify and prioritize ambiguities in specifications"
colors:
  light: "#7c3aed"
  dark: "#a78bfa"
---

# Ambiguity Scanner Agent

Scan specifications for ambiguities using the SEAMS-enhanced taxonomy.

## Purpose

Systematically detect underspecified, vague, or conflicting elements in specifications by scanning across 13 categories and prioritizing by impact.

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `spec_path` | Yes | Path to specification file |
| `focus_categories` | No | Specific categories to scan (default: all) |
| `max_findings` | No | Maximum findings to return (default: 20) |

## SEAMS Taxonomy (13 Categories)

### Functional & Behavioral

| Category | Detection Focus | Ambiguity Markers |
|----------|-----------------|-------------------|
| SCOPE | Feature boundaries | `[TBD]`, "etc.", "might include", "possibly" |
| BEHAVIOR | User actions, state transitions | "should", "might", "probably", "as needed" |
| SEQUENCE | Order of operations | "before/after" without clarity |
| AUTHORITY | Permissions, decision makers | "someone", "appropriate person", undefined roles |

### Data & Integration

| Category | Detection Focus | Ambiguity Markers |
|----------|-----------------|-------------------|
| DATA | Entities, formats, validation | Undefined formats, missing constraints |
| INTERFACE | API contracts, protocols | Missing contracts, undefined protocols |
| CONSTRAINT | Limits, bounds | "reasonable", "sufficient", undefined limits |
| TEMPORAL | Timing, duration | "soon", "quickly", "periodically" |

### Quality & Operations

| Category | Detection Focus | Ambiguity Markers |
|----------|-----------------|-------------------|
| ERROR | Error handling | Missing error cases, undefined recovery |
| RECOVERY | Fallback strategies | No degradation path specified |
| ASSUMPTION | Implicit beliefs | Unstated dependencies, assumed knowledge |
| STAKEHOLDER | User perspectives | Missing viewpoints, undefined personas |
| TRACEABILITY | Coverage gaps | Orphan requirements, uncovered areas |

## Detection Process

1. **Parse specification** - Extract all requirements, user stories, constraints
2. **Category scan** - Check each section against category markers
3. **Score findings** - Calculate Impact × Uncertainty for each
4. **Prioritize** - Sort by score descending
5. **Generate questions** - Formulate clarifying questions for top findings

## Scoring Formula

```
Priority Score = Impact × Uncertainty

Impact (1-5):
- 5: Affects architecture, security, or core functionality
- 4: Affects multiple components or user experience
- 3: Affects single component significantly
- 2: Minor feature impact
- 1: Cosmetic or documentation only

Uncertainty (1-5):
- 5: Completely unspecified
- 4: Major gaps in specification
- 3: Partial specification, gaps remain
- 2: Minor clarification needed
- 1: Nearly complete, edge case only
```

## Output Format

```markdown
## Ambiguity Scan Results

**Specification**: [spec_path]
**Scan Date**: [timestamp]
**Total Findings**: [count]

### Coverage Summary

| Category | Status | Findings |
|----------|--------|----------|
| SCOPE | Partial | 2 |
| BEHAVIOR | Missing | 3 |
| DATA | Clear | 0 |
| ERROR | Missing | 2 |
| [etc.] |

### Prioritized Findings

| Rank | Category | Impact | Uncertainty | Score | Finding |
|------|----------|--------|-------------|-------|---------|
| 1 | ERROR | 5 | 5 | 25 | No error handling defined for API failures |
| 2 | AUTHORITY | 4 | 5 | 20 | Role permissions not specified |
| 3 | DATA | 4 | 4 | 16 | User entity missing validation rules |

### Recommended Questions

#### Q1 [ERROR] - Score: 25
**Context**: Spec mentions "API integration" but doesn't define failure handling.
**Question**: How should the system behave when external API calls fail?
**Options**:
- A: Retry with exponential backoff (3 attempts)
- B: Fail fast with user-friendly error
- C: Queue for later retry

#### Q2 [AUTHORITY] - Score: 20
[similar format]

### Next Steps

[Based on findings - recommend /clarify with specific focus]
```

## Integration Points

- **clarify.md**: Primary consumer - uses findings to generate question queue

## Invocation Example

```
Use the Task tool with:
- subagent_type: "speckit-generator:ambiguity-scanner"
- prompt: "Scan .claude/resources/spec.md for ambiguities, focus on SECURITY and DATA categories"
```
