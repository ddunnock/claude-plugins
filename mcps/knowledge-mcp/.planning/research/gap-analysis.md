# Knowledge MCP v1.0 to v2.0 Gap Analysis

**Analysis Date:** 2027-01-27
**v1.0 Status:** Complete (86% test coverage, working MCP server)
**v2.0 Target:** Learning Knowledge Management System

---

## Executive Summary

Knowledge MCP v1.0 provides a solid foundation with working semantic search, document ingestion, embeddings, and MCP server infrastructure. The transition to v2.0 requires:

1. **Database Layer Addition** - PostgreSQL for relational data (projects, feedback, scoring)
2. **Web Ingestion** - Crawl4AI integration for web content
3. **Workflow Searchers** - Specialized retrieval for RCCA, trade studies, exploration, planning
4. **Learning Loop** - Feedback collection, scoring, and recommendation improvement
5. **Enhanced Models** - Authority scores, freshness tracking, relationships

The v1.0 architecture is clean and modular, enabling incremental extension rather than rewrite.

---

## Reusable Components Table

| Module | Path | v2.0 Reuse | Modifications Needed |
|--------|------|------------|---------------------|
| **models/chunk.py** | `src/knowledge_mcp/models/chunk.py` | Direct reuse | None - extend separately |
| **models/document.py** | `src/knowledge_mcp/models/document.py` | Direct reuse | None - extend separately |
| **store/base.py** | `src/knowledge_mcp/store/base.py` | Direct reuse | Abstract interface unchanged |
| **store/qdrant_store.py** | `src/knowledge_mcp/store/qdrant_store.py` | Direct reuse | 368 lines, mature implementation |
| **store/chromadb_store.py** | `src/knowledge_mcp/store/chromadb_store.py` | Direct reuse | 255 lines, fallback store |
| **embed/base.py** | `src/knowledge_mcp/embed/base.py` | Direct reuse | Abstract interface unchanged |
| **embed/openai_embedder.py** | `src/knowledge_mcp/embed/openai_embedder.py` | Direct reuse | 371 lines, batch + cache |
| **embed/local_embedder.py** | `src/knowledge_mcp/embed/local_embedder.py` | Direct reuse | 227 lines, sentence-transformers |
| **embed/cache.py** | `src/knowledge_mcp/embed/cache.py` | Direct reuse | Disk-based embedding cache |
| **search/semantic_search.py** | `src/knowledge_mcp/search/semantic_search.py` | Direct reuse | 184 lines, core search |
| **search/reranker.py** | `src/knowledge_mcp/search/reranker.py` | Direct reuse | Cohere + local cross-encoder |
| **search/models.py** | `src/knowledge_mcp/search/models.py` | Direct reuse | SearchResult dataclass |
| **chunk/base.py** | `src/knowledge_mcp/chunk/base.py` | Direct reuse | ChunkConfig, ChunkResult |
| **chunk/hierarchical.py** | `src/knowledge_mcp/chunk/hierarchical.py` | Direct reuse | 574 lines, structure-aware |
| **ingest/base.py** | `src/knowledge_mcp/ingest/base.py` | Direct reuse | BaseIngestor interface |
| **ingest/pipeline.py** | `src/knowledge_mcp/ingest/pipeline.py` | Direct reuse | 284 lines, orchestrator |
| **ingest/pdf_ingestor.py** | `src/knowledge_mcp/ingest/pdf_ingestor.py` | Direct reuse | Docling-based PDF |
| **ingest/docx_ingestor.py** | `src/knowledge_mcp/ingest/docx_ingestor.py` | Direct reuse | python-docx based |
| **utils/config.py** | `src/knowledge_mcp/utils/config.py` | Direct reuse | Pydantic config |
| **utils/hashing.py** | `src/knowledge_mcp/utils/hashing.py` | Direct reuse | Content deduplication |
| **utils/tokenizer.py** | `src/knowledge_mcp/utils/tokenizer.py` | Direct reuse | Token counting |
| **utils/normative.py** | `src/knowledge_mcp/utils/normative.py` | Direct reuse | Normative detection |
| **exceptions.py** | `src/knowledge_mcp/exceptions.py` | Direct reuse | Exception hierarchy |
| **cli/main.py** | `src/knowledge_mcp/cli/main.py` | Direct reuse | Typer CLI framework |
| **cli/ingest.py** | `src/knowledge_mcp/cli/ingest.py` | Direct reuse | `knowledge ingest` |
| **cli/verify.py** | `src/knowledge_mcp/cli/verify.py` | Direct reuse | `knowledge verify` |
| **monitoring/token_tracker.py** | `src/knowledge_mcp/monitoring/token_tracker.py` | Direct reuse | Token usage tracking |
| **evaluation/*** | `src/knowledge_mcp/evaluation/` | Direct reuse | Golden set evaluation |

**Total Reusable:** 27 modules / 27 modules (100% reusable, 0 requires rewrite)

---

## Extension Requirements Table

| Component | Current State | v2.0 Extension | Effort |
|-----------|---------------|----------------|--------|
| **models/chunk.py** | Basic KnowledgeChunk dataclass | Add `source_url`, `authority_score`, `freshness_date` fields | Low |
| **models/document.py** | Basic DocumentMetadata | Add `authority_tier`, `last_verified`, `source_type` (file/web) | Low |
| **store/base.py** | Single collection interface | Add optional collection parameter for multi-collection queries | Low |
| **server.py** | 2 tools (search, stats) | Add 13 more tools (ingest, assess, feedback, workflow, admin) | High |
| **utils/config.py** | Env-based config | Add PostgreSQL connection, Crawl4AI settings, scoring thresholds | Medium |
| **search/semantic_search.py** | Basic similarity search | Add score_boost parameter for authority-weighted results | Low |
| **ingest/pipeline.py** | File-based ingestion only | Add web source detection and routing to WebIngestor | Medium |

### Detailed Extension Specifications

#### models/chunk.py Extensions
```python
# New optional fields for v2.0
source_url: Optional[str] = None  # For web-sourced content
authority_score: float = 0.5      # 0.0-1.0 effectiveness score
freshness_date: Optional[str] = None  # Last verified/updated
source_type: Literal["file", "web"] = "file"
```

#### models/document.py Extensions
```python
# New optional fields for v2.0
authority_tier: int = 2           # 1=primary, 2=secondary, 3=tertiary
last_verified: Optional[str] = None
source_type: Literal["file", "web"] = "file"
acquisition_method: Optional[str] = None  # "manual", "crawl", "api"
```

#### server.py Tool Extensions
Current tools:
- `knowledge_search` - Semantic search
- `knowledge_stats` - Collection statistics

v2.0 additional tools:
- `knowledge_ingest` - Trigger document/web ingestion
- `knowledge_sources` - List/filter sources
- `knowledge_assess` - Coverage assessment
- `knowledge_preflight` - Check before acquisition
- `knowledge_acquire` - Acquire web content
- `knowledge_request` - Track acquisition requests
- `knowledge_rcca` - RCCA workflow support
- `knowledge_trade` - Trade study support
- `knowledge_explore` - Exploration support
- `knowledge_plan` - Planning support + capture
- `knowledge_feedback` - Collect effectiveness feedback
- `knowledge_admin` - Health reports, refresh
- `knowledge_relationships` - Relationship graph queries

---

## New Components Required Table

| Component | Purpose | Dependencies | Complexity | Priority |
|-----------|---------|--------------|------------|----------|
| **db/models.py** | SQLAlchemy ORM models for PostgreSQL | SQLAlchemy 2.0, asyncpg | Medium | P1 |
| **db/repositories.py** | Repository pattern for data access | db/models.py | Medium | P1 |
| **db/migrations/** | Alembic migration scripts | Alembic, db/models.py | Low | P1 |
| **ingest/web_ingestor.py** | Web content ingestion via Crawl4AI | Crawl4AI | High | P1 |
| **search/workflow_rcca.py** | RCCA-specific retrieval (similar failures) | search/semantic_search.py | Medium | P2a |
| **search/workflow_trade.py** | Trade study retrieval (criteria, alternatives) | search/semantic_search.py | Medium | P2a |
| **search/workflow_explore.py** | Exploration retrieval (anti-patterns, gaps) | search/semantic_search.py | Medium | P2a |
| **search/workflow_plan.py** | Planning retrieval (templates, precedents) | search/semantic_search.py | Medium | P2a |
| **capture/project.py** | Project lifecycle management | db/repositories.py | Medium | P2a |
| **capture/template.py** | Template capture and tracking | db/repositories.py | Medium | P2a |
| **feedback/collector.py** | Three-tier feedback collection | db/repositories.py | Medium | P2b |
| **scoring/simple.py** | Simple effectiveness scoring | feedback/collector.py | Low | P2b |
| **scoring/advanced.py** | Multi-factor scoring with propagation | scoring/simple.py | High | P3 |
| **graph/relationships.py** | Relationship graph storage | db/repositories.py | High | P3 |
| **sync/offline.py** | Offline mode with ChromaDB sync | store/chromadb_store.py | Medium | P1 |
| **admin/health.py** | Health reports and analytics | db/repositories.py | Low | P3 |
| **admin/refresh.py** | Source refresh management | ingest/pipeline.py | Medium | P3 |

### Detailed New Component Specifications

#### db/models.py - SQLAlchemy Models
```python
# Core models for PostgreSQL
class Source(Base):
    """Document or web source metadata"""
    id: Mapped[uuid.UUID]
    source_type: Mapped[str]  # "file" | "web"
    url_or_path: Mapped[str]
    title: Mapped[str]
    authority_tier: Mapped[int]  # 1-3
    last_ingested: Mapped[datetime]
    last_verified: Mapped[Optional[datetime]]
    status: Mapped[str]  # "active" | "stale" | "archived"

class Project(Base):
    """Project/engagement for outcome tracking"""
    id: Mapped[uuid.UUID]
    name: Mapped[str]
    project_type: Mapped[str]  # "rcca" | "trade" | "exploration" | "planning"
    status: Mapped[str]  # "draft" | "active" | "completed" | "abandoned"
    created_at: Mapped[datetime]
    completed_at: Mapped[Optional[datetime]]
    outcome: Mapped[Optional[str]]

class TemplateUsage(Base):
    """Track template/chunk usage in projects"""
    id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]
    chunk_id: Mapped[str]  # References vector store
    usage_context: Mapped[str]
    created_at: Mapped[datetime]

class Feedback(Base):
    """Three-tier feedback collection"""
    id: Mapped[uuid.UUID]
    template_usage_id: Mapped[uuid.UUID]
    feedback_tier: Mapped[int]  # 1=implicit, 2=quick, 3=detailed
    rating: Mapped[Optional[int]]  # 1-5 for tier 2+
    outcome: Mapped[Optional[str]]  # "success" | "partial" | "failure"
    notes: Mapped[Optional[str]]
    created_at: Mapped[datetime]

class ChunkScore(Base):
    """Effectiveness scores for chunks"""
    chunk_id: Mapped[str]  # References vector store
    score: Mapped[float]  # 0.0-1.0
    confidence: Mapped[float]  # 0.0-1.0
    usage_count: Mapped[int]
    last_updated: Mapped[datetime]

class Relationship(Base):
    """Knowledge graph relationships"""
    id: Mapped[uuid.UUID]
    source_chunk_id: Mapped[str]
    target_chunk_id: Mapped[str]
    relationship_type: Mapped[str]  # "causal" | "contradictory" | "supporting"
    confidence: Mapped[float]
    created_at: Mapped[datetime]

class AcquisitionRequest(Base):
    """Pending content acquisition requests"""
    id: Mapped[uuid.UUID]
    requested_url: Mapped[str]
    reason: Mapped[str]
    priority: Mapped[int]
    status: Mapped[str]  # "pending" | "approved" | "rejected" | "completed"
    requested_at: Mapped[datetime]
    completed_at: Mapped[Optional[datetime]]
```

#### ingest/web_ingestor.py - Crawl4AI Integration
```python
class WebIngestor(BaseIngestor):
    """Web content ingestion via Crawl4AI"""

    def __init__(self, config: WebIngestConfig):
        self.crawler = AsyncWebCrawler()
        self.config = config

    async def ingest(self, url: str) -> ParsedDocument:
        """Crawl and parse web content"""
        # Use Crawl4AI for JavaScript rendering
        result = await self.crawler.arun(url=url, ...)
        # Extract clean markdown content
        # Parse into ParsedElements
        # Return ParsedDocument

    async def preflight(self, url: str) -> PreflightResult:
        """Check URL before full acquisition"""
        # Verify accessibility
        # Check robots.txt
        # Estimate content size
        # Return preflight status
```

#### search/workflow_rcca.py - RCCA Support
```python
class RCCASearcher:
    """Root Cause Corrective Action workflow support"""

    def __init__(self, searcher: SemanticSearcher, db: Repository):
        self.searcher = searcher
        self.db = db

    async def find_similar_failures(
        self, failure_description: str, n_results: int = 10
    ) -> list[SimilarFailure]:
        """Find historical similar failures"""
        # Search for similar failures
        # Include causal chain references
        # Boost by outcome effectiveness

    async def get_causal_chain(self, chunk_id: str) -> list[CausalLink]:
        """Retrieve causal analysis chain"""
        # Query relationship graph
        # Return causal relationships
```

---

## Migration Complexity Assessment

### Low Complexity (Direct Extension)
| Change | Effort | Risk |
|--------|--------|------|
| Add fields to KnowledgeChunk | 1 day | Low |
| Add fields to DocumentMetadata | 1 day | Low |
| Extend KnowledgeConfig | 1 day | Low |
| Add score_boost to search | 2 days | Low |

### Medium Complexity (New Integration)
| Change | Effort | Risk |
|--------|--------|------|
| PostgreSQL connection setup | 2 days | Medium |
| SQLAlchemy model definitions | 3 days | Medium |
| Alembic migration framework | 2 days | Low |
| Web ingestor (Crawl4AI) | 5 days | Medium |
| Workflow searchers (4 types) | 8 days | Medium |
| Project/Template capture | 5 days | Medium |
| Offline sync manager | 3 days | Medium |

### High Complexity (Core Changes)
| Change | Effort | Risk |
|--------|--------|------|
| 13 new MCP tool handlers | 10 days | High |
| Feedback collection system | 5 days | Medium |
| Multi-factor scoring | 5 days | High |
| Relationship graph | 5 days | High |

### Total Estimated Effort
| Phase | Effort | Calendar Time |
|-------|--------|---------------|
| Phase 1 (Core + Acquisition) | 15 days | 3 weeks |
| Phase 2a (Workflow + Capture) | 15 days | 3 weeks |
| Phase 2b (Feedback + Scoring) | 8 days | 2 weeks |
| Phase 3 (Advanced + Admin) | 12 days | 3 weeks |
| **Total** | **50 days** | **11 weeks** |

---

## Recommended Implementation Order

### Phase 1: Core + Acquisition (Weeks 1-3)
1. **Week 1: Database Foundation**
   - Set up PostgreSQL connection and configuration
   - Define SQLAlchemy models (Source, AcquisitionRequest)
   - Create Alembic migration framework
   - Add PostgreSQL-related config to `utils/config.py`

2. **Week 2: Web Ingestion**
   - Implement `ingest/web_ingestor.py` with Crawl4AI
   - Add preflight checking
   - Integrate with existing pipeline
   - Extend models with web source fields

3. **Week 3: Coverage + Acquisition Tools**
   - Implement coverage assessment logic
   - Add MCP tools: `ingest`, `sources`, `assess`, `preflight`, `acquire`, `request`
   - Implement offline sync manager

### Phase 2a: Workflow + Capture (Weeks 4-6)
4. **Week 4: Data Models**
   - Define Project, TemplateUsage SQLAlchemy models
   - Create repositories for project lifecycle
   - Implement state machine for project status

5. **Week 5: Workflow Searchers**
   - Implement RCCA searcher
   - Implement trade study searcher
   - Implement exploration searcher
   - Implement planning searcher

6. **Week 6: Workflow Tools**
   - Add MCP tools: `rcca`, `trade`, `explore`, `plan`
   - Integrate capture operations into planning tool
   - Add pattern library for anti-pattern matching

### Phase 2b: Feedback + Scoring (Weeks 7-8)
7. **Week 7: Feedback System**
   - Define Feedback, ChunkScore SQLAlchemy models
   - Implement three-tier feedback collector
   - Add `feedback` MCP tool

8. **Week 8: Scoring Integration**
   - Implement simple effectiveness scoring
   - Integrate score_boost into search ranking
   - Add score propagation to templates

### Phase 3: Advanced + Admin (Weeks 9-11)
9. **Week 9: Advanced Scoring**
   - Implement multi-factor scoring with confidence
   - Add temporal decay to scores
   - Implement score propagation algorithms

10. **Week 10: Relationship Graph**
    - Define Relationship SQLAlchemy model
    - Implement relationship storage
    - Add `relationships` MCP tool

11. **Week 11: Admin Tools**
    - Implement health reports
    - Add analytics queries
    - Add `admin` MCP tool
    - Implement source refresh management

---

## API Compatibility

### Breaking Changes: None
The v1.0 API remains fully functional:
- `knowledge_search` continues to work identically
- `knowledge_stats` continues to work identically
- CLI commands (`ingest`, `verify`) continue to work

### Additive Changes
All v2.0 features are additive:
- New MCP tools alongside existing ones
- Optional new fields in models (defaults preserve v1 behavior)
- New database tables with no impact on existing vector stores

### Migration Path
1. Deploy PostgreSQL alongside existing Qdrant
2. Run Alembic migrations to create new tables
3. Existing vector data remains unchanged
4. New features become available incrementally

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| PostgreSQL connection issues | High | Medium | Use connection pooling, health checks |
| Crawl4AI reliability | Medium | Medium | Implement retry logic, preflight checks |
| Score calculation accuracy | Medium | High | Start simple, validate with user feedback |
| Relationship graph complexity | High | Medium | Defer to Phase 3, iterate based on usage |
| Tool count overwhelming agents | Medium | Medium | Consolidate tools, provide usage guidance |
| Test coverage regression | Medium | Low | Maintain 80% coverage throughout |

---

## Dependencies to Add

```toml
# pyproject.toml additions for v2.0
[tool.poetry.dependencies]
# Database
sqlalchemy = "^2.0.25"
asyncpg = "^0.29.0"
alembic = "^1.13.1"
psycopg = {extras = ["binary"], version = "^3.1.17"}

# Web Ingestion
crawl4ai = "^0.2.77"

# Optional: Enhanced relationship processing
networkx = "^3.2.1"
```

---

## Conclusion

The v1.0 to v2.0 transition is well-positioned for success:

1. **100% code reuse** - All existing modules can be directly reused
2. **Clean extension points** - Dataclasses and abstract interfaces enable extension
3. **No breaking changes** - v1.0 API remains fully compatible
4. **Modular architecture** - New features can be added incrementally
5. **Clear phase boundaries** - Each phase delivers standalone value

The primary complexity lies in:
- PostgreSQL integration (new dependency)
- 13 new MCP tool handlers (high surface area)
- Scoring algorithm accuracy (requires iteration)

With 11 weeks of estimated effort and a clear phase order, v2.0 can be delivered incrementally while maintaining production stability.
