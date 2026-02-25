---
name: reqdev:needs
description: Formalize stakeholder needs per functional block
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /reqdev:needs -- Formalize Stakeholder Needs

This command guides needs formalization from ingestion candidates into INCOSE-pattern need statements.

<prerequisite gate="init">
    <check>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json check-gate init</check>
    <on-fail>The init gate has not been passed. Please run /reqdev:init first.</on-fail>
</prerequisite>

<step sequence="1" name="load-context">
    <objective>Load ingestion data and current state.</objective>
    <read-files>
        .requirements-dev/ingestion.json
    </read-files>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json show</script>
    <extract>
        - blocks: the list of functional blocks to process
        - needs_candidates: pre-extracted need candidates (if concept-dev was used)
        - Current needs_total count (to know if resuming)
    </extract>
</step>

<step sequence="2" name="per-block-iteration">
    <objective>For each block defined in state.json, formalize stakeholder needs.</objective>

    <loop over="blocks in state.json">

        <branch condition="needs_candidates exist for this block (from ingestion)">

            <step sequence="2a" name="present-candidates">
                <presentation>
1. [★★★] [HIGH] "The operator needs to monitor system health..." (auth, CONCEPT-DOCUMENT.md)
2. [★★]  [MED]  "The user needs to configure alert thresholds..." (monitoring, CONCEPT-DOCUMENT.md)
                </presentation>
            </step>

            <step sequence="2b" name="formalize-needs">
                <objective>Formalize each candidate into INCOSE pattern.</objective>
                <pattern>
                    Format: [Stakeholder] needs [capability] [optional qualifier]
                    Use "should" for expectations, not "shall" (which is for requirements).
                    Must be solution-free: describe what is needed, not how to achieve it.
                </pattern>
                <examples>
                    <good>"The operator needs to monitor system health metrics in real-time"</good>
                    <bad reason="prescribes solution">"The operator needs a Grafana dashboard"</bad>
                    <bad reason="uses obligation language — this is a requirement, not a need">"The system shall display metrics"</bad>
                </examples>
            </step>

            <step sequence="2c" name="split-assessment">
                <objective>Before presenting, assess each formalized need for compound concerns.</objective>
                <rule>A need is compound if it describes two or more independent capabilities that could be satisfied separately.</rule>
                <indicators>
                    - Coordinating conjunctions joining distinct capabilities ("and", "as well as", "in addition to")
                    - Multiple verb phrases describing unrelated actions
                    - Mixed concern areas (e.g., monitoring AND configuration in one statement)
                </indicators>
                <examples>
                    <compound>"The operator needs to monitor health metrics and configure alert thresholds" → Split (monitoring ≠ configuration)</compound>
                    <not-compound>"The operator needs to monitor CPU and memory health metrics" → Keep (both are monitoring)</not-compound>
                </examples>
                <branch condition="compound need detected">
                    <presentation>
Candidate 3 appears to contain multiple concerns:
  Original: "The operator needs to monitor health metrics and configure
             alert thresholds for critical events"
  Proposed split:
    3a: "The operator needs to monitor system health metrics in real-time"
    3b: "The operator needs to configure alert thresholds for critical events"

  [S] Split into 3a and 3b (recommended)
  [K] Keep as a single need
  [E] Edit the original
                    </presentation>
                </branch>
            </step>

            <step sequence="2d" name="batch-review">
                <objective>Present a batch of 3-5 formalized needs (with any split proposals inline) for user review.</objective>
                <collect>For each need, user chooses: approve, edit, split (if compound), defer (with rationale), or reject.</collect>
            </step>

        </branch>

        <branch condition="no needs_candidates (manual mode)">
            <step sequence="2-manual" name="manual-needs">
                <collect>
                    <question>Describe stakeholder needs for this block.</question>
                </collect>
                <then>Guide through INCOSE formalization pattern. Assess for compound concerns using the same split assessment as above. Present formalized versions for approval.</then>
            </step>
        </branch>

    </loop>
</step>

<step sequence="3" name="register-approved-needs">
    <objective>Register each approved need in the needs registry with traceability.</objective>

    <script name="register">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev add --statement "The [stakeholder] needs [capability]" --stakeholder "STAKEHOLDER" --source-block "BLOCK_NAME" --source-artifacts "CONCEPT-DOCUMENT.md" --concept-dev-refs '{"sources": ["SRC-xxx"], "assumptions": []}'</script>

    <script name="concept-origin-link" condition="need derived from ingestion candidate">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev link --source NEED-xxx --target "CONCEPT-DOCUMENT.md:Section Name" --type concept_origin --role need</script>
    <note>Provides backward traceability from the need to the specific concept-dev artifact and section that originated it, per INCOSE SE Handbook §4.3.7.</note>

    <script name="split-need" condition="previously registered need found to be compound">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev split --id NEED-xxx --statements '[SPLIT_STATEMENTS_JSON]' --rationale "Split: original combined X and Y concerns"</script>
    <note>Rejects the original and creates new approved needs inheriting stakeholder, source_block, and concept-dev references.</note>

    <script name="defer-need">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev defer --id NEED-xxx --rationale "USER_RATIONALE"</script>

    <script name="reject-need">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/needs_tracker.py --workspace .requirements-dev reject --id NEED-xxx --rationale "USER_RATIONALE"</script>
</step>

<step sequence="4" name="block-summary">
    <objective>After processing each block, display counts.</objective>
    <presentation>
BLOCK: [block-name]
  Approved:  N needs
  Deferred:  M needs
  Rejected:  R needs
    </presentation>
</step>

<step sequence="5" name="review-cross-cutting-notes">
    <objective>Before closing the needs gate, resolve all open notes targeting this phase.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev check-gate needs</script>
    <branch condition="open notes exist">
        <then>Present notes and guide user to resolve or dismiss each one before proceeding (see SKILL.md Cross-Cutting Notes section for resolution flow).</then>
    </branch>

    <rule scope="step-2" priority="high">
        Capture forward-looking notes: During needs formalization, if the user raises observations that clearly belong in the requirements or later phases (e.g., "we'll need to benchmark this" or "this will require an interface spec"), capture them immediately:
    </rule>
    <script name="capture-forward-note">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev add --text "Needs benchmarking for latency target" --origin-phase needs --target-phase research --related-ids "NEED-xxx" --category performance</script>
    <note>Inform the user: "Good catch — I've noted that for the [target] phase so we don't lose it."</note>
</step>

<step sequence="6" name="gate-completion">
    <depends-on>All blocks processed, all cross-cutting notes resolved, user approves complete needs set.</depends-on>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json set-phase needs</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json pass-gate needs</script>
</step>

<step sequence="7" name="final-summary">
    <presentation>
NEEDS FORMALIZATION COMPLETE
============================
Total needs:     N
  Approved:      A
  Deferred:      D
  Rejected:      R
Blocks covered:  B

Next steps:
  /reqdev:gaps         -- Check concept-to-needs coverage (recommended)
  /reqdev:requirements -- Develop requirements from approved needs
  /reqdev:status       -- View current session status
    </presentation>
</step>
