# Analyze Workflow

Detailed workflow for `/docs.analyze` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Characteristics](#characteristics)
- [Workflow Steps](#workflow-steps)
- [Quality Metrics](#quality-metrics)
- [Outputs](#outputs)
- [Idempotency](#idempotency)

---

## Purpose

Read-only audit of documentation quality:
1. Assess documentation against quality criteria
2. Calculate Diátaxis coverage matrix
3. Detect structural issues (broken links, orphans)
4. Identify content issues (TODOs, placeholders)
5. Evaluate user journey coverage
6. Generate actionable improvement report

**Key principle**: This command NEVER modifies files. It only reads and reports.

---

## Trigger Conditions

**Explicit**:
- User runs `/docs.analyze`

**Auto-suggested**:
- Before major releases
- As part of CI/CD pipeline
- When requested by other commands needing quality check

---

## Characteristics

Following the speckit.analyze pattern:

| Property | Behavior |
|----------|----------|
| Read-only | Never modifies any files |
| Deterministic | Same input always produces same output |
| Stable IDs | Finding IDs remain consistent across runs |
| Cacheable | Results can be cached and compared |

### Why Read-Only Matters

- Safe to run anytime, anywhere
- Can be automated in CI/CD
- No risk of unintended changes
- Clear separation from `/docs.generate`

---

## Workflow Steps

### Step 1: Discover Documentation

Scan for all documentation files:

```
Discovering documentation...

Found:
├─ docs/index.md
├─ docs/user/ (4 files)
├─ docs/developer/ (3 files)
├─ docs/_meta/ (3 files)
├─ README.md
└─ CHANGELOG.md

Total: 12 documentation files
```

### Step 2: Structural Analysis

Check documentation structure:

```
Structural Analysis:

Directory Structure:
├─ ✓ docs/index.md exists
├─ ✓ docs/user/ section present
├─ ✓ docs/developer/ section present
├─ ⚠ docs/user/concepts/ empty
└─ ✓ docs/_meta/ present

Link Validation:
├─ Internal links: 23 checked
│   ├─ ✓ Valid: 21
│   └─ ✗ Broken: 2
├─ External links: 8 checked
│   ├─ ✓ Valid: 7
│   └─ ⚠ Unverified: 1
└─ Orphan pages: 1 found
```

### Step 3: Content Quality

Analyze each document for quality:

```markdown
## Content Quality Scores

| Document | Accuracy | Clarity | Complete | Structure | Overall |
|----------|----------|---------|----------|-----------|---------|
| quickstart.md | 90% | 85% | 95% | 90% | 90% |
| authentication.md | 85% | 80% | 70% | 85% | 80% |
| api-users.md | 95% | 90% | 90% | 95% | 93% |
| configuration.md | 80% | 75% | 60% | 80% | 74% |

Average Quality: 84%
```

### Step 4: Diátaxis Coverage

Assess coverage across quadrants:

```markdown
## Diátaxis Coverage Matrix

| Quadrant | Documents | Coverage | Health |
|----------|-----------|----------|--------|
| Tutorial | 2 | 60% | ⚠ Needs improvement |
| How-To | 3 | 80% | ✓ Good |
| Reference | 4 | 90% | ✓ Excellent |
| Explanation | 1 | 40% | ✗ Critical gap |

### Coverage Details

**Tutorial (Learning-oriented)**
├─ Getting started: ✓
├─ Installation: ✓
└─ First project: ✗ Missing

**How-To (Task-oriented)**
├─ Authentication: ✓
├─ API usage: ✓
├─ Deployment: ✗ Missing
└─ Troubleshooting: ✓

**Reference (Information-oriented)**
├─ API reference: ✓
├─ Configuration: ✓
├─ CLI reference: ✓
└─ Error codes: ✓

**Explanation (Understanding-oriented)**
├─ Architecture: ⚠ Incomplete
├─ Design decisions: ✗ Missing
└─ Concepts: ✗ Missing
```

### Step 5: Content Issues

Detect specific problems:

```markdown
## Content Issues

### Placeholders Found (5)

| ID | Location | Text |
|----|----------|------|
| PH-001 | quickstart.md:45 | [TODO: Add example] |
| PH-002 | config.md:23 | [Insert diagram] |
| PH-003 | api-users.md:67 | [TBD] |
| PH-004 | README.md:12 | [Coming soon] |
| PH-005 | architecture.md:34 | [To be documented] |

### Stale Content (2)

| ID | Location | Indicator |
|----|----------|-----------|
| ST-001 | quickstart.md | References v1.0 (current: v2.1) |
| ST-002 | api-auth.md | Mentions deprecated endpoint |

### Missing Elements (3)

| ID | Location | Missing |
|----|----------|---------|
| ME-001 | quickstart.md | Prerequisites section |
| ME-002 | config.md | Default values table |
| ME-003 | api-users.md | Error responses |
```

### Step 6: User Journey Analysis

Evaluate documentation from user perspective:

```markdown
## User Journey Coverage

### New User Journey
1. ✓ Find documentation (README links)
2. ✓ Understand purpose (Overview)
3. ⚠ Install project (Partial)
4. ✓ Run first example (Quickstart)
5. ✗ Next steps guidance (Missing)

**Journey Score**: 70%

### Developer Integration Journey
1. ✓ Find API docs
2. ✓ Understand authentication
3. ✓ Make first API call
4. ⚠ Handle errors (Incomplete)
5. ✓ Advanced usage

**Journey Score**: 80%

### Contributor Journey
1. ✓ Find contribution guide
2. ⚠ Setup development env (Partial)
3. ✗ Architecture overview (Missing)
4. ⚠ Testing guide (Incomplete)
5. ✗ Release process (Missing)

**Journey Score**: 40%
```

### Step 7: Generate Report

Compile findings into actionable report:

```
Analysis Complete

Summary:
├─ Total documents: 12
├─ Average quality: 84%
├─ Diátaxis coverage: 68%
├─ User journey score: 63%
└─ Issues found: 15

Priority Actions:
1. HIGH: Fill Explanation quadrant gaps
2. HIGH: Remove 5 placeholders
3. MEDIUM: Fix 2 broken links
4. MEDIUM: Update stale version references
5. LOW: Add missing prerequisites section

Report written to: docs/_meta/analysis-report.md
```

---

## Quality Metrics

### Document Quality Score

Each document scored on:

| Metric | Weight | Criteria |
|--------|--------|----------|
| Accuracy | 25% | Claims verified, sources cited |
| Clarity | 25% | Scannable, jargon-free, examples |
| Completeness | 25% | All sections present, no TODOs |
| Structure | 25% | Follows template, proper headings |

### Scoring Rubric

| Score | Label | Meaning |
|-------|-------|---------|
| 90-100% | Excellent | Publication ready |
| 80-89% | Good | Minor improvements |
| 70-79% | Adequate | Needs attention |
| 60-69% | Poor | Significant issues |
| <60% | Critical | Major rewrite needed |

### Diátaxis Health

| Health | Criteria |
|--------|----------|
| ✓ Excellent | >80% coverage, high quality |
| ✓ Good | 60-80% coverage, acceptable quality |
| ⚠ Needs work | 40-60% coverage or quality issues |
| ✗ Critical | <40% coverage or missing entirely |

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| Analysis report | `docs/_meta/analysis-report.md` | Full findings |
| JSON export | Optional: `--json` | Machine-readable |
| Summary | Console | Quick overview |

### analysis-report.md Structure

```markdown
# Documentation Analysis Report

**Generated**: [timestamp]
**Version**: [commit hash if git]

## Executive Summary

[Key metrics and priority actions]

## Quality Scores

[Document-by-document scores]

## Diátaxis Coverage

[Quadrant coverage matrix]

## Structural Analysis

[Links, orphans, structure]

## Content Issues

[Placeholders, stale, missing]

## User Journeys

[Journey coverage analysis]

## Recommendations

[Prioritized action items]

## Appendix

[Detailed findings with IDs]
```

---

## Idempotency

**Guaranteed behaviors**:
- Never creates or modifies documentation
- Same docs = same analysis (deterministic)
- Finding IDs remain stable
- Can be run repeatedly without side effects

**Stable Finding IDs**:

```python
def generate_finding_id(finding_type: str, location: str) -> str:
    """Generate stable, reproducible finding ID."""
    # Based on type + location, not timestamp
    return f"{finding_type}-{hash(location)[:3]}"

# Examples:
# Placeholder at config.md:23 → PH-A3F
# Broken link at index.md:45 → BL-7C2
```

**Comparison across runs**:

```
Previous analysis (2024-01-15):
├─ Issues: 20
├─ Quality: 78%
└─ Coverage: 65%

Current analysis (2024-01-20):
├─ Issues: 15 (-5)
├─ Quality: 84% (+6%)
└─ Coverage: 68% (+3%)

Resolved:
├─ PH-001: Removed
├─ PH-003: Removed
├─ BL-001: Fixed
├─ BL-002: Fixed
└─ ST-001: Updated

New:
└─ ME-004: New missing element found
```

---

## Integration with Other Commands

### Before `/docs.generate`

```
Run analysis before generating?
- Identifies gaps to prioritize
- Flags quality issues early
```

### After `/docs.sync`

```
Analysis recommended after sync.
- Verify sync resolved discrepancies
- Check if new issues introduced
```

### CI/CD Integration

```yaml
# Example GitHub Action
- name: Analyze Documentation
  run: |
    # Run analyze command
    claude docs.analyze --json > analysis.json

    # Fail if critical issues
    jq '.summary.critical > 0' analysis.json && exit 1
```
