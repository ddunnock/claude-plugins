# speckit-generator Integration

How documentation-architect integrates with speckit-generator for seamless development-to-documentation workflows.

## Table of Contents
- [Integration Points](#integration-points)
- [Command Mappings](#command-mappings)
- [Shared Artifacts](#shared-artifacts)
- [Workflow Scenarios](#workflow-scenarios)
- [Memory File Coordination](#memory-file-coordination)

---

## Integration Points

### After speckit Commands

| speckit Command | Suggested docs Action | Integration |
|-----------------|----------------------|-------------|
| `/speckit.init` | `/docs.init` | Share tech detection, create docs foundation |
| `/speckit.plan` | `/docs.plan --from-speckit` | Read plan.md, extract documentation needs |
| `/speckit.tasks` | `/docs.inventory` | Register task artifacts as sources |
| `/speckit.implement` | `/docs.sync` | Walk code, sync docs with reality |

### Trigger Messages

After `/speckit.init`:
```
speckit initialization complete.

Project foundation established with:
- .claude/ structure
- Memory files for [tech stack]

Documentation setup available. Run /docs.init?
- Creates docs/ structure aligned with project type
- Links to existing .claude/memory/
- Detects documentation needs from speckit context
```

After `/speckit.implement`:
```
Implementation complete for [component].

Documentation may need updating based on implementation.

Run /docs.sync?
- Walks implemented code to extract reality
- Compares against existing docs
- Suggests updates based on actual behavior
```

---

## Command Mappings

### `/docs.init` ← `/speckit.init`

**What docs.init reads from speckit**:
- Tech detection results (primary language, frameworks)
- Project type (library, CLI, service)
- Memory file selections

**How it's used**:
```
speckit detected: TypeScript + Next.js + Tailwind

docs.init will create:
├─ docs/user/guides/ (for UI patterns)
├─ docs/developer/reference/api/ (for component APIs)
└─ Memory: docs-constitution.md with React/TS context
```

### `/docs.plan --from-speckit` ← `/speckit.plan`

**What docs.plan reads**:
- `.claude/resources/plan.md` - Implementation plan
- Architecture decisions
- Feature breakdown
- Task structure

**Mapping logic**:
```
speckit plan item → docs WBS item

Implementation Tasks:
- Implement auth module    → docs/user/guides/authentication.md
- Create REST endpoints    → docs/developer/reference/api/
- Add config system        → docs/user/reference/configuration.md
```

### `/docs.inventory` ← `/speckit.tasks`

**What docs.inventory finds**:
- Task completion artifacts
- Implementation notes
- API definitions discovered during implementation

**Source registration**:
```markdown
| ID | Source | Type | Origin |
|----|--------|------|--------|
| SRC-010 | task-001-auth.md | SPEC | speckit.tasks |
| SRC-011 | api-endpoints.md | CODE | speckit.implement |
```

### `/docs.sync` ← `/speckit.implement`

**The key integration**: After implementation completes, code reality may differ from specs.

**What docs.sync does**:
1. Walks actual implemented code
2. Extracts real APIs, configs, behavior
3. Compares against documentation
4. Identifies discrepancies
5. Proposes updates

**Example discrepancy**:
```markdown
## Sync Finding: API-001

**Spec said**: POST /api/users returns 201
**Code does**: POST /api/users returns 200 with body

**Affected docs**:
- docs/developer/reference/api/users.md (line 45)

**Suggested update**:
```diff
- Returns: 201 Created
+ Returns: 200 OK with user object
```
```

---

## Shared Artifacts

### File Locations

Both skills share the `.claude/` directory structure:

```
.claude/
├── memory/
│   ├── constitution.md        # speckit: dev principles
│   ├── docs-constitution.md   # docs: doc principles
│   ├── typescript.md          # speckit: TS standards
│   ├── docs-sources.md        # docs: source tracking
│   ├── docs-terminology.md    # docs: term definitions
│   └── project-context.md     # shared: project description
│
└── resources/
    ├── requirements.md        # User-provided specs
    ├── plan.md               # speckit: implementation plan
    └── architecture.md       # speckit: arch decisions
```

### Reading speckit Artifacts

**plan.md structure** (read by docs.plan):
```markdown
# Implementation Plan

## Overview
[Project description]

## Architecture Decisions
[Key decisions - source for Explanation docs]

## Implementation Tasks
[Features to implement - source for How-To docs]

## API Design
[Endpoints - source for Reference docs]
```

**project-context.md** (shared):
```markdown
# Project Context

## Name
[Project name]

## Description
[One-paragraph description]

## Tech Stack
- Primary: TypeScript
- Framework: Next.js
- Styling: Tailwind CSS

## Type
Web Application
```

---

## Workflow Scenarios

### Scenario 1: New Project

```
1. /speckit.init
   └─ Creates .claude/, detects tech, selects memory files

2. /docs.init (suggested)
   └─ Creates docs/, docs memory files
   └─ Reads tech detection from speckit

3. /speckit.plan
   └─ Creates implementation plan in .claude/resources/plan.md

4. /docs.plan --from-speckit (suggested)
   └─ Reads plan.md
   └─ Creates documentation WBS

5. /speckit.implement (multiple runs)
   └─ Implements features

6. /docs.sync (suggested after each implementation)
   └─ Walks code
   └─ Updates docs based on reality

7. /docs.generate
   └─ Creates documentation from WBS
```

### Scenario 2: Existing Project, Adding Docs

```
1. /docs.init
   └─ Detects existing .claude/ from previous speckit run
   └─ Creates docs/ structure

2. /docs.inventory
   └─ Scans .claude/resources/ for speckit artifacts
   └─ Registers as documentation sources

3. /docs.sync --walkthrough
   └─ Full code exploration
   └─ Creates docs-codebase-snapshot.md

4. /docs.plan
   └─ Plans docs based on inventory + code snapshot
```

### Scenario 3: Post-Implementation Documentation

```
# After speckit.implement completes a feature

1. /docs.sync
   └─ "Implementation detected for: authentication"
   └─ Walks auth code
   └─ Compares to existing docs
   └─ Reports: 3 discrepancies found

2. User reviews sync report
   └─ Approves auto-updates for simple changes
   └─ Marks complex changes for manual review

3. /docs.generate WBS-003
   └─ Generates authentication.md
   └─ Uses code reality, not just specs
```

---

## Memory File Coordination

### Complementary Memory Files

| speckit Memory | docs Memory | Relationship |
|----------------|-------------|--------------|
| `constitution.md` | `docs-constitution.md` | Parallel principles |
| `typescript.md` | - | Referenced for code examples |
| `testing.md` | - | Referenced for test docs |
| - | `docs-sources.md` | Docs-specific tracking |
| - | `docs-terminology.md` | Docs-specific terms |
| `project-context.md` | (shared) | Both read |

### Loading Order

When generating developer documentation:
1. Load `constitution.md` (dev principles)
2. Load `docs-constitution.md` (doc principles)
3. Load relevant tech memory (e.g., `typescript.md`)
4. Apply combined context to generation

### Cross-References

**In generated docs**:
```markdown
## Code Style

This project follows the coding standards defined in
`.claude/memory/typescript.md`. Key points:

- Use TypeScript strict mode
- Prefer interfaces over types
- ...
```

**In docs-constitution.md**:
```markdown
## Coordination with Development Standards

Documentation code examples MUST comply with:
- `.claude/memory/constitution.md` - Core principles
- `.claude/memory/{language}.md` - Language standards

Reference these when creating code examples.
```

---

## Detection Logic

### Detecting speckit Presence

```python
def has_speckit_context(project_path: Path) -> bool:
    """Check if speckit has been run on this project."""
    claude_dir = project_path / ".claude"

    indicators = [
        claude_dir / "memory" / "constitution.md",
        claude_dir / "memory" / "project-context.md",
        claude_dir / "resources" / "plan.md",
    ]

    return any(f.exists() for f in indicators)
```

### Detecting Implementation Changes

```python
def implementation_changed_since_docs(
    project_path: Path,
    docs_path: Path
) -> bool:
    """Check if code changed since docs were last updated."""

    # Get last docs update time
    progress = docs_path / "_meta" / "progress.md"
    last_docs_update = progress.stat().st_mtime if progress.exists() else 0

    # Check for code files modified after docs
    code_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".rs"}
    for file in project_path.rglob("*"):
        if file.suffix in code_extensions:
            if file.stat().st_mtime > last_docs_update:
                return True

    return False
```

---

## CLI Flags

### docs.plan

```bash
# Standard planning
/docs.plan

# Use speckit artifacts
/docs.plan --from-speckit

# Specify speckit plan location
/docs.plan --from-speckit --plan-path .claude/resources/plan.md
```

### docs.sync

```bash
# Standard sync
/docs.sync

# Full walkthrough mode
/docs.sync --walkthrough

# Sync specific component
/docs.sync --component authentication
```
