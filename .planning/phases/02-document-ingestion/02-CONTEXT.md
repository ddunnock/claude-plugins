# Phase 2: Document Ingestion - Context

**Gathered:** 2026-01-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Structure-aware document chunking with clause preservation for engineering standards. Takes raw PDF/DOCX standards documents and prepares them for semantic search by chunking intelligently — preserving tables, clause hierarchy, and normative/informative tagging.

Docling 2.69.0 is already in the stack with AI-assisted chunking capabilities. This phase configures and integrates it properly.

</domain>

<decisions>
## Implementation Decisions

### Chunk Boundaries
- Split at **leaf clause level** (e.g., 6.4.3.2), keeping chunks smaller with parent context in metadata
- Chunk size: **256-512 tokens** with 15% overlap (matches ROADMAP spec)
- Tables: **row-level splitting if needed** — preserve column headers per chunk when table exceeds max size
- Figures: **Leverage Docling's figure capabilities** — research what 2.69.0 supports (may include embedding or text descriptions)

### Metadata Extraction
- **Normative/informative tagging is essential** — every chunk must be tagged for search filtering
- **Full hierarchy path** in metadata: standard → part → section → clause → sub-clause
- Document-level metadata to capture:
  - Standard ID & version (ISO 26262:2018, IEEE 15288-2015)
  - Effective/revision date
  - Scope/applicability domain
  - Source file path for traceability
- **Page numbers required** — every chunk must have page number(s) for precise citations

### Document Parsing
- Multi-column layouts: **linearize intelligently** — trust Docling's AI column detection
- Headers/footers: **strip completely** — they add noise to chunks
- Cross-references: **preserve as text** — keep "see 6.4.2" and "per ISO 12207" in chunk text for context
- Parse failures: **fail loudly** — stop ingestion on error, no partial/bad data in vector store

### Corpus Strategy
- Initial corpus: **all four standards** (INCOSE, IEEE 15288, ISO 15288, ISO 26262)
- Source documents: available locally, user has them
- Document path: **configurable via environment variable** (e.g., KNOWLEDGE_DOCS_PATH)
- Version updates: **replace in place** — delete old chunks, ingest new version, only latest available

### Claude's Discretion
- Exact figure handling approach (after researching Docling 2.69.0 capabilities)
- Column header preservation strategy for split tables
- Normative/informative detection heuristics (e.g., "NOTE:", "SHALL", "should")
- Chunk overlap implementation details

</decisions>

<specifics>
## Specific Ideas

- User knows Docling has AI-assisted chunking and figure capabilities — leverage these rather than building custom
- Standards may have complex nested tables (like ISO 26262 ASIL matrices) — row-level splitting with headers is the chosen approach
- Citation format should support precise references: "ISO 26262:2018, Part 6, Clause 8.4.3.2, p.47"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-document-ingestion*
*Context gathered: 2026-01-23*
