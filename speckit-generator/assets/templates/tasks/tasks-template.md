# [Project/Domain] Tasks

Generated: [ISO_TIMESTAMP]
Plan: [PLAN_FILE_REFERENCE]
Constitution: [CONSTITUTION_VERSION_HASH]
Memory Files: [LIST_OF_LOADED_MEMORY_FILES]

## Metadata

| Metric | Value |
|--------|-------|
| Total Tasks | [COUNT] |
| Phases | [COUNT] |
| Groups | [LIST] |
| Last Updated | [TIMESTAMP] |

---

## Phase 1: [Phase Name]

### TASK-001: [Task Title]

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @foundation

**Constitution Sections**:
- §[X.Y] ([Section Title])
- §[X.Z] ([Section Title])

**Memory Files**:
- [file.md]: "[Relevant Section]"
- [file.md]: "[Relevant Section]"

**Plan Reference**: [PHASE-X], [AD-XXX]

**Description**:
[Clear description of what needs to be done. Should be actionable
and specific enough to execute without ambiguity.]

**Acceptance Criteria**:
- [ ] [Criterion 1 - measurable/verifiable]
- [ ] [Criterion 2 - measurable/verifiable]
- [ ] [Criterion 3 - measurable/verifiable]

**Dependencies**: None

**Estimated Scope**: S

---

### TASK-002: [Task Title]

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @foundation

**Constitution Sections**:
- §[X.Y] ([Section Title])

**Memory Files**:
- [file.md]: "[Relevant Section]"

**Plan Reference**: [PHASE-X]

**Description**:
[Clear description]

**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Dependencies**: TASK-001

**Estimated Scope**: M

---

## Phase 2: [Phase Name]

### TASK-003: [Task Title]

**Status**: PENDING
**Priority**: P2
**Phase**: 2
**Group**: @core

**Constitution Sections**:
- §[X.Y] ([Section Title])

**Memory Files**:
- [file.md]: "[Relevant Section]"

**Plan Reference**: [PHASE-X], [AD-XXX]

**Description**:
[Clear description]

**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Dependencies**: TASK-002

**Estimated Scope**: L

---

## Task Status Legend

| Status | Meaning |
|--------|---------|
| PENDING | Not started, ready for execution |
| IN_PROGRESS | Currently being worked on |
| COMPLETED | Done and verified |
| FAILED | Execution failed, needs attention |
| BLOCKED | Waiting on dependency or blocker |
| SKIPPED | Intentionally not done (documented) |

## Priority Legend

| Priority | Meaning |
|----------|---------|
| P1 | Foundation - blocks other work |
| P2 | Core functionality |
| P3 | Enhancement - nice to have |

## Scope Legend

| Scope | Meaning |
|-------|---------|
| S | Small - < 1 hour |
| M | Medium - 1-4 hours |
| L | Large - 4+ hours |
