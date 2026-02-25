---
name: reqdev:requirements
description: Main workflow — develop requirements block-by-block with type-guided passes, quality checking, V&V planning, and traceability
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/references/incose-rules.md</read>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/references/type-guide.md</read>
</context>

# /reqdev:requirements -- Develop Requirements

This command guides block-by-block, type-guided requirements development with quality checking, V&V planning, and traceability linking.

<prerequisite gate="needs">
    <check>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev check-gate needs</check>
    <on-fail>The needs gate has not been passed. Please run /reqdev:needs first to formalize stakeholder needs.</on-fail>
</prerequisite>

<step sequence="1" name="load-context">
    <objective>Load session state and registries to determine resume position.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev show</script>
    <read-files>
        .requirements-dev/needs_registry.json
        .requirements-dev/requirements_registry.json
        .requirements-dev/state.json
    </read-files>
    <extract>
        - blocks: the list of functional blocks to process
        - Approved needs per block (from needs_registry.json)
        - Existing requirements (for resume)
        - progress.current_block and progress.current_type_pass (resume position)
        - progress.requirements_in_draft (unregistered drafts from previous session)
    </extract>
</step>

<step sequence="2" name="set-phase">
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev set-phase requirements</script>
</step>

<step sequence="3" name="handle-resume">
    <condition>progress.requirements_in_draft is non-empty</condition>
    <presentation>
===================================================================
RESUME: Found draft requirements from previous session
===================================================================

[List each draft REQ-xxx with its statement]

For each draft:
  [A] Register now (proceed to quality check + registration)
  [B] Discard (remove the draft)
===================================================================
    </presentation>
    <on-complete>
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '[]'</script>
    </on-complete>
</step>

<step sequence="4" name="block-type-iteration">
    <objective>For each block with approved needs, iterate over requirement types in fixed order.</objective>

    <loop over="blocks with approved needs">
        <loop over="type-passes" order="functional, performance, interface, constraint, quality">

            <step sequence="4a" name="update-progress">
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.current_block "BLOCK_NAME"</script>
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.current_type_pass "TYPE"</script>
            </step>

            <step sequence="4b" name="seed-drafts">
                <objective>Read the block's approved needs and propose 2-3 draft requirement statements for the current type.</objective>
                <rule>Use the INCOSE pattern: "The [subject] shall [action] [measurable criterion]."</rule>
            </step>

            <step sequence="4c" name="present-drafts">
                <presentation>
===================================================================
BLOCK: [block-name] | TYPE: [functional/performance/...]
===================================================================

Draft 1: The [subject] shall [action].
  Parent Need: NEED-xxx
  Priority: [suggested]

Draft 2: The [subject] shall [action].
  Parent Need: NEED-xxx
  Priority: [suggested]

-------------------------------------------------------------------
Review each draft:
  [A] Accept as-is
  [B] Edit (provide your revision)
  [C] Skip (don't create this requirement)
  [D] Add a new requirement not shown above
===================================================================
                </presentation>
            </step>

            <step sequence="4d" name="collect-attributes">
                <objective>For each accepted/edited requirement, confirm minimal attributes.</objective>
                <collect>
                    - Statement (the requirement text)
                    - Type (pre-set from the current pass)
                    - Priority (high/medium/low)
                </collect>
                <note>Optionally offer expansion to full 13 INCOSE attributes via ${CLAUDE_PLUGIN_ROOT}/references/attribute-schema.md. Do not force expansion.</note>
            </step>

            <step sequence="4e" name="quality-check-tier1">
                <objective>Run deterministic quality checks.</objective>
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/quality_rules.py check "REQUIREMENT_STATEMENT"</script>
                <on-violations>
                    Present violations with suggested rewrites.
                    User resolves each: accept rewrite, provide own rewrite, or justify and override.
                    Re-run check on revised text until it passes.
                </on-violations>
            </step>

            <step sequence="4f" name="quality-check-tier2">
                <depends-on>4e passes</depends-on>
                <objective>Run LLM semantic quality checks.</objective>
                <agent ref="agents/quality-checker.md">
                    <inputs>statement, context (block, type, parent need), existing requirements for R36 consistency</inputs>
                </agent>
                <rule>Present both tiers' results together. Only high-confidence flags block registration; medium/low are informational.</rule>
            </step>

            <step sequence="4f-split" name="split-assessment">
                <condition>Tier 1 R19 (Combinators) or Tier 2 R18 (Single Thought) flags the requirement</condition>
                <objective>Assess whether splitting is the right action for a multi-requirement statement.</objective>
                <presentation>
===================================================================
SPLIT ASSESSMENT: This statement may contain multiple requirements.
===================================================================

Original: "The system shall encrypt data at rest and shall log all
           access attempts within 5 seconds."

Trigger: [R19 Combinators / R18 Single Thought]

Proposed split:
  A: "The system shall encrypt all data at rest using AES-256."
  B: "The system shall log all access attempts within 5 seconds
      of the access event."

-------------------------------------------------------------------
Action:
  [S] Split into separate requirements (recommended)
  [R] Rewrite as a single requirement instead
  [O] Override — keep as-is with justification
===================================================================
                </presentation>

                <branch choice="S" name="split">
                    <branch condition="requirement already registered (status = registered or draft)">
                        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev split --id REQ-xxx --statements '[SPLIT_STATEMENTS_JSON]' --rationale "Split: original combined X and Y concerns (R19/R18)"</script>
                        <note>This atomically: withdraws original (with split rationale), creates N new draft requirements inheriting type/priority/block/level, records split_from: REQ-xxx in each new requirement's attributes.</note>
                        <then>For each new draft: run Tier 1 + Tier 2 quality checks → present for user confirmation → V&V planning (4g) → register (4h) → traceability (4i).</then>
                    </branch>
                    <branch condition="requirement is only a draft text (not yet in registry)">
                        <then>Replace the single draft with N separate drafts in the presentation. Continue normal flow from step 4c.</then>
                    </branch>
                </branch>
                <branch choice="R" name="rewrite">
                    <then>Return to step 4e with the revised single statement.</then>
                </branch>
                <branch choice="O" name="override">
                    <then>Record justification in attributes.r18_override or attributes.r19_override. Proceed to V&V planning.</then>
                </branch>
            </step>

            <step sequence="4g" name="vv-planning">
                <objective>Suggest verification method based on type-to-method mapping.</objective>
                <defaults>
                    <mapping type="functional" method="system test / unit test"/>
                    <mapping type="performance" method="load test / benchmark test"/>
                    <mapping type="interface" method="integration test / contract test"/>
                    <mapping type="constraint" method="inspection / analysis"/>
                    <mapping type="quality" method="demonstration / analysis"/>
                </defaults>
                <reference>${CLAUDE_PLUGIN_ROOT}/references/vv-methods.md</reference>
                <collect>Suggested method, draft success criteria (derived from statement), suggested responsible party. User confirms or modifies. Store as INCOSE attributes A6-A9.</collect>
            </step>

            <step sequence="4h" name="register-requirement">
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev add --statement "STATEMENT" --type TYPE --priority PRIORITY --source-block "BLOCK_NAME" --level 0</script>
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev register --id REQ-xxx --parent-need NEED-xxx</script>
            </step>

            <step sequence="4i" name="create-traceability">
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev link --source REQ-xxx --target NEED-xxx --type derives_from --role requirement</script>
                <script condition="concept-dev sources referenced">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev link --source REQ-xxx --target SRC-xxx --type sources --role requirement</script>
            </step>

            <step sequence="4j" name="sync-counts">
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev sync-counts</script>
            </step>

            <checkpoint name="metered-interaction" after="every 2-3 requirements">
                <rule priority="critical">NEVER generate more than 3 requirements without user confirmation.</rule>
                <presentation>
===================================================================
CHECKPOINT: [N] requirements registered for [block-name], [type] type.

  [A] Continue with more [type] requirements for this block
  [B] Move to [next-type] requirements
  [C] Review what we have so far (/reqdev:status)
  [D] Pause session (progress saved — use /reqdev:resume to continue)
===================================================================
                </presentation>
                <on-pause>
                    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.requirements_in_draft '["REQ-xxx"]'</script>
                </on-pause>
            </checkpoint>

        </loop>

        <on-type-pass-complete>
            <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev update progress.current_type_pass "NEXT_TYPE"</script>
        </on-type-pass-complete>

        <on-block-complete>
            <presentation>
===================================================================
BLOCK COMPLETE: [block-name]
===================================================================

Requirements registered: [count by type]
  Functional:   [n]
  Performance:  [n]
  Interface:    [n]
  Constraint:   [n]
  Quality:      [n]

Traceability: [n] needs covered out of [total]
Quality check pass rate: [n]%

Proceed to next block? [Y/N]
===================================================================
            </presentation>
        </on-block-complete>

    </loop>
</step>

<step sequence="5" name="review-cross-cutting-notes">
    <objective>Before closing the requirements gate, resolve all open notes targeting this phase.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev check-gate requirements</script>
    <branch condition="open notes exist">
        <presentation>
===================================================================
CROSS-CUTTING NOTES TO RESOLVE BEFORE GATE
===================================================================

The following observations were captured during earlier phases and
target the requirements phase for resolution:

[For each open note]:
  NOTE-xxx: "[text]"
    Captured during: [origin_phase]
    Category: [category]
    Related: [related_ids or "none"]

  Action:
    [A] Resolve (provide resolution and optionally a resolving REQ-xxx)
    [B] Dismiss with rationale
===================================================================
        </presentation>
        <on-resolve>
            <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev resolve --id NOTE-xxx --resolution "Addressed by REQ-015" --resolved-by REQ-015</script>
        </on-resolve>
        <on-dismiss>
            <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev dismiss --id NOTE-xxx --rationale "Not applicable — covered by existing constraint"</script>
        </on-dismiss>
        <rule>All notes targeting this phase must be resolved or dismissed before the gate can pass.</rule>
    </branch>
</step>

<step sequence="6" name="gate-completion">
    <depends-on>All blocks completed all type passes AND all cross-cutting notes resolved.</depends-on>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev pass-gate requirements</script>
</step>

<step sequence="7" name="transition-message">
    <presentation>
===================================================================
Requirements phase complete.

Total requirements registered: [N]
  By type: functional=[n], performance=[n], interface=[n],
           constraint=[n], quality=[n]
Traceability coverage: [n]%
Open TBD items: [n]
Open TBR items: [n]

Next steps:
  /reqdev:gaps     -- Check coverage gaps against concept (recommended)
  /reqdev:validate -- Run set validation
  /reqdev:deliver  -- Generate deliverable documents
  /reqdev:status   -- View full dashboard
===================================================================
    </presentation>
</step>

<behavior>
    <rule id="R1" priority="critical" scope="step-4e,4f">
        Never skip quality checking. Every requirement statement must pass through quality_rules.py before registration. No exceptions.
    </rule>
    <rule id="R2" priority="critical" scope="step-4c">
        Never auto-register. Always present requirements for user review before registration. The user must explicitly approve each requirement.
    </rule>
    <rule id="R3" priority="critical" scope="step-4">
        Respect the type order. Process types in the fixed order (functional, performance, interface, constraint, quality). Do not skip types unless the user explicitly requests it.
    </rule>
    <rule id="R4" priority="critical" scope="checkpoint">
        Meter the output. Present at most 2-3 draft requirements per round. Wait for user response before generating more.
    </rule>
    <rule id="R5" priority="high" scope="step-4a">
        Track position precisely. Update progress.current_block and progress.current_type_pass in state.json at every transition so /reqdev:resume can restore exact position.
    </rule>
    <rule id="R6" priority="high" scope="step-4d">
        Handle TBD/TBR values. When a requirement has a value that cannot be determined yet (e.g., a performance target needing research), mark it as TBD with a closure tracking field. Suggest /reqdev:research for TPM investigation.
    </rule>
    <rule id="R7" priority="medium" scope="step-4d">
        Offer attribute expansion. After the minimal 3 attributes (statement, type, priority), offer to expand to the full 13 INCOSE attributes. Reference ${CLAUDE_PLUGIN_ROOT}/references/attribute-schema.md. Do not force expansion on every requirement.
    </rule>
    <rule id="R8" priority="high" scope="step-4f">
        Use the quality-checker agent for semantic checks. After Tier 1 deterministic checks pass, invoke the quality-checker agent for the 9 semantic rules. Present both tiers' results together.
    </rule>
    <rule id="R9" priority="high" scope="all-steps">
        Capture cross-cutting observations. When a discussion during one type pass raises a concern for a different type or phase, record it immediately as a cross-cutting note:
        python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notes_tracker.py --workspace .requirements-dev add --text "Performance concern: [description]" --origin-phase requirements --target-phase requirements --related-ids "NEED-xxx" --category performance
        Inform the user: "Noted for the [target] pass — I've recorded this so we don't lose it."
    </rule>
</behavior>
