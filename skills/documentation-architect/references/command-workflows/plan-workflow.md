# Plan Workflow

Detailed workflow for `/docs.plan` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Workflow Steps](#workflow-steps)
- [WBS Structure](#wbs-structure)
- [Outputs](#outputs)
- [Idempotency](#idempotency)
- [speckit Integration](#speckit-integration)

---

## Purpose

Create a documentation plan (Work Breakdown Structure) from inventoried sources:
1. Load and analyze inventoried sources
2. Extract documentation requirements
3. Map requirements to Diátaxis quadrants
4. Design target document structure
5. Create prioritized WBS
6. Define dependencies and chunking strategies

---

## Trigger Conditions

**Explicit**:
- User runs `/docs.plan`

**Auto-suggested**:
- After `/docs.inventory` completes
- When `/docs.generate` detects missing plan

**With speckit integration**:
- `/docs.plan --from-speckit` - Use speckit artifacts as input

---

## Workflow Steps

### Step 1: Load Inventory

Read from `docs/_meta/inventory.md`:

```
Loading inventory...
├─ Sources: 12
├─ Coverage gaps: 4
└─ Large sources: 2
```

If inventory missing:
```
No inventory found. Run /docs.inventory first?
[Y] Run inventory  [n] Proceed with limited sources
```

### Step 2: Analyze Sources

For each source, extract:
- Key topics and concepts
- User-facing features
- API surfaces
- Configuration options
- Architectural decisions

**Classification output**:
```markdown
## Source Analysis

### SRC-001: requirements.md
- Topics: Authentication, User Management, API
- Features: Login, Registration, OAuth
- Quadrant fit: How-To (user flows), Reference (API)

### SRC-002: api-design.md
- Topics: REST endpoints, Error handling
- Features: CRUD operations
- Quadrant fit: Reference (primary), How-To (examples)
```

### Step 3: Design Target Structure

Map sources to target document structure:

```
Proposed Documentation Structure:

docs/
├── user/
│   ├── getting-started/
│   │   ├── quickstart.md        ← From: SRC-001 (auth basics)
│   │   └── installation.md      ← From: README.md
│   ├── guides/
│   │   ├── authentication.md    ← From: SRC-001, SRC-003
│   │   └── api-usage.md         ← From: SRC-002
│   └── reference/
│       └── configuration.md     ← From: SRC-004
│
└── developer/
    ├── architecture/
    │   └── overview.md          ← From: SRC-005
    └── reference/
        └── api/
            └── endpoints.md     ← From: SRC-002
```

Present for approval:
```
Target structure identified:
- 8 documents planned
- Covers 75% of sources
- Fills 3 of 4 coverage gaps

Proceed with this structure? [Y/n/modify]
```

### Step 4: Create WBS Items

Generate Work Breakdown Structure entries:

```markdown
## Documentation WBS

| ID | Document | Quadrant | Priority | Sources | Est. Size | Dependencies |
|----|----------|----------|----------|---------|-----------|--------------|
| WBS-001 | quickstart.md | Tutorial | HIGH | SRC-001 | Medium | None |
| WBS-002 | installation.md | Tutorial | HIGH | README | Small | None |
| WBS-003 | authentication.md | How-To | HIGH | SRC-001,SRC-003 | Large | WBS-001 |
| WBS-004 | api-usage.md | How-To | MEDIUM | SRC-002 | Medium | WBS-003 |
| WBS-005 | configuration.md | Reference | MEDIUM | SRC-004 | Medium | None |
| WBS-006 | overview.md | Explanation | LOW | SRC-005 | Large | None |
| WBS-007 | endpoints.md | Reference | MEDIUM | SRC-002 | Large | None |
```

### Step 5: Define Chunking Strategy

For large sources or documents:

```markdown
## Chunking Plan

### SRC-002: api-design.md (5,200 tokens)
Chunk into:
1. Authentication endpoints (chunk 1)
2. User management endpoints (chunk 2)
3. Error handling (chunk 3)

### WBS-007: endpoints.md (target: Large)
Generate in phases:
1. Authentication API section
2. User API section
3. Utility endpoints
```

### Step 6: Set Phases and Gates

Group WBS items into execution phases:

```markdown
## Execution Phases

### Phase 1: Foundation (Priority: HIGH)
- WBS-001: quickstart.md
- WBS-002: installation.md
**Gate**: User can complete basic setup

### Phase 2: Core Guides (Priority: HIGH)
- WBS-003: authentication.md
- WBS-004: api-usage.md
**Gate**: Main user journeys documented

### Phase 3: Reference (Priority: MEDIUM)
- WBS-005: configuration.md
- WBS-007: endpoints.md
**Gate**: Technical reference complete

### Phase 4: Deep Dives (Priority: LOW)
- WBS-006: overview.md
**Gate**: Architecture explained
```

### Step 7: Present Summary

```
Documentation Plan Created:

WBS Items: 7
├─ Phase 1 (Foundation): 2 items
├─ Phase 2 (Core): 2 items
├─ Phase 3 (Reference): 2 items
└─ Phase 4 (Deep): 1 item

Priority Distribution:
├─ HIGH: 4 items
├─ MEDIUM: 2 items
└─ LOW: 1 item

Estimated effort: Medium
Large documents requiring chunking: 2

Files updated:
└─ docs/_meta/plan.md

Next: Run /docs.generate to create documentation
```

---

## WBS Structure

### WBS Item Fields

| Field | Description | Required |
|-------|-------------|----------|
| ID | Unique identifier (WBS-001) | Yes |
| Document | Target file path | Yes |
| Quadrant | Diátaxis quadrant | Yes |
| Priority | HIGH, MEDIUM, LOW | Yes |
| Sources | Source IDs used | Yes |
| Est. Size | Small/Medium/Large | Yes |
| Dependencies | Other WBS IDs | No |
| Phase | Execution phase | No |
| Status | Pending/In Progress/Complete | Yes |

### Priority Guidelines

| Priority | Criteria |
|----------|----------|
| HIGH | User onboarding, critical paths, blocking items |
| MEDIUM | Important but not blocking, enhances understanding |
| LOW | Nice to have, deep dives, edge cases |

### Size Estimates

| Size | Token Range | Generation |
|------|-------------|------------|
| Small | < 1,000 | Single pass |
| Medium | 1,000 - 3,000 | Single pass |
| Large | > 3,000 | May need chunking |

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| Documentation plan | `docs/_meta/plan.md` | WBS and phases |
| Updated inventory | `docs/_meta/inventory.md` | Source-to-doc mapping |

### plan.md Structure

```markdown
# Documentation Plan

**Created**: [timestamp]
**Last Updated**: [timestamp]
**Status**: Active

## Overview

[Brief description of documentation goals]

## Target Structure

[Directory tree of planned docs/]

## Work Breakdown Structure

[WBS table]

## Execution Phases

[Phase definitions with gates]

## Chunking Strategy

[For large sources/documents]

## Dependencies

[Dependency graph or list]
```

---

## Idempotency

**Safe behaviors**:
- Detects existing plan
- Offers options: Update, Regenerate, Skip
- Preserves completed WBS items
- Updates status of changed items
- Adds new items for new sources

**Existing plan detected**:
```
Existing documentation plan found:
├─ Created: 2024-01-15
├─ WBS Items: 7 (2 complete, 5 pending)
└─ Last updated: 2024-01-16

Options:
1. Update - Add new items, preserve existing
2. Regenerate - Create fresh plan (confirm completed items)
3. Skip - Keep existing plan
```

**Re-run behavior**:
```
Plan update:
  + Added 2 new WBS items (new sources found)
  = 5 items unchanged
  ✓ 2 items already complete (preserved)
```

---

## speckit Integration

### Using speckit Artifacts

When called with `--from-speckit`:

```bash
/docs.plan --from-speckit
```

**Reads from**:
- `.claude/resources/plan.md` - speckit implementation plan
- `.claude/resources/*.md` - Specification files
- `.claude/memory/project-context.md` - Project description

**Extracts**:
- Architecture decisions → Explanation quadrant
- API designs → Reference quadrant
- User features → How-To quadrant
- Setup steps → Tutorial quadrant

### Integration Flow

```
speckit artifacts → /docs.plan --from-speckit
                          │
                          ├─ Read speckit plan.md
                          ├─ Extract implementation items
                          ├─ Map to documentation needs
                          └─ Generate docs WBS
```

### Example Mapping

From speckit `plan.md`:
```markdown
## Implementation Tasks
- [ ] Implement authentication module
- [ ] Create REST API endpoints
- [ ] Add configuration system
```

Generated docs WBS:
```markdown
| ID | Document | Source |
|----|----------|--------|
| WBS-001 | authentication.md | speckit: auth module |
| WBS-002 | api-reference.md | speckit: REST API |
| WBS-003 | configuration.md | speckit: config system |
```
