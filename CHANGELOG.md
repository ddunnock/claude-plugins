# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-23

### Changed

- **requirements-dev v1.3.0** — Cross-skill remediation addressing 16 findings (3 bugs, 8 structural gaps, 5 missed opportunities) from concept-dev → requirements-dev integration analysis
  - **Bug fixes:** Gate schema mismatch with concept-dev state format, wrong ingestion keys in gap_analyzer concept_coverage, empty gates falsely reporting all_passed
  - **Enriched ingestion:** Carries forward research gaps, ungrounded claims, citations, confidence levels, and skeptic findings from concept-dev
  - **Assumption lifecycle:** New `assumption_tracker.py` (7 functions) implementing INCOSE GtWR v4 §5.3 — imports concept-dev assumptions, tracks through active→challenged→invalidated|reaffirmed lifecycle
  - **Interface coverage:** New `interface_coverage()` in gap_analyzer validates block relationships have corresponding interface requirements; new gap-analyst rules G8/G9
  - **Concept-origin traceability:** New `concept_origin` link type for backward traceability to concept artifacts
  - **ConOps mining, priority hints, provenance scoring:** Init mines ConOps scenarios; maturation paths map to priority hints; needs annotated with ★★★/★★/★ provenance quality
  - **Research reuse:** `/reqdev:research` checks for existing concept-dev research before launching web crawling
  - 5 agents, 16 scripts, 10 commands, 279 pytest tests (was 15 scripts, 241 tests)

## [1.1.0] - 2026-02-15

### Added

- **concept-dev plugin** — NASA Phase A concept development lifecycle with 7 agents, 9 commands, 6 scripts
  - Five-phase workflow: ideation, problem definition, black-box architecture, drill-down with gap analysis, document generation
  - Produces Concept Document and Solution Landscape with cited sources
  - Tiered research tool detection (WebSearch/WebFetch + crawl4ai, Tavily, Exa, etc.)
  - `web_researcher.py` script with crawl4ai integration for BM25-filtered deep web research

### Fixed

- **concept-dev: state.json counters always zero** — Tracker scripts (`source_tracker.py`, `assumption_tracker.py`) now auto-sync counts to state.json after every mutation
- **concept-dev: update_state.py couldn't handle nested paths** — Replaced `update_counters()` with `update_by_path()` supporting dotted paths like `phases.drilldown.blocks_total`
- **concept-dev: assumption_tracker.py never called** — Added `init` subcommand to create empty registry; `/concept:init` now initializes it; all phase commands register assumptions
- **concept-dev: skeptic agent never invoked** — All phase commands now use explicit `Task tool with subagent_type='concept-dev:skeptic'` syntax instead of vague references
- **concept-dev: no prerequisite checks** — Added `check-gate` subcommand to `update_state.py`; all phase commands (problem through document) now run programmatic gate checks
- **concept-dev: missing sync-counts** — Added `sync-counts` subcommand that reads both registries and updates all state.json counters
- **concept-dev: template reads not explicit** — All phase commands now include explicit `Read file:` instructions for templates
- **concept-dev: drilldown AUTO mode undefined** — Added AUTO mode definition with parallel Task agents per block and consolidated skeptic review
- **concept-dev: source_tracker --source-type ambiguous** — Renamed to `--needed-source-type` with backward-compatible alias

## [1.0.0] - 2026-01-28

### Added

- **16 Skills** organized into 5 categories:
  - **Root Cause Analysis & Quality (8)**:
    - `rcca-master` - Master orchestrator for root cause analysis workflows
    - `problem-definition` - Structured problem definition using 5W2H framework
    - `five-whys-analysis` - Iterative root cause discovery
    - `fishbone-diagram` - Ishikawa cause-and-effect analysis
    - `pareto-analysis` - 80/20 prioritization of causes
    - `kepner-tregoe-analysis` - Systematic problem analysis and decision making
    - `fault-tree-analysis` - Top-down failure analysis with boolean logic
    - `fmea-analysis` - Failure Mode and Effects Analysis with RPN scoring
  - **Specification & Documentation (4)**:
    - `speckit-generator` - Generate specification documents from templates
    - `specification-refiner` - Refine and improve specifications
    - `documentation-architect` - Design documentation structure
    - `research-opportunity-investigator` - Identify research opportunities
  - **Decision Support (1)**:
    - `trade-study-analysis` - Multi-criteria decision analysis
  - **Output & Streaming (2)**:
    - `streaming-output` - Structured streaming output utilities
    - `streaming-output-mcp` - MCP-based streaming output
  - **Development (1)**:
    - `plugin-creator` - Create new Claude Code plugins

- **2 MCP Servers**:
  - `session-memory` - Persistent session memory with checkpoints and semantic search
  - `knowledge-mcp` - Semantic search over systems engineering standards (IEEE, INCOSE, ISO)

- Plugin packaging tools in `tools/`:
  - `init_plugin.py` - Initialize new plugins from templates
  - `package_plugins.py` - Package plugins for distribution
  - `create_toc.py` - Generate table of contents

- Comprehensive README documentation

[1.2.0]: https://github.com/dunnock/claude-plugins/releases/tag/v1.2.0
[1.1.0]: https://github.com/dunnock/claude-plugins/releases/tag/v1.1.0
[1.0.0]: https://github.com/dunnock/claude-plugins/releases/tag/v1.0.0
