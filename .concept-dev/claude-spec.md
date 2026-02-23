# requirements-dev Plugin — Synthesized Specification

## Overview

Build a Claude Code plugin called **requirements-dev** that transforms concept-dev outputs into INCOSE-compliant requirements through a guided, block-centric process. The plugin covers all 3 maturation phases: Foundation (core pipeline), Validation & Research (set validation, cross-cutting sweep, TPM researcher), and Decomposition (subsystem decomposer, re-entrant core).

## Source Material

- **Concept Document:** `.concept-dev/CONCEPT-DOCUMENT.md` — 46K comprehensive engineering concept
- **Solution Landscape:** `.concept-dev/SOLUTION-LANDSCAPE.md` — 34 approaches across 62 sub-functions
- **Research:** `.concept-dev/claude-research.md` — codebase patterns + web research on INCOSE automation, LLM precision, traceability schemas
- **Interview:** `.concept-dev/claude-interview.md` — 9 design decisions resolved

## Key Design Decisions (from Interview)

1. **Scope:** All 3 maturation phases, implemented incrementally
2. **Quality Checker:** Hybrid — regex/NLP for 21 syntactic rules + LLM with CoT for 9 semantic rules
3. **Attribute UX:** Minimal + expand — require statement + type + priority; offer full 13 attributes on demand
4. **Workspace:** Separate `.requirements-dev/` directory; concept-dev artifacts are read-only inputs
5. **Spec format:** Block-centric custom (organized by blocks, then types within blocks)
6. **Standalone support:** Concept-dev preferred with manual fallback for partial/missing artifacts
7. **TPM Research:** Same tiered tool approach as concept-dev (WebSearch always, crawl4ai/MCP optional)
8. **Export:** JSON registries + ReqIF XML export (using `reqif` Python package)

## Functional Architecture (11 Blocks)

### Phase 1: Foundation

**Block 1: Concept Ingestion**
- Read `.concept-dev/` artifacts (CONCEPT-DOCUMENT.md, BLACKBOX.md, SOLUTION-LANDSCAPE.md, source_registry.json, assumption_registry.json, state.json)
- Validate concept-dev phase gates passed (or gracefully degrade for partial artifacts)
- Extract needs candidates from capabilities, ConOps scenarios, and block behaviors
- Preserve source/assumption IDs for traceability linking
- Manual fallback: prompt users to define blocks and needs candidates manually
- Output: block-organized needs candidates with extraction summary

**Block 2: Needs Formalization**
- Transform needs candidates into INCOSE-compliant need statements
- Pattern: [Stakeholder] needs [capability] [qualifier]
- Validate each need is solution-free (expectations, not obligations)
- User review and approval per block
- Register in `needs_registry.json` with unique IDs (NEED-xxx)
- Gate: all needs approved before proceeding to requirements

**Block 3: Block Requirements Engine**
- For each block, guide through types in order: functional → performance → interface/API → constraint → quality
- Seed draft statements from approved needs and block context
- Minimal attribute collection: statement + type + priority (3 required)
- Expandable to full 13 INCOSE attributes on demand
- Track TBD/TBR items with NASA four-field closure (estimate, resolution path, owner, deadline)
- Trigger Quality Checker per requirement before registration

**Block 4: Quality Checker**
- **Tier 1 (Deterministic):** Regex/NLP checks for 21 fully automatable INCOSE rules
  - Vague terms (R7), escape clauses (R8), open-ended clauses (R9), combinators (R19), pronouns (R24), absolutes (R26), passive voice (R2), etc.
  - Implementation: Python with `re` module, word lists from INCOSE GtWR v4 summary
  - Passive voice detection: spaCy or simpler heuristic (was/were/been + past participle pattern)
- **Tier 2 (LLM-Assisted):** Chain-of-Thought prompting for 9 partially automatable rules
  - Solution-free (R31), measurable performance (R34), single thought (R18), etc.
  - 12-20 validated examples with rationales for few-shot context
  - Explicit confidence notes on all semantic flags
  - Human review required before registration
- Require violation resolution (with suggested rewrites) before requirement registration

**Block 5: V&V Planner**
- Attach verification method, success criteria, and responsible party to each requirement
- Suggest V&V methods based on type: performance → load test, interface → integration test, functional → unit/system test
- Populate INCOSE attributes A6-A9
- Every registered requirement has V&V attributes populated

**Block 6: Traceability Engine**
- Assign unique IDs: NEED-xxx, REQ-xxx
- Bidirectional links: need ↔ requirement ↔ V&V method
- Cross-references to concept-dev source/assumption registries (SRC-xxx, ASN-xxx)
- JSON registries: `needs_registry.json`, `requirements_registry.json`, `traceability_registry.json`
- Schema: `(source, target, type, role)` tuples, inverse computed at query time
- Query support: "which requirements trace to NEED-003?", "which needs have no requirements?"
- Atomic writes (temp-file-then-rename)
- ReqIF XML export via `reqif` Python package

**Block 7: Deliverable Assembly**
- REQUIREMENTS-SPECIFICATION.md — block-centric custom format (organized by block, then type)
- TRACEABILITY-MATRIX.md — concept-dev source → need → requirement → V&V
- VERIFICATION-MATRIX.md — requirements × method × criteria
- JSON registries for machine consumption
- ReqIF XML export
- User approval per deliverable section

### Phase 2: Validation & Research

**Block 8: Set Validator**
- After each block completes, validate cross-block consistency
- Check every block-to-block relationship has at least one interface requirement
- Detect duplicates and overlaps (n-gram cosine similarity — proven, lower complexity)
- Check terminology consistency
- Report uncovered needs
- Feed gaps back to Block Requirements Engine

**Block 9: Cross-Cutting Sweep**
- After all blocks complete, validate full set for system-level concerns
- Prompt for categories: security, reliability, availability, scalability, maintainability, data integrity, logging/observability
- Check INCOSE set characteristics C10-C15
- Skeptic review (opus agent) to verify coverage claims
- Add system-level requirements through standard pipeline

**Block 10: TPM Researcher**
- Triggered when Block Requirements Engine encounters a measurable requirement
- Tiered research tools (same as concept-dev: WebSearch → crawl4ai → MCP)
- Search for comparable systems and published benchmarks
- Present results as structured table with sources and consequence descriptions
- User makes final value selection informed by research
- Register sources in source registry

### Phase 3: Decomposition

**Block 11: Subsystem Decomposer**
- Guide functional decomposition per block
- Allocation rationale: which parent requirements allocate to which sub-blocks
- Allocation coverage validation
- Create parent-to-child traces (INCOSE A2)
- Sub-blocks re-enter Requirements Development Core at subsystem level
- Level tracking in state.json to prevent infinite regress
- Gate checks before decomposition (system-level requirements must be baselined)

## Plugin Structure (following concept-dev pattern)

```
requirements-dev/
├── .claude-plugin/plugin.json
├── SKILL.md
├── README.md
├── HOW_TO_USE.md
├── commands/
│   ├── reqdev.init.md           # Initialize session, ingest concept-dev
│   ├── reqdev.needs.md          # Needs formalization
│   ├── reqdev.requirements.md   # Block requirements engine (main workflow)
│   ├── reqdev.validate.md       # Set validation + cross-cutting sweep
│   ├── reqdev.research.md       # TPM research on demand
│   ├── reqdev.deliver.md        # Deliverable assembly
│   ├── reqdev.decompose.md      # Subsystem decomposition
│   ├── reqdev.status.md         # Session dashboard
│   └── reqdev.resume.md         # Resume interrupted session
├── agents/
│   ├── quality-checker.md       # INCOSE rule checking (sonnet)
│   ├── tpm-researcher.md        # Performance benchmark research (sonnet)
│   ├── skeptic.md               # Coverage/feasibility verification (opus)
│   └── document-writer.md       # Deliverable generation (sonnet)
├── scripts/
│   ├── init_session.py          # Workspace + state init
│   ├── update_state.py          # Atomic state management
│   ├── ingest_concept.py        # Parse concept-dev artifacts
│   ├── needs_tracker.py         # Needs registry CRUD
│   ├── requirement_tracker.py   # Requirements registry CRUD
│   ├── traceability.py          # Link management + queries
│   ├── quality_rules.py         # Syntactic rule engine (21 rules)
│   ├── check_tools.py           # Research tool detection (from concept-dev)
│   ├── reqif_export.py          # ReqIF XML generation
│   └── source_tracker.py        # Adapted from concept-dev
├── templates/
│   ├── state.json
│   ├── requirements-specification.md
│   ├── traceability-matrix.md
│   └── verification-matrix.md
├── references/
│   ├── incose-rules.md          # Rule definitions + word lists
│   ├── attribute-schema.md      # 13 INCOSE attributes definition
│   ├── type-guide.md            # Requirement type definitions + examples
│   ├── vv-methods.md            # V&V method selection guide
│   └── decomposition-guide.md   # Subsystem decomposition patterns
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       └── update-state-on-write.sh
└── data/
    ├── vague_terms.json         # R7 word list
    ├── escape_clauses.json      # R8 word list
    ├── absolutes.json           # R26 word list
    └── pronouns.json            # R24 word list
```

## State Management

```json
{
  "session": { "id", "created_at", "last_updated", "project_name" },
  "concept_dev": {
    "path": ".concept-dev/",
    "ingested": false,
    "blocks_found": 0,
    "needs_candidates": 0,
    "sources_available": 0,
    "manual_mode": false
  },
  "current_phase": null,
  "current_block": null,
  "current_type": null,
  "phases": {
    "init": { "status", "gate_passed", "artifact" },
    "needs": { "status", "gate_passed", "needs_total", "needs_approved", "needs_deferred" },
    "requirements": {
      "status", "gate_passed",
      "blocks": {
        "<block-id>": {
          "status": "not_started|in_progress|completed",
          "types_completed": [],
          "requirements_count": 0
        }
      }
    },
    "validation": { "status", "gate_passed", "interface_gaps", "duplicates_found" },
    "cross_cutting": { "status", "gate_passed", "system_reqs_added" },
    "deliverables": { "status", "gate_passed", "artifacts": [] },
    "decomposition": {
      "status",
      "levels": { "0": { "blocks_baselined": true }, "1": { "blocks": {} } }
    }
  },
  "tools": { "detected_at", "available", "tier1", "tier2", "tier3" },
  "requirements": {
    "total": 0,
    "by_type": { "functional", "performance", "interface", "constraint", "quality" },
    "by_status": { "draft", "registered", "baselined" },
    "tbd_count": 0, "tbr_count": 0
  },
  "needs": { "total", "approved", "deferred" },
  "traceability": { "coverage_percent", "orphan_needs", "orphan_requirements" },
  "quality_checks": { "total_checked", "passed", "failed", "pending_review" }
}
```

## Registry Schemas

### needs_registry.json
```json
{
  "metadata": { "created", "last_modified", "version" },
  "needs": [{
    "id": "NEED-001",
    "statement": "[Stakeholder] needs [capability] [qualifier]",
    "stakeholder": "end-user",
    "source_block": "block-task-engine",
    "source_artifacts": ["CONCEPT-DOCUMENT.md:Section 4"],
    "concept_dev_refs": { "sources": ["SRC-012"], "assumptions": ["ASN-003"] },
    "status": "approved|deferred|rejected",
    "rationale": "...",
    "registered_at": "2026-02-20T10:00:00"
  }]
}
```

### requirements_registry.json
```json
{
  "metadata": { "created", "last_modified", "version" },
  "requirements": [{
    "id": "REQ-001",
    "statement": "The [subject] shall [action] [object] [qualifier]",
    "type": "functional|performance|interface|constraint|quality",
    "priority": "high|medium|low",
    "status": "draft|registered|baselined",
    "parent_need": "NEED-001",
    "source_block": "block-task-engine",
    "level": 0,
    "attributes": {
      "A1_uid": "REQ-001",
      "A2_parent_trace": "NEED-001",
      "A3_rationale": "...",
      "A4_priority": "high",
      "A5_risk": "medium",
      "A6_verification_method": "test",
      "A7_success_criteria": "...",
      "A8_responsible_party": "...",
      "A9_vv_level": "system",
      "A10_status": "registered",
      "A11_stability": "stable",
      "A12_source": "CONCEPT-DOCUMENT.md",
      "A13_allocation": null
    },
    "quality_checks": {
      "syntactic": { "passed": true, "violations": [], "checked_at": "..." },
      "semantic": { "passed": true, "flags": [], "confidence": "high", "checked_at": "..." }
    },
    "tbd_tbr": null,
    "registered_at": "2026-02-20T10:00:00"
  }]
}
```

## Key Implementation Constraints

1. **Python scripts use stdlib only** — no pip dependencies for core scripts (except `reqif` for ReqIF export)
2. **Atomic writes** — all registry/state mutations use temp-file-then-rename
3. **Path validation** — `_validate_path()` on all CLI file arguments
4. **HTML escaping** — `html.escape()` on all user content in generated documents
5. **Metered questioning** — 3-4 questions per interaction round, then checkpoint
6. **Gate discipline** — user approval required before phase advancement
7. **Session resume** — state.json captures exact position for mid-session recovery
8. **Source grounding** — quality checker word lists sourced from INCOSE GtWR v4 summary sheet

## Assumptions Carried Forward from Concept-Dev

- A-001: LLM can reliably automate ~24 syntactic rules; semantic rules need human review (HIGH impact)
- A-002: Concept-dev outputs provide sufficient starting material (HIGH impact)
- A-005: Solo developers will accept INCOSE-level rigor if guided (HIGH impact)
- A-010: Re-entrant core operates at multiple levels without modification (HIGH impact)
