# Feature Landscape

**Domain:** MCP Knowledge Server (RAG/Semantic Search)
**Researched:** 2026-01-20
**Confidence:** HIGH (based on MCP official documentation + existing spec alignment)

---

## Table Stakes

Features users expect from a production MCP knowledge server. Missing = product feels incomplete or broken.

### Core MCP Tool Infrastructure

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Semantic search tool** | Primary use case - AI needs to query knowledge | Medium | `knowledge_search` per spec. Embeds query, vector similarity, returns ranked results |
| **Keyword/exact search tool** | Users need precise term matching | Low | `knowledge_keyword_search` - BM25/full-text for exact phrases, acronyms |
| **Definition lookup tool** | AI assistants frequently need term definitions | Low | `knowledge_lookup` - retrieves definitions from definition chunks |
| **Statistics tool** | User needs to understand knowledge base scope | Low | `knowledge_stats` - chunk counts, document inventory, storage info |
| **Complete JSON schemas** | MCP protocol requirement for tool discovery | Low | All tools must have inputSchema with property descriptions, required fields, constraints |
| **Structured error responses** | MCP best practice per official docs | Low | `isError: true` with structured content for tool execution failures |

### Search Capabilities

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Metadata filtering** | Users need to scope searches (by document, type, etc.) | Medium | Filter by document_id, document_type, chunk_type, normative flag |
| **Result pagination/limits** | Prevent context overflow in AI | Low | `n_results` parameter, sensible defaults (10) |
| **Relevance scores** | AI needs to assess result quality | Low | 0.0-1.0 normalized scores in response |
| **Source attribution** | Critical for AI to cite sources accurately | Low | document_title, section_title, page_numbers, clause_number in each result |

### Result Formatting for AI Consumption

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Consistent response structure** | AI relies on predictable JSON format | Low | Same schema across all search tools |
| **Empty result handling** | AI needs to know when nothing found | Low | `results: []` with helpful message and suggestions |
| **Chunk content in response** | AI needs actual text, not just metadata | Low | Full chunk content returned per result |
| **Citation-ready format** | AI can directly use sources in responses | Medium | `citation` field combining document + section + clause |

### Error Handling Patterns

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Protocol errors (JSON-RPC)** | Required by MCP spec | Low | Unknown tool, invalid arguments |
| **Tool execution errors** | MCP best practice | Low | `isError: true` for API failures, empty KB, etc. |
| **Actionable error messages** | AI can explain issues to users | Low | Include suggestion field with recovery steps |
| **Recoverable flag** | AI knows whether to retry | Low | `recoverable: true/false` per exception type |

### Health and Observability

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Health check tool** | AI/operators need to verify system status | Low | `knowledge_health` - vector store + embedding service status |
| **Latency reporting** | Identify degraded performance | Low | Include latency_ms in health checks |
| **Dependency status** | Know what's working/broken | Low | Individual status per external service |

---

## Differentiators

Features that set this knowledge server apart. Not expected but highly valued for systems engineering domain.

### Domain-Specific Search

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Requirements search tool** | Specialized for finding normative requirements in standards | Medium | `knowledge_requirements` - filters to requirement chunks, returns clause IDs |
| **Normative vs. informative filtering** | Critical for standards compliance work | Low | `normative_only` parameter distinguishes mandatory (shall) vs. advisory (should) |
| **Clause number navigation** | Standards users reference by clause (e.g., "5.3.1.2") | Medium | Prefix-based clause filtering, hierarchical navigation |
| **Cross-reference awareness** | Standards reference other standards/sections | High | `references` field in metadata, potentially follow-up tool |

### Hybrid Search Excellence

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Hybrid search (dense + sparse)** | Better recall for technical terminology | High | RRF fusion with configurable weight (default 70% semantic, 30% keyword) |
| **Configurable hybrid weight** | Tune for different query types | Low | `hybrid_weight` parameter (0.0-1.0) |
| **Graceful hybrid fallback** | Works even if sparse vectors unavailable | Medium | Falls back to dense-only with warning |

### AI-Optimized Output

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Section hierarchy in results** | AI understands document structure context | Low | `section_hierarchy` array showing path to chunk |
| **Chunk type classification** | AI knows if result is definition, requirement, example, etc. | Low | `chunk_type` field enables smarter response generation |
| **Similar terms suggestions** | Handles typos, helps with terminology discovery | Medium | When lookup fails, suggest related terms via semantic + fuzzy matching |

### Operational Excellence

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Document inventory in stats** | Shows what knowledge is available | Low | Per-document metadata in `knowledge_stats` response |
| **Token count awareness** | AI can manage context budgets | Low | Include token_count per chunk in results |
| **Ingested timestamp tracking** | Know when content was added | Low | `ingested_at` per document in stats |

### MCP Protocol Best Practices

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Tool descriptions with examples** | Better tool selection by AI | Low | Rich descriptions explaining when to use each tool |
| **Output schema definitions** | Enables structured content parsing | Medium | Optional but recommended per MCP docs |
| **List changed notifications** | Dynamic tool availability (future-proofing) | Low | `notifications/tools/list_changed` capability |

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Real-time document updates** | Adds complexity for minimal value; AI queries are point-in-time | Batch ingestion workflow with `--force` re-ingest |
| **Multi-tenant access control** | Out of scope for v1; adds auth complexity | Single knowledge base per deployment |
| **Custom embedding fine-tuning** | Maintenance burden, marginal gains | Use pre-trained models (OpenAI text-embedding-3-small) |
| **Web UI/REST API** | MCP protocol IS the interface | Focus on excellent MCP tool implementations |
| **Automatic document fetching** | Security risk, scope creep | User provides documents via CLI |
| **Result caching** | Embedding + vector search is already fast; caching adds staleness risk | Rely on vector store's built-in optimization |
| **Complex query language** | AI doesn't need SQL-like syntax | Natural language queries with metadata filters |
| **Streaming results** | MCP tools return complete responses | Return complete result set; pagination via n_results |
| **Answer generation (RAG response synthesis)** | That's the AI's job, not the knowledge server | Return relevant chunks, let AI synthesize |
| **Conversation memory** | MCP tools are stateless | AI maintains conversation context |
| **Re-ranking by external model** | Adds latency, cost, complexity | Rely on vector similarity + hybrid search quality |
| **Multi-modal search (images, tables)** | Complexity vs. value for systems engineering docs | Extract table/figure captions as text; text-first |
| **Incremental document updates** | Complex conflict resolution for minimal benefit | Full document re-ingest model |

---

## Feature Dependencies

```
[Foundation]
    |
    v
[Data Model: KnowledgeChunk] -----> [Enumerations: chunk_type, document_type, error_code]
    |
    v
[Embedding Service] + [Vector Store]
    |
    v
[Search Service: semantic, keyword, hybrid, filtered]
    |
    v
[MCP Tools]
    |
    +---> knowledge_search (depends: search service, embedding)
    +---> knowledge_keyword_search (depends: search service)
    +---> knowledge_lookup (depends: search service, similar terms)
    +---> knowledge_requirements (depends: search service, chunk_type filter)
    +---> knowledge_stats (depends: vector store)
    +---> knowledge_health (depends: vector store, embedding service)
```

### Critical Path

1. **Embedding Service** - must work before search
2. **Vector Store** - must be populated before search returns results
3. **Search Service** - must work before MCP tools can function
4. **MCP Tool Handlers** - thin wrappers over search service

### Independent Features

- `knowledge_stats` and `knowledge_health` can be implemented without search working
- Keyword search can work without hybrid (dense-only fallback)
- Similar terms (fuzzy matching) is optional enhancement to lookup

---

## MVP Recommendation

For MVP, prioritize these table stakes:

1. **knowledge_search** - semantic search with basic metadata filtering
2. **knowledge_keyword_search** - exact term matching
3. **knowledge_lookup** - definition retrieval (without similar terms)
4. **knowledge_stats** - knowledge base inventory
5. **Structured error responses** - per MCP best practices
6. **Complete JSON schemas** - for all tools

Defer to post-MVP:

- **knowledge_requirements**: Specialized filter can be achieved via knowledge_search + chunk_type filter initially
- **knowledge_health**: Stats tool provides sufficient operational visibility initially
- **Similar terms suggestions**: Enhancement to lookup, not critical
- **Hybrid search**: Dense-only works well enough for MVP; hybrid is optimization
- **Output schemas**: Optional per MCP spec

---

## Complexity Estimates

| Complexity | Features |
|------------|----------|
| **Low** | Stats tool, health tool, keyword search, error handling, JSON schemas, metadata filtering, result formatting |
| **Medium** | Semantic search (embedding + vector), requirements search, similar terms, citation formatting, hybrid fallback |
| **High** | Hybrid search with RRF fusion, cross-reference awareness |

---

## Sources

**HIGH Confidence (Official Documentation):**
- MCP Tools Specification: https://modelcontextprotocol.io/docs/concepts/tools
  - Tool definition structure with inputSchema, outputSchema
  - Error handling (protocol errors vs tool execution errors)
  - Best practices for descriptions, validation, security
- MCP Resources Specification: https://modelcontextprotocol.io/docs/concepts/resources
  - Resource-based knowledge base exposure patterns
  - Pagination, metadata, annotations
- MCP Prompts Specification: https://modelcontextprotocol.io/docs/concepts/prompts
  - When to use prompts vs tools (tools for actions, prompts for templates)

**HIGH Confidence (Project Specification):**
- KMCP-A-SPEC v1.0.0 (speckit/spec.md)
  - Defines 6 MCP tools with complete schemas
  - Response formats for all scenarios
  - Error codes and handling requirements

**MEDIUM Confidence (Implementation Analysis):**
- Existing codebase analysis showing:
  - Server skeleton with tool handler stubs
  - Qdrant store with search method
  - OpenAI embedder with retry logic
  - Exception hierarchy with MCP error codes

---

*End of Feature Landscape*
