# Init Workflow

Detailed workflow for `/docs.init` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Workflow Steps](#workflow-steps)
- [Outputs](#outputs)
- [Idempotency](#idempotency)
- [speckit Integration](#speckit-integration)

---

## Purpose

Establish the documentation foundation for a project by creating:
1. `docs/` directory structure following Diátaxis framework
2. Skill memory files in `.claude/memory/`
3. Project documentation context

---

## Trigger Conditions

**Explicit**:
- User runs `/docs.init`

**Auto-suggested**:
- Other `/docs.*` commands detect missing foundation
- After `/speckit.init` completes

---

## Workflow Steps

### Step 1: Assess Current State

Check for existing documentation infrastructure:

```
Check:
├─ docs/ directory exists?
├─ docs/_meta/ exists?
├─ .claude/memory/docs-*.md files exist?
└─ README.md exists?
```

**If exists**: Present options
```
Existing documentation structure detected:

docs/
├── [existing structure summary]

Options:
1. Augment - Add missing directories/files only
2. Reset - Remove and recreate (requires confirmation)
3. Skip - Exit without changes
```

### Step 2: Detect Project Type

Analyze project to determine documentation needs:

| Indicator | Project Type | Doc Needs |
|-----------|--------------|-----------|
| `package.json` + no `bin` | Library | API reference, integration guide |
| `package.json` + `bin` | CLI Tool | Command reference, tutorials |
| `main.py`, `app.py` | Application | User guides, deployment |
| `Cargo.toml` + `[[bin]]` | CLI Tool | Command reference |
| `Cargo.toml` + `[lib]` | Library | API reference |
| `.claude/resources/*.md` | Has specs | Plan from specs |

Present detection result:
```
Project Type Detected: [TYPE]

Based on:
- [indicator 1]
- [indicator 2]

This suggests documentation structure optimized for:
- [need 1]
- [need 2]

Proceed with this configuration? [Y/n]
```

### Step 3: Create Directory Structure

Create Diátaxis-aligned directory structure:

```bash
mkdir -p docs/user/getting-started
mkdir -p docs/user/guides
mkdir -p docs/user/concepts
mkdir -p docs/user/reference
mkdir -p docs/developer/architecture/decisions
mkdir -p docs/developer/contributing
mkdir -p docs/developer/reference/api
mkdir -p docs/_meta
```

### Step 4: Create Placeholder Files

Create index files with structure guidance:

**docs/index.md**:
```markdown
# [Project Name] Documentation

Welcome to the [Project Name] documentation.

## For Users

- [Getting Started](user/getting-started/) - Learn the basics
- [Guides](user/guides/) - How to accomplish specific tasks
- [Concepts](user/concepts/) - Understand how things work
- [Reference](user/reference/) - Configuration and options

## For Developers

- [Architecture](developer/architecture/) - System design and decisions
- [Contributing](developer/contributing/) - How to contribute
- [API Reference](developer/reference/api/) - Technical API documentation
```

### Step 5: Create Skill Memory Files

Create documentation-specific memory files in `.claude/memory/`:

**docs-constitution.md**:
```markdown
# Documentation Constitution

## Core Principles

1. **User-Centric**: Documentation serves the reader, not the writer
2. **Diátaxis Framework**: Content organized by user need (Tutorial/How-To/Reference/Explanation)
3. **Source-Grounded**: Every claim cites its source
4. **Maintainable**: Structure supports easy updates

## Quality Standards

- Clear, scannable headings
- Code examples are tested and work
- Links are verified
- Terminology is consistent (see docs-terminology.md)

## Review Requirements

- All new documents go through review loop
- Changes trigger cascade analysis
- Major changes require user approval
```

**docs-terminology.md**:
```markdown
# Documentation Terminology Registry

## Term Definitions

| Term | Definition | Usage Context |
|------|------------|---------------|
| *Add terms during documentation* | | |

## Consistency Rules

- Use consistent capitalization
- Prefer shorter terms when equally clear
- Define acronyms on first use
```

**docs-sources.md**:
```markdown
# Documentation Sources Registry

## Source Catalog

| ID | Source | Type | Location | Status |
|----|--------|------|----------|--------|
| *Sources registered during inventory* | | | | |

## Source Types

- SPEC: Specification document
- ADR: Architecture Decision Record
- RFC: Request for Comments
- CODE: Source code
- DOC: Existing documentation
- USER: User-provided information
```

### Step 6: Create Metadata Files

Create tracking files in `docs/_meta/`:

**docs/_meta/inventory.md**:
```markdown
# Documentation Inventory

*Run `/docs.inventory` to populate this file.*

## Source Registry

| ID | Source | Type | Diátaxis | Status |
|----|--------|------|----------|--------|

## Coverage Assessment

| Quadrant | Coverage | Notes |
|----------|----------|-------|
| Tutorial | - | |
| How-To | - | |
| Reference | - | |
| Explanation | - | |
```

**docs/_meta/progress.md**:
```markdown
# Documentation Progress

## Session History

| Session | Date | Actions | Documents |
|---------|------|---------|-----------|
| INIT | [timestamp] | Created structure | - |

## Status Summary

- Total Documents: 0
- Completed: 0
- In Progress: 0
- Planned: 0
```

### Step 7: Present Summary

```
Documentation Foundation Created:

docs/
├── index.md
├── user/
│   ├── getting-started/
│   ├── guides/
│   ├── concepts/
│   └── reference/
├── developer/
│   ├── architecture/decisions/
│   ├── contributing/
│   └── reference/api/
└── _meta/
    ├── inventory.md
    └── progress.md

.claude/memory/
├── docs-constitution.md
├── docs-terminology.md
└── docs-sources.md

Next Steps:
1. Run /docs.inventory to catalog sources
2. Run /docs.plan to create documentation plan
3. Run /docs.readme --init to create README.md
```

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| Directory structure | `docs/` | Documentation home |
| Index file | `docs/index.md` | Navigation hub |
| Constitution | `.claude/memory/docs-constitution.md` | Principles |
| Terminology | `.claude/memory/docs-terminology.md` | Term registry |
| Sources | `.claude/memory/docs-sources.md` | Source tracking |
| Inventory | `docs/_meta/inventory.md` | Source catalog |
| Progress | `docs/_meta/progress.md` | Session tracking |

---

## Idempotency

**Safe behaviors**:
- Skips existing directories
- Updates memory files only if content changed (hash comparison)
- Never deletes existing content
- Preserves user customizations

**Detection**:
```python
def is_initialized(project_path):
    docs_dir = project_path / "docs"
    meta_dir = docs_dir / "_meta"
    memory_dir = project_path / ".claude" / "memory"

    return (
        docs_dir.exists() and
        meta_dir.exists() and
        (memory_dir / "docs-constitution.md").exists()
    )
```

**Catch-up mode**:
- If partial init detected, offer to complete missing pieces
- Never re-create files that exist and have content

---

## speckit Integration

### After `/speckit.init`

When speckit.init completes, suggest docs initialization:

```
/speckit.init complete.

Project foundation established with:
- .claude/ structure
- Memory files selected for [tech stack]

Documentation setup available. Run /docs.init?
- Will create docs/ structure aligned with project type
- Will link to existing .claude/memory/
- Will detect documentation needs from speckit context
```

### Shared Context

Read from speckit artifacts if available:
- `project-context.md` - Project description, tech stack
- Memory files - Coding standards inform doc style
- Tech detection results - Inform project type classification

### Memory File Coordination

Documentation memory files complement speckit memory files:
- `constitution.md` (speckit) → Development principles
- `docs-constitution.md` (docs) → Documentation principles
- Both loaded when generating developer documentation
