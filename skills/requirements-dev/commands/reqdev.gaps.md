---
name: reqdev:gaps
description: Discover coverage gaps in needs and requirements against the concept architecture
---

# /reqdev:gaps - Gap Analysis

Proactively discovers what is missing from the needs and requirements sets to fully actualize the concept. Runs deterministic coverage metrics followed by semantic gap discovery via the gap-analyst agent.

Can be run after any phase gate: after needs (concept-to-need coverage), after requirements (full coverage analysis), or after deliver (pre-validation gap check).

## Procedure

### Step 1: Pre-check

Verify at least the `needs` gate is passed (needs must exist to analyze gaps):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev check-gate needs
```

If the gate is NOT passed, inform the user:
> The needs phase is not complete. Run `/reqdev:needs` to formalize stakeholder needs before running gap analysis.

Stop and wait for user action.

### Step 2: Detect Scope

Check the current phase to determine which analyses are most relevant:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev show
```

**Phase-dependent scope:**

| Current Phase | Analyses to Emphasize |
|---------------|----------------------|
| needs | Concept coverage, block need coverage, stakeholder balance |
| requirements | All analyses including block×type matrix, V&V, priority, sufficiency |
| deliver or later | All analyses (full gap assessment before validation/decomposition) |

Inform the user of the scope:
> Running gap analysis at **{phase}** scope. {brief description of what will be checked}

### Step 3: Run Deterministic Gap Analysis

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gap_analyzer.py --workspace .requirements-dev analyze
```

This produces a JSON report with seven gap categories:
- `block_type_matrix` — Block × requirement type coverage
- `concept_coverage` — Concept-dev source/assumption traceability
- `block_asymmetry` — Related blocks with uneven coverage
- `vv_coverage` — V&V method assignment gaps
- `priority_alignment` — Need-to-requirement priority mismatch
- `need_sufficiency` — Needs with 0-1 derived requirements
- `block_need_coverage` — Blocks without approved needs

The report is saved to `.requirements-dev/gap_analysis.json`.

### Step 3.5: Assumption Health Check

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --workspace .requirements-dev/ summary
```

Flag assumption health issues as additional gap findings:
- **Critical**: High/critical-impact assumptions still active (unvalidated) late in the lifecycle
- **High**: Challenged assumptions with no resolution (neither invalidated nor reaffirmed)
- **Medium**: Concept-dev assumptions never reviewed during requirements development

Include assumption health in the gap-analyst agent context.

### Step 4: Semantic Gap Discovery

Launch the `gap-analyst` agent with:
- The gap analysis JSON from Step 3
- The full registries: needs_registry.json, requirements_registry.json, traceability_registry.json
- The block architecture from state.json
- Concept-dev artifacts from ingestion.json (if available)
- The current phase context

Reference: `${CLAUDE_PLUGIN_ROOT}/agents/gap-analyst.md`

The agent returns a JSON array of findings, each with gap_id, category, severity, finding, affected_entities, suggested_action, and evidence.

### Step 5: Present Findings

Present findings to the user grouped by severity:

#### Critical
Gaps that indicate concept functionality is not captured at all:
- Blocks with zero approved needs
- Concept sources with no corresponding needs
- Blocks with zero requirements of any type

#### High
Gaps that indicate systematic missing coverage:
- Requirement types missing from blocks where they should exist
- High-priority requirements without V&V methods
- Related blocks with severe asymmetry

#### Medium
Gaps that may need attention:
- Needs with only 1 derived requirement that appears insufficient
- Priority misalignment between needs and requirements
- Under-represented stakeholder groups

#### Low / Info
Gaps acknowledged for record or likely intentional:
- Minor type coverage gaps with reasonable explanation
- Expected asymmetry between blocks

For each finding, display:
```
[GAP-{id}] [{severity}] {category}
  Finding: {finding}
  Affected: {affected_entities}
  Suggested action: {suggested_action}
```

### Step 6: Interactive Resolution

For each finding (starting with critical, then high), prompt the user:

> How would you like to address **GAP-{id}**?
> 1. **Create need** — formalize a new stakeholder need
> 2. **Create requirement** — add a requirement to address this gap
> 3. **Add cross-cutting note** — capture for a future phase
> 4. **Accept gap** — acknowledge and record with rationale
> 5. **Defer** — revisit later

For each user decision:

**Create need:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev add \
  --statement "{user-provided statement}" \
  --stakeholder "{stakeholder}" \
  --source-block "{block}"
```

**Create requirement:**
Follow the standard quality-check pipeline from `/reqdev:requirements` step 4 (draft → Tier 1 check → Tier 2 check → register).

**Add cross-cutting note:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev add \
  --text "{finding}" \
  --source-phase "{current_phase}" \
  --target-phase "{appropriate_phase}" \
  --category "{category}"
```

**Accept or Defer:**
Record the decision. The gap_analysis.json file stores the finding; the user's rationale is documented in the session.

### Step 7: Gap Summary

After all findings are addressed (or deferred/accepted), display:

```
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
```

## Behavioral Rules

1. **Present, don't prescribe.** The agent identifies gaps; the user decides action. Never auto-create needs or requirements from gap findings.
2. **Context matters.** A block missing performance requirements may be intentional (static configuration block) or critical (API gateway block). The agent's reasoning helps the user decide.
3. **One finding at a time.** Present findings individually for user decision, starting with highest severity.
4. **Capture cross-cutting notes** for any gap that belongs to a phase not yet reached. This ensures the observation is not lost.
5. **Re-run is safe.** Gap analysis can be run multiple times. Each run overwrites gap_analysis.json with fresh metrics.
