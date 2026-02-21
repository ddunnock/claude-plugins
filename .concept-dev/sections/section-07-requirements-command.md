Now I have all the context needed. Let me generate the section content.

# Section 07: Requirements Command (`/reqdev:requirements`)

## Overview

This section implements the `/reqdev:requirements` command prompt file, which is the main workflow command for the requirements-dev plugin. It orchestrates the block-by-block, type-guided requirements development process, integrating quality checking, V&V planning, requirement registration, and traceability linking into a metered conversational flow.

**What this section produces:**
- `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.requirements.md` -- the command prompt file

**Dependencies (must be completed first):**
- Section 03 (Concept Ingestion) -- provides `ingest_concept.py`, ingestion data, and the `/reqdev:init` command
- Section 06 (Requirements Engine) -- provides `requirement_tracker.py`, `traceability.py`, and `source_tracker.py`
- Section 04 (Needs Tracker) -- provides `needs_tracker.py` and `needs_registry.json`
- Section 05 (Quality Checker) -- provides `quality_rules.py` and the quality-checker agent
- Section 02 (State Management) -- provides `update_state.py` and `state.json`

**Blocks:** Section 09 (Deliverables)

---

## Tests

This section's tests live in the integration test file since the command prompt itself is a markdown file (not executable code). The tests validate the full pipeline that the command orchestrates.

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_integration.py`**

The following integration tests are owned by this section (other integration tests belong to sections 08 and 09):

```python
# --- Full pipeline (needs -> requirements -> V&V -> traceability) ---
# Test: create need -> derive requirement -> quality check -> register -> create trace -> verify coverage
# Test: pipeline with quality violation -> resolve -> re-check -> register
# Test: pipeline with TBD value -> register with TBD tracking

# --- Metered interaction flow ---
# Test: after registering 2-3 requirements, state.json progress is updated correctly
# Test: current_block and current_type_pass reflect position in type-guided passes
# Test: requirements_in_draft holds IDs of quality-checked but unregistered requirements
```

These tests exercise the scripts that the command prompt calls (`requirement_tracker.py`, `quality_rules.py`, `traceability.py`, `update_state.py`, `needs_tracker.py`) in the sequence dictated by the command's procedure. Each test sets up a workspace with pre-populated `needs_registry.json` and `state.json`, then runs the script commands in pipeline order, asserting state transitions and registry contents.

**Test fixture setup pattern:**

```python
import pytest
import json
import subprocess
import tempfile
import os

@pytest.fixture
def workspace(tmp_path):
    """Create a minimal .requirements-dev workspace with pre-populated needs."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    # Write state.json with init gate passed, needs gate passed, current_phase="requirements"
    # Write needs_registry.json with 2-3 approved needs
    # Write empty requirements_registry.json and traceability_registry.json
    # Return workspace path
    ...
```

**Test: full pipeline flow**

```python
def test_full_pipeline_need_to_traced_requirement(workspace):
    """Verify the complete flow: quality check -> register -> trace -> coverage."""
    # 1. Run quality_rules.py check on a clean requirement statement
    # 2. Run requirement_tracker.py add with statement, type, priority
    # 3. Run requirement_tracker.py register on the new REQ-xxx
    # 4. Run traceability.py link REQ-xxx -> NEED-xxx derives_from
    # 5. Run traceability.py coverage_report
    # Assert: requirement exists in registry with status="registered"
    # Assert: traceability link exists
    # Assert: coverage > 0%
    ...
```

**Test: pipeline with quality violation**

```python
def test_pipeline_quality_violation_then_resolve(workspace):
    """Verify violation blocks registration, resolution allows it."""
    # 1. Run quality_rules.py check on "The system shall provide appropriate handling"
    # Assert: violations list is non-empty (R7 flags "appropriate")
    # 2. Run quality_rules.py check on "The system shall provide structured error responses"
    # Assert: violations list is empty
    # 3. Proceed with registration of the clean statement
    ...
```

**Test: TBD tracking**

```python
def test_pipeline_tbd_tracking(workspace):
    """Verify TBD values are tracked through registration."""
    # 1. Add requirement with tbd_tbr field set
    # 2. Register the requirement
    # 3. Run update_state.py sync-counts
    # Assert: state.json counts.tbd_open is incremented
    ...
```

---

## Command Prompt Implementation

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.requirements.md`**

This is a markdown command prompt file following the pattern established by concept-dev commands (e.g., `concept.blackbox.md`). It instructs Claude on the exact procedure, script invocations, interaction format, and gating logic for the requirements development workflow.

### Front Matter

The file begins with YAML front matter:

```yaml
---
name: reqdev:requirements
description: Main workflow — develop requirements block-by-block with type-guided passes, quality checking, V&V planning, and traceability
---
```

### Prerequisite Gate Check

The command must verify that prerequisite gates have been passed before proceeding. The `needs` gate must be passed (meaning at least one block's needs have been formalized and approved).

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json check-gate needs
```

If this exits non-zero, the command instructs Claude to stop and tell the user to complete `/reqdev:needs` first.

Then load context:
- Run `update_state.py show` to display current state
- Read `needs_registry.json` to know what needs exist per block
- Read `requirements_registry.json` to know what requirements already exist (for resume)
- Read `state.json` progress section to determine where to start/resume

### Phase Setting

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json set-phase requirements
```

### Procedure: Block-by-Block, Type-Guided Passes

The core procedure iterates over blocks and, within each block, iterates over requirement types in a fixed order. The command prompt must specify this procedure in detail.

**Block iteration:** The command reads blocks from `state.json` (populated during `/reqdev:init`). For each block that has approved needs, the command guides the user through all five type passes.

**Type pass order (fixed):**
1. Functional -- what the block must do
2. Performance -- measurable behavior targets
3. Interface -- how the block communicates with other blocks
4. Constraint -- limitations from environment, standards, or technology
5. Quality -- non-functional characteristics (reliability, maintainability, etc.)

**For each type pass within a block, the procedure is:**

1. **Update progress tracking:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json update progress.current_block "<block-name>"
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json update progress.current_type_pass "<type>"
   ```

2. **Seed draft requirements:** Claude reads the block's approved needs from `needs_registry.json` and the block context (from ingestion data). It proposes 2-3 draft requirement statements appropriate for the current type. Drafts use the INCOSE pattern: "The [subject] shall [action] [measurable criterion]."

3. **Present drafts for user refinement:** Display drafts in a structured format:
   ```
   ===================================================================
   BLOCK: [block-name] | TYPE: [functional/performance/...]
   ===================================================================
   
   Draft 1: The [subject] shall [action].
     Parent Need: NEED-xxx
     Priority: [suggested]
   
   Draft 2: The [subject] shall [action].
     Parent Need: NEED-xxx
     Priority: [suggested]
   
   -------------------------------------------------------------------
   Review each draft:
     [A] Accept as-is
     [B] Edit (provide your revision)
     [C] Skip (don't create this requirement)
     [D] Add a new requirement not shown above
   ===================================================================
   ```

4. **Collect minimal attributes:** For each accepted/edited requirement, confirm: statement, type (pre-set from the current pass), priority (high/medium/low). Optionally offer expansion to full 13 INCOSE attributes (rationale, risk, stability, source, allocation, etc.) via reference to `references/attribute-schema.md`.

5. **Run Quality Checker (Tier 1 -- deterministic):**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/quality_rules.py check "<requirement statement>"
   ```
   Parse the JSON output. If violations are found, present them with suggested rewrites. The user resolves each violation (accept rewrite, provide own rewrite, or justify and override). Re-run the check on revised text until it passes.

6. **Run Quality Checker (Tier 2 -- LLM semantic):** If Tier 1 passes, invoke the quality-checker agent (defined in `agents/quality-checker.md`) with the requirement statement, its context (block, type, parent need), and the `references/incose-rules.md` examples. Present any flags. Only high-confidence flags block registration; medium/low flags are informational.

7. **Run V&V Planner:** Suggest verification method based on type-to-method mapping:
   - Functional -> system test / unit test
   - Performance -> load test / benchmark test
   - Interface -> integration test / contract test
   - Constraint -> inspection / analysis
   - Quality -> demonstration / analysis

   Present suggested method, draft success criteria derived from the requirement statement, and suggested responsible party. User confirms or modifies. Store as INCOSE attributes A6-A9.

8. **Register the requirement:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --registry .requirements-dev/requirements_registry.json add "<statement>" --type <type> --priority <priority> --parent-need <NEED-xxx> --source-block "<block-name>" --level 0
   ```
   Then register (transition from draft to registered):
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --registry .requirements-dev/requirements_registry.json register <REQ-xxx>
   ```

9. **Create traceability links:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --registry .requirements-dev/traceability_registry.json link <REQ-xxx> <NEED-xxx> derives_from requirement
   ```
   If concept-dev sources are referenced:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --registry .requirements-dev/traceability_registry.json link <REQ-xxx> <SRC-xxx> sources requirement
   ```

10. **Sync counts:**
    ```bash
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json sync-counts
    ```

### Metered Interaction Pattern

After registering each batch of 2-3 requirements, the command instructs Claude to checkpoint with the user:

```
===================================================================
CHECKPOINT: [N] requirements registered for [block-name], [type] type.

  [A] Continue with more [type] requirements for this block
  [B] Move to [next-type] requirements
  [C] Review what we have so far (/reqdev:status)
  [D] Pause session (progress saved — use /reqdev:resume to continue)
===================================================================
```

This metered pattern prevents runaway generation and gives the user control over pacing. The command explicitly states that Claude must NOT generate more than 3 requirements without user confirmation.

### Type Pass Completion

When the user signals no more requirements for a given type (by choosing "Move to next type" or confirming the type is complete), the command updates progress:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json update progress.current_type_pass "<next-type>"
```

### Block Completion

When all five type passes are complete for a block, present a block summary:

```
===================================================================
BLOCK COMPLETE: [block-name]
===================================================================

Requirements registered: [count by type]
  Functional:   [n]
  Performance:  [n]
  Interface:    [n]
  Constraint:   [n]
  Quality:      [n]

Traceability: [n] needs covered out of [total]
Quality check pass rate: [n]%

Proceed to next block? [Y/N]
===================================================================
```

### Draft Preservation (requirements_in_draft)

If a requirement passes quality checking but has not yet been formally registered when the user pauses the session, the command must save the draft requirement IDs to `state.json`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json update progress.requirements_in_draft '["REQ-xxx"]'
```

On resume (via `/reqdev:resume`), these drafts are presented for confirmation before continuing with new requirements.

### Gate: Requirements Phase Complete

After all blocks have completed all type passes, the command passes the requirements gate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json pass-gate requirements
```

### Transition Message

```
===================================================================
Requirements phase complete.

Total requirements registered: [N]
  By type: functional=[n], performance=[n], interface=[n],
           constraint=[n], quality=[n]
Traceability coverage: [n]%
Open TBD items: [n]
Open TBR items: [n]

Next steps:
  /reqdev:validate — Run set validation (recommended)
  /reqdev:deliver  — Generate deliverable documents
  /reqdev:status   — View full dashboard
===================================================================
```

### Key Behavioral Rules for the Command Prompt

The command prompt must include these explicit instructions for Claude's behavior:

1. **Never skip quality checking.** Every requirement statement must pass through `quality_rules.py` before registration. No exceptions.

2. **Never auto-register.** Always present requirements for user review before registration. The user must explicitly approve each requirement.

3. **Respect the type order.** Process types in the fixed order (functional, performance, interface, constraint, quality). Do not skip types unless the user explicitly requests it.

4. **Meter the output.** Present at most 2-3 draft requirements per round. Wait for user response before generating more.

5. **Track position precisely.** Update `progress.current_block` and `progress.current_type_pass` in state.json at every transition so `/reqdev:resume` can restore exact position.

6. **Handle TBD/TBR values.** When a requirement has a value that cannot be determined yet (e.g., a performance target needing research), mark it as TBD with a closure tracking field. Suggest `/reqdev:research` for TPM investigation.

7. **Offer attribute expansion.** After the minimal 3 attributes (statement, type, priority), offer to expand to the full 13 INCOSE attributes. Reference `references/attribute-schema.md` for the schema. Do not force expansion on every requirement.

8. **Use the quality-checker agent for semantic checks.** After Tier 1 deterministic checks pass, invoke the quality-checker agent for the 9 semantic rules. Present both tiers' results together.

---

## File Structure Summary

| File | Action | Description |
|------|--------|-------------|
| `skills/requirements-dev/commands/reqdev.requirements.md` | CREATE | Main command prompt file |
| `skills/requirements-dev/tests/test_integration.py` | CREATE | 8 integration tests (3 pipeline, 2 regression, 3 state tracking) |
| `skills/requirements-dev/scripts/update_state.py` | MODIFY | Bug fix: `sync_counts` + `_parse_value` JSON array support |
| `skills/requirements-dev/scripts/requirement_tracker.py` | MODIFY | `update_requirement` now raises ValueError for unknown fields |

## Implementation Notes

- The command prompt uses `--workspace .requirements-dev` consistently (matching actual script CLIs), not `--registry` as originally drafted in some plan examples.
- The section plan's `--registry` flag references were corrected to `--workspace` in the actual implementation.
- During integration testing, discovered and fixed a bug in `update_state.sync_counts()` where dict-wrapped registries (with `schema_version` + inner list) were iterated as dicts instead of extracting the `"needs"`/`"requirements"` lists.
- Code review identified a critical bug in `_parse_value()` which didn't handle JSON arrays, causing `requirements_in_draft` to be stored as a string instead of a list. Fixed by adding `json.loads()` fallback for array/object values.
- Code review also identified silent field-name dropping in `update_requirement()`. Now raises ValueError for unknown fields.
- 122 total tests passing (8 new integration + 114 existing).