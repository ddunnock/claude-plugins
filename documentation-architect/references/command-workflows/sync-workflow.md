# Sync Workflow

Detailed workflow for `/docs.sync` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Workflow Steps](#workflow-steps)
- [Code Walkthrough](#code-walkthrough)
- [Discrepancy Types](#discrepancy-types)
- [Update Options](#update-options)
- [Outputs](#outputs)
- [Idempotency](#idempotency)
- [speckit Integration](#speckit-integration)

---

## Purpose

Walk the codebase to sync documentation with implementation reality:
1. Analyze current implementation (code walkthrough)
2. Extract actual APIs, configs, behavior
3. Compare against existing documentation
4. Generate discrepancy report
5. Propose documentation updates
6. Create/update memory files with code state

**Key insight**: Documentation often drifts from reality during implementation. This command bridges that gap by treating code as the source of truth.

---

## Trigger Conditions

**Explicit**:
- User runs `/docs.sync`
- User runs `/docs.sync --walkthrough` (full exploration)
- User runs `/docs.sync --component auth` (specific component)

**Auto-suggested**:
- After `/speckit.implement` completes
- When code changes detected since last docs update
- When `/docs.analyze` finds stale documentation

---

## Workflow Steps

### Step 1: Detect Scope

Determine what to analyze:

```
Detecting sync scope...

Options detected:
├─ Full codebase: 45 files, 12,000 LOC
├─ Changed since last sync: 8 files
└─ Specific component: [none specified]

Mode: [incremental / full / component]
```

If `--walkthrough`:
```
Full walkthrough mode enabled.
Will analyze entire codebase and create comprehensive snapshot.
This may take a few minutes for large projects.

Proceed? [Y/n]
```

### Step 2: Code Walkthrough

Analyze implementation using `sync_codebase.py`:

```
Walking codebase...

Extracting:
├─ Python files: 15 found
│   ├─ Classes: 23
│   ├─ Functions: 87 (52 public)
│   └─ Docstrings: 34 present
├─ TypeScript files: 20 found
│   ├─ Exports: 45
│   └─ Components: 12
├─ Config files: 5 found
└─ Entry points: 3 found

Snapshot complete.
```

### Step 3: Extract Reality

Build understanding of actual implementation:

```markdown
## Code Reality Snapshot

### Public APIs

| Module | Function/Class | Signature | Has Docstring |
|--------|---------------|-----------|---------------|
| auth.py | login | (email: str, password: str) -> User | Yes |
| auth.py | logout | () -> None | No |
| users.py | UserService | class | Yes |
| users.py | create_user | (data: UserCreate) -> User | No |

### Configuration Options

| File | Key | Type | Default | Documented |
|------|-----|------|---------|------------|
| config.yaml | api.timeout | int | 30 | Yes |
| config.yaml | auth.secret | str | None | No |
| .env.example | DATABASE_URL | str | - | Yes |

### Entry Points

| File | Type | Description |
|------|------|-------------|
| main.py | CLI | Main application entry |
| api/index.py | HTTP | REST API server |
| worker.py | Background | Task worker |
```

### Step 4: Compare to Documentation

Load existing docs and compare:

```
Comparing code to documentation...

Checking:
├─ docs/user/guides/authentication.md
├─ docs/developer/reference/api/users.md
├─ docs/user/reference/configuration.md
└─ README.md

Findings: 7 discrepancies detected
```

### Step 5: Generate Sync Report

Create detailed discrepancy report:

```markdown
## Sync Report

**Generated**: [timestamp]
**Scope**: Full codebase
**Discrepancies**: 7

### HIGH Severity (3)

#### SYNC-001: Missing API Documentation
**Code**: `auth.py:logout()` - Public function
**Docs**: Not documented
**Suggestion**: Add to docs/developer/reference/api/auth.md

#### SYNC-002: Incorrect Return Type
**Code**: `POST /api/users` returns `200 OK`
**Docs**: docs/developer/reference/api/users.md says `201 Created`
**Suggestion**: Update docs to match implementation

#### SYNC-003: Undocumented Config Option
**Code**: `config.yaml:auth.secret` - Required for auth
**Docs**: Not in configuration reference
**Suggestion**: Add to docs/user/reference/configuration.md

### MEDIUM Severity (2)

#### SYNC-004: Missing Docstring
**Code**: `users.py:create_user()` - Public, no docstring
**Docs**: Documented in API reference
**Suggestion**: Add docstring to code

#### SYNC-005: Outdated Example
**Code**: API now requires `api_key` header
**Docs**: Examples don't include header
**Suggestion**: Update code examples

### LOW Severity (2)

#### SYNC-006: Terminology Mismatch
**Code**: Uses "user_id"
**Docs**: Uses "userId" (camelCase)
**Suggestion**: Standardize terminology

#### SYNC-007: Deprecated Function Still Documented
**Code**: `legacy_auth()` marked deprecated
**Docs**: Still prominently featured
**Suggestion**: Add deprecation notice or remove
```

### Step 6: Present Update Options

For each discrepancy:

```
SYNC-002: Incorrect Return Type

Code says: POST /api/users returns 200 OK
Docs say:  POST /api/users returns 201 Created

Affected file: docs/developer/reference/api/users.md (line 45)

Options:
[A] Auto-update docs to match code
[M] Mark for manual review
[S] Skip (acknowledge, don't change)
[C] Code is wrong (note for dev fix)

Choice: _
```

### Step 7: Apply Updates

Execute approved changes:

```
Applying updates...

Auto-updates:
├─ ✓ SYNC-002: Updated return code in users.md
├─ ✓ SYNC-003: Added auth.secret to configuration.md
└─ ✓ SYNC-005: Updated API examples with api_key header

Marked for manual review:
├─ SYNC-001: New auth documentation needed
└─ SYNC-004: Add docstring to create_user

Skipped:
└─ SYNC-006: Terminology (user decision pending)

Flagged as code issues:
└─ SYNC-007: Deprecated function (notify dev team)
```

### Step 8: Update Memory Files

Create/update `docs-codebase-snapshot.md`:

```markdown
# Codebase Snapshot

**Generated**: [timestamp]
**Commit**: abc123 (if git repo)

## Summary

| Metric | Count |
|--------|-------|
| Python files | 15 |
| TypeScript files | 20 |
| Public functions | 52 |
| Public classes | 23 |
| Config options | 12 |

## API Surface

[Detailed API listing]

## Configuration Schema

[All config options with types]

## Entry Points

[Application entry points]
```

Update `docs/_meta/sync-report.md` with findings.

---

## Code Walkthrough

### What Gets Analyzed

| Language | Extraction Method | Elements |
|----------|------------------|----------|
| Python | AST parsing | Classes, functions, docstrings |
| TypeScript/JS | Regex patterns | Exports, functions, JSDoc |
| Config (JSON/YAML) | Parser | Keys, types, defaults |
| Rust | Regex patterns | pub items, docs |

### Extraction Details

**Python** (via `sync_codebase.py`):
```python
# Extracts:
# - Class definitions with docstrings
# - Function signatures with type hints
# - Public vs private (underscore prefix)
# - Module-level docstrings
```

**TypeScript**:
```typescript
// Extracts:
// - export statements
// - function signatures
// - interface/type definitions
// - JSDoc comments
```

**Configuration**:
```yaml
# Extracts:
# - All keys and nested structure
# - Value types (inferred)
# - Default values
# - Comments as descriptions
```

---

## Discrepancy Types

| Type | Description | Severity |
|------|-------------|----------|
| MISSING | Code element not in docs | HIGH |
| INCORRECT | Docs don't match code | HIGH |
| OUTDATED | Docs refer to old behavior | MEDIUM |
| UNDOCUMENTED | Public API lacks docstring | MEDIUM |
| DEPRECATED | Documented but deprecated | LOW |
| TERMINOLOGY | Naming inconsistency | LOW |

### Severity Guidelines

**HIGH**: Blocks user success or causes confusion
- Missing critical API docs
- Wrong instructions
- Missing required config

**MEDIUM**: Degrades experience but workaround exists
- Missing docstrings
- Outdated examples
- Incomplete reference

**LOW**: Nice to fix but not blocking
- Style inconsistencies
- Deprecated content
- Minor terminology

---

## Update Options

### Auto-Update (Safe)

Applied automatically for:
- Simple text corrections
- Adding missing items to lists
- Updating version numbers
- Fixing broken links

### Manual Review (Careful)

Flagged for human decision:
- Substantial content changes
- Architectural descriptions
- User-facing instructions
- Deletion of content

### Skip (Acknowledged)

User explicitly skips:
- Known discrepancy
- Intentional difference
- Pending other changes

### Code Issue (Reverse)

Documentation is correct, code needs fixing:
- Creates issue/task
- Notifies development
- Docs unchanged

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| Sync report | `docs/_meta/sync-report.md` | Discrepancy list |
| Codebase snapshot | `.claude/memory/docs-codebase-snapshot.md` | Code state |
| Updated docs | Various | Applied changes |
| Progress log | `docs/_meta/progress.md` | Action record |

### sync-report.md Structure

```markdown
# Documentation Sync Report

**Last Sync**: [timestamp]
**Scope**: [full/incremental/component]
**Status**: [findings count]

## Summary

| Severity | Count | Resolved |
|----------|-------|----------|
| HIGH | 3 | 2 |
| MEDIUM | 2 | 1 |
| LOW | 2 | 0 |

## Active Findings

[Unresolved discrepancies]

## Resolved Findings

[History of resolved items]

## Skipped Findings

[Acknowledged but not addressed]
```

---

## Idempotency

**Safe behaviors**:
- Always safe to run (read-only analysis)
- Updates are opt-in per finding
- Preserves previous sync history
- Never auto-deletes documentation
- Creates backups before changes

**Multiple runs**:
```
Sync already run today.

Previous findings: 7
├─ Resolved: 4
├─ Pending: 2
└─ Skipped: 1

Options:
1. Incremental - Check for new discrepancies
2. Full rescan - Re-analyze everything
3. Review pending - Address unresolved findings
```

**Finding persistence**:
- Finding IDs are stable (SYNC-001 stays SYNC-001)
- Resolved findings move to history
- New findings get new IDs
- Enables tracking over time

---

## speckit Integration

### After Implementation

When `/speckit.implement` completes:

```
Implementation complete: Authentication Module

Files created/modified:
├─ src/auth/login.py
├─ src/auth/logout.py
├─ src/auth/middleware.py
└─ tests/test_auth.py

Run /docs.sync to update documentation?
- Will analyze new auth code
- Compare against existing docs
- Suggest updates based on implementation
```

### Automatic Detection

```python
def should_suggest_sync(project_path: Path) -> bool:
    """Check if sync should be suggested."""

    # Check for recent speckit implementation
    speckit_log = project_path / ".claude" / "speckit-log.md"
    if speckit_log.exists():
        # Parse for recent implement runs
        ...

    # Check for code changes since last sync
    last_sync = get_last_sync_time(project_path)
    if code_modified_since(project_path, last_sync):
        return True

    return False
```

### Sync Modes

**Post-implementation** (suggested):
```bash
/docs.sync
# Focuses on recently changed files
# Compares to existing documentation
# Quick, targeted sync
```

**Full walkthrough** (manual):
```bash
/docs.sync --walkthrough
# Analyzes entire codebase
# Creates comprehensive snapshot
# Good for initial docs or major refactors
```

**Component-specific**:
```bash
/docs.sync --component authentication
# Only analyzes auth-related code
# Faster for focused work
```
