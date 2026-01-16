# Tasks Workflow Reference

Detailed workflow for the `/speckit.tasks` command with SMART validation for acceptance criteria.

## Purpose

Generate SMART-validated implementation tasks from plans + constitution + memory files. Tasks define HOW to implement what the plan describes, with verifiable acceptance criteria.

## Key Features

- **SMART Validation**: Every acceptance criterion validated for verifiability
- **Plan Traceability**: Full chain from TASK → PHASE → ADR → REQ
- **8-Point Validation**: Comprehensive checklist before completion
- **Constitution Integration**: Tasks reference specific sections

## Idempotency

- Preserves existing task statuses
- Adds new tasks for new plan items
- Never removes manually added tasks
- Updates task content while preserving status
- Updates SMART validation on regeneration

---

## SMART Validation Framework

Every acceptance criterion must pass SMART validation:

| Element | Requirement | Fail Condition |
|---------|-------------|----------------|
| **S**pecific | Clear, concrete action | "properly", "correctly", "fully", "appropriately" |
| **M**easurable | Objective verification | No command/metric/file check defined |
| **A**chievable | Single task scope | Requires other tasks to complete first |
| **R**elevant | Ties to task purpose | No trace to plan/requirement/ADR |
| **T**ime-bound | Immediate verification | Requires external delays or human approval |

### SMART Strictness Levels

| Level | Behavior | When to Use |
|-------|----------|-------------|
| Strict | Block until criterion rewritten | Critical tasks, security-related |
| Standard | Flag for review, allow with warning | Default for most tasks |
| Relaxed | Log finding only | Exploratory/research tasks |

### SMART Failure Examples

| Criterion | Issue | SMART Failure | Suggested Fix |
|-----------|-------|---------------|---------------|
| "Works correctly" | Vague | S✗ (not specific) | "Returns 200 OK with user JSON" |
| "Performance is good" | No metric | M✗ (not measurable) | "Response time < 200ms (p95)" |
| "Complete auth system" | Too large | A✗ (not achievable) | Split into multiple tasks |
| "Add logging" (no trace) | Orphan | R✗ (not relevant) | Link to plan phase/ADR |
| "User approves design" | External | T✗ (not time-bound) | "Design review checklist passes" |

---

## Workflow Steps

### Step 1: Load Plan(s)

```
1. Find plan files in speckit/
2. Parse plan structure (phases, requirements, ADRs)
3. Identify domains from complex plans
4. Extract task generation notes from each phase

If no plans found:
"No plans found. Run /speckit.plan first?"
```

### Step 2: Load Constitution

Read `.claude/memory/constitution.md`:
- Extract section structure
- Build section index for referencing
- Identify applicable sections per task type

Section reference format:
- `§1.0` - Chapter
- `§1.1` - Section
- `§1.1.a` - Subsection

### Step 3: Load Memory Files

Based on project tech stack:
```
Memory files loaded:
- constitution.md (universal)
- typescript.md (TypeScript detected)
- react-nextjs.md (Next.js detected)
- testing.md (universal)
```

Extract relevant sections for each task type.

### Step 4: Generate Tasks

For each plan phase, generate tasks with SMART-validated criteria:

```markdown
# [Domain] Tasks

Generated: [timestamp]
Plan: plan.md
Constitution: [version]

## Metadata
- Total Tasks: [count]
- Phases: [count]
- SMART Compliance: [percentage]

## Phase 1: Foundation

### TASK-001: Initialize project structure
**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @foundation

**Plan Reference**: PHASE-1, ADR-001
**Constitution Sections**: §3.1, §3.2
**Memory Files**: typescript.md, git-cicd.md

**Description**:
Set up the initial project structure following the patterns defined
in constitution.md §3.1. This includes...

**Acceptance Criteria**:
- [ ] Directory structure matches §3.1 template
      Verification: `diff -r project/ .claude/templates/structure/`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Configuration files exist and are valid
      Verification: `npm run validate:config`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Initial commit follows git-cicd.md format
      Verification: `git log -1 --format='%s' | grep -E '^(feat|fix|chore):'`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None

**Estimated Scope**: M
```

### Step 5: SMART Validate All Criteria

For each acceptance criterion:

```
SMART Validation Process:

1. Specific Check:
   - Contains vague words? ("properly", "correctly", "fully") → S✗
   - Describes concrete action? → S✓

2. Measurable Check:
   - Has verification command/metric? → M✓
   - Subjective assessment only? → M✗

3. Achievable Check:
   - Depends on other incomplete tasks? → A✗
   - Self-contained within this task? → A✓

4. Relevant Check:
   - Links to plan phase or ADR? → R✓
   - Orphan (no traceability)? → R✗

5. Time-bound Check:
   - Can verify immediately after implementation? → T✓
   - Requires external delay/approval? → T✗
```

#### SMART Validation Output

```markdown
### SMART Validation Results

| Task | Criterion | S | M | A | R | T | Status |
|------|-----------|---|---|---|---|---|--------|
| TASK-001 | Directory structure matches | ✓ | ✓ | ✓ | ✓ | ✓ | Pass |
| TASK-001 | Config files valid | ✓ | ✓ | ✓ | ✓ | ✓ | Pass |
| TASK-003 | Works correctly | ✗ | ✗ | ✓ | ✓ | ✓ | Fail |
| TASK-005 | Performance good | ✓ | ✗ | ✓ | ✓ | ✓ | Warn |

**Overall Compliance**: 87% (13/15 criteria pass)
**Failures**: 1 (must fix)
**Warnings**: 1 (review recommended)
```

### Step 6: Assign Task Metadata

#### Priority Assignment

| Priority | Criteria |
|----------|----------|
| P1 | Foundation, blocks other tasks |
| P2 | Core functionality |
| P3 | Enhancement, nice-to-have |

#### Group Assignment

Groups enable batch execution:
- `@foundation` - Initial setup tasks
- `@core` - Core functionality
- `@testing` - Test-related tasks
- `@docs` - Documentation tasks
- `@polish` - Final refinements

#### Dependency Detection

Automatically detect:
- Explicit plan dependencies
- Implicit code dependencies
- Constitution prerequisites

### Step 7: 8-Point Validation

Before completing task generation, verify ALL items:

```markdown
## Task Validation

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1 | SMART criteria validated | ✓ | 87% compliance, 1 failure |
| 2 | Plan traceability established | ✓ | All tasks linked to phases |
| 3 | Constitution references valid | ✓ | All §X.X refs exist |
| 4 | Memory file references valid | ⚠ | rust.md not in project |
| 5 | No circular dependencies | ✓ | DAG verified |
| 6 | Status-criteria consistent | ✓ | No completed tasks with unchecked criteria |
| 7 | ID uniqueness verified | ✓ | No duplicate TASK-XXX |
| 8 | Phase grouping correct | ✓ | Tasks in correct phases |

**Issues found**: 2 (1 blocking, 1 warning)
**Blocking issues**: 1 (SMART failure in TASK-003)
**SMART compliance**: 87%
```

#### Validation Rules

| Check | Fail Condition | Action |
|-------|----------------|--------|
| 1. SMART criteria | Any criterion fails SMART (Strict mode) | Block, rewrite criterion |
| 2. Plan traceability | TASK with no PHASE/ADR link | Block, require link |
| 3. Constitution refs | Invalid section reference (§X.X not found) | Warn, suggest correction |
| 4. Memory refs | File not in project | Warn, list available files |
| 5. Dependencies | Cycle detected (TASK-A → B → C → A) | Block, show cycle |
| 6. Status consistency | COMPLETED task with unchecked `[ ]` criteria | Block, fix status |
| 7. ID uniqueness | Duplicate TASK-XXX | Block, renumber |
| 8. Phase grouping | Task in wrong phase (prereq incomplete) | Warn, suggest move |

### Step 8: Save and Report

```markdown
## Task Generation Complete

Generated 15 tasks across 3 phases:

| Phase | Tasks | P1 | P2 | P3 |
|-------|-------|----|----|----|
| Phase 1: Foundation | 5 | 3 | 2 | 0 |
| Phase 2: Core | 7 | 2 | 4 | 1 |
| Phase 3: Polish | 3 | 0 | 1 | 2 |

### SMART Compliance

| Status | Count |
|--------|-------|
| All criteria pass | 12 tasks |
| Has warnings | 2 tasks |
| Has failures | 1 task |

**Overall**: 87% SMART compliant

### SMART Failures

| Task | Criterion | Issue | Suggested Fix |
|------|-----------|-------|---------------|
| TASK-003 | "Works correctly" | S✗ Not specific | "Returns 200 OK with user JSON" |

### 8-Point Validation
- [x] SMART criteria validated
- [x] Plan traceability established
- [x] Constitution references valid
- [ ] Memory references valid (1 warning)
- [x] No circular dependencies
- [x] Status-criteria consistent
- [x] IDs unique
- [x] Phase grouping correct

### Constitution Coverage
- §3.1 (Project Structure): 4 tasks
- §4.1 (Error Handling): 6 tasks
- §4.2 (Logging): 3 tasks

### Groups
- @foundation: 5 tasks
- @core: 7 tasks
- @testing: 3 tasks

**Action Required**: Fix SMART failure in TASK-003 before proceeding.

Next step: Run /speckit.implement to begin execution
```

---

## Task File Format

### File Structure

```markdown
# [Project/Domain] Tasks

Generated: [ISO timestamp]
Plan: [plan file reference]
Constitution: [version/hash]
Memory Files: [list]

## Metadata
- Total Tasks: [count]
- Phases: [count]
- SMART Compliance: [percentage]
- Last Updated: [timestamp]

## Phase 1: [Phase Name]

### TASK-001: [Title]
[task content with SMART-validated criteria]

### TASK-002: [Title]
[task content with SMART-validated criteria]

## Phase 2: [Phase Name]
...
```

### Task Content

Each task contains:

| Field | Purpose |
|-------|---------|
| Status | Current state (PENDING, IN_PROGRESS, COMPLETED, FAILED, etc.) |
| Priority | P1/P2/P3 |
| Phase | Which phase this belongs to |
| Group | @tag for batch selection |
| Plan Reference | Traceability to plan phase and ADR |
| Constitution Sections | Which constitution sections apply |
| Memory Files | Which memory files provide guidance |
| Description | What to do |
| Acceptance Criteria | SMART-validated definition of done |
| Dependencies | What must complete first |
| Estimated Scope | S/M/L complexity indicator |

### Acceptance Criteria Format

Each criterion includes:
1. Checkbox `- [ ]` for tracking
2. Clear, specific description
3. Verification command or check
4. SMART validation status

```markdown
**Acceptance Criteria**:
- [ ] File `src/lib/auth.ts` exports `authenticate` function
      Verification: `grep -q "export.*authenticate" src/lib/auth.ts`
      SMART: S✓ M✓ A✓ R✓ T✓
```

---

## Update Mode

When tasks already exist:

```
Existing tasks found: project-tasks.md
- Total: 15 tasks
- COMPLETED: 5
- IN_PROGRESS: 1
- PENDING: 9
- SMART compliance: 93%

Options:
1. Add new tasks only (preserve existing)
2. Update task content (preserve statuses, refresh SMART validation)
3. Full regenerate (reset all statuses)
4. View changes
```

Update behavior:
- New plan items → New tasks added
- Removed plan items → Tasks marked OBSOLETE (not deleted)
- Changed plan items → Task content updated, status preserved
- SMART validation refreshed for all criteria

---

## Constitution Section Mapping

Automatic mapping based on task type:

| Task Type | Constitution Sections |
|-----------|----------------------|
| Setup/Init | §3 (Structure), §7 (Security) |
| API/Backend | §4 (Error Handling), §5 (Performance) |
| UI/Frontend | §6 (Accessibility), §8 (UX) |
| Testing | §9 (Testing), §10 (Quality) |
| Documentation | §11 (Documentation) |

### Section Extraction

For each referenced section, extract:
1. Section header
2. Key requirements
3. Examples if available

Present in task context:
```markdown
**Constitution Sections**:
- §4.1 (Error Handling)
  > All errors must be caught and logged with correlation IDs.
  > User-facing errors must be sanitized to prevent information leakage.
```

---

## Memory File Integration

### Relevant Section Detection

For each task, identify relevant memory file sections:

```python
def find_relevant_sections(task_type, memory_files):
    relevance_map = {
        "api": ["API Design", "Error Handling", "Validation"],
        "ui": ["Component Patterns", "State Management"],
        "test": ["Testing Strategy", "Coverage Requirements"],
    }
    return sections matching task_type
```

### Section Presentation

```markdown
**Memory Files**:
- typescript.md: "Error Handling Patterns"
  > Use Result<T, E> pattern for recoverable errors...
- testing.md: "Unit Test Requirements"
  > All public functions must have unit tests...
```

---

## SMART Criterion Rewrite Process

When a criterion fails SMART validation:

### 1. Identify the Failure

```
TASK-003, Criterion: "API works correctly"
SMART: S✗ M✗ A✓ R✓ T✓

Issues:
- S✗: "correctly" is vague
- M✗: No verification method specified
```

### 2. Rewrite Following Pattern

| Element | Before | After |
|---------|--------|-------|
| Specific | "works correctly" | "returns 200 with user object containing id, email, name" |
| Measurable | (none) | `curl -s /api/user/1 | jq '.id, .email, .name'` |

### 3. Validate Rewrite

```markdown
- [ ] GET /api/user/:id returns 200 with JSON containing id, email, name
      Verification: `curl -s /api/user/1 | jq -e '.id and .email and .name'`
      SMART: S✓ M✓ A✓ R✓ T✓
```

---

## Integration with Other Commands

### From /speckit.plan
Tasks receive:
- Phase structure for grouping
- Requirements for traceability
- ADRs for context and SMART criteria
- Task generation notes

### To /speckit.implement
Tasks provide:
- Execution order (phase → priority → dependencies)
- Context requirements
- SMART-validated acceptance criteria for verification

### With /speckit.analyze
Tasks are analyzed for:
- Coverage completeness
- Dependency validity
- Constitution compliance
- SMART compliance percentage
