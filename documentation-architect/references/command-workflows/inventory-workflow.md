# Inventory Workflow

Detailed workflow for `/docs.inventory` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Workflow Steps](#workflow-steps)
- [Source Classification](#source-classification)
- [Outputs](#outputs)
- [Idempotency](#idempotency)

---

## Purpose

Catalog and classify all documentation sources in the project:
1. Scan available source locations
2. Classify sources by type and Diátaxis quadrant
3. Estimate token counts for chunking decisions
4. Register sources in tracking system
5. Identify coverage gaps

---

## Trigger Conditions

**Explicit**:
- User runs `/docs.inventory`

**Auto-suggested**:
- After `/docs.init` completes
- When `/docs.plan` detects missing inventory
- After new sources added to `.claude/resources/`

---

## Workflow Steps

### Step 1: Identify Source Locations

Scan for sources in standard locations:

```
Source Locations:
├─ .claude/resources/          # Uploaded specs, plans, RFCs
├─ .claude/memory/             # Existing memory files
├─ docs/                       # Existing documentation
├─ README.md, CHANGELOG.md     # Root documentation
├─ Codebase                    # Docstrings, comments
└─ ADRs (docs/*/decisions/)    # Architecture Decision Records
```

### Step 2: Extract Source Metadata

For each discovered source:

| Field | Description |
|-------|-------------|
| ID | Unique identifier (SRC-001, SRC-002...) |
| Name | File or resource name |
| Location | Path or URL |
| Type | SPEC, ADR, RFC, CODE, DOC, USER |
| Size | Character/token count |
| Last Modified | Timestamp |
| Summary | Brief description |

### Step 3: Classify by Diátaxis Quadrant

Map each source to potential documentation output:

| Source Type | Primary Quadrant | Secondary |
|-------------|------------------|-----------|
| SPEC (feature) | How-To | Reference |
| SPEC (architecture) | Explanation | Reference |
| ADR | Explanation | Reference |
| RFC | Explanation | How-To |
| CODE (public API) | Reference | How-To |
| CODE (examples) | Tutorial | How-To |
| DOC (existing) | Preserve quadrant | - |

### Step 4: Estimate Token Counts

For chunking decisions:

```python
def estimate_tokens(content: str) -> int:
    """Rough token estimate (chars / 4)."""
    return len(content) // 4

# Chunking thresholds
CHUNK_THRESHOLD = 8000  # tokens
LARGE_SOURCE = 16000    # tokens - requires chunking plan
```

### Step 5: Register Sources

Update `docs/_meta/inventory.md`:

```markdown
# Documentation Inventory

**Last Updated**: [timestamp]
**Total Sources**: [count]

## Source Registry

| ID | Source | Type | Quadrant | Tokens | Status |
|----|--------|------|----------|--------|--------|
| SRC-001 | requirements.md | SPEC | How-To | 2,400 | Pending |
| SRC-002 | api-design.md | SPEC | Reference | 5,200 | Pending |
| SRC-003 | ADR-001.md | ADR | Explanation | 800 | Pending |

## Large Sources (Require Chunking)

| Source | Tokens | Suggested Chunks |
|--------|--------|------------------|
| full-spec.md | 24,000 | 3 chunks |
```

Update `.claude/memory/docs-sources.md`:

```markdown
# Documentation Sources Registry

## Active Sources

| ID | Source | Type | Location | Last Synced |
|----|--------|------|----------|-------------|
| SRC-001 | requirements.md | SPEC | .claude/resources/ | [timestamp] |

## Source Types

- SPEC: Specification document
- ADR: Architecture Decision Record
- RFC: Request for Comments
- CODE: Source code (docstrings, comments)
- DOC: Existing documentation
- USER: User-provided information
```

### Step 6: Assess Coverage

Generate coverage matrix:

```markdown
## Coverage Assessment

| Quadrant | Sources | Coverage | Gaps |
|----------|---------|----------|------|
| Tutorial | 0 | None | Getting started guide needed |
| How-To | 3 | Partial | Authentication, deployment |
| Reference | 2 | Good | API fully covered |
| Explanation | 1 | Minimal | Architecture overview needed |

## Recommended Actions

1. HIGH: Create getting-started tutorial
2. MEDIUM: Document authentication flow
3. LOW: Add architecture explanation
```

### Step 7: Present Summary

```
Documentation Inventory Complete:

Sources Found: 12
├─ Specifications: 4
├─ ADRs: 2
├─ Code (docstrings): 5
└─ Existing docs: 1

Coverage:
├─ Tutorial: None
├─ How-To: Partial (3 sources)
├─ Reference: Good (6 sources)
└─ Explanation: Minimal (1 source)

Large sources requiring chunking: 2

Files updated:
├─ docs/_meta/inventory.md
└─ .claude/memory/docs-sources.md

Next: Run /docs.plan to create documentation plan
```

---

## Source Classification

### Type Definitions

| Type | Description | Examples |
|------|-------------|----------|
| SPEC | Requirements, feature specs | SRS, PRD, feature.md |
| ADR | Architecture decisions | ADR-001-auth-strategy.md |
| RFC | Proposals, design docs | RFC-002-api-versioning.md |
| CODE | Source code artifacts | Docstrings, JSDoc, comments |
| DOC | Existing documentation | README, guides, API docs |
| USER | User-provided info | Uploads, conversation context |

### Detection Patterns

**SPEC Detection**:
- Files in `.claude/resources/` with requirements patterns
- Contains sections like "Requirements", "Features", "User Stories"

**ADR Detection**:
- Files matching `ADR-*.md` or in `decisions/` directory
- Contains "Status", "Context", "Decision" sections

**RFC Detection**:
- Files matching `RFC-*.md`
- Contains "Proposal", "Motivation", "Detailed Design"

**CODE Detection**:
- Python: `ast.get_docstring()` extraction
- TypeScript: JSDoc comment extraction
- Public exports, API definitions

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| Source registry | `docs/_meta/inventory.md` | Master list of sources |
| Source memory | `.claude/memory/docs-sources.md` | Cross-session tracking |
| Coverage matrix | Within inventory.md | Gap analysis |

---

## Idempotency

**Safe behaviors**:
- Re-scans all locations on each run
- Updates existing source entries (doesn't duplicate)
- Adds new sources discovered
- Never removes sources from registry (mark as "Archived" instead)
- Preserves user-added notes on sources

**Detection**:
```python
def source_exists(inventory: dict, source_path: str) -> bool:
    """Check if source already registered."""
    return any(
        s["location"] == source_path
        for s in inventory.get("sources", [])
    )
```

**Re-run behavior**:
```
First run:
  + Added 12 sources

Second run (no changes):
  = All sources up to date

Third run (new file added):
  + Added 1 new source
  = 12 sources unchanged
```
