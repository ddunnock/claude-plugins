# Phase 4: Interface Resolution + Behavioral Contracts - Research

**Researched:** 2026-03-01
**Domain:** INCOSE-style interface contracts, behavioral obligations, V&V method assignment
**Confidence:** HIGH

## Summary

Phase 4 completes the "design triad" (components + interfaces + contracts) by building two new agent patterns on top of the proven Phase 3 infrastructure. The work follows established patterns exactly: Python agent scripts for data preparation, command workflow markdown for Claude reasoning, SlotAPI for persistence, and the generic ApprovalGate for developer review. Two new proposal slot types (`interface-proposal`, `contract-proposal`) and two new committed slot types (enhanced `interface`, enhanced `contract`) go through the same approval gate with the same `approval-rules.json` config.

The key technical challenge is the schema evolution: the existing `interface.json` and `contract.json` schemas from Phase 1 are minimal stubs. Phase 4 must extend them significantly (adding direction, data format schemas, error categories for interfaces; adding INCOSE-style obligations, V&V assignments for contracts) while preserving backward compatibility through `additionalProperties: false` -- meaning the schemas must be updated in place. Additionally, a new `vv-rules.json` declarative config mirrors the `approval-rules.json` pattern for V&V method defaults.

**Primary recommendation:** Split into 3 plans: (1) schema evolution + vv-rules config + registry registration of new proposal types, (2) interface resolution agent + interface command + stale detection, (3) behavioral contract agent + contract command + V&V assignment + change cascade.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Both requirement cross-references AND AI semantic analysis for interface discovery
- Requirement cross-references are the baseline; Claude enriches with additional interfaces
- One interface per component pair (not multiple per concern)
- Through the approval gate with a new `interface-proposal` slot type
- Phase 3 proposal `relationships` (data flows/dependencies) seed interface candidates
- Obligation lists (INCOSE-style): "SHALL process X within Y", "SHALL emit Z on failure"
- NOT pre/post conditions -- keep lightweight and readable
- Concrete JSON snippets for data formats: include example payloads or mini-schemas per interface
- Named error categories per interface (validation_error, not_found, timeout, etc.)
- Behavioral/functional obligations only -- no non-functional requirements
- Rule-based V&V with AI override: declarative JSON config maps obligation types to default V&V methods, Claude can override with rationale
- Standard four INCOSE methods: Test, Analysis, Inspection, Demonstration
- V&V assignments bundled with behavioral contract proposals
- vv-rules.json config using same declarative JSON pattern as approval-rules.json (XCUT-03)
- Flag as stale + auto-repropose pattern (same as Phase 3's check_stale_components)
- Timestamp-based detection: component updated_at > interface updated_at triggers stale
- One-level cascade: component change flags interfaces, interface change flags contracts
- Automatic re-proposal during normal command runs (no separate --refresh flag)

### Claude's Discretion
- Exact interface-proposal schema fields beyond the core ones
- How to handle components with no inferred interfaces (orphan detection)
- Obligation wording conventions and templates
- V&V rule default mappings (which obligation types map to which methods)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INTF-01 | Interface identification between connected components (REQ-034..037, REQ-267..272) | Interface resolution agent discovers boundaries from component relationships and requirement cross-refs; Claude enriches with semantic analysis |
| INTF-02 | Contract generation with data formats and protocols (REQ-267..272) | Interface-proposal schema includes protocol, data_format_schema, direction, error_categories; concrete JSON snippets |
| INTF-03 | Interface proposal sub-agent through approval gate (REQ-267..272, REQ-278..282) | Reuse ApprovalGate with `interface-proposal` slot type; same approval-rules.json config |
| INTF-04 | Change-reactive contract re-proposal on boundary changes (REQ-273..277) | Timestamp-based stale detection (component updated_at > interface updated_at); auto-repropose in command workflow |
| BHVR-01 | Behavioral obligation derivation per component (REQ-038..041, REQ-283..298) | Contract agent reads approved components + interfaces + requirements; derives INCOSE-style obligations |
| BHVR-02 | Obligation deriver sub-agent (REQ-283..288) | Python data prep function extracts component requirements, groups by type, identifies obligation candidates |
| BHVR-03 | Contract proposal with accept/reject/modify (REQ-283..298, REQ-294..298) | Reuse ApprovalGate with `contract-proposal` slot type; same pattern as interface-proposal |
| BHVR-04 | V&V method assignment (REQ-040, REQ-289..293, REQ-407) | vv-rules.json maps obligation types to default methods; Claude can override with rationale; bundled in contract-proposal |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib | 3.11+ | All implementation | Project standard from Phase 1 |
| json | stdlib | Schema loading, slot persistence | Project standard |
| jsonschema | existing | Schema validation on write | Already in project via schema_validator.py |
| uuid4 | stdlib | Slot ID generation | Project standard |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scripts/registry.py | existing | SlotAPI for all persistence | Every read/write/query operation (XCUT-04) |
| scripts/approval_gate.py | existing | Generic approval gate | All proposal review flows |
| scripts/schema_validator.py | existing | Schema validation | Automatically on every SlotAPI write |

### No New Dependencies
This phase adds zero new libraries. Everything builds on Phase 1-3 infrastructure.

## Architecture Patterns

### Recommended Project Structure

New/modified files for Phase 4:
```
schemas/
  interface-proposal.json    # NEW: proposal schema for interface discovery
  contract-proposal.json     # NEW: proposal schema for behavioral contracts
  interface.json             # MODIFIED: add direction, data_format_schema, error_categories
  contract.json              # MODIFIED: add structured obligations, vv_assignments
scripts/
  interface_agent.py         # NEW: interface resolution data prep + proposal creation
  contract_agent.py          # NEW: behavioral contract data prep + obligation derivation + V&V
  registry.py                # MODIFIED: register new slot types
commands/
  interface.md               # NEW: /system-dev:interface command workflow
  contract.md                # NEW: /system-dev:contract command workflow
agents/
  interface-resolution.md    # NEW: Claude instructions for interface analysis
  behavioral-contract.md     # NEW: Claude instructions for obligation derivation
data/
  vv-rules.json              # NEW: V&V method default mappings
tests/
  test_interface_agent.py    # NEW: interface agent unit tests
  test_contract_agent.py     # NEW: contract agent unit tests
  test_interface_integration.py  # NEW: interface discovery + approval integration
  test_contract_integration.py   # NEW: contract + V&V integration
```

### Pattern 1: Agent Pattern (Reuse from Phase 3)

**What:** Data preparation in Python, AI reasoning in command workflow markdown, structured output through SlotAPI.
**When to use:** Every agent in this phase follows this pattern exactly.
**Example:**

```python
# Source: scripts/decomposition_agent.py (established pattern)
class InterfaceAgent:
    def __init__(self, api: SlotAPI, schemas_dir: str):
        self._api = api
        self._schemas_dir = schemas_dir

    def prepare(self) -> dict:
        """Query approved components and their relationships, prepare data for Claude."""
        components = self._api.query("component", {"status": "approved"})
        # ... extract relationships, requirement cross-refs
        return {"components": components, "relationships": relationships, ...}

    def create_proposals(self, interfaces: list[dict], session_id: str) -> list[dict]:
        """Create interface-proposal slots from Claude's analysis output."""
        # Same pattern as DecompositionAgent.create_proposals
```

### Pattern 2: Approval Gate Reuse

**What:** Instantiate ApprovalGate with new proposal_type; it automatically derives committed slot type.
**When to use:** Both interface-proposal and contract-proposal flows.
**Example:**

```python
# Source: commands/approve.md (established pattern)
# For interfaces:
gate = ApprovalGate(api, rules_path, "interface-proposal")
# Derived committed type: "interface" (strips "-proposal" suffix)

# For contracts:
gate = ApprovalGate(api, rules_path, "contract-proposal")
# Derived committed type: "contract"
```

**Critical note:** The existing ApprovalGate._handle_accept() hardcodes field mapping (name, description, parent_requirements, rationale) specific to component-proposals. This MUST be generalized for Phase 4. The accept handler needs to either: (a) copy all non-system fields from proposal to committed slot, or (b) use a configurable field mapping per proposal type.

### Pattern 3: Stale Detection Cascade

**What:** Timestamp-based staleness check before command execution, one-level cascade.
**When to use:** At start of interface and contract commands.
**Example:**

```python
# Source: scripts/decomposition_agent.py check_stale_components (established pattern)
def check_stale_interfaces(api: SlotAPI) -> list[dict]:
    """Detect interfaces whose source components have changed."""
    interfaces = api.query("interface", {"status": "approved"})
    stale = []
    for intf in interfaces:
        src = api.read(intf["source_component"])
        tgt = api.read(intf["target_component"])
        if (src and src["updated_at"] > intf["updated_at"]) or \
           (tgt and tgt["updated_at"] > intf["updated_at"]):
            stale.append({"interface_slot_id": intf["slot_id"], ...})
    return stale

def check_stale_contracts(api: SlotAPI) -> list[dict]:
    """Detect contracts whose interfaces have changed."""
    # Same pattern, checking interface updated_at > contract updated_at
```

### Pattern 4: Declarative Config (XCUT-03)

**What:** JSON config files for externalizable rules, matching approval-rules.json pattern.
**When to use:** V&V method defaults.
**Example:**

```json
// data/vv-rules.json
{
  "schema_version": "1.0.0",
  "default_methods": {
    "data_processing": "test",
    "state_management": "test",
    "error_handling": "test",
    "interface_protocol": "demonstration",
    "configuration": "inspection",
    "logging": "inspection",
    "algorithmic": "analysis",
    "performance": "analysis"
  },
  "override_policy": "ai_with_rationale"
}
```

### Pattern 5: Interface Discovery from Component Relationships

**What:** Phase 3 component-proposals include `relationships` field with `{target_proposal, type, description}`. These seed interface candidates.
**When to use:** Step 1 of interface discovery.
**Example:**

```python
def discover_interface_candidates(api: SlotAPI) -> list[dict]:
    """Extract interface candidates from approved component relationships."""
    components = api.query("component", {"status": "approved"})
    candidates = []
    seen_pairs = set()

    for comp in components:
        # Check component-proposals for relationship data
        proposals = api.query("component-proposal", {"status": "accepted"})
        for prop in proposals:
            if prop.get("decision", {}).get("committed_slot_id") == comp["slot_id"]:
                for rel in prop.get("relationships", []):
                    # Find target component by name matching
                    pair = tuple(sorted([comp["slot_id"], target_id]))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        candidates.append({
                            "source_component": comp["slot_id"],
                            "target_component": target_id,
                            "relationship_type": rel["type"],
                            "description": rel["description"],
                        })
    return candidates
```

### Anti-Patterns to Avoid

- **Coupling ApprovalGate to specific fields:** The current _handle_accept hardcodes component-specific field mapping. Must generalize before adding new proposal types.
- **Multiple interfaces per component pair:** User decision locked one interface per pair. If two components share both data_flow and dependency, these are aspects of the same interface.
- **V&V as separate proposal:** User decision locked V&V bundled WITH contract proposals, not as separate approval items.
- **Non-functional obligations:** User explicitly deferred performance/availability to Phase 6 risk analysis. Only behavioral/functional obligations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Approval workflow | Custom state machine | Existing ApprovalGate with new proposal_type | Already tested, generic by design |
| Schema validation | Manual field checks | Existing SchemaValidator (auto on SlotAPI write) | Consistency, error messages |
| Slot persistence | Direct file I/O | SlotAPI (XCUT-04 mandate) | Atomic writes, journaling, versioning |
| Session tracking | Custom tracking | proposal_session_id field (Phase 3 pattern) | Batch tracking per run |
| Stale detection | Event-based system | Timestamp comparison (Phase 3 pattern) | Simple, proven, no infrastructure |

**Key insight:** Phase 4 reuses more infrastructure than it creates. The novelty is in the domain logic (interface discovery, obligation derivation, V&V mapping), not in the plumbing.

## Common Pitfalls

### Pitfall 1: ApprovalGate Accept Handler Field Mapping
**What goes wrong:** The existing `_handle_accept` in approval_gate.py hardcodes `name`, `description`, `parent_requirements`, `rationale` when creating the committed slot. Interface and contract proposals have different fields.
**Why it happens:** Phase 3 only needed one proposal type, so the accept handler was built for that specific case.
**How to avoid:** Generalize the accept handler to copy all non-system, non-decision fields from proposal to committed slot. Or add a configurable field mapping per proposal_type in approval-rules.json.
**Warning signs:** Tests pass for component proposals but fail for interface proposals on accept.

### Pitfall 2: Circular Stale Cascade
**What goes wrong:** Component change flags interface as stale, which triggers interface re-proposal, which updates interface timestamp, which flags contract as stale. If contract re-proposal then updates contract, which somehow cascades back...
**Why it happens:** Multi-level cascade without clear termination.
**How to avoid:** One-level cascade only (user decision). Component -> interface, interface -> contract. No cascading back from contract to interface. Stale detection runs at command start, not as automatic triggers.
**Warning signs:** Infinite re-proposal loops in integration tests.

### Pitfall 3: Interface Discovery Producing Duplicates
**What goes wrong:** Same component pair gets multiple interface proposals from different discovery methods (relationship seeding + requirement cross-ref + AI analysis).
**Why it happens:** Multiple discovery sources all independently find the same boundary.
**How to avoid:** Deduplicate by component pair BEFORE creating proposals. Use a set of `(source_component, target_component)` pairs (sorted for order independence).
**Warning signs:** Multiple interface-proposals referencing the same two components.

### Pitfall 4: Schema Migration for Existing Slots
**What goes wrong:** Existing interface and contract slots (created in Phase 1 testing) fail validation against the updated schemas.
**Why it happens:** Phase 4 adds new required fields to schemas that existing slots don't have.
**How to avoid:** New fields should be optional in the committed slot schema (interface.json, contract.json). Only the proposal schemas (interface-proposal.json, contract-proposal.json) should require the new fields. The accept handler populates the committed slot fields.
**Warning signs:** SchemaValidationError on reading existing interface/contract slots.

### Pitfall 5: V&V Method Assignment as Afterthought
**What goes wrong:** V&V methods are assigned superficially without connection to obligation content.
**Why it happens:** Treating V&V as a checkbox rather than a design-time decision.
**How to avoid:** vv-rules.json provides meaningful defaults per obligation type. Claude examines each obligation's content and overrides when the default doesn't fit. The override rationale is recorded.
**Warning signs:** Every obligation gets the same V&V method, or overrides have no rationale.

### Pitfall 6: Orphan Components with No Interfaces
**What goes wrong:** Components with no relationships to other components are silently ignored.
**Why it happens:** Interface discovery only processes components with detected boundaries.
**How to avoid:** Explicitly detect and report orphan components (components with no inferred interfaces). These may be genuinely independent or may indicate missing relationships.
**Warning signs:** Component count minus interface-connected components > 0 with no explanation.

## Code Examples

### Schema: interface-proposal.json (new)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://system-dev.local/schemas/interface-proposal.json",
  "title": "Interface Proposal Slot",
  "type": "object",
  "required": [
    "slot_id", "slot_type", "name", "description", "version",
    "created_at", "updated_at", "status",
    "source_component", "target_component", "direction",
    "proposal_session_id"
  ],
  "properties": {
    "slot_id": {"type": "string", "pattern": "^iprop-[a-f0-9-]+$"},
    "slot_type": {"const": "interface-proposal"},
    "name": {"type": "string", "minLength": 1, "maxLength": 200},
    "description": {"type": "string"},
    "version": {"type": "integer", "minimum": 1},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "status": {"type": "string", "enum": ["proposed", "accepted", "rejected", "modified"]},
    "source_component": {"type": "string"},
    "target_component": {"type": "string"},
    "direction": {"type": "string", "enum": ["unidirectional", "bidirectional"]},
    "protocol": {"type": "string"},
    "data_format_schema": {"type": "object"},
    "error_categories": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "expected_behavior": {"type": "string"}
        },
        "required": ["name", "description", "expected_behavior"],
        "additionalProperties": false
      }
    },
    "rationale": {
      "type": "object",
      "properties": {
        "narrative": {"type": "string"},
        "discovery_method": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "object"}}
      },
      "required": ["narrative"],
      "additionalProperties": false
    },
    "requirement_ids": {"type": "array", "items": {"type": "string"}},
    "gap_markers": {"type": "array", "items": {"type": "object"}, "default": []},
    "decision": {
      "type": "object",
      "properties": {
        "action": {"type": ["string", "null"]},
        "decided_by": {"type": ["string", "null"]},
        "decided_at": {"type": ["string", "null"], "format": "date-time"},
        "notes": {"type": ["string", "null"]},
        "rejection_rationale": {"type": ["string", "null"]},
        "modifications": {"type": ["object", "null"]},
        "committed_slot_id": {"type": ["string", "null"]}
      },
      "additionalProperties": false
    },
    "proposal_session_id": {"type": "string"},
    "extensions": {"type": "object"}
  },
  "additionalProperties": false
}
```

### Schema: contract-proposal.json (new)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://system-dev.local/schemas/contract-proposal.json",
  "title": "Contract Proposal Slot",
  "type": "object",
  "required": [
    "slot_id", "slot_type", "name", "description", "version",
    "created_at", "updated_at", "status",
    "component_id", "interface_id",
    "obligations", "vv_assignments",
    "proposal_session_id"
  ],
  "properties": {
    "slot_id": {"type": "string", "pattern": "^ctprop-[a-f0-9-]+$"},
    "slot_type": {"const": "contract-proposal"},
    "name": {"type": "string", "minLength": 1, "maxLength": 200},
    "description": {"type": "string"},
    "version": {"type": "integer", "minimum": 1},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "status": {"type": "string", "enum": ["proposed", "accepted", "rejected", "modified"]},
    "component_id": {"type": "string"},
    "interface_id": {"type": "string"},
    "obligations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "statement": {"type": "string"},
          "obligation_type": {"type": "string"},
          "source_requirement_ids": {"type": "array", "items": {"type": "string"}},
          "error_category": {"type": "string"}
        },
        "required": ["id", "statement", "obligation_type", "source_requirement_ids"],
        "additionalProperties": false
      }
    },
    "vv_assignments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "obligation_id": {"type": "string"},
          "method": {"type": "string", "enum": ["test", "analysis", "inspection", "demonstration"]},
          "rationale": {"type": "string"},
          "is_override": {"type": "boolean"}
        },
        "required": ["obligation_id", "method", "rationale"],
        "additionalProperties": false
      }
    },
    "rationale": {
      "type": "object",
      "properties": {
        "narrative": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "object"}}
      },
      "required": ["narrative"],
      "additionalProperties": false
    },
    "requirement_ids": {"type": "array", "items": {"type": "string"}},
    "gap_markers": {"type": "array", "items": {"type": "object"}, "default": []},
    "decision": {
      "type": "object",
      "properties": {
        "action": {"type": ["string", "null"]},
        "decided_by": {"type": ["string", "null"]},
        "decided_at": {"type": ["string", "null"], "format": "date-time"},
        "notes": {"type": ["string", "null"]},
        "rejection_rationale": {"type": ["string", "null"]},
        "modifications": {"type": ["object", "null"]},
        "committed_slot_id": {"type": ["string", "null"]}
      },
      "additionalProperties": false
    },
    "proposal_session_id": {"type": "string"},
    "extensions": {"type": "object"}
  },
  "additionalProperties": false
}
```

### Generalizing ApprovalGate Accept Handler

```python
# BEFORE (Phase 3 - hardcoded component fields):
def _handle_accept(self, proposal, ...):
    committed_content = {
        "name": proposal["name"],
        "description": proposal.get("description", ""),
        "status": "approved",
        "parent_requirements": proposal.get("requirement_ids", []),
        "rationale": proposal.get("rationale", {}).get("narrative", ""),
    }

# AFTER (Phase 4 - generic field copy):
def _handle_accept(self, proposal, ...):
    SYSTEM_FIELDS = {"slot_id", "slot_type", "version", "created_at", "updated_at"}
    PROPOSAL_FIELDS = {"decision", "proposal_session_id", "status"}
    committed_content = {"status": "approved"}
    for key, value in proposal.items():
        if key not in SYSTEM_FIELDS and key not in PROPOSAL_FIELDS:
            committed_content[key] = value
```

### V&V Default Assignment

```python
def assign_vv_methods(obligations: list[dict], vv_rules: dict) -> list[dict]:
    """Assign default V&V methods from rules, flagging for AI override."""
    defaults = vv_rules.get("default_methods", {})
    assignments = []
    for ob in obligations:
        ob_type = ob.get("obligation_type", "")
        default_method = defaults.get(ob_type, "test")  # test is safe fallback
        assignments.append({
            "obligation_id": ob["id"],
            "method": default_method,
            "rationale": f"Default for {ob_type} obligations per vv-rules.json",
            "is_override": False,
        })
    return assignments
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stub interface.json (Phase 1) | Rich interface schema with direction, data_format_schema, error_categories | Phase 4 | Existing stub fields preserved; new fields added as optional on committed schema |
| Stub contract.json (Phase 1) | Rich contract schema with structured obligations, vv_assignments | Phase 4 | Same approach -- extend without breaking |
| ApprovalGate hardcoded to component fields | Generic field-copy accept handler | Phase 4 | Required before adding new proposal types |
| Single proposal type (component-proposal) | Three proposal types in registry | Phase 4 | SLOT_TYPE_DIRS and SLOT_ID_PREFIXES extended |

## Open Questions

1. **ApprovalGate generalization strategy**
   - What we know: Current _handle_accept hardcodes component-proposal fields. Phase 4 needs it generic.
   - What's unclear: Should the field mapping be configurable per proposal_type in approval-rules.json, or should the handler simply copy all non-system fields?
   - Recommendation: Generic field-copy (exclude system + decision + session fields). Simpler, less config, works for all future proposal types.

2. **Requirement cross-reference discovery mechanism**
   - What we know: Two components sharing requirement_ids indicates an interface boundary.
   - What's unclear: How to handle requirements that are in many components (cross-cutting requirements) -- these would generate interfaces between nearly all component pairs.
   - Recommendation: Filter out requirements that appear in more than N components (e.g., 3+) from interface discovery -- they are cross-cutting concerns, not interface indicators.

3. **Interface naming convention**
   - What we know: Need descriptive names like "Auth-Service-to-Registry data flow"
   - What's unclear: Whether to auto-generate names or have Claude name them.
   - Recommendation: Claude names them in the agent analysis step, following a convention like "{source}-to-{target}: {purpose}".

## Sources

### Primary (HIGH confidence)
- Existing codebase: scripts/approval_gate.py, scripts/decomposition_agent.py, scripts/registry.py
- Existing schemas: schemas/component-proposal.json, schemas/interface.json, schemas/contract.json
- Existing commands: commands/decompose.md, commands/approve.md
- Phase 3 plans: 03-01-PLAN.md, 03-02-PLAN.md (established patterns)

### Secondary (MEDIUM confidence)
- Upstream requirements: requirements_registry.json REQ-034..041, REQ-267..298, REQ-407
- Upstream VERIFICATION-MATRIX.md (V&V method categories)

### Tertiary (LOW confidence)
- None -- all findings based on existing codebase and locked user decisions

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new dependencies, reuses Phase 1-3 infrastructure entirely
- Architecture: HIGH - follows established agent/command/approval patterns exactly
- Pitfalls: HIGH - derived from direct code inspection of approval_gate.py accept handler and schema constraints
- Schema design: MEDIUM - interface-proposal and contract-proposal schemas are recommendations within Claude's discretion area

**Research date:** 2026-03-01
**Valid until:** 2026-03-31 (stable -- all based on existing codebase patterns)
