---
name: reqdev:deliver
description: Assemble and deliver requirements documents with baselining
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /reqdev:deliver - Deliverable Assembly

Orchestrates the deliverable generation pipeline: validates traceability, generates documents from templates, exports ReqIF, and baselines requirements.

<prerequisite gate="requirements">
    <check>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev check-gate requirements</check>
    <on-fail>The requirements phase is not complete. Run /reqdev:requirements to complete all requirement blocks before delivering.</on-fail>
</prerequisite>

<step sequence="1" name="validate-traceability">
    <objective>Run traceability checks and present coverage to the user.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev orphans</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev coverage</script>
    <present>
        - Orphan needs (needs with no derived requirements)
        - Orphan requirements (requirements with no parent need)
        - Coverage percentage
    </present>
    <rule>Warn but do not block delivery. Gaps are reported in the traceability matrix.</rule>
</step>

<step sequence="2" name="generate-deliverables">
    <objective>Invoke the document-writer agent for each deliverable.</objective>
    <agent ref="agents/document-writer.md">
        <deliverable name="REQUIREMENTS-SPECIFICATION.md">Requirements organized by block and type</deliverable>
        <deliverable name="TRACEABILITY-MATRIX.md">Full chain from source to need to requirement to V&V</deliverable>
        <deliverable name="VERIFICATION-MATRIX.md">All requirements with V&V methods and criteria</deliverable>
    </agent>
    <inputs>
        <template>${CLAUDE_PLUGIN_ROOT}/templates/requirements-specification.md</template>
        <template>${CLAUDE_PLUGIN_ROOT}/templates/traceability-matrix.md</template>
        <template>${CLAUDE_PLUGIN_ROOT}/templates/verification-matrix.md</template>
        <registry>.requirements-dev/needs_registry.json</registry>
        <registry>.requirements-dev/requirements_registry.json</registry>
        <registry>.requirements-dev/traceability_registry.json</registry>
    </inputs>
    <output-dir>.requirements-dev/deliverables/</output-dir>
</step>

<step sequence="3" name="user-approval">
    <objective>Present each deliverable for review. All three must be approved before proceeding.</objective>
    <loop over="each deliverable">
        <presentation>
**{deliverable name}** generated. Please review:
[Show document content or summary]
Approve? (yes/edit/reject)
        </presentation>
    </loop>
    <gate type="user-confirm">All three documents must be approved.</gate>
</step>

<step sequence="4" name="reqif-export">
    <objective>Export optional ReqIF interchange format.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/reqif_export.py --requirements .requirements-dev/requirements_registry.json --needs .requirements-dev/needs_registry.json --traceability .requirements-dev/traceability_registry.json --output .requirements-dev/exports/requirements.reqif</script>
    <branch condition="reqif package not installed">
        <then>Inform the user and continue. ReqIF is optional.</then>
    </branch>
</step>

<step sequence="5" name="baselining">
    <depends-on>All deliverables approved (step 3).</depends-on>
    <objective>Transition every registered requirement to baselined status.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev baseline --all</script>
    <note>Withdrawn requirements are unaffected. Draft requirements generate warnings.</note>
</step>

<step sequence="6" name="review-cross-cutting-notes">
    <objective>Before closing the deliver gate, resolve all open notes targeting this phase.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev check-gate deliver</script>
    <branch condition="open notes exist">
        <then>Present notes and guide user to resolve or dismiss each one. All notes targeting this phase must be resolved or dismissed before the gate can pass.</then>
    </branch>
</step>

<step sequence="7" name="state-updates">
    <objective>Record deliverable artifacts and pass the deliver gate.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-artifact deliver REQUIREMENTS-SPECIFICATION.md</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-artifact deliver TRACEABILITY-MATRIX.md</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-artifact deliver VERIFICATION-MATRIX.md</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev pass-gate deliver</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --workspace .requirements-dev set-phase deliver</script>
</step>

<step sequence="8" name="summary">
    <presentation>
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
    </presentation>
</step>
