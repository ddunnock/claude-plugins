Deterministic, read-only audit of project artifacts for consistency and completeness.

## Usage
- `/speckit.analyze` - Full analysis
- `/speckit.analyze --verbose` - Detailed output
- `/speckit.analyze --category gaps` - Filter by category

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
