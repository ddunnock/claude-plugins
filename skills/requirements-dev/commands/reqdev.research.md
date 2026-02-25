---
name: reqdev:research
description: Research performance benchmarks and comparable system data for measurable requirements. Launches the tpm-researcher agent with tiered research tools.
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /reqdev:research - TPM Research

Researches performance benchmarks and comparable system data for measurable requirements. Launches the `tpm-researcher` agent with context about the requirement and available tools.

## Usage

```
/reqdev:research                              # Interactive -- prompts for requirement
/reqdev:research REQ-005                      # Research benchmarks for specific requirement
/reqdev:research "API response time target"   # Research by topic description
```

## Procedure

### Step 1: Identify the Research Target

If a requirement ID is provided (e.g., REQ-005), look it up in `.requirements-dev/requirements_registry.json`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/requirement_tracker.py --workspace .requirements-dev query --status registered
```

Parse the JSON output to find the requirement by ID.

Extract:
- The requirement statement
- Its type (performance, or any type with a quantitative target)
- Its parent need for context
- The source block for domain context

If no argument is provided, ask the user:
> What would you like to research? You can provide:
> - A requirement ID (e.g., REQ-005)
> - A performance area (e.g., "API response time")
> - A specific metric you need benchmarks for

### Step 1.5: Check for Existing Concept-Dev Research

Before launching new research, check if concept-dev already crawled relevant sources:

```bash
ls .concept-dev/research/ 2>/dev/null
```

If `.concept-dev/research/` exists and contains `WR-xxx.md` files or `research_index.json`, review these for existing benchmarks relevant to the research target. Concept-dev's research corpus may already contain the data needed, avoiding duplicate web crawling.

If relevant concept-dev research exists, note it in the research summary and cite it as a concept_dev source.

### Step 2: Check Research Tool Availability

Read `.requirements-dev/state.json` to check detected research tools:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_tools.py --state .requirements-dev/state.json --json
```

Report available tools briefly:
> Research tools available: WebSearch, WebFetch [, crawl4ai] [, Semantic Scholar] [, ...]

### Step 3: Launch TPM Research

Dispatch to the `tpm-researcher` agent with:
- The requirement statement (or research topic)
- The requirement type and block context
- Available research tools from state.json
- The source registry path: `.requirements-dev/source_registry.json`

The agent conducts tiered research and presents structured benchmark tables with consequence analysis.

### Step 4: Apply Research Results

After the tpm-researcher agent presents findings:

1. Ask the user which benchmark value they want to use (or a custom value informed by the research).

2. If a requirement ID was provided, offer to update the requirement:
   Read `.requirements-dev/requirements_registry.json`, update the requirement's statement field, and write back. The `update_requirement()` function in `requirement_tracker.py` handles this programmatically.

3. Create traceability links from the requirement to the research sources:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traceability.py --workspace .requirements-dev link --source REQ-005 --target SRC-xxx --type informed_by --role requirement
   ```

4. Re-run quality checks on the updated statement:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/quality_rules.py check "The system shall respond to queries within 200ms at the 95th percentile under normal load"
   ```

### Step 5: Report Summary

```
===================================================================
TPM RESEARCH COMPLETE
===================================================================

Requirement: REQ-005
Original: "The system shall respond to queries quickly"
Updated:  "The system shall respond to queries within 200ms
           at the 95th percentile under normal load"

Sources registered: SRC-014, SRC-015, SRC-016
Traceability links: REQ-005 -> SRC-014 (informed_by)
                     REQ-005 -> SRC-015 (informed_by)

Quality check: PASSED (no violations)
===================================================================
```
