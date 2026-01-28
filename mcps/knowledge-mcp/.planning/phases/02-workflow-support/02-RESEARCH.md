# Phase 2: Workflow Support - Research

**Researched:** 2026-01-27
**Domain:** Specialized retrieval strategies for systems engineering workflows
**Confidence:** HIGH

## Summary

Phase 2 implements specialized retrieval for four SE workflows: RCCA (Root Cause Corrective Action), Trade Studies, Exploration, and Planning/Project Capture. The standard approach uses a **Strategy Pattern** with a shared search core and swappable strategy objects that modify query preprocessing, ranking adjustments, and output formatting. Modern RAG (2026) has evolved to include agentic patterns with sophisticated query strategies, reranking, and routing—all implemented in Python using frameworks like LangChain and LlamaIndex.

The four workflow tools require:
1. **knowledge_rcca**: Unified search (symptoms + causes), rich metadata extraction
2. **knowledge_trade**: Alternative-grouped results, synthesize from any content
3. **knowledge_explore**: Multi-facet search (definitions, examples, standards)
4. **knowledge_plan**: Project capture with query history, profile, decision trail

**Primary recommendation:** Implement Strategy Pattern with shared `SemanticSearcher` core. Create abstract `SearchStrategy` base class with three methods: `preprocess_query()`, `adjust_ranking()`, `format_output()`. Store project capture data in new PostgreSQL tables (`projects`, `query_history`, `decisions`, `decision_sources`). Use SQLAlchemy async patterns from Phase 1 for database operations.

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy | ^2.0.25 | Async ORM for project data | Industry standard, type-safe, mature async support |
| asyncpg | ^0.29.0 | PostgreSQL async driver | Highest performance, native asyncio, recommended by SQLAlchemy |
| dataclasses | stdlib | Strategy and result models | Zero dependencies, native Python 3.11+, type-safe |
| abc (Abstract Base Classes) | stdlib | Strategy interface definition | Standard OOP pattern enforcement |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | ^2.5 (optional) | Request/response validation | If MCP tool schemas need runtime validation |
| networkx | ^3.2.1 (deferred) | Decision graph analysis | Phase 4 only, not Phase 2 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Strategy Pattern | Plugin system (importlib) | Strategy is simpler, fewer moving parts, better for 4 tools |
| Dataclasses | Pydantic models | Dataclasses lighter, no runtime overhead, sufficient for internal use |
| PostgreSQL tables | JSON in metadata | Tables enforce schema, enable complex queries, better for relationships |

**Installation:**
```bash
# Phase 1 already installed SQLAlchemy + asyncpg
# No new dependencies for Phase 2 core functionality
```

## Architecture Patterns

### Recommended Project Structure

```
src/knowledge_mcp/
├── search/
│   ├── semantic_search.py       # Existing (Phase 1)
│   ├── coverage.py               # Existing (Phase 1)
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py               # SearchStrategy ABC
│   │   ├── rcca.py               # RCCAStrategy
│   │   ├── trade.py              # TradeStudyStrategy
│   │   ├── explore.py            # ExploreStrategy
│   │   └── plan.py               # PlanStrategy
│   └── workflow_search.py        # WorkflowSearcher orchestrator
├── db/
│   ├── models.py                 # Add: Project, QueryHistory, Decision
│   └── repositories.py           # Add: ProjectRepository, DecisionRepository
└── tools/
    └── workflows.py              # New MCP tool handlers
```

### Pattern 1: Strategy Pattern for Search Specialization

**What:** Define family of algorithms (search strategies) that are interchangeable at runtime. Each strategy encapsulates domain-specific query processing, ranking, and formatting.

**When to use:** When multiple algorithms solve the same problem differently (semantic search variants) and the choice depends on context (workflow type).

**Example:**
```python
# Source: Strategy Pattern + RAG Architecture (2026)
# https://refactoring.guru/design-patterns/strategy/python/example
# https://dev.to/suraj_khaitan_f893c243958/-rag-in-2026-a-practical-blueprint-for-retrieval-augmented-generation-16pp

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from knowledge_mcp.search.semantic_search import SemanticSearcher
from knowledge_mcp.search.models import SearchResult


@dataclass
class SearchQuery:
    """Internal representation of processed query."""

    original: str
    expanded_terms: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    facets: list[str] = field(default_factory=list)  # For multi-facet search


class SearchStrategy(ABC):
    """Abstract base class for workflow-specific search strategies.

    Strategies customize three phases:
    1. Query preprocessing (expansion, faceting)
    2. Ranking adjustments (boost domain-specific fields)
    3. Output formatting (structured metadata)
    """

    @abstractmethod
    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any]
    ) -> SearchQuery:
        """Transform user query into internal search representation.

        Args:
            query: Natural language query from user.
            params: Tool-specific parameters (filters, options).

        Returns:
            SearchQuery with expanded terms, filters, facets.
        """
        pass

    @abstractmethod
    def adjust_ranking(
        self,
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """Apply strategy-specific ranking adjustments.

        Args:
            results: Raw semantic search results.

        Returns:
            Reranked results with strategy-specific scoring.
        """
        pass

    @abstractmethod
    def format_output(
        self,
        results: list[SearchResult]
    ) -> dict[str, Any]:
        """Structure output according to strategy requirements.

        Args:
            results: Ranked search results.

        Returns:
            Formatted dict for MCP tool response.
        """
        pass


class WorkflowSearcher:
    """Orchestrates workflow-specific searches using strategy pattern."""

    def __init__(
        self,
        searcher: SemanticSearcher,
        strategy: SearchStrategy
    ):
        self.searcher = searcher
        self.strategy = strategy

    async def search(
        self,
        query: str,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute workflow-specific search.

        Template method: defines search algorithm structure,
        delegates customization to strategy.
        """
        params = params or {}

        # 1. Preprocess query (strategy-specific)
        search_query = await self.strategy.preprocess_query(query, params)

        # 2. Execute semantic search (shared core)
        results = await self.searcher.search(
            query=search_query.original,
            n_results=params.get("n_results", 10),
            filter_dict=search_query.filters,
        )

        # 3. Adjust ranking (strategy-specific)
        ranked_results = self.strategy.adjust_ranking(results)

        # 4. Format output (strategy-specific)
        return self.strategy.format_output(ranked_results)
```

### Pattern 2: RCCA Strategy - Unified Search with Metadata Extraction

**What:** Search symptoms and root causes simultaneously, extract structured failure analysis fields from content.

**When to use:** When analyzing failures, incidents, or problems in systems engineering context.

**Example:**
```python
# Source: RCCA methodology from aerospace/defense
# https://www.lockheedmartin.com/content/dam/lockheed-martin/uk/documents/suppliers/RCCA-Problem-Solving-Guidebook.pdf

import re
from dataclasses import dataclass


@dataclass
class RCCAMetadata:
    """Extracted structured fields from RCCA content."""

    symptoms: list[str]
    root_cause: str | None
    contributing_factors: list[str]
    resolution: str | None


class RCCAStrategy(SearchStrategy):
    """Strategy for Root Cause Corrective Action searches."""

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any]
    ) -> SearchQuery:
        """Expand query to cover both symptoms and causes."""
        expanded_terms = [
            query,
            f"{query} symptoms",
            f"{query} root cause",
            f"{query} failure analysis",
        ]

        # Filter for normative content (standards, best practices)
        filters = {"document_type": ["standard", "handbook"]}

        return SearchQuery(
            original=query,
            expanded_terms=expanded_terms,
            filters=filters,
        )

    def adjust_ranking(
        self,
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """Boost results with RCCA-specific terms."""
        keywords = ["root cause", "failure", "corrective action", "symptoms"]

        for result in results:
            boost = 1.0
            content_lower = result.content.lower()
            for keyword in keywords:
                if keyword in content_lower:
                    boost += 0.1

            # Adjust score (semantic * boost)
            result.score = min(1.0, result.score * boost)

        return sorted(results, key=lambda r: r.score, reverse=True)

    def format_output(
        self,
        results: list[SearchResult]
    ) -> dict[str, Any]:
        """Extract RCCA metadata and structure output."""
        formatted_results = []

        for result in results:
            metadata = self._extract_rcca_metadata(result.content)
            formatted_results.append({
                "content": result.content,
                "score": result.score,
                "source": {
                    "document_title": result.document_title,
                    "section_title": result.section_title,
                },
                "rcca_metadata": {
                    "symptoms": metadata.symptoms,
                    "root_cause": metadata.root_cause,
                    "contributing_factors": metadata.contributing_factors,
                    "resolution": metadata.resolution,
                }
            })

        return {
            "results": formatted_results,
            "result_type": "rcca_analysis",
            "total_results": len(formatted_results),
        }

    def _extract_rcca_metadata(self, content: str) -> RCCAMetadata:
        """Parse content for RCCA fields using heuristics."""
        # Simple extraction - can be enhanced with NLP
        symptoms = self._extract_list_items(content, ["symptom", "observed", "error"])
        contributing = self._extract_list_items(content, ["contributing", "factor"])

        root_cause = None
        if match := re.search(r"root cause:?\s*(.+?)(?:\n|$)", content, re.IGNORECASE):
            root_cause = match.group(1).strip()

        resolution = None
        if match := re.search(r"resolution:?\s*(.+?)(?:\n|$)", content, re.IGNORECASE):
            resolution = match.group(1).strip()

        return RCCAMetadata(
            symptoms=symptoms,
            root_cause=root_cause,
            contributing_factors=contributing,
            resolution=resolution,
        )

    def _extract_list_items(
        self,
        content: str,
        keywords: list[str]
    ) -> list[str]:
        """Extract bulleted/numbered items near keywords."""
        items = []
        for keyword in keywords:
            pattern = rf"{keyword}.*?[:\-]?\s*([^\n]+)"
            matches = re.finditer(pattern, content, re.IGNORECASE)
            items.extend(m.group(1).strip() for m in matches)
        return items[:5]  # Limit to top 5
```

### Pattern 3: Trade Study Strategy - Alternative-Grouped Output

**What:** Group results by alternative/option, synthesize criteria evidence from any relevant content.

**When to use:** When comparing technical alternatives, design options, or vendor solutions.

**Example:**
```python
# Source: Systems Engineering trade study methodology
# https://mechanicalc.com/reference/trade-study
# https://sebokwiki.org/wiki/Decision_Management

from collections import defaultdict
from typing import Any


class TradeStudyStrategy(SearchStrategy):
    """Strategy for trade study decision support."""

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any]
    ) -> SearchQuery:
        """Generate queries for alternatives and criteria."""
        alternatives = params.get("alternatives", [])
        criteria = params.get("criteria", [])

        # Search for each alternative + criteria combination
        # (orchestrator will merge results)
        expanded_terms = [
            f"{query} {alt} {criterion}"
            for alt in alternatives
            for criterion in criteria
        ]

        return SearchQuery(
            original=query,
            expanded_terms=expanded_terms,
        )

    def adjust_ranking(
        self,
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """Boost results with quantitative criteria."""
        criteria_keywords = [
            "cost", "performance", "weight", "reliability",
            "maintainability", "COTS", "schedule"
        ]

        for result in results:
            boost = 1.0
            content_lower = result.content.lower()

            # Higher boost for quantitative data
            if re.search(r"\d+\s*(kg|lbs|USD|ms|%)", content_lower):
                boost += 0.2

            for keyword in criteria_keywords:
                if keyword in content_lower:
                    boost += 0.05

            result.score = min(1.0, result.score * boost)

        return sorted(results, key=lambda r: r.score, reverse=True)

    def format_output(
        self,
        results: list[SearchResult]
    ) -> dict[str, Any]:
        """Group results by alternative, synthesize criteria."""
        # Group by alternative (simple keyword matching)
        alternatives = params.get("alternatives", [])
        grouped = defaultdict(list)

        for result in results:
            # Assign to alternatives based on content
            assigned = False
            for alt in alternatives:
                if alt.lower() in result.content.lower():
                    grouped[alt].append(result)
                    assigned = True
                    break

            if not assigned:
                grouped["__general__"].append(result)

        # Format as alternative-centric
        formatted = []
        for alt, alt_results in grouped.items():
            if alt == "__general__":
                continue

            criteria_evidence = self._extract_criteria(alt_results)
            formatted.append({
                "alternative": alt,
                "criteria": criteria_evidence,
                "result_count": len(alt_results),
            })

        return {
            "alternatives": formatted,
            "result_type": "trade_study",
            "total_alternatives": len(formatted),
        }

    def _extract_criteria(
        self,
        results: list[SearchResult]
    ) -> list[dict[str, Any]]:
        """Extract criteria evidence from results."""
        # Simple heuristic: look for criteria keywords + values
        criteria = []
        for result in results:
            # Extract cost mentions
            if cost_match := re.search(r"cost.*?(\d+)", result.content, re.IGNORECASE):
                criteria.append({
                    "name": "cost",
                    "evidence": cost_match.group(0),
                    "score": result.score,
                    "source": result.document_title,
                })

            # Extract performance mentions
            if perf_match := re.search(r"performance.*?(\d+)", result.content, re.IGNORECASE):
                criteria.append({
                    "name": "performance",
                    "evidence": perf_match.group(0),
                    "score": result.score,
                    "source": result.document_title,
                })

        return criteria
```

### Pattern 4: Project State Machine

**What:** Enforce valid lifecycle transitions for projects (planning → active → completed/abandoned).

**When to use:** When capturing project outcomes and preventing invalid state changes.

**Example:**
```python
# Source: SQLAlchemy async state management patterns
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from knowledge_mcp.db.models import Base


class ProjectStatus(str, Enum):
    """Project lifecycle states."""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# Valid state transitions
STATE_TRANSITIONS = {
    ProjectStatus.PLANNING: [ProjectStatus.ACTIVE, ProjectStatus.ABANDONED],
    ProjectStatus.ACTIVE: [ProjectStatus.COMPLETED, ProjectStatus.ABANDONED],
    ProjectStatus.COMPLETED: [],  # Terminal state
    ProjectStatus.ABANDONED: [],  # Terminal state
}


class Project(Base):
    """Project model with state machine enforcement."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, native_enum=False),
        default=ProjectStatus.PLANNING,
    )

    def can_transition_to(self, new_status: ProjectStatus) -> bool:
        """Check if transition is valid."""
        return new_status in STATE_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status: ProjectStatus) -> None:
        """Transition to new status if valid."""
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid transition: {self.status.value} -> {new_status.value}"
            )
        self.status = new_status
```

### Anti-Patterns to Avoid

- **Strategy God Class**: Don't put all strategy logic in base class. Keep strategies independent.
- **Over-Engineering Extensibility**: Phase 2 has 4 strategies. Don't build plugin system for 4 items—YAGNI.
- **Lazy Loading in Async**: Don't rely on lazy-loaded relationships in async SQLAlchemy. Use eager loading (`selectinload`).
- **Shared Sessions Across Tasks**: Don't pass AsyncSession between concurrent operations. Create session per operation.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Query expansion | Manual synonym lists | LLM-based expansion or knowledge graph | Edge cases (acronyms, domain terms), maintenance burden |
| Metadata extraction | Regex-only parsers | Hybrid (regex + heuristics), defer complex NLP to Phase 3 | Precision/recall tradeoff, false positives |
| Alternative clustering | Custom text similarity | Re-use existing embedder + cosine similarity | Already have embeddings, avoid duplicate work |
| State machine enforcement | Manual if/else chains | Enum + transition dict pattern (shown above) | Declarative, testable, auditable |

**Key insight:** Phase 2 is about **structure** and **orchestration**, not novel algorithms. Leverage existing semantic search, embedder, and vector store. Focus strategy effort on domain-specific ranking and formatting.

## Common Pitfalls

### Pitfall 1: Premature Multi-Query Execution

**What goes wrong:** Implementing `TradeStudyStrategy.preprocess_query()` to generate multiple queries (one per alternative/criterion pair) and expecting orchestrator to execute all.

**Why it happens:** Trade study methodology talks about "evaluating alternatives against criteria" which sounds like NxM queries.

**How to avoid:** Start with single unified query. Use post-processing to group/cluster results by alternative. Only add multi-query if single query has poor recall.

**Warning signs:** `WorkflowSearcher.search()` getting complex, multiple calls to `searcher.search()`, performance degradation.

### Pitfall 2: Forcing Strategy When Simple Filter Suffices

**What goes wrong:** Creating new strategy class for minor search variation (e.g., "search only normative content").

**Why it happens:** Over-application of strategy pattern when parameterization works better.

**How to avoid:** Strategies for **different algorithms**, not **different parameters**. If only changing `filter_dict`, add parameter to existing strategy or base search.

**Warning signs:** Strategies with identical `preprocess_query()` and `adjust_ranking()`, only `format_output()` differs.

### Pitfall 3: Session-Per-Tool Instead of Session-Per-Operation

**What goes wrong:** Creating AsyncSession in MCP tool handler, passing to multiple repository calls, getting connection leaks or race conditions.

**Why it happens:** Porting synchronous "session-per-request" pattern to async without understanding concurrency.

**How to avoid:** Create session in each repository method or use Unit of Work pattern. Follow SQLAlchemy async research (Phase 1).

**Warning signs:** `pool.TimeoutError`, `MissingGreenlet` exceptions, intermittent test failures.

### Pitfall 4: Returning ORM Objects from Tools

**What goes wrong:** MCP tool handler returns `Project` object directly instead of dict, causes serialization errors or detached object issues.

**Why it happens:** Convenience—ORM objects have all fields. Forgetting JSON serialization and session lifecycle.

**How to avoid:** Always convert ORM objects to dicts before returning from tools. Use Pydantic models or manual dict construction.

**Warning signs:** `Object is not JSON serializable`, `Instance is not bound to a Session`, data staleness.

## Code Examples

Verified patterns from official sources:

### Multi-Facet Search (Explore Strategy)

```python
# Source: Faceted search + query expansion
# https://arxiv.org/abs/1310.5698 (Massive Query Expansion)
# https://www.emergentmind.com/topics/faceted-search-system

from dataclasses import dataclass, field


@dataclass
class Facet:
    """A facet of exploratory search."""
    name: str
    query: str
    results: list[SearchResult] = field(default_factory=list)


class ExploreStrategy(SearchStrategy):
    """Strategy for exploratory multi-facet search."""

    FACETS = [
        ("definitions", "definition terminology"),
        ("examples", "example case study"),
        ("standards", "standard requirement"),
        ("best_practices", "best practice guidance"),
    ]

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any]
    ) -> SearchQuery:
        """Generate faceted queries."""
        facets = [
            f"{query} {facet_query}"
            for _, facet_query in self.FACETS
        ]

        return SearchQuery(
            original=query,
            expanded_terms=facets,
            facets=[name for name, _ in self.FACETS],
        )

    def adjust_ranking(
        self,
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """Maintain facet diversity in ranking."""
        # Simple: return as-is, formatting handles facet assignment
        return results

    def format_output(
        self,
        results: list[SearchResult]
    ) -> dict[str, Any]:
        """Organize results by facet."""
        facets_output = []

        for facet_name, facet_query in self.FACETS:
            # Assign results to facets by keyword matching
            facet_results = [
                r for r in results
                if any(kw in r.content.lower() for kw in facet_query.split())
            ][:3]  # Top 3 per facet

            facets_output.append({
                "facet": facet_name,
                "results": [
                    {
                        "content": r.content[:200] + "...",
                        "score": r.score,
                        "source": r.document_title,
                    }
                    for r in facet_results
                ]
            })

        return {
            "facets": facets_output,
            "result_type": "exploratory",
            "total_facets": len(facets_output),
        }
```

### Project Capture with Decision Trail

```python
# Source: Knowledge graph for decision capture
# https://www.graphlit.com/blog/context-layer-ai-agents-need
# https://foundationcapital.com/context-graphs-ais-trillion-dollar-opportunity/

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from knowledge_mcp.db.models import Base


class QueryHistory(Base):
    """Tracks queries made during project."""

    __tablename__ = "query_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    query: Mapped[str] = mapped_column(Text)
    result_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="query_history")


class Decision(Base):
    """Captures decisions with rationale and sources."""

    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))

    decision: Mapped[str] = mapped_column(Text)  # What was decided
    alternatives: Mapped[list[str]] = mapped_column(postgresql.ARRAY(String))  # What else was considered
    rationale: Mapped[str] = mapped_column(Text)  # Why this choice

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="decisions")
    sources: Mapped[list["DecisionSource"]] = relationship(back_populates="decision")


class DecisionSource(Base):
    """Links decisions to supporting evidence (chunks)."""

    __tablename__ = "decision_sources"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(ForeignKey("decisions.id"))
    chunk_id: Mapped[str] = mapped_column(String(255))  # References Qdrant chunk UUID
    relevance: Mapped[float]  # How relevant to decision

    decision: Mapped["Decision"] = relationship(back_populates="sources")


# Repository method for project capture
class ProjectRepository:
    """Async repository for project operations."""

    async def capture_query(
        self,
        project_id: UUID,
        query: str,
        result_count: int
    ) -> QueryHistory:
        """Record query in project history."""
        query_record = QueryHistory(
            project_id=project_id,
            query=query,
            result_count=result_count,
        )
        self.session.add(query_record)
        await self.session.flush()
        return query_record

    async def capture_decision(
        self,
        project_id: UUID,
        decision: str,
        alternatives: list[str],
        rationale: str,
        supporting_chunks: list[tuple[str, float]],  # (chunk_id, relevance)
    ) -> Decision:
        """Record decision with source links."""
        decision_record = Decision(
            project_id=project_id,
            decision=decision,
            alternatives=alternatives,
            rationale=rationale,
        )
        self.session.add(decision_record)
        await self.session.flush()

        # Link supporting sources
        for chunk_id, relevance in supporting_chunks:
            source = DecisionSource(
                decision_id=decision_record.id,
                chunk_id=chunk_id,
                relevance=relevance,
            )
            self.session.add(source)

        await self.session.flush()
        return decision_record
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fixed query expansion | LLM-based expansion | 2024 (GPT-3.5) | More contextual, higher recall |
| Single-pass retrieval | Agentic RAG with planning | 2025-2026 | Adaptive, multi-query strategies |
| Manual metadata tagging | In-context extraction | 2024 (GPT-4) | Reduces ingestion burden |
| Keyword-based faceting | Semantic clustering | 2024 | Better facet coherence |

**Deprecated/outdated:**
- Boolean query syntax - Replaced by: Natural language queries with semantic search
- Manual trade study matrices - Replaced by: LLM-synthesized comparisons from unstructured content
- Fixed workflow taxonomies - Replaced by: Configurable strategy pattern

## Open Questions

Things that couldn't be fully resolved:

1. **RCCA Metadata Extraction Precision**
   - What we know: Simple regex + heuristics work for well-structured content
   - What's unclear: Accuracy on unstructured failure reports, false positive rate
   - Recommendation: Start simple (Phase 2), add NER/LLM extraction in Phase 3 if needed. Monitor precision via feedback.

2. **Trade Study Alternative Discovery**
   - What we know: Can group results by mentioned alternatives
   - What's unclear: How to discover alternatives not explicitly provided by user
   - Recommendation: Require user to provide alternatives in Phase 2. Defer auto-discovery to Phase 3 (entity extraction).

3. **Multi-Query Performance Impact**
   - What we know: Faceted search may need multiple sequential queries
   - What's unclear: Latency impact, whether to parallelize or aggregate
   - Recommendation: Start with single query + post-processing. Add multi-query only if recall insufficient. Use asyncio.gather() for parallel queries if needed.

4. **Decision Trail Granularity**
   - What we know: Need to link decisions to source chunks
   - What's unclear: How granular—every search result, or only explicitly saved?
   - Recommendation: Capture explicit saves only (via tool parameter). Add implicit tracking in Phase 3 if usage data shows value.

## Sources

### Primary (HIGH confidence)
- [SQLAlchemy 2.0 Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - ORM patterns
- [Strategy Pattern in Python](https://refactoring.guru/design-patterns/strategy/python/example) - Design pattern reference
- [Lockheed Martin RCCA Guidebook](https://www.lockheedmartin.com/content/dam/lockheed-martin/uk/documents/suppliers/RCCA-Problem-Solving-Guidebook.pdf) - RCCA methodology
- [SEBoK Decision Management](https://sebokwiki.org/wiki/Decision_Management) - Trade study methodology
- [RAG in 2026: Practical Blueprint](https://dev.to/suraj_khaitan_f893c243958/-rag-in-2026-a-practical-blueprint-for-retrieval-augmented-generation-16pp) - Modern RAG patterns

### Secondary (MEDIUM confidence)
- [Context Graphs for AI Agents](https://www.graphlit.com/blog/context-layer-ai-agents-need) - Decision trail concepts
- [AI's Trillion-Dollar Opportunity: Context Graphs](https://foundationcapital.com/context-graphs-ais-trillion-dollar-opportunity/) - Knowledge graph rationale
- [Massive Query Expansion Using Knowledge Bases](https://arxiv.org/abs/1310.5698) - Query expansion theory
- [Enterprise AI Knowledge Management 2026](https://www.gosearch.ai/faqs/enterprise-ai-knowledge-management-guide-2026/) - Industry trends
- [Trade Study Examples - MechaniCalc](https://mechanicalc.com/reference/trade-study) - Practical examples

### Tertiary (LOW confidence)
- Various blog posts on RAG agentic patterns - Marked for validation in implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - SQLAlchemy, dataclasses, strategy pattern are mature and well-documented
- Architecture: HIGH - Strategy pattern verified for similar use cases, PostgreSQL schema follows Phase 1 patterns
- Pitfalls: MEDIUM - Based on SQLAlchemy async research + common OOP mistakes, not workflow-specific

**Research date:** 2026-01-27
**Valid until:** 60 days (2026-03-28) - Core patterns stable, but RAG techniques evolve rapidly
