Revert to a previous git checkpoint with intelligent failure analysis and artifact update recommendations.

## Usage
- `/speckit.revert` - Revert to most recent checkpoint
- `/speckit.revert speckit-checkpoint-20240115_143500` - Revert to specific checkpoint
- `/speckit.revert --list` - List available checkpoints
- `/speckit.revert --dry-run` - Show what would be reverted without executing

## When to Use

Use `/speckit.revert` when:
- Implementation introduced bugs or broke tests
- Acceptance criteria cannot be met with current approach
- Need to try a different implementation strategy
- Want to undo all changes from a failed implementation session

---

## Workflow: Revert → Analyze → Recommend

```
═══════════════════════════════════════════
Phase 1: Pre-Revert Validation
═══════════════════════════════════════════
    ↓
Check working tree state
    ↓
Identify checkpoint to revert to
    ↓
Show what will be reverted
    ↓
Get user confirmation
    ↓
═══════════════════════════════════════════
Phase 2: Execute Revert
═══════════════════════════════════════════
    ↓
git reset --hard [checkpoint]
    ↓
Restore stashed changes if applicable
    ↓
═══════════════════════════════════════════
Phase 3: Failure Analysis
═══════════════════════════════════════════
    ↓
Analyze what was attempted
    ↓
Identify failure patterns
    ↓
Generate recommendations
    ↓
Update artifacts (plans/tasks) if needed
```

---

## Phase 1: Pre-Revert Validation

### Step 1: List Available Checkpoints

```bash
# List all speckit checkpoints
git tag -l "speckit-checkpoint-*" --sort=-creatordate

# Show checkpoint details
git log --oneline speckit-checkpoint-* -1
```

### Checkpoint List Output

```markdown
## Available Checkpoints

| Checkpoint | Created | Tasks | Status |
|------------|---------|-------|--------|
| speckit-checkpoint-20240115_143500 | 2024-01-15 14:35 | TASK-007..010 | Most Recent |
| speckit-checkpoint-20240114_091000 | 2024-01-14 09:10 | TASK-001..006 | Phase 1 |
| speckit-checkpoint-20240113_160000 | 2024-01-13 16:00 | Initial | Project Init |

**Select checkpoint to revert to, or press Enter for most recent.**
```

### Step 2: Show Revert Preview

```markdown
## Revert Preview

**Target**: speckit-checkpoint-20240115_143500
**Current HEAD**: abc1234

### Files to be Reverted
| File | Change Type | Lines Changed |
|------|-------------|---------------|
| src/auth/middleware.ts | Modified | +45 / -12 |
| src/routes/index.ts | Modified | +23 / -5 |
| tests/auth.test.ts | Added | +120 |

### Tasks Affected
- TASK-007: Implement user auth → Will be reset to PENDING
- TASK-008: Add session handling → Will be reset to PENDING
- TASK-009: Create middleware → Will be reset to PENDING
- TASK-010: Set up routes → Will be reset to PENDING

**Proceed with revert? (y/n)**
```

---

## Phase 2: Execute Revert

### Revert Process

```bash
# 1. Save current state for analysis (before destroying it)
git diff HEAD [checkpoint] > /tmp/speckit-failed-changes.diff
git log --oneline [checkpoint]..HEAD > /tmp/speckit-failed-commits.log

# 2. Check for uncommitted changes
if git status --porcelain | grep -q .; then
    git stash push -m "speckit-pre-revert-stash-$(date +%Y%m%d_%H%M%S)"
fi

# 3. Reset to checkpoint
git reset --hard [checkpoint]

# 4. Clean untracked files (optional, with confirmation)
# git clean -fd

# 5. Verify revert
git status
```

### Revert Execution Output

```markdown
## Revert Executed

| Action | Status |
|--------|--------|
| Pre-revert state saved | ✓ /tmp/speckit-failed-changes.diff |
| Uncommitted changes | ✓ Stashed (speckit-pre-revert-stash-...) |
| Reset to checkpoint | ✓ speckit-checkpoint-20240115_143500 |
| Working tree | ✓ Clean |

**Revert complete. Proceeding to failure analysis...**
```

---

## Phase 3: Failure Analysis

**CRITICAL**: After every revert, perform failure analysis to learn from what went wrong.

### Analysis Process

1. **Examine the diff** - What changes were attempted?
2. **Check test failures** - What tests failed and why?
3. **Review error logs** - What errors occurred during implementation?
4. **Identify patterns** - What category of failure was this?

### Failure Categories

| Category | Indicators | Typical Cause |
|----------|------------|---------------|
| **SPEC_GAP** | Implementation diverged from spec | Missing/unclear requirements |
| **APPROACH_WRONG** | Fundamental approach doesn't work | Need different architecture |
| **DEPENDENCY_ISSUE** | External dependency problems | Version mismatch, missing package |
| **TEST_MISMATCH** | Tests don't match implementation | Outdated tests or wrong assumptions |
| **SCOPE_CREEP** | Too many changes at once | Task too large, needs decomposition |
| **KNOWLEDGE_GAP** | Unfamiliar technology/pattern | Need research or different approach |

### Analysis Output Template

```markdown
## Failure Analysis Report

### What Was Attempted
**Tasks**: TASK-007..TASK-010
**Goal**: Implement user authentication with session handling
**Approach**: JWT-based auth with Redis session store

### What Went Wrong

#### Primary Failure
**Category**: APPROACH_WRONG
**Evidence**:
- Redis connection timeouts in tests
- Session middleware conflicts with existing auth
- 3 of 4 tasks completed but integration fails

#### Root Cause Analysis
1. **Immediate cause**: Redis not configured in test environment
2. **Underlying cause**: Architecture assumes Redis, but project uses in-memory sessions
3. **Specification gap**: Auth spec doesn't specify session storage mechanism

### Files Changed (Now Reverted)
| File | Purpose | Issue |
|------|---------|-------|
| src/auth/middleware.ts | JWT validation | Works in isolation |
| src/session/redis.ts | Redis session store | Wrong storage choice |
| src/routes/protected.ts | Protected routes | Depends on Redis |

### Test Results (Pre-Revert)
| Test Suite | Pass | Fail | Skip |
|------------|------|------|------|
| auth.test.ts | 8 | 4 | 0 |
| session.test.ts | 0 | 12 | 0 |
| routes.test.ts | 15 | 3 | 2 |

### Impact Assessment
- **Severity**: HIGH - Core functionality blocked
- **Scope**: Phase 2 cannot proceed with current approach
- **Dependencies**: TASK-011..014 depend on auth working
```

---

## Phase 4: Recommendation Generation

Based on failure analysis, generate specific recommendations:

### Recommendation Output

```markdown
## Recommendations

### Immediate Actions

1. **Update Specification** (if SPEC_GAP identified)
   ```
   /speckit.clarify
   ```
   Questions to resolve:
   - What session storage mechanism should be used?
   - Is Redis a hard requirement or can we use alternatives?

2. **Update Plan** (if APPROACH_WRONG identified)

   Suggested plan modifications:
   ```markdown
   ## Phase 2: Core Features (REVISED)

   ### Original Approach (Failed)
   - JWT auth with Redis sessions

   ### Revised Approach
   - JWT auth with in-memory sessions (development)
   - Abstract session interface for production flexibility

   ### New Tasks
   - TASK-007a: Create session interface abstraction
   - TASK-007b: Implement in-memory session adapter
   - TASK-007c: Implement JWT validation (extracted from TASK-007)
   ```

3. **Update Tasks** (always after revert)

   Reset affected tasks:
   ```markdown
   ### TASK-007: Implement user auth
   **Status**: PENDING (reverted from FAILED)
   **Previous Attempt**: 2024-01-15 - APPROACH_WRONG
   **Notes**: Need session abstraction first. See failure analysis.
   ```

### Process Improvements

| Finding | Recommendation |
|---------|----------------|
| Redis assumption not validated | Add tech validation step to /speckit.plan |
| Task scope too large | Decompose auth into smaller tasks |
| Missing test fixtures | Add test environment setup to Phase 1 |

### Suggested Next Steps

1. **If spec needs clarification**:
   ```
   /speckit.clarify
   ```

2. **If plan needs revision**:
   ```
   /speckit.plan --revise "Phase 2"
   ```

3. **If tasks need regeneration**:
   ```
   /speckit.tasks --regenerate "Phase 2"
   ```

4. **When ready to retry**:
   ```
   /speckit.implement TASK-007a
   ```
```

---

## Post-Revert Updates

### Update project-status.md

```markdown
## Recent Activity
| Date | Tasks | Action | Checkpoint |
|------|-------|--------|------------|
| 2024-01-15 | TASK-007..010 | ⚠ REVERTED | speckit-checkpoint-20240115_143500 |
| 2024-01-15 | TASK-007..010 | Attempted Phase 2a | (failed) |
| 2024-01-14 | TASK-001..006 | Completed Phase 1 | speckit-checkpoint-20240114_091000 |

## Blockers & Issues
| ID | Task | Issue | Impact | Resolution | Status |
|----|------|-------|--------|------------|--------|
| BLK-001 | TASK-007 | Session storage approach | HIGH | Clarify spec, revise plan | OPEN |
```

### Update tasks.md

For each reverted task:

```markdown
### TASK-007: Implement user auth

**Status**: PENDING
**Previous Attempts**: 1
**Last Attempt**: 2024-01-15T14:35:00Z - REVERTED
**Failure Category**: APPROACH_WRONG
**Notes**: Session storage mechanism unclear. Blocked until spec clarified.

**Pre-Retry Checklist**:
- [ ] Clarify session storage requirements (/speckit.clarify)
- [ ] Update plan with revised approach
- [ ] Consider task decomposition
```

---

## Summary Output

```markdown
## Revert Complete

### Revert Summary
| Property | Value |
|----------|-------|
| Checkpoint | speckit-checkpoint-20240115_143500 |
| Tasks Reverted | TASK-007..TASK-010 |
| Files Restored | 4 |
| Failure Category | APPROACH_WRONG |

### Analysis Summary
- **Root Cause**: Architecture mismatch (Redis vs in-memory sessions)
- **Spec Gap**: Session storage mechanism not specified
- **Recommendation**: Clarify spec, then revise plan before retry

### Artifacts Updated
- ✓ project-status.md - Activity logged, blocker added
- ✓ *-tasks.md - Task statuses reset, notes added
- ✓ Failure analysis saved to .claude/resources/failure-analysis-20240115.md

### Next Steps
1. Run `/speckit.clarify` to resolve session storage question
2. Run `/speckit.plan --revise "Phase 2"` after clarification
3. Run `/speckit.tasks --regenerate "Phase 2"` if plan changes
4. Retry with `/speckit.implement TASK-007`

**The codebase has been restored to a known good state.**
```

---

## Flags and Options

| Flag | Effect |
|------|--------|
| `--list` | Show available checkpoints without reverting |
| `--dry-run` | Show what would be reverted without executing |
| `--no-analysis` | Skip failure analysis (not recommended) |
| `--keep-stash` | Don't restore pre-revert stash after revert |
| `--force` | Skip confirmation prompts |

---

## Error Handling

| Error | Resolution |
|-------|------------|
| No checkpoints found | Cannot revert - no checkpoints exist |
| Checkpoint not found | List available checkpoints with `--list` |
| Uncommitted changes | Will be stashed automatically |
| Merge conflicts | Manual resolution required |
| Protected branch | Cannot revert on protected branches |
