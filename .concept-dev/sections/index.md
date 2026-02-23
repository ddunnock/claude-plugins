<!-- PROJECT_CONFIG
runtime: python-uv
test_command: uv run pytest
END_PROJECT_CONFIG -->

<!-- SECTION_MANIFEST
section-01-plugin-scaffolding
section-02-state-management
section-03-concept-ingestion
section-04-needs-tracker
section-05-quality-checker
section-06-requirements-engine
section-07-requirements-command
section-08-status-resume
section-09-deliverables
section-10-validation-sweep
section-11-tpm-research
section-12-decomposition
END_MANIFEST -->

# Implementation Sections Index

## Dependency Graph

| Section | Depends On | Blocks | Parallelizable |
|---------|------------|--------|----------------|
| section-01-plugin-scaffolding | - | all | Yes |
| section-02-state-management | 01 | 03, 04, 05, 08 | No |
| section-03-concept-ingestion | 02 | 07 | Yes |
| section-04-needs-tracker | 02 | 06 | Yes |
| section-05-quality-checker | 02 | 06 | Yes |
| section-06-requirements-engine | 04, 05 | 07 | No |
| section-07-requirements-command | 03, 06 | 09 | No |
| section-08-status-resume | 02 | - | Yes |
| section-09-deliverables | 07 | 10, 11 | No |
| section-10-validation-sweep | 09 | 12 | Yes |
| section-11-tpm-research | 09 | 12 | Yes |
| section-12-decomposition | 10 | - | No |

## Execution Order

1. section-01-plugin-scaffolding (no dependencies)
2. section-02-state-management (after 01)
3. section-03-concept-ingestion, section-04-needs-tracker, section-05-quality-checker (parallel after 02)
4. section-06-requirements-engine (after 04 AND 05)
5. section-07-requirements-command (after 03 AND 06), section-08-status-resume (after 02, parallel with 07)
6. section-09-deliverables (after 07)
7. section-10-validation-sweep, section-11-tpm-research (parallel after 09)
8. section-12-decomposition (after 10)

## Section Summaries

### section-01-plugin-scaffolding
Plugin directory structure, plugin.json manifest, SKILL.md, README.md, HOW_TO_USE.md. Data files (vague_terms.json, escape_clauses.json, absolutes.json, pronouns.json). Reference document stubs (incose-rules.md, attribute-schema.md, type-guide.md, vv-methods.md, decomposition-guide.md). Template files (requirements-specification.md, traceability-matrix.md, verification-matrix.md). Hook configuration (hooks.json, update-state-on-write.sh).

Plan sections: 2 (Architecture Overview), 9 (Hooks), 10 (Data Files), 11 (Reference Documents), 12 (Security & Safety)
TDD: No tests — scaffolding only

### section-02-state-management
init_session.py (workspace creation, state.json from template, session ID generation). update_state.py (phase management, gate passing, artifact tracking, counter sync, atomic writes). state.json template with schema_version, progress tracking (current_block, current_type_pass, requirements_in_draft).

Plan sections: 3.1 (init_session.py portion), 6.1 (State Management)
TDD: tests/test_init_session.py, tests/test_update_state.py

### section-03-concept-ingestion
ingest_concept.py (JSON registry parsing for source_registry.json, assumption_registry.json, state.json validation). /reqdev:init command prompt (LLM-assisted extraction from BLACKBOX.md, CONCEPT-DOCUMENT.md). Manual mode fallback interaction pattern. check_tools.py (research tool availability detection).

Plan sections: 3.1 (Concept Ingestion), 6.5 (Concept Ingestion detail), 7 (/reqdev:init command)
TDD: tests/test_ingest_concept.py

### section-04-needs-tracker
needs_tracker.py with subcommands (add, update, defer, reject, list, query, export). Need dataclass (NEED-xxx IDs, statement, stakeholder, source_block, concept_dev_refs, status). /reqdev:needs command prompt (INCOSE pattern formalization, batch review, gate checking). Schema_version in registry.

Plan sections: 3.2 (Needs Formalization), 7 (/reqdev:needs command)
TDD: tests/test_needs_tracker.py

### section-05-quality-checker
quality_rules.py (21 deterministic INCOSE rules via regex/string matching). Violation dataclass. CLI interface (check, check-all, rules subcommands). Module interface for agent integration. Rule implementations: vague terms (R7), escape clauses (R8), open-ended (R9), combinators (R19 restricted), pronouns (R24), absolutes (R26), passive voice (R2 with whitelist), purpose phrases (R20), parentheses (R21), and/or (R15/R17), negatives (R16), infinitives (R10), temporal (R35), quantifiers (R32), decimal format (R40), range checking (R33). quality-checker agent (sonnet, 9 semantic rules with CoT).

Plan sections: 3.4 (Quality Checker), 6.2 (Quality Rules Engine), 8 (quality-checker agent)
TDD: tests/test_quality_rules.py (golden tests)

### section-06-requirements-engine
requirement_tracker.py with subcommands (add, update, register, baseline, withdraw, list, query, export). Requirement dataclass (REQ-xxx IDs, statement, type, priority, status, parent_need, level, attributes, quality_checks, tbd_tbr). traceability.py (link, query, coverage_report, orphan_check). Link types (derives_from, verified_by, sources, informed_by, allocated_to, parent_of, conflicts_with). source_tracker.py (adapted from concept-dev). V&V Planner type-to-method mapping.

Plan sections: 3.3 (Block Requirements Engine scripts), 3.5 (V&V Planner), 3.6 (Traceability Engine), 6.4 (Source Tracker)
TDD: tests/test_requirement_tracker.py, tests/test_traceability.py

### section-07-requirements-command
/reqdev:requirements command prompt. Block-by-block, type-guided pass orchestration (functional → performance → interface → constraint → quality). Metered interaction (2-3 requirements per round). Quality check → V&V plan → register → trace flow. Integration of quality_rules.py + quality-checker agent + requirement_tracker.py + traceability.py.

Plan sections: 3.3 (Block Requirements Engine procedure), 7 (/reqdev:requirements command)
TDD: tests/test_integration.py (full pipeline tests)

### section-08-status-resume
/reqdev:status command (dashboard: phase, block progress, counts, coverage, TBD/TBR, pass rate). /reqdev:resume command (read state.json progress section, report exact position including current_block and current_type_pass, handle requirements_in_draft).

Plan sections: 7 (/reqdev:status, /reqdev:resume commands)
TDD: tests/test_integration.py (resume flow tests)

### section-09-deliverables
document-writer agent (sonnet, generates deliverables from registries and templates). /reqdev:deliver command (assembly process: read registries, validate traceability, generate from templates, user approval, baselining). reqif_export.py (ReqIF XML via strictdoc reqif package, graceful ImportError, SPEC-OBJECTS/RELATIONS/TYPES mapping).

Plan sections: 3.7 (Deliverable Assembly), 6.3 (ReqIF Export), 7 (/reqdev:deliver command), 8 (document-writer agent)
TDD: tests/test_reqif_export.py, tests/test_integration.py (deliverable generation, baselining)

### section-10-validation-sweep
Set Validator (interface coverage, word-level n-gram duplicate detection, terminology consistency, uncovered needs, TBD/TBR report). Cross-Cutting Sweep (category checklist, INCOSE C10-C15 validation). /reqdev:validate command. skeptic agent (opus, coverage and feasibility verification).

Plan sections: 4.1 (Set Validator), 4.2 (Cross-Cutting Sweep), 7 (/reqdev:validate), 8 (skeptic agent)
TDD: tests/test_set_validator.py

### section-11-tpm-research
tpm-researcher agent (sonnet, tiered research tools, structured benchmark tables, consequence descriptions). check_tools.py integration (detect WebSearch, crawl4ai, MCP). /reqdev:research command. Source registration for TPM findings.

Plan sections: 4.3 (TPM Researcher), 7 (/reqdev:research command), 8 (tpm-researcher agent)
TDD: Agent-driven, no unit tests; smoke test only

### section-12-decomposition
Subsystem Decomposer (/reqdev:decompose command). Decomposition state tracking (multi-level state.json, max_level=3). Allocation logic (parent requirement → sub-block mapping with rationale). Coverage validation (every parent requirement allocated). Parent-to-child traces (INCOSE A2). Re-entrant pipeline validation (same quality at subsystem level). decomposition-guide.md reference content.

Plan sections: 5.1 (Subsystem Decomposer), 7 (/reqdev:decompose command)
TDD: tests/test_decomposition.py
