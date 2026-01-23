# Feature Landscape: RAG for Engineering Standards

**Domain:** RAG-powered engineering standards search and validation
**Researched:** 2026-01-23
**Confidence:** MEDIUM-HIGH

## Executive Summary

RAG systems in 2026 have shifted from "retrieve and stuff" to intelligent context engineering. For engineering standards, traceability and citation are critical - users must trace recommendations to specific standard clauses.

## Table Stakes

Features users expect from any standards RAG system:

| Feature | Why Expected | Complexity |
|---------|--------------|------------|
| **Semantic search** | Core RAG value - find by meaning | Medium |
| **Source citation with section refs** | Compliance requires traceability | Medium |
| **Multi-standard corpus** | Work across INCOSE/IEEE/ISO/IEC | Low |
| **Context-aware retrieval** | Pass spec context to improve relevance | Medium |
| **Chunk overlap** | Prevent semantic boundary issues | Low |
| **Relevance scoring** | Users need confidence in results | Medium |
| **Full-text fallback** | When semantic fails, use keywords | Low |

## Differentiators

Features that create significant value:

| Feature | Value | Complexity |
|---------|-------|------------|
| **Auto-query during spec validation** | Proactive standards grounding | High |
| **Contextual retrieval with reranking** | 49% fewer retrieval failures | High |
| **Standards version awareness** | Track ISO 15288:2023 vs 2015 | Medium |
| **Manual deep-dive mode** | User-triggered focused search | Low |
| **Evaluation metrics** | Context precision, faithfulness | High |
| **Dual-granularity chunks** | Small for retrieval, large for context | High |

## Anti-Features (Do NOT Build)

| Anti-Feature | Why Avoid |
|--------------|-----------|
| Custom embedding training | Over-engineering for marginal gains |
| Real-time document sync | Standards are stable - batch is fine |
| Multi-tenant isolation | Single-user Claude Desktop context |
| Full document as context | Exceeds limits, reduces relevance |
| Fixed-size chunks without eval | "One size fits all" fails |
| No reranking | Results in poor retrieval quality |
| Skipping evaluation framework | 90% of issues start in retrieval |

## Feature Dependencies

```
Foundation (First):
├─ Document ingestion → Chunking → Embedding → Vector store
└─ Basic semantic search

Retrieval Quality (Second):
├─ Hybrid retrieval (semantic + keyword)
├─ Reranking (BM25 or cross-encoder)
└─ Contextual retrieval

Integration (Third):
├─ Auto-query during spec validation
└─ Manual deep-dive mode

Advanced (Fourth, after evaluation):
├─ Dual-granularity chunks
├─ Standards version tracking
└─ Cross-standard linking
```

## MVP Recommendation

**Phase 1: Foundation**
- Semantic search over 4 core standards (INCOSE, IEEE 15288, ISO 15288, ISO 26262)
- Source citation with section references
- Hybrid retrieval with BM25 reranking
- 256-512 token chunks with 15% overlap
- Manual deep-dive mode

**Phase 2: Integration**
- Auto-query during spec validation
- Context-aware retrieval
- Basic evaluation metrics

**Defer to Post-MVP:**
- Contextual retrieval (high value but can iterate)
- Dual-granularity chunks
- Cross-standard linking
- Compliance matrix generation

## Standards-Specific Considerations

**Corpus characteristics:**
- Stability: Standards change slowly (yearly/multi-year)
- Structure: Hierarchical sections with clause numbers
- Cross-references: Standards reference each other extensively
- Version sensitivity: Must track specific versions

**Trust requirements:**
- Exact citations: "ISO 15288:2023, Clause 6.4.3, paragraph 2"
- Source viewing: User must see original text
- Confidence scores: Retrieval relevance visible
- Negative results: "No standard found" is valid

## Sources

- RAG Architecture: AWS, IBM, Anthropic contextual retrieval (2026)
- Engineering Standards: INCOSE, SEBoK, ISO documentation
- Anti-patterns: IBM RAG problems, production failure analyses

---
*Features research: 2026-01-23*