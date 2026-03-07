# Phase 3: Structural Decomposition + Approval Gate - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

AI-driven component proposals from ingested requirements, with developer accept/reject/modify workflow that persists decisions atomically. This is the first agent phase — it establishes the agent-proposal-approval pattern that Phases 4-7 reuse. The approval gate's state-transition rules must be externalizable (APPR-04).

Scope: decomposition algorithm, proposal presentation, approval gate workflow, partial results with gap markers. Interface resolution, behavioral contracts, and traceability are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Decomposition strategy
- AI-adaptive granularity — the AI determines component count based on natural clustering in requirements, not a fixed target
- Flat component list (single level) — no sub-component hierarchy. Sub-decomposition can come in later phases if needed
- Rationale format: domain narrative as headline ("These requirements deal with user authentication flows") with requirement IDs as supporting evidence underneath (REQ-031, REQ-033, ...)
- Single proposal (not multiple alternatives) — Claude decides whether ambiguity warrants alternatives, but default is one well-reasoned grouping

### Proposal presentation
- Show coverage summary first: "47/52 requirements mapped, 5 unmapped (gap markers)" — big picture before details
- Show inferred inter-component relationships (dependencies/data flows) when they help validate the grouping — Claude decides when this adds value
- Narrative blocks format (headed sections per component with prose explanation) — more readable for complex rationale than tables
- Summary-first density: component name + 1-line purpose + requirement count, with expandable details

### Approval workflow
- Batch review — see all proposals, then decide on each. Claude may switch to 1x1 for very large sets
- Split/merge + edit for modifications — can split a component into two, merge two into one, plus rename and scope changes
- Auto re-propose after rejection — AI immediately generates a new proposal incorporating rejection rationale (conversational loop)
- Support notes on all decisions — accept/reject/modify can include optional annotations, captured in registry for downstream context

### Partial results behavior
- Warn first when gaps are significant — show what's missing, ask whether to proceed with partial decomposition. For minor gaps, proceed and mark
- Gap markers: both inline markers within relevant components + summary section at the end
- Allow approval with gaps — components with gap markers can be accepted, gaps tracked for later resolution
- Proactive flagging when gaps are filled — when new requirements are ingested, affected components are flagged for potential revision

</decisions>

<specifics>
## Specific Ideas

- The approval gate workflow must be reusable — Phases 4-7 all use the same accept/reject/modify pattern with the same state-transition machinery
- Externalizable state-transition rules (APPR-04) means the gate's behavior is declarative configuration, not hardcoded logic
- Gap markers should be first-class registry entries (not just text decorations) so they can be queried and tracked

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-structural-decomposition-approval-gate*
*Context gathered: 2026-03-01*
