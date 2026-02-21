# How to Use requirements-dev

A step-by-step guide to developing INCOSE-compliant requirements with this plugin.

## Prerequisites

| Requirement | Required | Notes |
|-------------|----------|-------|
| Claude Code | Yes | Plugin host |
| Python >= 3.11 | Yes | Script runtime |
| Concept-dev session | Recommended | BLACKBOX.md, source/assumption registries in `.concept-dev/` |
| `reqif` package | Optional | `pip install reqif` for ReqIF XML export |
| `crawl4ai` package | Optional | `pip install crawl4ai` for deep web crawling during research |

If concept-dev artifacts are not available, the plugin prompts you to define functional blocks and stakeholders manually.

## Workflow Overview

```
/reqdev:init  -->  /reqdev:needs  -->  /reqdev:requirements  -->  /reqdev:deliver
     |                                                                  |
     v                                                                  v
  Workspace created,                                          Specification documents
  concept-dev ingested                                        generated and baselined
                                                                        |
                          /reqdev:validate  <---  /reqdev:research  <----+
                                |
                                v
                          /reqdev:decompose  (optional, max 3 levels)
```

Use `/reqdev:status` at any time to see where you are. Use `/reqdev:resume` to continue after an interruption.

## Phase 1: Foundation

### Step 1: Initialize Session

```
/reqdev:init
```

Creates a `.requirements-dev/` workspace in your project root containing:

| File | Purpose |
|------|---------|
| `state.json` | Session state: phase, gates, counts, progress, traceability |
| `ingestion.json` | Concept-dev artifact inventory and parsed registries |

**What gets ingested from concept-dev:**
- Functional blocks from BLACKBOX.md
- Source registry entries for traceability
- Assumption registry entries flagged for formalization
- Gate status from the concept development session

**If no concept-dev artifacts exist:** The plugin prompts you to define blocks and stakeholders interactively.

The init command also detects available research tools (crawl4ai, MCP servers) and records them in `state.json` so the research agent can adapt its strategy.

### Step 2: Formalize Needs

```
/reqdev:needs
```

For each functional block, the plugin helps you formalize stakeholder needs using INCOSE patterns.

**Each need gets:**
- A unique `NEED-xxx` identifier
- A structured "stakeholder needs to..." statement
- Source traceability back to concept-dev
- Status tracking: approved, deferred (with rationale), or rejected (with rationale)

**Interaction pattern:** The plugin presents needs in batches of 2-3 for your review and approval. You can revise, defer, or reject any need before moving on.

**Registry:** `needs_registry.json`

**CLI (for debugging/scripting):**

| Action | Command |
|--------|---------|
| Add | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ add --statement "..." --stakeholder "..." --source-block "..."` |
| Update | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ update --id NEED-001 --statement "..."` |
| Defer | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ defer --id NEED-001 --rationale "..."` |
| Reject | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ reject --id NEED-001 --rationale "..."` |
| List | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ list [--block X] [--status Y]` |
| Query | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ query [--source-ref SRC-xxx]` |
| Export | `python3 scripts/needs_tracker.py --workspace .requirements-dev/ export` |

**Gate:** All needs approved (or explicitly deferred/rejected) before advancing to requirements.

### Step 3: Develop Requirements

```
/reqdev:requirements
```

This is the core workflow. For each functional block, the plugin walks through five type passes:

| Pass | Type | Focus | Default V&V Method |
|------|------|-------|-------------------|
| 1 | Functional | What the system shall do | System/unit test |
| 2 | Performance | How well it shall do it | Load/benchmark test |
| 3 | Interface | How it connects to other systems | Integration/contract test |
| 4 | Constraint | Limitations it must operate within | Inspection/analysis |
| 5 | Quality | Non-functional characteristics | Demonstration/analysis |

**For each requirement, the pipeline is:**

1. Claude drafts the requirement statement
2. **Tier 1 check** -- 16 deterministic rules run instantly (vague terms, escape clauses, passive voice, combinators, pronouns, absolutes, etc.)
3. **Tier 2 check** -- 9 semantic rules analyzed by the quality-checker agent (necessity, feasibility, verifiability, etc.)
4. You review and approve (or revise)
5. V&V method is planned based on requirement type
6. Requirement is registered with traceability to its parent need

**Requirement lifecycle:**

```
draft  -->  registered (linked to parent need)  -->  baselined  -->  [withdrawn]
```

**Registry:** `requirements_registry.json`

**CLI (for debugging/scripting):**

| Action | Command |
|--------|---------|
| Add (draft) | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ add --statement "..." --type functional --priority high --source-block blk` |
| Register | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ register --id REQ-001 --parent-need NEED-001` |
| Baseline | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ baseline --id REQ-001` |
| Baseline all | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ baseline --all` |
| Withdraw | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ withdraw --id REQ-001 --rationale "..."` |
| List | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ list [--include-withdrawn]` |
| Query | `python3 scripts/requirement_tracker.py --workspace .requirements-dev/ query [--type X] [--source-block Y] [--level N]` |

**Gate:** All requirements for all blocks registered and quality-checked before advancing to deliverables.

### Step 4: Generate Deliverables

```
/reqdev:deliver
```

The document-writer agent assembles deliverables from registries and templates:

| Deliverable | Source Data | Description |
|-------------|-------------|-------------|
| `REQUIREMENTS-SPECIFICATION.md` | requirements_registry.json | All requirements organized by block and type |
| `TRACEABILITY-MATRIX.md` | traceability_registry.json | Bidirectional links: sources -> needs -> requirements -> V&V |
| `VERIFICATION-MATRIX.md` | requirements_registry.json + traceability | V&V methods, success criteria, and status per requirement |
| `*.reqif` (optional) | All registries | Industry-standard ReqIF XML interchange format |

You approve each document section by section before baselining.

**ReqIF export** requires the `reqif` package (`pip install reqif`). If not installed, all other deliverables are generated normally and a message explains how to install it.

**Gate:** User approves assembled specification before advancing.

## Status and Resume

### Check Progress

```
/reqdev:status
```

Displays a dashboard with:
- Current phase and gate status
- Block progress (current block, current type pass)
- Requirement counts (total, registered, baselined, withdrawn)
- Traceability coverage percentage
- Open TBD/TBR items
- Suggested next action

### Resume After Interruption

```
/reqdev:resume
```

Reads `state.json` to determine exactly where you left off -- including the current block and type pass -- and resumes from that point. Five resumption patterns:

1. **Mid-block:** Resume at the current type pass within the current block
2. **Between blocks:** Start the next block
3. **Draft recovery:** Present any requirements left in draft status for completion
4. **Phase transition:** Check gates and advance to the next phase
5. **Fresh start:** Begin from init if no progress recorded

## Phase 2: Validation and Research

After generating deliverables, optionally strengthen your requirements.

### Validate the Set

```
/reqdev:validate
```

Runs six cross-block validation checks:

| Check | What It Finds |
|-------|---------------|
| Interface coverage | Block-to-block relationships missing interface requirements |
| Duplicate detection | Near-duplicate statements across blocks (n-gram cosine similarity, threshold 0.8) |
| Terminology consistency | Inconsistent synonyms across blocks (e.g., "user" vs "client") |
| Uncovered needs | Approved needs with no derived requirements |
| TBD/TBR report | Open to-be-determined and to-be-resolved items |
| INCOSE C10-C15 | Completeness, consistency, feasibility, comprehensibility, validatability, correctness |

The skeptic agent (Opus) verifies coverage and feasibility claims.

**CLI:**

| Action | Command |
|--------|---------|
| Full validation | `python3 scripts/set_validator.py --workspace .requirements-dev/ validate` |
| Interface check | `python3 scripts/set_validator.py --workspace .requirements-dev/ check-interfaces` |
| Duplicate check | `python3 scripts/set_validator.py --workspace .requirements-dev/ check-duplicates` |
| Terminology check | `python3 scripts/set_validator.py --workspace .requirements-dev/ check-terminology` |
| Coverage check | `python3 scripts/set_validator.py --workspace .requirements-dev/ check-coverage` |
| TBD/TBR check | `python3 scripts/set_validator.py --workspace .requirements-dev/ check-tbd` |

### Research Benchmarks

```
/reqdev:research
```

The TPM researcher agent finds industry benchmarks for measurable requirements. For example, if you have a performance requirement about response time, the researcher finds relevant benchmarks from published studies and standards.

Results are presented as structured benchmark tables with source citations.

**Gate:** User reviews and resolves all validation findings.

## Phase 3: Decomposition

```
/reqdev:decompose
```

For complex systems, decompose system-level requirements into subsystem allocations.

**Workflow:**
1. Select a block to decompose
2. Validate that all block requirements are baselined
3. Define sub-blocks with names and descriptions
4. Allocate each parent requirement to one or more sub-blocks with rationale
5. Validate allocation coverage (every baselined requirement must be allocated)
6. Repeat for deeper levels (max 3)

Each decomposition level re-enters the quality checking pipeline.

**CLI:**

| Action | Command |
|--------|---------|
| Validate baseline | `python3 scripts/decompose.py --workspace .requirements-dev/ validate-baseline --block blk` |
| Register sub-blocks | `python3 scripts/decompose.py --workspace .requirements-dev/ register-sub-blocks --parent blk --sub-blocks '[...]' --level 1` |
| Allocate | `python3 scripts/decompose.py --workspace .requirements-dev/ allocate --requirement REQ-001 --sub-block sub-blk --rationale "..."` |
| Check coverage | `python3 scripts/decompose.py --workspace .requirements-dev/ validate-coverage --block blk` |
| Check level limit | `python3 scripts/decompose.py --workspace .requirements-dev/ check-level --level 2` |

**Gate:** User approves decomposition at each level.

## State Management

### State File

All session state is stored in `.requirements-dev/state.json`:

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | UUID hex identifying the session |
| `schema_version` | string | State schema version (currently "1.0.0") |
| `current_phase` | string | Active phase: init, needs, requirements, validate, deliver, decompose |
| `gates` | object | Phase gate pass/fail status |
| `blocks` | object | Functional blocks with relationships and hierarchy |
| `progress` | object | Current block, type pass, and draft requirements |
| `counts` | object | Running tallies of needs and requirements by status |
| `traceability` | object | Link count and coverage percentage |
| `decomposition` | object | Decomposition levels and max depth |
| `artifacts` | object | Paths to generated deliverable files |

### CLI State Management

| Action | Command |
|--------|---------|
| Set phase | `python3 scripts/update_state.py --state .requirements-dev/ set-phase requirements` |
| Pass gate | `python3 scripts/update_state.py --state .requirements-dev/ pass-gate needs` |
| Check gate | `python3 scripts/update_state.py --state .requirements-dev/ check-gate needs` |
| Update field | `python3 scripts/update_state.py --state .requirements-dev/ update counts.needs_total 5` |
| Sync counts | `python3 scripts/update_state.py --state .requirements-dev/ sync-counts` |
| Show status | `python3 scripts/update_state.py --state .requirements-dev/ show` |

## Traceability

The plugin maintains bidirectional traceability links in `traceability_registry.json`:

| Link Type | Meaning | Example |
|-----------|---------|---------|
| `derives_from` | Requirement derives from need | REQ-001 -> NEED-001 |
| `verified_by` | Requirement verified by method | REQ-001 -> V&V entry |
| `sources` | Need sourced from artifact | NEED-001 -> SRC-001 |
| `informed_by` | Requirement informed by source | REQ-001 -> SRC-002 |
| `allocated_to` | Requirement allocated to sub-block | REQ-001 -> sub-block |
| `parent_of` | Block hierarchy | parent-block -> child-block |
| `conflicts_with` | Conflict requiring resolution | REQ-001 -> REQ-002 |

**CLI:**

| Action | Command |
|--------|---------|
| Create link | `python3 scripts/traceability.py --workspace .requirements-dev/ link --source REQ-001 --target NEED-001 --type derives_from --role requirement` |
| Query links | `python3 scripts/traceability.py --workspace .requirements-dev/ query --entity REQ-001 --direction both` |
| Coverage report | `python3 scripts/traceability.py --workspace .requirements-dev/ coverage` |
| Orphan check | `python3 scripts/traceability.py --workspace .requirements-dev/ orphans` |

## Quality Rules

### Running Quality Checks Manually

```bash
# Check a single statement
python3 scripts/quality_rules.py check "The system shall quickly process data"

# Check all requirements in a registry
python3 scripts/quality_rules.py check-all --registry .requirements-dev/requirements_registry.json

# List all available rules
python3 scripts/quality_rules.py rules
```

### Understanding Violations

Each violation includes:
- **rule_id:** Which rule triggered (e.g., R7)
- **severity:** `error` (must fix) or `warning` (review recommended)
- **matched_text:** The exact text that triggered the rule
- **position:** Character position in the statement
- **suggestion:** How to fix it

## Tips for Writing Good Requirements

1. **Use "shall" for requirements, "will" for statements of fact, "should" for goals**
2. **One requirement per statement** -- avoid "and" connecting separate capabilities
3. **Be specific and measurable** -- "within 200ms" not "quickly"
4. **Avoid vague terms** -- the quality checker flags these automatically
5. **Trace everything** -- every requirement needs a parent need
6. **Think about verification** -- if you can't test it, rewrite it
7. **Use active voice** -- "The system shall..." not "It shall be..."
8. **No escape clauses** -- "where possible" or "if practical" weaken requirements

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Workspace already initialized" | Use `/reqdev:resume` to continue the existing session |
| ReqIF export skipped | Install: `pip install reqif` |
| Research finds no benchmarks | Check `/reqdev:status` for available research tools; install crawl4ai or configure MCP servers |
| Gate won't pass | Check that all items in the current phase are approved/resolved |
| Path traversal error | Paths must not contain `..` components; use absolute or clean relative paths |
| "Schema version mismatch" warning | The workspace was created with a different plugin version; features may be limited |
