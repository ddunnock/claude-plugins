# Tasks Workflow Reference

Detailed workflow for the `/speckit.tasks` command.

## Purpose

Generate implementation tasks from plans + constitution + memory files. Tasks define HOW to implement what the plan describes.

## Idempotency

- Preserves existing task statuses
- Adds new tasks for new plan items
- Never removes manually added tasks
- Updates task content while preserving status

---

## Workflow Steps

### Step 1: Load Plan(s)

```
1. Find plan files in .claude/resources/
2. Parse plan structure (phases, requirements, decisions)
3. Identify domains from complex plans

If no plans found:
"No plans found. Run /speckit.plan first?"
```

### Step 2: Load Constitution

Read `.claude/memory/constitution.md`:
- Extract section structure
- Build section index for referencing
- Identify applicable sections per task

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

For each plan phase, generate tasks:

```markdown
# [Domain] Tasks

Generated: [timestamp]
Plan source: plan.md
Constitution version: [hash]

## Phase 1: Foundation

### TASK-001: Initialize project structure
**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @foundation

**Constitution Sections**:
- §3.1 (Project Structure)
- §3.2 (Configuration)

**Memory Files**:
- typescript.md: "Project Setup" section
- git-cicd.md: "Initial Setup" section

**Plan Reference**: PHASE-1, AD-001

**Description**:
Set up the initial project structure following the patterns defined
in constitution.md §3.1. This includes...

**Acceptance Criteria**:
- [ ] Project directories created per §3.1
- [ ] Configuration files in place
- [ ] Initial commit with proper message format

**Dependencies**: None

**Estimated Scope**: [S/M/L]
```

### Step 5: Assign Task Metadata

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

### Step 6: Validate Tasks

Check for:
- All plan phases covered
- No circular dependencies
- All constitution references valid
- Acceptance criteria are testable

```
Task Validation:
✓ 15 tasks generated
✓ All phases covered
✓ No circular dependencies
⚠ TASK-007 references §5.3 which doesn't exist

Issues: 1 error

Options:
1. Fix and continue
2. Generate anyway with warnings
3. Cancel
```

### Step 7: Save and Report

```
Tasks generated: project-tasks.md

Summary:
- Total tasks: 15
- Phase 1: 4 tasks
- Phase 2: 6 tasks
- Phase 3: 5 tasks

Groups:
- @foundation: 4 tasks
- @core: 8 tasks
- @testing: 3 tasks

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
- Last Updated: [timestamp]

## Phase 1: [Phase Name]

### TASK-001: [Title]
[task content]

### TASK-002: [Title]
[task content]

## Phase 2: [Phase Name]
...
```

### Task Content

Each task contains:

| Field | Purpose |
|-------|---------|
| Status | Current state (PENDING, IN_PROGRESS, etc.) |
| Priority | P1/P2/P3 |
| Phase | Which phase this belongs to |
| Group | @tag for batch selection |
| Constitution Sections | Which constitution sections apply |
| Memory Files | Which memory files provide guidance |
| Plan Reference | Traceability to plan |
| Description | What to do |
| Acceptance Criteria | Definition of done |
| Dependencies | What must complete first |
| Estimated Scope | S/M/L complexity indicator |

---

## Update Mode

When tasks already exist:

```
Existing tasks found: project-tasks.md
- Total: 15 tasks
- COMPLETED: 5
- IN_PROGRESS: 1
- PENDING: 9

Options:
1. Add new tasks only (preserve existing)
2. Update task content (preserve statuses)
3. Full regenerate (reset all statuses)
4. View changes
```

Update behavior:
- New plan items → New tasks added
- Removed plan items → Tasks marked obsolete (not deleted)
- Changed plan items → Task content updated, status preserved

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

## Integration with Other Commands

### From /speckit.plan
Tasks receive:
- Phase structure
- Requirements mapping
- Architecture decisions

### To /speckit.implement
Tasks provide:
- Execution order
- Context requirements
- Acceptance criteria

### With /speckit.analyze
Tasks are analyzed for:
- Coverage completeness
- Dependency validity
- Constitution compliance
