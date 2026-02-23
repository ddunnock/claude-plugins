# Requirements-Dev Plugin Usage Guide

## Quick Start

The requirements-dev plugin provides INCOSE-aligned requirements engineering for Claude Code projects. It transforms concept-dev outputs into formal, traceable requirements through a structured workflow.

### Prerequisites

- A completed concept-dev session (with `.concept-dev/` directory containing source/assumption registries)
- Claude Code with the requirements-dev plugin installed

### Workflow

```
/reqdev:init     --> Initialize session, ingest concept-dev artifacts
/reqdev:needs    --> Capture stakeholder needs (INCOSE pattern)
/reqdev:requirements --> Develop requirements block-by-block
/reqdev:validate --> Cross-block validation sweep
/reqdev:research --> TPM benchmark research (optional)
/reqdev:deliver  --> Baseline and export deliverables
/reqdev:decompose --> Subsystem decomposition (optional)
/reqdev:status   --> Session dashboard
/reqdev:resume   --> Resume interrupted session
```

## Commands

### `/reqdev:init`
Initializes a `.requirements-dev/` workspace. Ingests concept-dev artifacts (source registry, assumption registry, concept document). Detects available research tools for later TPM research.

### `/reqdev:needs`
Interactive stakeholder needs capture. Each need follows INCOSE pattern: "The [stakeholder] needs [capability] so that [rationale]." Supports add, update, defer, reject, list, query, and export subcommands.

### `/reqdev:requirements`
Block-by-block, type-guided requirements development. Processes each block through 5 type passes (functional, performance, interface, constraint, quality). Each requirement undergoes:
- 16 deterministic INCOSE GtWR v4 quality checks
- Semantic quality review via quality-checker agent
- V&V method planning
- Traceability linking (derives_from needs, informed_by sources)

### `/reqdev:validate`
Cross-block validation sweep with 6 checks:
- Interface coverage between related blocks
- Duplicate detection (n-gram cosine similarity)
- Terminology consistency
- Uncovered needs
- Open TBD/TBR items
- INCOSE C10-C15 set characteristics

Optional skeptic agent (opus) for feasibility verification.

### `/reqdev:research`
TPM benchmark research using tiered tool strategy. Launches tpm-researcher agent to find real-world performance benchmarks for requirements with quantitative values.

### `/reqdev:deliver`
Baselines all requirements, generates deliverable documents (requirements specification, traceability matrix, verification matrix), and optionally exports ReqIF XML.

### `/reqdev:decompose`
Decomposes baselined blocks into sub-blocks with requirement allocation. Validates allocation coverage (100% required). Sub-blocks then re-enter the requirements pipeline at the subsystem level.

### `/reqdev:status`
Session dashboard showing phase progress, block progress, requirement counts, traceability coverage, and next recommended action.

### `/reqdev:resume`
Resumes an interrupted session. Detects 5 resumption patterns: mid-block requirements, validation in progress, delivery incomplete, decomposition in progress, and fresh phase start.

## Scripts (CLI Reference)

All scripts are in `scripts/` and use `python3 <script> --workspace .requirements-dev/ <subcommand>`.

| Script | Purpose |
|--------|---------|
| `init_session.py` | Workspace creation, session management |
| `update_state.py` | State machine (phases, gates, progress) |
| `ingest_concept.py` | Concept-dev artifact ingestion |
| `check_tools.py` | Research tool availability detection |
| `needs_tracker.py` | Need CRUD operations |
| `quality_rules.py` | 16 deterministic quality checks |
| `requirement_tracker.py` | Requirement lifecycle management |
| `traceability.py` | Bidirectional link management |
| `source_tracker.py` | Source registration with research context |
| `set_validator.py` | Cross-block validation checks |
| `reqif_export.py` | ReqIF XML export |
| `decompose.py` | Subsystem decomposition logic |
| `shared_io.py` | Atomic writes, path validation |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `quality-checker` | sonnet | Semantic quality review (9 LLM rules) |
| `document-writer` | sonnet | Deliverable document generation |
| `tpm-researcher` | sonnet | Performance benchmark research |
| `skeptic` | opus | Coverage and feasibility verification |

## Data Files

| File | Contents |
|------|----------|
| `data/absolutes.json` | Absolute terms (all, every, never, etc.) |
| `data/escape_clauses.json` | Escape clauses (if possible, as appropriate, etc.) |
| `data/pronouns.json` | Ambiguous pronouns (it, they, this, etc.) |
| `data/vague_terms.json` | Vague qualitative terms (fast, efficient, etc.) |

## Workspace Structure

After initialization, `.requirements-dev/` contains:

```
.requirements-dev/
  state.json                    # Session state, phases, gates, blocks
  needs_registry.json           # Stakeholder needs
  requirements_registry.json    # Formal requirements
  traceability_registry.json    # Bidirectional links
  source_registry.json          # Research sources
```

## Test Suite

```bash
cd skills/requirements-dev
uv run pytest           # 172 tests, ~0.5s
uv run pytest -v        # Verbose output
uv run pytest -k "test_quality"  # Filter by name
```
