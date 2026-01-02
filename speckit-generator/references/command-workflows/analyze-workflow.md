# Analyze Workflow Reference

Detailed workflow for the `/speckit.analyze` command.

## Purpose

Provide deterministic, read-only audit of project artifacts for consistency and completeness. Like a linter for specifications and project structure.

## Key Characteristics

- **Read-only**: Never modifies any files
- **Deterministic**: Identical inputs produce identical outputs
- **Stable Finding IDs**: IDs remain consistent across runs
- **Quantified Metrics**: Coverage percentages, counts, scores

---

## Workflow Steps

### Step 1: Discover Artifacts

Scan project for analyzable files:

```
.claude/
├── memory/          → Constitution compliance
├── resources/       → Specs, plans, tasks
└── project-context.md

Source files         → Code-spec alignment
```

Report discovery:
```
Artifacts discovered:
- Specifications: 2 files
- Plans: 3 files (1 master, 2 domain)
- Tasks: 2 files (28 tasks total)
- Memory: 6 files
- Source: 45 files
```

### Step 2: Run Analysis Passes

#### Pass 1: Gap Analysis (GAPS)

Check for missing required elements:

| Check | Severity |
|-------|----------|
| Requirements without plan coverage | CRITICAL |
| Plan phases without tasks | HIGH |
| Tasks without acceptance criteria | MEDIUM |
| Missing memory files for tech stack | HIGH |

#### Pass 2: Consistency Analysis (INCONSISTENCIES)

Check for contradictions:

| Check | Severity |
|-------|----------|
| Conflicting requirements | CRITICAL |
| Plan contradicts spec | CRITICAL |
| Task contradicts plan | HIGH |
| Memory file conflicts | HIGH |

#### Pass 3: Ambiguity Analysis (AMBIGUITIES)

Detect unclear specifications:

| Pattern | Severity |
|---------|----------|
| `[TBD]`, `[TODO]` markers | HIGH |
| `[NEEDS CLARIFICATION]` | HIGH |
| Vague language ("should", "might", "probably") | MEDIUM |
| Missing error handling specs | MEDIUM |

#### Pass 4: Orphan Analysis (ORPHANS)

Find unreferenced elements:

| Check | Severity |
|-------|----------|
| Tasks not traced to plan | HIGH |
| Plan sections not traced to spec | MEDIUM |
| Architecture decisions not used | LOW |

#### Pass 5: Assumption Analysis (ASSUMPTIONS)

Track unvalidated assumptions:

| Check | Severity |
|-------|----------|
| Unvalidated technical assumptions | MEDIUM |
| Implicit organizational assumptions | MEDIUM |
| Environmental assumptions | LOW |

### Step 3: Generate Stable Finding IDs

Finding IDs are deterministic based on:
```
FINDING_ID = hash(category + location + description_normalized)
```

Example: `GAP-a1b2c3`

This ensures:
- Same issue gets same ID across runs
- Resolved issues can be tracked
- Findings can be referenced in other documents

### Step 4: Calculate Metrics

```
Coverage Metrics:
- Requirements → Plan: 95% (19/20)
- Plan → Tasks: 100% (all phases covered)
- Tasks → Constitution: 85% (24/28 have refs)

Quality Metrics:
- Ambiguity score: 12 (lower is better)
- Orphan count: 3
- Assumption count: 7 (4 validated)
```

### Step 5: Generate Report

```markdown
# Analysis Report

Generated: 2024-01-15T10:30:00Z
Project: my-project
Artifacts: 52 files

## Summary

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| GAPS | 1 | 3 | 5 | 2 | 11 |
| INCONSISTENCIES | 0 | 1 | 2 | 0 | 3 |
| AMBIGUITIES | 0 | 4 | 8 | 3 | 15 |
| ORPHANS | 0 | 1 | 2 | 5 | 8 |
| ASSUMPTIONS | 0 | 0 | 4 | 3 | 7 |

**Total Findings**: 44
**Critical/High**: 10 (require attention)

## Coverage Metrics

| Traceability | Coverage | Status |
|--------------|----------|--------|
| Spec → Plan | 95% | ⚠️ |
| Plan → Tasks | 100% | ✓ |
| Tasks → Constitution | 85% | ⚠️ |

## Findings

### GAP-a1b2c3 [CRITICAL]
**Category**: GAPS
**Location**: spec.md:45
**Description**: Requirement REQ-015 has no plan coverage
**Recommendation**: Add plan section addressing REQ-015

### GAP-b2c3d4 [HIGH]
**Category**: GAPS
**Location**: plan.md:Phase 3
**Description**: Phase 3 has no tasks generated
**Recommendation**: Run /speckit.tasks or mark phase as deferred

[... more findings ...]

## Trend (if previous runs exist)

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Total findings | 52 | 44 | -8 ⬇️ |
| Critical | 2 | 1 | -1 ⬇️ |
| Coverage | 82% | 93% | +11% ⬆️ |
```

---

## Finding Format

```markdown
### [FINDING-ID] [SEVERITY]

**Category**: [GAPS | INCONSISTENCIES | AMBIGUITIES | ORPHANS | ASSUMPTIONS]
**Location**: [file:line or file:section]
**First Seen**: [date if tracking history]
**Status**: [NEW | EXISTING | RESOLVED]

**Description**:
[Clear description of the issue]

**Evidence**:
[Specific quotes or references that demonstrate the issue]

**Impact**:
[What problems this causes if not addressed]

**Recommendation**:
[Specific action to resolve]

**Related**:
[Links to related findings]
```

---

## Command Options

```bash
# Full analysis
/speckit.analyze

# Specific category only
/speckit.analyze --category gaps
/speckit.analyze --category inconsistencies

# Verbose output (show all findings, not just critical/high)
/speckit.analyze --verbose

# JSON output for tooling
/speckit.analyze --json

# Compare with previous run
/speckit.analyze --diff

# Specific files only
/speckit.analyze --files spec.md,plan.md
```

---

## Determinism Requirements

For identical inputs, output must be identical:

1. **Sort order**: Findings sorted by severity, then category, then ID
2. **Timestamps**: Use deterministic timestamps or exclude from comparison
3. **File scanning**: Consistent file order (alphabetical)
4. **ID generation**: Hash-based, not sequence-based

Test with:
```bash
analyze > output1.md
analyze > output2.md
diff output1.md output2.md  # Should be empty
```

---

## Integration Points

### With /speckit.clarify

Ambiguity findings can trigger clarify:
```
15 ambiguities found. Run /speckit.clarify to resolve?
```

### With /speckit.plan

Gap findings inform plan updates:
```
1 requirement has no plan coverage. Update plan?
```

### With /speckit.tasks

Orphan tasks or missing task references inform task generation:
```
Phase 3 has no tasks. Run /speckit.tasks?
```

---

## Exit Codes (for scripting)

| Code | Meaning |
|------|---------|
| 0 | No critical or high findings |
| 1 | High findings exist |
| 2 | Critical findings exist |
| 3 | Analysis failed (error) |
