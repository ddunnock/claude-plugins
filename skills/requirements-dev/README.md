# requirements-dev

A Claude Code plugin for INCOSE-compliant requirements development. Transforms concept development artifacts into formal requirements with hybrid quality checking, verification planning, bidirectional traceability, and deliverable generation.

## What It Does

requirements-dev guides you through three progressive phases:

| Phase | Commands | Output |
|-------|----------|--------|
| 1. Foundation | `/reqdev:init`, `/reqdev:needs`, `/reqdev:requirements`, `/reqdev:deliver` | REQUIREMENTS-SPECIFICATION.md, TRACEABILITY-MATRIX.md, VERIFICATION-MATRIX.md |
| 2. Validation & Research | `/reqdev:validate`, `/reqdev:research` | Validation findings, TPM benchmarks |
| 3. Decomposition | `/reqdev:decompose` | Subsystem requirements with allocation rationale |

Each phase has a mandatory gate -- Claude will not advance until you explicitly approve the output.

## Final Deliverables

1. **REQUIREMENTS-SPECIFICATION.md** -- All requirements organized by block and type with V&V methods
2. **TRACEABILITY-MATRIX.md** -- Bidirectional traceability from concept sources through needs to requirements
3. **VERIFICATION-MATRIX.md** -- Verification methods, success criteria, and status for all requirements
4. **JSON registries** -- Machine-readable needs, requirements, traceability links, and sources
5. **ReqIF export** (optional) -- Industry-standard requirements interchange format

## Installation

Copy or symlink the `requirements-dev/` directory into your Claude Code plugins path. The plugin registers automatically via `.claude-plugin/plugin.json`.

### Optional: ReqIF Export

```bash
pip install strictdoc-reqif
```

Without the reqif package, all features work except `/reqdev:deliver` with ReqIF format. A graceful ImportError message will explain how to install it.

## Quick Start

```
/reqdev:init           # Create workspace, ingest concept-dev artifacts
/reqdev:needs          # Formalize stakeholder needs
```

That's it. The plugin guides you through each phase with prompts, gates, and suggested next steps.

## Commands

| Command | Description |
|---------|-------------|
| `/reqdev:init` | Initialize session, create `.requirements-dev/` workspace, ingest concept-dev artifacts |
| `/reqdev:needs` | Formalize stakeholder needs per functional block using INCOSE patterns |
| `/reqdev:requirements` | Block-by-block, type-guided requirements engine with quality checking |
| `/reqdev:validate` | Set validation and cross-cutting sweep (coverage, duplicates, terminology) |
| `/reqdev:research` | TPM research for measurable requirements with benchmark tables |
| `/reqdev:deliver` | Generate deliverable documents from templates |
| `/reqdev:decompose` | Subsystem decomposition with allocation rationale (max 3 levels) |
| `/reqdev:status` | Session status dashboard (phase, counts, coverage, TBD/TBR) |
| `/reqdev:resume` | Resume interrupted session from last checkpoint |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| quality-checker | Sonnet | 9 semantic INCOSE rules with chain-of-thought reasoning |
| tpm-researcher | Sonnet | Industry benchmark research for measurable requirements |
| skeptic | Opus | Coverage verification and feasibility checking |
| document-writer | Sonnet | Deliverable generation from registries and templates |

## Version History

### v1.0.0
- Initial release
- Three-phase requirements development workflow
- Hybrid quality checking (21 deterministic + 9 semantic INCOSE GtWR v4 rules)
- Bidirectional traceability engine
- V&V planning with type-to-method mapping
- ReqIF export support
- 4 specialized agents, 10 scripts, 9 commands
