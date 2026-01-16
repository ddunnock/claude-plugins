# Specification Analysis Report

Generated: [ISO_TIMESTAMP]
Feature: [FEATURE_NAME]
Artifacts Analyzed: spec.md, plan.md, tasks.md

---

## Executive Summary

**Overall Status**: [PASS | NEEDS_ATTENTION | BLOCKED]
**Critical Issues**: [COUNT]
**Ready for Implementation**: [YES/NO]

---

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| [ID] | [CAT] | [SEV] | [LOC] | [SUMMARY] | [REC] |

*[N] findings total. Sorted by severity (CRITICAL → LOW).*

---

## Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| [REQ-KEY] | [✓/✗] | [IDs] | [NOTES] |

**Coverage**: [N]% ([COVERED]/[TOTAL] requirements have ≥1 task)

---

## Directive Alignment

### Directives Loaded

| Directive | Status | Reason |
|-----------|--------|--------|
| constitution.md | ✓ | Always loaded |
| security.md | ✓ | Always loaded |
| testing.md | ✓ | Always loaded |
| documentation.md | ✓ | Always loaded |
| typescript.md | [✓/✗] | [Detected: TypeScript / Not applicable] |
| python.md | [✓/✗] | [Detected: Python / Not applicable] |
| rust.md | [✓/✗] | [Detected: Rust / Not applicable] |
| react-nextjs.md | [✓/✗] | [Detected: React/Next.js / Not applicable] |
| tailwind-*.md | [✓/✗] | [Detected: Frontend styling / Not applicable] |
| git-cicd.md | [✓/✗] | [CI/CD referenced / Not applicable] |

### Directive Violations

*Grouped by source directive:*

**From constitution.md:**
- [FINDING-ID]: [Description]

**From security.md:**
- [FINDING-ID]: [Description]

**From testing.md:**
- [FINDING-ID]: [Description]

*(Or "No directive violations found." if clean)*

---

## Unmapped Tasks

Tasks with no traced requirement or user story:

| Task ID | Description | Recommendation |
|---------|-------------|----------------|
| [ID] | [DESC] | [REC] |

*(Or "All tasks are mapped to requirements." if clean)*

---

## Metrics

| Metric | Value |
|--------|-------|
| Total Requirements | [N] |
| Total Tasks | [N] |
| Requirement Coverage | [N]% |
| Ambiguity Count | [N] |
| Duplication Count | [N] |
| Underspecification Count | [N] |
| Directive Violations | [N] |
| Coverage Gaps | [N] |
| Inconsistencies | [N] |
| **Critical Issues** | **[N]** |
| **High Issues** | **[N]** |

---

## Next Actions

### If CRITICAL Issues Exist

⚠️ **Resolve before `/speckit.implement`:**

1. [FINDING-ID]: [Action] - [Command suggestion]
2. [FINDING-ID]: [Action] - [Command suggestion]

### If Only MEDIUM/LOW Issues

✓ **You may proceed with `/speckit.implement`.**

Suggested improvements:
- [FINDING-ID]: [Suggestion]
- [FINDING-ID]: [Suggestion]

### Command Suggestions

- `Run /speckit.clarify` - To resolve ambiguities
- `Run /speckit.plan` - To adjust architecture/plan
- `Run /speckit.tasks` - To regenerate tasks with better coverage
- `Manually edit [file]` - For specific fixes

---

## Remediation Offer

Would you like me to suggest concrete remediation edits for the top [N] issues?

*(This is read-only analysis. No changes will be applied without explicit approval.)*
