# Technology Stack

**Project:** Knowledge MCP
**Researched:** 2026-01-20
**Confidence:** MEDIUM (based on poetry.lock analysis + training knowledge; WebSearch unavailable for version freshness verification)

## Executive Summary

The Knowledge MCP project has a solid foundation with MCP SDK 1.25.0, Docling for document parsing, and OpenAI embeddings already integrated. The gaps are: (1) local embedding model implementation, (2) search/reranking layer, (3) type safety with pyright strict mode, and (4) test coverage reaching 80%.

The recommended path forward uses **sentence-transformers 5.2.0** for local embeddings (already in poetry.lock), **Cohere 5.20.1** for cloud reranking with a local cross-encoder fallback, MCP SDK's built-in **memory transport** for testing, and strategic **type: ignore** comments for third-party library gaps.

---

## Current Stack (Already Configured)

From `poetry.lock` analysis:

| Technology | Version | Purpose | Status |
|------------|---------|---------|--------|
| mcp | 1.25.0 | MCP server SDK | Integrated |
| openai | >=1.0.0 | Cloud embeddings | Implemented |
| qdrant-client | 1.16.2 | Primary vector store | Implemented |
| chromadb | 1.4.1 | Fallback vector store | Implemented |
| docling | >=2.15.0 | Document parsing (PDF, DOCX, etc.) | Integrated |
| docling-core | >=2.15.0 | Chunking strategies | Integrated |
| tiktoken | >=0.5.0 | Token counting | Available |
| pydantic | >=2.0.0 | Configuration validation | Implemented |
| tenacity | >=8.0.0 | Retry logic | Implemented |

---

## Recommended Stack Additions

### 1. Local Embeddings

**Recommendation:** `sentence-transformers` 5.2.0 (already in poetry.lock as optional dependency)

| Model | Dimensions | Use Case | Why |
|-------|------------|----------|-----|
| `all-MiniLM-L6-v2` | 384 | Fast, small footprint | Default for offline/development |
| `all-mpnet-base-v2` | 768 | Higher quality | Production alternative |
| `multilingual-e5-base` | 768 | Non-English docs | If needed for international standards |

**Rationale:**
- sentence-transformers v5.x includes retrieval AND reranking in one package (description: "Embeddings, Retrieval, and Reranking")
- Already present in poetry.lock under `[local]` group
- Dependencies include transformers 4.41+, torch 1.11+, huggingface-hub 0.20+
- Supports CPU-only mode for environments without GPU

**Confidence:** HIGH (verified from poetry.lock)

**Implementation Notes:**
```python
from sentence_transformers import SentenceTransformer

class LocalEmbedder(BaseEmbedder):
    """Local embedder using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = SentenceTransformer(model_name)
        self._dimensions = self._model.get_sentence_embedding_dimension()

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        # sentence-transformers is sync, wrap with asyncio.to_thread
        embedding = await asyncio.to_thread(
            self._model.encode, text, convert_to_numpy=False
        )
        return embedding.tolist()
```

**Type Safety:** sentence-transformers has limited type stubs. Use `# type: ignore[reportUnknownMemberType]` selectively.

---

### 2. Reranking

**Primary Recommendation:** `cohere` 5.20.1 for cloud reranking

**Fallback Recommendation:** `sentence-transformers` cross-encoder models for local reranking

| Option | Latency | Quality | Cost | Confidence |
|--------|---------|---------|------|------------|
| Cohere Rerank v3 | ~100ms | Excellent | $1/1000 queries | HIGH |
| cross-encoder/ms-marco-MiniLM-L-6-v2 | ~50ms/doc | Good | Free | HIGH |
| bge-reranker-base | ~60ms/doc | Good | Free | MEDIUM |

**Rationale:**
- Cohere 5.20.1 already in poetry.lock under `[rerank]` group
- Cohere provides production-grade reranking with simple API
- Cross-encoders in sentence-transformers provide offline fallback
- sentence-transformers 5.x explicitly lists reranking as a feature

**Confidence:** HIGH for Cohere (in lock); MEDIUM for cross-encoder specifics (training knowledge)

**Implementation Pattern:**
```python
from abc import ABC, abstractmethod

class BaseReranker(ABC):
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Rerank documents by relevance to query."""
        ...

class CohereReranker(BaseReranker):
    """Cloud reranker using Cohere Rerank API."""

    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        # Use cohere.Client().rerank()
        ...

class CrossEncoderReranker(BaseReranker):
    """Local reranker using sentence-transformers cross-encoder."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        from sentence_transformers import CrossEncoder
        self._model = CrossEncoder(model_name)

    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        # Score pairs with cross-encoder, sort by score
        ...
```

---

### 3. Search Layer Architecture

**Recommendation:** Two-stage retrieval with optional reranking

```
Query
  │
  ▼
┌─────────────────┐
│   Embedder      │  (OpenAI or Local)
│   embed(query)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │  (Qdrant or ChromaDB)
│  search(vec,    │
│    n=top_k*3)   │  ← Over-fetch for reranking
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Reranker      │  (Optional: Cohere or CrossEncoder)
│   rerank(query, │
│    docs, top_k) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final Results  │
│   (top_k docs)  │
└─────────────────┘
```

**File Structure:**
```
src/knowledge_mcp/search/
├── __init__.py
├── base.py              # BaseSearcher ABC
├── semantic_search.py   # Simple vector search
├── hybrid_search.py     # Vector + keyword (Qdrant feature)
└── reranker.py          # Reranking strategies
```

---

### 4. MCP Testing Strategy

**Key Discovery:** MCP SDK 1.25.0 includes `mcp.shared.memory` module with `create_connected_server_and_client_session` for in-memory testing.

**Confidence:** HIGH (verified from installed package inspection)

**Testing Approach:**

| Test Type | Method | Purpose |
|-----------|--------|---------|
| Unit tests | Mock dependencies | Test individual components |
| Integration tests | In-memory MCP transport | Test full tool flow |
| E2E tests | stdio subprocess | Test real server startup |

**In-Memory Testing Pattern:**
```python
import pytest
from mcp.shared.memory import create_connected_server_and_client_session
from knowledge_mcp.server import KnowledgeMCPServer

@pytest.mark.asyncio
async def test_knowledge_search_tool():
    """Test search tool via in-memory MCP transport."""
    # Arrange
    server = KnowledgeMCPServer()

    async with create_connected_server_and_client_session(
        server.server,
        raise_exceptions=True,
    ) as client:
        # Act
        tools = await client.list_tools()
        result = await client.call_tool(
            "knowledge_search",
            {"query": "system requirements"}
        )

        # Assert
        assert any(t.name == "knowledge_search" for t in tools.tools)
        assert result.content[0].type == "text"
```

**Test Organization:**
```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_embed/
│   │   ├── test_openai_embedder.py  ← EXISTS
│   │   └── test_local_embedder.py   ← TODO
│   ├── test_search/
│   │   ├── test_semantic_search.py  ← TODO
│   │   └── test_reranker.py         ← TODO
│   └── test_store/
│       ├── test_qdrant_store.py     ← TODO (mock client)
│       └── test_chromadb_store.py   ← TODO
├── integration/
│   ├── test_mcp_server.py           ← TODO (in-memory transport)
│   └── test_search_pipeline.py      ← TODO
└── fixtures/
    └── sample_documents/            ← Need test data
```

---

### 5. Type Stub Solutions

**Problem:** pyright strict mode with 55 errors, many from third-party libraries lacking complete stubs.

**Analysis from codebase inspection:**

| Library | py.typed | Stub Quality | Strategy |
|---------|----------|--------------|----------|
| qdrant-client 1.16.2 | YES | Partial (gRPC stubs exist) | Selective `# type: ignore` |
| chromadb 1.4.1 | YES | Partial | Cast + `# type: ignore` |
| sentence-transformers | NO | None | Wrapper with explicit types |
| mcp 1.25.0 | YES | Good | Should work well |
| cohere 5.20.1 | Unknown | Unknown | Test and document |

**Recommended Strategy:**

1. **Wrapper Pattern:** Create typed wrappers around untyped libraries
   ```python
   # knowledge_mcp/embed/local_embedder.py
   from __future__ import annotations
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       # Avoid runtime import for typing
       from sentence_transformers import SentenceTransformer

   class LocalEmbedder(BaseEmbedder):
       _model: SentenceTransformer  # type: ignore[reportPrivateUsage]
   ```

2. **Targeted Ignores:** Use specific error codes
   ```python
   # Good: specific error code
   result = client.search(...)  # type: ignore[reportUnknownMemberType]

   # Bad: blanket ignore
   result = client.search(...)  # type: ignore
   ```

3. **Cast for Known Types:**
   ```python
   from typing import cast

   # ChromaDB returns untyped dict, but we know structure
   results: dict[str, Any] = cast(
       dict[str, Any],
       collection.query(...)  # type: ignore[reportUnknownMemberType]
   )
   ```

4. **Pyright Configuration Tweaks:**
   ```toml
   [tool.pyright]
   reportMissingTypeStubs = "warning"  # Already set
   # Consider adding for third-party integration:
   reportUnknownMemberType = "warning"  # Downgrade from error
   reportUnknownVariableType = "warning"
   ```

**Confidence:** MEDIUM (observed patterns in chromadb_store.py, need to test others)

---

## Installation Commands

```bash
# Core dependencies (already installed)
poetry install

# Local embeddings (optional group)
poetry install --with local

# Reranking (optional group)
poetry install --with rerank

# All optional groups for development
poetry install --with local,rerank,chromadb,docs
```

---

## Alternatives Considered

### Local Embeddings

| Considered | Verdict | Reason |
|------------|---------|--------|
| sentence-transformers | SELECTED | Already in lock, mature, dual-use (embed + rerank) |
| fastembed | REJECTED | Additional dependency, less ecosystem support |
| llama-cpp-python | REJECTED | Overkill for embeddings, complex setup |
| onnxruntime | DEFERRED | Good for optimization later, not needed initially |

### Reranking

| Considered | Verdict | Reason |
|------------|---------|--------|
| Cohere Rerank | SELECTED (primary) | Simple API, high quality, pay-per-use |
| Cross-encoder (sentence-transformers) | SELECTED (fallback) | Free, local, included with sentence-transformers |
| FlashRank | REJECTED | Less proven than alternatives |
| Custom fine-tuned | DEFERRED | Requires training data and effort |

### Vector Stores

| Considered | Status | Notes |
|------------|--------|-------|
| Qdrant Cloud | SELECTED (primary) | Already implemented, free tier available |
| ChromaDB | SELECTED (fallback) | Already implemented, local persistence |
| Pinecone | REJECTED | Proprietary, cost at scale |
| Weaviate | REJECTED | Heavier than needed |
| pgvector | DEFERRED | Good option if PostgreSQL already in stack |

---

## Version Freshness Warning

**IMPORTANT:** WebSearch was unavailable during this research. Versions are from `poetry.lock` analysis, which may be several weeks old. Before implementation:

1. Check PyPI for newer versions:
   - `pip index versions sentence-transformers`
   - `pip index versions cohere`
   - `pip index versions mcp`

2. Review changelogs for breaking changes

3. Run `poetry update` to get latest compatible versions

---

## Sources

| Source | Confidence | What It Provided |
|--------|------------|-----------------|
| poetry.lock | HIGH | Exact versions, dependencies |
| Installed packages (.venv inspection) | HIGH | py.typed markers, module structure |
| mcp/shared/memory.py | HIGH | Testing utilities for MCP |
| Codebase analysis | HIGH | Existing patterns, gaps |
| Training knowledge (May 2025) | LOW-MEDIUM | General library guidance, may be stale |

---

## Roadmap Implications

Based on this stack research:

1. **Phase 1: Local Embedder** - Straightforward, sentence-transformers API is simple
2. **Phase 2: Search Layer** - Build semantic_search.py first, add reranking later
3. **Phase 3: Type Safety** - Parallel effort, tackle file by file
4. **Phase 4: Test Coverage** - Use MCP memory transport for integration tests
5. **Phase 5: MCP Tools** - Wire search layer to tool handlers

**Research flag:** Cohere API details may need phase-specific research when implementing reranker.
