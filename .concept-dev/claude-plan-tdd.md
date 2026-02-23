# TDD Plan: requirements-dev Plugin

## Testing Approach

**Framework:** pytest with fixtures (matching existing codebase patterns)
**Conventions:** Test files in `tests/` directory, named `test_<module>.py`
**Fixtures:** Shared fixtures in `conftest.py` with env var sourcing
**Mocking:** Mock all LLM calls; no external API dependencies in tests
**Coverage target:** High coverage on deterministic scripts (quality_rules.py, trackers, traceability); smoke tests for agent-driven flows

---

## 3. Phase 1: Foundation

### 3.1 Concept Ingestion (`ingest_concept.py`, `init_session.py`)

**File: `tests/test_ingest_concept.py`**

```python
# Test: ingest() with valid concept-dev directory returns source_refs and assumption_refs
# Test: ingest() with valid directory reports correct gate_status (all gates passed)
# Test: ingest() with missing source_registry.json returns empty source_refs, no error
# Test: ingest() with missing assumption_registry.json returns empty assumption_refs, no error
# Test: ingest() with state.json showing failed gates reports gate_status warnings
# Test: ingest() with completely missing .concept-dev/ returns graceful fallback dict
# Test: ingest() validates path (rejects .. traversal)
# Test: ingest() output JSON contains artifact_inventory listing which files exist
```

**File: `tests/test_init_session.py`**

```python
# Test: init creates .requirements-dev/ directory
# Test: init creates state.json from template with session_id and schema_version
# Test: init state.json has correct initial counts (all zeros)
# Test: init state.json has correct initial progress (current_block=null, current_type_pass=null)
# Test: init with existing .requirements-dev/ does not overwrite (resume scenario)
# Test: init validates path argument
```

### 3.2 Needs Formalization (`needs_tracker.py`)

**File: `tests/test_needs_tracker.py`**

```python
# Test: add creates NEED-001 with correct fields (statement, stakeholder, source_block)
# Test: add auto-increments ID (NEED-001, NEED-002, NEED-003)
# Test: add validates uniqueness (same statement + stakeholder rejected)
# Test: add syncs needs_total count to state.json
# Test: update modifies statement and preserves other fields
# Test: defer sets status="deferred" and requires rationale
# Test: defer without rationale raises error
# Test: reject sets status="rejected" and requires rationale
# Test: list returns all needs for a given block
# Test: list with status filter returns only matching needs
# Test: query by concept_dev_refs returns needs linked to specific SRC-xxx
# Test: export produces correct JSON structure
# Test: atomic write: registry not corrupted if write is interrupted (temp file exists)
# Test: schema_version field present in registry output
```

### 3.3 Block Requirements Engine (`requirement_tracker.py`)

**File: `tests/test_requirement_tracker.py`**

```python
# Test: add creates REQ-001 with minimal fields (statement, type, priority)
# Test: add auto-increments ID across multiple additions
# Test: add validates type is one of: functional, performance, interface, constraint, quality
# Test: add validates priority is one of: high, medium, low
# Test: register transitions status from "draft" to "registered"
# Test: register requires parent_need to be set
# Test: baseline transitions status from "registered" to "baselined"
# Test: baseline on non-registered requirement raises error
# Test: withdraw sets status="withdrawn" with rationale
# Test: withdraw without rationale raises error
# Test: withdraw preserves requirement in registry (not deleted)
# Test: list excludes withdrawn requirements from default output
# Test: list with include_withdrawn=True shows all requirements
# Test: query by type returns correct subset
# Test: query by source_block returns correct subset
# Test: query by level returns correct subset (system=0, subsystem=1+)
# Test: update modifies attributes dict without overwriting other fields
# Test: export produces correct JSON structure
# Test: sync-counts updates state.json with correct registered/baselined/withdrawn counts
```

### 3.4 Quality Checker (`quality_rules.py`)

**File: `tests/test_quality_rules.py`**

Golden tests — known-good and known-bad requirement statements with expected violations:

```python
# --- Vague terms (R7) ---
# Test: "The system shall provide appropriate error handling" → flags "appropriate"
# Test: "The system shall provide structured error responses" → no R7 violation
# Test: "Several modules shall be loaded" → flags "several"

# --- Escape clauses (R8) ---
# Test: "The system shall, where possible, cache results" → flags "where possible"
# Test: "The system shall cache all query results" → no R8 violation

# --- Open-ended clauses (R9) ---
# Test: "The system shall support formats including but not limited to JSON" → flags clause
# Test: "The system shall support JSON, XML, and CSV formats" → no R9 violation

# --- Combinators (R19) ---
# Test: "The system shall log errors and shall send alerts" → flags (shall...and...shall)
# Test: "The system shall log errors and warnings" → no R19 violation (compound subject OK)
# Test: "The system shall respond or shall queue the request" → flags (shall...or...shall)

# --- Pronouns (R24) ---
# Test: "It shall respond within 200ms" → flags "it"
# Test: "The API Gateway shall respond within 200ms" → no R24 violation

# --- Absolutes (R26) ---
# Test: "The system shall always be available" → flags "always"
# Test: "The system shall maintain 99.9% availability" → no R26 violation

# --- Passive voice (R2) ---
# Test: "Errors shall be logged by the system" → flags passive (be...logged)
# Test: "The system shall log errors" → no R2 violation
# Test: "The indicator shall be green when ready" → no R2 violation (whitelist: "green")
# Test: "The port shall be open for connections" → no R2 violation (whitelist: "open")

# --- Purpose phrases (R20) ---
# Test: "The system shall cache results in order to improve latency" → flags "in order to"

# --- Parentheses (R21) ---
# Test: "The system shall return status codes (200, 404, 500)" → flags parentheses

# --- Logical and/or (R15, R17) ---
# Test: "The system shall accept JSON and/or XML" → flags "and/or"

# --- Negatives (R16) ---
# Test: "The system shall not expose internal errors" → flags "not"

# --- Superfluous infinitives (R10) ---
# Test: "The system shall be able to process 1000 requests" → flags "be able to"

# --- Temporal dependencies (R35) ---
# Test: "The cache shall be invalidated before serving new data" → flags "before"

# --- Universal quantifiers (R32) ---
# Test: "Every endpoint shall require authentication" → flags "every"

# --- CLI interface ---
# Test: check subcommand returns JSON array of violations
# Test: check-all with registry file processes all requirements
# Test: rules subcommand lists all available rules with IDs
# Test: check with clean requirement returns empty violations array
```

### 3.5 V&V Planner

No separate script to test — V&V planning is conversational flow within the `/reqdev:requirements` command. Testing is via integration tests (see below).

### 3.6 Traceability Engine (`traceability.py`)

**File: `tests/test_traceability.py`**

```python
# --- Link creation ---
# Test: link(REQ-001, NEED-001, "derives_from", "requirement") creates valid link
# Test: link validates source_id exists in requirements registry
# Test: link validates target_id exists in needs registry
# Test: link with non-existent source raises referential integrity error
# Test: link with non-existent target raises referential integrity error
# Test: link creates conflicts_with link type with resolution_status field

# --- Query ---
# Test: query(REQ-001, "forward") returns all forward links
# Test: query(NEED-001, "backward") returns all requirements deriving from this need
# Test: query(REQ-001, "both") returns forward and backward links
# Test: query on entity with no links returns empty list

# --- Coverage ---
# Test: coverage_report() returns percentage of needs with at least one requirement
# Test: coverage_report() with full coverage returns 100%
# Test: coverage_report() with partial coverage returns correct percentage
# Test: coverage_report() excludes withdrawn requirements

# --- Orphan detection ---
# Test: orphan_check() finds needs with no derived requirements
# Test: orphan_check() finds requirements with no parent need
# Test: orphan_check() with no orphans returns empty lists

# --- Atomic writes ---
# Test: registry not corrupted on interrupted write
# Test: schema_version present in output
```

### 3.7 Deliverable Assembly (`reqif_export.py`)

**File: `tests/test_reqif_export.py`**

```python
# Test: export_reqif generates valid XML structure
# Test: export maps each requirement to a SPEC-OBJECT
# Test: export maps traceability links to SPEC-RELATIONS
# Test: export maps requirement types to SPEC-TYPES
# Test: export handles empty requirements registry (produces minimal valid ReqIF)
# Test: export with missing reqif package prints install message and exits 0
# Test: export escapes XML special characters in requirement statements
```

### State Management (`update_state.py`)

**File: `tests/test_update_state.py`**

```python
# Test: set-phase updates current_phase
# Test: pass-gate sets gate to true
# Test: pass-gate on already-passed gate is idempotent
# Test: check-gate returns 0 when gate passed, 1 when not
# Test: set-artifact stores path under artifacts
# Test: update with dotted path (e.g., "counts.needs_total") updates nested field
# Test: sync-counts reads registries and updates all count fields
# Test: show returns human-readable summary
# Test: atomic write on all mutations
```

---

## 4. Phase 2: Validation & Research

### 4.1 Set Validator

**File: `tests/test_set_validator.py`**

```python
# --- Interface coverage ---
# Test: validates all block relationships have interface requirements (pass)
# Test: flags block relationships missing interface requirements (fail)
# Test: handles blocks with no relationships (skip)

# --- Duplicate detection ---
# Test: identical requirements flagged as duplicates (similarity 1.0)
# Test: near-duplicate requirements flagged (above threshold)
# Test: different requirements not flagged (below threshold)
# Test: requirements sharing only "The system shall" prefix not flagged
# Test: word-level n-gram computation is correct for sample sentences

# --- Terminology consistency ---
# Test: flags "user" vs "end-user" vs "client" across blocks
# Test: consistent terminology produces no flags

# --- Uncovered needs ---
# Test: need with no derived requirements flagged
# Test: need with derived requirement not flagged
# Test: deferred needs excluded from coverage check

# --- TBD/TBR report ---
# Test: lists all open TBD items with closure fields
# Test: resolved TBD items excluded from report
```

### 4.2 Cross-Cutting Sweep

Cross-cutting sweep is primarily conversational (command-driven). Tests focus on the INCOSE C10-C15 checks:

```python
# Test: C10 completeness check — all needs traced to requirements
# Test: C14 validatability check — all requirements have V&V methods
# Test: C15 correctness check — all requirements derive from approved needs
```

### 4.3 TPM Researcher

Agent-driven — no unit tests. Smoke test that agent prompt includes correct context.

---

## 5. Phase 3: Decomposition

### 5.1 Subsystem Decomposer

**File: `tests/test_decomposition.py`**

```python
# Test: decompose requires block status "baselined"
# Test: decompose on non-baselined block raises error
# Test: allocation creates parent_of traces for each parent requirement
# Test: allocation coverage validation: flags requirements not allocated to any sub-block
# Test: allocation coverage validation: passes when all requirements allocated
# Test: sub-blocks registered with level=1 in state.json
# Test: max_level=3 prevents decomposition beyond level 3
# Test: decomposition state tracks parent_block and sub_blocks correctly
```

---

## Integration Tests

**File: `tests/test_integration.py`**

```python
# --- Full pipeline (needs → requirements → V&V → traceability) ---
# Test: create need → derive requirement → quality check → register → create trace → verify coverage
# Test: pipeline with quality violation → resolve → re-check → register
# Test: pipeline with TBD value → register with TBD tracking

# --- Resume flow ---
# Test: interrupt after need registration → resume → state shows correct position
# Test: interrupt mid-type-pass → resume → state shows current_block and current_type_pass
# Test: requirements_in_draft preserved across interruption

# --- Deliverable generation ---
# Test: generate specification with 3 blocks, 10 requirements → correct markdown structure
# Test: generate traceability matrix → all links present
# Test: generate verification matrix → all requirements have V&V entries
# Test: baselining after delivery → all requirements status="baselined"

# --- Withdrawal ---
# Test: withdraw requirement → excluded from coverage → preserved in registry
# Test: withdraw requirement → deliverable regeneration excludes it
```
