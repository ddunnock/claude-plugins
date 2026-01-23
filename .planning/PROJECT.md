# Knowledge MCP Integration

## What This Is

Integration of the finished knowledge-mcp RAG system into the claude-plugins repository. Knowledge-mcp provides semantic search over document collections, enabling skills like specification-refiner to ground their analysis in actual standards (INCOSE, IEEE, ISO, IEC). It serves dual purposes: a standalone marketplace plugin for general RAG use, and infrastructure powering standards-based validation in specification workflows.

## Core Value

Ground specification refinement in actual engineering standards via RAG — recommendations and validations backed by searchable standards documents, not just training data.

## Requirements

### Validated

- ✓ Plugin packaging infrastructure — existing
- ✓ MCP server pattern (session-memory) — existing
- ✓ Skill workflow pattern (specification-refiner) — existing
- ✓ Knowledge-mcp core functionality — tested in ../knowledge-mcp

### Active

- [ ] Migrate knowledge-mcp into mcps/knowledge-mcp/ (replace older version)
- [ ] Package knowledge-mcp as standalone marketplace plugin
- [ ] Integrate knowledge-mcp with specification-refiner skill
- [ ] Ingest INCOSE/IEEE/ISO/IEC standards documents
- [ ] Auto-query standards during spec validation
- [ ] Manual lookup for deep dives into specific standards

### Out of Scope

- Real-time document sync — batch ingestion sufficient for standards docs
- Multi-tenant isolation — single-user Claude Desktop context
- Custom embedding models — OpenAI embeddings work, keep it simple

## Context

**Existing codebase:**
- `mcps/knowledge-mcp/` exists but is older/incomplete version
- `../knowledge-mcp/` is finished, tested, ready to migrate
- `skills/specification-refiner/` needs to call knowledge-mcp tools

**Knowledge-mcp architecture (from ../knowledge-mcp):**
- Modular: chunk, ingest, embed, search, store components
- Vector stores: Qdrant (primary), ChromaDB (fallback)
- Document processing: PDF, DOCX via docling
- Full test coverage

**Integration pattern:**
- Skills call MCP tools via Claude Desktop
- Auto-query: skill workflow triggers search automatically
- Manual: user requests specific standard lookups

## Constraints

- **Preserve working code**: ../knowledge-mcp is tested, don't break it during migration
- **Minimize dependencies**: Use existing vector store choices (Qdrant/ChromaDB)
- **Keep it simple**: Avoid over-engineering the skill integration

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Replace mcps/knowledge-mcp entirely | External version is more complete and tested | — Pending |
| Qdrant as primary vector store | Already configured, cloud-hosted option | — Pending |
| OpenAI embeddings | Consistent with session-memory, proven quality | — Pending |

---
*Last updated: 2026-01-23 after initialization*