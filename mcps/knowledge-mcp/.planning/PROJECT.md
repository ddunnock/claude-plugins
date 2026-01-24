# Knowledge MCP - Spec Compliance

## What This Is

An MCP server providing semantic search over technical reference documents (IEEE standards, INCOSE guides, NASA handbooks) for RAG workflows. Enables AI assistants to query systems engineering knowledge with structured context.

## Core Value

The MCP server must actually work — when Claude calls the search tool, it gets real results from the knowledge base.

## Requirements

### Validated

- ✓ MCP server infrastructure (stdio transport, handlers) — existing
- ✓ Docling document ingestion (PDF, DOCX, PPTX, XLSX, HTML, images) — existing
- ✓ Docling-based chunking with HybridChunker — existing
- ✓ OpenAI embedding generation (text-embedding-3-small) — existing
- ✓ Qdrant vector storage with hybrid search support — existing
- ✓ ChromaDB fallback storage — existing
- ✓ Pydantic configuration with environment validation — existing
- ✓ Structured exception hierarchy with MCP error codes — existing
- ✓ Logging with sensitive data filtering — existing

### Active

- [ ] Working MCP tool handlers (currently return "not implemented")
- [ ] Local embedding support (offline/cost-free operation)
- [ ] Semantic search implementation
- [ ] Hybrid search implementation
- [ ] Result reranking
- [ ] Hierarchical chunking strategy
- [ ] Semantic chunking strategy
- [ ] Standards-aware chunking strategy
- [ ] CLI for document ingestion
- [ ] CLI for embedding verification
- [ ] 80% test coverage (currently 34%)
- [ ] Zero pyright errors (currently 55)
- [ ] Verified Docling integration with real documents

### Out of Scope

- GUI/web interface — MCP protocol is the interface
- Multi-tenant support — single knowledge base per deployment
- Real-time document updates — batch ingestion workflow
- Custom training/fine-tuning — uses pre-trained models only

## Context

**Recent changes:** Docling integration is a recent refactor replacing custom document parsing code. The integration is functional but needs verification with real documents and comprehensive test coverage.

**Codebase state:** Core pipeline exists but many modules are stubs or missing. The architecture is sound (layered with abstract base classes) but implementation is incomplete vs. the specification in CLAUDE.md.

**Quality gaps:** 34% test coverage (80% required), 55 pyright errors (0 required), several test files reference non-existent code.

**Codebase map:** Full analysis available in `.planning/codebase/`

## Constraints

- **Python version**: ≥3.11,<3.14 — per CLAUDE.md specification
- **Type safety**: Pyright strict mode with zero errors — per CLAUDE.md
- **Test coverage**: ≥80% — per CLAUDE.md
- **API compatibility**: Existing base class interfaces must be preserved
- **Dependency budget**: Prefer existing pyproject.toml dependencies

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Docling for parsing | Unified parser for multiple formats, IBM-backed | — Pending verification |
| Qdrant primary, ChromaDB fallback | Cloud scalability + local dev flexibility | ✓ Good |
| OpenAI embeddings | Best quality, widely available | ✓ Good |
| Abstract base classes | Enable provider switching | ✓ Good |

---
*Last updated: 2026-01-20 after initialization*
