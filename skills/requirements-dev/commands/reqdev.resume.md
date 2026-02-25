---
name: reqdev:resume
description: Resume an interrupted requirements development session from the last known state, including mid-block and mid-type-pass positions
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /reqdev:resume -- Resume Interrupted Session

<step sequence="1" name="load-state">
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev show</script>
    <branch condition="no state file exists">
        <presentation>No active session found. Run /reqdev:init to start a new session.</presentation>
        <then>Stop.</then>
    </branch>
</step>

<step sequence="2" name="identify-resume-point">
    <objective>Read state.json to determine exact position.</objective>
    <read-files>.requirements-dev/state.json</read-files>
    <extract>
        - current_phase: which phase was active
        - progress.current_block: which block was being worked on (null if between blocks)
        - progress.current_type_pass: which type pass was active (null if between passes)
        - progress.type_pass_order: fixed ordering ["functional", "performance", "interface", "constraint", "quality"]
        - progress.requirements_in_draft: list of quality-checked but unregistered requirement IDs
    </extract>
</step>

<step sequence="3" name="display-resume-summary">
    <objective>Show session context and the specific resumption point.</objective>
    <presentation>
===================================================================
RESUMING SESSION
===================================================================

Session: [id]
Last Updated: [timestamp]

Current Phase: [phase name]

Progress Summary:
  [N] needs approved across [N] blocks
  [N] requirements registered ([N] baselined, [N] withdrawn)
  Traceability coverage: [N]%

-------------------------------------------------------------------
RESUMPTION POINT:
-------------------------------------------------------------------
    </presentation>

    <resume-patterns>
        <pattern name="A" condition="progress.current_block is null AND previous block completed all type passes">
            <presentation>
All type passes complete for [previous block].
Next block: [block-name]. Ready to begin functional requirements.
            </presentation>
        </pattern>

        <pattern name="B" condition="progress.current_block is set AND progress.current_type_pass is set AND no drafts pending">
            <presentation>
Block: [block-name]
Completed types: [list]
Current type: [type] (in progress)
[N] requirements registered for this block so far.
            </presentation>
        </pattern>

        <pattern name="C" condition="progress.requirements_in_draft is non-empty">
            <presentation>
Block: [block-name], Type: [type]
[N] requirements in draft (passed quality check, not yet registered):
  - [REQ-xxx]: [first 60 chars of statement]...
  - [REQ-yyy]: [first 60 chars of statement]...
These need confirmation before proceeding.
            </presentation>
        </pattern>

        <pattern name="D" condition="current_phase is needs">
            <presentation>
[N] needs approved. [N] blocks have completed needs formalization.
[N] blocks remaining.
            </presentation>
        </pattern>

        <pattern name="E" condition="current_phase is init AND init gate not passed">
            <presentation>
Initialization started but not complete. Re-run /reqdev:init.
            </presentation>
        </pattern>
    </resume-patterns>

    <presentation>
-------------------------------------------------------------------

Ready to continue?
  [A] Continue from where we left off
  [B] Show full status dashboard (/reqdev:status)
  [C] Start a different phase

===================================================================
    </presentation>
</step>

<step sequence="4" name="load-context-for-resume">
    <objective>Load the relevant artifacts based on current phase.</objective>
    <context-map>
        <phase name="init">state only</phase>
        <phase name="needs">needs_registry.json, ingestion.json (block list)</phase>
        <phase name="requirements">needs_registry.json, requirements_registry.json, traceability_registry.json</phase>
        <phase name="deliver">All registries + any existing deliverable drafts</phase>
    </context-map>
    <then>Read each artifact and provide a brief context summary.</then>
</step>

<step sequence="5" name="handle-draft-requirements">
    <rule priority="critical">When progress.requirements_in_draft is non-empty, handle drafts BEFORE continuing.</rule>
    <condition>progress.requirements_in_draft is non-empty</condition>

    <presentation>
===================================================================
DRAFT REQUIREMENTS TO RESOLVE
===================================================================

[For each draft REQ-xxx]:
  REQ-xxx: "[statement]"
    Type: [type]  Priority: [priority]  Block: [source-block]
    Quality check: Passed (Tier 1)

  Action:
    [A] Register now (with parent need assignment)
    [B] Discard (remove from registry)
===================================================================
    </presentation>

    <branch choice="A" name="register">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev register --id REQ-xxx --parent-need NEED-xxx</script>
    </branch>
    <branch choice="B" name="discard">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev withdraw --id REQ-xxx --rationale "Discarded during resume"</script>
    </branch>

    <on-complete>
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'</script>
    </on-complete>
</step>

<step sequence="6" name="continue">
    <objective>Dispatch based on user selection.</objective>
    <branch choice="A" name="continue-from-position">
        <then>Invoke the appropriate command for the current phase. If in requirements phase mid-type-pass, /reqdev:requirements detects progress.current_block and progress.current_type_pass and skips completed passes.</then>
    </branch>
    <branch choice="B" name="dashboard">
        <then>Run /reqdev:status.</then>
    </branch>
    <branch choice="C" name="different-phase">
        <collect>
            <question>Which phase would you like to work on?</question>
        </collect>
        <then>
            Verify gate prerequisites are met:
            python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev check-gate PHASE
            Warn if prerequisites are not met.
        </then>
    </branch>
</step>
