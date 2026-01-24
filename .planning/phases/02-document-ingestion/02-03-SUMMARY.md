---
phase: 02-document-ingestion
plan: 03
subsystem: chunking
tags: [chunking, hierarchical, token-limits, overlap, table-splitting]
requires:
  - phase: 02-01
    provides: tokenizer utility for accurate token counting
provides:
  - base-chunker-interface
  - hierarchical-chunker-implementation
  - chunk-result-model
  - parsed-element-model
  - document-metadata-model
affects: [02-04, 02-05]
tech-stack:
  added: []
  patterns: [structure-aware-chunking, overlap-for-context, table-row-splitting]
key-files:
  created:
    - mcps/knowledge-mcp/src/knowledge_mcp/chunk/base.py
    - mcps/knowledge-mcp/src/knowledge_mcp/chunk/hierarchical.py
    - mcps/knowledge-mcp/tests/unit/test_chunk/test_hierarchical.py
  modified:
    - mcps/knowledge-mcp/src/knowledge_mcp/chunk/__init__.py
decisions:
  - id: chunk-config-defaults
    summary: 500 token target, 1000 max, 100 overlap (20%)
    rationale: Balances embedding API limits with context continuity
  - id: structure-aware-splitting
    summary: Split by paragraphs (double newline) to preserve structure
    rationale: Maintains semantic coherence within chunks
  - id: table-row-splitting
    summary: Split tables by rows with header preservation
    rationale: Never split mid-row, preserves table structure
  - id: overlap-strategy
    summary: Take last 20% of previous chunk as overlap
    rationale: Provides context continuity between adjacent chunks
  - id: small-chunk-merging
    summary: Merge chunks under 100 tokens with adjacent chunks
    rationale: Avoids inefficient micro-chunks
metrics:
  duration: 6m 59s
  completed: 2026-01-24
---

# Phase 02 Plan 03: Hierarchical Chunking Summary

**Structure-aware document chunker with 500 token target, table row splitting, and 20% overlap for context continuity**

## Performance

- **Duration:** 6m 59s
- **Started:** 2026-01-24T20:07:53Z
- **Completed:** 2026-01-24T20:14:52Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Base chunker interface with ChunkConfig, ChunkResult, ParsedElement, DocumentMetadata models
- HierarchicalChunker implementation with structure-aware splitting by paragraphs
- Table chunking by rows with header preservation (never split mid-row)
- 20% overlap between adjacent chunks for context continuity
- Clause number extraction from section hierarchy and headings
- Small chunk merging (under 100 tokens)
- Comprehensive test coverage: 22 unit tests covering normal and edge cases

## Task Commits

Each task was committed atomically:

1. **Task 1: Create base chunker interface and configuration** - `3820471` (feat)
2. **Task 2: Implement HierarchicalChunker with structure-aware splitting** - `93da05b` (feat)
3. **Task 3: Create unit tests for hierarchical chunker** - `35f8148` (test)

## Files Created/Modified

**Created:**
- `mcps/knowledge-mcp/src/knowledge_mcp/chunk/base.py` - Base chunker interface with ChunkConfig, ChunkResult, ParsedElement, DocumentMetadata models
- `mcps/knowledge-mcp/src/knowledge_mcp/chunk/hierarchical.py` - HierarchicalChunker with structure-aware splitting, table handling, overlap
- `mcps/knowledge-mcp/tests/unit/test_chunk/__init__.py` - Test package initialization
- `mcps/knowledge-mcp/tests/unit/test_chunk/test_hierarchical.py` - Comprehensive unit tests (22 tests)

**Modified:**
- `mcps/knowledge-mcp/src/knowledge_mcp/chunk/__init__.py` - Export HierarchicalChunker, ChunkConfig, ChunkResult, ParsedElement, DocumentMetadata

## Decisions Made

**1. Chunk Size Configuration**
- **Decision:** 500 token target, 1000 token max, 100 token overlap (20%)
- **Why:** Balances OpenAI embedding API limits (8191 tokens) with optimal chunk size for retrieval
- **Impact:** Ensures chunks stay well under API limits while maintaining context

**2. Structure-Aware Splitting Strategy**
- **Decision:** Split text by paragraphs (double newline), not arbitrary token boundaries
- **Why:** Preserves semantic coherence - doesn't split mid-sentence or mid-paragraph
- **Implementation:** Accumulate paragraphs until target_tokens reached, then flush chunk

**3. Table Row-Level Splitting**
- **Decision:** When tables exceed max_tokens, split by rows with header preserved in each chunk
- **Why:** Maintains table structure integrity - never split mid-row
- **Implementation:** First row is header, repeated in each chunk; rows added until token limit

**4. Overlap Strategy**
- **Decision:** Take last ~20% of previous chunk content as overlap for next chunk
- **Why:** Provides context continuity between chunks for better retrieval
- **Implementation:** Prepend overlap with "---" separator, mark chunk with has_overlap=True

**5. Small Chunk Merging**
- **Decision:** Merge chunks under 100 tokens with adjacent chunks
- **Why:** Avoids inefficient micro-chunks that don't provide enough context
- **Implementation:** Configurable via merge_small_chunks flag (default: True)

**6. Clause Number Extraction**
- **Decision:** Extract from section_hierarchy first, then heading text via regex
- **Why:** Enables filtering and navigation by clause number in standards documents
- **Pattern:** `\b(\d+(?:\.\d+){0,4})\b` (matches "5.1.2.3" format)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all functionality implemented as designed.

## Test Coverage

**Unit Tests:** 22 tests across 5 test classes
- TestChunkConfig: 2 tests (defaults, custom values)
- TestParsedElement: 2 tests (minimal, full)
- TestDocumentMetadata: 1 test (creation)
- TestChunkResult: 2 tests (minimal, full)
- TestHierarchicalChunker: 15 tests covering:
  - Empty elements error handling
  - Single/multiple element processing
  - Text splitting by paragraphs
  - Table chunking with row splitting
  - Overlap addition between chunks
  - Section hierarchy preservation
  - Clause number extraction (hierarchy, heading, none)
  - Small chunk merging
  - Metadata and page number preservation
  - Edge cases (empty tables, no clause numbers)

**Type Safety:** Zero pyright errors in strict mode

## Next Phase Readiness

**Ready for Phase 02-04 (PDF/DOCX Ingestion):**
- ✅ Chunker interface defined (BaseChunker, ChunkConfig)
- ✅ HierarchicalChunker ready for document parsing integration
- ✅ ChunkResult model ready for embedding pipeline
- ✅ ParsedElement model defines expected parser output
- ✅ DocumentMetadata model defines document info structure

**Blockers:** None

**Integration Points:**
- Document parsers (02-04) will produce ParsedElement lists
- Chunker consumes ParsedElement, produces ChunkResult
- ChunkResult feeds into embedding pipeline (Phase 03)

## Known Issues

None - all functionality working as designed.

## Usage Examples

**Basic Chunking:**
```python
from knowledge_mcp.chunk import HierarchicalChunker, ChunkConfig, ParsedElement, DocumentMetadata

# Configure chunker
config = ChunkConfig(target_tokens=500, max_tokens=1000, overlap_tokens=100)
chunker = HierarchicalChunker(config)

# Prepare elements
elements = [
    ParsedElement(
        element_type="text",
        content="The system shall...",
        section_hierarchy=["5", "5.1"],
        heading="Requirements",
    )
]

metadata = DocumentMetadata(
    document_id="ieee-15288",
    document_title="IEEE 15288-2023",
    document_type="standard",
)

# Chunk document
chunks = chunker.chunk(elements, metadata)

for chunk in chunks:
    print(f"Chunk: {chunk.token_count} tokens")
    print(f"Clause: {chunk.clause_number}")
    print(f"Has overlap: {chunk.has_overlap}")
```

**Table Chunking:**
```python
table_element = ParsedElement(
    element_type="table",
    content="Header1 | Header2\nRow1 | Data1\nRow2 | Data2",
    metadata={"caption": "Table 1: Requirements"},
)

chunks = chunker.chunk([table_element], metadata)
# Each chunk preserves header row and includes caption
```

## Performance Notes

- **Token Counting:** Uses tiktoken (cached encoding) for accurate OpenAI-compatible counts
- **Overlap Calculation:** Word-based approximation for efficiency (~20% of words)
- **Memory:** Processes elements sequentially, not loading entire document in memory

## Architecture Decisions

**Why not use Docling HybridChunker directly?**
- Docling HybridChunker expects DoclingDocument input
- Our interface uses simplified ParsedElement for flexibility
- HierarchicalChunker implements same principles (structure-aware, token limits)
- Future: Can wrap HybridChunker when full Docling integration complete

**Why separate ParsedElement from KnowledgeChunk?**
- ParsedElement: Parser output (pre-chunking)
- ChunkResult: Chunker output (post-chunking, pre-embedding)
- KnowledgeChunk: Final model (post-embedding, stored in vector DB)
- Clean separation of concerns across pipeline stages

---

*Execution completed successfully in 6m 59s with zero deviations*
