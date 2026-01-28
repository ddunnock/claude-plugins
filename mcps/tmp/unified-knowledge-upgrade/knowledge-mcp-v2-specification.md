# Knowledge-MCP v2 Complete Specification

**Version:** 2.0.0-draft-r2  
**Date:** 2026-01-27  
**Status:** Draft for Review  
**Authors:** D. Dunnock  

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-20 | D. Dunnock | Initial knowledge-mcp |
| 2.0.0-draft | 2026-01-27 | D. Dunnock | Unified ingestion, acquisition, workflow tools |
| 2.0.0-draft-r2 | 2026-01-27 | D. Dunnock | Added planning support, capture, feedback, scoring |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope and Objectives](#2-scope-and-objectives)
3. [Architecture Overview](#3-architecture-overview)
4. [Data Models](#4-data-models)
5. [MCP Tools Specification](#5-mcp-tools-specification)
6. [Scoring System](#6-scoring-system)
7. [Implementation Phases](#7-implementation-phases)
8. [Storage Design](#8-storage-design)
9. [Configuration](#9-configuration)
10. [Testing Strategy](#10-testing-strategy)
11. [Appendices](#11-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

Knowledge-MCP v2 transforms the existing semantic search MCP server into a **learning knowledge management system** that:

1. **Unifies Ingestion** - Static documents (PDF, DOCX) and dynamic web content through a single pipeline
2. **Enables Acquisition** - Detect gaps, acquire missing knowledge, verify coverage
3. **Supports Workflows** - Specialized retrieval for RCCA, Trade Studies, Exploration, and Planning
4. **Captures Knowledge** - Store project structures, outcomes, and lessons learned
5. **Learns from Feedback** - Multi-factor scoring improves recommendations over time
6. **Builds Institutional Memory** - Knowledge compounds as more projects use and refine it

### 1.2 Key Decisions from SEAMS Analysis

| Decision | Rationale | Impact |
|----------|-----------|--------|
| **15 consolidated tools** | Balance capability vs. agent complexity | Merged capture into planning_support, scores into admin |
| **3-phase + sub-phases** | Manage complexity, deliver incrementally | Phase 2 split into 2a (capture) and 2b (feedback) |
| **Simple → Full scoring** | Reduce initial complexity | Start with single score, expand to multi-factor |
| **Three-tier feedback** | Maximize collection, minimize friction | Implicit + Quick + Detailed options |
| **Project state machine** | Prevent invalid states | Explicit lifecycle transitions |
| **Visibility controls** | Balance personal and org knowledge | Default personal, explicit sharing |

### 1.3 Success Criteria

| Criterion | Metric | Target | Phase |
|-----------|--------|--------|-------|
| Web ingestion reliability | Pages successfully indexed | 100% | 1 |
| Coverage assessment accuracy | Correlation with expert rating | >0.75 | 1 |
| Offline mode functional | Operations work without network | 100% | 1 |
| Similar failure retrieval | Recall@5 | >0.70 | 2a |
| Project capture adoption | Projects captured per month | >5 | 2a |
| Feedback collection rate | Feedback per completed project | >60% | 2b |
| Score prediction accuracy | Correlation: score vs outcome | >0.6 | 3 |
| Recommendation improvement | User satisfaction trend | Increasing | 3 |

---

## 2. Scope and Objectives

### 2.1 In Scope

| Category | Items | Phase |
|----------|-------|-------|
| **Ingestion** | PDF (Docling), DOCX (Mammoth), Web (Crawl4AI), Markdown | 1 |
| **Storage** | Qdrant Cloud (primary), ChromaDB (fallback/offline) | 1 |
| **Acquisition** | Coverage assessment, web acquisition, document requests | 1 |
| **RCCA Workflow** | Similar failures, causal chains, corrective actions, compliance | 2a |
| **Trade Study Workflow** | Criteria, alternatives, precedents, risk assessment | 2a |
| **Exploration Workflow** | Anti-patterns, gap analysis, counterarguments, synthesis | 2a |
| **Planning Workflow** | Templates, precedents, risks, dependencies, constraints, checkpoints | 2a |
| **Knowledge Capture** | Project structures, outcomes, lessons learned, templates | 2a |
| **Feedback** | Ratings, aspect feedback, outcome reports, suggestions | 2b |
| **Scoring** | Simple scores (2b), multi-factor with propagation (3) | 2b/3 |
| **Relationships** | Causal, contradiction, support, reference | 3 |
| **Administration** | Health reports, analytics, score management | 3 |

### 2.2 Out of Scope (v2)

| Item | Rationale | Future Version |
|------|-----------|----------------|
| Multi-user access control | Complexity; single-user MVP | v3 |
| Real-time collaboration | Not needed for individual workflows | v3 |
| Automated standard updates | Legal/licensing complexity | v3 |
| Non-English content | Embedding model limitations | v2.1 |
| External PM tool sync | Integration complexity | v2.1 |
| Score dispute resolution UI | Requires frontend | v2.1 |

### 2.3 Constraints

| Constraint | Source | Impact |
|------------|--------|--------|
| Python ≥3.11,<3.14 | Project standard | Use modern features |
| Pyright strict mode | Project standard | Full type hints required |
| 80%+ test coverage | Project standard | Comprehensive testing |
| MCP Protocol v1.x | Compatibility | Standard tool format |
| OpenAI API costs | Budget | Aggressive caching |
| Copyright compliance | Legal | Store only user's copies |
| Feedback friction | UX | Three-tier collection strategy |
| Cold start | New artifacts | Seed data + confidence display |

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE-MCP V2 LEARNING ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │           MCP INTERFACE             │
                    │              15 Tools               │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │     Tool Categories           │  │
                    │  │                               │  │
                    │  │  Core (4)      Acquire (4)    │  │
                    │  │  Workflow (4)  Feedback (1)   │  │
                    │  │  Graph (1)     Admin (1)      │  │
                    │  └───────────────┬───────────────┘  │
                    └──────────────────┼──────────────────┘
                                       │
        ┌──────────────────────────────┼─────────────────────────────┐
        │                              │                             │
        ▼                              ▼                             ▼
┌───────────────┐             ┌─────────────────┐           ┌─────────────────┐
│   INGESTION   │             │     SEARCH      │           │    LEARNING     │
│    LAYER      │             │     LAYER       │           │     LAYER       │
│               │             │                 │           │                 │
│ ┌───────────┐ │             │ ┌─────────────┐ │           │ ┌─────────────┐ │
│ │Ingestors  │ │             │ │  Semantic   │ │           │ │  Project    │ │
│ │PDF/DOCX/  │ │             │ │  Searcher   │ │           │ │  Capture    │ │
│ │Web/MD     │ │             │ └─────────────┘ │           │ └─────────────┘ │
│ └───────────┘ │             │ ┌─────────────┐ │           │ ┌─────────────┐ │
│ ┌───────────┐ │             │ │  Workflow   │ │           │ │  Feedback   │ │
│ │Relevance  │ │             │ │  Searcher   │ │           │ │  Collector  │ │
│ │Assessor   │ │             │ └─────────────┘ │           │ └─────────────┘ │
│ └───────────┘ │             │ ┌─────────────┐ │           │ ┌─────────────┐ │
│ ┌───────────┐ │             │ │  Planning   │ │           │ │  Score      │ │
│ │Chunker    │ │             │ │  Searcher   │ │           │ │  Calculator │ │
│ └───────────┘ │             │ └─────────────┘ │           │ └─────────────┘ │
└───────┬───────┘             └────────┬────────┘           └────────┬────────┘
        │                              │                             │
        │                     ┌────────┴────────┐                    │
        │                     │                 │                    │
        │                     ▼                 ▼                    │
        │              ┌─────────────┐   ┌─────────────┐             │
        │              │  COVERAGE   │   │   PATTERN   │             │
        │              │  ASSESSOR   │   │   MATCHER   │             │
        │              └─────────────┘   └─────────────┘             │
        │                                                            │
        └──────────────────────────────┬─────────────────────────────┘
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────────┐
        │                        STORAGE LAYER                            │
        │                                                                 │
        │  ┌─────────────────────────────────────────────────────────┐    │
        │  │         Vector Store (Qdrant + ChromaDB Offline)        │    │
        │  └─────────────────────────────────────────────────────────┘    │
        │                                                                 │
        │  ┌─────────────────────────────────────────────────────────┐    │
        │  │                    8 Collections                        │    │
        │  │                                                         │    │
        │  │  chunks ──── sources ──── relationships ──── patterns   │    │
        │  │  decisions ── projects ── feedback ──────── scores      │    │
        │  │                                                         │    │
        │  └─────────────────────────────────────────────────────────┘    │
        │                                                                 │
        │  ┌─────────────────────────────────────────────────────────┐    │
        │  │              Offline Manager (Sync)                     │    │
        │  └─────────────────────────────────────────────────────────┘    │
        │                                                                 │
        └─────────────────────────────────────────────────────────────────┘
```

### 3.2 Learning Loop Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE LEARNING LOOP                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐                                      
    │   USER      │                                      
    │   STARTS    │                                      
    │   WORKFLOW  │                                      
    └──────┬──────┘                                      
           │                                             
           ▼                                             
    ┌─────────────────────────────────────────────────────────────────┐
    │                   RETRIEVAL (Score-Boosted)                     │
    │                                                                 │
    │  planning_support:find_templates ──▶ Templates (ranked by score)│
    │  planning_support:find_precedents ──▶ Projects (ranked by score)│
    │  planning_support:identify_risks ──▶ Patterns (ranked by score) │
    │                                                                 │
    └──────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                         CAPTURE                                 │
    │                                                                 │
    │   planning_support:capture_project ──▶ ProjectRecord created    │
    │                                        (status: PLANNING)       │
    │                                        (source_template_id set) │
    │                                                                 │
    └──────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
    ═══════════════════════════════════════════════════════════════════
                          EXECUTION PHASE
    ═══════════════════════════════════════════════════════════════════
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                      OUTCOME CAPTURE                            │
    │                                                                 │
    │   planning_support:capture_outcome ──▶ ProjectRecord updated    │
    │                                        (status: COMPLETED)      │
    │                                        (actuals recorded)       │
    │                                        (lessons captured)       │
    │                                                                 │
    └──────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    FEEDBACK COLLECTION                          │
    │                                                                 │
    │   Tier 1 (Implicit):    Usage tracked automatically             │
    │   Tier 2 (Quick):       "Was this helpful?" prompt              │
    │   Tier 3 (Detailed):    knowledge_feedback tool                 │
    │                                                                 │
    └──────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                      SCORE UPDATE                               │
    │                                                                 │
    │   1. Update project's score based on outcome + feedback         │
    │   2. Propagate to source template (weighted by modifications)   │
    │   3. Recalculate composite scores                               │
    │   4. Apply staleness decay to old artifacts                     │
    │                                                                 │
    └──────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                   IMPROVED RANKINGS                             │
    │                                                                 │
    │   Next retrieval returns better-ranked results                  │
    │   Templates that worked well rise to top                        │
    │   Templates that failed sink in rankings                        │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

### 3.3 Component Responsibilities

| Component | Responsibility | Phase |
|-----------|---------------|-------|
| **PDFIngestor** | Parse PDFs via Docling | Existing |
| **DOCXIngestor** | Parse DOCX via Mammoth | Existing |
| **WebIngestor** | Crawl web via Crawl4AI | 1 |
| **HierarchicalChunker** | Structure-aware chunking | Existing |
| **SemanticSearcher** | Vector similarity search | Existing |
| **WorkflowSearcher** | RCCA/Trade/Explore specialized | 2a |
| **PlanningSearcher** | Planning-specific retrieval | 2a |
| **PatternMatcher** | Anti-pattern detection | 2a |
| **CoverageAssessor** | Knowledge gap detection | 1 |
| **RelevanceAssessor** | Content relevance scoring | 1 |
| **AcquisitionManager** | Orchestrate knowledge acquisition | 1 |
| **ProjectCapture** | Store project structures | 2a |
| **FeedbackCollector** | Gather and store feedback | 2b |
| **ScoreCalculator** | Compute and update scores | 2b/3 |
| **ScorePropagator** | Propagate scores to templates | 3 |
| **RelationshipStore** | Graph edge storage | 3 |
| **OfflineManager** | ChromaDB sync | 1 |

### 3.4 Project Lifecycle State Machine

```
                              ┌─────────────────────────────────────┐
                              │                                     │
                              ▼                                     │
                        ┌──────────┐                                │
                        │ PLANNING │                                │
                        │          │                                │
                        │ • Tasks defined                           │
                        │ • Estimates set                           │
                        │ • Risks identified                        │
                        └────┬─────┘                                │
                             │                                      │
                    activate │                                      │
                             ▼                                      │
                        ┌──────────┐      abandon                   │
                        │  ACTIVE  │─────────────────┐              │
                        │          │                 │              │
                        │ • Execution in progress    │              │
                        │ • Progress tracked         │              │
                        │ • Blockers noted           │              │
                        └────┬─────┘                 │              │
                             │                       │              │
                   complete  │                       │              │
                             ▼                       ▼              │
                        ┌──────────┐           ┌──────────┐         │
                        │COMPLETED │           │ABANDONED │         │
                        │          │           │          │         │
                        │ • Actuals recorded   │ • Reason captured  │
                        │ • Outcomes captured  │ • Partial data     │
                        │ • Feedback requested │   preserved        │
                        └────┬─────┘           └──────────┘         │
                             │                                      │
                    reopen   │                                      │
                             └──────────────────────────────────────┘

Valid Transitions:
  PLANNING → ACTIVE       project.activate()
  ACTIVE → COMPLETED      project.complete(outcomes)
  ACTIVE → ABANDONED      project.abandon(reason)
  COMPLETED → ACTIVE      project.reopen()   // For continuation/phase 2
```
# Knowledge-MCP v2 Complete Specification (Part 2)

## 4. Data Models

### 4.1 Core Models

#### 4.1.1 KnowledgeChunk (Extended)

```python
# src/knowledge_mcp/models/chunk.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class KnowledgeChunk:
    """
    A chunk of knowledge from a document or web source.
    
    Extended in v2 to support:
    - Web sources with URL and freshness tracking
    - Authority scoring for ranking
    - Reference tracking for relationship building
    """
    
    # === IDENTITY ===
    id: str                              # UUID
    document_id: str                     # Source document/page identifier
    document_title: str                  # Human-readable title
    document_type: str                   # "standard" | "handbook" | "guide" | "web" | "report"
    
    # === CONTENT ===
    content: str                         # Text content
    content_hash: str                    # SHA-256 for deduplication
    token_count: int                     # Token count for context management
    
    # === HIERARCHY ===
    section_hierarchy: list[str]         # Path through document structure ["6", "6.4", "6.4.7"]
    section_title: str                   # Title of containing section
    parent_chunk_id: str | None = None   # Link to parent chunk
    
    # === CLASSIFICATION ===
    chunk_type: str = "content"          # "definition" | "requirement" | "guidance" | "content"
    normative: bool | None = None        # True=normative, False=informative, None=unknown
    
    # === LOCATION ===
    page_numbers: list[int] = field(default_factory=list)
    clause_number: str | None = None     # Clause identifier (e.g., "6.4.7.2")
    char_start: int | None = None        # Character offset for precise citation
    char_end: int | None = None
    
    # === SOURCE (v2) ===
    source_type: str = "document"        # "document" | "web"
    source_url: str | None = None        # Original URL for web content
    source_domain: str | None = None     # Domain for authority scoring
    crawled_at: str | None = None        # When web content was acquired
    
    # === QUALITY (v2) ===
    authority_score: float = 0.5         # 0-1, based on source authority
    relevance_score: float | None = None # 0-1, from assessment (if assessed)
    
    # === EMBEDDINGS ===
    embedding: list[float] | None = None
    embedding_model: str = "text-embedding-3-small"
    
    # === REFERENCES (v2) ===
    references: list[str] = field(default_factory=list)      # Extracted cross-references
    referenced_by: list[str] = field(default_factory=list)   # Chunks that reference this
    
    # === TIMESTAMPS ===
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            k: v for k, v in self.__dict__.items() 
            if v is not None and k != "embedding"
        }
```

#### 4.1.2 DocumentMetadata (Extended)

```python
# src/knowledge_mcp/models/document.py

@dataclass
class DocumentMetadata:
    """
    Metadata for a source document or web page.
    
    Extended in v2 to track:
    - Web source provenance
    - Authority classification
    - Freshness for staleness detection
    """
    
    # === IDENTITY ===
    document_id: str                     # Unique identifier
    title: str                           # Human-readable title
    document_type: str                   # Classification
    source_path: str                     # File path or URL
    
    # === VERSIONING ===
    version: str | None = None           # Document version
    publication_date: str | None = None  # Publication date (ISO format)
    standard_id: str | None = None       # Standards body identifier
    
    # === SOURCE (v2) ===
    source_type: str = "document"        # "document" | "web"
    source_url: str | None = None        # Canonical URL
    source_domain: str | None = None     # Domain for filtering
    
    # === AUTHORITY (v2) ===
    authority_level: str = "unverified"  # See AUTHORITY_LEVELS constant
    authority_score: float = 0.5         # Numeric score 0-1
    
    # === FRESHNESS (v2) ===
    crawled_at: str | None = None        # When acquired (web)
    last_verified_at: str | None = None  # When last checked for updates
    content_hash: str | None = None      # For change detection
    
    # === PROCESSING ===
    chunk_count: int = 0                 # Number of chunks generated
    processing_status: str = "pending"   # "pending" | "processing" | "complete" | "failed"
    processing_error: str | None = None
    
    # === TIMESTAMPS ===
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### 4.2 Relationship Models

#### 4.2.1 ChunkRelationship

```python
# src/knowledge_mcp/models/relationship.py

from enum import Enum


class RelationshipType(str, Enum):
    """Types of relationships between knowledge chunks."""
    
    # Reference relationships
    REFERENCES = "references"            # A cites B
    SUPERSEDES = "supersedes"            # A replaces B (newer version)
    IMPLEMENTS = "implements"            # A implements B (requirement → design)
    
    # Logical relationships
    SUPPORTS = "supports"                # A provides evidence for B
    CONTRADICTS = "contradicts"          # A conflicts with B
    QUALIFIES = "qualifies"              # A adds conditions/exceptions to B
    
    # Causal relationships (for RCCA)
    CAUSES = "causes"                    # A leads to B (root cause → effect)
    PREVENTS = "prevents"                # A mitigates B (control → failure)
    INDICATES = "indicates"              # A is symptom of B
    
    # Comparative relationships (for Trade Studies)
    ALTERNATIVE_TO = "alternative_to"    # A is alternative to B
    PREFERRED_OVER = "preferred_over"    # A is recommended over B


@dataclass
class ChunkRelationship:
    """
    Relationship between two knowledge chunks.
    
    Enables graph traversal for causal analysis and contradiction detection.
    """
    
    id: str
    source_chunk_id: str
    target_chunk_id: str
    relationship_type: RelationshipType
    
    # Metadata
    confidence: float = 1.0              # 0-1, for inferred relationships
    bidirectional: bool = False          # True if relationship goes both ways
    context: str = ""                    # Why this relationship exists
    
    # Provenance
    created_by: str = "manual"           # "manual" | "inferred" | "extracted"
    evidence_chunk_ids: list[str] = field(default_factory=list)
    
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### 4.3 Pattern Models

#### 4.3.1 Pattern

```python
# src/knowledge_mcp/models/pattern.py

class PatternType(str, Enum):
    """Classification of patterns."""
    
    ANTIPATTERN = "antipattern"          # Known bad practice
    BEST_PRACTICE = "best_practice"      # Recommended approach
    FAILURE_MODE = "failure_mode"        # Known failure pattern
    DESIGN_PATTERN = "design_pattern"    # Reusable solution


class PatternDomain(str, Enum):
    """Domain classification for patterns."""
    
    ARCHITECTURE = "architecture"
    REQUIREMENTS = "requirements"
    VERIFICATION = "verification"
    PROCESS = "process"
    SAFETY = "safety"
    RELIABILITY = "reliability"
    INTEGRATION = "integration"
    PLANNING = "planning"


@dataclass
class Pattern:
    """
    A reusable pattern for matching against content.
    
    Patterns are indexed and matched against proposals,
    designs, problem descriptions, or project plans.
    """
    
    id: str
    name: str                            # e.g., "Incomplete Requirements Traceability"
    pattern_type: PatternType
    domain: PatternDomain
    
    # Description
    description: str                     # What this pattern is
    indicators: list[str]                # Signs that pattern is present
    consequences: list[str]              # What happens if pattern occurs/is ignored
    
    # For antipatterns/failure modes
    root_causes: list[str] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)
    
    # For best practices
    benefits: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    
    # Matching
    keywords: list[str] = field(default_factory=list)
    embedding: list[float] | None = None
    
    # Evidence
    example_chunk_ids: list[str] = field(default_factory=list)
    
    # Source
    source_standard: str | None = None   # e.g., "NASA-HDBK-8739.18"
    source_clause: str | None = None
    
    # Severity
    severity: str = "medium"             # "low" | "medium" | "high" | "critical"
    
    # Scoring (v2 learning)
    score: float = 0.5                   # Effectiveness score
    score_confidence: float = 0.0        # Confidence in score
    
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### 4.4 Project Models

#### 4.4.1 TaskRecord

```python
# src/knowledge_mcp/models/project.py

@dataclass
class TaskRecord:
    """A task within a captured project."""
    
    id: str
    name: str
    description: str = ""
    
    # Structure
    parent_task_id: str | None = None
    sequence_order: int = 0
    phase: str | None = None
    
    # Estimates vs Actuals
    estimated_hours: float | None = None
    actual_hours: float | None = None
    estimated_complexity: str | None = None   # "low" | "medium" | "high"
    actual_complexity: str | None = None
    
    # Outcome
    status: str = "planned"                   # "planned" | "in_progress" | "completed" | "skipped" | "blocked"
    completion_notes: str | None = None
    blockers_encountered: list[str] = field(default_factory=list)
    
    # Dependencies
    depends_on: list[str] = field(default_factory=list)   # Task IDs
    dependency_type: str | None = None        # "finish_to_start" | "start_to_start"
```

#### 4.4.2 ProjectRecord

```python
# src/knowledge_mcp/models/project.py

class ProjectStatus(str, Enum):
    """Project lifecycle states."""
    
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ProjectVisibility(str, Enum):
    """Project visibility levels."""
    
    PERSONAL = "personal"        # Only creator can see
    TEAM = "team"                # Team members can see
    ORGANIZATION = "organization" # Everyone can see


@dataclass
class ProjectRecord:
    """
    A captured project structure with outcomes.
    
    This is what gets ingested when a project is planned and executed.
    Unlike templates (abstract patterns), this is a concrete instance.
    """
    
    id: str
    name: str
    description: str
    
    # Classification
    project_type: str                         # "mcp_server" | "trade_study" | "rcca" | "specification"
    domain: str                               # "software" | "systems" | "hardware"
    tags: list[str] = field(default_factory=list)
    
    # Visibility (SEAMS finding S2)
    visibility: ProjectVisibility = ProjectVisibility.PERSONAL
    owner: str | None = None
    
    # Context (for similarity matching)
    context_factors: dict[str, Any] = field(default_factory=dict)
    # e.g., {"team_size": 2, "new_technology": True, "integration_complexity": "high"}
    
    # Structure
    tasks: list[TaskRecord] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    checkpoints: list[str] = field(default_factory=list)
    
    # Planning artifacts
    identified_risks: list[dict] = field(default_factory=list)
    identified_dependencies: list[dict] = field(default_factory=list)
    constraints_applied: list[dict] = field(default_factory=list)
    
    # Estimates
    estimated_duration_days: float | None = None
    estimated_effort_hours: float | None = None
    
    # Actuals (filled in as project progresses)
    actual_duration_days: float | None = None
    actual_effort_hours: float | None = None
    start_date: str | None = None
    end_date: str | None = None
    
    # Lifecycle (SEAMS decision A4)
    status: ProjectStatus = ProjectStatus.PLANNING
    status_history: list[dict] = field(default_factory=list)  # [{status, timestamp, reason}]
    
    # Outcome
    outcome_summary: str | None = None
    success_rating: float | None = None       # 0-1, user-provided
    lessons_learned: list[str] = field(default_factory=list)
    what_worked: list[str] = field(default_factory=list)
    what_didnt_work: list[str] = field(default_factory=list)
    
    # Source (if derived from template)
    source_template_id: str | None = None
    template_modifications: list[str] = field(default_factory=list)
    
    # Embedding (for similarity search)
    embedding: list[float] | None = None
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    
    # === LIFECYCLE METHODS ===
    
    def activate(self) -> None:
        """Transition from PLANNING to ACTIVE."""
        if self.status != ProjectStatus.PLANNING:
            raise InvalidStateTransition(f"Cannot activate from {self.status}")
        self._transition_to(ProjectStatus.ACTIVE)
        self.start_date = datetime.now(UTC).isoformat()
    
    def complete(self, outcome_summary: str, success_rating: float) -> None:
        """Transition from ACTIVE to COMPLETED."""
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransition(f"Cannot complete from {self.status}")
        self._transition_to(ProjectStatus.COMPLETED)
        self.outcome_summary = outcome_summary
        self.success_rating = success_rating
        self.end_date = datetime.now(UTC).isoformat()
        self.completed_at = self.end_date
    
    def abandon(self, reason: str) -> None:
        """Transition from ACTIVE to ABANDONED."""
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransition(f"Cannot abandon from {self.status}")
        self._transition_to(ProjectStatus.ABANDONED, reason)
        self.end_date = datetime.now(UTC).isoformat()
    
    def reopen(self) -> None:
        """Transition from COMPLETED back to ACTIVE."""
        if self.status != ProjectStatus.COMPLETED:
            raise InvalidStateTransition(f"Cannot reopen from {self.status}")
        self._transition_to(ProjectStatus.ACTIVE)
    
    def _transition_to(self, new_status: ProjectStatus, reason: str = "") -> None:
        """Record state transition."""
        self.status_history.append({
            "from_status": self.status.value,
            "to_status": new_status.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        })
        self.status = new_status
        self.updated_at = datetime.now(UTC).isoformat()
```

#### 4.4.3 ProjectTemplate

```python
# src/knowledge_mcp/models/template.py

@dataclass
class ProjectTemplate:
    """
    Reusable project structure template.
    
    Abstracted from successful projects or created manually.
    Templates are scored and ranked based on outcomes of
    projects that used them.
    """
    
    id: str
    name: str
    description: str
    
    # Classification
    project_type: str                         # "mcp_server" | "trade_study" | etc.
    domain: str
    tags: list[str] = field(default_factory=list)
    
    # Visibility
    visibility: ProjectVisibility = ProjectVisibility.PERSONAL
    owner: str | None = None
    
    # Template content
    task_template: list[dict] = field(default_factory=list)  # Task structure
    phase_template: list[str] = field(default_factory=list)
    checkpoint_template: list[str] = field(default_factory=list)
    risk_template: list[dict] = field(default_factory=list)
    
    # Guidance
    typical_duration_range: str | None = None    # "2-4 weeks"
    typical_task_count: int | None = None
    complexity_level: str | None = None          # "low" | "medium" | "high"
    prerequisites: list[str] = field(default_factory=list)
    applicable_when: list[str] = field(default_factory=list)
    not_applicable_when: list[str] = field(default_factory=list)
    
    # Provenance
    abstracted_from_project_ids: list[str] = field(default_factory=list)
    created_manually: bool = False
    
    # Scoring (v2 learning)
    score: float = 0.5
    score_confidence: float = 0.0
    times_used: int = 0
    
    # Embedding
    embedding: list[float] | None = None
    
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### 4.5 Feedback & Scoring Models

#### 4.5.1 FeedbackRecord

```python
# src/knowledge_mcp/models/feedback.py

class FeedbackType(str, Enum):
    """Types of feedback."""
    
    # Overall ratings (Tier 2: Quick)
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    RATING = "rating"                    # 1-5 stars
    
    # Specific aspects (Tier 3: Detailed)
    TASKS_COMPLETE = "tasks_complete"
    TASKS_INCOMPLETE = "tasks_incomplete"
    ESTIMATES_ACCURATE = "estimates_accurate"
    ESTIMATES_INACCURATE = "estimates_inaccurate"
    RISKS_IDENTIFIED = "risks_identified"
    RISKS_MISSED = "risks_missed"
    DEPENDENCIES_ACCURATE = "dependencies_accurate"
    DEPENDENCIES_MISSED = "dependencies_missed"
    
    # Outcomes
    PROJECT_SUCCESS = "project_success"
    PROJECT_PARTIAL = "project_partial"
    PROJECT_FAILURE = "project_failure"
    
    # Modifications
    NEEDED_MODIFICATION = "needed_modification"
    USED_AS_IS = "used_as_is"
    
    # Implicit (Tier 1: Automatic)
    RETRIEVED = "retrieved"              # Appeared in results
    USED = "used"                        # Actually used in project


class FeedbackTier(str, Enum):
    """Feedback collection tier (SEAMS decision A5)."""
    
    IMPLICIT = "implicit"                # No user effort
    QUICK = "quick"                      # Minimal effort (thumbs, stars)
    DETAILED = "detailed"                # Significant effort (form)


@dataclass
class FeedbackRecord:
    """
    User feedback on a knowledge artifact or recommendation.
    
    Used to update effectiveness scores and improve future recommendations.
    """
    
    id: str
    
    # What is being rated
    artifact_id: str
    artifact_type: str                   # "template" | "pattern" | "project" | "chunk"
    
    # Context of use
    usage_context: str = ""              # What was the user trying to do?
    project_id: str | None = None        # If used in a project
    
    # Feedback
    feedback_type: FeedbackType
    feedback_tier: FeedbackTier
    rating: float | None = None          # 0-1 for numeric ratings
    comment: str | None = None
    
    # Specific feedback
    specific_data: dict[str, Any] = field(default_factory=dict)
    # e.g., {"tasks_added": 3, "tasks_removed": 1, "estimate_delta_percent": 25}
    
    # Corrections provided
    corrections: list[str] = field(default_factory=list)
    suggested_improvements: list[str] = field(default_factory=list)
    
    # Metadata
    feedback_source: str = "user"        # "user" | "automated" | "outcome_tracking"
    
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

#### 4.5.2 SimpleScore (Phase 2b)

```python
# src/knowledge_mcp/models/score.py

@dataclass
class SimpleScore:
    """
    Simple effectiveness score for Phase 2b.
    
    Single composite score with confidence based on sample size.
    Expanded to multi-factor in Phase 3.
    """
    
    artifact_id: str
    artifact_type: str                   # "template" | "pattern" | "project" | "decision"
    
    # Single composite score
    score: float = 0.5                   # 0-1, default neutral
    confidence: float = 0.0              # 0-1, based on sample size
    
    # Counts
    times_retrieved: int = 0             # Appeared in search results
    times_used: int = 0                  # Actually used in a project
    positive_feedback: int = 0
    negative_feedback: int = 0
    
    # Recency
    last_retrieved: str | None = None
    last_used: str | None = None
    last_feedback: str | None = None
    
    # Staleness (SEAMS standard N4)
    staleness_penalty: float = 0.0       # Increases over time without use
    
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def effective_score(self) -> float:
        """Score with staleness penalty applied."""
        return self.score * (1 - self.staleness_penalty)
    
    def update_from_feedback(self, feedback: FeedbackRecord) -> None:
        """Update score based on new feedback."""
        weight = FEEDBACK_WEIGHTS.get(feedback.feedback_tier.value, 0.4)
        
        if feedback.rating is not None:
            # Weighted moving average
            total_weight = self.positive_feedback + self.negative_feedback + weight
            self.score = (
                (self.score * (total_weight - weight) + feedback.rating * weight) 
                / total_weight
            )
        
        if feedback.feedback_type in [FeedbackType.HELPFUL, FeedbackType.PROJECT_SUCCESS]:
            self.positive_feedback += 1
        elif feedback.feedback_type in [FeedbackType.NOT_HELPFUL, FeedbackType.PROJECT_FAILURE]:
            self.negative_feedback += 1
        
        self.last_feedback = datetime.now(UTC).isoformat()
        self._update_confidence()
        self.updated_at = self.last_feedback
    
    def _update_confidence(self) -> None:
        """Update confidence based on sample size."""
        total_samples = self.positive_feedback + self.negative_feedback + self.times_used
        self.confidence = min(1.0, total_samples / 10)  # Full confidence at 10 samples
```

#### 4.5.3 EffectivenessScore (Phase 3)

```python
# src/knowledge_mcp/models/score.py

@dataclass
class EffectivenessScore:
    """
    Multi-factor effectiveness score for Phase 3.
    
    Expands SimpleScore with factor breakdown and propagation support.
    """
    
    artifact_id: str
    artifact_type: str
    
    # === FACTOR SCORES (0-1 each) ===
    
    relevance_score: float = 0.5         # How well does this match query contexts?
    relevance_samples: int = 0
    
    effectiveness_score: float = 0.5     # When used, did it work?
    effectiveness_samples: int = 0
    
    accuracy_score: float = 0.5          # Were estimates/predictions accurate?
    accuracy_samples: int = 0
    
    completeness_score: float = 0.5      # Was anything missing?
    completeness_samples: int = 0
    
    user_rating_score: float = 0.5       # Explicit user feedback
    user_rating_samples: int = 0
    
    # === COMPOSITE ===
    composite_score: float = 0.5
    confidence: float = 0.0
    
    # === COUNTS ===
    times_retrieved: int = 0
    times_used: int = 0
    times_feedback_received: int = 0
    
    # === RECENCY ===
    last_positive_use: str | None = None
    last_negative_feedback: str | None = None
    staleness_penalty: float = 0.0
    
    # === TIMESTAMPS ===
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def calculate_composite(self, weights: dict[str, float] | None = None) -> float:
        """Calculate weighted composite score."""
        weights = weights or SCORE_FACTOR_WEIGHTS
        
        raw_score = (
            self.relevance_score * weights["relevance"] +
            self.effectiveness_score * weights["effectiveness"] +
            self.accuracy_score * weights["accuracy"] +
            self.completeness_score * weights["completeness"] +
            self.user_rating_score * weights["user_rating"]
        )
        
        # Apply staleness penalty
        self.composite_score = raw_score * (1 - self.staleness_penalty)
        
        # Update confidence
        total_samples = (
            self.relevance_samples +
            self.effectiveness_samples +
            self.accuracy_samples +
            self.completeness_samples +
            self.user_rating_samples
        )
        self.confidence = min(1.0, total_samples / 20)
        
        self.updated_at = datetime.now(UTC).isoformat()
        return self.composite_score
```

### 4.6 Coverage & Assessment Models

#### 4.6.1 CoverageAssessment

```python
# src/knowledge_mcp/models/coverage.py

@dataclass
class KnowledgeGap:
    """A specific gap in knowledge coverage."""
    
    gap_type: str                        # "missing_topic" | "insufficient_depth" | "no_authority" | "stale"
    description: str
    importance: str                      # "critical" | "important" | "nice_to_have"
    suggested_sources: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)


@dataclass
class AcquisitionRecommendation:
    """Recommendation for acquiring missing knowledge."""
    
    action: str                          # "web_search" | "web_crawl" | "request_document" | "none"
    priority: int                        # 1-5, 1 is highest
    rationale: str
    
    # For web actions
    suggested_queries: list[str] = field(default_factory=list)
    suggested_urls: list[str] = field(default_factory=list)
    suggested_domains: list[str] = field(default_factory=list)
    
    # For document requests
    document_type: str = ""
    document_description: str = ""
    example_documents: list[str] = field(default_factory=list)


@dataclass
class CoverageAssessment:
    """Result of knowledge coverage assessment."""
    
    topic: str
    workflow_context: str | None = None
    
    # Scores (0-1)
    coverage_score: float = 0.0
    confidence_score: float = 0.0
    authority_score: float = 0.0
    recency_score: float = 0.0
    overall_score: float = 0.0
    
    # Interpretation
    overall_level: str = ""              # "very_high" | "high" | "medium" | "low" | "very_low"
    
    # Recommendation
    recommendation: str = ""             # "proceed" | "acquire_web" | "request_docs" | "caveat"
    recommendation_rationale: str = ""
    
    # Gaps
    gaps: list[KnowledgeGap] = field(default_factory=list)
    
    # Source summary
    sources_found: int = 0
    source_types: dict[str, int] = field(default_factory=dict)
    most_authoritative: list[str] = field(default_factory=list)
    oldest_source_date: str | None = None
    newest_source_date: str | None = None
    
    # Recommendations
    acquisition_recommendations: list[AcquisitionRecommendation] = field(default_factory=list)
    
    # Proceed options
    can_proceed_with_caveats: bool = False
    caveats_if_proceeding: list[str] = field(default_factory=list)
    
    assessed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### 4.7 Response Envelope

```python
# src/knowledge_mcp/models/response.py

@dataclass
class ToolResponse:
    """Standard response envelope for all MCP tools."""
    
    schema_version: str = "2.0"
    tool: str = ""
    success: bool = True
    
    # Result (tool-specific)
    result: dict[str, Any] | None = None
    
    # Error (if success=False)
    error: str | None = None
    error_code: str | None = None
    
    # Metadata
    coverage_metadata: dict[str, Any] | None = None
    execution_time_ms: int | None = None
    
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### 4.8 Constants

```python
# src/knowledge_mcp/constants.py

# Authority levels for source classification
AUTHORITY_LEVELS = {
    "normative": 1.0,        # Standards with "shall" requirements
    "authoritative": 0.85,   # Official handbooks, guides
    "reputable": 0.7,        # Peer-reviewed, .gov, .edu
    "informative": 0.5,      # General technical content
    "unverified": 0.3,       # Web content, blogs, forums
}

# Confidence score interpretation (SEAMS standard N2)
CONFIDENCE_INTERPRETATION = {
    (0.8, 1.0): ("well_established", "Based on 20+ data points"),
    (0.5, 0.8): ("moderately_validated", "Based on 10-20 data points"),
    (0.2, 0.5): ("limited_data", "Based on 3-10 data points"),
    (0.0, 0.2): ("unvalidated", "Based on 0-3 data points"),
}

# Score interpretation (SEAMS standard N1)
SCORE_INTERPRETATION = {
    (0.8, 1.0): ("highly_effective", "⭐⭐⭐⭐⭐", 1.5),
    (0.6, 0.8): ("effective", "⭐⭐⭐⭐", 1.2),
    (0.4, 0.6): ("moderate", "⭐⭐⭐", 1.0),
    (0.2, 0.4): ("limited", "⭐⭐", 0.8),
    (0.0, 0.2): ("poor", "⭐", 0.5),
}

# Feedback weights (SEAMS standard N3)
FEEDBACK_WEIGHTS = {
    "detailed": 1.0,         # Outcome with actuals
    "quick": 0.4,            # Thumbs/stars
    "implicit": 0.1,         # Usage only
}

# Staleness decay (SEAMS standard N4)
STALENESS_DECAY = {
    30: 0.0,                 # < 30 days: no penalty
    90: 0.05,                # 30-90 days: 5%
    180: 0.10,               # 90-180 days: 10%
    365: 0.20,               # 180-365 days: 20%
    float('inf'): 0.30,      # > 365 days: 30%
}

# Workflow-specific coverage weights
WORKFLOW_WEIGHTS = {
    "rcca": {"coverage": 0.2, "authority": 0.4, "recency": 0.1, "confidence": 0.3},
    "trade_study": {"coverage": 0.3, "authority": 0.3, "recency": 0.2, "confidence": 0.2},
    "exploration": {"coverage": 0.4, "authority": 0.2, "recency": 0.2, "confidence": 0.2},
    "planning": {"coverage": 0.3, "authority": 0.25, "recency": 0.25, "confidence": 0.2},
    "default": {"coverage": 0.25, "authority": 0.25, "recency": 0.25, "confidence": 0.25},
}

# Score factor weights (Phase 3)
SCORE_FACTOR_WEIGHTS = {
    "relevance": 0.15,
    "effectiveness": 0.30,
    "accuracy": 0.20,
    "completeness": 0.15,
    "user_rating": 0.20,
}

# Depth thresholds
DEPTH_THRESHOLDS = {
    "surface": 3,
    "working": 10,
    "expert": 25,
}
```
# Knowledge-MCP v2 Complete Specification (Part 3)

## 5. MCP Tools Specification

### 5.1 Tool Overview

| # | Tool | Category | Phase | Primary Operations |
|---|------|----------|-------|-------------------|
| 1 | `knowledge_search` | Core | 1 | Semantic search with score boosting |
| 2 | `knowledge_stats` | Core | 1 | Collection statistics |
| 3 | `knowledge_ingest` | Core | 1 | Ingest document or URL |
| 4 | `knowledge_sources` | Core | 1 | List indexed sources |
| 5 | `knowledge_assess_coverage` | Acquisition | 1 | Topic coverage assessment |
| 6 | `knowledge_preflight` | Acquisition | 1 | Workflow readiness check |
| 7 | `knowledge_acquire` | Acquisition | 1 | Web content acquisition |
| 8 | `knowledge_request_document` | Acquisition | 1 | Request doc from user |
| 9 | `knowledge_rcca_support` | Workflow | 2a | RCCA operations |
| 10 | `knowledge_trade_support` | Workflow | 2a | Trade study operations |
| 11 | `knowledge_explore` | Workflow | 2a | Exploration operations |
| 12 | `knowledge_planning_support` | Workflow | 2a | Planning + capture operations |
| 13 | `knowledge_feedback` | Learning | 2b | Feedback collection |
| 14 | `knowledge_relationship` | Graph | 3 | Relationship management |
| 15 | `knowledge_admin` | Admin | 3 | Administration + scores |

---

### 5.2 Core Tools (Phase 1)

#### 5.2.1 knowledge_search

```json
{
    "name": "knowledge_search",
    "description": "Search the knowledge base for relevant information.\n\nReturns semantically similar content with source citations, coverage quality indicators, and score-boosted ranking.\n\nResults are ranked by: (semantic_similarity * 0.7) + (effectiveness_score * 0.3)\n\nUse for general knowledge retrieval. For workflow-specific searches, use the workflow tools.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query"
            },
            "n_results": {
                "type": "integer",
                "description": "Maximum results (1-100)",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            },
            "filter": {
                "type": "object",
                "description": "Metadata filters",
                "properties": {
                    "document_type": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by type: standard, handbook, guide, web, report"
                    },
                    "source_type": {
                        "type": "string",
                        "enum": ["any", "document", "web"],
                        "default": "any"
                    },
                    "normative_only": {
                        "type": "boolean",
                        "default": false
                    },
                    "min_authority": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "min_score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Minimum effectiveness score"
                    }
                }
            },
            "score_threshold": {
                "type": "number",
                "default": 0.0,
                "minimum": 0.0,
                "maximum": 1.0
            },
            "include_coverage_assessment": {
                "type": "boolean",
                "default": true
            },
            "boost_by_score": {
                "type": "boolean",
                "default": true,
                "description": "Boost results by effectiveness score"
            }
        },
        "required": ["query"]
    }
}
```

#### 5.2.2 knowledge_stats

```json
{
    "name": "knowledge_stats",
    "description": "Get statistics about the knowledge base.\n\nReturns collection metrics, source distribution, health indicators, and scoring statistics.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "include_domain_breakdown": {
                "type": "boolean",
                "default": false
            },
            "include_freshness_metrics": {
                "type": "boolean",
                "default": false
            },
            "include_score_distribution": {
                "type": "boolean",
                "default": false
            }
        }
    }
}
```

#### 5.2.3 knowledge_ingest

```json
{
    "name": "knowledge_ingest",
    "description": "Ingest a document or web page into the knowledge base.\n\nSupports:\n- Local files: PDF, DOCX (provide file path)\n- Web pages: HTTP/HTTPS URLs\n- Direct content: Markdown text with 'content:' prefix\n\nFor bulk web acquisition, use knowledge_acquire instead.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "File path, URL, or 'content:' prefix for direct markdown"
            },
            "source_type": {
                "type": "string",
                "enum": ["auto", "pdf", "docx", "web", "markdown"],
                "default": "auto"
            },
            "metadata_overrides": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "document_type": {"type": "string"},
                    "authority_level": {
                        "type": "string",
                        "enum": ["normative", "authoritative", "reputable", "informative", "unverified"]
                    },
                    "standard_id": {"type": "string"},
                    "version": {"type": "string"}
                }
            },
            "assess_relevance": {
                "type": "boolean",
                "default": false
            },
            "relevance_context": {
                "type": "string",
                "description": "Context for relevance assessment (required if assess_relevance=true)"
            },
            "relevance_threshold": {
                "type": "number",
                "default": 0.5
            }
        },
        "required": ["source"]
    }
}
```

#### 5.2.4 knowledge_sources

```json
{
    "name": "knowledge_sources",
    "description": "List indexed sources with metadata.\n\nReturns information about documents and web pages in the knowledge base.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "source_type": {
                "type": "string",
                "enum": ["all", "document", "web"],
                "default": "all"
            },
            "document_type": {
                "type": "array",
                "items": {"type": "string"}
            },
            "sort_by": {
                "type": "string",
                "enum": ["title", "date_added", "chunk_count", "authority", "score"],
                "default": "title"
            },
            "limit": {
                "type": "integer",
                "default": 50,
                "maximum": 200
            },
            "include_scores": {
                "type": "boolean",
                "default": true
            }
        }
    }
}
```

---

### 5.3 Acquisition Tools (Phase 1)

#### 5.3.1 knowledge_assess_coverage

```json
{
    "name": "knowledge_assess_coverage",
    "description": "Assess knowledge base coverage for a topic.\n\nCALL THIS BEFORE starting workflows that depend on knowledge retrieval.\n\nReturns coverage scores, identified gaps, and acquisition recommendations.\n\nScores are weighted by workflow context:\n- RCCA: High weight on authority\n- Trade Study: Balanced\n- Planning: Higher recency weight",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Topic or question to assess coverage for"
            },
            "required_depth": {
                "type": "string",
                "enum": ["surface", "working", "expert"],
                "default": "working"
            },
            "required_authority": {
                "type": "string",
                "enum": ["any", "reputable", "authoritative", "normative"],
                "default": "reputable"
            },
            "recency_requirement": {
                "type": "string",
                "enum": ["any", "recent_5y", "recent_2y", "current"],
                "default": "any"
            },
            "workflow_context": {
                "type": "string",
                "enum": ["rcca", "trade_study", "exploration", "planning", "general"],
                "default": "general"
            }
        },
        "required": ["topic"]
    }
}
```

#### 5.3.2 knowledge_preflight

```json
{
    "name": "knowledge_preflight",
    "description": "Run comprehensive knowledge check before starting a workflow.\n\nAnalyzes workflow requirements and assesses coverage for ALL topics that will be needed.\n\nCALL THIS AT THE START of RCCA, Trade Study, Planning, or Exploration workflows.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "workflow_type": {
                "type": "string",
                "enum": ["rcca", "trade_study", "exploration", "planning", "gap_analysis"]
            },
            "workflow_description": {
                "type": "string"
            },
            "key_topics": {
                "type": "array",
                "items": {"type": "string"}
            },
            "required_standards": {
                "type": "array",
                "items": {"type": "string"}
            },
            "domain": {
                "type": "string"
            }
        },
        "required": ["workflow_type", "workflow_description"]
    }
}
```

#### 5.3.3 knowledge_acquire

```json
{
    "name": "knowledge_acquire",
    "description": "Acquire knowledge from web sources and add to knowledge base.\n\nUse when knowledge_assess_coverage recommends web acquisition.\n\nProcess:\n1. Search/crawl specified URLs or queries\n2. Assess relevance to topic\n3. Ingest relevant content\n4. Return acquisition summary with coverage improvement",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Topic being researched (for relevance assessment)"
            },
            "urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific URLs to crawl"
            },
            "search_queries": {
                "type": "array",
                "items": {"type": "string"}
            },
            "max_pages": {
                "type": "integer",
                "default": 10,
                "maximum": 50
            },
            "relevance_threshold": {
                "type": "number",
                "default": 0.6
            },
            "domain_allowlist": {
                "type": "array",
                "items": {"type": "string"}
            },
            "prefer_authoritative": {
                "type": "boolean",
                "default": true
            }
        },
        "required": ["topic"]
    }
}
```

#### 5.3.4 knowledge_request_document

```json
{
    "name": "knowledge_request_document",
    "description": "Request a document from the user to add to knowledge base.\n\nUse when knowledge_assess_coverage indicates need for authoritative sources that cannot be obtained from web.\n\nGenerates a structured request for the user.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string"
            },
            "document_type": {
                "type": "string",
                "enum": ["standard", "handbook", "guide", "report", "paper", "internal", "vendor", "any"]
            },
            "rationale": {
                "type": "string"
            },
            "example_documents": {
                "type": "array",
                "items": {"type": "string"}
            },
            "urgency": {
                "type": "string",
                "enum": ["blocking", "important", "nice_to_have"],
                "default": "important"
            },
            "workflow_context": {
                "type": "string"
            },
            "can_proceed_without": {
                "type": "boolean",
                "default": true
            },
            "workaround_if_unavailable": {
                "type": "string"
            }
        },
        "required": ["topic", "rationale"]
    }
}
```

---

### 5.4 Workflow Tools (Phase 2a)

#### 5.4.1 knowledge_rcca_support

```json
{
    "name": "knowledge_rcca_support",
    "description": "Specialized knowledge retrieval for RCCA workflows.\n\nOperations:\n- find_similar: Find similar past failures/incidents\n- trace_cause: Trace causal chains from effect to root cause\n- find_corrective: Find corrective actions for a root cause\n- check_compliance: Check for requirement violations",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["find_similar", "trace_cause", "find_corrective", "check_compliance"]
            },
            "problem_description": {
                "type": "string",
                "description": "[find_similar] Description of the current problem"
            },
            "symptom_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "[find_similar] Observable symptoms"
            },
            "effect_description": {
                "type": "string",
                "description": "[trace_cause] The observed failure effect"
            },
            "known_factors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "[trace_cause] Known contributing factors"
            },
            "max_chain_depth": {
                "type": "integer",
                "default": 5
            },
            "root_cause": {
                "type": "string",
                "description": "[find_corrective] The identified root cause"
            },
            "ca_type": {
                "type": "string",
                "enum": ["any", "corrective", "preventive", "detective"],
                "default": "any"
            },
            "situation_description": {
                "type": "string",
                "description": "[check_compliance] Situation to check"
            },
            "standards_filter": {
                "type": "array",
                "items": {"type": "string"}
            },
            "domain": {
                "type": "string"
            },
            "n_results": {
                "type": "integer",
                "default": 10
            }
        },
        "required": ["operation"]
    }
}
```

#### 5.4.2 knowledge_trade_support

```json
{
    "name": "knowledge_trade_support",
    "description": "Specialized knowledge retrieval for Trade Study workflows.\n\nOperations:\n- extract_criteria: Find evaluation criteria from standards\n- find_alternatives: Discover documented alternatives\n- find_precedents: Find similar past decisions\n- assess_risks: Find documented risks for an alternative",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["extract_criteria", "find_alternatives", "find_precedents", "assess_risks"]
            },
            "decision_context": {
                "type": "string",
                "description": "[extract_criteria] What decision is being made"
            },
            "need_statement": {
                "type": "string",
                "description": "[find_alternatives] What need to address"
            },
            "current_approach": {
                "type": "string",
                "description": "[find_alternatives] Current approach"
            },
            "decision_description": {
                "type": "string",
                "description": "[find_precedents] The decision being made"
            },
            "key_factors": {
                "type": "array",
                "items": {"type": "string"}
            },
            "alternative_description": {
                "type": "string",
                "description": "[assess_risks] Alternative to assess"
            },
            "context": {
                "type": "string"
            },
            "domain": {
                "type": "string"
            },
            "standards_filter": {
                "type": "array",
                "items": {"type": "string"}
            },
            "n_results": {
                "type": "integer",
                "default": 10
            }
        },
        "required": ["operation"]
    }
}
```

#### 5.4.3 knowledge_explore

```json
{
    "name": "knowledge_explore",
    "description": "Exploration and analysis operations.\n\nOperations:\n- match_antipatterns: Match content against known anti-patterns\n- gap_analysis: Compare content against standards\n- counterarguments: Find contradicting evidence\n- synthesize: Multi-query research synthesis",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["match_antipatterns", "gap_analysis", "counterarguments", "synthesize"]
            },
            "content": {
                "type": "string",
                "description": "[match_antipatterns, gap_analysis] Content to analyze"
            },
            "domains": {
                "type": "array",
                "items": {"type": "string"}
            },
            "severity_threshold": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium"
            },
            "reference_standards": {
                "type": "array",
                "items": {"type": "string"},
                "description": "[gap_analysis] Standards to compare against"
            },
            "focus_areas": {
                "type": "array",
                "items": {"type": "string"}
            },
            "claim": {
                "type": "string",
                "description": "[counterarguments] Claim to challenge"
            },
            "search_mode": {
                "type": "string",
                "enum": ["contradicts", "qualifies", "alternatives", "all"],
                "default": "all"
            },
            "question": {
                "type": "string",
                "description": "[synthesize] Research question"
            },
            "sub_queries": {
                "type": "array",
                "items": {"type": "string"}
            },
            "synthesis_format": {
                "type": "string",
                "enum": ["narrative", "bullet_points", "structured"],
                "default": "structured"
            },
            "n_results": {
                "type": "integer",
                "default": 10
            }
        },
        "required": ["operation"]
    }
}
```

#### 5.4.4 knowledge_planning_support

```json
{
    "name": "knowledge_planning_support",
    "description": "Specialized knowledge retrieval and capture for project planning workflows.\n\nRetrieval Operations:\n- find_templates: Task structures, WBS patterns, checklists\n- find_precedents: How similar projects were structured\n- identify_risks: Documented risks for this type of work\n- identify_dependencies: Technical and process dependencies\n- find_constraints: Standards, policies that apply\n- find_checkpoints: Required reviews, gates, milestones\n- estimate_scope: Historical complexity/effort indicators\n\nCapture Operations:\n- capture_project: Store a project structure\n- capture_outcome: Record project completion and outcomes\n- capture_template: Abstract project into reusable template\n- capture_lesson: Store a lesson learned",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "find_templates", "find_precedents", "identify_risks",
                    "identify_dependencies", "find_constraints", "find_checkpoints",
                    "estimate_scope",
                    "capture_project", "capture_outcome", "capture_template", "capture_lesson"
                ]
            },
            
            "project_type": {
                "type": "string",
                "description": "Type of project (e.g., 'mcp_server', 'trade_study', 'rcca')"
            },
            "project_description": {
                "type": "string"
            },
            "domain": {
                "type": "string"
            },
            
            "template_type": {
                "type": "string",
                "enum": ["wbs", "checklist", "task_list", "phase_structure", "any"],
                "default": "any"
            },
            "similarity_factors": {
                "type": "array",
                "items": {"type": "string"}
            },
            "include_outcomes": {
                "type": "boolean",
                "default": true
            },
            "risk_categories": {
                "type": "array",
                "items": {"type": "string"}
            },
            "dependency_types": {
                "type": "array",
                "items": {"type": "string"}
            },
            "constraint_sources": {
                "type": "array",
                "items": {"type": "string"}
            },
            "lifecycle_model": {
                "type": "string"
            },
            "scope_factors": {
                "type": "array",
                "items": {"type": "string"}
            },
            
            "project": {
                "type": "object",
                "description": "[capture_project] Project structure",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "project_type": {"type": "string"},
                    "domain": {"type": "string"},
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "parent_task": {"type": "string"},
                                "estimated_hours": {"type": "number"},
                                "depends_on": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "context_factors": {"type": "object"},
                    "identified_risks": {"type": "array"},
                    "estimated_duration_days": {"type": "number"},
                    "source_template_id": {"type": "string"},
                    "visibility": {
                        "type": "string",
                        "enum": ["personal", "team", "organization"],
                        "default": "personal"
                    }
                }
            },
            
            "project_id": {
                "type": "string",
                "description": "[capture_outcome, capture_template] Project ID"
            },
            "outcome": {
                "type": "object",
                "description": "[capture_outcome] Outcome details",
                "properties": {
                    "status": {"type": "string", "enum": ["completed", "partial", "abandoned"]},
                    "actual_duration_days": {"type": "number"},
                    "actual_effort_hours": {"type": "number"},
                    "success_rating": {"type": "number", "minimum": 0, "maximum": 1},
                    "outcome_summary": {"type": "string"},
                    "lessons_learned": {"type": "array", "items": {"type": "string"}},
                    "what_worked": {"type": "array", "items": {"type": "string"}},
                    "what_didnt_work": {"type": "array", "items": {"type": "string"}}
                }
            },
            
            "template_name": {
                "type": "string",
                "description": "[capture_template] Name for new template"
            },
            "generalization_notes": {
                "type": "string",
                "description": "[capture_template] How to generalize"
            },
            
            "lesson": {
                "type": "object",
                "description": "[capture_lesson] Lesson learned",
                "properties": {
                    "title": {"type": "string"},
                    "context": {"type": "string"},
                    "lesson": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "project_type": {"type": "string"},
                    "domain": {"type": "string"}
                }
            },
            
            "n_results": {
                "type": "integer",
                "default": 10
            }
        },
        "required": ["operation"]
    }
}
```

---

### 5.5 Learning Tools (Phase 2b)

#### 5.5.1 knowledge_feedback

```json
{
    "name": "knowledge_feedback",
    "description": "Provide feedback on knowledge artifacts to improve future recommendations.\n\nOperations:\n- rate: Quick overall rating (Tier 2)\n- rate_specific: Detailed aspect ratings (Tier 3)\n- report_outcome: Report how well a recommendation worked\n- suggest_improvement: Suggest how an artifact could be better\n\nFeedback updates effectiveness scores and improves ranking.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["rate", "rate_specific", "report_outcome", "suggest_improvement"]
            },
            
            "artifact_id": {
                "type": "string",
                "description": "ID of the artifact being rated"
            },
            "artifact_type": {
                "type": "string",
                "enum": ["template", "pattern", "project", "decision", "chunk"]
            },
            "usage_context": {
                "type": "string",
                "description": "What were you trying to accomplish?"
            },
            
            "rating": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "[rate] Overall rating 0-1"
            },
            "helpful": {
                "type": "boolean",
                "description": "[rate] Was this helpful?"
            },
            
            "aspect_ratings": {
                "type": "object",
                "description": "[rate_specific] Aspect ratings",
                "properties": {
                    "relevance": {"type": "number", "minimum": 0, "maximum": 1},
                    "completeness": {"type": "number", "minimum": 0, "maximum": 1},
                    "accuracy": {"type": "number", "minimum": 0, "maximum": 1},
                    "usefulness": {"type": "number", "minimum": 0, "maximum": 1}
                }
            },
            
            "outcome_type": {
                "type": "string",
                "enum": [
                    "tasks_complete", "tasks_incomplete",
                    "estimates_accurate", "estimates_inaccurate",
                    "risks_identified", "risks_missed",
                    "used_as_is", "needed_modification",
                    "project_success", "project_partial", "project_failure"
                ]
            },
            "outcome_details": {
                "type": "object",
                "properties": {
                    "tasks_added": {"type": "integer"},
                    "tasks_removed": {"type": "integer"},
                    "estimate_delta_percent": {"type": "number"},
                    "risks_that_occurred": {"type": "array", "items": {"type": "string"}},
                    "risks_missed": {"type": "array", "items": {"type": "string"}},
                    "modifications_made": {"type": "array", "items": {"type": "string"}}
                }
            },
            
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "[suggest_improvement] Improvement suggestions"
            },
            "missing_elements": {
                "type": "array",
                "items": {"type": "string"}
            },
            
            "comment": {
                "type": "string"
            }
        },
        "required": ["operation", "artifact_id", "artifact_type"]
    }
}
```

---

### 5.6 Graph Tools (Phase 3)

#### 5.6.1 knowledge_relationship

```json
{
    "name": "knowledge_relationship",
    "description": "Manage relationships between knowledge chunks.\n\nOperations:\n- add: Create a relationship\n- remove: Delete a relationship\n- traverse: Follow relationships from a chunk\n- find: Find relationships of a type\n\nRelationships enable causal tracing and contradiction detection.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "remove", "traverse", "find"]
            },
            
            "source_chunk_id": {
                "type": "string"
            },
            "target_chunk_id": {
                "type": "string"
            },
            "relationship_type": {
                "type": "string",
                "enum": [
                    "references", "supersedes", "implements",
                    "supports", "contradicts", "qualifies",
                    "causes", "prevents", "indicates",
                    "alternative_to", "preferred_over"
                ]
            },
            "context": {
                "type": "string",
                "description": "[add] Why this relationship exists"
            },
            "bidirectional": {
                "type": "boolean",
                "default": false
            },
            
            "relationship_id": {
                "type": "string",
                "description": "[remove] Relationship ID"
            },
            
            "direction": {
                "type": "string",
                "enum": ["outgoing", "incoming", "both"],
                "default": "both"
            },
            "max_depth": {
                "type": "integer",
                "default": 3
            },
            "relationship_types": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["operation"]
    }
}
```

---

### 5.7 Admin Tools (Phase 3)

#### 5.7.1 knowledge_admin

```json
{
    "name": "knowledge_admin",
    "description": "Administrative operations for knowledge base management.\n\nOperations:\n- health_report: Overall KB health and coverage\n- usage_analytics: Search patterns and gaps\n- stale_content: Identify outdated content\n- refresh_web: Re-crawl web sources\n- scores_view: View score details for artifacts\n- scores_recalculate: Force score recalculation\n- scores_explain: Explain why artifact has its score\n- export: Export collection data\n- import: Import from backup",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "health_report", "usage_analytics", "stale_content",
                    "refresh_web",
                    "scores_view", "scores_recalculate", "scores_explain",
                    "export", "import"
                ]
            },
            
            "include_recommendations": {
                "type": "boolean",
                "default": true
            },
            
            "max_age_days": {
                "type": "integer",
                "default": 365
            },
            
            "source_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "[refresh_web] Sources to refresh"
            },
            
            "artifact_id": {
                "type": "string",
                "description": "[scores_*] Artifact ID"
            },
            "artifact_type": {
                "type": "string"
            },
            "artifact_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "[scores_view] Multiple artifacts"
            },
            
            "format": {
                "type": "string",
                "enum": ["json", "parquet"],
                "default": "json"
            },
            "path": {
                "type": "string",
                "description": "[export, import] File path"
            },
            "collections": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["operation"]
    }
}
```

---

### 5.8 Response Examples

#### Search with Score Boosting

```json
{
    "schema_version": "2.0",
    "tool": "knowledge_search",
    "success": true,
    "result": {
        "query": "system requirements review",
        "total_results": 15,
        "results": [
            {
                "id": "chunk-uuid-1",
                "content": "The System Requirements Review (SRR) shall...",
                "semantic_score": 0.92,
                "effectiveness_score": 0.85,
                "combined_score": 0.90,
                "score_confidence": 0.78,
                "source": {
                    "document_id": "ieee-15288-2023",
                    "document_title": "IEEE 15288:2023",
                    "section_title": "Technical Reviews",
                    "clause_number": "6.4.7.2",
                    "authority_score": 1.0
                }
            }
        ],
        "coverage_metadata": {
            "coverage_score": 0.78,
            "authority_score": 0.85,
            "recommendation": "results_sufficient"
        }
    }
}
```

#### Project Capture Response

```json
{
    "schema_version": "2.0",
    "tool": "knowledge_planning_support",
    "success": true,
    "result": {
        "operation": "capture_project",
        "project_id": "proj-2026-0127-001",
        "status": "planning",
        "summary": {
            "name": "Knowledge-MCP v2 Implementation",
            "task_count": 32,
            "estimated_duration_days": 45,
            "source_template_id": "tmpl-mcp-server-001"
        },
        "next_steps": [
            "Execute project with planning_support:capture_outcome when complete",
            "Provide feedback with knowledge_feedback for continuous improvement"
        ]
    }
}
```

#### Feedback Response with Score Update

```json
{
    "schema_version": "2.0",
    "tool": "knowledge_feedback",
    "success": true,
    "result": {
        "operation": "report_outcome",
        "feedback_id": "fb-2026-0127-001",
        "artifact_id": "tmpl-mcp-server-001",
        "score_update": {
            "previous_score": 0.65,
            "new_score": 0.72,
            "previous_confidence": 0.45,
            "new_confidence": 0.52,
            "factors_updated": ["effectiveness", "accuracy"]
        },
        "propagation": {
            "propagated_to": [],
            "note": "No source template to propagate to"
        },
        "message": "Thank you for the feedback. This helps improve future recommendations."
    }
}
```
# Knowledge-MCP v2 Complete Specification (Part 4)

## 6. Scoring System

### 6.1 Overview

The scoring system enables **learning from experience**. Artifacts (templates, patterns, projects) receive effectiveness scores based on:
- Implicit signals (retrieval, usage)
- Quick feedback (helpful/not helpful, stars)
- Detailed feedback (outcome data, aspect ratings)
- Propagation from derived artifacts

### 6.2 Score Calculation

#### 6.2.1 Phase 2b: Simple Scoring

```python
# Single composite score with confidence

def calculate_simple_score(
    positive_feedback: int,
    negative_feedback: int,
    times_used: int,
    recent_ratings: list[float],
) -> tuple[float, float]:
    """
    Calculate simple score and confidence.
    
    Returns: (score, confidence)
    """
    # Base score from feedback ratio
    total_feedback = positive_feedback + negative_feedback
    if total_feedback > 0:
        feedback_score = positive_feedback / total_feedback
    else:
        feedback_score = 0.5  # Neutral default
    
    # Incorporate recent ratings
    if recent_ratings:
        rating_score = sum(recent_ratings) / len(recent_ratings)
        score = (feedback_score * 0.4) + (rating_score * 0.6)
    else:
        score = feedback_score
    
    # Confidence based on sample size
    total_samples = total_feedback + times_used
    confidence = min(1.0, total_samples / 10)
    
    return score, confidence
```

#### 6.2.2 Phase 3: Multi-Factor Scoring

```python
# Weighted factor scoring with propagation

def calculate_multi_factor_score(
    effectiveness: EffectivenessScore,
    weights: dict[str, float] | None = None,
) -> float:
    """
    Calculate weighted composite from factors.
    """
    weights = weights or {
        "relevance": 0.15,
        "effectiveness": 0.30,
        "accuracy": 0.20,
        "completeness": 0.15,
        "user_rating": 0.20,
    }
    
    raw_score = (
        effectiveness.relevance_score * weights["relevance"] +
        effectiveness.effectiveness_score * weights["effectiveness"] +
        effectiveness.accuracy_score * weights["accuracy"] +
        effectiveness.completeness_score * weights["completeness"] +
        effectiveness.user_rating_score * weights["user_rating"]
    )
    
    # Apply staleness penalty
    return raw_score * (1 - effectiveness.staleness_penalty)
```

### 6.3 Score Propagation (Phase 3)

When a project provides feedback, scores propagate to related artifacts:

```python
class ScorePropagator:
    """Propagate feedback to related artifacts."""
    
    async def propagate(
        self,
        project: ProjectRecord,
        feedback: FeedbackRecord,
    ) -> list[str]:
        """
        Propagate feedback from project to source template.
        
        Weight is based on how much the project was modified.
        """
        updated = []
        
        if not project.source_template_id:
            return updated
        
        # Calculate modification factor
        modification_count = len(project.template_modifications)
        weight = max(0.3, 1.0 - (modification_count * 0.1))
        
        # Update template score
        template_score = await self._get_score(project.source_template_id)
        
        if feedback.rating is not None:
            await self._update_factor(
                artifact_id=project.source_template_id,
                factor="effectiveness",
                value=feedback.rating,
                weight=weight,
            )
            updated.append(project.source_template_id)
        
        return updated
```

### 6.4 Staleness Decay

Scores decay over time without use:

```python
def calculate_staleness_penalty(
    last_used: datetime | None,
    last_feedback: datetime | None,
) -> float:
    """
    Calculate staleness penalty based on recency.
    
    Returns penalty factor (0.0 to 0.3).
    """
    if not last_used and not last_feedback:
        return 0.3  # Maximum penalty for never-used
    
    # Use most recent activity
    most_recent = max(filter(None, [last_used, last_feedback]))
    days_since = (datetime.now(UTC) - most_recent).days
    
    # Apply decay schedule
    for threshold, penalty in STALENESS_DECAY.items():
        if days_since < threshold:
            return penalty
    
    return 0.3  # Maximum penalty
```

### 6.5 Search Ranking with Scores

Results are ranked by combined semantic and effectiveness scores:

```python
def rank_results(
    results: list[SearchResult],
    semantic_weight: float = 0.7,
    effectiveness_weight: float = 0.3,
) -> list[SearchResult]:
    """
    Rank results by combined score.
    
    combined = (semantic * 0.7) + (effectiveness * boost_factor * 0.3)
    
    boost_factor comes from SCORE_INTERPRETATION table.
    """
    for result in results:
        score = result.effectiveness_score or 0.5
        
        # Get boost factor from score interpretation
        boost = 1.0
        for (low, high), (_, _, factor) in SCORE_INTERPRETATION.items():
            if low <= score < high:
                boost = factor
                break
        
        result.combined_score = (
            result.semantic_score * semantic_weight +
            score * boost * effectiveness_weight
        )
    
    return sorted(results, key=lambda r: r.combined_score, reverse=True)
```

---

## 7. Implementation Phases

### 7.1 Phase Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   IMPLEMENTATION TIMELINE                   │
└─────────────────────────────────────────────────────────────┘

  Week 1-2         Week 3-4         Week 5-6         Week 7-8
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ PHASE 1 │      │ PHASE 1 │      │PHASE 2a │      │PHASE 2b │
│  Core   │──────│  Test   │──────│Workflow │──────│Feedback │
│ +Acquis │      │  & Fix  │      │+Capture │      │+Scoring │
└─────────┘      └─────────┘      └─────────┘      └─────────┘

  Week 9-10        Week 11-12
     │                │
     ▼                ▼
┌─────────┐      ┌─────────┐
│ PHASE 3 │      │ PHASE 3 │
│Advanced │──────│ Release │
│+Admin   │      │   Prep  │
└─────────┘      └─────────┘
```

### 7.2 Phase 1: Core + Acquisition (Weeks 1-4)

**Objective:** Enable unified document and web ingestion with acquisition loop.

#### Deliverables

| Component | Files | Description |
|-----------|-------|-------------|
| KnowledgeChunk v2 | `models/chunk.py` | Extended with web source fields |
| DocumentMetadata v2 | `models/document.py` | Extended with authority, freshness |
| WebIngestor | `ingest/web_ingestor.py` | Crawl4AI integration |
| CoverageAssessor | `assess/coverage_assessor.py` | Topic coverage analysis |
| RelevanceAssessor | `assess/relevance_assessor.py` | Content relevance scoring |
| AcquisitionManager | `acquire/manager.py` | Orchestrate acquisition |
| SourceStore | `store/source_store.py` | Track source metadata |
| OfflineManager | `store/offline_manager.py` | ChromaDB sync |

#### Tools (8)

- `knowledge_search` (enhanced)
- `knowledge_stats` (enhanced)
- `knowledge_ingest`
- `knowledge_sources`
- `knowledge_assess_coverage`
- `knowledge_preflight`
- `knowledge_acquire`
- `knowledge_request_document`

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Web ingestion reliability | 100% |
| Coverage assessment correlation | >0.75 |
| Offline mode functional | 100% |
| No regression on existing tests | 100% |

---

### 7.3 Phase 2a: Workflow + Capture (Weeks 5-6)

**Objective:** Add workflow tools and project capture capability.

#### Deliverables

| Component | Files | Description |
|-----------|-------|-------------|
| TaskRecord | `models/project.py` | Task within project |
| ProjectRecord | `models/project.py` | Project structure with lifecycle |
| ProjectTemplate | `models/template.py` | Reusable templates |
| WorkflowSearcher | `search/workflow_search.py` | Workflow-specific search |
| PlanningSearcher | `search/planning_search.py` | Planning-specific retrieval |
| ProjectCapture | `capture/project_capture.py` | Store project structures |
| PatternStore | `store/pattern_store.py` | Pattern library |

#### Tools (+4 = 12)

- `knowledge_rcca_support`
- `knowledge_trade_support`
- `knowledge_explore`
- `knowledge_planning_support`

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Similar failure recall@5 | >0.70 |
| Project capture works | 100% |
| State machine transitions valid | 100% |

---

### 7.4 Phase 2b: Feedback + Basic Scoring (Weeks 7-8)

**Objective:** Add feedback collection and simple scoring.

#### Deliverables

| Component | Files | Description |
|-----------|-------|-------------|
| FeedbackRecord | `models/feedback.py` | Feedback storage |
| SimpleScore | `models/score.py` | Simple effectiveness score |
| FeedbackCollector | `feedback/collector.py` | Gather feedback |
| SimpleScorer | `scoring/simple_scorer.py` | Calculate simple scores |
| ScoreStore | `store/score_store.py` | Store scores |

#### Tools (+1 = 13)

- `knowledge_feedback`

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Feedback collection works | 100% |
| Score updates on feedback | 100% |
| Score-boosted search works | 100% |

---

### 7.5 Phase 3: Advanced Scoring + Admin (Weeks 9-12)

**Objective:** Full multi-factor scoring, propagation, and admin tools.

#### Deliverables

| Component | Files | Description |
|-----------|-------|-------------|
| EffectivenessScore | `models/score.py` | Multi-factor scoring |
| ChunkRelationship | `models/relationship.py` | Relationship model |
| ScorePropagator | `scoring/propagator.py` | Propagate to templates |
| StalenessCalculator | `scoring/staleness.py` | Decay calculation |
| RelationshipStore | `store/relationship_store.py` | Graph edges |
| AdminManager | `admin/manager.py` | Admin operations |

#### Tools (+2 = 15)

- `knowledge_relationship`
- `knowledge_admin`

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Score prediction accuracy | >0.6 correlation |
| Propagation works | 100% |
| Admin tools functional | 100% |

---

## 8. Storage Design

### 8.1 Collections

```
┌────────────────────────────────────────────────────────────────┐
│                           8 COLLECTIONS                        │
└────────────────────────────────────────────────────────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   chunks    │  │   sources   │  │relationships│  │  patterns   │
│             │  │             │  │             │  │             │
│ • Vector    │  │ • Metadata  │  │ • Graph     │  │ • Vector    │
│ • 1536 dim  │  │ • No vector │  │ • No vector │  │ • 1536 dim  │
│ • Content   │  │ • Tracking  │  │ • Edges     │  │ • Matching  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  decisions  │  │  projects   │  │  feedback   │  │   scores    │
│             │  │             │  │             │  │             │
│ • Vector    │  │ • Vector    │  │ • Metadata  │  │ • Metadata  │
│ • 1536 dim  │  │ • 1536 dim  │  │ • No vector │  │ • No vector │
│ • Precedent │  │ • Captured  │  │ • Append    │  │ • Lookup    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

### 8.2 Collection Schemas

#### chunks (Phase 1)

```python
{
    "vectors": {"size": 1536, "distance": "Cosine"},
    "payload_schema": {
        "document_id": "keyword",
        "document_type": "keyword",
        "source_type": "keyword",
        "content_hash": "keyword",
        "clause_number": "keyword",
        "chunk_type": "keyword",
        "normative": "bool",
        "source_domain": "keyword",
        "authority_score": "float",
        "created_at": "datetime",
    }
}
```

#### sources (Phase 1)

```python
{
    "vectors": None,
    "payload_schema": {
        "document_id": "keyword",
        "document_type": "keyword",
        "source_type": "keyword",
        "source_url": "keyword",
        "source_domain": "keyword",
        "authority_level": "keyword",
        "crawled_at": "datetime",
        "processing_status": "keyword",
    }
}
```

#### projects (Phase 2a)

```python
{
    "vectors": {"size": 1536, "distance": "Cosine"},
    "payload_schema": {
        "project_type": "keyword",
        "domain": "keyword",
        "status": "keyword",
        "visibility": "keyword",
        "source_template_id": "keyword",
        "success_rating": "float",
        "created_at": "datetime",
        "completed_at": "datetime",
    }
}
```

#### patterns (Phase 2a)

```python
{
    "vectors": {"size": 1536, "distance": "Cosine"},
    "payload_schema": {
        "pattern_type": "keyword",
        "domain": "keyword",
        "severity": "keyword",
        "score": "float",
        "score_confidence": "float",
    }
}
```

#### feedback (Phase 2b)

```python
{
    "vectors": None,
    "payload_schema": {
        "artifact_id": "keyword",
        "artifact_type": "keyword",
        "feedback_type": "keyword",
        "feedback_tier": "keyword",
        "rating": "float",
        "project_id": "keyword",
        "created_at": "datetime",
    }
}
```

#### scores (Phase 2b)

```python
{
    "vectors": None,
    "payload_schema": {
        "artifact_id": "keyword",
        "artifact_type": "keyword",
        "score": "float",
        "confidence": "float",
        "times_used": "integer",
        "last_used": "datetime",
        "updated_at": "datetime",
    }
}
```

#### relationships (Phase 3)

```python
{
    "vectors": None,
    "payload_schema": {
        "source_chunk_id": "keyword",
        "target_chunk_id": "keyword",
        "relationship_type": "keyword",
        "confidence": "float",
        "created_at": "datetime",
    }
}
```

#### decisions (Phase 3)

```python
{
    "vectors": {"size": 1536, "distance": "Cosine"},
    "payload_schema": {
        "domain": "keyword",
        "decision_date": "datetime",
        "tags": "keyword[]",
    }
}
```

---

## 9. Configuration

### 9.1 Environment Variables

```bash
# === EXISTING ===
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
CHROMADB_PATH=./data/chromadb

# === PHASE 1 ===
CRAWL4AI_HEADLESS=true
CRAWL4AI_RATE_LIMIT_RPS=2
WEB_ACQUISITION_MAX_PAGES=10
WEB_ACQUISITION_RELEVANCE_THRESHOLD=0.6
OFFLINE_MODE_ENABLED=true
OFFLINE_SYNC_INTERVAL_MINUTES=15

# === PHASE 2b ===
FEEDBACK_IMPLICIT_TRACKING=true
FEEDBACK_PROMPT_ON_COMPLETION=true
SCORE_SEARCH_BOOST_ENABLED=true
SCORE_SEMANTIC_WEIGHT=0.7
SCORE_EFFECTIVENESS_WEIGHT=0.3

# === PHASE 3 ===
SCORE_PROPAGATION_ENABLED=true
STALENESS_DECAY_ENABLED=true
```

### 9.2 Configuration Schema

```python
from pydantic import BaseModel

class KnowledgeConfig(BaseModel):
    """Root configuration."""
    
    # API
    openai_api_key: str
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    chromadb_path: str = "./data/chromadb"
    
    # Web Acquisition
    crawl4ai_headless: bool = True
    crawl4ai_rate_limit_rps: float = 2.0
    web_acquisition_max_pages: int = 10
    web_acquisition_relevance_threshold: float = 0.6
    
    # Offline
    offline_mode_enabled: bool = True
    offline_sync_interval_minutes: int = 15
    
    # Feedback
    feedback_implicit_tracking: bool = True
    feedback_prompt_on_completion: bool = True
    
    # Scoring
    score_search_boost_enabled: bool = True
    score_semantic_weight: float = 0.7
    score_effectiveness_weight: float = 0.3
    score_propagation_enabled: bool = True
    staleness_decay_enabled: bool = True
```

---

## 10. Testing Strategy

### 10.1 Test Structure

```
tests/
├── unit/
│   ├── test_models/
│   │   ├── test_chunk.py
│   │   ├── test_project.py
│   │   ├── test_feedback.py
│   │   └── test_score.py
│   ├── test_scoring/
│   │   ├── test_simple_scorer.py
│   │   ├── test_multi_factor_scorer.py
│   │   └── test_propagator.py
│   └── test_capture/
│       └── test_project_capture.py
│
├── integration/
│   ├── test_learning_loop.py
│   ├── test_score_boosted_search.py
│   └── test_feedback_to_score.py
│
├── e2e/
│   ├── test_planning_workflow.py
│   └── test_capture_feedback_loop.py
│
└── evaluation/
    ├── test_score_prediction.py
    └── test_recommendation_quality.py
```

### 10.2 Key Test Cases

#### Learning Loop Integration Test

```python
@pytest.mark.integration
async def test_learning_loop_improves_rankings():
    """
    Test that feedback improves future rankings.
    
    1. Create two templates with equal scores
    2. Use template A, provide positive feedback
    3. Use template B, provide negative feedback
    4. Search again
    5. Assert template A ranks higher
    """
    # Setup
    template_a = await create_template("Template A", score=0.5)
    template_b = await create_template("Template B", score=0.5)
    
    # Use and provide feedback
    project_a = await capture_project(source_template_id=template_a.id)
    await provide_feedback(project_a.id, rating=0.9, outcome="success")
    
    project_b = await capture_project(source_template_id=template_b.id)
    await provide_feedback(project_b.id, rating=0.3, outcome="failure")
    
    # Search
    results = await search_templates("project template")
    
    # Assert
    assert results[0].id == template_a.id
    assert results[0].effectiveness_score > results[1].effectiveness_score
```

#### State Machine Test

```python
@pytest.mark.unit
def test_project_lifecycle_transitions():
    """Test valid and invalid state transitions."""
    project = ProjectRecord(id="test", name="Test", description="Test")
    
    # Valid: planning -> active
    assert project.status == ProjectStatus.PLANNING
    project.activate()
    assert project.status == ProjectStatus.ACTIVE
    
    # Valid: active -> completed
    project.complete(outcome_summary="Done", success_rating=0.8)
    assert project.status == ProjectStatus.COMPLETED
    
    # Valid: completed -> active (reopen)
    project.reopen()
    assert project.status == ProjectStatus.ACTIVE
    
    # Invalid: active -> planning
    with pytest.raises(InvalidStateTransition):
        project._transition_to(ProjectStatus.PLANNING)
```

---

## 11. Appendices

### Appendix A: Authority Levels

| Level | Score | Examples |
|-------|-------|----------|
| Normative | 1.0 | IEEE 15288, ISO 9001, MIL-STD-461 |
| Authoritative | 0.85 | NASA-HDBK series, INCOSE Handbook |
| Reputable | 0.7 | Peer-reviewed papers, .gov/.edu |
| Informative | 0.5 | Technical blogs, tutorials |
| Unverified | 0.3 | General web content, forums |

### Appendix B: Score Interpretation

| Range | Level | Stars | Boost |
|-------|-------|-------|-------|
| 0.8-1.0 | Highly Effective | ⭐⭐⭐⭐⭐ | 1.5x |
| 0.6-0.8 | Effective | ⭐⭐⭐⭐ | 1.2x |
| 0.4-0.6 | Moderate | ⭐⭐⭐ | 1.0x |
| 0.2-0.4 | Limited | ⭐⭐ | 0.8x |
| 0.0-0.2 | Poor | ⭐ | 0.5x |

### Appendix C: Confidence Interpretation

| Range | Level | Display |
|-------|-------|---------|
| 0.8-1.0 | Well Established | "Based on 20+ data points" |
| 0.5-0.8 | Moderately Validated | "Based on 10-20 data points" |
| 0.2-0.5 | Limited Data | "Based on 3-10 data points" |
| 0.0-0.2 | Unvalidated | "Based on 0-3 data points" |

### Appendix D: Feedback Weights

| Tier | Type | Weight |
|------|------|--------|
| Detailed | Outcome with actuals | 1.0 |
| Quick | Thumbs/stars | 0.4 |
| Implicit | Usage only | 0.1 |

### Appendix E: Staleness Decay

| Days Since Activity | Penalty |
|---------------------|---------|
| < 30 | 0% |
| 30-90 | 5% |
| 90-180 | 10% |
| 180-365 | 20% |
| > 365 | 30% |

### Appendix F: Workflow Coverage Weights

| Workflow | Coverage | Authority | Recency | Confidence |
|----------|----------|-----------|---------|------------|
| RCCA | 20% | 40% | 10% | 30% |
| Trade Study | 30% | 30% | 20% | 20% |
| Exploration | 40% | 20% | 20% | 20% |
| Planning | 30% | 25% | 25% | 20% |
| Default | 25% | 25% | 25% | 25% |

### Appendix G: Project Status Transitions

| From | To | Method | Trigger |
|------|-----|--------|---------|
| PLANNING | ACTIVE | `activate()` | User starts execution |
| ACTIVE | COMPLETED | `complete()` | User finishes |
| ACTIVE | ABANDONED | `abandon()` | User stops |
| COMPLETED | ACTIVE | `reopen()` | User continues |

---

## Document End

**Specification Version:** 2.0.0-draft-r2  
**Status:** Ready for implementation planning  
**Total Tools:** 15  
**Total Collections:** 8  
**Estimated Implementation:** 12 weeks (3 phases)

**Key Innovations:**
1. Unified document + web ingestion
2. Acquisition loop with coverage assessment
3. Workflow-specific retrieval tools
4. Project capture and outcome tracking
5. Three-tier feedback collection
6. Score-boosted search rankings
7. Learning from experience over time
