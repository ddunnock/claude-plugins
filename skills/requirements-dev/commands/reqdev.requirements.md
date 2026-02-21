---
name: reqdev:requirements
description: Main workflow — develop requirements block-by-block with type-guided passes, quality checking, V&V planning, and traceability
---

# /reqdev:requirements -- Develop Requirements

This command guides block-by-block, type-guided requirements development with quality checking, V&V planning, and traceability linking.

## Prerequisites

Verify the `needs` gate is passed:

```bash
uv run scripts/update_state.py --state .requirements-dev check-gate needs
```

If the gate check fails (exit code 1), inform the user:
```
The needs gate has not been passed. Please run /reqdev:needs first to formalize stakeholder needs.
```

## Step 1: Load Context

```bash
uv run scripts/update_state.py --state .requirements-dev show
```

Read registries:

```bash
cat .requirements-dev/needs_registry.json
cat .requirements-dev/requirements_registry.json
cat .requirements-dev/state.json
```

Extract:
- `blocks`: the list of functional blocks to process
- Approved needs per block (from `needs_registry.json`)
- Existing requirements (for resume)
- `progress.current_block` and `progress.current_type_pass` (resume position)
- `progress.requirements_in_draft` (unregistered drafts from previous session)

## Step 2: Set Phase

```bash
uv run scripts/update_state.py --state .requirements-dev set-phase requirements
```

## Step 3: Handle Resume

If `progress.requirements_in_draft` contains IDs, present them for confirmation before continuing:

```
===================================================================
RESUME: Found draft requirements from previous session
===================================================================

[List each draft REQ-xxx with its statement]

For each draft:
  [A] Register now (proceed to quality check + registration)
  [B] Discard (remove the draft)
===================================================================
```

After handling drafts, clear the list:
```bash
uv run scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'
```

## Step 4: Block-by-Block, Type-Guided Passes

For each block that has approved needs, iterate over requirement types in this fixed order:

1. **Functional** -- what the block must do
2. **Performance** -- measurable behavior targets
3. **Interface** -- how the block communicates with other blocks
4. **Constraint** -- limitations from environment, standards, or technology
5. **Quality** -- non-functional characteristics (reliability, maintainability, etc.)

### For Each Type Pass Within a Block

#### 4a. Update Progress Tracking

```bash
uv run scripts/update_state.py --state .requirements-dev update progress.current_block "<block-name>"
uv run scripts/update_state.py --state .requirements-dev update progress.current_type_pass "<type>"
```

#### 4b. Seed Draft Requirements

Read the block's approved needs from `needs_registry.json` and the block context. Propose 2-3 draft requirement statements for the current type.

Use the INCOSE pattern: **"The [subject] shall [action] [measurable criterion]."**

#### 4c. Present Drafts for User Refinement

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

#### 4d. Collect Minimal Attributes

For each accepted/edited requirement, confirm:
- **Statement** (the requirement text)
- **Type** (pre-set from the current pass)
- **Priority** (high/medium/low)

Optionally offer expansion to full 13 INCOSE attributes (rationale, risk, stability, source, allocation, etc.) via `references/attribute-schema.md`. Do not force expansion.

#### 4e. Quality Check -- Tier 1 (Deterministic)

```bash
uv run scripts/quality_rules.py check "<requirement statement>"
```

Parse the JSON output. If violations are found, present them with suggested rewrites. The user resolves each violation (accept rewrite, provide own rewrite, or justify and override). Re-run the check on revised text until it passes.

#### 4f. Quality Check -- Tier 2 (LLM Semantic)

If Tier 1 passes, invoke the **quality-checker** agent with:
- The requirement statement
- Context: block name, requirement type, parent need statement
- Existing requirements (for terminology consistency via R36)

Reference: `agents/quality-checker.md`

Present both tiers' results together. Only **high-confidence flags** block registration; medium/low flags are informational.

#### 4g. V&V Planning

Suggest verification method based on type-to-method mapping:

| Type | Suggested V&V Method |
|------|---------------------|
| Functional | System test / unit test |
| Performance | Load test / benchmark test |
| Interface | Integration test / contract test |
| Constraint | Inspection / analysis |
| Quality | Demonstration / analysis |

Reference: `references/vv-methods.md`

Present suggested method, draft success criteria derived from the requirement statement, and suggested responsible party. User confirms or modifies. Store as INCOSE attributes A6-A9.

#### 4h. Register the Requirement

```bash
uv run scripts/requirement_tracker.py --workspace .requirements-dev add \
  --statement "<statement>" --type <type> --priority <priority> \
  --source-block "<block-name>" --level 0
```

Then register (transition from draft to registered):

```bash
uv run scripts/requirement_tracker.py --workspace .requirements-dev register \
  --id <REQ-xxx> --parent-need <NEED-xxx>
```

#### 4i. Create Traceability Links

```bash
uv run scripts/traceability.py --workspace .requirements-dev link \
  --source <REQ-xxx> --target <NEED-xxx> --type derives_from --role requirement
```

If concept-dev sources are referenced:

```bash
uv run scripts/traceability.py --workspace .requirements-dev link \
  --source <REQ-xxx> --target <SRC-xxx> --type sources --role requirement
```

#### 4j. Sync Counts

```bash
uv run scripts/update_state.py --state .requirements-dev sync-counts
```

### Metered Interaction Checkpoint

After registering each batch of 2-3 requirements, checkpoint with the user:

```
===================================================================
CHECKPOINT: [N] requirements registered for [block-name], [type] type.

  [A] Continue with more [type] requirements for this block
  [B] Move to [next-type] requirements
  [C] Review what we have so far (/reqdev:status)
  [D] Pause session (progress saved -- use /reqdev:resume to continue)
===================================================================
```

**CRITICAL: Do NOT generate more than 3 requirements without user confirmation.**

If the user chooses [D] (Pause), save any quality-checked but unregistered drafts:

```bash
uv run scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '["REQ-xxx"]'
```

### Type Pass Completion

When the user signals no more requirements for a given type, transition:

```bash
uv run scripts/update_state.py --state .requirements-dev update progress.current_type_pass "<next-type>"
```

### Block Completion

When all five type passes are complete for a block:

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

## Step 5: Gate Completion

After all blocks have completed all type passes:

```bash
uv run scripts/update_state.py --state .requirements-dev pass-gate requirements
```

## Step 6: Transition Message

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
  /reqdev:validate -- Run set validation (recommended)
  /reqdev:deliver  -- Generate deliverable documents
  /reqdev:status   -- View full dashboard
===================================================================
```

## Behavioral Rules

1. **Never skip quality checking.** Every requirement statement must pass through `quality_rules.py` before registration. No exceptions.

2. **Never auto-register.** Always present requirements for user review before registration. The user must explicitly approve each requirement.

3. **Respect the type order.** Process types in the fixed order (functional, performance, interface, constraint, quality). Do not skip types unless the user explicitly requests it.

4. **Meter the output.** Present at most 2-3 draft requirements per round. Wait for user response before generating more.

5. **Track position precisely.** Update `progress.current_block` and `progress.current_type_pass` in state.json at every transition so `/reqdev:resume` can restore exact position.

6. **Handle TBD/TBR values.** When a requirement has a value that cannot be determined yet (e.g., a performance target needing research), mark it as TBD with a closure tracking field. Suggest `/reqdev:research` for TPM investigation.

7. **Offer attribute expansion.** After the minimal 3 attributes (statement, type, priority), offer to expand to the full 13 INCOSE attributes. Reference `references/attribute-schema.md` for the schema. Do not force expansion on every requirement.

8. **Use the quality-checker agent for semantic checks.** After Tier 1 deterministic checks pass, invoke the quality-checker agent for the 9 semantic rules. Present both tiers' results together.
