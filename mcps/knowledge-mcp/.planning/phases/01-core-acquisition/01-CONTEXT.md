# Phase 1: Core + Acquisition - Context

**Gathered:** 2026-01-27
**Status:** Ready for planning

<domain>
## Phase Boundary

PostgreSQL relational layer, web content ingestion via Crawl4AI, coverage assessment, and offline sync. Delivers 6 new MCP tools for content acquisition and assessment. Workflow-specific tools and feedback collection belong in later phases.

</domain>

<decisions>
## Implementation Decisions

### Web Ingestion Behavior
- **Robots.txt**: Strict respect — never crawl disallowed paths; preflight tool warns before attempting
- **Failed pages**: Retry 3x, then skip with warning; log failures, continue with other URLs, report at end
- **Rate limiting**: Moderate (1 request per 500ms), per-domain tracking
- **JavaScript rendering**: Always render JS by default (Crawl4AI handles SPAs, dynamic content)

### MCP Tool Interface Design
- **Response verbosity**: Balanced — include essential metadata, counts, brief descriptions
- **Batch support**: Yes, batch by default — tools accept lists, return aggregate results
- **Long-running operations**: Return immediately with job ID (async pattern); separate status check tool
- **Tool organization**: Separate focused tools (6 tools: knowledge_ingest, knowledge_sources, knowledge_assess, knowledge_preflight, knowledge_acquire, knowledge_request)

### Coverage Assessment UX
- **Gap presentation**: Prioritized list with confidence scores and suggested sources
- **Confidence threshold**: Medium (>0.5) — only show gaps with reasonable confidence
- **Source suggestions**: Yes, with specific URLs when possible (IEEE, NASA, INCOSE authoritative sources)
- **Coverage scope**: Both options available — per-project context OR global knowledge base, selectable via parameter

### Offline Sync Behavior
- **Architecture**: Qdrant is primary, ChromaDB is fallback (not a replica)
- **Sync scope**: Full vectors + metadata for complete offline search capability
- **Conflict resolution**: Qdrant wins (cloud is source of truth)
- **Sync frequency**: On-demand only — sync when explicitly requested
- **Failover**: Automatic failover with notification — switch to ChromaDB if Qdrant unreachable, inform user they're in offline mode

### Tenant ID Preparation (v3.0 Multi-tenancy)
- **Add tenant_id columns**: Yes, add UUID columns now to avoid migration pain in v3.0
- **Default value**: NULL (no tenant) for v2.0 single-tenant operation
- **Table scope**: Claude's discretion based on multi-tenancy isolation needs
- **Indexes**: Claude's discretion based on performance implications

### Claude's Discretion
- Which tables get tenant_id columns (based on v3.0 isolation requirements)
- Whether to create indexes on tenant_id in v2.0
- Internal implementation details for retry logic, rate limiting tracking
- Exact schema for job tracking (async operations)

</decisions>

<specifics>
## Specific Ideas

- Qdrant/ChromaDB relationship: Qdrant is primary cloud store, ChromaDB is local fallback — not a bidirectional sync. On-demand sync pulls from Qdrant to ChromaDB.
- Authoritative sources for gap suggestions: IEEE standards, NASA handbooks, INCOSE guides — include actual URLs when known
- Async job pattern: MCP tools return job ID immediately for long operations, allowing progress checks without blocking

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-core-acquisition*
*Context gathered: 2026-01-27*
