# Phase 3: Structural Decomposition + Approval Gate - Research

**Researched:** 2026-03-01
**Domain:** AI-driven component decomposition, state-machine-based approval workflow, Claude Code skill agent pattern
**Confidence:** HIGH

## Summary

Phase 3 introduces the first agent pattern in the system-dev skill: an AI (Claude) proposes component groupings from ingested requirements, and the developer reviews/accepts/rejects/modifies each proposal through a reusable approval gate. This phase establishes the agent-proposal-approval pattern that Phases 4-7 reuse.

The technical domain has two distinct halves. The **decomposition side** reads requirement slots from the Design Registry, clusters them by functional coherence and data affinity, and produces component-proposal slots with rationale. This is a prompt-engineering + data-preparation problem -- the "algorithm" is Claude's reasoning over structured requirement data, not a custom clustering implementation. The **approval gate side** is a state machine with declarative transitions (proposed -> accepted/rejected/modified), atomic persistence via SlotAPI, and a conversational re-proposal loop on rejection. The gate must be externalizable (APPR-04) so Phases 4-7 can reuse it with different proposal types.

**Primary recommendation:** Build the approval gate as a generic, configuration-driven module first (it is the reusable foundation), then build the decomposition agent on top of it. The component-proposal schema needs to be a new slot type distinct from the existing "component" type -- proposals become components only after acceptance.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- AI-adaptive granularity -- the AI determines component count based on natural clustering in requirements, not a fixed target
- Flat component list (single level) -- no sub-component hierarchy
- Rationale format: domain narrative as headline with requirement IDs as supporting evidence underneath
- Single proposal (not multiple alternatives) -- default is one well-reasoned grouping
- Show coverage summary first: "47/52 requirements mapped, 5 unmapped (gap markers)"
- Show inferred inter-component relationships when they help validate the grouping
- Narrative blocks format (headed sections per component with prose explanation)
- Summary-first density: component name + 1-line purpose + requirement count, with expandable details
- Batch review -- see all proposals, then decide on each
- Split/merge + edit for modifications -- can split a component into two, merge two into one, plus rename and scope changes
- Auto re-propose after rejection -- AI immediately generates a new proposal incorporating rejection rationale
- Support notes on all decisions -- accept/reject/modify can include optional annotations
- Warn first when gaps are significant -- show what's missing, ask whether to proceed with partial decomposition
- Gap markers: both inline within relevant components + summary section at the end
- Allow approval with gaps -- components with gap markers can be accepted, gaps tracked for later resolution
- Proactive flagging when gaps are filled -- when new requirements are ingested, affected components are flagged

### Claude's Discretion
None explicitly stated -- all major decisions were locked.

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| STRC-01 | Component proposal from requirements with functional coherence/data affinity rationale -- REQ-031..033, REQ-251..258 | Decomposition agent reads requirement slots, produces component-proposal slots with structured rationale referencing REQ IDs |
| STRC-02 | Component proposer sub-agent with grouping algorithms -- REQ-251..258 | Prompt template + requirement data preparation; AI does the clustering, code handles data marshalling and output formatting |
| STRC-03 | Partial decomposition with gap markers when requirements are incomplete -- REQ-090..092 | Reuse gap_markers schema pattern from Phase 2; detect missing/incomplete requirement slots before decomposition |
| APPR-01 | Accept/reject/modify workflow for component proposals -- REQ-259..266 | Approval gate state machine with declarative transitions; batch review presentation |
| APPR-02 | Atomic transactions (no partial state on accept/reject) -- REQ-470 | SlotAPI.create/update with optimistic locking; all-or-nothing write of accepted proposals |
| APPR-03 | Decision persistence before response -- REQ-450 | Write decision to registry (journal + slot update) before returning result to caller |
| APPR-04 | Externalizable workflow state-transition rules -- REQ-474 | JSON/YAML config file defining states, valid transitions, and actions; loaded at runtime |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python 3.14 | 3.14 | Runtime | Already established in Phases 1-2 |
| json (stdlib) | n/a | Config and slot serialization | Project convention: JSON files, no external deps |
| dataclasses (stdlib) | n/a | Data structures for proposals, decisions, reports | Consistent with DeltaReport, IngestResult patterns |
| logging (stdlib) | n/a | Structured logging per XCUT-02 | Consistent with Phase 2 logging pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scripts/registry.py (SlotAPI) | existing | All slot CRUD operations | Every read/write to Design Registry (XCUT-04) |
| scripts/shared_io.py | existing | Atomic writes, path validation | Any file persistence outside SlotAPI |
| scripts/schema_validator.py | existing | JSON Schema validation on proposal writes | Validate component-proposal and component slots |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JSON config for state transitions | YAML config | YAML needs PyYAML dependency; JSON is zero-dep and consistent with project |
| Custom prompt template | Jinja2 templates | Jinja2 adds dependency; string formatting or f-strings sufficient for structured prompts |
| State machine library (transitions, pytransitions) | Custom declarative engine | External deps violate project's zero-infrastructure principle; the state machine is simple enough (4 states, ~6 transitions) |

**Installation:**
```bash
# No new dependencies required -- stdlib + existing project modules only
```

## Architecture Patterns

### Recommended Project Structure
```
scripts/
    approval_gate.py        # Generic approval gate (reusable by Phases 4-7)
    decomposition_agent.py  # Structural decomposition agent
schemas/
    component-proposal.json # New slot type for proposals (pre-approval)
    approval-config.json    # JSON Schema for gate config validation (optional)
data/
    approval-rules.json     # Declarative state-transition config (APPR-04)
commands/
    decompose.md            # /system-dev:decompose command workflow
    approve.md              # /system-dev:approve command workflow
agents/
    structural-decomposition.md  # Agent definition for Claude
tests/
    test_approval_gate.py
    test_decomposition_agent.py
    test_decomposition_integration.py
```

### Pattern 1: Component-Proposal as Separate Slot Type
**What:** Proposals are a distinct slot type (`component-proposal`) separate from committed `component` slots. On acceptance, the gate creates a `component` slot from the proposal data.
**When to use:** Always -- this ensures proposals do not pollute the committed design state.
**Why:**
- REQ-259 says "present component-proposal slots" -- proposals are their own type
- REQ-260 says "write accepted component proposals to the design-registry as committed design artifacts" -- acceptance converts proposal to component
- The existing `component` schema has `status: ["proposed", "approved", "rejected", "modified", "deprecated"]` but mixing proposals with committed components creates query confusion
- Keeping them separate means querying `component` slots always returns committed design

**Schema design for component-proposal:**
```json
{
  "slot_id": "cprop-{uuid}",
  "slot_type": "component-proposal",
  "name": "Authentication Gateway",
  "description": "Handles all user authentication flows...",
  "version": 1,
  "status": "proposed",  // proposed | accepted | rejected | modified
  "requirement_ids": ["requirement:REQ-031", "requirement:REQ-032"],
  "rationale": {
    "narrative": "These requirements deal with user authentication flows...",
    "grouping_criteria": ["functional_coherence", "data_affinity"],
    "evidence": [
      {"req_id": "requirement:REQ-031", "relevance": "Core auth flow"},
      {"req_id": "requirement:REQ-032", "relevance": "Session management"}
    ]
  },
  "gap_markers": [],
  "relationships": [
    {"target_proposal": "cprop-{uuid2}", "type": "data_flow", "description": "Passes auth tokens"}
  ],
  "decision": {
    "action": null,        // accept | reject | modify | null
    "decided_by": null,
    "decided_at": null,
    "notes": null,
    "rejection_rationale": null,
    "modifications": null
  },
  "proposal_session_id": "session-{uuid}",
  "created_at": "...",
  "updated_at": "..."
}
```

### Pattern 2: Declarative Approval Gate State Machine
**What:** State transitions defined in a JSON config file, not hardcoded in Python logic.
**When to use:** For the approval gate (APPR-04 requirement).
**Why:** Phases 4-7 reuse the same accept/reject/modify pattern with different proposal types. The config defines:
- Valid states and transitions
- Required fields per transition
- Side effects (e.g., "on accept, create committed slot")

**Config structure (`data/approval-rules.json`):**
```json
{
  "schema_version": "1.0.0",
  "states": {
    "proposed": {
      "transitions": {
        "accept": {"target": "accepted", "requires": [], "side_effects": ["create_committed_slot"]},
        "reject": {"target": "rejected", "requires": ["rejection_rationale"], "side_effects": ["trigger_re_proposal"]},
        "modify": {"target": "modified", "requires": ["modifications"], "side_effects": ["apply_modifications"]}
      }
    },
    "accepted": {
      "terminal": true,
      "transitions": {}
    },
    "rejected": {
      "transitions": {
        "re_propose": {"target": "proposed", "requires": [], "side_effects": ["clear_decision"]}
      }
    },
    "modified": {
      "transitions": {
        "accept": {"target": "accepted", "requires": [], "side_effects": ["create_committed_slot"]},
        "reject": {"target": "rejected", "requires": ["rejection_rationale"], "side_effects": ["trigger_re_proposal"]}
      }
    }
  },
  "proposal_type_overrides": {}
}
```

### Pattern 3: Decomposition as Prompt + Data Preparation
**What:** The decomposition "algorithm" is Claude's reasoning over structured requirement data. The Python code prepares data, formats the prompt, and post-processes the response.
**When to use:** This is the only pattern for STRC-02 -- there is no traditional clustering algorithm.
**Why:** This is a Claude Code skill. The "agent" IS Claude. The code provides:
1. Data preparation: query all requirement slots, extract relevant fields, detect gaps
2. Prompt template: structured instructions for grouping with rationale format
3. Output parsing: validate the response against the component-proposal schema
4. Gap detection: identify missing/incomplete requirements before prompting

**The agent definition file (`agents/structural-decomposition.md`) contains:**
- Instructions for Claude on how to analyze requirements
- Expected output format (narrative blocks with requirement evidence)
- Coverage summary format
- Gap handling instructions

### Pattern 4: Atomic Batch Approval
**What:** When the developer accepts multiple proposals in batch, all writes succeed or none do.
**When to use:** Batch approval workflow (APPR-02).
**Implementation approach:**
- Collect all decisions first, validate all transitions
- Write all accepted proposals as component slots
- Update all proposal slot statuses
- Write a single batch journal entry
- If any write fails, the partial state is acceptable because each slot write is individually atomic (existing SlotAPI pattern), and proposals remain in their pre-decision state

**Important nuance:** True all-or-nothing batch atomicity across multiple files is complex without a database. The practical approach matching the existing project pattern:
- Each SlotAPI.create/update is individually atomic (temp+rename)
- Process decisions sequentially; if one fails, log the error and stop
- The proposal slots track their own status, so you can always see which were processed
- This matches REQ-470's intent: "preventing partial design state from persisting" -- each individual action is atomic

### Anti-Patterns to Avoid
- **Mixing proposals with committed components:** Never query `component` slots and get back unreviewed proposals. Separate types.
- **Hardcoding state transitions:** The gate must be declarative config, not if/elif chains (APPR-04).
- **Direct file access from the agent:** All reads/writes go through SlotAPI (XCUT-04). The decomposition agent must never read .system-dev/ files directly.
- **Skipping gap detection:** Always check for missing requirements before decomposition. Don't silently produce a decomposition that appears complete when requirements are missing.
- **Generating component IDs during proposal:** Proposal IDs (cprop-*) are separate from component IDs (comp-*). Component IDs are generated only on acceptance.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Slot persistence | Custom JSON file I/O | SlotAPI.create/update/query | Atomic writes, schema validation, journaling, versioning all built in |
| Schema validation | Custom field checking | SchemaValidator + JSON Schema files | Existing infrastructure, consistent patterns |
| Atomic file writes | Manual temp+rename | shared_io.atomic_write | Already battle-tested in Phases 1-2 |
| Content hashing | Custom hash logic | upstream_schemas.content_hash | Established pattern for delta detection |

**Key insight:** Phase 3 introduces new slot types and new behavioral logic, but ALL persistence, validation, and journaling infrastructure already exists from Phase 1. The new code is about decomposition logic, approval state management, and presentation formatting -- not storage.

## Common Pitfalls

### Pitfall 1: Proposal-Component Confusion
**What goes wrong:** Using the existing `component` slot type for proposals, leading to queries that return unreviewed proposals mixed with committed design.
**Why it happens:** The component schema already has a `status` field with "proposed" as a valid value, tempting developers to use it directly.
**How to avoid:** Create a dedicated `component-proposal` slot type. Only create `component` slots on acceptance.
**Warning signs:** `api.query("component")` returns items with `status: "proposed"`.

### Pitfall 2: Non-Atomic Decision Persistence
**What goes wrong:** Updating the proposal status and creating the committed component as two separate operations. If the second fails, you have a proposal marked "accepted" but no corresponding component.
**Why it happens:** Natural sequential coding -- update proposal first, create component second.
**How to avoid:** Create the component first (the critical new artifact), then update the proposal status. If the proposal status update fails, you have a duplicate that can be detected and cleaned up. If component creation fails, the proposal remains in its original state.
**Warning signs:** Proposals with `status: "accepted"` that have no corresponding component slot.

### Pitfall 3: Tightly Coupling Gate to Decomposition
**What goes wrong:** The approval gate code assumes component-proposal structure, making it unusable for Phases 4-7 (interface proposals, contract proposals).
**Why it happens:** Building the gate and the decomposition agent as a single module.
**How to avoid:** The approval gate takes a proposal slot type name and a config reference as parameters. It knows nothing about component-specific fields.
**Warning signs:** Import statements like `from scripts.decomposition_agent import` in approval_gate.py.

### Pitfall 4: Forgetting to Register New Slot Types
**What goes wrong:** Adding a component-proposal schema file but forgetting to register the new slot type in `registry.py`'s `SLOT_TYPE_DIRS` and `SLOT_ID_PREFIXES`.
**Why it happens:** The slot type registration is in registry.py, separate from the schema files.
**How to avoid:** Every new slot type requires updates to THREE places: (1) schemas/*.json, (2) SLOT_TYPE_DIRS in registry.py, (3) SLOT_ID_PREFIXES in registry.py.
**Warning signs:** `ValueError: Unknown slot type: 'component-proposal'` at runtime.

### Pitfall 5: Losing Requirement Traceability in Proposals
**What goes wrong:** The proposal records component names and descriptions but loses the specific requirement IDs that justified each grouping.
**Why it happens:** Summarizing too aggressively when constructing the proposal.
**How to avoid:** REQ-253 and REQ-466 explicitly require maintaining requirement identifiers in each proposal. The `requirement_ids` field is mandatory, not optional.
**Warning signs:** Proposals without requirement_ids or with only partial coverage.

### Pitfall 6: Gap Detection After Decomposition Instead of Before
**What goes wrong:** Running decomposition on whatever requirements exist, then checking for gaps afterward. The decomposition may produce misleading groupings based on incomplete data.
**Why it happens:** Gap detection feels like validation, which developers put at the end.
**How to avoid:** Check for missing/incomplete requirements BEFORE decomposition. Per CONTEXT.md: "Warn first when gaps are significant -- show what's missing, ask whether to proceed with partial decomposition."
**Warning signs:** Decomposition output with gap markers added post-hoc rather than gap detection driving a pre-decomposition warning.

## Code Examples

### Querying Requirement Slots for Decomposition Input
```python
# Source: existing scripts/registry.py SlotAPI pattern
from scripts.registry import SlotAPI

api = SlotAPI(workspace_root, schemas_dir)
requirements = api.query("requirement")

# Extract relevant fields for decomposition
req_data = []
for req in requirements:
    req_data.append({
        "slot_id": req["slot_id"],
        "upstream_id": req["upstream_id"],
        "description": req["description"],
        "requirement_type": req.get("requirement_type"),
        "source_block": req.get("source_block"),
        "parent_need": req.get("parent_need"),
        "gap_markers": req.get("gap_markers", []),
    })
```

### Approval Gate State Transition
```python
# Source: pattern derived from CONTEXT.md + REQ-474
import json

def load_approval_rules(rules_path: str) -> dict:
    """Load declarative state-transition rules."""
    with open(rules_path) as f:
        return json.load(f)

def validate_transition(
    rules: dict,
    current_state: str,
    action: str,
    decision_data: dict,
) -> tuple[bool, str]:
    """Check if a state transition is valid per the rules config.

    Returns (is_valid, error_message).
    """
    state_config = rules["states"].get(current_state)
    if state_config is None:
        return False, f"Unknown state: {current_state}"

    if state_config.get("terminal"):
        return False, f"State '{current_state}' is terminal, no transitions allowed"

    transition = state_config.get("transitions", {}).get(action)
    if transition is None:
        return False, f"Action '{action}' not valid from state '{current_state}'"

    # Check required fields
    for req_field in transition.get("requires", []):
        if not decision_data.get(req_field):
            return False, f"Action '{action}' requires '{req_field}'"

    return True, ""
```

### Creating Committed Component from Accepted Proposal
```python
# Source: pattern following existing SlotAPI.create
def accept_proposal(
    api: SlotAPI,
    proposal: dict,
    notes: str | None = None,
    agent_id: str = "approval-gate",
) -> dict:
    """Accept a proposal: create committed component, update proposal status.

    Creates the component FIRST (critical artifact), then updates
    proposal status. If proposal update fails, component exists
    and proposal can be reconciled.
    """
    # 1. Create the committed component slot
    component_content = {
        "name": proposal["name"],
        "description": proposal["description"],
        "source_block": proposal.get("source_block", ""),
        "status": "approved",
        "parent_requirements": proposal["requirement_ids"],
        "rationale": proposal["rationale"]["narrative"],
    }
    result = api.create("component", component_content, agent_id=agent_id)

    # 2. Update proposal status (REQ-450: persist decision before response)
    now = datetime.now(timezone.utc).isoformat()
    proposal["status"] = "accepted"
    proposal["decision"] = {
        "action": "accept",
        "decided_by": "developer",
        "decided_at": now,
        "notes": notes,
        "committed_slot_id": result["slot_id"],
    }
    api.update(
        proposal["slot_id"],
        proposal,
        expected_version=proposal["version"],
        agent_id=agent_id,
    )

    return {
        "proposal_id": proposal["slot_id"],
        "component_id": result["slot_id"],
        "status": "accepted",
    }
```

### Gap Detection Before Decomposition
```python
# Source: pattern derived from CONTEXT.md + STRC-03
def detect_requirement_gaps(requirements: list[dict]) -> dict:
    """Analyze requirements for completeness before decomposition.

    Returns gap report with severity assessment.
    """
    total = len(requirements)
    gaps = {
        "missing_descriptions": [],
        "missing_source_blocks": [],
        "incomplete_slots": [],  # slots with existing gap_markers
        "total_requirements": total,
    }

    for req in requirements:
        if not req.get("description"):
            gaps["missing_descriptions"].append(req["slot_id"])
        if not req.get("source_block"):
            gaps["missing_source_blocks"].append(req["slot_id"])
        if req.get("gap_markers"):
            gaps["incomplete_slots"].append(req["slot_id"])

    gap_count = (
        len(gaps["missing_descriptions"])
        + len(gaps["incomplete_slots"])
    )

    gaps["severity"] = (
        "high" if gap_count > total * 0.2
        else "medium" if gap_count > 0
        else "none"
    )
    gaps["gap_count"] = gap_count

    return gaps
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded workflows | Declarative state machines | Project requirement (APPR-04) | Gate config is JSON, not code |
| Component = proposal | Proposal -> Component conversion | Phase 3 design decision | Clean separation of proposed vs committed |
| Per-item journaling | Batch journal entries | Phase 2 (02-02 decision) | Continue batch pattern for approval batches |

**Key architectural evolution:**
- Phase 1 established: SlotAPI, atomic writes, schema validation, journaling
- Phase 2 established: batch processing, gap markers, delta detection, ingestion pattern
- Phase 3 establishes: agent-proposal-approval pattern, declarative config, state machine -- reused by Phases 4-7

## Open Questions

1. **Component-proposal schema: should `rationale` be a structured object or free-text string?**
   - What we know: CONTEXT.md says "domain narrative as headline with requirement IDs as supporting evidence underneath"
   - Recommendation: Use a structured object with `narrative` (string) and `evidence` (array of {req_id, relevance}) fields. This keeps the narrative readable while making evidence queryable.

2. **How should the decomposition agent handle 478 requirements in a single prompt?**
   - What we know: REQ-255 says "up to 200 requirement slots within 30 seconds". The upstream has 478 requirements but many are filtered (draft/withdrawn) and not all are relevant for component decomposition.
   - What's unclear: Whether all active requirements fit in a single Claude context window when serialized.
   - Recommendation: Pre-filter to active requirements with descriptions, group by source_block for context, and chunk if needed. Most real decompositions will be well under 200 active requirements after filtering.

3. **Should the approval gate persist its config path in the workspace config, or accept it as a parameter?**
   - What we know: APPR-04 says "externalizable" -- the rules should be a file that can be edited.
   - Recommendation: Default path in `data/approval-rules.json` within the skill plugin directory (read-only). If customization is needed later, support an override path in workspace config.

4. **How does "auto re-propose after rejection" work in a CLI skill context?**
   - What we know: CONTEXT.md says "AI immediately generates a new proposal incorporating rejection rationale (conversational loop)"
   - Recommendation: The approval command returns the rejection to Claude, which then re-runs the decomposition agent with the rejection rationale as additional context. This is a natural Claude Code conversation loop, not a programmatic retry. The command workflow description in `commands/approve.md` should document this loop.

## Sources

### Primary (HIGH confidence)
- Existing codebase: `scripts/registry.py`, `scripts/shared_io.py`, `scripts/ingest_upstream.py`, `scripts/delta_detector.py` -- established patterns for slot types, atomic writes, batch processing, gap markers
- Existing schemas: `schemas/component.json`, `schemas/requirement.json` -- field patterns, gap_markers structure, additionalProperties: false convention
- Formal requirements: `REQUIREMENTS-SPECIFICATION.md` sections 3.2 (approval-gate: REQ-259..266, REQ-450, REQ-470, REQ-474), 3.10 (component-proposer: REQ-251..258), 3.38 (structural-decomposition-agent: REQ-031..033, REQ-070, REQ-080, REQ-090, REQ-099, REQ-109, REQ-119, REQ-139, REQ-466)
- CONTEXT.md: User decisions locked for decomposition strategy, proposal presentation, approval workflow, partial results behavior

### Secondary (MEDIUM confidence)
- Skill authoring best practices (`_references/skill-authoring-best-practices.md`): Progressive disclosure, concise SKILL.md, command workflows

### Tertiary (LOW confidence)
- None -- all findings based on existing codebase and formal requirements

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - No new dependencies needed; existing codebase provides all infrastructure
- Architecture: HIGH - Clear separation of concerns (proposal type, gate, agent) supported by formal requirements and existing patterns
- Pitfalls: HIGH - Derived from analysis of existing codebase patterns and formal requirement constraints

**Research date:** 2026-03-01
**Valid until:** 2026-04-01 (stable -- internal project, no external dependency changes expected)
