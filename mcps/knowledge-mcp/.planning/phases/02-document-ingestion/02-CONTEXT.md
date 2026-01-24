# Phase 2: Document Ingestion - Context

**Gathered:** 2026-01-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Ingest engineering standards documents (PDF, DOCX) into the vector store with structure preservation. This phase delivers: hierarchical chunking with clause boundaries, table integrity, metadata extraction, and normative tagging. The system is designed as a general-purpose document ingestion MCP, with initial use case focused on systems engineering standards.

Search and retrieval (Phase 3) and MCP tool exposure are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Chunking Strategy
- **Hybrid approach**: Prefer clause boundaries but enforce max token limit
- **Target size**: ~500 tokens per chunk
- **Max limit**: Split clauses that exceed token limit
- **Overlap**: 20% (~100 tokens) between adjacent chunks
- **Split logic**: When clause exceeds limit, split at paragraph boundaries

### Table Handling
- **Use Docling fully**: Leverage Docling 2.69.0's native table and figure extraction
- **Format**: Structured JSON for programmatic access (chunks serve as search index pointing to source docs)
- **Large tables**: Split by rows, preserving column headers in each chunk
- **Context**: Include table title + caption with each table chunk
- **Figures**: Use Docling's image embedding capabilities

### Metadata Extraction
- **Clause IDs**: Full path format ("Section 4.2.3.1" — complete hierarchical path)
- **Normative tagging**: Required — tag every chunk as normative or informative
- **Location info**: Page number + full section path (e.g., page 45, Section 4.2.3)
- **Document metadata**: Embedded in every chunk (doc title, version, publication date)

### Document Scope
- **Formats**: Both PDF and DOCX from the start
- **Initial corpus**: INCOSE SE Handbook, IEEE 15288, ISO 15288, ISO 26262
- **Validation**: Ingest directly (no dry-run preview mode)
- **Design**: General-purpose MCP, not limited to these specific standards

### Claude's Discretion
- Exact Docling configuration and pipeline setup
- Normative detection heuristics (SHALL/SHOULD keywords, Annex markers)
- Error handling for malformed documents
- Chunk ID generation scheme

</decisions>

<specifics>
## Specific Ideas

- Chunks serve as a search index pointing to source documents, not the final content destination
- User plans to house source docs locally or within projects
- System should work with any well-structured technical document, not just the initial standards
- Docling is already a dependency (2.69.0) — leverage its structure extraction fully

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-document-ingestion*
*Context gathered: 2026-01-24*
