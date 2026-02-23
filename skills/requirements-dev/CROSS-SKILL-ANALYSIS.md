# Cross-Skill Analysis: concept-dev ↔ requirements-dev

**Date:** 2026-02-23
**Scope:** Workflow integration, schema consistency, INCOSE alignment
**Skills analyzed:** concept-dev v1.1.5, requirements-dev v1.2.0

---

## Executive Summary

The two skills implement a concept-to-requirements pipeline loosely aligned with INCOSE SE Handbook v4 and GtWR v4. concept-dev covers NASA Phase A (concept exploration through document generation), while requirements-dev covers stakeholder needs formalization through requirements specification, traceability, and V&V planning. The handoff relies on `ingest_concept.py` parsing concept-dev's JSON registries and the `/reqdev:init` command extracting structured data from Markdown artifacts via LLM.

This analysis identified **3 bugs**, **8 structural gaps**, and **5 missed opportunities** across the integration boundary. The most severe finding is a schema mismatch that causes gate status ingestion to silently fail.

---

## SECTION 1: BUGS (Code Defects)

### BUG-1: Gate Status Schema Mismatch (Severity: HIGH)

**File:** `requirements-dev/scripts/ingest_concept.py`, line 102

concept-dev stores gate status as:
```json
{"phases": {"spitball": {"gate_passed": true}, "problem": {"gate_passed": true}, ...}}
```

But `ingest_concept.py` reads:
```python
gates = state_data.get("gates", {})  # line 102 — this key does not exist
```

**Impact:** Gate status is always reported as `all_passed: True` (because `failed` list is empty when `gates` dict is empty) OR `all_passed: True` with no warnings. The intent — warning the user when concept-dev phases weren't completed — never fires.

**Fix:** Read `state_data.get("phases", {})` and extract `gate_passed` from each phase dict:
```python
phases = state_data.get("phases", {})
gates = {name: phase.get("gate_passed", False) for name, phase in phases.items()}
```

### BUG-2: gap_analyzer concept_coverage Reads Wrong Keys (Severity: MEDIUM)

**File:** `requirements-dev/scripts/gap_analyzer.py`, lines 106 and 110

`concept_coverage()` reads:
```python
ingestion.get("sources", [])      # line 106
ingestion.get("assumptions", [])  # line 110
```

But `ingest_concept.py` writes them as:
```python
"source_refs": source_refs,           # line 119
"assumption_refs": assumption_refs,   # line 120
```

**Impact:** `concept_coverage()` always finds zero concept sources and assumptions, so it can never detect uncovered items. The gap analysis for concept-to-needs traceability is non-functional.

**Fix:** Change to `ingestion.get("source_refs", [])` and `ingestion.get("assumption_refs", [])`.

### BUG-3: Gate Status Logic Inversion

**File:** `requirements-dev/scripts/ingest_concept.py`, lines 104–110

Even after fixing the schema path (BUG-1), the logic has an edge case: when `gates` is empty `{}` (no phases found), `failed` is `[]`, so `all_passed` is set to `True` — incorrectly signaling that all gates passed when in reality no gate information was available.

**Fix:** Add `if not gates: gate_status["all_passed"] = False; gate_status["warnings"].append("No gate information found")`.

---

## SECTION 2: SCHEMA INCONSISTENCIES

### SCHEMA-1: Duplicate source_tracker.py With Incompatible Schemas

concept-dev `source_tracker.py` uses a class-based registry with:
- `{metadata, sources: [...], gaps: [...], citations: [...]}`
- Source fields: `id, name, type (11 types), type_description, url, version, date, file_path, relevant_sections, confidence (4 levels), confidence_description, notes, phase, registered_at, citation_count`

requirements-dev `source_tracker.py` uses a function-based registry with:
- `{schema_version, sources: [...]}`
- Source fields: `id, title, url, type (4 types: research|standard|stakeholder|concept_dev), research_context, concept_dev_ref, metadata, registered_at`

**Issues:**
- Field name mismatch: `name` vs `title`
- Type taxonomy mismatch: 11 types → 4 types with no mapping
- Confidence levels exist in concept-dev but not requirements-dev
- Citation tracking exists in concept-dev but not requirements-dev
- Gap tracking exists in concept-dev source_tracker but not requirements-dev's

### SCHEMA-2: Assumption ID Prefix Mismatch

concept-dev generates assumption IDs as `A-001, A-002, ...`
The `ingest_concept.py` correctly reads these and stores them in `assumption_refs`.
Needs tracker accepts arbitrary `concept_dev_refs.assumptions` arrays.

However, requirements-dev has no assumption registry of its own, so there is no way to track whether concept-dev assumptions remain valid as requirements are refined. Assumptions are read-only artifacts after ingestion.

### SCHEMA-3: State.json Structural Divergence

concept-dev state.json uses:
```json
{
  "session": {"id": "...", "created_at": "...", "last_updated": "..."},
  "current_phase": "drilldown",
  "phases": {"spitball": {"status": "completed", "gate_passed": true, "artifact": "..."}, ...},
  "sources": {"total": 12, "by_confidence": {"high": 5, ...}},
  "assumptions": {"total": 8, "pending": 2, "approved": 6}
}
```

requirements-dev state.json uses:
```json
{
  "session_id": "...",
  "schema_version": "1.0.0",
  "created_at": "...",
  "current_phase": "needs",
  "gates": {"init": true, "needs": false, ...},
  "blocks": {...},
  "progress": {...},
  "counts": {...}
}
```

Key differences:
- Session ID: nested in `session.id` vs top-level `session_id`
- Gates: nested per-phase `phases.X.gate_passed` vs flat `gates.X`
- Phase names: spitball/problem/blackbox/drilldown/document vs init/needs/requirements/validate/deliver/decompose
- No shared schema version namespace

---

## SECTION 3: STRUCTURAL GAPS (Missing Handoff Features)

### GAP-1: Concept-Dev Research Gaps Not Carried Forward

concept-dev `source_registry.json` includes a `gaps` array tracking research gaps identified during Phase 4 (Drill-Down) — topics where authoritative sources couldn't be found. These are not ingested by `ingest_concept.py` and are lost at the skill boundary.

**INCOSE relevance:** SE Handbook §4.3 (Stakeholder Needs and Requirements) recommends that known information gaps be documented and tracked as risks. Unresolved research gaps from concept development should inform requirements uncertainty and drive TPM research in requirements-dev Phase 2.

### GAP-2: Concept-Dev Ungrounded Claims Not Carried Forward

concept-dev `assumption_registry.json` includes an `ungrounded_claims` array — statements the skeptic agent flagged as lacking source documentation. These are not ingested. If an ungrounded claim about system feasibility persists into requirements development, requirements may be written against unverified premises.

### GAP-3: Concept-Dev Citations Not Carried Forward

concept-dev tracks `citations` in source_registry.json — specific claim-to-source links showing which claims are grounded. This citation graph is lost during ingestion, removing the evidentiary chain from concept claims to their sources.

### GAP-4: Confidence Levels Lost in Translation

concept-dev sources have 4-level confidence ratings (high/medium/low/ungrounded). requirements-dev source_tracker has no confidence field. When concept-dev sources are "carried forward" (shown in ingestion summary), their confidence context is lost. A requirement derived from an ungrounded concept claim looks the same as one derived from a high-confidence source.

### GAP-5: No Concept-Dev Research Artifact Access

concept-dev produces `research/WR-xxx.md` files with sanitized web content and `research_index.json`. These are not referenced by `ingest_concept.py` and not accessible to requirements-dev's TPM researcher. When requirements-dev needs to research benchmarks for a requirement, it starts from scratch even when concept-dev already crawled relevant sources.

### GAP-6: No Block Relationship Validation Post-Ingestion

`/reqdev:init` extracts blocks from `BLACKBOX.md` including relationships (uses/provides/depends). These relationships are stored in `state.json.blocks.{name}.relationships`. However:
- `/reqdev:needs` never uses relationships to suggest interface-related needs
- `/reqdev:requirements` never validates that interface requirements exist for each relationship
- `/reqdev:gaps` `block_asymmetry()` checks requirement count ratios but doesn't check if interface requirements cover all declared relationships

### GAP-7: No Assumption Lifecycle in Requirements-Dev

concept-dev has a full assumption lifecycle (pending → approved/rejected/modified) with mandatory review gates. requirements-dev reads these assumptions during ingestion but provides no mechanism to:
- Challenge concept assumptions based on requirements analysis findings
- Mark assumptions as invalidated when requirements conflict with them
- Create new assumptions during requirements development
- Report on assumption status in `/reqdev:status`

**INCOSE relevance:** GtWR v4 §5.3 emphasizes that assumptions constraining requirements must be tracked, validated, and revisited as the requirements baseline evolves. INCOSE SE Handbook §4.3.3 notes assumptions should be continuously challenged throughout the SE lifecycle.

### GAP-8: No Backward Traceability to Concept Artifacts

requirements-dev traceability tracks `derives_from` (requirement → need), `verified_by`, `sources`, `informed_by`, `allocated_to`, `parent_of`, `conflicts_with`. There is no link type for "originated from concept-dev artifact" that would let a reviewer trace a requirement back through the need, through the concept ingestion, to the specific section of BLACKBOX.md or CONCEPT-DOCUMENT.md that motivated it.

The `concept_dev_refs` field on needs partially addresses this, but there is no equivalent on requirements. A requirement's only backward link is to its parent need.

---

## SECTION 4: MISSED OPPORTUNITIES

### OPP-1: Shared Source Registry with Cross-Skill Provenance

Both skills maintain independent source registries with incompatible schemas. A shared or interoperable format would allow requirements-dev to inherit concept-dev's research corpus (with confidence, citations, and gaps intact) and extend it with standards and TPM benchmarks. The `concept_dev_ref` field on requirements-dev sources exists for this purpose but is never populated by the ingestion workflow.

**Recommendation:** Define a common source interchange schema with a `provenance` field indicating origin skill, and populate `concept_dev_ref` during ingestion for all carried-forward sources.

### OPP-2: Skeptic Agent Cross-Calibration

Both skills have skeptic agents, but they operate independently. concept-dev's skeptic (Opus) checks for AI slop, ungrounded claims, and indirect prompt injection. requirements-dev's skeptic (also Opus) checks coverage and feasibility. Neither agent sees the other's findings.

**Recommendation:** Pass concept-dev skeptic findings (especially UNVERIFIED_CLAIM and DISPUTED_CLAIM verdicts) to requirements-dev's skeptic as context. Requirements derived from disputed concept claims should receive heightened scrutiny.

### OPP-3: Automatic Needs Candidate Scoring

`/reqdev:init` extracts `needs_candidates` from concept documents, but all candidates are presented equally. Candidates sourced from high-confidence concept-dev claims, approved assumptions, or verified skeptic findings could be ranked higher than candidates from ungrounded sections.

**Recommendation:** During ingestion, annotate each needs_candidate with a provenance score derived from concept-dev confidence levels and skeptic verdicts.

### OPP-4: ConOps-to-Operational-Requirements Traceability

concept-dev Phase 3 produces ConOps scenarios (today-vs-concept workflow narratives). These are rich sources of operational requirements (performance, usability, reliability under operational conditions). Currently, `/reqdev:init` reads CONCEPT-DOCUMENT.md for needs candidates using pattern matching ("The user needs...", "The system shall...") but doesn't specifically mine ConOps scenarios for implicit operational requirements.

**INCOSE relevance:** GtWR v4 §5.2.4 recommends deriving requirements from operational scenarios. SE Handbook §4.3.1 notes that ConOps is a primary source for stakeholder requirements.

### OPP-5: Maturation Path → Priority Mapping

concept-dev's Maturation Path (Foundation → Integration → Advanced phases with risk-reduction milestones) could inform requirements priority assignment. Foundation-phase capabilities should generate high-priority requirements, while Advanced-phase capabilities could be lower priority or deferred.

**Recommendation:** During ingestion, extract maturation phase assignments per capability and carry them as priority hints for needs formalization.

---

## SECTION 5: INCOSE ALIGNMENT ASSESSMENT

### What's Well-Aligned

1. **GtWR v4 need/requirement separation**: concept-dev produces stakeholder expectations, requirements-dev formalizes them into INCOSE-pattern needs and then derives "shall" requirements. This matches GtWR v4 §4 (needs) → §5 (requirements) separation.

2. **Quality rules**: requirements-dev implements 16 deterministic + 9 semantic rules from GtWR v4. Coverage of individual requirement quality is strong.

3. **Traceability structure**: `derives_from`, `verified_by`, `allocated_to` link types map directly to GtWR v4 §6 traceability recommendations.

4. **V&V planning**: requirements-dev includes verification method assignment (analysis/demonstration/inspection/test) per GtWR v4 §7.

5. **Set-level validation**: `set_validator.py` checks INCOSE C10-C15 set characteristics (completeness, consistency, feasibility, etc.).

### Where Alignment Is Weak

1. **Continuous assumption management** (GtWR §5.3): Assumptions are captured in concept-dev but become read-only in requirements-dev. INCOSE requires ongoing assumption tracking through the requirements lifecycle.

2. **Requirements-to-concept backward traceability** (SE Handbook §4.3.7): Current traceability goes forward (concept → need → requirement) but has no formalized backward path. An auditor cannot traverse from a requirement back to the specific concept-dev artifact and section that originated it without manually following `concept_dev_refs` on needs.

3. **Operational concept traceability** (GtWR §5.2.4): ConOps scenarios from concept-dev are available as Markdown but not systematically mined for operational requirements. This is a missed primary requirements source per INCOSE.

4. **Interface requirements from architecture** (SE Handbook §4.3.4): concept-dev produces block relationships (uses/provides/depends) and interface descriptions. requirements-dev ingests these but has no validation that interface requirements exist for each declared relationship.

5. **Assumption-driven risk identification** (SE Handbook §6.3.3): Neither skill produces a formal risk register. High-impact concept assumptions (particularly rejected or modified ones) should feed into project risk tracking, which is outside both skills' scope but should at least be flagged.

---

## SECTION 6: PRIORITIZED RECOMMENDATIONS

| # | Finding | Type | Effort | Priority |
|---|---------|------|--------|----------|
| 1 | Fix BUG-1: gate status schema mismatch | Bug | Small | Critical |
| 2 | Fix BUG-2: gap_analyzer reads wrong keys | Bug | Small | Critical |
| 3 | Fix BUG-3: empty gates logic inversion | Bug | Small | High |
| 4 | GAP-4: Carry confidence levels through ingestion | Gap | Medium | High |
| 5 | GAP-1+2: Ingest concept-dev gaps and ungrounded claims | Gap | Medium | High |
| 6 | GAP-7: Add assumption lifecycle to requirements-dev | Gap | Large | High |
| 7 | SCHEMA-1: Harmonize source_tracker field names | Schema | Medium | Medium |
| 8 | GAP-6: Validate interface requirements against block relationships | Gap | Medium | Medium |
| 9 | OPP-4: Mine ConOps scenarios for operational requirements | Opportunity | Medium | Medium |
| 10 | OPP-2: Pass skeptic findings across skill boundary | Opportunity | Medium | Medium |
| 11 | GAP-3: Carry citation graph through ingestion | Gap | Small | Low |
| 12 | OPP-5: Maturation path → priority hints | Opportunity | Small | Low |
| 13 | GAP-5: Reference concept-dev research artifacts | Gap | Small | Low |
| 14 | OPP-1: Shared source interchange schema | Opportunity | Large | Low |
| 15 | OPP-3: Score needs candidates by provenance | Opportunity | Medium | Low |

---

## Appendix: File-Level Reference

| Finding | concept-dev File | requirements-dev File |
|---------|-----------------|----------------------|
| BUG-1 | scripts/update_state.py (pass_gate, line 69) | scripts/ingest_concept.py (line 102) |
| BUG-2 | — | scripts/gap_analyzer.py (lines 106, 110) |
| BUG-3 | — | scripts/ingest_concept.py (lines 104–110) |
| SCHEMA-1 | scripts/source_tracker.py | scripts/source_tracker.py |
| SCHEMA-2 | scripts/assumption_tracker.py | scripts/needs_tracker.py (concept_dev_refs) |
| GAP-1 | source_registry.json → gaps[] | scripts/ingest_concept.py (not read) |
| GAP-2 | assumption_registry.json → ungrounded_claims[] | scripts/ingest_concept.py (not read) |
| GAP-3 | source_registry.json → citations[] | scripts/ingest_concept.py (not read) |
| GAP-4 | source_tracker.py → confidence field | source_tracker.py (no confidence field) |
| GAP-5 | research/WR-xxx.md, research_index.json | scripts/ingest_concept.py (not referenced) |
| GAP-6 | BLACKBOX.md → block relationships | commands/reqdev.needs.md, reqdev.requirements.md |
| GAP-7 | scripts/assumption_tracker.py (full lifecycle) | — (no assumption tracker) |
| GAP-8 | — | scripts/traceability.py (no concept-origin link type) |
