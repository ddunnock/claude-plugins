# requirements-dev

A Claude Code plugin for INCOSE-compliant requirements development. Transforms concept development artifacts into formal requirements with hybrid quality checking, verification planning, bidirectional traceability, and deliverable generation.

## Overview

requirements-dev guides you through a three-phase, gate-controlled workflow:

| Phase | Purpose | Commands |
|-------|---------|----------|
| **1. Foundation** | Ingest concepts, formalize needs, develop requirements, generate deliverables | `/reqdev:init`, `/reqdev:needs`, `/reqdev:requirements`, `/reqdev:deliver` |
| **2. Validation & Research** | Cross-block validation, duplicate detection, TPM benchmarks | `/reqdev:validate`, `/reqdev:research` |
| **3. Decomposition** | Subsystem breakdown with allocation rationale (max 3 levels) | `/reqdev:decompose` |

Each phase has a mandatory gate -- the plugin will not advance until you explicitly approve the output.

## Installation

### Basic Setup

Copy or symlink the `requirements-dev/` directory into your Claude Code plugins path. The plugin registers automatically via `.claude-plugin/plugin.json`.

**System requirements:**

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | >= 3.11 | For running scripts |
| Claude Code | Latest | Plugin host |

### Optional Dependencies

| Package | Install | Used By | Purpose |
|---------|---------|---------|---------|
| `reqif` (strictdoc) | `pip install reqif` | `/reqdev:deliver` | ReqIF XML export to industry-standard interchange format |
| `crawl4ai` | `pip install crawl4ai` | `/reqdev:research` | Deep web crawling for TPM benchmark research |

Without these packages all core features work. Missing packages produce a user-friendly message explaining how to install them.

### Research Tool Tiers

The `/reqdev:init` command detects available research tools and adapts the research strategy accordingly.

| Tier | Tools | Notes |
|------|-------|-------|
| Always available | `WebSearch`, `WebFetch` | Built into Claude Code |
| Python packages | `crawl4ai` | Detected via import check at init |
| Tier 1 (Free MCP) | `jina`, `paper_search`, `fetch` | Detected at runtime via ToolSearch |
| Tier 2 (Configurable) | `tavily`, `semantic_scholar`, `context7` | Optional MCP servers |
| Tier 3 (Premium) | `exa`, `perplexity` | Optional MCP servers |

## Quick Start

```
/reqdev:init           # Create workspace, ingest concept-dev artifacts
/reqdev:needs          # Formalize stakeholder needs per block
/reqdev:requirements   # Develop requirements with quality checking
/reqdev:deliver        # Generate specification documents
```

The plugin guides you through each phase with prompts, gates, and suggested next steps.

## Commands

| Command | Description |
|---------|-------------|
| `/reqdev:init` | Initialize session, create `.requirements-dev/` workspace, ingest concept-dev artifacts |
| `/reqdev:needs` | Formalize stakeholder needs per functional block using INCOSE patterns |
| `/reqdev:requirements` | Block-by-block, type-guided requirements engine with hybrid quality checking |
| `/reqdev:validate` | Set validation sweep (coverage, duplicates, terminology, TBD/TBR, INCOSE C10-C15) |
| `/reqdev:research` | TPM research for measurable requirements with industry benchmark tables |
| `/reqdev:deliver` | Generate deliverable documents and optional ReqIF export |
| `/reqdev:decompose` | Subsystem decomposition with allocation rationale (max 3 levels) |
| `/reqdev:status` | Session dashboard (phase, counts, coverage, TBD/TBR, next action) |
| `/reqdev:resume` | Resume interrupted session from last checkpoint |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `quality-checker` | Sonnet | 9 semantic INCOSE rules with chain-of-thought reasoning |
| `tpm-researcher` | Sonnet | Industry benchmark research with tiered tool strategy and structured tables |
| `skeptic` | Opus | Coverage verification and feasibility checking |
| `document-writer` | Sonnet | Deliverable generation from registries and templates |

## Scripts

All scripts live in `scripts/` and are invoked by commands/agents via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/...` for deterministic path resolution. Each uses atomic writes (temp-file-then-rename) and validates paths at the argparse boundary to prevent path traversal.

### Registry Management

| Script | Functions | Description |
|--------|-----------|-------------|
| `needs_tracker.py` | `add_need`, `update_need`, `defer_need`, `reject_need`, `split_need`, `list_needs`, `query_needs`, `export_needs` | Stakeholder needs CRUD with INCOSE-pattern formalization, compound need splitting, concept-dev cross-references, and state sync |
| `requirement_tracker.py` | `add_requirement`, `register_requirement`, `baseline_requirement`, `baseline_all`, `withdraw_requirement`, `split_requirement`, `update_requirement`, `list_requirements`, `query_requirements`, `export_requirements` | Requirements lifecycle (draft -> registered -> baselined -> withdrawn) with split workflow, type/priority validation and parent-need traceability |
| `source_tracker.py` | `add_source`, `list_sources`, `export_sources` | Source reference registry for research artifacts and concept-dev cross-references |
| `traceability.py` | `link`, `query`, `coverage_report`, `orphan_check` | Bidirectional traceability links with referential integrity, coverage analysis, and orphan detection |

### Quality and Validation

| Script | Functions | Description |
|--------|-----------|-------------|
| `quality_rules.py` | `check_requirement`, `check_rule`, `list_rules` | 16 deterministic INCOSE GtWR v4 quality rules (R2-R40): vague terms, escape clauses, passive voice, combinators, pronouns, absolutes, and more |
| `set_validator.py` | `validate_all`, `check_interface_coverage`, `check_duplicates`, `check_terminology`, `check_uncovered_needs`, `check_tbd_tbr`, `check_incose_set_characteristics` | Cross-block set validation with n-gram cosine similarity for duplicates, synonym-group terminology checking, and INCOSE C10-C15 compliance |

| `notes_tracker.py` | `add_note`, `resolve_note`, `dismiss_note`, `list_notes`, `check_gate`, `summary`, `export_notes` | Cross-cutting notes registry for observations surfacing in one phase but belonging to another, with gate integration |

### Session and State

| Script | Functions | Description |
|--------|-----------|-------------|
| `init_session.py` | `init_workspace` | Create `.requirements-dev/` workspace from template, detect existing sessions for resume |
| `update_state.py` | `set_phase`, `pass_gate`, `check_gate`, `set_artifact`, `update_field`, `sync_counts`, `show` | State machine for phase transitions, gate management, count synchronization, and dot-notation field updates |
| `check_tools.py` | `check_tools`, `detect_python_package` | Detect available research tools by tier and record in state.json |

### Specialized

| Script | Functions | Description |
|--------|-----------|-------------|
| `ingest_concept.py` | `ingest` | Parse concept-dev JSON registries (sources, assumptions) and validate artifact presence |
| `decompose.py` | `validate_baseline`, `register_sub_blocks`, `allocate_requirement`, `validate_allocation_coverage`, `update_decomposition_state`, `check_max_level` | Subsystem decomposition with baseline validation, sub-block registration, requirement allocation, and coverage tracking |
| `reqif_export.py` | `export_reqif` | ReqIF XML export using strictdoc's reqif package with SPEC-OBJECTs, SPEC-RELATIONs, and atomic writes |
| `shared_io.py` | `_atomic_write`, `_validate_path`, `_validate_dir_path` | Shared utilities: atomic JSON writes via temp-file-then-rename, path traversal validation |

## Quality Rules

The plugin applies a two-tier quality checking system to every requirement:

### Tier 1: Deterministic (16 rules, instant)

| Rule | Name | Severity | Detection |
|------|------|----------|-----------|
| R2 | Passive voice | warning | Heuristic be-form + past participle detection |
| R7 | Vague terms | error | 50+ terms from INCOSE word list |
| R8 | Escape clauses | error | Phrases that weaken obligation |
| R9 | Open-ended clauses | error | "etc.", "and so on", "including but not limited to" |
| R10 | Superfluous infinitives | error | "be able to", "be capable of" |
| R15 | Logical and/or | error | Ambiguous "and/or" usage |
| R16 | Negatives | warning | Negative requirements |
| R19 | Combinators | warning | Multiple "shall" clauses combined |
| R20 | Purpose phrases | warning | "in order to", "so that" |
| R21 | Parentheses | warning | Parenthetical content |
| R24 | Pronouns | error | Ambiguous pronoun references |
| R26 | Absolutes | error | "always", "never", "every" |
| R32 | Universal quantifiers | warning | "each", "every", "all", "any" |
| R33 | Range checking | warning | Numeric ranges missing units |
| R35 | Temporal dependencies | warning | Temporal keywords needing precision |
| R40 | Decimal format | warning | Mixed decimal separators |

### Tier 2: Semantic (9 rules, LLM-assisted)

Run by the `quality-checker` agent with chain-of-thought reasoning. Covers necessity, feasibility, singularity, verifiability, completeness, non-ambiguity, design-freedom, traceability, and conformance.

## Data Files

Word lists used by deterministic quality rules, located in `data/`:

| File | Contents |
|------|----------|
| `vague_terms.json` | 50+ INCOSE-flagged vague/ambiguous terms |
| `escape_clauses.json` | Phrases that weaken requirement obligation |
| `pronouns.json` | Pronouns that create ambiguous references |
| `absolutes.json` | Absolute terms requiring quantified criteria |

## Templates

Document templates in `templates/` used by the `document-writer` agent:

| Template | Output |
|----------|--------|
| `state.json` | Session state initialization template |
| `requirements-specification.md` | REQUIREMENTS-SPECIFICATION.md deliverable |
| `traceability-matrix.md` | TRACEABILITY-MATRIX.md deliverable |
| `verification-matrix.md` | VERIFICATION-MATRIX.md deliverable |

## Reference Documents

Guides in `references/` used by agents and commands:

| Reference | Purpose |
|-----------|---------|
| `type-guide.md` | Requirement type definitions with examples and block-pattern hints |
| `vv-methods.md` | V&V method selection guide with type-to-method mapping |
| `incose-rules.md` | Full INCOSE GtWR v4 rule reference |
| `attribute-schema.md` | Requirement attribute schema definition |
| `decomposition-guide.md` | Subsystem decomposition methodology |

## Hooks

| Event | Trigger | Action |
|-------|---------|--------|
| `PostToolUse` | Write to `**/.requirements-dev/*.md` | Auto-update state.json via `update-state-on-write.sh` |

## Final Deliverables

1. **REQUIREMENTS-SPECIFICATION.md** -- All requirements organized by block and type with V&V methods
2. **TRACEABILITY-MATRIX.md** -- Bidirectional traceability from concept sources through needs to requirements
3. **VERIFICATION-MATRIX.md** -- Verification methods, success criteria, and status for all requirements
4. **JSON registries** -- Machine-readable needs, requirements, traceability links, and sources
5. **ReqIF export** (optional) -- Industry-standard requirements interchange format

## Project Structure

```
requirements-dev/
  .claude-plugin/plugin.json   Plugin manifest
  SKILL.md                     Skill trigger description
  pyproject.toml               Python project config (>=3.11)
  agents/                      4 specialized LLM agents
  commands/                    9 slash commands
  data/                        Quality rule word lists
  hooks/                       PostToolUse hook for state sync
  references/                  INCOSE methodology guides
  scripts/                     14 Python scripts (CLI + library)
  templates/                   Deliverable document templates
  tests/                       216 pytest tests
```

## Security

- **Path traversal prevention:** All CLI path arguments are validated at the argparse boundary via `type=_validate_dir_path` or `type=_validate_path`, rejecting any path containing `..` components
- **Extension whitelisting:** File path arguments are restricted to expected extensions (`.json`, `.reqif`, `.md`)
- **Atomic writes:** All JSON mutations use temp-file-then-rename to prevent corruption
- **No network access from scripts:** Python scripts perform no network requests; research is done through Claude tools (WebSearch, WebFetch)
- **External content isolation:** TPM research content is wrapped in BEGIN/END EXTERNAL CONTENT markers
- **HTML escaping:** User content in generated deliverables is escaped via `html.escape()`

## Testing

```bash
cd skills/requirements-dev
python3 -m pytest tests/    # 216 tests
python3 -m pytest tests/ -q # Quiet mode
python3 -m pytest tests/ -k needs # Filter by keyword
```

## Version History

### v1.1.0
- **Cross-cutting notes registry:** Capture observations that surface in one phase but belong to another. Notes are tracked through `open` → `resolved` | `dismissed` lifecycle with mandatory gate checks before phase advancement. New `notes_tracker.py` script with 7 functions and full CLI.
- **Need/requirement split workflow:** Compound needs and multi-thought requirements are detected and can be split into atomic items. Quality-checker agent suggests splits for R18 (Single Thought) and R19 (Combinators). New `split_need()` and `split_requirement()` functions with split/rewrite/override decision workflow.
- **Deterministic script path resolution:** All commands use `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/...` instead of relative paths, eliminating CWD-dependent failures.
- **User-friendly security messaging:** Rewrote content security documentation with plain-language callout box explaining protections as background safeguards.
- **Hooks schema fix:** Corrected `hooks.json` from array format to record-keyed-by-event format matching the plugin schema.
- 14 scripts, 216 pytest tests (was 13 scripts, 172 tests)

### v1.0.0
- Three-phase requirements development workflow
- Hybrid quality checking (16 deterministic + 9 semantic INCOSE GtWR v4 rules)
- Bidirectional traceability engine with coverage analysis
- V&V planning with type-to-method mapping
- ReqIF export support
- 4 specialized agents, 13 scripts, 9 commands
- 172 pytest tests
