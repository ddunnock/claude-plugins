---
name: reqdev:gaps
description: Discover coverage gaps in needs and requirements against the concept architecture
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /reqdev:gaps - Gap Analysis

Proactively discovers what is missing from the needs and requirements sets to fully actualize the concept. Runs deterministic coverage metrics followed by semantic gap discovery via the gap-analyst agent.

Can be run after any phase gate: after needs (concept-to-need coverage), after requirements (full coverage analysis), or after deliver (pre-validation gap check).

<prerequisite gate="needs">
    <check>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev check-gate needs</check>
    <on-fail>The needs phase is not complete. Run /reqdev:needs to formalize stakeholder needs before running gap analysis.</on-fail>
</prerequisite>

<step sequence="1" name="detect-scope">
    <objective>Check the current phase to determine which analyses are most relevant.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev show</script>
    <scope-map>
        <phase name="needs">Concept coverage, block need coverage, stakeholder balance</phase>
        <phase name="requirements">All analyses including block×type matrix, V&V, priority, sufficiency</phase>
        <phase name="deliver or later">All analyses (full gap assessment before validation/decomposition)</phase>
    </scope-map>
    <presentation>Running gap analysis at **{phase}** scope. {brief description of what will be checked}</presentation>
</step>

<step sequence="2" name="run-deterministic-gap-analysis">
    <objective>Run deterministic coverage metrics.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gap_analyzer.py --workspace .requirements-dev analyze</script>
    <output-categories>
        - block_type_matrix: Block × requirement type coverage
        - concept_coverage: Concept-dev source/assumption traceability
        - block_asymmetry: Related blocks with uneven coverage
        - vv_coverage: V&V method assignment gaps
        - priority_alignment: Need-to-requirement priority mismatch
        - need_sufficiency: Needs with 0-1 derived requirements
        - block_need_coverage: Blocks without approved needs
    </output-categories>
    <output-file>.requirements-dev/gap_analysis.json</output-file>
</step>

<step sequence="2.5" name="assumption-health-check">
    <objective>Flag assumption lifecycle issues as additional gap findings.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --workspace .requirements-dev/ summary</script>
    <findings>
        <severity level="critical">High/critical-impact assumptions still active (unvalidated) late in the lifecycle</severity>
        <severity level="high">Challenged assumptions with no resolution (neither invalidated nor reaffirmed)</severity>
        <severity level="medium">Concept-dev assumptions never reviewed during requirements development</severity>
    </findings>
    <note>Include assumption health in the gap-analyst agent context.</note>
</step>

<step sequence="3" name="semantic-gap-discovery">
    <objective>Launch the gap-analyst agent for deeper semantic analysis.</objective>
    <agent ref="agents/gap-analyst.md">
        <inputs>
            - Gap analysis JSON from step 2
            - Full registries: needs_registry.json, requirements_registry.json, traceability_registry.json
            - Block architecture from state.json
            - Concept-dev artifacts from ingestion.json (if available)
            - Current phase context
        </inputs>
        <outputs>JSON array of findings with gap_id, category, severity, finding, affected_entities, suggested_action, evidence</outputs>
    </agent>
</step>

<step sequence="4" name="present-findings">
    <objective>Present findings to the user grouped by severity.</objective>

    <findings-presentation>
        <severity level="critical" label="Concept functionality not captured at all">
            - Blocks with zero approved needs
            - Concept sources with no corresponding needs
            - Blocks with zero requirements of any type
        </severity>
        <severity level="high" label="Systematic missing coverage">
            - Requirement types missing from blocks where they should exist
            - High-priority requirements without V&V methods
            - Related blocks with severe asymmetry
        </severity>
        <severity level="medium" label="May need attention">
            - Needs with only 1 derived requirement that appears insufficient
            - Priority misalignment between needs and requirements
            - Under-represented stakeholder groups
        </severity>
        <severity level="low-info" label="Acknowledged for record or likely intentional">
            - Minor type coverage gaps with reasonable explanation
            - Expected asymmetry between blocks
        </severity>
    </findings-presentation>

    <per-finding-format>
[GAP-{id}] [{severity}] {category}
  Finding: {finding}
  Affected: {affected_entities}
  Suggested action: {suggested_action}
    </per-finding-format>
</step>

<step sequence="5" name="interactive-resolution">
    <objective>For each finding (starting with critical, then high), prompt the user for action.</objective>

    <resolution-protocol>
        <option value="1" name="create-need">
            <action>Formalize a new stakeholder need.</action>
            <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev add --statement "USER_STATEMENT" --stakeholder "STAKEHOLDER" --source-block "BLOCK"</script>
        </option>
        <option value="2" name="create-requirement">
            <action>Add a requirement to address this gap.</action>
            <then>Follow the standard quality-check pipeline from /reqdev:requirements step 4 (draft → Tier 1 check → Tier 2 check → register).</then>
        </option>
        <option value="3" name="cross-cutting-note">
            <action>Capture for a future phase.</action>
            <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev add --text "FINDING" --source-phase "CURRENT_PHASE" --target-phase "TARGET_PHASE" --category "CATEGORY"</script>
        </option>
        <option value="4" name="accept-gap">
            <action>Acknowledge and record with rationale.</action>
        </option>
        <option value="5" name="defer">
            <action>Revisit later.</action>
        </option>
    </resolution-protocol>
</step>

<step sequence="6" name="gap-summary">
    <presentation>
Gap Analysis Complete ({phase} scope)
--------------------------------------
Critical gaps:    {count} ({resolved} resolved, {deferred} deferred, {accepted} accepted)
High gaps:        {count} ({resolved} resolved, {deferred} deferred, {accepted} accepted)
Medium gaps:      {count} ({resolved} resolved, {deferred} deferred, {accepted} accepted)
Low/Info gaps:    {count}

New needs created:        {count}
New requirements created: {count}
Cross-cutting notes added: {count}

Next: /reqdev:requirements (if needs-phase gaps resolved)
      /reqdev:validate (if requirements-phase gaps resolved)
      /reqdev:deliver (if ready to generate deliverables)
    </presentation>
</step>

<behavior>
    <rule id="G1" priority="critical" scope="step-5">
        Present, don't prescribe. The agent identifies gaps; the user decides action. Never auto-create needs or requirements from gap findings.
    </rule>
    <rule id="G2" priority="high" scope="step-4">
        Context matters. A block missing performance requirements may be intentional (static configuration block) or critical (API gateway block). The agent's reasoning helps the user decide.
    </rule>
    <rule id="G3" priority="high" scope="step-5">
        One finding at a time. Present findings individually for user decision, starting with highest severity.
    </rule>
    <rule id="G4" priority="high" scope="step-5">
        Capture cross-cutting notes for any gap that belongs to a phase not yet reached. This ensures the observation is not lost.
    </rule>
    <rule id="G5" priority="low" scope="all">
        Re-run is safe. Gap analysis can be run multiple times. Each run overwrites gap_analysis.json with fresh metrics.
    </rule>
</behavior>
