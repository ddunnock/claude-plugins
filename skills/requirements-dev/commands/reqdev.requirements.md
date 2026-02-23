---
name: reqdev:requirements
description: Main workflow — develop requirements block-by-block with type-guided passes, quality checking, V&V planning, and traceability
---

# /reqdev:requirements -- Develop Requirements

This command guides block-by-block, type-guided requirements development with quality checking, V&V planning, and traceability linking.

## Prerequisites

Verify the `needs` gate is passed:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev check-gate needs
```

If the gate check fails (exit code 1), inform the user:
```
The needs gate has not been passed. Please run /reqdev:needs first to formalize stakeholder needs.
```

## Step 1: Load Context

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev show
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
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev set-phase requirements
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
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'
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
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.current_block "<block-name>"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.current_type_pass "<type>"
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

Optionally offer expansion to full 13 INCOSE attributes (rationale, risk, stability, source, allocation, etc.) via `${CLAUDE_PLUGIN_ROOT}/references/attribute-schema.md`. Do not force expansion.

#### 4e. Quality Check -- Tier 1 (Deterministic)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/quality_rules.py check "<requirement statement>"
```

Parse the JSON output. If violations are found, present them with suggested rewrites. The user resolves each violation (accept rewrite, provide own rewrite, or justify and override). Re-run the check on revised text until it passes.

#### 4f. Quality Check -- Tier 2 (LLM Semantic)

If Tier 1 passes, invoke the **quality-checker** agent with:
- The requirement statement
- Context: block name, requirement type, parent need statement
- Existing requirements (for terminology consistency via R36)

Reference: `${CLAUDE_PLUGIN_ROOT}/agents/quality-checker.md`

Present both tiers' results together. Only **high-confidence flags** block registration; medium/low flags are informational.

#### 4f-split. Split Assessment (when R19 or R18 triggers)

When Tier 1 rule R19 (Combinators — multiple `shall` clauses) or Tier 2 rule R18 (Single Thought) flags a requirement, the statement likely contains multiple requirements combined into one. Before attempting a rewrite, assess whether splitting is the right action.

**Present the split decision to the user:**

```
===================================================================
SPLIT ASSESSMENT: This statement may contain multiple requirements.
===================================================================

Original: "The system shall encrypt data at rest and shall log all
           access attempts within 5 seconds."

Trigger: [R19 Combinators / R18 Single Thought]

Proposed split:
  A: "The system shall encrypt all data at rest using AES-256."
  B: "The system shall log all access attempts within 5 seconds
      of the access event."

-------------------------------------------------------------------
Action:
  [S] Split into separate requirements (recommended)
  [R] Rewrite as a single requirement instead
  [O] Override — keep as-is with justification
===================================================================
```

**If the user chooses [S] Split:**

If the requirement is already registered (status = `registered` or `draft`):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev split \
  --id <REQ-xxx> \
  --statements '["The system shall encrypt all data at rest using AES-256.", "The system shall log all access attempts within 5 seconds of the access event."]' \
  --rationale "Split: original combined encryption and logging concerns (R19/R18)"
```

This atomically:
- Withdraws the original (with split rationale)
- Creates N new draft requirements inheriting type, priority, block, level
- Records `split_from: REQ-xxx` in each new requirement's attributes

Then for each new draft requirement:
1. Run Tier 1 + Tier 2 quality checks (the split statements should now pass R18/R19)
2. Present for user confirmation
3. Complete V&V planning (step 4g)
4. Register with the same parent need (step 4h)
5. Create traceability links (step 4i)

If the requirement was only a draft text (not yet added to registry), simply replace the single draft with N separate drafts in the presentation and continue the normal flow from step 4c.

**If the user chooses [R] Rewrite:** Return to step 4e with the revised single statement.

**If the user chooses [O] Override:** Record the justification in the requirement's `attributes.r18_override` or `attributes.r19_override` field and proceed to V&V planning.

#### 4g. V&V Planning

Suggest verification method based on type-to-method mapping:

| Type | Suggested V&V Method |
|------|---------------------|
| Functional | System test / unit test |
| Performance | Load test / benchmark test |
| Interface | Integration test / contract test |
| Constraint | Inspection / analysis |
| Quality | Demonstration / analysis |

Reference: `${CLAUDE_PLUGIN_ROOT}/references/vv-methods.md`

Present suggested method, draft success criteria derived from the requirement statement, and suggested responsible party. User confirms or modifies. Store as INCOSE attributes A6-A9.

#### 4h. Register the Requirement

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev add \
  --statement "<statement>" --type <type> --priority <priority> \
  --source-block "<block-name>" --level 0
```

Then register (transition from draft to registered):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev register \
  --id <REQ-xxx> --parent-need <NEED-xxx>
```

#### 4i. Create Traceability Links

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev link \
  --source <REQ-xxx> --target <NEED-xxx> --type derives_from --role requirement
```

If concept-dev sources are referenced:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev link \
  --source <REQ-xxx> --target <SRC-xxx> --type sources --role requirement
```

#### 4j. Sync Counts

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev sync-counts
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
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '["REQ-xxx"]'
```

### Type Pass Completion

When the user signals no more requirements for a given type, transition:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.current_type_pass "<next-type>"
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

## Step 5: Review Cross-Cutting Notes

Before closing the requirements gate, check for open notes targeting this phase:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev check-gate requirements
```

If there are open notes, present them to the user:

```
===================================================================
CROSS-CUTTING NOTES TO RESOLVE BEFORE GATE
===================================================================

The following observations were captured during earlier phases and
target the requirements phase for resolution:

[For each open note]:
  NOTE-xxx: "[text]"
    Captured during: [origin_phase]
    Category: [category]
    Related: [related_ids or "none"]

  Action:
    [A] Resolve (provide resolution and optionally a resolving REQ-xxx)
    [B] Dismiss with rationale
===================================================================
```

For resolutions:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev resolve --id NOTE-xxx --resolution "Addressed by REQ-015" --resolved-by REQ-015
```

For dismissals:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev dismiss --id NOTE-xxx --rationale "Not applicable — covered by existing constraint"
```

All notes targeting this phase must be resolved or dismissed before the gate can pass.

## Step 6: Gate Completion

After all blocks have completed all type passes and all cross-cutting notes are resolved:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev pass-gate requirements
```

## Step 7: Transition Message

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
  /reqdev:gaps     -- Check coverage gaps against concept (recommended)
  /reqdev:validate -- Run set validation
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

7. **Offer attribute expansion.** After the minimal 3 attributes (statement, type, priority), offer to expand to the full 13 INCOSE attributes. Reference `${CLAUDE_PLUGIN_ROOT}/references/attribute-schema.md` for the schema. Do not force expansion on every requirement.

8. **Use the quality-checker agent for semantic checks.** After Tier 1 deterministic checks pass, invoke the quality-checker agent for the 9 semantic rules. Present both tiers' results together.

9. **Capture cross-cutting observations.** When a discussion during one type pass raises a concern for a different type or phase (e.g., functional pass reveals a performance concern, or a constraint that needs research), record it immediately as a cross-cutting note:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev add \
     --text "Performance concern: [description]" --origin-phase requirements \
     --target-phase requirements --related-ids "NEED-xxx" --category performance
   ```
   Inform the user: "Noted for the [target] pass — I've recorded this so we don't lose it."
