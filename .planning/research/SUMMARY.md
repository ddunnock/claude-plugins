# Research Summary: Knowledge MCP Integration

**Project:** Migrate knowledge-mcp RAG system into claude-plugins
**Date:** 2026-01-23
**Overall Confidence:** HIGH

## Key Decisions

### 1. Migration Strategy: Preserve & Integrate
The existing `../knowledge-mcp` implementation is sound. Focus on integration, not rewrite.

**Critical updates before production:**
- MCP SDK: 1.0.0 → 1.25.0 (security, structured output)
- Qdrant: 1.7.0 → 1.16.2 (24x compression, hybrid search)
- pymupdf4llm: 0.0.5 → 0.2.9 (latest features)

### 2. Architecture: Modular Components
Five independent, testable components:
1. **Ingest** - PDF/DOCX parsing via pymupdf4llm
2. **Chunk** - Hierarchical chunking preserving clause structure
3. **Embed** - OpenAI text-embedding-3-small ($0.02/1M tokens)
4. **Store** - Qdrant primary, ChromaDB fallback
5. **Search** - Semantic + keyword hybrid with reranking

### 3. Integration: Dual-Mode Access
- **Auto-query**: specification-refiner skill triggers knowledge search automatically
- **Manual**: `/lookup-standard` command for user-initiated deep dives

## MVP Feature Set

**Must have:**
- Semantic search over 4 standards (INCOSE, IEEE 15288, ISO 15288, ISO 26262)
- Source citation with section references
- Hybrid retrieval with BM25 reranking
- 256-512 token chunks with 15% overlap

**Defer:**
- Contextual retrieval (post-MVP iteration)
- Dual-granularity chunks
- Cross-standard linking

## Critical Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking working code during migration | Test in new location BEFORE changes; parallel testing |
| Embedding model lock-in | Version collection names; store model in metadata |
| Chunking destroys clause structure | Hierarchical chunking; never split tables |
| No systematic evaluation | Build 20-50 query golden test set; RAG Triad metrics |
| Qdrant cloud downtime | Implement AND TEST ChromaDB fallback |

## Build Order

1. **Phase 1: Migration** - Move code, update dependencies, test in place
2. **Phase 2: Document Ingestion** - Structure-aware chunking, PDF parsing validation
3. **Phase 3: Search & Integration** - MCP tools, skill integration
4. **Phase 4: Production** - Evaluation framework, monitoring

## Cost Estimate

| Item | Cost |
|------|------|
| 10K pages embedding | ~$0.50 |
| Per query | ~$0.00002 |
| Qdrant Cloud (free tier) | $0 |

## Sources

Research based on:
- RAG best practices: AWS, IBM, Anthropic contextual retrieval (2026)
- Vector DBs: Qdrant/ChromaDB official docs, MTEB leaderboard
- MCP: Official specification, Auth0 updates (June 2025)
- Engineering standards: INCOSE, SEBoK, ISO documentation

---
*Research synthesis: 2026-01-23*