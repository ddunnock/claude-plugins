---
description: "Validate ADRs have required fields for their designated level"
when_to_use: "Use during /plan to ensure architecture decisions are properly documented"
colors:
  light: "#ca8a04"
  dark: "#facc15"
---

# ADR Validator Agent

Validate Architecture Decision Records against MADR template requirements.

## Purpose

Ensure all ADRs in the plan have the required fields for their designated level (Lightweight, Standard, or Full), and that the content is complete and consistent.

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `plan_path` | Yes | Path to plan file containing ADRs |
| `default_level` | No | Default level if not specified (Lightweight/Standard/Full) |
| `strict_status` | No | If true, require explicit status transitions |

## ADR Template Levels

### Lightweight

Required fields:
- Status
- Context and Problem Statement
- Decision Outcome
- Consequences

### Standard (Default)

All Lightweight fields plus:
- Date
- Decision-makers
- Decision Drivers
- Considered Options

### Full

All Standard fields plus:
- Confirmation (how compliance will be verified)
- Traceability (REQ and TASK references)

## Field Validation Rules

| Field | Validation |
|-------|------------|
| Status | Must be: proposed, accepted, rejected, deprecated, superseded |
| Date | Must be valid ISO date (YYYY-MM-DD) |
| Decision-makers | Non-empty list |
| Context | 2+ sentences or a question |
| Decision Drivers | 2+ bullet points |
| Considered Options | 2+ numbered options |
| Decision Outcome | Must reference a considered option |
| Consequences | At least 1 good and 1 bad |
| Confirmation | Must describe verification method |
| Traceability | REQ-XXX and/or TASK-XXX references |

## Detection Process

1. **Parse plan** - Extract all ADR sections (### ADR-XXX pattern)
2. **Detect level** - Infer from fields present or use default
3. **Validate fields** - Check required fields for that level
4. **Check content** - Validate field content meets requirements
5. **Check consistency** - Status matches content (e.g., rejected has rationale)

## Output Format

```markdown
## ADR Validation Results

**Plan File**: [plan_path]
**ADRs Found**: [count]
**Default Level**: [level]

### ADR Summary

| ADR | Title | Status | Level | Validation |
|-----|-------|--------|-------|------------|
| ADR-001 | OAuth 2.0 for auth | accepted | Standard | PASS |
| ADR-002 | PostgreSQL for DB | proposed | Standard | PASS |
| ADR-003 | Next.js API routes | proposed | Lightweight | WARN |
| ADR-004 | Caching strategy | proposed | Standard | FAIL |

### Detailed Results

#### ADR-001: OAuth 2.0 for auth - PASS

| Field | Required | Present | Valid |
|-------|----------|---------|-------|
| Status | ✓ | ✓ | ✓ (accepted) |
| Date | ✓ | ✓ | ✓ (2024-01-15) |
| Context | ✓ | ✓ | ✓ (3 sentences) |
| Decision Drivers | ✓ | ✓ | ✓ (3 items) |
| Considered Options | ✓ | ✓ | ✓ (3 options) |
| Decision Outcome | ✓ | ✓ | ✓ (references option 1) |
| Consequences | ✓ | ✓ | ✓ (2 good, 1 bad) |

#### ADR-003: Next.js API routes - WARN

Detected as Lightweight (missing Standard fields)

| Field | Required | Present | Valid | Note |
|-------|----------|---------|-------|------|
| Status | ✓ | ✓ | ✓ | |
| Context | ✓ | ✓ | ✗ | Only 1 sentence |
| Decision Outcome | ✓ | ✓ | ✓ | |
| Consequences | ✓ | ✓ | ✗ | Missing "bad" consequence |

**Recommendations**:
- Expand context to 2+ sentences
- Add at least one negative consequence

#### ADR-004: Caching strategy - FAIL

| Field | Required | Present | Valid | Note |
|-------|----------|---------|-------|------|
| Status | ✓ | ✓ | ✓ | |
| Date | ✓ | ✗ | - | Missing |
| Decision-makers | ✓ | ✗ | - | Missing |
| Context | ✓ | ✓ | ✓ | |
| Considered Options | ✓ | ✗ | - | Missing |
| Decision Outcome | ✓ | ✓ | ✗ | Doesn't reference option |

**Required Actions**:
- Add Date field
- Add Decision-makers
- Add Considered Options with 2+ alternatives
- Update Decision Outcome to reference chosen option

### Status Consistency Check

| ADR | Status | Issue |
|-----|--------|-------|
| ADR-004 | proposed | OK - no issues |
| ADR-001 | accepted | OK - has confirmation |
| ADR-005 | rejected | WARN - missing rejection rationale |

### Overall Assessment

**Valid ADRs**: [X]/[Y] ([Z]%)
**Blocking Issues**: [count]
**Recommendation**: [Fix FAIL items before proceeding | Ready for tasks]
```

## Integration Points

- **plan.md**: Primary consumer - validates ADRs during plan generation

## Invocation Example

```
Use the Task tool with:
- subagent_type: "speckit-generator:adr-validator"
- prompt: "Validate ADRs in .claude/resources/plan.md at Standard level"
```
