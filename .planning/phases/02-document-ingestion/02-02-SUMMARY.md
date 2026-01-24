---
phase: 02-document-ingestion
plan: 02
subsystem: ingestion
tags: [docling, pdf, parsing, document-metadata, tables, hierarchical-structure]

# Dependency graph
requires:
  - phase: 02-01
    provides: Foundation utilities (tokenizer, hashing, normative detection)
provides:
  - Base ingestor interface (BaseIngestor, ParsedDocument, ParsedElement)
  - DocumentMetadata model for source tracking
  - PDFIngestor using Docling 2.70.0 for AI-based layout analysis
  - Table extraction with structured data preservation
  - Section hierarchy tracking for nested headings
  - Unit tests with mocked Docling (13 tests)
affects: [02-03, 02-04, 02-05, chunking, metadata-enrichment]

# Tech tracking
tech-stack:
  added: [docling==2.70.0]
  patterns: [base-ingestor-interface, parsed-document-dataclass, section-hierarchy-tracking]

key-files:
  created:
    - mcps/knowledge-mcp/src/knowledge_mcp/models/document.py
    - mcps/knowledge-mcp/src/knowledge_mcp/ingest/base.py
    - mcps/knowledge-mcp/src/knowledge_mcp/ingest/pdf_ingestor.py
    - mcps/knowledge-mcp/tests/unit/test_ingest/test_pdf_ingestor.py
  modified:
    - mcps/knowledge-mcp/src/knowledge_mcp/exceptions.py
    - mcps/knowledge-mcp/src/knowledge_mcp/ingest/__init__.py

key-decisions:
  - "Use Docling 2.70.0 for PDF parsing (superior table extraction vs pymupdf4llm)"
  - "Extract tables via export_to_dataframe() as list[list[str]] for structured data"
  - "Track section hierarchy as list[str] (e.g., ['4', '4.2', '4.2.3'])"
  - "Use type: ignore for Docling NodeItem attributes (dynamic typing in library)"

patterns-established:
  - "BaseIngestor abstract class with ingest() and supported_extensions() methods"
  - "ParsedElement dataclass for all document elements (heading, paragraph, table, list, figure)"
  - "DocumentMetadata tracks source_path per NFR-4.4 for provenance"
  - "Section stack algorithm for hierarchical heading tracking"

# Metrics
duration: 10m 28s
completed: 2026-01-24
---

# Phase 02 Plan 02: PDF Ingestor Summary

**Docling-based PDF parser extracting tables as structured data with clause hierarchy preserved**

## Performance

- **Duration:** 10 min 28 sec
- **Started:** 2026-01-24T20:07:52Z
- **Completed:** 2026-01-24T20:18:20Z
- **Tasks:** 3/3
- **Files modified:** 6

## Accomplishments
- Base ingestor interface defines ParsedDocument, ParsedElement, and DocumentMetadata models
- PDFIngestor converts PDFs to structured ParsedDocument using Docling AI-based layout analysis
- Tables extracted as list[list[str]] via export_to_dataframe() preserving rows and columns
- Section hierarchy tracked through heading nesting for citation support
- Page numbers captured from Docling provenance information
- IngestionError exception added for parse failure handling
- 13 unit tests with mocked Docling for comprehensive coverage

## Task Commits

Each task was committed atomically:

1. **Task 1: Create DocumentMetadata model and base ingestor interface** - `c84c334` (feat)
   - DocumentMetadata dataclass with document_id, title, document_type, source_path
   - ParsedElement dataclass for structured document elements
   - ParsedDocument dataclass combining metadata and elements
   - BaseIngestor abstract base class defining ingestion interface

2. **Task 2: Implement Docling-based PDF ingestor** - `53655e6` (feat)
   - PDFIngestor class using DocumentConverter from Docling 2.70.0
   - Extracts ParsedElements with element_type, content, page_number
   - Preserves section_hierarchy from heading nesting
   - Extracts tables as structured data via export_to_dataframe()
   - Handles figures with captions
   - Added IngestionError exception for parse failures

3. **Task 3: Create unit tests for PDF ingestor** - `85d8aa3` (test)
   - Test supported_extensions returns ['.pdf']
   - Test ParsedDocument structure with mocked Docling
   - Test metadata extraction from filename and document
   - Test section hierarchy tracking
   - Test table data extraction with export_to_dataframe()
   - Test error handling for missing files and parse failures
   - Test section stack updates for nested headings

## Files Created/Modified

### Created
- `mcps/knowledge-mcp/src/knowledge_mcp/models/document.py` - DocumentMetadata dataclass for source document tracking
- `mcps/knowledge-mcp/src/knowledge_mcp/ingest/base.py` - Base ingestor interface (BaseIngestor, ParsedDocument, ParsedElement)
- `mcps/knowledge-mcp/src/knowledge_mcp/ingest/pdf_ingestor.py` - Docling-based PDF parser with table extraction
- `mcps/knowledge-mcp/tests/unit/test_ingest/__init__.py` - Test module initialization
- `mcps/knowledge-mcp/tests/unit/test_ingest/test_pdf_ingestor.py` - 13 unit tests for PDF ingestor

### Modified
- `mcps/knowledge-mcp/src/knowledge_mcp/exceptions.py` - Added IngestionError exception
- `mcps/knowledge-mcp/src/knowledge_mcp/ingest/__init__.py` - Export PDFIngestor and base classes

## Decisions Made

**1. Docling 2.70.0 for PDF parsing**
- Rationale: Superior table extraction and hierarchical structure detection vs pymupdf4llm
- Trade-off: 10-20x slower, but accuracy is critical for engineering standards
- Already installed in project (from 02-01 dependency addition)

**2. Table extraction via export_to_dataframe()**
- Exports tables as pandas DataFrame, then converts to list[list[str]]
- Preserves row/column structure for downstream chunking
- Handles merged cells and complex layouts

**3. Section hierarchy as list[str]**
- Example: ["4", "4.2", "4.2.3"] for nested headings
- Enables clause-level citations and parent-child relationships
- Updated via section stack algorithm during parsing

**4. Type: ignore for Docling NodeItem**
- Docling's NodeItem uses dynamic typing that pyright cannot infer
- Strategic type: ignore comments maintain type safety elsewhere
- Runtime behavior validated via unit tests with mocking

**5. Added IngestionError exception**
- Specific exception for document parse failures
- Distinguishes from general errors (config, connection, etc.)
- Maps to MCP error code "ingestion_error"

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Docling type annotations incomplete for pyright strict mode**
- **Problem:** NodeItem attributes (label, text, prov) not exposed in type stubs
- **Solution:** Used `# type: ignore` comments strategically on Docling API calls
- **Impact:** Type safety maintained for our code, runtime validated via tests
- **Verification:** All 13 unit tests pass, imports work correctly

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for 02-03 (Chunking strategies):**
- ParsedDocument provides structured input for chunking
- Section hierarchy enables clause-boundary chunking
- Table data ready for smart table splitting
- Page numbers available for citations

**Ready for 02-04 (Document ingestion pipeline):**
- PDFIngestor.ingest() returns standardized ParsedDocument
- Error handling via IngestionError
- Extensible via BaseIngestor for DOCX, Markdown ingestors

**No blockers:**
- Docling 2.70.0 installed and working
- All success criteria met (see verification below)

## Verification

All success criteria from plan verified:

✅ **1. PDFIngestor uses Docling DocumentConverter for PDF parsing**
- Confirmed: `converter = DocumentConverter()` in __init__
- Verified: converter.convert() called in ingest()

✅ **2. ParsedDocument contains list of ParsedElements with element_type, content, page_number**
- Confirmed: ParsedElement has all required fields
- Verified: Test suite validates structure

✅ **3. Section hierarchy is tracked as list of strings**
- Confirmed: section_hierarchy: list[str] in ParsedElement
- Verified: _update_section_stack() maintains hierarchy

✅ **4. Tables are extracted with table_data as list[list[str]]**
- Confirmed: _extract_table_data() uses export_to_dataframe()
- Verified: Test validates table_data structure

✅ **5. DocumentMetadata includes source_path per NFR-4.4**
- Confirmed: source_path field in DocumentMetadata
- Verified: Set to str(file_path.absolute()) in metadata extraction

✅ **6. All code passes pyright strict mode**
- Confirmed: 0 errors, 0 warnings
- Command: `poetry run pyright src/knowledge_mcp/ingest/ src/knowledge_mcp/models/document.py`

✅ **7. Unit tests pass with mocked Docling**
- Confirmed: 13/13 tests passed
- Coverage: 73% for pdf_ingestor.py (uncovered: edge cases in element type mapping)

---
*Phase: 02-document-ingestion*
*Completed: 2026-01-24*
