# Implementation Plan: requirements-dev Plugin

## 1. What We're Building

A Claude Code plugin called **requirements-dev** that transforms concept development artifacts into INCOSE-compliant formal requirements. The plugin implements an AI-assisted requirements development process organized around the functional blocks users defined during concept development, with inline quality checking, verification planning, bidirectional traceability, and ReqIF export.

The plugin has three maturation phases, implemented incrementally:
- **Phase 1 (Foundation):** Concept ingestion, needs formalization, block requirements engine, quality checker, V&V planner, traceability engine, deliverable assembly
- **Phase 2 (Validation & Research):** Set validator, cross-cutting sweep, TPM researcher
- **Phase 3 (Decomposition):** Subsystem decomposer with re-entrant pipeline

### Why This Approach

Solo developers and small teams completing concept development (via concept-dev or equivalent) have no structured follow-on to transform concept artifacts into formal requirements. They jump to implementation, use spec-driven tools that conflate solutions with requirements, or write ad-hoc requirement lists without quality checking, traceability, or verification planning. This plugin bridges that gap with INCOSE-level rigor embedded in a conversational, guided process.

### Key Design Decisions

1. **Hybrid quality checker:** Regex/NLP for 21 deterministic INCOSE rules + LLM with Chain-of-Thought for 9 semantic rules
2. **Minimal attribute UX:** Require only statement + type + priority; full 13 INCOSE attributes available on demand
3. **Separate workspace:** `.requirements-dev/` directory; concept-dev artifacts are read-only inputs
4. **Block-centric deliverables:** Specification organized by functional blocks, then by requirement type within each block
5. **Concept-dev preferred, manual fallback:** Optimized for ingesting concept-dev artifacts but supports manual block/needs definition
6. **JSON + ReqIF export:** Machine-readable JSON registries plus ReqIF XML for interoperability with DOORS/Jama/ReqView

---

## 2. Architecture Overview

### Plugin Structure

```
skills/requirements-dev/
├── .claude-plugin/plugin.json
├── SKILL.md
├── README.md
├── HOW_TO_USE.md
├── commands/
│   ├── reqdev.init.md
│   ├── reqdev.needs.md
│   ├── reqdev.requirements.md
│   ├── reqdev.validate.md
│   ├── reqdev.research.md
│   ├── reqdev.deliver.md
│   ├── reqdev.decompose.md
│   ├── reqdev.status.md
│   └── reqdev.resume.md
├── agents/
│   ├── quality-checker.md
│   ├── tpm-researcher.md
│   ├── skeptic.md
│   └── document-writer.md
├── scripts/
│   ├── init_session.py
│   ├── update_state.py
│   ├── ingest_concept.py
│   ├── needs_tracker.py
│   ├── requirement_tracker.py
│   ├── traceability.py
│   ├── quality_rules.py
│   ├── check_tools.py
│   ├── reqif_export.py
│   └── source_tracker.py
├── templates/
│   ├── state.json
│   ├── requirements-specification.md
│   ├── traceability-matrix.md
│   └── verification-matrix.md
├── references/
│   ├── incose-rules.md
│   ├── attribute-schema.md
│   ├── type-guide.md
│   ├── vv-methods.md
│   └── decomposition-guide.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       └── update-state-on-write.sh
└── data/
    ├── vague_terms.json
    ├── escape_clauses.json
    ├── absolutes.json
    └── pronouns.json
```

### Workspace Structure

The plugin creates and manages a `.requirements-dev/` directory:

```
.requirements-dev/
├── state.json                      # Session state with phase tracking
├── needs_registry.json             # Formalized stakeholder needs
├── requirements_registry.json      # Registered requirements with attributes
├── traceability_registry.json      # Bidirectional links
├── source_registry.json            # Sources referenced during requirements dev
├── REQUIREMENTS-SPECIFICATION.md   # Final deliverable (block-centric)
├── TRACEABILITY-MATRIX.md          # Need → Requirement → V&V chain
├── VERIFICATION-MATRIX.md          # Requirements × method × criteria
└── exports/
    └── requirements.reqif          # ReqIF XML export
```

### Concept-Dev Integration

The plugin reads from `.concept-dev/` as read-only input:
- `CONCEPT-DOCUMENT.md` — block definitions, capabilities, ConOps scenarios
- `BLACKBOX.md` — functional architecture, block relationships, interfaces
- `SOLUTION-LANDSCAPE.md` — solution approaches per block (informs design-input requirements)
- `source_registry.json` — existing sources for traceability linking
- `assumption_registry.json` — assumptions to carry forward
- `state.json` — validate concept-dev gates passed

If concept-dev artifacts are missing or incomplete, the plugin falls back to manual mode: prompts users to define blocks and needs candidates interactively.

---

## 3. Phase 1: Foundation

### 3.1 Concept Ingestion (`/reqdev:init`)

**Purpose:** Initialize the requirements development session by ingesting concept-dev artifacts or setting up manual mode.

**Procedure:**

1. Check for `.concept-dev/` directory and validate artifacts exist
2. If found: parse concept-dev `state.json` to verify gate completion. Extract blocks from `BLACKBOX.md`, capabilities and scenarios from `CONCEPT-DOCUMENT.md`, source/assumption registries for cross-referencing
3. If not found or incomplete: enter manual mode — prompt user to: (a) name each functional block with a 1-2 sentence description, (b) list 3-5 capabilities per block, (c) describe key interfaces between blocks. Present a summary table for user approval before proceeding. This structured interaction prevents improvisation drift across sessions
4. Run `check_tools.py` to detect research tool availability (WebSearch, crawl4ai, MCP servers) for Phase 2 TPM research
5. Create `.requirements-dev/` workspace with initialized `state.json`
6. Display extraction summary: blocks found, needs candidates extracted, sources available

**Ingestion approach — two tiers:**

- **Structured artifacts (Python script):** `ingest_concept.py` parses JSON registries (`source_registry.json`, `assumption_registry.json`, `state.json`) which have reliable, deterministic structure. It validates gate completion, extracts registry IDs, and copies cross-references. This is the script's primary role.

- **Markdown artifacts (LLM-assisted):** The `/reqdev:init` command prompt instructs Claude to read `BLACKBOX.md` and `CONCEPT-DOCUMENT.md` and extract blocks, capabilities, and ConOps scenarios. This is guided extraction, not regex parsing — Claude understands the document structure semantically. The command specifies what to extract (block names, descriptions, relationships, interfaces, capabilities, scenarios) and the output format (structured JSON written to `ingestion.json`).

This split avoids the brittleness of regex-parsing free-form Markdown generated by an LLM. If concept-dev changes its document template, the LLM-assisted extraction adapts naturally; the script only handles stable JSON schemas.

**Script: `ingest_concept.py`**

```python
def ingest(concept_path: str, output_path: str) -> dict:
    """Parse concept-dev JSON registries and validate artifact presence.

    Handles: source_registry.json, assumption_registry.json, state.json.
    Returns dict with source_refs, assumption_refs, gate_status, artifact_inventory.
    Markdown extraction (blocks, needs_candidates) is LLM-assisted via command prompt.
    """
```

**Script: `init_session.py`**

Same pattern as concept-dev: create workspace directory, initialize `state.json` from template, generate session ID, display summary.

**State template (`templates/state.json`):**

```json
{
  "session_id": "",
  "schema_version": "1.0.0",
  "created_at": "",
  "current_phase": "init",
  "gates": { "init": false, "needs": false, "requirements": false, "deliver": false },
  "blocks": {},
  "progress": {
    "current_block": null,
    "current_type_pass": null,
    "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
    "requirements_in_draft": []
  },
  "counts": {
    "needs_total": 0, "needs_approved": 0, "needs_deferred": 0,
    "requirements_total": 0, "requirements_registered": 0, "requirements_baselined": 0, "requirements_withdrawn": 0,
    "tbd_open": 0, "tbr_open": 0
  },
  "traceability": { "links_total": 0, "coverage_pct": 0.0 },
  "decomposition": { "levels": {}, "max_level": 3 },
  "artifacts": {}
}
```

The `progress` section enables granular resume: `current_block` and `current_type_pass` track exactly where the user left off within the type-guided passes. `requirements_in_draft` holds requirement IDs that passed quality checking but were not yet registered when the session was interrupted — these are presented for confirmation on resume rather than lost.

### 3.2 Needs Formalization (`/reqdev:needs`)

**Purpose:** Transform extracted needs candidates into INCOSE-compliant need statements with user review and approval.

**Procedure per block:**

1. Present needs candidates extracted during ingestion (or prompt for manual entry)
2. For each candidate, formalize into INCOSE pattern: `[Stakeholder] needs [capability] [qualifier]`
3. Validate solution-free: needs express expectations ("should"), not obligations ("shall") and not solutions
4. Present batch of 3-5 formalized needs for user review
5. User can: approve, edit, defer (with rationale), or reject each need
6. Register approved needs in `needs_registry.json` via `needs_tracker.py`
7. Gate: user approves the complete needs set for each block before proceeding

**Script: `needs_tracker.py`**

Subcommands: `add`, `update`, `defer`, `reject`, `list`, `query`, `export`

```python
@dataclass
class Need:
    id: str           # NEED-001 format
    statement: str
    stakeholder: str
    source_block: str
    source_artifacts: list[str]
    concept_dev_refs: dict  # {"sources": ["SRC-xxx"], "assumptions": ["ASN-xxx"]}
    status: str       # approved, deferred, rejected
    rationale: str | None
    registered_at: str
```

The tracker assigns sequential IDs (NEED-001, NEED-002...), validates uniqueness, and auto-syncs counts to `state.json`. Atomic writes via temp-file-then-rename. All registry JSON files include a `schema_version` field (initially "1.0.0"); `init_session.py` checks this on resume and logs a warning if the version is older than the current code expects, enabling future migrations.

### 3.3 Block Requirements Engine (`/reqdev:requirements`)

**Purpose:** Guide users through requirement writing for each block, type by type, with inline quality checking and V&V planning.

**Procedure per block:**

For each block in the architecture, iterate through requirement types in order:

1. **Functional requirements** — what the block must do
2. **Performance requirements** — measurable behavior targets
3. **Interface/API requirements** — how the block communicates with other blocks
4. **Constraint requirements** — limitations imposed by environment, standards, or technology
5. **Quality requirements** — non-functional characteristics (reliability, maintainability, etc.)

For each type pass within a block:

1. Seed draft requirement statements from approved needs and block context
2. Present drafts to user for refinement
3. Collect minimal attributes: statement, type, priority
4. Offer to expand to full 13 INCOSE attributes (rationale, risk, stability, source, allocation, etc.)
5. Run Quality Checker on the statement
6. If violations found: present violations with suggested rewrites, iterate until resolved
7. Run V&V Planner to suggest verification method and success criteria
8. Register in `requirements_registry.json` via `requirement_tracker.py`
9. Create traceability links via `traceability.py`

**Metered interaction:** Present 2-3 draft requirements per round. After each round, checkpoint: "3 requirements registered for Block X, functional type. Continue with more functional requirements, or move to performance?"

**Script: `requirement_tracker.py`**

Subcommands: `add`, `update`, `register`, `baseline`, `withdraw`, `list`, `query`, `export`

The `withdraw` subcommand sets `status: "withdrawn"` with a mandatory rationale field. Withdrawn requirements are preserved in registries and traceability for audit trail but excluded from coverage calculations, deliverable generation, and set validation counts.

```python
@dataclass
class Requirement:
    id: str            # REQ-001 format
    statement: str
    type: str          # functional, performance, interface, constraint, quality
    priority: str      # high, medium, low
    status: str        # draft, registered, baselined
    parent_need: str   # NEED-xxx
    source_block: str
    level: int         # 0 = system, 1+ = subsystem
    attributes: dict   # A1-A13 INCOSE attributes (populated on demand)
    quality_checks: dict
    tbd_tbr: dict | None
    registered_at: str
```

### 3.4 Quality Checker

**Purpose:** Apply INCOSE GtWR v4 rules to each requirement statement before registration. Two-tier architecture.

#### Tier 1: Deterministic Checks (`quality_rules.py`)

A standalone Python script that checks requirement text against 21 rules using regex and string matching. No external dependencies — pure stdlib.

**Script: `quality_rules.py`**

```python
def check_requirement(statement: str) -> list[Violation]:
    """Run all deterministic INCOSE checks on a requirement statement.

    Returns list of Violation objects with rule_id, rule_name,
    severity, matched_text, suggestion.
    """
```

The script implements each rule as a function that returns violations:

**Rule groups and their detection approach:**

- **Vague terms (R7):** Match against word list loaded from `data/vague_terms.json`. List includes: "some", "any", "allowable", "several", "many", "a lot of", "a few", "almost always", "very nearly", "nearly", "about", "close to", "adequate", "sufficient", "appropriate", "suitable", "reasonable", "normal", "common", "typical"
- **Escape clauses (R8):** Match against `data/escape_clauses.json`. List includes: "so far as is possible", "as little as possible", "as much as possible", "if it should prove necessary", "where possible", "if practicable", "as appropriate", "as required", "to the extent possible"
- **Open-ended clauses (R9):** Regex for "including but not limited to", "etc.", "and so on", "such as", "for example" (when used to define scope, not illustrate)
- **Combinators (R19):** Restricted to detect combinators between "shall" clauses only (e.g., `shall .+ and .+ shall` or `shall .+ or shall`). Simple compound subjects ("errors and warnings") are legitimate and not flagged. Severity: warning, not error. The LLM tier's R18 (Single thought) check is the authoritative detector for compound requirements
- **Pronouns (R24):** Regex matching `data/pronouns.json`: "it", "they", "them", "this", "that", "these", "those", "which", "its"
- **Absolutes (R26):** Match against `data/absolutes.json`: "always", "never", "every", "all", "none", "no"
- **Passive voice (R2):** Heuristic pattern: forms of "be" (is, are, was, were, been, being, be) followed within 3 words by a word ending in "-ed" or "-en". Severity: warning (not error) due to known false positives. Exemption whitelist for common -en adjectives used predicatively: "open", "green", "broken", "driven", "written", "given" (when not part of passive construction). This catches most passive constructions without requiring spaCy.
- **Purpose phrases (R20):** Regex for "in order to", "so that", "to ensure", "for the purpose of"
- **Parentheses (R21):** Regex `\(.*?\)` in requirement text
- **Logical "and/or" (R15, R17):** Regex for literal "and/or" and oblique "/" used as conjunction
- **Negatives (R16):** Regex `\bnot\b` — flags negative requirements for review
- **Superfluous infinitives (R10):** Regex for "be able to", "be capable of"
- **Temporal dependencies (R35):** Keywords "before", "after", "during", "while", "when" — flags for potential ordering issues
- **Universal quantifiers (R32):** "each", "every", "all", "any" — flags for completeness review
- **Decimal format (R40):** Regex for inconsistent numeric formatting
- **Range checking (R33):** Pattern matching for numeric ranges with missing units or bounds

Each violation includes: rule ID, rule name, severity (error/warning), the matched text, position in statement, and a suggested rewrite.

The script is invocable via CLI:
```bash
python3 quality_rules.py check "The system shall be able to handle any requests appropriately."
# Output: JSON array of violations
```

And importable as a module for the LLM tier to call programmatically.

#### Tier 2: LLM-Assisted Checks (quality-checker agent)

An agent (sonnet model) that evaluates requirements against 9 partially automatable rules using Chain-of-Thought prompting.

**Agent: `agents/quality-checker.md`**

The agent receives:
- The requirement statement
- Its context (block, type, parent need)
- 12-20 validated examples with rationales (stored in `references/incose-rules.md`)

It evaluates:
- **R31 (Solution-free):** Does the requirement prescribe a solution or state a need?
- **R34 (Measurable):** Are performance criteria quantifiable?
- **R18 (Single thought):** Does the statement contain only one requirement?
- **R1 (Structured):** Does it follow "The [subject] shall [action]" pattern?
- **R11 (Separate clauses):** Are conditions properly separated?
- **R22 (Enumeration):** Are lists complete?
- **R27 (Explicit conditions):** Are all conditions stated?
- **R28 (Multiple conditions):** Are nested conditions clear?
- **R36 (Consistent terms):** Is terminology consistent with other requirements?

Each finding includes: rule ID, assessment (pass/flag), confidence (high/medium/low), reasoning, and suggested rewrite if flagged. Only high-confidence flags block registration; medium/low flags are informational and flagged for human review.

#### Quality Check Flow

1. Run Tier 1 (deterministic) — immediate results
2. If Tier 1 passes: run Tier 2 (LLM) via quality-checker agent
3. Present all violations to user with suggested rewrites
4. User resolves each violation (accept rewrite, provide own rewrite, or justify and override)
5. Re-run Tier 1 on rewritten statement to confirm resolution
6. Registration proceeds only when Tier 1 passes and Tier 2 flags are resolved or acknowledged

### 3.5 V&V Planner

**Purpose:** Attach verification method, success criteria, and responsible party to each requirement at creation time.

This runs as part of the Block Requirements Engine flow (not a separate command). After quality checking passes, the skill suggests V&V attributes based on requirement type:

**Type → Default V&V method mapping:**
- Functional → system test / unit test
- Performance → load test / benchmark test
- Interface/API → integration test / contract test
- Constraint → inspection / analysis
- Quality → demonstration / analysis

For each requirement, the skill presents:
1. Suggested verification method (with rationale based on type)
2. Draft success criteria derived from the requirement statement
3. Suggested responsible party (developer, QA, reviewer)

User confirms or modifies. The V&V attributes are stored as INCOSE attributes A6-A9 in the requirement record.

### 3.6 Traceability Engine

**Purpose:** Maintain bidirectional links between all entities and support traceability queries.

**Script: `traceability.py`**

```python
def link(source_id: str, target_id: str, link_type: str, role: str) -> None:
    """Create a traceability link. Validates both IDs exist in their registries."""

def query(entity_id: str, direction: str = "both") -> list[Link]:
    """Find all links for an entity. Direction: forward, backward, or both."""

def coverage_report() -> dict:
    """Compute traceability coverage statistics."""

def orphan_check() -> dict:
    """Find needs with no requirements and requirements with no needs."""
```

**Link types:**
- `derives_from`: REQ-xxx → NEED-xxx (requirement traces to need)
- `verified_by`: REQ-xxx → V&V method reference
- `sources`: REQ-xxx → SRC-xxx (concept-dev source reference)
- `informed_by`: REQ-xxx → ASN-xxx (assumption reference)
- `allocated_to`: REQ-xxx → sub-block (Phase 3, subsystem decomposition)
- `parent_of`: REQ-xxx → REQ-yyy (parent-child requirement relationship)
- `conflicts_with`: REQ-xxx → REQ-yyy (identified conflict, with resolution status and rationale)

Links are stored as `(source, target, type, role)` tuples in `traceability_registry.json`. Inverse traversal is computed at query time — no duplicate storage.

The engine validates referential integrity on every mutation: both source and target IDs must exist in their respective registries. Orphan detection runs on demand and before deliverable generation.

### 3.7 Deliverable Assembly (`/reqdev:deliver`)

**Purpose:** Generate final deliverable documents from registered requirements.

**Deliverables:**

1. **REQUIREMENTS-SPECIFICATION.md** — Block-centric format:
   - For each block: block description, then sections for each requirement type
   - Each requirement shows: ID, statement, priority, V&V method, parent need
   - Full attributes available in JSON registries
   - Template in `templates/requirements-specification.md`

2. **TRACEABILITY-MATRIX.md** — Full chain visualization:
   - Concept-dev source → Need → Requirement → V&V method
   - Highlights orphans and gaps
   - Template in `templates/traceability-matrix.md`

3. **VERIFICATION-MATRIX.md** — Testing reference:
   - All requirements × verification method × success criteria × responsible party
   - Template in `templates/verification-matrix.md`

4. **JSON registries** — Machine-readable exports:
   - `needs_registry.json`, `requirements_registry.json`, `traceability_registry.json`
   - Already maintained during the workflow

5. **ReqIF export** — `exports/requirements.reqif`:
   - Uses `reqif` Python package
   - Maps INCOSE attributes to ReqIF SPEC-TYPES
   - Exports requirements, needs, and traceability links as ReqIF SPEC-OBJECTS and SPEC-RELATIONS

**Script: `reqif_export.py`**

```python
def export_reqif(requirements_path: str, needs_path: str,
                 traceability_path: str, output_path: str) -> None:
    """Generate ReqIF XML from JSON registries.

    Maps requirements to SPEC-OBJECTS, traceability links to SPEC-RELATIONS,
    and requirement types to SPEC-TYPES.
    """
```

This is the only script requiring an external dependency (`reqif` package by strictdoc, pinned to latest stable version). It's invoked only during deliverable generation, not during the core workflow. The script handles `ImportError` gracefully: if `reqif` is not installed, it prints "ReqIF export requires the reqif package. Install with: pip install reqif" and exits with code 0 (other deliverables are unaffected).

**Assembly process:**
1. Read all registries
2. Validate traceability completeness (warn on gaps)
3. Generate each deliverable from templates
4. Present each deliverable section for user review and approval
5. Gate: all deliverables approved before marking phase complete
6. **Baselining:** After all deliverables are approved, transition all registered requirements to `status: "baselined"`. This is the formal baseline — baselined requirements can only be modified through a change request workflow (out of scope for Phase 1, but the status transition enables Phase 3 decomposition which requires baselined parent requirements)

---

## 4. Phase 2: Validation & Research

### 4.1 Set Validator

**Purpose:** After each block's requirements are complete, validate cross-block consistency.

This runs automatically at the end of each block's type passes (within `/reqdev:requirements`) and can also be triggered manually via `/reqdev:validate`.

**Checks:**

1. **Interface coverage:** For every block-to-block relationship defined in `BLACKBOX.md`, verify at least one interface requirement exists. Uses the block relationship map from concept ingestion.

2. **Duplicate detection:** Compare requirement statements across blocks using word-level n-gram cosine similarity (unigrams + bigrams, threshold 0.8 — tunable, will be calibrated during development). Flag potential duplicates for user review. Implementation: stdlib only — compute n-gram frequency vectors and cosine similarity without numpy (pure Python dot product / magnitude). Word-level n-grams are more semantically meaningful than character-level for short requirement statements (typical 10-20 words).

3. **Terminology consistency:** Build a term dictionary from registered requirements. Flag when the same concept uses different terms across blocks (e.g., "user" vs. "end-user" vs. "client").

4. **Uncovered needs:** Query traceability engine for needs with no derived requirements.

5. **TBD/TBR report:** List all unresolved TBD/TBR items with their closure tracking fields.

Validation findings are presented to the user as a prioritized list. Interface gaps feed back to the Block Requirements Engine — the skill prompts the user to write missing interface requirements through the standard pipeline.

### 4.2 Cross-Cutting Sweep

**Purpose:** After all blocks complete, validate the full requirement set for system-level concerns.

**Procedure:**

1. Present cross-cutting category checklist: security, reliability, availability, scalability, maintainability, data integrity, logging/observability. User selects applicable categories.

2. For each selected category, review existing requirements for coverage. Flag blocks with no requirements in that category.

3. Prompt user to write system-level requirements for uncovered categories. These go through the standard pipeline (quality checker, V&V planner, traceability).

4. Run INCOSE set characteristics C10-C15 validation:
   - **C10 Completeness:** All needs traced to at least one requirement
   - **C11 Consistency:** No conflicting requirements (user-reviewed)
   - **C12 Feasibility:** Skeptic review on feasibility claims
   - **C13 Comprehensibility:** Terminology consistency check
   - **C14 Validatability:** All requirements have V&V methods
   - **C15 Correctness:** Requirements derive from approved needs

5. Launch skeptic agent (opus model) to verify coverage claims. The skeptic reviews: "All OWASP Top 10 categories covered" → actually checks which categories have requirements. Reports: verified, unverified, disputed, needs_user_input.

**Agent: `agents/skeptic.md`**

Same pattern as concept-dev's skeptic agent. Receives the full requirement set and cross-cutting findings. Reviews feasibility and coverage claims. Uses opus model for rigor.

### 4.3 TPM Researcher

**Purpose:** Provide research-grounded baselines for measurable requirements.

**Trigger:** When the Block Requirements Engine encounters a performance or measurable requirement, the skill asks: "Would you like to research benchmarks for this requirement?"

**Agent: `agents/tpm-researcher.md`** (sonnet model)

The agent:
1. Searches for comparable systems and published benchmarks using tiered research tools (WebSearch always; crawl4ai and MCP if available, per check_tools.py)
2. Presents results as a structured table: comparable system, metric, value, source
3. Includes consequence/effect descriptions at different value ranges
4. User makes the final value selection

Sources found during TPM research are registered in `source_registry.json` for traceability.

---

## 5. Phase 3: Decomposition

### 5.1 Subsystem Decomposer (`/reqdev:decompose`)

**Purpose:** Guide functional decomposition of system-level blocks into sub-blocks that re-enter the requirements pipeline.

**Prerequisites:** System-level requirements for the target block must be baselined (status: "baselined" in registry).

**Procedure:**

1. Select block to decompose
2. Guide user through functional decomposition: identify sub-functions that together fulfill the block's responsibilities
3. For each sub-block: name, description, parent block reference
4. Allocation: for each parent requirement, user specifies which sub-block(s) it allocates to, with rationale
5. Validate allocation coverage: every parent requirement allocated to at least one sub-block
6. Create parent-to-child traces (INCOSE attribute A2)
7. Register sub-blocks in state.json with `level: 1` (or deeper)
8. Sub-blocks become new "blocks" — user runs `/reqdev:requirements` to develop sub-block requirements through the same pipeline

**State tracking for decomposition levels:**

```json
"decomposition": {
  "levels": {
    "0": { "blocks_baselined": true },
    "1": {
      "parent_block": "block-dependency-tracker",
      "sub_blocks": ["graph-engine", "cycle-detector", "critical-path-calc"],
      "allocation_coverage": 1.0
    }
  },
  "max_level": 3
}
```

The `max_level` field (default 3) prevents infinite regress. The skill warns when approaching the limit and requires explicit user override to go deeper.

**Re-entrant behavior:** The Block Requirements Engine, Quality Checker, V&V Planner, and Traceability Engine operate identically at any level. The only difference is:
- `level` field in requirement records (0 = system, 1+ = subsystem)
- Parent-to-child traces created during allocation
- Sub-block requirements inherit the parent block's source traceability

---

## 6. Scripts Detail

### 6.1 State Management (`update_state.py`)

Identical pattern to concept-dev. Subcommands:

- `set-phase <phase>` — set current phase
- `pass-gate <phase>` — mark phase gate as passed
- `set-artifact <phase> <path>` — record deliverable artifact
- `update <dotted.path> <value>` — update nested counter/field
- `check-gate <phase>` — verify prerequisite gates passed (exit 0/1)
- `sync-counts` — sync registry counts to state.json
- `show` — display current state summary

All mutations use atomic write (temp-file-then-rename).

### 6.2 Quality Rules Engine (`quality_rules.py`)

Standalone script, no external dependencies. Loads word lists from `data/*.json` files.

CLI interface:
```bash
# Check a single requirement
python3 quality_rules.py check "The system shall handle requests appropriately."

# Check all requirements in registry
python3 quality_rules.py check-all --registry requirements_registry.json

# List available rules
python3 quality_rules.py rules

# Output format: JSON array of violations
```

Module interface for agent integration:
```python
def check_requirement(statement: str) -> list[Violation]
def check_rule(statement: str, rule_id: str) -> Violation | None
def list_rules() -> list[RuleInfo]
```

### 6.3 ReqIF Export (`reqif_export.py`)

Requires `reqif` package. Creates ReqIF XML mapping:
- Each requirement type → ReqIF SPEC-TYPE
- INCOSE attributes → ReqIF attribute definitions
- Requirements → SPEC-OBJECTS
- Traceability links → SPEC-RELATIONS
- Block hierarchy → SPEC-HIERARCHY (nested specification structure)

### 6.4 Source Tracker (`source_tracker.py`)

Adapted from concept-dev with minimal changes. Used to register sources found during TPM research and cross-reference concept-dev sources.

### 6.5 Concept Ingestion (`ingest_concept.py`)

Parses concept-dev artifacts and produces structured extraction:

```bash
python3 ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json
```

Output JSON contains:
- `blocks`: list of blocks with names, descriptions, relationships
- `needs_candidates`: extracted from capabilities and ConOps, organized by block
- `source_refs`: available concept-dev sources
- `assumption_refs`: assumptions to carry forward
- `validation`: gate status, missing artifacts, warnings

---

## 7. Commands

### `/reqdev:init`
Initialize session. Ingest concept-dev artifacts or set up manual mode. Create workspace. Detect research tools.

### `/reqdev:needs`
Needs formalization per block. Present candidates, formalize to INCOSE pattern, user review and approval. Gate: all block needs approved.

### `/reqdev:requirements`
Main workflow. For each block: type-guided passes (functional → performance → interface → constraint → quality). Each requirement: quality check → V&V plan → register → trace. Metered interaction (2-3 requirements per round).

### `/reqdev:validate`
Run set validation on current requirements. Interface coverage, duplicate detection, terminology consistency, orphan check. Phase 2 feature but useful during Phase 1 development.

### `/reqdev:research`
Trigger TPM research for a specific requirement. Launches tpm-researcher agent. Registers sources. Phase 2 feature.

### `/reqdev:deliver`
Generate deliverables: REQUIREMENTS-SPECIFICATION.md, TRACEABILITY-MATRIX.md, VERIFICATION-MATRIX.md, JSON registries, ReqIF export. Section-by-section user approval.

### `/reqdev:decompose`
Subsystem decomposition for a baselined block. Guide sub-block definition, allocation, coverage validation. Sub-blocks re-enter pipeline. Phase 3 feature.

### `/reqdev:status`
Session dashboard showing: current phase, block progress (types completed), requirement counts by type/status, traceability coverage %, TBD/TBR counts, quality check pass rate.

### `/reqdev:resume`
Resume interrupted session. Read state.json and report exact position. E.g., "15 needs approved. 23 requirements registered. Block 3: 2/5 types done. Resuming at interface/API requirements."

---

## 8. Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| quality-checker | sonnet | LLM-assisted semantic quality checks (9 rules) with CoT and few-shot examples |
| tpm-researcher | sonnet | Search for performance benchmarks and comparable system data |
| skeptic | opus | Verify coverage and feasibility claims during cross-cutting sweep |
| document-writer | sonnet | Generate deliverable documents from registries and templates |

---

## 9. Hooks

### PostToolUse: Auto-update state on artifact write

```json
{
  "event": "PostToolUse",
  "matcher": {
    "tool_name": "Write",
    "path_pattern": "**/.requirements-dev/*.md"
  },
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/update-state-on-write.sh \"$TOOL_INPUT_PATH\""
}
```

The hook script detects which artifact was written based on filename and updates state.json accordingly (e.g., writing REQUIREMENTS-SPECIFICATION.md sets the deliverables artifact path).

---

## 10. Data Files

### Word Lists (`data/*.json`)

Each file contains a JSON array of strings for deterministic rule matching:

- `vague_terms.json` (R7): ~20 vague terms from INCOSE GtWR v4 summary sheet
- `escape_clauses.json` (R8): ~10 escape clause phrases
- `absolutes.json` (R26): 6 absolute terms
- `pronouns.json` (R24): ~10 pronouns to flag

These are maintained as separate data files (not hardcoded) so they can be updated independently of the rule engine code. The concept document notes GtWR v4 has a known rule count discrepancy (42 vs 44); data files can be adjusted when the primary source is obtained.

---

## 11. Reference Documents

### `references/incose-rules.md`
Complete rule definitions for all 42 INCOSE GtWR v4 rules. For each rule: ID, name, characteristic, detection tier (deterministic/LLM/manual), description, examples of violations and corrections. Also includes 12-20 validated examples for the LLM tier's few-shot context.

### `references/attribute-schema.md`
The 13 INCOSE attributes (A1-A13) with definitions, data types, and examples. Distinguishes the 3 mandatory attributes (statement, type, priority) from the 10 expandable attributes.

### `references/type-guide.md`
Requirement type definitions with examples: functional, performance, interface/API, constraint, quality. Includes guidance on which types to expect for different block patterns. Helps the skill seed appropriate draft requirements.

### `references/vv-methods.md`
V&V method selection guide. Maps requirement types to suggested verification methods. Includes success criteria templates for each method type.

### `references/decomposition-guide.md`
Subsystem decomposition patterns. Guidance on when to decompose, how to identify sub-functions, allocation rationale templates. Stopping condition guidance.

---

## 12. Security & Safety

Following established codebase patterns:

1. **Path validation:** `_validate_path()` on all CLI file arguments — reject `..` traversal, restrict extensions
2. **HTML escaping:** `html.escape()` on all user-provided content in generated markdown/HTML
3. **Atomic writes:** temp-file-then-rename for all registry/state mutations
4. **No network in scripts:** Python scripts are local-only; network research done through Claude tools
5. **Content boundary marking:** Any external content (from TPM research) wrapped in BEGIN/END markers
6. **Input as data:** All user-provided requirement text treated as data, never as instructions

---

## 13. Implementation Order

Within each phase, implement in dependency order:

### Phase 1 (Foundation)
1. Plugin scaffolding (plugin.json, SKILL.md, directory structure)
2. `init_session.py` + `update_state.py` (state management — foundation for everything)
3. `ingest_concept.py` (concept-dev artifact parsing)
4. `/reqdev:init` command
5. `needs_tracker.py` + `/reqdev:needs` command
6. `quality_rules.py` + word list data files (deterministic quality checking)
7. `requirement_tracker.py` + `traceability.py` (requirement and link management)
8. quality-checker agent (LLM semantic checks)
9. `/reqdev:requirements` command (main workflow — ties together engine, quality, V&V, traceability)
10. `/reqdev:status` + `/reqdev:resume` commands
11. document-writer agent + templates
12. `reqif_export.py`
13. `/reqdev:deliver` command
14. Hooks (auto-state-update)
15. README.md + HOW_TO_USE.md
16. Reference documents

### Phase 2 (Validation & Research)
17. Set Validator logic (interface coverage, duplicate detection, terminology)
18. `/reqdev:validate` command
19. Cross-cutting sweep logic + INCOSE C10-C15 checks
20. skeptic agent
21. tpm-researcher agent + `check_tools.py` adaptation
22. `/reqdev:research` command

### Phase 3 (Decomposition)
23. Subsystem decomposition state tracking (multi-level state.json)
24. Allocation logic + coverage validation
25. `/reqdev:decompose` command
26. Re-entrant pipeline validation (ensure same quality at subsystem level)

---

## 14. Dependencies

**Runtime (stdlib only for core scripts):**
- Python 3.11+
- Standard library: json, argparse, pathlib, re, sys, datetime, tempfile, os

**Optional (for ReqIF export):**
- `reqif` Python package (PyPI)

**Plugin infrastructure:**
- Claude Code plugin system
- WebSearch (always available for TPM research)
- WebFetch, crawl4ai, MCP servers (optional, detected at init)

**Input artifacts:**
- `.concept-dev/` directory (preferred) or manual block/needs entry
