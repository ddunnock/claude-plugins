# Pitfalls: RAG Integration for Engineering Standards

**Project:** Knowledge MCP Integration
**Researched:** 2026-01-23
**Confidence:** HIGH

## Executive Summary

40-60% of RAG implementations fail to reach production. This migration from `../knowledge-mcp` multiplies risk - moving working code that could easily break. This document identifies 15 pitfalls with prevention strategies.

## Critical Pitfalls (7)

### 1. Breaking Working Code During Migration

**What goes wrong:** Path dependencies, .env locations, import resolution all change during migration. Tests pass in old location, fail in new.

**Prevention:**
- Test in new location BEFORE any changes
- Parallel testing: old vs new for 1 week
- Keep git history for easy rollback
- Update all paths atomically

**Phase mapping:** Phase 1 (Migration) - CRITICAL

### 2. Embedding Model Version Lock-In

**What goes wrong:** Qdrant collections lock to embedding dimensions (1536). Can't change models without full reingestion.

**Prevention:**
- Store source document paths in chunk metadata
- Version collection names: `knowledge_v1_te3small`
- Build reingestion automation from day one
- Track `embedding_model` field in metadata

**Phase mapping:** Phase 1 (Migration)

### 3. Chunking Destroys Semantic Coherence

**What goes wrong:** Standards have complex structure (multi-page tables, clause hierarchies). Naive chunking splits tables mid-row, separates requirements from context.

**Prevention:**
- Structure-aware chunking (Docling HierarchicalChunker)
- Keep parent clause context in metadata
- Never split tables across chunks
- Test against known multi-page tables

**Phase mapping:** Phase 2 (Document Ingestion) - CRITICAL

### 4. No Systematic Evaluation

**What goes wrong:** Quality degrades silently. You change chunking, quality drops 20%, you don't notice until users complain.

**Prevention:**
- Build 20-50 query golden test set during Phase 2
- RAG Triad metrics: context relevance, faithfulness, answer relevance
- Run evaluation on every PR
- Track metrics over time

**Phase mapping:** Phase 2-3

### 5. PDF Parsing Loses Critical Information

**What goes wrong:** Columns merge incorrectly, tables lose structure, clause numbers disappear, math becomes gibberish.

**Prevention:**
- Validate extraction on sample docs FIRST
- Compare parsed text to original PDF
- Consider Docling for complex sections
- Preserve page/bbox for visual lookup

**Phase mapping:** Phase 2 (Document Ingestion)

### 6. Qdrant Cloud Single Point of Failure

**What goes wrong:** If Qdrant is down, entire system fails. No local fallback tested.

**Prevention:**
- Implement AND TEST ChromaDB fallback
- Graceful degradation with retry logic
- Docker Compose for local Qdrant
- Health checks before operations

**Phase mapping:** Phase 1 (Migration)

### 7. Mixing Vectors from Different Embedding Models

**What goes wrong:** Incremental updates add vectors from new model to old collection. Search becomes nonsensical.

**Prevention:**
- Store `embedding_model` in collection metadata
- Validate model match before ingestion
- Version collection names
- Audit existing collections

**Phase mapping:** Phase 1 (Migration)

## Moderate Pitfalls (5)

### 8. Ignoring Normative vs Informative

Standards have normative content (SHALL/MUST) and informative (examples). Treating equally dilutes results.

**Prevention:** Tag chunks with `normative=true/false`, filter in search.

### 9. Cross-Reference Resolution Failure

Standards reference other clauses ("as specified in 7.2.3"). Chunking breaks links.

**Prevention:** Parse cross-refs during ingestion, store in metadata.

### 10. No Cost Monitoring

OpenAI embeddings cost $0.02/1M tokens. Repeated reingestion adds up.

**Prevention:** Log token counts, cache embeddings by hash.

### 11. Skill Assumes MCP Availability

Spec-refiner calls knowledge_search, but MCP might be down. Skill hallucinates instead of admitting no access.

**Prevention:** Check tool availability, graceful degradation message.

### 12. Large Chunks Exceed Context

Multi-page tables as single chunks → 5000+ tokens. 5 chunks = 25K tokens.

**Prevention:** 2000 token max, progressive disclosure.

## Minor Pitfalls (3)

### 13. Hard-Coding Model Name

Can't upgrade without code changes.

**Prevention:** Use .env variable `EMBEDDING_MODEL`.

### 14. No Document Update Strategy

Standards get revised. No plan for updating corpus.

**Prevention:** Version tracking in metadata, scheduled audits.

### 15. Search Results Lack Provenance

User can't verify source.

**Prevention:** Return source, clause, page in results.

## Phase-Specific Warnings

| Phase | Likely Pitfalls | Mitigation |
|-------|-----------------|------------|
| Phase 1: Migration | 1, 2, 6, 7 | Test before changes, parallel run |
| Phase 2: Ingestion | 3, 4, 5 | Validate on samples first |
| Phase 3: Integration | 11, 15 | Graceful degradation |
| Phase 4+: Production | 10, 14 | Monitoring and audits |

## Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| RAG pitfalls (general) | HIGH | Multiple 2026 production sources |
| Standards challenges | MEDIUM | Inferred from PDF research + domain |
| Migration risks | HIGH | Software best practices |
| Evaluation | HIGH | Industry RAG Triad standard |

## Sources

- RAG Pitfalls: nb-data.com (23 pitfalls), IBM, Snorkel AI
- Chunking: NVIDIA, Weaviate, arXiv vision-guided
- Evaluation: RAG Triad, EvidentlyAI, Redis guides
- Migration: HeroDevs, .NET migration guides

---
*Pitfalls research: 2026-01-23*