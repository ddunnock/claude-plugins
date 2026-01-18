# Implement Workflow Reference

Detailed workflow for the `/speckit.implement` command.

## Purpose

Execute tasks from *-tasks.md with batch+gates execution model. Provides structured implementation with checkpoints for review.

## Key Characteristics

- **Pre-hooks**: Always loads status and validates before execution
- **Context-aware**: Loads constitution sections and memory files per task
- **Batch execution**: Runs related tasks together
- **Gates**: Pauses at phase/group boundaries for review
- **Status tracking**: Updates task statuses in real-time
- **Post-hooks**: Updates status files and outputs summary
- **Resumable**: Can stop and continue later

---

## MANDATORY: Pre-Implementation Hooks

**CRITICAL**: These hooks MUST execute BEFORE any task work begins.

### Pre-Hook 1: Load Project Status

**ALWAYS** read `.claude/memory/project-status.md` first:

```
Read: .claude/memory/project-status.md

Extract and understand:
- Current Phase: [phase name]
- Progress: [X]/[Y] tasks ([Z]%)
- Last Activity: [date] - [what was done]
- Blockers: [any outstanding issues]
- Recommended Next Actions: [from file]
```

### Pre-Hook 2: Validate Argument / Show Status

**IF no argument provided OR invalid argument:**

```markdown
## Current Project Status

| Metric | Value |
|--------|-------|
| Project | [PROJECT_NAME] |
| Current Phase | Phase [N]: [Name] |
| Progress | [X]/[Y] tasks ([Z]%) |
| Last Updated | [DATE] |

### Phase Progress
| Phase | Status | Completed/Total |
|-------|--------|-----------------|
| Phase 1 | ✓ COMPLETE | 6/6 |
| Phase 2 | IN PROGRESS | 3/8 |
| Phase 3 | PENDING | 0/5 |

### Recommended Next Action

Based on current state, you should run:
```
/speckit.implement "Phase 2"
```

Or to continue from where you left off:
```
/speckit.implement --continue
```

### Available Selectors

| Selector | What It Does |
|----------|--------------|
| `TASK-XXX` | Execute single task |
| `TASK-XXX..TASK-YYY` | Execute range |
| `"Phase N"` | Execute all in phase |
| `@group` | Execute all with group tag |
| `--continue` | Resume from last position |
| `--all` | Execute all pending tasks |

**Please specify which tasks to implement.**
```

**STOP HERE** - Do not proceed without valid task selection.

### Pre-Hook 3: Validate Task Selection

For valid arguments, verify:

1. **Tasks exist** - Check *-tasks.md contains specified tasks
2. **Tasks are actionable** - Filter out COMPLETED tasks
3. **Dependencies met** - Check for BLOCKED status

**IF no actionable tasks found:**

```markdown
## No Actionable Tasks

The specified selection has no pending tasks:

- `TASK-001`: COMPLETED (2024-01-15)
- `TASK-002`: COMPLETED (2024-01-15)

### Suggestions

1. Move to next phase: `/speckit.implement "Phase [N+1]"`
2. Re-run a task: `/speckit.implement TASK-XXX --force`
3. Check status: `cat .claude/memory/project-status.md`
```

### Pre-Hook 4: Present Execution Plan

Before executing, present the plan for confirmation:

```markdown
## Execution Plan

**Selection**: [what user specified]
**Tasks to execute**: [count]

| Task | Title | Status | Dependencies |
|------|-------|--------|--------------|
| TASK-004 | [Title] | PENDING | None |
| TASK-005 | [Title] | PENDING | TASK-004 |
| TASK-006 | [Title] | FAILED | None (retry) |

**Context to load**:
- Constitution: §3.1, §4.2, §5.1
- Memory: typescript.md, testing.md

**Proceed with execution?**
```

---

## Task Selection

### Selection Syntax

| Selector | Meaning | Example |
|----------|---------|---------|
| `TASK-XXX` | Single task | `TASK-001` |
| `TASK-XXX..TASK-YYY` | Range | `TASK-001..TASK-005` |
| `"Phase N"` | All in phase | `"Phase 1"` |
| `@group` | All with group tag | `@foundation` |
| `--all` | All pending tasks | `--all` |
| `--continue` | Resume from last | `--continue` |

### Selection Examples

```bash
# Single task
/speckit.implement TASK-001

# Range of tasks
/speckit.implement TASK-001..TASK-010

# Entire phase
/speckit.implement "Phase 1"

# All foundation tasks
/speckit.implement @foundation

# All pending tasks
/speckit.implement --all

# Continue from where we left off
/speckit.implement --continue
```

---

## Workflow Steps

### Step 1: Parse Selection

```
Selection: "Phase 1"

Tasks selected:
- TASK-001: Initialize project structure [PENDING]
- TASK-002: Set up configuration [PENDING]
- TASK-003: Create base components [PENDING]
- TASK-004: Implement auth flow [PENDING]

Total: 4 tasks
Status: All PENDING

Proceed with Phase 1 execution?
```

### Step 2: Build Execution Order

Respect dependencies:
```
Dependency analysis:
- TASK-001: No dependencies (start)
- TASK-002: Depends on TASK-001
- TASK-003: Depends on TASK-002
- TASK-004: Depends on TASK-001, TASK-002

Execution order:
1. TASK-001
2. TASK-002
3. TASK-003, TASK-004 (can parallelize)
```

### Step 3: Load Context Per Task

For each task, load referenced materials:

```markdown
## Execution Context for TASK-001

### Task Details
**Title**: Initialize project structure
**Priority**: P1
**Status**: PENDING → IN_PROGRESS

### Constitution Requirements

#### §3.1 Project Structure
> All projects must follow the standard directory layout:
> - src/ for source code
> - tests/ for test files
> - docs/ for documentation
> Projects must include standard config files...

#### §3.2 Configuration
> Configuration must use environment variables for secrets.
> Config files must have schema validation...

### Memory File Guidelines

#### From typescript.md - "Project Setup"
> Use pnpm as package manager.
> Enable strict TypeScript mode.
> Configure path aliases in tsconfig.json...

#### From git-cicd.md - "Initial Setup"
> Initialize with .gitignore from template.
> Set up pre-commit hooks with husky.
> Configure GitHub Actions for CI...

### Acceptance Criteria
- [ ] Project directories created per §3.1
- [ ] Configuration files in place per §3.2
- [ ] TypeScript configured per typescript.md
- [ ] Git initialized per git-cicd.md
```

### Step 4: Execute Task

Present context and execute:

```
Executing TASK-001: Initialize project structure

Context loaded:
- Constitution: §3.1, §3.2
- Memory: typescript.md, git-cicd.md

Acceptance criteria:
- [ ] Project directories created per §3.1
- [ ] Configuration files in place per §3.2
- [ ] TypeScript configured per typescript.md
- [ ] Git initialized per git-cicd.md

Executing...
```

### Step 5: Verify Completion

Check acceptance criteria:

```
TASK-001 Execution Complete

Acceptance criteria check:
✓ Project directories created per §3.1
✓ Configuration files in place per §3.2
✓ TypeScript configured per typescript.md
✓ Git initialized per git-cicd.md

All criteria met. Marking as COMPLETED.

Files modified:
- Created: src/, tests/, docs/
- Created: package.json, tsconfig.json
- Created: .gitignore, .husky/

Continue to TASK-002?
```

### Step 6: Gate at Phase Boundary

After completing phase tasks:

```
═══════════════════════════════════════════
GATE: Phase 1 Complete
═══════════════════════════════════════════

Tasks completed: 4
Tasks failed: 0
Tasks skipped: 0

Summary:
- TASK-001: Initialize project structure ✓
- TASK-002: Set up configuration ✓
- TASK-003: Create base components ✓
- TASK-004: Implement auth flow ✓

Files modified: 23
Lines added: 1,247
Lines removed: 0

Options:
1. Continue to Phase 2 (5 tasks)
2. Review completed work in detail
3. Re-run specific tasks
4. Stop execution (can resume later)

Your choice:
```

---

## Status Transitions

```
PENDING → IN_PROGRESS → COMPLETED
                     ↘ FAILED → [fix] → IN_PROGRESS
                     ↘ BLOCKED
                     ↘ SKIPPED
```

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Not started | Ready to execute |
| IN_PROGRESS | Currently executing | Wait for completion |
| COMPLETED | Done and verified | Move to next |
| FAILED | Execution failed | Fix and retry |
| BLOCKED | Waiting on dependency | Resolve blocker |
| SKIPPED | Intentionally skipped | Document reason |

---

## Context Loading

### Constitution Section Extraction

For each referenced section:
1. Find section by ID (§X.Y)
2. Extract section content
3. Include relevant examples
4. Highlight key requirements

```python
def extract_constitution_section(constitution_path, section_id):
    """
    Extract section content from constitution.
    Returns header, content, examples, and key requirements.
    """
    # Parse markdown
    # Find section by heading pattern
    # Extract until next section
    # Identify code blocks as examples
    # Extract "must", "shall", "required" statements
```

### Memory File Section Extraction

For each memory file reference:
1. Find relevant section by title or keyword
2. Extract guidance content
3. Include code examples
4. Highlight patterns and anti-patterns

---

## Failure Handling

### Task Failure

```
TASK-003 Failed

Error: TypeScript compilation errors
Details: 3 type errors in src/components/Button.tsx

Options:
1. View error details
2. Retry task
3. Mark as BLOCKED (add blocker note)
4. Skip task (document reason)
5. Stop execution
```

### Dependency Failure

```
TASK-005 Blocked

Reason: Depends on TASK-003 which FAILED

Options:
1. Fix TASK-003 first
2. Skip TASK-005 (document reason)
3. Override dependency check
4. Stop execution
```

---

## Resumption

After stopping:

```bash
/speckit.implement --continue
```

```
Resuming execution...

Last session: 2024-01-15T14:30:00Z
Progress: Phase 1 complete, Phase 2 in progress

Status:
- COMPLETED: 4 tasks
- IN_PROGRESS: 0 tasks
- PENDING: 11 tasks

Continue from TASK-005?
```

---

## Execution Summary

After completing all selected tasks:

```
═══════════════════════════════════════════
Execution Complete
═══════════════════════════════════════════

Duration: 45 minutes
Tasks executed: 15

By status:
- COMPLETED: 14
- FAILED: 1 (TASK-012)
- SKIPPED: 0

By phase:
- Phase 1: 4/4 ✓
- Phase 2: 6/6 ✓
- Phase 3: 4/5 (1 failed)

Files modified: 67
Lines added: 3,456
Lines removed: 234

Failed tasks require attention:
- TASK-012: API integration test
  Error: External API timeout

Recommendations:
1. Review TASK-012 failure
2. Run /speckit.analyze to check consistency
3. Commit changes with /commit
```

---

## Integration Points

### From /speckit.tasks

Tasks file provides:
- Task definitions
- Constitution references
- Memory file references
- Acceptance criteria
- Dependencies

### To Task File Updates

Status updates written back:
```markdown
### TASK-001: Initialize project structure
**Status**: COMPLETED
**Completed**: 2024-01-15T14:35:00Z
```

### With /speckit.analyze

Post-execution analysis:
```
Execution complete. Run /speckit.analyze to verify consistency?
```

---

## Idempotency

- **Skip COMPLETED**: Already-done tasks skipped
- **Resume IN_PROGRESS**: Interrupted tasks restart
- **Preserve history**: Completion timestamps preserved
- **Re-runnable FAILED**: Failed tasks can retry

---

## MANDATORY: Post-Implementation Hooks

**CRITICAL**: The following hooks MUST execute after ANY `/speckit.implement` run. These are NOT optional and the command is not complete without them.

### Hook Workflow Diagram

```
Execution Complete
        │
        ▼
┌───────────────────────────────────────┐
│ HOOK 1: Update tasks.md               │
│                                       │
│ For each completed task:              │
│ 1. Set Status: COMPLETED              │
│ 2. Add Completed timestamp            │
│ 3. Verify EACH acceptance criterion   │
│ 4. Mark [x] or [ ] with evidence      │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ HOOK 2: Update project-status.md      │
│                                       │
│ 1. Update progress metrics            │
│ 2. Update phase status                │
│ 3. Log recent activity                │
│ 4. List next actions                  │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ HOOK 3: Output Completion Summary     │
│                                       │
│ 1. Tasks completed table              │
│ 2. Acceptance criteria summary        │
│ 3. Failed criteria (if any)           │
│ 4. Project status confirmation        │
│ 5. Recommended next steps             │
└───────────────────────────────────────┘
        │
        ▼
    COMMAND COMPLETE
```

---

### Hook 1: Update tasks.md - Detailed Process

#### Step 1.1: Update Task Status

```markdown
### TASK-001: [Title]

**Status**: COMPLETED          ← Change from PENDING/IN_PROGRESS
**Completed**: 2024-01-15T14:35:00Z    ← Add timestamp
**Verified By**: Claude        ← Add verification attribution
```

#### Step 1.2: Verify Each Acceptance Criterion

For EACH criterion in the task's acceptance criteria:

| Criterion Type | Verification Method | Example |
|----------------|---------------------|---------|
| File exists | `ls` or `Glob` tool | `ls src/components/Button.tsx` |
| Tests pass | Run test command | `npm test -- Button.test.ts` |
| Code compiles | Run build | `npm run build` |
| Lint passes | Run linter | `npm run lint` |
| Type checks | Run type checker | `npm run typecheck` |
| Endpoint works | Make request | `curl localhost:3000/api/health` |
| Config valid | Validate schema | `npx ajv validate -s schema.json` |

#### Step 1.3: Document Evidence

Transform acceptance criteria from:
```markdown
**Acceptance Criteria**:
- [ ] Button component exists in src/components/
- [ ] Component has proper TypeScript types
- [ ] Unit tests pass with >80% coverage
```

To:
```markdown
**Acceptance Criteria**:
- [x] Button component exists in src/components/
      Verified: `ls src/components/Button.tsx` → exists
- [x] Component has proper TypeScript types
      Verified: `npx pyright src/components/Button.tsx` → 0 errors
- [x] Unit tests pass with >80% coverage
      Verified: `npm test -- --coverage` → 94% coverage
```

Or if failed:
```markdown
- [ ] Unit tests pass with >80% coverage
      FAILED: `npm test -- --coverage` → 72% coverage (below 80% threshold)
```

---

### Hook 2: Update project-status.md - Detailed Process

#### File Location

`.claude/memory/project-status.md`

If this file does not exist, CREATE IT using the template below.

#### Template Structure

```markdown
# Project Status

## Current State

| Metric | Value |
|--------|-------|
| Project | [PROJECT_NAME] |
| Current Phase | Phase [N]: [Phase Name] |
| Total Tasks | [TOTAL] |
| Completed | [COMPLETED] |
| In Progress | [IN_PROGRESS] |
| Blocked | [BLOCKED] |
| Pending | [PENDING] |
| Progress | [PERCENTAGE]% |
| Last Updated | [ISO_TIMESTAMP] |

## Phase Progress

| Phase | Status | Tasks | Completed | Remaining |
|-------|--------|-------|-----------|-----------|
| Phase 1: [Name] | ✓ COMPLETE | [N] | [N] | 0 |
| Phase 2: [Name] | IN PROGRESS | [N] | [M] | [N-M] |
| Phase 3: [Name] | PENDING | [N] | 0 | [N] |

## Recent Activity

| Date | Session | Tasks | Status |
|------|---------|-------|--------|
| [DATE] | [SESSION_ID] | TASK-XXX..TASK-YYY | Completed [N] tasks |
| [DATE] | [SESSION_ID] | TASK-XXX | Partial - 2/3 criteria met |

## Blockers & Issues

| Task | Issue | Impact | Resolution |
|------|-------|--------|------------|
| TASK-XXX | [Description] | Blocks Phase 2 | [Action needed] |

## Next Actions

- [ ] [Next immediate action]
- [ ] [Following action]
- [ ] [Future action]

---

*Generated by SpecKit Generator*
*Last Updated: [ISO_TIMESTAMP]*
```

#### Update Process

1. **Read current project-status.md** (or create from template)
2. **Calculate metrics**:
   - Count tasks by status from *-tasks.md
   - Calculate completion percentage
   - Identify current phase
3. **Update phase table**:
   - Mark phases complete when all tasks done
   - Set IN PROGRESS for current phase
4. **Add activity log entry**:
   - Record tasks completed this session
   - Note any failures or partial completions
5. **Update next actions**:
   - Clear completed actions
   - Add new relevant actions

---

### Hook 3: Generate Completion Summary - Template

MUST output this summary to the user after every `/speckit.implement` run:

```markdown
## Implementation Complete

### Session Summary
- **Started**: [START_TIME]
- **Duration**: [DURATION]
- **Tasks Attempted**: [N]
- **Tasks Completed**: [M]

### Tasks Completed This Session

| Task ID | Title | Status | Criteria |
|---------|-------|--------|----------|
| TASK-001 | [Title] | ✓ COMPLETED | 3/3 ✓ |
| TASK-002 | [Title] | ✓ COMPLETED | 4/4 ✓ |
| TASK-003 | [Title] | ⚠ PARTIAL | 2/3 |

### Acceptance Criteria Verification

**Total Criteria Checked**: [N]
**Passed**: [M] ([PERCENTAGE]%)
**Failed**: [F]

[If any failed:]

#### ⚠ Failed Criteria Requiring Attention

| Task | Criterion | Failure Reason |
|------|-----------|----------------|
| TASK-003 | Unit tests pass | Coverage at 72%, required 80% |

### Artifacts Updated

✓ `speckit/*-tasks.md` - Task statuses and criteria
✓ `.claude/memory/project-status.md` - Progress metrics

### Project Progress

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Completed Tasks | [N] | [M] | +[DIFF] |
| Progress | [X]% | [Y]% | +[DIFF]% |
| Current Phase | Phase [N] | Phase [M] | [same/advanced] |

### Recommended Next Steps

[Based on current state, provide specific guidance:]

1. **[If all criteria passed and phase not complete]**:
   Continue with remaining phase tasks:
   ```
   /speckit.implement "Phase [N]"
   ```

2. **[If any criteria failed]**:
   Address failed criteria:
   - [Specific action for each failure]
   Then re-run:
   ```
   /speckit.implement TASK-XXX
   ```

3. **[If phase complete]**:
   Proceed to next phase:
   ```
   /speckit.implement "Phase [N+1]"
   ```

4. **[If all phases complete]**:
   Run final consistency check:
   ```
   /speckit.analyze
   ```

5. **[Always include]**:
   Review updated status:
   ```
   cat .claude/memory/project-status.md
   ```
```

---

### Hook Enforcement

The `/speckit.implement` command is **NOT COMPLETE** until this checklist is satisfied:

```
Post-Implementation Checklist:

[HOOK 1: tasks.md Updates]
□ All executed task statuses updated to COMPLETED/FAILED
□ Completion timestamps added
□ Each acceptance criterion individually verified
□ Evidence documented for each criterion
□ Checkboxes accurately reflect verification results

[HOOK 2: project-status.md Updates]
□ File exists at .claude/memory/project-status.md
□ Progress metrics are current and accurate
□ Phase progress table reflects reality
□ Recent activity entry added for this session
□ Next actions list is current

[HOOK 3: User Summary Output]
□ Task completion table displayed
□ Acceptance criteria summary shown
□ Failed criteria highlighted (if any)
□ Artifact update confirmation shown
□ Next steps clearly communicated
□ Specific commands provided for next actions
```

---

### Error Handling in Hooks

If a hook cannot complete:

```markdown
⚠ Post-Implementation Hook Warning

Hook 2 (project-status.md update) encountered an issue:
- File not found and could not be created
- Reason: [error details]

Manual action required:
1. Create .claude/memory/project-status.md using template
2. Re-run: /speckit.implement --continue

Hook 1 and Hook 3 completed successfully.
```

---

## Continuation Format

After command completion, always present the next logical step using this standardized format:

```markdown
## ▶ Next Up
**{command}: {name}** — {one-line description}
`/{command}`
<sub>`/clear` first → fresh context window</sub>
```

### Next Step Logic for /implement

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| All criteria passed, more tasks | `/implement "Phase [N]"` | Continue remaining phase tasks |
| Any criteria failed | `/implement TASK-XXX` | Retry failed task |
| Phase complete | `/implement "Phase [N+1]"` | Start next phase |
| All phases complete | `/analyze` | Run final consistency check |
| Blocked by dependency | `/implement TASK-XXX` | Resolve blocking task first |

### Example Output

```markdown
## ▶ Next Up
**analyze: Consistency Check** — Verify implementation meets spec requirements
`/analyze`
<sub>`/clear` first → fresh context window</sub>
```
