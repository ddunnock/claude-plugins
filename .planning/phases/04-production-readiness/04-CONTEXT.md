# Phase 4: Production Readiness - Context

**Gathered:** 2026-01-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Quality gates and monitoring ensure sustained performance. Build evaluation framework with golden test set, track RAG Triad metrics, implement cost monitoring and embedding caching, and package for marketplace distribution.

</domain>

<decisions>
## Implementation Decisions

### Golden Test Set Design
- Query sources: Both real user scenarios (from specification-refiner usage) and systematic standards coverage (INCOSE, IEEE, ISO)
- Expected results: Top-k relevance — expected clause must appear in results
- Pass/fail threshold: Top 5 (balanced RAG benchmark)
- CI integration: Run on every PR (~30-60s overhead acceptable)

### RAG Metrics & Reporting
- All three RAG Triad metrics tracked equally: context relevance, faithfulness, answer relevance
- Reporting: Both structured JSON logs for detailed analysis + CLI summary command for quick evaluation
- Alerting: Threshold-based — alert if recall drops below 80%

### Cost Monitoring & Caching
- Token tracking: Aggregated daily totals (not per-query)
- Budget control: Soft limit with warning — warn when approaching threshold, don't block operations
- Cache key: Content hash only (same text = same embedding)
- Cache invalidation: On embedding model change only (otherwise immutable)

### Marketplace Packaging
- Distribution: Both Claude Desktop plugin + standalone MCP server with installation docs
- Configuration: Environment variables (QDRANT_URL, OPENAI_API_KEY, etc.) — standard 12-factor approach
- Documentation: Concise README + example queries and configs
- Initial content: Empty — users ingest their own documents

### Claude's Discretion
- Exact log format and field names
- CLI report layout and formatting
- Alert delivery mechanism (stdout warning, log level, etc.)
- Cache storage implementation (file-based, in-memory, etc.)

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-production-readiness*
*Context gathered: 2026-01-24*
