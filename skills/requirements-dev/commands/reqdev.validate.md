---
name: reqdev:validate
description: Cross-cutting validation sweep for the requirements set
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/references/incose-rules.md</read>
</context>

# /reqdev:validate - Validation Sweep

Orchestrates cross-block validation of the full requirements set. Runs deterministic checks, presents findings interactively, and optionally launches the skeptic agent for feasibility review.

<prerequisite gate="deliver">
    <check>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev check-gate deliver</check>
    <on-fail>The deliver phase is not complete. Run /reqdev:deliver to baseline requirements before running the validation sweep.</on-fail>
</prerequisite>

<step sequence="1" name="run-deterministic-validation">
    <objective>Run all set validation checks.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/set_validator.py --workspace .requirements-dev validate</script>
    <output-categories>
        - interface_coverage: block pairs with/without interface requirements
        - duplicates: near-duplicate requirements across blocks
        - terminology: inconsistent term usage across blocks
        - uncovered_needs: approved needs with no derived requirements
        - tbd_tbr: open TBD/TBR items
        - incose_set: INCOSE C10-C15 set characteristic results
    </output-categories>
</step>

<step sequence="2" name="present-findings">
    <objective>Present findings to the user grouped by severity.</objective>

    <findings-presentation>
        <severity level="critical" label="blocks delivery readiness">
            <finding type="missing-interfaces">For each block pair flagged as missing, prompt the user to write interface requirements or confirm the relationship is not relevant.</finding>
            <finding type="uncovered-needs">For each approved need with no derived requirement, prompt the user to either write requirements or defer/reject the need.</finding>
            <finding type="incose-c10">INCOSE C10 (Completeness) failures: same as uncovered needs above.</finding>
            <finding type="incose-c15">INCOSE C15 (Correctness) failures: requirements not traced to approved needs.</finding>
        </severity>

        <severity level="warning" label="should address before final delivery">
            <finding type="duplicates">Present each pair with similarity score. User decides: merge (withdraw one), differentiate (clarify statements), or accept (both intentional).</finding>
            <finding type="terminology">Present term variants and affected blocks. Propose a canonical term and offer to update requirement statements.</finding>
            <finding type="tbd-open">Present each TBD with its requirement ID. Prompt for resolution value.</finding>
            <finding type="tbr-open">Present each TBR with its requirement ID. Prompt for review decision.</finding>
            <finding type="incose-c14">INCOSE C14 (Validatability): requirements without V&V methods.</finding>
        </severity>

        <severity level="info">
            <finding type="incose-c11">INCOSE C11 (Consistency): unresolved conflicts (if any).</finding>
            <finding type="incose-c13">INCOSE C13 (Comprehensibility): same as terminology above.</finding>
            <finding type="resolved-tbd-tbr">Resolved TBD/TBR count for reference.</finding>
        </severity>
    </findings-presentation>
</step>

<step sequence="3" name="cross-cutting-category-checklist">
    <objective>Check cross-cutting concern coverage.</objective>
    <collect>
        <question>Which cross-cutting concerns apply to this system? Select all that apply:</question>
        <options>
            - Security
            - Reliability / Availability
            - Scalability / Performance
            - Maintainability
            - Data integrity
            - Logging / Observability
            - Regulatory compliance
            - Accessibility
            - Other (specify)
        </options>
    </collect>
    <loop over="each selected category">
        <step sequence="3a">
            <then>Search registered requirements for coverage of that category.</then>
        </step>
        <step sequence="3b">
            <then>Identify blocks with NO requirements addressing the category.</then>
        </step>
        <step sequence="3c">
            <then>Present gaps to the user and prompt for action (write new requirements or accept the gap).</then>
        </step>
    </loop>
</step>

<step sequence="4" name="feasibility-review">
    <objective>INCOSE C12 Feasibility Review (optional).</objective>
    <condition>User requests feasibility review, OR performance/constraint requirements have numeric targets warranting scrutiny.</condition>
    <collect>
        <question>Would you like to run the skeptic agent for a rigorous feasibility and coverage review?</question>
    </collect>
    <branch condition="user says yes">
        <agent ref="agents/skeptic.md">
            <inputs>
                - Full requirements set from requirements_registry.json
                - Validation findings from step 1
                - Block relationship map from state.json
                - Coverage claims from step 3
            </inputs>
        </agent>
        <then>Present the skeptic's findings. For each finding with status disputed or unverified, prompt the user for action.</then>
    </branch>
</step>

<step sequence="5" name="resolution-actions">
    <objective>Guide the user through fixing issues identified during validation.</objective>
    <resolution-options>
        <option name="write-requirements">Guide through the standard pipeline (quality check, V&V plan, register, trace). Use the same flow as /reqdev:requirements.</option>
        <option name="merge-duplicates">Withdraw one requirement, update traceability links.</option>
        <option name="update-terminology">Edit requirement statements via requirement_tracker.py update.</option>
        <option name="resolve-tbd-tbr">Update the requirement's tbd_tbr field.</option>
        <option name="defer-reject-needs">Use needs_tracker.py to change need status.</option>
    </resolution-options>
    <on-fix>
        Re-run the relevant check to confirm resolution:
        <script name="check-duplicates">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/set_validator.py --workspace .requirements-dev check-duplicates</script>
        <script name="check-terminology">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/set_validator.py --workspace .requirements-dev check-terminology</script>
        <script name="check-coverage">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/set_validator.py --workspace .requirements-dev check-coverage</script>
        <script name="check-tbd">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/set_validator.py --workspace .requirements-dev check-tbd</script>
    </on-fix>
</step>

<step sequence="6" name="validation-summary">
    <presentation>
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
    </presentation>
</step>
