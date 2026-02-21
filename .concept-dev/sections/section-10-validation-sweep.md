Now I have all the context needed. Let me generate the section content.

# Section 10: Validation Sweep

## Overview

This section implements the **Set Validator**, **Cross-Cutting Sweep**, the `/reqdev:validate` command, and the **skeptic agent**. These components validate requirements across blocks for completeness, consistency, and coverage after individual block requirements have been developed.

**Dependencies:** Section 09 (Deliverables) must be complete. This section uses `requirement_tracker.py`, `needs_tracker.py`, `traceability.py` from Sections 04-06, and the block/state structures from Sections 01-02.

**Blocks:** Section 12 (Decomposition) depends on this section.

---

## Background

After requirements are developed block-by-block (Phase 1), Phase 2 validates the *entire set* of requirements for cross-block consistency. The INCOSE GtWR v4 defines set characteristics (C10-C15) that apply to requirements as a collection, not individually. The validation sweep catches issues that per-requirement quality checking cannot: missing interface requirements between related blocks, near-duplicate requirements across blocks, inconsistent terminology, uncovered needs, and unresolved TBD/TBR items.

The skeptic agent (opus model) provides a rigorous LLM-based review of coverage and feasibility claims that emerge during the cross-cutting sweep.

---

## Tests FIRST

### File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_set_validator.py`

```python
"""Tests for set_validator.py — cross-block validation checks."""

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

### Cross-Cutting Sweep Tests (in same file or separate)

The cross-cutting sweep is primarily conversational but includes INCOSE C10-C15 checks that can be tested deterministically:

```python
"""Tests for cross-cutting INCOSE set characteristic checks."""

# Test: C10 completeness check — all needs traced to requirements
# Test: C14 validatability check — all requirements have V&V methods
# Test: C15 correctness check — all requirements derive from approved needs
```

### Test Fixture Setup

Tests require fixture data representing a multi-block requirements set. The test fixtures should include:

- A `state.json` with at least 3 blocks and block-to-block relationships
- A `needs_registry.json` with needs across multiple blocks (some covered, some uncovered, some deferred)
- A `requirements_registry.json` with requirements across blocks including:
  - Duplicate and near-duplicate statements
  - Inconsistent terminology ("user" vs "end-user")
  - Requirements with TBD/TBR items (some resolved, some open)
  - At least one block pair with interface requirements and one pair without
- A `traceability_registry.json` with `derives_from` links connecting requirements to needs

These fixtures should be created in `tests/conftest.py` or as JSON fixture files in `tests/fixtures/`.

---

## Implementation Details

### 1. Set Validator Script

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/set_validator.py`

A standalone Python script (stdlib only) that performs five cross-block validation checks. It reads the requirements, needs, and traceability registries plus block relationship data from `state.json`.

**CLI interface:**

```bash
# Run all validation checks
python3 set_validator.py validate --workspace .requirements-dev/

# Run specific check
python3 set_validator.py check-interfaces --workspace .requirements-dev/
python3 set_validator.py check-duplicates --workspace .requirements-dev/
python3 set_validator.py check-terminology --workspace .requirements-dev/
python3 set_validator.py check-coverage --workspace .requirements-dev/
python3 set_validator.py check-tbd --workspace .requirements-dev/

# Output: JSON with findings per check category
```

**Module interface:**

```python
def validate_all(workspace_path: str) -> dict:
    """Run all set validation checks. Returns dict with findings by category."""

def check_interface_coverage(blocks: dict, requirements: list[dict]) -> list[dict]:
    """For every block-to-block relationship, verify at least one interface requirement exists.
    
    Uses the block relationship map from state.json (populated during concept ingestion).
    Returns list of findings: {block_a, block_b, status: 'covered'|'missing'}.
    """

def check_duplicates(requirements: list[dict], threshold: float = 0.8) -> list[dict]:
    """Compare requirement statements across blocks using word-level n-gram cosine similarity.
    
    Uses unigrams + bigrams. Threshold 0.8 default (tunable).
    Implementation: pure Python dot product / magnitude — no numpy.
    Returns list of findings: {req_a, req_b, similarity, status: 'duplicate'|'near_duplicate'}.
    """

def compute_ngram_similarity(text_a: str, text_b: str, n_sizes: tuple = (1, 2)) -> float:
    """Compute cosine similarity between two texts using word-level n-gram frequency vectors.
    
    Word-level n-grams are more semantically meaningful than character-level
    for short requirement statements (typical 10-20 words).
    """

def check_terminology(requirements: list[dict]) -> list[dict]:
    """Build term dictionary from registered requirements. Flag inconsistent terms.
    
    Detects synonyms/variants used across blocks for the same concept
    (e.g., 'user' vs 'end-user' vs 'client').
    Returns list of findings: {term_variants: [...], blocks_affected: [...]}.
    """

def check_uncovered_needs(needs: list[dict], traceability_links: list[dict]) -> list[dict]:
    """Query for needs with no derived requirements.
    
    Deferred needs are excluded from the coverage check.
    Returns list of uncovered need IDs with their statements.
    """

def check_tbd_tbr(requirements: list[dict]) -> dict:
    """List all open TBD/TBR items with closure tracking fields.
    
    Returns: {open_tbd: [...], open_tbr: [...], resolved_count: int}.
    Resolved items excluded from the report.
    """
```

#### Duplicate Detection Algorithm Detail

The n-gram cosine similarity works as follows:

1. Tokenize each requirement statement into lowercase words (strip punctuation).
2. Generate unigrams and bigrams from the word list.
3. Build frequency vectors (Python `dict` of n-gram to count).
4. Compute cosine similarity: `dot(A, B) / (magnitude(A) * magnitude(B))`.
5. If similarity exceeds threshold (default 0.8), flag as potential duplicate.
6. Compare every unique pair of requirements across different blocks (not within the same block).

The "The system shall" prefix is extremely common and should not dominate similarity scores. Consider either removing common requirement prefixes before comparison or ensuring the n-gram approach naturally handles this (bigrams like "system shall" will match but won't dominate when statements are long enough).

#### Terminology Consistency Algorithm Detail

Build a normalized term dictionary:
1. Extract noun phrases or significant terms from each requirement (simple approach: words not in a stop-word list, appearing in 2+ requirements).
2. Group terms by stem or Levenshtein distance (e.g., "user", "users", "end-user", "end user").
3. For each group, check if variants appear in different blocks.
4. Flag groups where more than one variant is used across the requirement set.

This can be kept simple for Phase 2 since the LLM can assist with judgment calls.

---

### 2. Cross-Cutting Sweep Logic

The cross-cutting sweep is primarily driven by the `/reqdev:validate` command prompt but includes deterministic checks for INCOSE set characteristics C10-C15 that should be implemented in `set_validator.py` or a separate function within it.

**INCOSE Set Characteristic Checks:**

- **C10 (Completeness):** All approved needs must be traced to at least one requirement. This reuses `check_uncovered_needs()` above.
- **C11 (Consistency):** No conflicting requirements. This is detected via `conflicts_with` links in the traceability registry. The check verifies all conflicts have `resolution_status: "resolved"`.
- **C12 (Feasibility):** Delegated to the skeptic agent (LLM review).
- **C13 (Comprehensibility):** Reuses `check_terminology()` above.
- **C14 (Validatability):** All registered/baselined requirements must have V&V methods assigned (check `attributes` dict for verification method fields).
- **C15 (Correctness):** All requirements must derive from approved needs. Check that every requirement has a `derives_from` link to a need with `status: "approved"`.

```python
def check_incose_set_characteristics(workspace_path: str) -> dict:
    """Run INCOSE C10-C15 set characteristic validation.
    
    Returns dict with results per characteristic:
    {c10_completeness: {passed: bool, findings: [...]},
     c11_consistency: {passed: bool, findings: [...]},
     c14_validatability: {passed: bool, findings: [...]},
     c15_correctness: {passed: bool, findings: [...]}}.
    C12 feasibility is marked as 'requires_skeptic_review'.
    """
```

**Cross-cutting category checklist** (handled conversationally in the command prompt):
- Security, reliability, availability, scalability, maintainability, data integrity, logging/observability
- User selects applicable categories
- For each selected category, the command reviews existing requirements for coverage and flags blocks with no requirements in that category

---

### 3. The `/reqdev:validate` Command

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.validate.md`

This command prompt orchestrates the validation sweep. It should:

1. Run `set_validator.py validate` to get all deterministic findings.
2. Present findings to the user as a prioritized list, grouped by category.
3. For interface gaps: prompt the user to write missing interface requirements through the standard pipeline (quality check, V&V plan, register, trace).
4. For duplicates: present pairs for user decision (merge, differentiate, or accept).
5. For terminology inconsistencies: propose a canonical term and offer to update.
6. For uncovered needs: prompt the user to either write requirements or defer/reject the need.
7. For TBD/TBR items: present the open items and prompt for resolution values.
8. Run the cross-cutting category checklist interactively.
9. Run INCOSE C10-C15 checks and present results.
10. If C12 feasibility review is needed: launch the skeptic agent.

The command should update `state.json` to track validation status and findings count.

---

### 4. Skeptic Agent

**File:** `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/agents/skeptic.md`

The skeptic agent uses the **opus model** for rigorous verification. It follows the same pattern as concept-dev's skeptic agent.

**Agent receives:**
- The full requirements set (all blocks, all types)
- Cross-cutting sweep findings from set_validator.py
- Coverage claims made during the sweep (e.g., "All OWASP Top 10 categories covered")
- Block relationship map

**Agent evaluates:**
- Coverage claims: Does the requirement set actually cover what it claims? For example, if the user says "all security categories are addressed," the skeptic checks each category against the actual requirements.
- Feasibility claims: Are performance targets realistic? Are constraint requirements achievable?
- Completeness: Are there obvious gaps the automated checks missed?

**Agent output format for each finding:**
- Status: `verified`, `unverified`, `disputed`, `needs_user_input`
- Confidence: high/medium/low
- Reasoning: Chain-of-thought explanation
- Recommendation: What to do if disputed or unverified

**Agent prompt structure:**
```markdown
# Skeptic Agent

## Model
opus

## Role
You are a requirements skeptic. Your job is to rigorously verify coverage 
and feasibility claims in a requirements set. You challenge assumptions, 
check for gaps, and verify that stated coverage actually exists.

## Context
[Full requirements set, block relationships, cross-cutting findings]

## Instructions
1. For each coverage claim, verify it against the actual requirements
2. For each feasibility concern, assess whether targets are realistic
3. Report findings with status, confidence, reasoning, and recommendation
4. Be thorough but fair — flag real issues, not stylistic preferences

## Output Format
JSON array of findings, each with: claim, status, confidence, reasoning, recommendation
```

---

### 5. Security Considerations

All file path arguments to `set_validator.py` must use `_validate_path()` / `_validate_dir_path()` following the established codebase pattern (reject `..` traversal, use `os.path.realpath()`). The script reads registries as read-only — no mutations to registry files. Validation findings are output as JSON to stdout or written to a findings file in the workspace.

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `skills/requirements-dev/scripts/set_validator.py` | Create | Set validation logic (interface coverage, duplicates, terminology, uncovered needs, TBD/TBR, INCOSE C10-C15) |
| `skills/requirements-dev/commands/reqdev.validate.md` | Create | Command prompt orchestrating the validation sweep |
| `skills/requirements-dev/agents/skeptic.md` | Create | Opus-model agent for coverage and feasibility verification |
| `skills/requirements-dev/tests/test_set_validator.py` | Create | Tests for all set validation checks |
| `skills/requirements-dev/tests/conftest.py` | Modify | Add fixtures for multi-block validation test data |

---

## Integration Notes

- The set validator uses `traceability.py` (Section 06) for orphan/coverage queries but re-implements some checks directly against registry JSON to keep the validator self-contained for CLI use.
- Interface coverage checking depends on block relationships being stored in `state.json` during concept ingestion (Section 03). The relationship data should be in `state.json["blocks"]` with a `relationships` field per block listing connected blocks.
- The `/reqdev:validate` command feeds findings back into the `/reqdev:requirements` pipeline when interface gaps need new requirements written. The command prompt should reference the standard quality check / V&V / register / trace flow.
- The skeptic agent is invoked only when the cross-cutting sweep identifies coverage or feasibility claims that need verification. It is not run on every validation pass.
- Withdrawn requirements (status: "withdrawn") are excluded from all validation checks (duplicate detection, coverage calculation, terminology analysis).

## Implementation Notes (Post-Build)

### Deviations from Plan

1. **conftest.py not modified** - Fixtures are inlined in `test_set_validator.py` rather than added to `conftest.py`. The `validation_workspace` fixture is specific to set validation and doesn't need sharing.

2. **Terminology check uses hardcoded synonym groups** - The plan described stemming/Levenshtein approach. Implementation uses 3 hardcoded KNOWN_SYNONYMS groups (user/end-user/client, admin/administrator, log/audit). This is pragmatic for Phase 2 since the LLM (skeptic agent) assists with judgment on novel inconsistencies.

3. **C14 checks traceability links, not attributes** - The plan said to check `attributes` dict for V&V methods. Implementation checks for `verified_by` traceability links, which is the established mechanism in the codebase.

### Code Review Fixes

1. **Tightened interface coverage check** - `check_interface_coverage()` now verifies that interface requirements reference the other block by name in the statement text, preventing false positives from unrelated interface requirements.
2. **Fixed TBD/TBR elif bug** - Changed `elif tbr_val` to `if tbr_val` so both TBD and TBR are reported when both are open on the same requirement.
3. **Fixed docstring CLI argument order** - Updated module docstring to show `--workspace` before subcommand.

### Actual Files Created/Modified

| File | Action | Notes |
|------|--------|-------|
| `skills/requirements-dev/scripts/set_validator.py` | Created | 6 validation functions + INCOSE C10-C15 + CLI |
| `skills/requirements-dev/tests/test_set_validator.py` | Created | 17 tests covering all validation checks |
| `skills/requirements-dev/agents/skeptic.md` | Created | Opus agent for coverage/feasibility verification |
| `skills/requirements-dev/commands/reqdev.validate.md` | Created | 7-step validation sweep orchestration |

### Test Results

- 156 total tests passing (up from 139)
- 17 new set validator tests