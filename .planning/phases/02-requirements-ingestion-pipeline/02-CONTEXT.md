# Phase 2: Requirements Ingestion Pipeline - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Bridge requirements-dev outputs into the Design Registry. Ingest all upstream registries (needs, requirements, traceability, sources, assumptions), detect deltas on re-ingestion when upstream changes, and handle known schema gaps gracefully with structured gap markers. Does NOT include design work on ingested data — that starts in Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Ingestion Scope
- All-at-once ingestion: single init command reads all registries in dependency order
- Selective re-ingestion happens implicitly via delta detection (only changed items update)
- Explicit path argument: user provides path to `.requirements-dev/` directory
- Warn but ingest when upstream gates aren't all passed — show which phases are incomplete, still ingest available data, mark incomplete areas with gap markers (aligns with XCUT-01 partial-state tolerance)
- Preserve upstream confidence levels (high/medium/low/ungrounded) as metadata on source slots — addresses GAP-4 from CROSS-SKILL-ANALYSIS

### Delta Detection
- Content hash comparison: hash each upstream registry entry, store hashes in a manifest, compare on re-ingest to find adds/updates/deletes
- Conflicts (upstream change vs. local design edit): report conflict, don't overwrite — flag in delta report, preserve local edit, user resolves manually
- Delta report: both console summary (immediate visibility) and persistent `.system-dev/delta-report.json` (for downstream agents like impact analysis)
- Upstream deletions with downstream design artifacts flagged as 'breaking' severity; deletions with no downstream refs flagged as 'info'

### Schema Gap Handling
- Work around known upstream bugs (BUG-1, BUG-2, BUG-3) in our parser — handle both buggy and correct schemas, no upstream dependency
- Ingest what exists, gap-mark the rest — for known gaps (research gaps, citations, ungrounded claims not in upstream JSON), produce structured gap markers referencing CROSS-SKILL-ANALYSIS finding IDs
- Gap marker format: structured JSON object with `type`, `finding_ref`, `severity`, and `description` fields in slot metadata — machine-readable for downstream agents
- Compatibility report: after ingestion, write `.system-dev/compatibility-report.json` listing all gap markers by finding ID, affected slot counts, and severity

### Slot Mapping Strategy
- One slot per entity: each need → `need` slot, each requirement → `requirement` slot, each source → `source` slot, etc.
- Naming convention: `type:upstream-id` (e.g., `need:N-001`, `requirement:REQ-026`, `source:SRC-003`, `assumption:A-001`) — type prefix enables filtering, upstream ID preserved
- Traceability as slot cross-references: explicit link fields pointing to other slot IDs (e.g., `derives_from: ['need:N-003']`) — enables Phase 5 graph traversal natively
- Provenance metadata on every ingested slot: `{source: 'requirements-dev', upstream_file: '...', ingested_at: '...', hash: '...'}` — enables delta detection and audit trails

### Claude's Discretion
- Internal ingestion order (which registry to process first)
- Hash algorithm choice for delta detection
- Console output formatting and verbosity levels
- Error recovery strategy for malformed upstream JSON

</decisions>

<specifics>
## Specific Ideas

- CROSS-SKILL-ANALYSIS.md (in requirements-dev) is the authoritative reference for all known schema mismatches — findings BUG-1..3, SCHEMA-1..3, GAP-1..8 should be referenced by ID in gap markers
- The ingestion parser should be resilient to both current (buggy) and future (fixed) upstream schemas
- Delta report should be useful to Phase 5 impact analysis — structured enough to answer "what changed since last ingestion?"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-requirements-ingestion-pipeline*
*Context gathered: 2026-02-28*
