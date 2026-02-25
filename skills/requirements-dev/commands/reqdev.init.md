---
name: reqdev:init
description: Initialize requirements-dev session and ingest concept-dev artifacts
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /reqdev:init -- Initialize Requirements Development Session

This command initializes the requirements development workspace and ingests concept-dev artifacts.

<step sequence="1" name="initialize-workspace">
    <objective>Create the .requirements-dev/ workspace with state.json.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_session.py PROJECT_PATH</script>
    <note>PROJECT_PATH is the project root (typically the current working directory).</note>
    <branch condition="workspace already exists">
        <then>Script prints the existing session ID and suggests /reqdev:resume.</then>
    </branch>
    <branch condition="creating new">
        <then>Script creates .requirements-dev/ with state.json.</then>
    </branch>
</step>

<step sequence="2" name="ingest-concept-artifacts">
    <objective>Run concept ingestion and inspect the returned inventory.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json</script>
    <extract>
        - artifact_inventory: which concept-dev files exist
        - gate_status: whether all concept-dev gates were passed
        - source_refs: sources from concept-dev (carried forward)
        - assumption_refs: assumptions from concept-dev (carried forward)
        - research_gaps: open research gaps from concept-dev source registry
        - ungrounded_claims: claims flagged as lacking source documentation
        - citations: claim-to-source links from concept-dev
        - skeptic_findings: concept-dev skeptic agent verdicts (verified/unverified/disputed counts)
    </extract>
    <branch condition="gate_status.warnings has entries">
        <then>Display warnings to the user with a note that proceeding without all gates passed may result in incomplete ingestion.</then>
    </branch>
</step>

<step sequence="2.5" name="import-assumptions">
    <objective>Import concept-dev assumptions into the local assumption lifecycle tracker per INCOSE GtWR v4 §5.3.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --workspace .requirements-dev/ import-from-ingestion</script>
    <note>Creates local copies with origin: "concept-dev" and unique ASN-xxx IDs. These can be challenged, invalidated, or reaffirmed as requirements analysis progresses.</note>
    <presentation>
Assumptions imported: {imported_count} from concept-dev
Assumptions skipped:  {skipped_count} (already imported)
    </presentation>
</step>

<step sequence="3" name="branch-on-availability">
    <objective>Fork based on whether concept-dev artifacts exist.</objective>

    <branch condition="concept-dev artifacts found (CONCEPT-DOCUMENT.md and BLACKBOX.md exist in artifact_inventory)">

        <step sequence="3a" name="read-blackbox">
            <objective>Extract structured block data from BLACKBOX.md.</objective>
            <extract>
                - Block names and descriptions
                - Block-to-block relationships (uses, provides, depends)
                - Interface descriptions between blocks
            </extract>
        </step>

        <step sequence="3b" name="read-concept-document">
            <objective>Extract capabilities, scenarios, and needs candidates from CONCEPT-DOCUMENT.md.</objective>
            <extract>
                - Capabilities per block
                - ConOps scenarios (today-vs-concept workflow narratives) — mine these specifically for implicit operational requirements per GtWR v4 §5.2.4: performance expectations, usability constraints, reliability under operational conditions, error recovery workflows
                - Stakeholder needs candidates (statements beginning with "The user needs...", "The system shall...", or similar requirement-like patterns)
                - Maturation Path phases (Foundation/Integration/Advanced) per capability, if present
            </extract>
        </step>

        <step sequence="3c" name="read-solution-landscape">
            <condition>SOLUTION-LANDSCAPE.md exists</condition>
            <objective>Read for additional context (alternatives, trade-offs).</objective>
        </step>

        <step sequence="3d" name="format-extraction">
            <objective>Structure extracted data as JSON.</objective>
            <output-schema>
```json
{
  "blocks": [
    {
      "name": "block-name",
      "description": "One-line description",
      "relationships": [{"target": "other-block", "type": "uses|provides|depends"}],
      "interfaces": ["interface description"],
      "capabilities": ["capability 1", "capability 2"]
    }
  ],
  "needs_candidates": [
    {
      "source_block": "block-name",
      "statement": "The user needs...",
      "source_artifact": "CONCEPT-DOCUMENT.md",
      "source_section": "Section heading where found",
      "priority_hint": "high|medium|low",
      "provenance_score": "★★★|★★|★"
    }
  ]
}
```
            </output-schema>
            <priority-hints>
                <rule source="maturation-path">Foundation-phase capabilities → priority_hint: "high"</rule>
                <rule source="maturation-path">Integration-phase capabilities → priority_hint: "medium"</rule>
                <rule source="maturation-path">Advanced-phase capabilities → priority_hint: "low"</rule>
                <rule source="maturation-path">If no maturation path exists, omit priority_hint</rule>
            </priority-hints>
            <provenance-scoring>
                <level score="★★★">Derived from high-confidence sources with approved assumptions and verified skeptic findings</level>
                <level score="★★">Derived from medium-confidence sources or unreviewed assumptions</level>
                <level score="★">Derived from low-confidence/ungrounded sources, unresolved claims, or disputed skeptic findings</level>
                <note>Use ingestion.json → source_refs[].confidence, assumption_refs[].status, and skeptic_findings to compute provenance.</note>
            </provenance-scoring>
        </step>

        <step sequence="3e" name="register-sources">
            <objective>Register carried-forward concept-dev sources in the requirements-dev source registry.</objective>
            <loop over="each source in ingestion.json → source_refs">
                <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/source_tracker.py --workspace .requirements-dev add --title "SOURCE_TITLE" --url "" --type concept_dev --confidence "SOURCE_CONFIDENCE" --concept-dev-ref "SOURCE_ID"</script>
            </loop>
        </step>

        <step sequence="3f" name="update-ingestion">
            <objective>Add blocks and needs_candidates keys to the existing .requirements-dev/ingestion.json.</objective>
        </step>

        <step sequence="3g" name="present-summary">
            <presentation>
CONCEPT INGESTION SUMMARY
=========================
Blocks found:          {N}
Needs candidates:      {M}
Sources carried:       {S}
Assumptions carried:   {A}
Research gaps:         {RG}
Ungrounded claims:     {UC}
Skeptic findings:      {SF verified}/{SF unverified} verified/unverified
Gate warnings:         {W}

Blocks:
  - block-1: description...
  - block-2: description...

Needs candidates (first 5):
  1. "The user needs..." (from block-1, CONCEPT-DOCUMENT.md)
  2. ...
            </presentation>
            <gate type="user-confirm">Ask user to confirm before proceeding.</gate>
        </step>

    </branch>

    <branch condition="concept-dev artifacts NOT found">
        <objective>Manual mode — user defines blocks and capabilities directly.</objective>
        <presentation>
No concept-dev artifacts found. Entering manual mode.
You'll define the system's functional blocks and capabilities directly.
        </presentation>

        <step sequence="3-manual" name="manual-block-definition">
            <collect>
                <question>How many functional blocks does your system have?</question>
                <per-block>
                    - Name (short identifier, kebab-case)
                    - Description (1-2 sentences)
                    - 3-5 key capabilities
                </per-block>
                <question>What are the inter-block interfaces?</question>
            </collect>
            <gate type="user-confirm">Present complete summary table for approval. Only proceed after explicit user confirmation.</gate>
            <on-complete>Write manual entries to .requirements-dev/ingestion.json using the same JSON structure as the automated path (with source_artifact: "manual" in needs_candidates).</on-complete>
        </step>
    </branch>

</step>

<step sequence="4" name="detect-research-tools">
    <objective>Check which research tools are available for Phase 2 TPM research.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_tools.py --state .requirements-dev/state.json --json</script>
    <then>Display available tools summary to the user.</then>
</step>

<step sequence="5" name="update-state">
    <objective>Record initialization completion.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json set-phase init</script>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json pass-gate init</script>
    <loop over="each block discovered or defined">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json update blocks.BLOCK_NAME "DESCRIPTION"</script>
    </loop>
</step>

<step sequence="6" name="display-final-summary">
    <presentation>
REQUIREMENTS-DEV SESSION INITIALIZED
=====================================
Session ID:       {session_id}
Workspace:        .requirements-dev/
Ingestion source: {concept-dev | manual}

Blocks:           {N} defined
Needs candidates: {M} extracted
Sources:          {S} carried from concept-dev
Assumptions:      {A} carried from concept-dev
Research tools:   {T} detected

Next steps:
  /reqdev:needs    -- Formalize needs from candidates
  /reqdev:status   -- View current session status
    </presentation>
</step>

<notes>
    <note name="split-responsibility">JSON parsing in scripts, markdown extraction by LLM: The split is intentional. ingest_concept.py handles structured JSON data (deterministic, testable). Markdown reading and extraction is done by Claude directly (adaptive to format variations).</note>
    <note name="atomic-writes">All JSON file writes use temp-file-then-rename pattern via shared_io._atomic_write.</note>
    <note name="path-validation">All paths are validated to reject ".." traversal.</note>
</notes>
