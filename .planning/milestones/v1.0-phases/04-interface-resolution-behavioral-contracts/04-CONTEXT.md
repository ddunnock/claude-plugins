# Phase 4: Interface Resolution + Behavioral Contracts - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Define interfaces between approved components and establish behavioral contracts with V&V method assignments. Builds on Phase 3's approved components and reuses the generic approval gate for interface and contract proposals. Traceability weaving (Phase 5) and risk analysis (Phase 6) are out of scope.

</domain>

<decisions>
## Implementation Decisions

### Interface Discovery
- Both requirement cross-references AND AI semantic analysis of descriptions
- Requirement cross-references are the baseline (two components sharing requirement_ids or having relationships in proposals)
- Claude enriches with additional interfaces inferred from component descriptions
- One interface per component pair (not multiple per pair by concern)
- Through the approval gate with a new `interface-proposal` slot type -- consistent pattern from Phase 3
- Phase 3 proposal `relationships` (data flows/dependencies) seed interface candidates -- Claude enriches with data formats, protocols, direction

### Contract Structure
- Obligation lists (INCOSE-style): "SHALL process X within Y", "SHALL emit Z on failure"
- NOT pre/post conditions -- keep lightweight and readable
- Concrete JSON snippets for data formats: include example payloads or mini-schemas per interface
- Named error categories per interface (validation_error, not_found, timeout, etc.) with expected behavior per category
- Behavioral/functional obligations only -- no non-functional requirements (performance, availability). Those belong in Phase 6 risk analysis

### V&V Method Assignment
- Rule-based with AI override: declarative JSON config maps obligation types to default V&V methods, Claude can override with rationale
- Standard four INCOSE methods: Test, Analysis, Inspection, Demonstration
- V&V assignments bundled with behavioral contract proposals -- approving a contract approves its V&V methods
- vv-rules.json config using same declarative JSON pattern as approval-rules.json (XCUT-03 consistency)

### Change Reactivity
- Flag as stale + auto-repropose: same pattern as Phase 3's check_stale_components
- Timestamp-based detection: component updated_at newer than interface updated_at triggers stale flag
- One-level cascade: component change flags interfaces, interface change flags contracts
- Automatic re-proposal during normal command runs (no separate --refresh flag needed)

### Claude's Discretion
- Exact interface-proposal schema fields beyond the core ones
- How to handle components with no inferred interfaces (orphan detection)
- Obligation wording conventions and templates
- V&V rule default mappings (which obligation types map to which methods)

</decisions>

<specifics>
## Specific Ideas

- Reuse ApprovalGate from Phase 3 with new proposal slot types (interface-proposal, contract-proposal)
- Follow the established agent pattern: data preparation in Python, AI reasoning in command workflow, structured output via SlotAPI
- V&V rules should mirror the upstream VERIFICATION-MATRIX.md categories where possible
- Interface proposals should include direction (provider/consumer) and data flow description

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 04-interface-resolution-behavioral-contracts*
*Context gathered: 2026-03-01*
