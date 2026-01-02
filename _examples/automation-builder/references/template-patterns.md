# Template Patterns Reference

## Contents
- Template structure
- Pattern 1: Status/progress templates
- Pattern 2: Report templates
- Pattern 3: Checklist templates
- Pattern 4: Configuration templates
- Placeholder conventions
- Update guidance

## Template Structure

```markdown
# Template Title

<!--
Purpose: What this template is for
Updated by: Which command/script populates this
Placeholders: List of [PLACEHOLDER] values
-->

**Last Updated**: [TIMESTAMP]
**Status**: [STATUS]

---

## Section Name

| Field | Value |
|-------|-------|
| Item  | [PLACEHOLDER] |

<!-- 
Inline guidance for complex sections.
These comments help the updating command/script
understand what content belongs here.
-->

---

## Notes

<!-- Optional section for additional context -->
```

## Pattern 1: Status/Progress Templates

Track ongoing work with clear status indicators.

```markdown
# Implementation Status

<!--
Purpose: Track implementation progress across tasks
Updated by: /project.implement after each task
Placeholders: [TIMESTAMP], [PHASE], [PROGRESS], task rows
-->

**Last Updated**: [TIMESTAMP]
**Current Phase**: [PHASE]
**Progress**: [PROGRESS]% ([COMPLETED]/[TOTAL] tasks)

---

## Phase Summary

| Phase | Name | Tasks | Done | Status |
|-------|------|-------|------|--------|
| 1 | Setup | - | - | ○ Pending |
| 2 | Core | - | - | ○ Pending |
| 3 | Tests | - | - | ○ Pending |

**Legend**: ○ Pending | → In Progress | ✓ Complete | ✗ Failed | ⊘ Skipped

---

## Recent Activity

| Time | Task | Status | Notes |
|------|------|--------|-------|
| [TIME] | - | Started | Implementation initialized |

<!--
Activity entries are prepended (newest first).
Format: | HH:MM | T### | Status | Notes |
-->

---

## Blocked Items

| Task | Reason | Since | Resolution |
|------|--------|-------|------------|
| - | - | - | - |

<!--
Tasks that cannot proceed.
Resolution: decision needed | dependency | external
-->

---

## Resume Information

| Field | Value |
|-------|-------|
| Last Completed | - |
| Next Task | - |
| Resume Command | `/project.implement --continue` |
```

## Pattern 2: Report Templates

Structured output for analysis results.

```markdown
# Analysis Report

<!--
Purpose: Document analysis findings
Updated by: /project.analyze
Placeholders: [TIMESTAMP], [TARGET], findings tables
-->

**Generated**: [TIMESTAMP]
**Target**: [TARGET]
**Status**: [STATUS]

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Critical | [CRITICAL_COUNT] |
| Warning | [WARNING_COUNT] |
| Info | [INFO_COUNT] |

[SUMMARY_PARAGRAPH]

---

## Critical Findings

| ID | Location | Issue | Recommendation |
|----|----------|-------|----------------|
| C001 | - | - | - |

<!--
Critical issues that must be addressed.
Include specific file:line references.
-->

---

## Warnings

| ID | Location | Issue | Recommendation |
|----|----------|-------|----------------|
| W001 | - | - | - |

<!--
Issues that should be addressed.
Lower priority than critical.
-->

---

## Informational

| ID | Location | Note |
|----|----------|------|
| I001 | - | - |

<!--
Observations that may be useful.
No action required.
-->

---

## Next Steps

1. [NEXT_STEP_1]
2. [NEXT_STEP_2]

---

## Appendix

### Methodology

[Description of how analysis was performed]

### Tool Versions

| Tool | Version |
|------|---------|
| - | - |
```

## Pattern 3: Checklist Templates

Track completion of discrete items.

```markdown
# Deployment Checklist

<!--
Purpose: Ensure all deployment steps completed
Updated by: /project.deploy
Placeholders: [TIMESTAMP], [VERSION], checkbox states
-->

**Deployment**: [VERSION]
**Date**: [TIMESTAMP]
**Environment**: [ENVIRONMENT]

---

## Pre-Deployment

- [ ] Code review approved
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Changelog updated

<!--
All items must be checked before proceeding.
Script validates these before continuing.
-->

---

## Deployment Steps

- [ ] **Step 1**: Backup current state
  - Command: `./scripts/backup.sh`
  - Verified: [TIMESTAMP or -]
  
- [ ] **Step 2**: Deploy new version
  - Command: `./scripts/deploy.sh [VERSION]`
  - Verified: [TIMESTAMP or -]
  
- [ ] **Step 3**: Run smoke tests
  - Command: `./scripts/smoke-test.sh`
  - Verified: [TIMESTAMP or -]

---

## Post-Deployment

- [ ] Monitoring alerts configured
- [ ] Stakeholders notified
- [ ] Rollback plan documented

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Developer | [NAME] | [DATE] |
| Reviewer | [NAME] | [DATE] |
```

## Pattern 4: Configuration Templates

Capture decisions and settings.

```markdown
# Project Configuration

<!--
Purpose: Document project configuration decisions
Updated by: /project.init
Placeholders: All [BRACKETED] values
-->

**Created**: [TIMESTAMP]
**Last Modified**: [TIMESTAMP]

---

## Project Identity

| Field | Value |
|-------|-------|
| Name | [PROJECT_NAME] |
| Type | [PROJECT_TYPE] |
| Language | [LANGUAGE] |

---

## Structure

```
[PROJECT_NAME]/
├── src/
│   └── [MAIN_MODULE]/
├── tests/
├── docs/
└── [CONFIG_FILE]
```

---

## Dependencies

### Runtime

| Package | Version | Purpose |
|---------|---------|---------|
| - | - | - |

### Development

| Package | Version | Purpose |
|---------|---------|---------|
| - | - | - |

---

## Quality Standards

| Standard | Value | Rationale |
|----------|-------|-----------|
| Test Coverage | [COVERAGE]% | [RATIONALE] |
| Lint Rules | [RULESET] | [RATIONALE] |

---

## Decisions Log

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| [DATE] | [DECISION] | [CHOICE] | [RATIONALE] |

<!--
Record significant decisions here.
Helps future maintainers understand choices.
-->
```

## Placeholder Conventions

### Naming

| Pattern | Usage |
|---------|-------|
| `[TIMESTAMP]` | ISO datetime or relative |
| `[STATUS]` | State indicator |
| `[NAME]` | Entity name |
| `[COUNT]` | Numeric value |
| `[PARAGRAPH]` | Multi-line text |

### Formatting

- Use `[UPPERCASE_SNAKE_CASE]` for all placeholders
- Include type hints in comments: `<!-- [VALUE]: number -->`
- Group related placeholders: `[START_DATE]`, `[END_DATE]`

### Required vs Optional

Mark optional placeholders:

```markdown
| Field | Value |
|-------|-------|
| Name | [NAME] |
| Alias | [ALIAS or -] |
```

## Update Guidance

Include comments that help automation:

```markdown
## Section

<!--
HOW TO UPDATE:
1. Run: script.sh --output json
2. Parse "items" array
3. Add row for each item

VALIDATION:
- All rows must have non-empty values
- Dates must be ISO format
-->

| Item | Value |
|------|-------|
| - | - |
```

This helps both Claude and scripts update templates correctly.
