---
name: reqdev:needs
description: Formalize stakeholder needs per functional block
---

# /reqdev:needs -- Formalize Stakeholder Needs

This command guides needs formalization from ingestion candidates into INCOSE-pattern need statements.

## Prerequisites

Before starting, verify the `init` gate is passed:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json check-gate init
```

If the gate check fails (exit code 1), inform the user:
```
The init gate has not been passed. Please run /reqdev:init first.
```

## Step 1: Load Context

Read the ingestion data and current state:

```bash
cat .requirements-dev/ingestion.json
```

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json show
```

Extract:
- `blocks`: the list of functional blocks to process
- `needs_candidates`: pre-extracted need candidates (if concept-dev was used)
- Current `needs_total` count (to know if resuming)

## Step 2: Per-Block Iteration

For each block defined in state.json `blocks`:

### If needs_candidates exist for this block (from ingestion):

1. Present the candidates in a numbered list
2. For each candidate, formalize into INCOSE pattern:

**INCOSE Need Pattern:**
- Pattern: `[Stakeholder] needs [capability] [optional qualifier]`
- Use "should" for expectations, not "shall" (which is for requirements)
- Solution-free: describe what is needed, not how to achieve it

**Examples:**
- Good: "The operator needs to monitor system health metrics in real-time"
- Bad: "The operator needs a Grafana dashboard" (prescribes solution)
- Bad: "The system shall display metrics" (uses obligation language -- this is a requirement, not a need)

3. **Split assessment:** Before presenting, assess each formalized need for compound concerns. A need is compound if it describes two or more independent capabilities that could be satisfied separately. Look for:
   - Coordinating conjunctions joining distinct capabilities ("and", "as well as", "in addition to")
   - Multiple verb phrases describing unrelated actions
   - Mixed concern areas (e.g., monitoring AND configuration in one statement)

   **Compound need indicators:**
   - "The operator needs to monitor health metrics and configure alert thresholds" → **Split** (monitoring ≠ configuration)
   - "The operator needs to monitor CPU and memory health metrics" → **Keep** (both are monitoring)

   When a compound need is detected, propose the split alongside the original:

   ```
   Candidate 3 appears to contain multiple concerns:
     Original: "The operator needs to monitor health metrics and configure
                alert thresholds for critical events"
     Proposed split:
       3a: "The operator needs to monitor system health metrics in real-time"
       3b: "The operator needs to configure alert thresholds for critical events"

     [S] Split into 3a and 3b (recommended)
     [K] Keep as a single need
     [E] Edit the original
   ```

4. Present a batch of 3-5 formalized needs (with any split proposals inline) for user review
5. For each need, ask the user to: approve, edit, split (if compound), defer (with rationale), or reject

### If no needs_candidates (manual mode):

1. Ask the user to describe stakeholder needs for this block
2. Guide them through the INCOSE formalization pattern
3. **Assess for compound concerns** using the same split assessment as above
4. Present formalized versions for approval

## Step 3: Register Approved Needs

For each approved need:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev add \
  --statement "The [stakeholder] needs [capability]" \
  --stakeholder "[Stakeholder Name]" \
  --source-block "[block-name]" \
  --source-artifacts "CONCEPT-DOCUMENT.md" \
  --concept-dev-refs '{"sources": ["SRC-xxx"], "assumptions": []}'
```

For split needs (when a previously registered need is found to be compound during review):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev split \
  --id NEED-xxx \
  --statements '["The operator needs to monitor system health metrics in real-time", "The operator needs to configure alert thresholds for critical events"]' \
  --rationale "Split: original combined monitoring and configuration concerns"
```

This rejects the original and creates new approved needs inheriting stakeholder, source_block, and concept-dev references.

For deferred needs:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev defer \
  --id NEED-xxx --rationale "User rationale here"
```

For rejected needs:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev reject \
  --id NEED-xxx --rationale "User rationale here"
```

## Step 4: Block Summary

After processing each block, display:

```
BLOCK: [block-name]
  Approved:  N needs
  Deferred:  M needs
  Rejected:  R needs
```

## Step 5: Review Cross-Cutting Notes

Before closing the needs gate, check for open notes targeting this phase:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev check-gate needs
```

If open notes exist, present them and guide the user to resolve or dismiss each one before proceeding (see SKILL.md Cross-Cutting Notes section for resolution flow).

**Capture forward-looking notes:** During needs formalization, if the user raises observations that clearly belong in the requirements or later phases (e.g., "we'll need to benchmark this" or "this will require an interface spec"), capture them:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev add \
  --text "Needs benchmarking for latency target" --origin-phase needs \
  --target-phase research --related-ids "NEED-xxx" --category performance
```

Inform the user: "Good catch — I've noted that for the [target] phase so we don't lose it."

## Step 6: Gate Completion

After all blocks have been processed, all cross-cutting notes are resolved, and the user approves the complete needs set:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json set-phase needs
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json pass-gate needs
```

## Step 7: Final Summary

```
NEEDS FORMALIZATION COMPLETE
============================
Total needs:     N
  Approved:      A
  Deferred:      D
  Rejected:      R
Blocks covered:  B

Next steps:
  /reqdev:requirements -- Develop requirements from approved needs
  /reqdev:status       -- View current session status
```
