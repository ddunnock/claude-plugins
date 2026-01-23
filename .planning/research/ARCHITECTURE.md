# Architecture: RAG Knowledge Management System

**Project:** Knowledge MCP Integration
**Researched:** 2026-01-23
**Confidence:** HIGH

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Desktop                               │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ specification-  │    │         knowledge-mcp             │   │
│  │ refiner skill   │───▶│         (MCP Server)              │   │
│  │                 │    │                                    │   │
│  │ Auto-query +    │    │  ┌────────────────────────────┐   │   │
│  │ Manual lookup   │    │  │     RAG Components         │   │   │
│  └─────────────────┘    │  │  Ingest→Chunk→Embed→Store  │   │   │
│                         │  │         ↓                   │   │   │
│                         │  │       Search                │   │   │
│                         │  └────────────────────────────┘   │   │
│                         └──────────────────────────────────┘   │
│                                       │                         │
└───────────────────────────────────────┼─────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │          Qdrant Cloud                  │
                    │      (or ChromaDB fallback)            │
                    └────────────────────────────────────────┘
```

## Component Architecture

### Core Components (5 modules)

| Component | Interface | Input | Output |
|-----------|-----------|-------|--------|
| **Ingest** | `ingest(path) → Document` | File path | Parsed document |
| **Chunk** | `chunk(doc) → Chunks` | Document | List of chunks with metadata |
| **Embed** | `embed(texts) → Vectors` | Text strings | Embedding vectors |
| **Store** | `upsert/search/delete` | Vectors + metadata | CRUD operations |
| **Search** | `search(query, k) → Results` | Natural language | Ranked results |

### Data Flow

**Ingestion Path:**
```
PDF/DOCX → Ingest (Docling) → Chunk (Hierarchical) → Embed (OpenAI) → Store (Qdrant)
```

**Search Path:**
```
Query → Embed → Store.search → Rerank → Format → Return
```

## Key Patterns

### Pattern 1: Modular Components
Each component is independent, testable, swappable:
```python
class SearchComponent:
    def __init__(self, embed: EmbedComponent, store: StoreComponent):
        self.embed = embed
        self.store = store

    def search(self, query: str, collection: str, k: int) -> List[Result]:
        vector = self.embed.embed([query])[0]
        return self.store.search(collection, vector, k)
```

### Pattern 2: Thin MCP Wrappers
MCP tools call components, don't contain logic:
```python
@app.call_tool()
async def search_knowledge(query: str, collection: str = "default", k: int = 5):
    # Validation, call components, format output
    return search_component.search(query, collection, k)
```

### Pattern 3: Vector Store Abstraction
Abstract interface with Qdrant primary, ChromaDB fallback:
```python
class VectorDB(ABC):
    @abstractmethod
    def upsert(self, collection, vectors, payloads): pass
    @abstractmethod
    def search(self, collection, query_vector, limit, filters): pass

def get_vector_db() -> VectorDB:
    try:
        return QdrantVectorDB(url=QDRANT_URL)
    except:
        return ChromaVectorDB()  # Fallback
```

### Pattern 4: Hierarchical Chunking
Preserve document structure for standards:
```python
chunker = HierarchicalChunker(
    tokenizer="cl100k_base",
    max_tokens=512,
    include_tables=True
)
# Each chunk includes: section, page, type (normative/informative)
```

### Pattern 5: Dual-Mode Integration
Auto-query (skill-triggered) + Manual (user-triggered):
```python
# Auto-query in specification-refiner
context = await mcp_client.call_tool("knowledge-mcp", "search_knowledge", {...})

# Manual lookup via /lookup-standard command
results = await mcp_client.call_tool("knowledge-mcp", "search_knowledge", {...})
```

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Instead |
|--------------|---------|---------|
| Monolithic pipeline | Can't test or swap parts | Modular components |
| Tight vector store coupling | Vendor lock-in | Abstraction layer |
| No chunk metadata | No traceability | Rich metadata (source, section, page) |
| Naive text splitting | Breaks context | Semantic/hierarchical chunking |
| Raw component APIs as MCP | No validation | Thin wrappers with validation |

## Build Order

| Phase | Components | Deliverable |
|-------|------------|-------------|
| 1. Foundation | Store + Embed | Can create/store embeddings |
| 2. Pipeline | Chunk + Ingest | Can ingest PDFs with structured chunks |
| 3. Search | Search + formatting | Can search with natural language |
| 4. MCP | Server + tools | MCP callable from Claude Desktop |
| 5. Integration | Skill + commands | Spec validation grounded in standards |

## Scalability

| Scale | Vector Storage | Chunking | Search |
|-------|----------------|----------|--------|
| 10 docs | ChromaDB | 512 tokens | Brute-force OK |
| 1,000 docs | Qdrant cloud | 512 tokens | HNSW index |
| 100,000 docs | Qdrant cluster | 256 tokens | HNSW + quantization |

## Integration Points

**Session-memory pattern:** Similar structure - `components/` instead of `modules/`

**Specification-refiner integration:**
- Auto-query: Skill calls `mcp__knowledge-mcp__search()`
- Results formatted as: "INCOSE 6.4.2 recommends..."

**Plugin packaging:** Standard `.claude-plugin/plugin.json` format

## Sources

- RAG Architecture: AWS, IBM, arXiv surveys (2026)
- MCP: Official specification, Anthropic docs
- Vector DBs: Qdrant/ChromaDB official docs
- Docling: IBM tutorials, GitHub

---
*Architecture research: 2026-01-23*