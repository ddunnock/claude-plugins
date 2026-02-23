---
name: reqdev:init
description: Initialize requirements-dev session and ingest concept-dev artifacts
---

# /reqdev:init -- Initialize Requirements Development Session

This command initializes the requirements development workspace and ingests concept-dev artifacts.

## Step 1: Initialize Workspace

Run the session initialization script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_session.py <project_path>
```

Where `<project_path>` is the project root (typically the current working directory).

- If workspace already exists, the script prints the existing session ID and suggests `/reqdev:resume`
- If creating new, the script creates `.requirements-dev/` with `state.json`

## Step 2: Ingest Concept-Dev Artifacts

Run the concept ingestion script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json
```

Check the returned JSON output:
- `artifact_inventory`: Which concept-dev files exist
- `gate_status`: Whether all concept-dev gates were passed
- `source_refs`: Sources from concept-dev (carried forward)
- `assumption_refs`: Assumptions from concept-dev (carried forward)

If `gate_status.warnings` has entries, display them to the user with a note that proceeding without all gates passed may result in incomplete ingestion.

Also note enriched ingestion fields in the output:
- `research_gaps`: Open research gaps from concept-dev source registry
- `ungrounded_claims`: Claims flagged as lacking source documentation
- `citations`: Claim-to-source links from concept-dev
- `skeptic_findings`: Concept-dev skeptic agent verdicts (verified/unverified/disputed counts)

## Step 2.5: Import Assumptions

Import concept-dev assumptions into the local assumption lifecycle tracker:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assumption_tracker.py --workspace .requirements-dev/ import-from-ingestion
```

This creates local copies of concept-dev assumptions with `origin: "concept-dev"` and unique ASN-xxx IDs. These can be challenged, invalidated, or reaffirmed as requirements analysis progresses — per INCOSE GtWR v4 §5.3 continuous assumption management.

Display the import result:
```
Assumptions imported: {imported_count} from concept-dev
Assumptions skipped:  {skipped_count} (already imported)
```

## Step 3: Branch on Concept-Dev Availability

### If concept-dev artifacts found

Check `artifact_inventory` for `CONCEPT-DOCUMENT.md` and `BLACKBOX.md`.

If both exist, read and extract structured data:

1. **Read `BLACKBOX.md`** and extract:
   - Block names and descriptions
   - Block-to-block relationships (uses, provides, depends)
   - Interface descriptions between blocks

2. **Read `CONCEPT-DOCUMENT.md`** and extract:
   - Capabilities per block
   - ConOps scenarios (today-vs-concept workflow narratives) — **mine these specifically for implicit operational requirements** per GtWR v4 §5.2.4: performance expectations, usability constraints, reliability under operational conditions, error recovery workflows
   - Stakeholder needs candidates (statements beginning with "The user needs...", "The system shall...", or similar requirement-like patterns)
   - Maturation Path phases (Foundation/Integration/Advanced) per capability, if present

3. **Read `SOLUTION-LANDSCAPE.md`** if present for additional context (alternatives, trade-offs)

Format extracted data as:

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

**Priority hints** from maturation path (OPP-5):
- Foundation-phase capabilities → `priority_hint: "high"`
- Integration-phase capabilities → `priority_hint: "medium"`
- Advanced-phase capabilities → `priority_hint: "low"`
- If no maturation path exists, omit priority_hint

**Provenance scoring** (OPP-3): Annotate each needs_candidate with a provenance quality indicator based on the strength of its backing evidence:
- ★★★ — derived from high-confidence sources with approved assumptions and verified skeptic findings
- ★★ — derived from medium-confidence sources or unreviewed assumptions
- ★ — derived from low-confidence/ungrounded sources, unresolved claims, or disputed skeptic findings

Use `ingestion.json → source_refs[].confidence`, `assumption_refs[].status`, and `skeptic_findings` to compute provenance
```

4. **Register carried-forward sources**: For each source in `ingestion.json → source_refs`, register it in the requirements-dev source registry with confidence preserved:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/source_tracker.py --workspace .requirements-dev add \
  --title "{source title/name}" --url "" --type concept_dev \
  --confidence "{source confidence level}" --concept-dev-ref "{source id}"
```

5. **Update `ingestion.json`**: Read the existing `.requirements-dev/ingestion.json` (written by `ingest_concept.py`), add the `blocks` and `needs_candidates` keys, and write it back.

6. **Present extraction summary** to user:

```
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
```

Ask user to confirm before proceeding.

### If concept-dev artifacts NOT found (manual mode)

Inform the user:

```
No concept-dev artifacts found. Entering manual mode.
You'll define the system's functional blocks and capabilities directly.
```

Guide through manual block definition:

1. Ask: "How many functional blocks does your system have?"
2. For each block, collect:
   - Name (short identifier, kebab-case)
   - Description (1-2 sentences)
   - 3-5 key capabilities
3. After all blocks, ask about inter-block interfaces
4. Present complete summary table for approval
5. Only proceed after explicit user confirmation

Write manual entries to `.requirements-dev/ingestion.json` using the same JSON structure as the automated path (with `source_artifact: "manual"` in needs_candidates).

## Step 4: Detect Research Tools

Run the tool availability checker:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_tools.py --state .requirements-dev/state.json --json
```

Display available tools summary to the user. Note which tools are available for Phase 2 TPM research.

## Step 5: Update State

Use `update_state.py` to record initialization completion:

```bash
# Set phase
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json set-phase init

# Pass the init gate
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json pass-gate init

# Record blocks (one per block discovered/defined)
# For each block, use the update command to add to blocks dict:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .requirements-dev/state.json update blocks.<block-name> "<description>"
```

## Step 6: Display Final Summary

```
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
```

## Important Notes

- **JSON parsing in scripts, markdown extraction by LLM**: The split is intentional. `ingest_concept.py` handles structured JSON data (deterministic, testable). Markdown reading and extraction is done by Claude directly (adaptive to format variations).
- **Atomic writes**: All JSON file writes use temp-file-then-rename pattern via `shared_io._atomic_write`.
- **Path validation**: All paths are validated to reject `..` traversal.
