---
name: reqdev:deliver
description: Assemble and deliver requirements documents with baselining
---

# /reqdev:deliver - Deliverable Assembly

Orchestrates the deliverable generation pipeline: validates traceability, generates documents from templates, exports ReqIF, and baselines requirements.

## Procedure

### Step 1: Pre-check

Verify the `requirements` gate is passed:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev check-gate requirements
```

If the gate is NOT passed, inform the user:
> The requirements phase is not complete. Run `/reqdev:requirements` to complete all requirement blocks before delivering.

Stop and wait for user action.

### Step 2: Validate Traceability

Run traceability checks:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev orphans
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev coverage
```

Present results to the user:
- Show any orphan needs (needs with no derived requirements)
- Show any orphan requirements (requirements with no parent need)
- Show coverage percentage

**Warn but do not block delivery.** Gaps are reported in the traceability matrix.

### Step 3: Generate Deliverables

Invoke the `document-writer` agent for each deliverable:

1. **REQUIREMENTS-SPECIFICATION.md** - Requirements organized by block and type
2. **TRACEABILITY-MATRIX.md** - Full chain from source to need to requirement to V&V
3. **VERIFICATION-MATRIX.md** - All requirements with V&V methods and criteria

The agent reads from:
- `${CLAUDE_PLUGIN_ROOT}/templates/requirements-specification.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/traceability-matrix.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/verification-matrix.md`
- `.requirements-dev/needs_registry.json`
- `.requirements-dev/requirements_registry.json`
- `.requirements-dev/traceability_registry.json`

Write generated documents to `.requirements-dev/deliverables/`.

### Step 4: User Approval

Present each deliverable for review:

> **Requirements Specification** generated. Please review:
> [Show document content or summary]
> Approve? (yes/edit/reject)

Repeat for each document. All three must be approved before proceeding.

### Step 5: ReqIF Export

Run the ReqIF export:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/reqif_export.py \
    --requirements .requirements-dev/requirements_registry.json \
    --needs .requirements-dev/needs_registry.json \
    --traceability .requirements-dev/traceability_registry.json \
    --output .requirements-dev/exports/requirements.reqif
```

If the `reqif` package is not installed, inform the user and continue. ReqIF is optional.

### Step 6: Baselining

After all deliverables are approved, baseline all registered requirements:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev baseline --all
```

This transitions every registered requirement to `baselined` status. Withdrawn requirements are unaffected. Draft requirements generate warnings.

### Step 7: Review Cross-Cutting Notes

Before closing the deliver gate, check for open notes targeting this phase:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev check-gate deliver
```

If open notes exist, present them and guide the user to resolve or dismiss each one before proceeding (see SKILL.md Cross-Cutting Notes section for resolution flow). All notes targeting this phase must be resolved or dismissed before the gate can pass.

### Step 8: State Updates

Record deliverable artifacts and pass the deliver gate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-artifact deliver REQUIREMENTS-SPECIFICATION.md
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-artifact deliver TRACEABILITY-MATRIX.md
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-artifact deliver VERIFICATION-MATRIX.md
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev pass-gate deliver
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-phase deliver
```

### Step 9: Summary

Display delivery summary:

```
Delivery Complete
-----------------
Requirements baselined: {count}
Deliverables generated:
  - REQUIREMENTS-SPECIFICATION.md
  - TRACEABILITY-MATRIX.md
  - VERIFICATION-MATRIX.md
ReqIF export: {Generated | Skipped (reqif package not installed)}

Phase: deliver (gate passed)
Next: /reqdev:validate or /reqdev:decompose
```
