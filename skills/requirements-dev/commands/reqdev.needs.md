---
name: reqdev:needs
description: Formalize stakeholder needs per functional block
---

# /reqdev:needs -- Formalize Stakeholder Needs

This command guides needs formalization from ingestion candidates into INCOSE-pattern need statements.

## Prerequisites

Before starting, verify the `init` gate is passed:

```bash
uv run scripts/update_state.py --state .requirements-dev/state.json check-gate init
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
uv run scripts/update_state.py --state .requirements-dev/state.json show
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

3. Present a batch of 3-5 formalized needs for user review
4. For each need, ask the user to: approve, edit, defer (with rationale), or reject

### If no needs_candidates (manual mode):

1. Ask the user to describe stakeholder needs for this block
2. Guide them through the INCOSE formalization pattern
3. Present formalized versions for approval

## Step 3: Register Approved Needs

For each approved need:

```bash
uv run scripts/needs_tracker.py --workspace .requirements-dev add \
  --statement "The [stakeholder] needs [capability]" \
  --stakeholder "[Stakeholder Name]" \
  --source-block "[block-name]" \
  --source-artifacts "CONCEPT-DOCUMENT.md" \
  --concept-dev-refs '{"sources": ["SRC-xxx"], "assumptions": []}'
```

For deferred needs:

```bash
uv run scripts/needs_tracker.py --workspace .requirements-dev defer \
  --id NEED-xxx --rationale "User rationale here"
```

For rejected needs:

```bash
uv run scripts/needs_tracker.py --workspace .requirements-dev reject \
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

## Step 5: Gate Completion

After all blocks have been processed and the user approves the complete needs set:

```bash
uv run scripts/update_state.py --state .requirements-dev/state.json set-phase needs
uv run scripts/update_state.py --state .requirements-dev/state.json pass-gate needs
```

## Step 6: Final Summary

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
