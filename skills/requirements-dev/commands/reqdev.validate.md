---
name: reqdev:validate
description: Cross-cutting validation sweep for the requirements set
---

# /reqdev:validate - Validation Sweep

Orchestrates cross-block validation of the full requirements set. Runs deterministic checks, presents findings interactively, and optionally launches the skeptic agent for feasibility review.

## Procedure

### Step 1: Pre-check

Verify the `deliver` gate is passed (requirements must be baselined before validation):

```bash
python3 scripts/update_state.py --workspace .requirements-dev check-gate deliver
```

If the gate is NOT passed, inform the user:
> The deliver phase is not complete. Run `/reqdev:deliver` to baseline requirements before running the validation sweep.

Stop and wait for user action.

### Step 2: Run Deterministic Validation

Run all set validation checks:

```bash
python3 scripts/set_validator.py --workspace .requirements-dev validate
```

This produces JSON output with findings grouped by category:
- `interface_coverage` - block pairs with/without interface requirements
- `duplicates` - near-duplicate requirements across blocks
- `terminology` - inconsistent term usage across blocks
- `uncovered_needs` - approved needs with no derived requirements
- `tbd_tbr` - open TBD/TBR items
- `incose_set` - INCOSE C10-C15 set characteristic results

### Step 3: Present Findings

Present findings to the user as a prioritized list, grouped by severity:

#### Critical (blocks delivery readiness)
- **Missing interface requirements**: For each block pair flagged as `missing`, prompt the user to write interface requirements or confirm the relationship is not relevant.
- **Uncovered needs**: For each approved need with no derived requirement, prompt the user to either write requirements or defer/reject the need.
- **INCOSE C10 (Completeness) failures**: Same as uncovered needs above.
- **INCOSE C15 (Correctness) failures**: Requirements not traced to approved needs.

#### Warning (should address before final delivery)
- **Near-duplicate requirements**: Present each pair with similarity score. Ask the user to decide: merge (withdraw one), differentiate (clarify statements), or accept (both are intentional).
- **Terminology inconsistencies**: Present term variants and affected blocks. Propose a canonical term and offer to update requirement statements.
- **Open TBD items**: Present each TBD with its requirement ID. Prompt for resolution value.
- **Open TBR items**: Present each TBR with its requirement ID. Prompt for review decision.
- **INCOSE C14 (Validatability)**: Requirements without V&V methods.

#### Info
- **INCOSE C11 (Consistency)**: Unresolved conflicts (if any).
- **INCOSE C13 (Comprehensibility)**: Same as terminology above.
- **Resolved TBD/TBR count**: For reference.

### Step 4: Cross-Cutting Category Checklist

Present the cross-cutting category checklist to the user:

> Which cross-cutting concerns apply to this system? Select all that apply:
> - Security
> - Reliability / Availability
> - Scalability / Performance
> - Maintainability
> - Data integrity
> - Logging / Observability
> - Regulatory compliance
> - Accessibility
> - Other (specify)

For each selected category:
1. Search registered requirements for coverage of that category.
2. Identify blocks that have NO requirements addressing the category.
3. Present gaps to the user and prompt for action (write new requirements or accept the gap).

### Step 5: INCOSE C12 Feasibility Review (Optional)

If the user requests feasibility review, or if any performance/constraint requirements have numeric targets that warrant scrutiny:

> Would you like to run the skeptic agent for a rigorous feasibility and coverage review?

If yes, launch the `skeptic` agent with:
- The full requirements set from `requirements_registry.json`
- The validation findings from Step 2
- The block relationship map from `state.json`
- Any coverage claims made during Step 4

Present the skeptic's findings to the user. For each finding with status `disputed` or `unverified`, prompt the user for action.

### Step 6: Resolution Actions

For any issues the user decides to fix during validation:

- **Write new requirements**: Guide through the standard pipeline - quality check, V&V plan, register, trace. Use the same flow as `/reqdev:requirements`.
- **Merge duplicates**: Withdraw one requirement, update traceability links.
- **Update terminology**: Edit requirement statements via `requirement_tracker.py update`.
- **Resolve TBD/TBR**: Update the requirement's `tbd_tbr` field.
- **Defer/reject needs**: Use `needs_tracker.py` to change need status.

After each fix, re-run the relevant check to confirm resolution:

```bash
python3 scripts/set_validator.py --workspace .requirements-dev check-duplicates
python3 scripts/set_validator.py --workspace .requirements-dev check-terminology
python3 scripts/set_validator.py --workspace .requirements-dev check-coverage
python3 scripts/set_validator.py --workspace .requirements-dev check-tbd
```

### Step 7: Validation Summary

After all findings are addressed (or accepted), display the summary:

```
Validation Sweep Complete
-------------------------
Interface coverage:    {N}/{M} block pairs covered
Duplicates resolved:   {count}
Terminology fixes:     {count}
Uncovered needs:       {count} remaining
TBD items:             {open} open, {resolved} resolved
TBR items:             {open} open

INCOSE Set Characteristics:
  C10 Completeness:      {Pass/Fail}
  C11 Consistency:       {Pass/Fail}
  C12 Feasibility:       {Reviewed/Skipped}
  C13 Comprehensibility: {Pass/Fail}
  C14 Validatability:    {Pass/Fail}
  C15 Correctness:       {Pass/Fail}

Next: /reqdev:deliver (re-deliver if changes made) or /reqdev:decompose
```
