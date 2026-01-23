# Technology Stack: RAG Knowledge Management for Engineering Standards

**Project:** Knowledge MCP Integration
**Researched:** 2026-01-23
**Confidence:** HIGH

## Executive Summary

The existing knowledge-mcp implementation uses current 2025/2026 RAG best practices. Minor version updates recommended; architecture is sound.

**Key Principle:** Don't break working code. Focus on integration, not rewrite.

## Recommended Stack

### Core Framework & Runtime

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Python** | >=3.11,<3.14 | Runtime | Modern type hints, dependency compatibility |
| **Poetry** | >=1.8.0 | Package manager | Lock file ensures reproducibility |
| **MCP SDK** | >=1.25.0 | Protocol | **UPDATE from 1.0.0** - security, structured output |

### Vector Storage

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Qdrant** | >=1.16.2 | Primary store | **UPDATE from 1.7.0** - 24x compression, hybrid search |
| **ChromaDB** | >=0.5.0 | Fallback | Local development, zero-config |

**Why Qdrant:** Open-source, self-hostable, hybrid search built-in, production-ready scaling.

### Embeddings

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **OpenAI API** | >=1.0.0 | Embeddings | text-embedding-3-small: competitive, $0.02/1M tokens |
| **tiktoken** | >=0.5.0 | Tokenization | Token counting for chunking |

### Document Processing

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **pymupdf4llm** | >=0.2.9 | PDF parsing | **UPDATE from 0.0.5** - fast, OCR support |
| **python-docx** | >=1.1.0 | DOCX parsing | Solid for Word documents |
| **mammoth** | >=1.8.0 | DOCX to Markdown | Complements python-docx |

**Optional:** Add `docling >=2.70.0` for complex tables (heavier, 4 sec/page vs sub-second).

### Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | >=8.0 | Testing |
| pytest-asyncio | >=0.23 | Async testing |
| ruff | >=0.4 | Linting/formatting |
| pyright | >=1.1 | Type checking |
| pip-audit | >=2.7 | Security scanning |

## Critical Updates

**Do before production:**
1. `mcp` 1.0.0 → 1.25.0 (security, structured output)
2. `qdrant-client` 1.7.0 → 1.16.2 (compression, performance)
3. `pymupdf4llm` 0.0.5 → 0.2.9 (latest features)

## Cost Estimation

| Document Volume | Embedding Cost |
|-----------------|----------------|
| 100 pages | ~$0.01 |
| 1,000 pages | ~$0.05 |
| 10,000 pages | ~$0.50 |

**Query cost:** ~$0.00002 per query (negligible)

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Qdrant downtime | Medium | ChromaDB fallback |
| OpenAI rate limits | Low | Batch + retry logic |
| PDF parsing errors | Medium | Docling fallback for complex tables |
| Breaking changes in MCP | Low | Pin SDK version |

**Overall risk: LOW** - Stack is mature with clear fallbacks.

## Sources

- Vector DB comparisons: Airbyte, DataCamp, WaterFlai (2026)
- Embeddings: MTEB leaderboard, OpenAI pricing
- PDF processing: PyPI, Docling docs
- MCP: Official specification, Auth0 updates (June 2025)

---
*Stack research: 2026-01-23*