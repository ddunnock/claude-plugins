# Project Research Summary

**Project:** Knowledge MCP
**Domain:** MCP Server for RAG/Semantic Search over Technical Documents
**Researched:** 2026-01-20
**Confidence:** HIGH (codebase analysis + existing spec alignment + MCP official docs)

## Executive Summary

Knowledge MCP is a partially-implemented MCP server for semantic search over systems engineering standards (IEEE, INCOSE, NASA handbooks). The codebase has solid foundations (Docling ingestion, Qdrant/ChromaDB stores, OpenAI embeddings) but critical gaps: the MCP server returns empty tool lists, search layer is missing, test coverage is 34% (target 80%), and pyright shows 55 errors. The recommended approach is to fix foundations first (broken tests, type errors), then implement the search layer to connect existing stores to MCP tools, finally wire up functional MCP tool handlers.

The architecture should follow the established patterns: abstract base classes (BaseSearcher, BaseReranker), Pydantic models for data contracts, factory methods for instantiation. The search layer sits between store and MCP server, composing embedder + store to provide query-centric operations. Local embeddings via sentence-transformers (already in poetry.lock) and Cohere reranking are available but optional.

Key risks: (1) Test-code mismatch causing false confidence (tests import non-existent classes), (2) Third-party type stub gaps requiring careful adapter patterns, (3) Docling API instability requiring exact version pinning. Mitigation requires running `pytest --collect-only` before any work, creating typed wrappers for external libraries, and pinning docling to exact version.

## Key Findings

### Recommended Stack

The technology stack is largely complete in poetry.lock. Core technologies are production-ready; additions are minimal.

**Core technologies (already integrated):**
- **MCP SDK 1.25.0:** Server protocol with in-memory test transport available
- **Docling 2.15+:** Document parsing (PDF, DOCX) with hierarchical chunking
- **Qdrant Cloud / ChromaDB:** Vector stores with fallback logic (needs error categorization fix)
- **OpenAI embeddings:** text-embedding-3-small for production quality

**Additions recommended:**
- **sentence-transformers 5.2.0:** Local embeddings + cross-encoder reranking (already in `[local]` group)
- **Cohere 5.20.1:** Cloud reranking (already in `[rerank]` group)

**Critical version requirements:**
- Pin docling exactly (`==2.15.0`) to avoid API breakage
- MCP SDK 1.25.0 provides `mcp.shared.memory` for integration testing

### Expected Features

**Must have (table stakes):**
- `knowledge_search` - semantic search with metadata filtering
- `knowledge_keyword_search` - exact term matching for acronyms/phrases
- `knowledge_lookup` - definition retrieval
- `knowledge_stats` - knowledge base inventory
- Structured error responses with `isError: true`
- Complete JSON schemas for all tools

**Should have (differentiators):**
- `knowledge_requirements` - specialized for normative requirements
- Hybrid search (dense + sparse) via Qdrant
- Reranking via Cohere
- Section hierarchy in results for document context

**Defer (v2+):**
- Real-time document updates
- Multi-tenant access control
- Custom embedding fine-tuning
- Cross-reference awareness

### Architecture Approach

The search layer should use the Facade pattern with Strategy for different search modes. MCP tool handlers are thin wrappers calling `SemanticSearcher.search()` which composes embedder + store + optional reranker.

**Major components:**
1. **Search Layer** (`search/`) - Query embedding, retrieval, optional reranking
2. **MCP Server** (`server.py`) - Tool dispatch, protocol handling
3. **Embedder** (`embed/`) - Text-to-vector (OpenAI primary, local fallback)
4. **Store** (`store/`) - Vector persistence (Qdrant primary, ChromaDB fallback)
5. **CLI** (`cli/`) - Operational commands for ingestion and verification

### Critical Pitfalls

1. **Test-code mismatch** - Tests import non-existent classes (IngestOutcome, IngestSection). Run `pytest --collect-only` before any work. Fix imports first.

2. **Type stub gaps** - Qdrant/ChromaDB lack complete stubs, causing 55 pyright errors. Create typed wrapper functions with explicit return types. Use `cast()` with documented reasoning, not blanket `type: ignore`.

3. **Store fallback masking config errors** - Generic `Exception` catch causes auth errors to silently fall back to ChromaDB. Categorize exceptions: only fallback on transient errors (timeout, connection refused), not config errors (bad API key).

4. **MCP server without functional tools** - `handle_list_tools()` returns empty list. Implement ONE working tool end-to-end before adding more. Write integration test using MCP memory transport.

5. **Docling API instability** - Pre-1.0 library with breaking changes. Pin exact version, replace `hasattr()` checks with explicit attribute access, add integration tests with real documents.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation Fixes
**Rationale:** Cannot measure progress without working tests. Pyright errors block CI enforcement. Must fix before any new code.
**Delivers:** Clean test collection, zero pyright errors, accurate coverage baseline
**Addresses:** Infrastructure needed for all subsequent phases
**Avoids:** Test-code mismatch (Pitfall 1), Type stub gaps (Pitfall 2)

Key tasks:
- Fix test imports (IngestOutcome, IngestSection, config fields)
- Create typed wrappers for Qdrant/ChromaDB calls
- Pin docling exact version
- Establish `pytest --collect-only` as pre-flight check

### Phase 2: Search Layer Implementation
**Rationale:** Search layer is the missing link between existing stores and MCP tools. Required before MCP tools can function.
**Delivers:** `SemanticSearcher`, `BaseSearcher` interface, search models
**Uses:** Existing embedder (OpenAI), existing store (Qdrant/ChromaDB)
**Implements:** Core search architecture from ARCHITECTURE.md

Key tasks:
- Create `search/models.py` (SearchResult, SearchQuery)
- Implement `search/base.py` (BaseSearcher ABC)
- Implement `search/semantic.py` (SemanticSearcher composing embedder + store)
- Add factory `create_searcher()` in `search/__init__.py`
- Unit tests with mock embedder/store

### Phase 3: MCP Tool Implementation
**Rationale:** MCP tools are the user-facing interface. Depends on search layer.
**Delivers:** Working `knowledge_search`, `knowledge_stats` tools at minimum
**Addresses:** Table stakes features from FEATURES.md
**Avoids:** Empty tool implementations (Pitfall 3)

Key tasks:
- Implement `knowledge_search` tool handler calling SemanticSearcher
- Implement `knowledge_stats` tool handler
- Add MCP integration test using `mcp.shared.memory` transport
- Wire search layer to server.py

### Phase 4: Test Coverage to 80%
**Rationale:** After core functionality works, achieve compliance target. Must cover edge cases.
**Delivers:** 80% line coverage, 75% branch coverage
**Uses:** AAA pattern established in existing tests, MCP memory transport for integration

Key tasks:
- Unit tests for search layer (~20 tests)
- Integration tests for MCP tools (~10 tests)
- Edge case tests (empty results, score thresholds, large batches)
- Store fallback tests with categorized exceptions

### Phase 5: Extended Features
**Rationale:** After MVP works, add differentiating features.
**Delivers:** Hybrid search, reranking, CLI commands, `knowledge_requirements` tool
**Uses:** sentence-transformers (local), Cohere (reranking)

Key tasks:
- Implement `HybridSearcher` for Qdrant hybrid mode
- Implement `CohereReranker` and `CrossEncoderReranker`
- Implement CLI with Click (ingest, verify, search commands)
- Add remaining MCP tools (`knowledge_keyword_search`, `knowledge_lookup`, `knowledge_requirements`)

### Phase Ordering Rationale

- **Phase 1 before all others:** Cannot trust test results or CI without fixing foundations. Pyright errors indicate potential runtime bugs.
- **Phase 2 before Phase 3:** MCP tools depend on search layer. Search layer is straightforward (compose existing components) while MCP protocol requires more care.
- **Phase 3 before Phase 4:** Need functional code to test. Coverage without functionality is meaningless.
- **Phase 4 before Phase 5:** Establish quality baseline before adding complexity. Extended features are optional for MVP.
- **Phases 2-3 could partially overlap:** Search models and base interface don't depend on MCP work.

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 5 (Reranking):** Cohere API details need verification. Cross-encoder model selection depends on document domain.
- **Phase 5 (Hybrid Search):** Qdrant hybrid mode configuration needs testing with actual data.

**Phases with standard patterns (skip research-phase):**
- **Phase 1:** Standard Python typing/testing patterns
- **Phase 2:** Facade pattern, dependency injection - well documented
- **Phase 3:** MCP SDK has good documentation and examples
- **Phase 4:** pytest patterns are established in codebase

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified from poetry.lock, installed packages inspected |
| Features | HIGH | Based on MCP official docs + existing spec (speckit/spec.md) |
| Architecture | HIGH | Direct codebase analysis, established patterns |
| Pitfalls | HIGH | Concrete evidence from code inspection |

**Overall confidence:** HIGH

### Gaps to Address

- **Cohere API specifics:** Verify current Cohere rerank API (v3 vs v2) during Phase 5
- **Version freshness:** poetry.lock may be weeks old. Run `poetry update` before Phase 1
- **Docling 2.15 exact API:** Current `hasattr()` usage suggests uncertainty about stable API

## Sources

### Primary (HIGH confidence)
- poetry.lock analysis - exact versions and dependencies
- Codebase inspection (`src/knowledge_mcp/`) - actual implementation state
- MCP Tools Specification (modelcontextprotocol.io/docs/concepts/tools) - protocol requirements
- KMCP-A-SPEC v1.0.0 (speckit/spec.md) - project specification

### Secondary (MEDIUM confidence)
- Installed package inspection (.venv) - py.typed markers, module structure
- MCP SDK `mcp.shared.memory` module - testing utilities confirmed

### Tertiary (LOW confidence)
- Training knowledge (May 2025 cutoff) - general library patterns, may be stale
- Cohere/sentence-transformers API details - need verification

---
*Research completed: 2026-01-20*
*Ready for roadmap: yes*
