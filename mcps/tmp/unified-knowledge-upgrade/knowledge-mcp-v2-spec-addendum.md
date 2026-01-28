# Knowledge-MCP v2 Specification Addendum

## Relational Layer & Multi-Tenancy Design

**Version:** 2.0.0-addendum-1  
**Date:** 2026-01-27  
**Status:** Draft for Review  
**Scope:** PostgreSQL integration, SQLAlchemy ORM, multi-tenancy architecture, migration path

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Evolution](#2-architecture-evolution)
3. [PostgreSQL Schema Design](#3-postgresql-schema-design)
4. [SQLAlchemy Models](#4-sqlalchemy-models)
5. [Multi-Tenancy Design](#5-multi-tenancy-design)
6. [Repository Pattern](#6-repository-pattern)
7. [Migration Path](#7-migration-path)
8. [Configuration](#8-configuration)
9. [Testing Considerations](#9-testing-considerations)
10. [Appendices](#10-appendices)

---

## 1. Overview

### 1.1 Purpose

This addendum extends the Knowledge-MCP v2 specification to include:

1. **PostgreSQL integration** for relational data (projects, feedback, scores, relationships)
2. **SQLAlchemy ORM** for Python database access
3. **Multi-tenancy architecture** with Row-Level Security (RLS)
4. **Migration path** from hybrid (v2) to consolidated pgvector (v3)

### 1.2 Rationale

The v2 specification stores relational data (projects, feedback, scores) in vector databases, which:

| Problem | Impact |
|---------|--------|
| No JOINs | Can't efficiently query related data |
| No foreign keys | No referential integrity |
| No transactions | Risk of inconsistent state |
| No aggregations | Can't compute analytics efficiently |
| No recursive queries | Graph traversal is slow |
| No multi-tenancy | Can't isolate user data |

A relational database solves these while preserving vector search capabilities.

### 1.3 Key Decisions

| Decision | Rationale |
|----------|-----------|
| **PostgreSQL** | Mature, pgvector extension, RLS support |
| **SQLAlchemy 2.0** | Modern async support, type hints |
| **Hybrid architecture (v2)** | Minimize disruption, gradual migration |
| **pgvector consolidation (v3)** | Simplify to single database |
| **RLS for multi-tenancy** | Database-enforced isolation |

---

## 2. Architecture Evolution

### 2.1 Current Architecture (v1)

```
┌─────────────────────────────────┐
│         v1 ARCHITECTURE         │
└─────────────────────────────────┘

        ┌─────────────────┐
        │   MCP Server    │
        └────────┬────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │   Qdrant / ChromaDB     │
    │                         │
    │   • chunks (vectors)    │
    │   • All metadata        │
    └─────────────────────────┘

Limitations:
  • Single-user only
  • No relational queries
  • No transactions
  • No referential integrity
```

### 2.2 v2 Hybrid Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                      v2 HYBRID ARCHITECTURE                               │
└───────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │   MCP Server    │
                         │   (Python)      │
                         └────────┬────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
        ┌─────────────────┐              ┌─────────────────┐
        │   PostgreSQL    │              │     Qdrant      │
        │                 │              │                 │
        │ RELATIONAL DATA │              │  VECTOR DATA    │
        │                 │              │                 │
        │ • organizations │              │ • chunks        │
        │ • users         │              │   (embeddings)  │
        │ • projects      │              │ • patterns      │
        │ • templates     │              │   (embeddings)  │
        │ • feedback      │              │ • templates     │
        │ • scores        │              │   (embeddings)  │
        │ • relationships │              │                 │
        │ • decisions     │              │                 │
        │                 │              │                 │
        │ SQLAlchemy ORM  │              │ Existing client │
        │ RLS policies    │              │                 │
        └─────────────────┘              └─────────────────┘

Benefits:
  ✓ Multi-tenancy with RLS
  ✓ Full relational queries
  ✓ ACID transactions
  ✓ Referential integrity
  ✓ Preserved vector search performance
  
Trade-offs:
  • Two databases to manage
  • Sync required for denormalized data
```

### 2.3 v3 Consolidated Architecture (Future)

```
┌──────────────────────────────────┐
│    v3 CONSOLIDATED ARCHITECTURE  │
└──────────────────────────────────┘

          ┌─────────────────┐
          │   MCP Server    │
          │   (Python)      │
          └────────┬────────┘
                   │
                   ▼
     ┌─────────────────────────┐
     │      PostgreSQL         │
     │      + pgvector         │
     │                         │
     │  UNIFIED DATA LAYER     │
     │                         │
     │  ┌───────────────────┐  │
     │  │  Vector Tables    │  │
     │  │  • chunks         │  │
     │  │  • patterns       │  │
     │  │  • templates      │  │
     │  │  • projects       │  │
     │  │  • decisions      │  │
     │  └───────────────────┘  │
     │                         │
     │  ┌───────────────────┐  │
     │  │ Relational Tables │  │
     │  │  • organizations  │  │
     │  │  • users          │  │
     │  │  • feedback       │  │
     │  │  • scores         │  │
     │  │  • relationships  │  │
     │  └───────────────────┘  │
     │                         │
     │  • RLS policies         │
     │  • Hybrid queries       │
     │  • Single transaction   │
     │                         │
     │  SQLAlchemy + pgvector  │
     └─────────────────────────┘

Benefits:
  ✓ Single database
  ✓ Hybrid queries (vector + relational in one)
  ✓ Simpler operations
  ✓ Full ACID across all data
  ✓ Unified backup/restore
```

---

## 3. PostgreSQL Schema Design

### 3.1 Schema Overview

```sql
-- Schema organization
-- 
-- public schema: shared tables (organizations, users)
-- tenant schemas: per-organization data (optional for extreme isolation)
-- 
-- For v2, we use single schema with RLS for isolation

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";  -- For v3 migration

-- Enums
CREATE TYPE project_status AS ENUM ('planning', 'active', 'completed', 'abandoned');
CREATE TYPE project_visibility AS ENUM ('personal', 'team', 'organization');
CREATE TYPE feedback_type AS ENUM (
    'helpful', 'not_helpful', 'rating',
    'tasks_complete', 'tasks_incomplete',
    'estimates_accurate', 'estimates_inaccurate',
    'risks_identified', 'risks_missed',
    'used_as_is', 'needed_modification',
    'project_success', 'project_partial', 'project_failure',
    'retrieved', 'used'
);
CREATE TYPE feedback_tier AS ENUM ('implicit', 'quick', 'detailed');
CREATE TYPE relationship_type AS ENUM (
    'references', 'supersedes', 'implements',
    'supports', 'contradicts', 'qualifies',
    'causes', 'prevents', 'indicates',
    'alternative_to', 'preferred_over'
);
```

### 3.2 Core Tables

```sql
-- ============================================================================
-- ORGANIZATION & USER TABLES
-- ============================================================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,  -- URL-friendly identifier
    settings JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    email TEXT NOT NULL,
    name TEXT,
    role TEXT NOT NULL DEFAULT 'member',  -- 'owner', 'admin', 'member', 'viewer'
    settings JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_active_at TIMESTAMPTZ,
    
    UNIQUE(organization_id, email)
);

CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================================
-- PROJECT TABLES
-- ============================================================================

CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Core
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT NOT NULL,
    domain TEXT,
    tags TEXT[] DEFAULT '{}',
    visibility project_visibility DEFAULT 'personal',
    
    -- Template content
    task_template JSONB DEFAULT '[]',
    phase_template TEXT[] DEFAULT '{}',
    checkpoint_template TEXT[] DEFAULT '{}',
    risk_template JSONB DEFAULT '[]',
    
    -- Guidance
    typical_duration_range TEXT,
    typical_task_count INTEGER,
    complexity_level TEXT,
    prerequisites TEXT[] DEFAULT '{}',
    applicable_when TEXT[] DEFAULT '{}',
    not_applicable_when TEXT[] DEFAULT '{}',
    
    -- Provenance
    abstracted_from_project_ids UUID[] DEFAULT '{}',
    created_manually BOOLEAN DEFAULT false,
    
    -- Vector (for v3 migration, nullable for v2)
    embedding vector(1536),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_templates_organization ON templates(organization_id);
CREATE INDEX idx_templates_project_type ON templates(project_type);
CREATE INDEX idx_templates_visibility ON templates(visibility);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Core
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT NOT NULL,
    domain TEXT,
    tags TEXT[] DEFAULT '{}',
    visibility project_visibility DEFAULT 'personal',
    
    -- Lifecycle
    status project_status DEFAULT 'planning',
    status_history JSONB DEFAULT '[]',
    
    -- Structure
    tasks JSONB DEFAULT '[]',
    phases TEXT[] DEFAULT '{}',
    checkpoints TEXT[] DEFAULT '{}',
    context_factors JSONB DEFAULT '{}',
    
    -- Planning artifacts
    identified_risks JSONB DEFAULT '[]',
    identified_dependencies JSONB DEFAULT '[]',
    constraints_applied JSONB DEFAULT '[]',
    
    -- Estimates
    estimated_duration_days REAL,
    estimated_effort_hours REAL,
    
    -- Actuals
    actual_duration_days REAL,
    actual_effort_hours REAL,
    start_date DATE,
    end_date DATE,
    
    -- Outcome
    outcome_summary TEXT,
    success_rating REAL CHECK (success_rating >= 0 AND success_rating <= 1),
    lessons_learned TEXT[] DEFAULT '{}',
    what_worked TEXT[] DEFAULT '{}',
    what_didnt_work TEXT[] DEFAULT '{}',
    
    -- Source template
    source_template_id UUID REFERENCES templates(id) ON DELETE SET NULL,
    template_modifications TEXT[] DEFAULT '{}',
    
    -- Vector (for v3 migration)
    embedding vector(1536),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_projects_organization ON projects(organization_id);
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_project_type ON projects(project_type);
CREATE INDEX idx_projects_source_template ON projects(source_template_id);

-- ============================================================================
-- FEEDBACK & SCORING TABLES
-- ============================================================================

CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Target
    artifact_id UUID NOT NULL,
    artifact_type TEXT NOT NULL,  -- 'template', 'pattern', 'project', 'chunk', 'decision'
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Feedback
    feedback_type feedback_type NOT NULL,
    feedback_tier feedback_tier NOT NULL,
    rating REAL CHECK (rating >= 0 AND rating <= 1),
    comment TEXT,
    specific_data JSONB DEFAULT '{}',
    
    -- Corrections
    corrections TEXT[] DEFAULT '{}',
    suggested_improvements TEXT[] DEFAULT '{}',
    
    -- Metadata
    feedback_source TEXT DEFAULT 'user',
    usage_context TEXT,
    
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_feedback_organization ON feedback(organization_id);
CREATE INDEX idx_feedback_artifact ON feedback(artifact_id, artifact_type);
CREATE INDEX idx_feedback_project ON feedback(project_id);
CREATE INDEX idx_feedback_created ON feedback(created_at DESC);

CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Target (unique per artifact)
    artifact_id UUID NOT NULL,
    artifact_type TEXT NOT NULL,
    
    -- Simple score (Phase 2b)
    score REAL DEFAULT 0.5 CHECK (score >= 0 AND score <= 1),
    confidence REAL DEFAULT 0.0 CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Multi-factor (Phase 3)
    relevance_score REAL DEFAULT 0.5,
    relevance_samples INTEGER DEFAULT 0,
    effectiveness_score REAL DEFAULT 0.5,
    effectiveness_samples INTEGER DEFAULT 0,
    accuracy_score REAL DEFAULT 0.5,
    accuracy_samples INTEGER DEFAULT 0,
    completeness_score REAL DEFAULT 0.5,
    completeness_samples INTEGER DEFAULT 0,
    user_rating_score REAL DEFAULT 0.5,
    user_rating_samples INTEGER DEFAULT 0,
    
    -- Usage tracking
    times_retrieved INTEGER DEFAULT 0,
    times_used INTEGER DEFAULT 0,
    positive_feedback INTEGER DEFAULT 0,
    negative_feedback INTEGER DEFAULT 0,
    
    -- Staleness
    staleness_penalty REAL DEFAULT 0.0,
    last_retrieved TIMESTAMPTZ,
    last_used TIMESTAMPTZ,
    last_feedback TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    UNIQUE(artifact_id, artifact_type)
);

CREATE INDEX idx_scores_artifact ON scores(artifact_id, artifact_type);
CREATE INDEX idx_scores_score ON scores(score DESC);

-- ============================================================================
-- RELATIONSHIP TABLE (GRAPH EDGES)
-- ============================================================================

CREATE TABLE chunk_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Edge
    source_chunk_id UUID NOT NULL,  -- References chunk in Qdrant (v2) or chunks table (v3)
    target_chunk_id UUID NOT NULL,
    relationship_type relationship_type NOT NULL,
    
    -- Metadata
    confidence REAL DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    bidirectional BOOLEAN DEFAULT false,
    context TEXT,
    created_by TEXT DEFAULT 'manual',
    evidence_chunk_ids UUID[] DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT now(),
    
    -- Prevent duplicate relationships
    UNIQUE(source_chunk_id, target_chunk_id, relationship_type)
);

CREATE INDEX idx_relationships_organization ON chunk_relationships(organization_id);
CREATE INDEX idx_relationships_source ON chunk_relationships(source_chunk_id);
CREATE INDEX idx_relationships_target ON chunk_relationships(target_chunk_id);
CREATE INDEX idx_relationships_type ON chunk_relationships(relationship_type);

-- ============================================================================
-- DECISION RECORDS TABLE
-- ============================================================================

CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Core
    title TEXT NOT NULL,
    decision_date DATE,
    domain TEXT,
    tags TEXT[] DEFAULT '{}',
    
    -- Context
    problem_statement TEXT,
    constraints TEXT[] DEFAULT '{}',
    assumptions TEXT[] DEFAULT '{}',
    
    -- Evaluation
    criteria JSONB DEFAULT '[]',
    alternatives JSONB DEFAULT '[]',
    
    -- Decision
    selected_alternative_id TEXT,
    rationale TEXT,
    dissenting_opinions TEXT[] DEFAULT '{}',
    
    -- Outcome
    outcome TEXT,
    lessons_learned TEXT[] DEFAULT '{}',
    
    -- Vector (for similarity search)
    embedding vector(1536),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_decisions_organization ON decisions(organization_id);
CREATE INDEX idx_decisions_domain ON decisions(domain);
CREATE INDEX idx_decisions_date ON decisions(decision_date DESC);

-- ============================================================================
-- PATTERNS TABLE (for v3 when migrated from Qdrant)
-- ============================================================================

CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,  -- NULL = global
    
    -- Core
    name TEXT NOT NULL,
    pattern_type TEXT NOT NULL,  -- 'antipattern', 'best_practice', 'failure_mode', 'design_pattern'
    domain TEXT NOT NULL,
    
    -- Description
    description TEXT NOT NULL,
    indicators TEXT[] DEFAULT '{}',
    consequences TEXT[] DEFAULT '{}',
    
    -- For antipatterns
    root_causes TEXT[] DEFAULT '{}',
    mitigations TEXT[] DEFAULT '{}',
    
    -- For best practices
    benefits TEXT[] DEFAULT '{}',
    prerequisites TEXT[] DEFAULT '{}',
    
    -- Matching
    keywords TEXT[] DEFAULT '{}',
    
    -- Source
    source_standard TEXT,
    source_clause TEXT,
    example_chunk_ids UUID[] DEFAULT '{}',
    
    -- Severity
    severity TEXT DEFAULT 'medium',
    
    -- Vector
    embedding vector(1536),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_patterns_organization ON patterns(organization_id);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_domain ON patterns(domain);
CREATE INDEX idx_patterns_severity ON patterns(severity);

-- ============================================================================
-- CHUNKS TABLE (for v3 when migrated from Qdrant)
-- ============================================================================

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Content
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    token_count INTEGER,
    
    -- Document reference
    document_id TEXT NOT NULL,
    document_title TEXT,
    document_type TEXT,
    
    -- Hierarchy
    section_hierarchy TEXT[] DEFAULT '{}',
    section_title TEXT,
    parent_chunk_id UUID REFERENCES chunks(id) ON DELETE SET NULL,
    
    -- Classification
    chunk_type TEXT DEFAULT 'content',
    normative BOOLEAN,
    
    -- Location
    page_numbers INTEGER[] DEFAULT '{}',
    clause_number TEXT,
    char_start INTEGER,
    char_end INTEGER,
    
    -- Source
    source_type TEXT DEFAULT 'document',
    source_url TEXT,
    source_domain TEXT,
    crawled_at TIMESTAMPTZ,
    
    -- Quality
    authority_score REAL DEFAULT 0.5,
    relevance_score REAL,
    
    -- References
    references TEXT[] DEFAULT '{}',
    referenced_by TEXT[] DEFAULT '{}',
    
    -- Vector
    embedding vector(1536),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chunks_organization ON chunks(organization_id);
CREATE INDEX idx_chunks_document ON chunks(document_id);
CREATE INDEX idx_chunks_document_type ON chunks(document_type);
CREATE INDEX idx_chunks_source_type ON chunks(source_type);
CREATE INDEX idx_chunks_content_hash ON chunks(content_hash);
CREATE INDEX idx_chunks_clause ON chunks(clause_number);

-- Vector index (for v3)
CREATE INDEX idx_chunks_embedding ON chunks 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- SOURCES TABLE (document/web source tracking)
-- ============================================================================

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Identity
    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    document_type TEXT,
    source_path TEXT,
    
    -- Versioning
    version TEXT,
    publication_date DATE,
    standard_id TEXT,
    
    -- Source type
    source_type TEXT DEFAULT 'document',
    source_url TEXT,
    source_domain TEXT,
    
    -- Authority
    authority_level TEXT DEFAULT 'unverified',
    authority_score REAL DEFAULT 0.5,
    
    -- Freshness
    crawled_at TIMESTAMPTZ,
    last_verified_at TIMESTAMPTZ,
    content_hash TEXT,
    
    -- Processing
    chunk_count INTEGER DEFAULT 0,
    processing_status TEXT DEFAULT 'pending',
    processing_error TEXT,
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    UNIQUE(organization_id, document_id)
);

CREATE INDEX idx_sources_organization ON sources(organization_id);
CREATE INDEX idx_sources_document_type ON sources(document_type);
CREATE INDEX idx_sources_source_type ON sources(source_type);
```

### 3.3 Utility Functions & Triggers

```sql
-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_scores_updated_at
    BEFORE UPDATE ON scores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_decisions_updated_at
    BEFORE UPDATE ON decisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- SCORE UPDATE TRIGGER
-- ============================================================================

-- Automatically update scores when feedback is inserted
CREATE OR REPLACE FUNCTION update_score_from_feedback()
RETURNS TRIGGER AS $$
DECLARE
    current_score RECORD;
    new_score REAL;
    new_confidence REAL;
    weight REAL;
BEGIN
    -- Get current score
    SELECT * INTO current_score
    FROM scores
    WHERE artifact_id = NEW.artifact_id AND artifact_type = NEW.artifact_type;
    
    -- Determine weight based on feedback tier
    weight := CASE NEW.feedback_tier
        WHEN 'detailed' THEN 1.0
        WHEN 'quick' THEN 0.4
        WHEN 'implicit' THEN 0.1
    END;
    
    IF current_score IS NULL THEN
        -- Create new score record
        INSERT INTO scores (artifact_id, artifact_type, score, confidence)
        VALUES (
            NEW.artifact_id,
            NEW.artifact_type,
            COALESCE(NEW.rating, 0.5),
            weight / 10.0
        );
    ELSE
        -- Update existing score with weighted average
        IF NEW.rating IS NOT NULL THEN
            new_score := (current_score.score * (1 - weight * 0.1) + NEW.rating * weight * 0.1);
        ELSE
            new_score := current_score.score;
        END IF;
        
        -- Update feedback counts
        UPDATE scores
        SET 
            score = new_score,
            confidence = LEAST(1.0, confidence + weight / 10.0),
            positive_feedback = positive_feedback + CASE 
                WHEN NEW.feedback_type IN ('helpful', 'project_success', 'tasks_complete', 'estimates_accurate', 'risks_identified', 'used_as_is')
                THEN 1 ELSE 0 END,
            negative_feedback = negative_feedback + CASE
                WHEN NEW.feedback_type IN ('not_helpful', 'project_failure', 'tasks_incomplete', 'estimates_inaccurate', 'risks_missed')
                THEN 1 ELSE 0 END,
            times_used = times_used + CASE WHEN NEW.feedback_type = 'used' THEN 1 ELSE 0 END,
            times_retrieved = times_retrieved + CASE WHEN NEW.feedback_type = 'retrieved' THEN 1 ELSE 0 END,
            last_feedback = now()
        WHERE artifact_id = NEW.artifact_id AND artifact_type = NEW.artifact_type;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_score_from_feedback
    AFTER INSERT ON feedback
    FOR EACH ROW EXECUTE FUNCTION update_score_from_feedback();

-- ============================================================================
-- PROJECT STATUS TRANSITION VALIDATION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_project_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate status transitions
    IF OLD.status = 'planning' AND NEW.status NOT IN ('active', 'planning') THEN
        RAISE EXCEPTION 'Invalid transition from planning to %', NEW.status;
    END IF;
    
    IF OLD.status = 'active' AND NEW.status NOT IN ('completed', 'abandoned', 'active') THEN
        RAISE EXCEPTION 'Invalid transition from active to %', NEW.status;
    END IF;
    
    IF OLD.status = 'completed' AND NEW.status NOT IN ('active', 'completed') THEN
        RAISE EXCEPTION 'Invalid transition from completed to %', NEW.status;
    END IF;
    
    IF OLD.status = 'abandoned' THEN
        RAISE EXCEPTION 'Cannot transition from abandoned status';
    END IF;
    
    -- Record status change in history
    IF OLD.status != NEW.status THEN
        NEW.status_history = OLD.status_history || jsonb_build_object(
            'from_status', OLD.status,
            'to_status', NEW.status,
            'timestamp', now()
        );
        
        -- Set timestamps
        IF NEW.status = 'active' AND OLD.status = 'planning' THEN
            NEW.start_date = CURRENT_DATE;
        END IF;
        
        IF NEW.status IN ('completed', 'abandoned') THEN
            NEW.end_date = CURRENT_DATE;
            IF NEW.status = 'completed' THEN
                NEW.completed_at = now();
            END IF;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_project_status
    BEFORE UPDATE ON projects
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION validate_project_status_transition();
```

---

## 4. SQLAlchemy Models

### 4.1 Base Configuration

```python
# src/knowledge_mcp/db/base.py

from datetime import datetime, UTC
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import MetaData, create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all models."""
    
    metadata = metadata
    
    # Common columns
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        server_default=func.now()
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class TimestampMixin:
    """Mixin for updated_at timestamp."""
    
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC)
    )


# Database connection
async def get_engine(database_url: str):
    """Create async engine."""
    return create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )


async def get_session_maker(engine) -> async_sessionmaker[AsyncSession]:
    """Create session maker."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

### 4.2 Organization & User Models

```python
# src/knowledge_mcp/db/models/organization.py

from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project, Template
    from .feedback import Feedback


class Organization(Base, TimestampMixin):
    """Organization (tenant) model."""
    
    __tablename__ = "organizations"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Relationships
    users: Mapped[list["User"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    templates: Mapped[list["Template"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="member")
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_active_at: Mapped[datetime | None] = mapped_column()
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="users")
    
    __table_args__ = (
        # Unique email per organization
        {"unique_together": ("organization_id", "email")},
    )
```

### 4.3 Project Models

```python
# src/knowledge_mcp/db/models/project.py

from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text, Float, Integer, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from ..base import Base, TimestampMixin

if TYPE_CHECKING:
    from .organization import Organization, User
    from .feedback import Feedback
    from .score import Score


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ProjectVisibility(str, Enum):
    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"


class Template(Base, TimestampMixin):
    """Reusable project template."""
    
    __tablename__ = "templates"
    
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    owner_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    
    # Core
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    project_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    domain: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    visibility: Mapped[ProjectVisibility] = mapped_column(
        SQLEnum(ProjectVisibility),
        default=ProjectVisibility.PERSONAL
    )
    
    # Template content
    task_template: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    phase_template: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    checkpoint_template: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    risk_template: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    
    # Guidance
    typical_duration_range: Mapped[str | None] = mapped_column(String(50))
    typical_task_count: Mapped[int | None] = mapped_column(Integer)
    complexity_level: Mapped[str | None] = mapped_column(String(20))
    prerequisites: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    applicable_when: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    not_applicable_when: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Provenance
    abstracted_from_project_ids: Mapped[list[UUID]] = mapped_column(
        ARRAY(UUID), default=list
    )
    created_manually: Mapped[bool] = mapped_column(default=False)
    
    # Vector embedding
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="templates")
    owner: Mapped["User | None"] = relationship()
    projects: Mapped[list["Project"]] = relationship(back_populates="source_template")


class Project(Base, TimestampMixin):
    """Captured project structure with outcomes."""
    
    __tablename__ = "projects"
    
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    owner_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True
    )
    
    # Core
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    project_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    domain: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    visibility: Mapped[ProjectVisibility] = mapped_column(
        SQLEnum(ProjectVisibility),
        default=ProjectVisibility.PERSONAL
    )
    
    # Lifecycle
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.PLANNING,
        index=True
    )
    status_history: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    
    # Structure
    tasks: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    phases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    checkpoints: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    context_factors: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Planning artifacts
    identified_risks: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    identified_dependencies: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    constraints_applied: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    
    # Estimates
    estimated_duration_days: Mapped[float | None] = mapped_column(Float)
    estimated_effort_hours: Mapped[float | None] = mapped_column(Float)
    
    # Actuals
    actual_duration_days: Mapped[float | None] = mapped_column(Float)
    actual_effort_hours: Mapped[float | None] = mapped_column(Float)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    
    # Outcome
    outcome_summary: Mapped[str | None] = mapped_column(Text)
    success_rating: Mapped[float | None] = mapped_column(Float)
    lessons_learned: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    what_worked: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    what_didnt_work: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Source template
    source_template_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"),
        index=True
    )
    template_modifications: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Vector embedding
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    
    # Completion timestamp
    completed_at: Mapped[datetime | None] = mapped_column()
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="projects")
    owner: Mapped["User | None"] = relationship()
    source_template: Mapped["Template | None"] = relationship(back_populates="projects")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="project")
    
    # === LIFECYCLE METHODS ===
    
    def activate(self) -> None:
        """Transition from PLANNING to ACTIVE."""
        if self.status != ProjectStatus.PLANNING:
            raise InvalidStateTransition(f"Cannot activate from {self.status}")
        self.status = ProjectStatus.ACTIVE
        self.start_date = date.today()
        self._record_transition(ProjectStatus.PLANNING, ProjectStatus.ACTIVE)
    
    def complete(self, outcome_summary: str, success_rating: float) -> None:
        """Transition from ACTIVE to COMPLETED."""
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransition(f"Cannot complete from {self.status}")
        self.status = ProjectStatus.COMPLETED
        self.outcome_summary = outcome_summary
        self.success_rating = success_rating
        self.end_date = date.today()
        self.completed_at = datetime.now(UTC)
        self._record_transition(ProjectStatus.ACTIVE, ProjectStatus.COMPLETED)
    
    def abandon(self, reason: str = "") -> None:
        """Transition from ACTIVE to ABANDONED."""
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransition(f"Cannot abandon from {self.status}")
        self.status = ProjectStatus.ABANDONED
        self.end_date = date.today()
        self._record_transition(ProjectStatus.ACTIVE, ProjectStatus.ABANDONED, reason)
    
    def reopen(self) -> None:
        """Transition from COMPLETED back to ACTIVE."""
        if self.status != ProjectStatus.COMPLETED:
            raise InvalidStateTransition(f"Cannot reopen from {self.status}")
        self.status = ProjectStatus.ACTIVE
        self._record_transition(ProjectStatus.COMPLETED, ProjectStatus.ACTIVE)
    
    def _record_transition(
        self, 
        from_status: ProjectStatus, 
        to_status: ProjectStatus,
        reason: str = ""
    ) -> None:
        """Record status transition in history."""
        self.status_history = self.status_history + [{
            "from_status": from_status.value,
            "to_status": to_status.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        }]


class InvalidStateTransition(Exception):
    """Raised when an invalid project state transition is attempted."""
    pass
```

### 4.4 Feedback & Score Models

```python
# src/knowledge_mcp/db/models/feedback.py

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text, Float, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .organization import Organization, User
    from .project import Project


class FeedbackType(str, Enum):
    # Quick (Tier 2)
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    RATING = "rating"
    
    # Detailed (Tier 3)
    TASKS_COMPLETE = "tasks_complete"
    TASKS_INCOMPLETE = "tasks_incomplete"
    ESTIMATES_ACCURATE = "estimates_accurate"
    ESTIMATES_INACCURATE = "estimates_inaccurate"
    RISKS_IDENTIFIED = "risks_identified"
    RISKS_MISSED = "risks_missed"
    USED_AS_IS = "used_as_is"
    NEEDED_MODIFICATION = "needed_modification"
    PROJECT_SUCCESS = "project_success"
    PROJECT_PARTIAL = "project_partial"
    PROJECT_FAILURE = "project_failure"
    
    # Implicit (Tier 1)
    RETRIEVED = "retrieved"
    USED = "used"


class FeedbackTier(str, Enum):
    IMPLICIT = "implicit"
    QUICK = "quick"
    DETAILED = "detailed"


class Feedback(Base):
    """User feedback on artifacts."""
    
    __tablename__ = "feedback"
    
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    
    # Target
    artifact_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True
    )
    
    # Feedback
    feedback_type: Mapped[FeedbackType] = mapped_column(nullable=False)
    feedback_tier: Mapped[FeedbackTier] = mapped_column(nullable=False)
    rating: Mapped[float | None] = mapped_column(Float)
    comment: Mapped[str | None] = mapped_column(Text)
    specific_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Corrections
    corrections: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    suggested_improvements: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Metadata
    feedback_source: Mapped[str] = mapped_column(String(50), default="user")
    usage_context: Mapped[str | None] = mapped_column(Text)
    
    # Relationships
    organization: Mapped["Organization"] = relationship()
    user: Mapped["User | None"] = relationship()
    project: Mapped["Project | None"] = relationship(back_populates="feedback")


# src/knowledge_mcp/db/models/score.py

class Score(Base):
    """Effectiveness scores for artifacts."""
    
    __tablename__ = "scores"
    
    # Target (unique per artifact)
    artifact_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Simple score (Phase 2b)
    score: Mapped[float] = mapped_column(Float, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Multi-factor (Phase 3)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5)
    relevance_samples: Mapped[int] = mapped_column(Integer, default=0)
    effectiveness_score: Mapped[float] = mapped_column(Float, default=0.5)
    effectiveness_samples: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.5)
    accuracy_samples: Mapped[int] = mapped_column(Integer, default=0)
    completeness_score: Mapped[float] = mapped_column(Float, default=0.5)
    completeness_samples: Mapped[int] = mapped_column(Integer, default=0)
    user_rating_score: Mapped[float] = mapped_column(Float, default=0.5)
    user_rating_samples: Mapped[int] = mapped_column(Integer, default=0)
    
    # Usage tracking
    times_retrieved: Mapped[int] = mapped_column(Integer, default=0)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    positive_feedback: Mapped[int] = mapped_column(Integer, default=0)
    negative_feedback: Mapped[int] = mapped_column(Integer, default=0)
    
    # Staleness
    staleness_penalty: Mapped[float] = mapped_column(Float, default=0.0)
    last_retrieved: Mapped[datetime | None] = mapped_column()
    last_used: Mapped[datetime | None] = mapped_column()
    last_feedback: Mapped[datetime | None] = mapped_column()
    
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
    
    __table_args__ = (
        # Unique score per artifact
        {"unique_together": ("artifact_id", "artifact_type")},
    )
    
    def effective_score(self) -> float:
        """Score with staleness penalty applied."""
        return self.score * (1 - self.staleness_penalty)
```

---

## 5. Multi-Tenancy Design

### 5.1 Row-Level Security Policies

```sql
-- ============================================================================
-- ROW-LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunk_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE patterns ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- POLICY: Users can only see their organization's data
-- ============================================================================

-- Users table
CREATE POLICY users_organization_isolation ON users
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- Projects table with visibility rules
CREATE POLICY projects_organization_isolation ON projects
    USING (
        organization_id = current_setting('app.current_organization_id', true)::UUID
        AND (
            -- Organization-wide visibility
            visibility = 'organization'
            -- Team visibility (same org)
            OR visibility = 'team'
            -- Personal visibility (owner only)
            OR (visibility = 'personal' AND owner_id = current_setting('app.current_user_id', true)::UUID)
            -- Admins can see all in their org
            OR current_setting('app.current_user_role', true) IN ('admin', 'owner')
        )
    );

-- Templates table with visibility rules
CREATE POLICY templates_organization_isolation ON templates
    USING (
        organization_id = current_setting('app.current_organization_id', true)::UUID
        AND (
            visibility = 'organization'
            OR visibility = 'team'
            OR (visibility = 'personal' AND owner_id = current_setting('app.current_user_id', true)::UUID)
            OR current_setting('app.current_user_role', true) IN ('admin', 'owner')
        )
    );

-- Feedback table
CREATE POLICY feedback_organization_isolation ON feedback
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- Relationships table
CREATE POLICY relationships_organization_isolation ON chunk_relationships
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- Decisions table
CREATE POLICY decisions_organization_isolation ON decisions
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- Sources table
CREATE POLICY sources_organization_isolation ON sources
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- Chunks table (v3)
CREATE POLICY chunks_organization_isolation ON chunks
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- Patterns table (allow global patterns where organization_id IS NULL)
CREATE POLICY patterns_organization_isolation ON patterns
    USING (
        organization_id IS NULL  -- Global patterns
        OR organization_id = current_setting('app.current_organization_id', true)::UUID
    );

-- ============================================================================
-- INSERT POLICIES (for new records)
-- ============================================================================

CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::UUID);

CREATE POLICY projects_insert_policy ON projects
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::UUID);

CREATE POLICY templates_insert_policy ON templates
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::UUID);

CREATE POLICY feedback_insert_policy ON feedback
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- ============================================================================
-- UPDATE POLICIES
-- ============================================================================

CREATE POLICY projects_update_policy ON projects
    FOR UPDATE
    USING (
        organization_id = current_setting('app.current_organization_id', true)::UUID
        AND (
            owner_id = current_setting('app.current_user_id', true)::UUID
            OR current_setting('app.current_user_role', true) IN ('admin', 'owner')
        )
    );

CREATE POLICY templates_update_policy ON templates
    FOR UPDATE
    USING (
        organization_id = current_setting('app.current_organization_id', true)::UUID
        AND (
            owner_id = current_setting('app.current_user_id', true)::UUID
            OR current_setting('app.current_user_role', true) IN ('admin', 'owner')
        )
    );
```

### 5.2 Session Context Management

```python
# src/knowledge_mcp/db/context.py

from __future__ import annotations
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class TenantContext:
    """Current tenant context for RLS."""
    
    organization_id: UUID
    user_id: UUID
    user_role: str  # 'owner', 'admin', 'member', 'viewer'


class TenantSessionManager:
    """Manages database sessions with tenant context."""
    
    def __init__(self, session_maker):
        self._session_maker = session_maker
    
    @asynccontextmanager
    async def session(
        self, 
        context: TenantContext
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        Create a session with tenant context set for RLS.
        
        Usage:
            async with manager.session(context) as session:
                # All queries are automatically filtered by tenant
                projects = await session.execute(select(Project))
        """
        async with self._session_maker() as session:
            # Set RLS context variables
            await session.execute(
                text("SET LOCAL app.current_organization_id = :org_id"),
                {"org_id": str(context.organization_id)}
            )
            await session.execute(
                text("SET LOCAL app.current_user_id = :user_id"),
                {"user_id": str(context.user_id)}
            )
            await session.execute(
                text("SET LOCAL app.current_user_role = :role"),
                {"role": context.user_role}
            )
            
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# src/knowledge_mcp/db/middleware.py

class DatabaseMiddleware:
    """
    Middleware to inject tenant context into requests.
    
    For MCP server, context comes from authentication/session.
    """
    
    def __init__(self, session_manager: TenantSessionManager):
        self._session_manager = session_manager
    
    async def get_session(
        self,
        organization_id: UUID,
        user_id: UUID,
        user_role: str,
    ) -> AsyncGenerator[AsyncSession, None]:
        """Get a session with tenant context."""
        context = TenantContext(
            organization_id=organization_id,
            user_id=user_id,
            user_role=user_role,
        )
        async with self._session_manager.session(context) as session:
            yield session
```

### 5.3 Tenant-Aware Repositories

```python
# src/knowledge_mcp/db/repositories/base.py

from __future__ import annotations
from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository with tenant-aware operations."""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self._session = session
        self._model = model
    
    async def get_by_id(self, id: UUID) -> T | None:
        """Get by ID (RLS automatically filters by tenant)."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Get all (filtered by tenant via RLS)."""
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
    
    async def create(self, entity: T) -> T:
        """Create (tenant ID should be set on entity)."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def update(self, entity: T) -> T:
        """Update (RLS ensures tenant isolation)."""
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def delete(self, id: UUID) -> bool:
        """Delete by ID (RLS ensures tenant isolation)."""
        result = await self._session.execute(
            delete(self._model).where(self._model.id == id)
        )
        return result.rowcount > 0
```

---

## 6. Repository Pattern

### 6.1 Project Repository

```python
# src/knowledge_mcp/db/repositories/project.py

from __future__ import annotations
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.project import Project, Template, ProjectStatus, ProjectVisibility
from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for project operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)
    
    async def get_by_status(
        self, 
        status: ProjectStatus,
        limit: int = 100,
    ) -> Sequence[Project]:
        """Get projects by status."""
        result = await self._session.execute(
            select(Project)
            .where(Project.status == status)
            .order_by(Project.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_type(
        self,
        project_type: str,
        limit: int = 100,
    ) -> Sequence[Project]:
        """Get projects by type."""
        result = await self._session.execute(
            select(Project)
            .where(Project.project_type == project_type)
            .order_by(Project.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_with_template(self, id: UUID) -> Project | None:
        """Get project with source template loaded."""
        result = await self._session.execute(
            select(Project)
            .options(selectinload(Project.source_template))
            .where(Project.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_derived_from_template(
        self,
        template_id: UUID,
        limit: int = 100,
    ) -> Sequence[Project]:
        """Get all projects derived from a template."""
        result = await self._session.execute(
            select(Project)
            .where(Project.source_template_id == template_id)
            .order_by(Project.completed_at.desc().nullslast())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> Sequence[tuple[Project, float]]:
        """
        Search for similar projects by embedding.
        
        Returns projects with similarity scores.
        """
        from pgvector.sqlalchemy import Vector
        
        # Cosine similarity search
        result = await self._session.execute(
            select(
                Project,
                (1 - Project.embedding.cosine_distance(embedding)).label("similarity")
            )
            .where(Project.embedding.isnot(None))
            .where((1 - Project.embedding.cosine_distance(embedding)) >= min_similarity)
            .order_by(Project.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return result.all()


class TemplateRepository(BaseRepository[Template]):
    """Repository for template operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Template)
    
    async def get_by_type(
        self,
        project_type: str,
        limit: int = 100,
    ) -> Sequence[Template]:
        """Get templates by project type."""
        result = await self._session.execute(
            select(Template)
            .where(Template.project_type == project_type)
            .order_by(Template.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 10,
    ) -> Sequence[tuple[Template, float]]:
        """Search for similar templates by embedding."""
        result = await self._session.execute(
            select(
                Template,
                (1 - Template.embedding.cosine_distance(embedding)).label("similarity")
            )
            .where(Template.embedding.isnot(None))
            .order_by(Template.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return result.all()
    
    async def get_with_usage_stats(
        self,
        template_id: UUID,
    ) -> dict:
        """Get template with usage statistics."""
        template = await self.get_by_id(template_id)
        if not template:
            return None
        
        # Count derived projects
        from sqlalchemy import func
        
        project_stats = await self._session.execute(
            select(
                func.count(Project.id).label("total_projects"),
                func.avg(Project.success_rating).label("avg_success_rating"),
                func.count(Project.id).filter(Project.status == ProjectStatus.COMPLETED).label("completed_count"),
            )
            .where(Project.source_template_id == template_id)
        )
        stats = project_stats.one()
        
        return {
            "template": template,
            "total_projects": stats.total_projects or 0,
            "avg_success_rating": float(stats.avg_success_rating or 0),
            "completed_count": stats.completed_count or 0,
        }
```

### 6.2 Feedback & Score Repository

```python
# src/knowledge_mcp/db/repositories/feedback.py

from __future__ import annotations
from datetime import datetime, timedelta, UTC
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.feedback import Feedback, FeedbackType, FeedbackTier
from ..models.score import Score
from .base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    """Repository for feedback operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Feedback)
    
    async def get_for_artifact(
        self,
        artifact_id: UUID,
        artifact_type: str,
        limit: int = 100,
    ) -> Sequence[Feedback]:
        """Get all feedback for an artifact."""
        result = await self._session.execute(
            select(Feedback)
            .where(and_(
                Feedback.artifact_id == artifact_id,
                Feedback.artifact_type == artifact_type,
            ))
            .order_by(Feedback.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent(
        self,
        days: int = 30,
        limit: int = 100,
    ) -> Sequence[Feedback]:
        """Get recent feedback."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        result = await self._session.execute(
            select(Feedback)
            .where(Feedback.created_at >= cutoff)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_aggregated_stats(
        self,
        artifact_id: UUID,
        artifact_type: str,
    ) -> dict:
        """Get aggregated feedback statistics."""
        result = await self._session.execute(
            select(
                func.count(Feedback.id).label("total_count"),
                func.avg(Feedback.rating).label("avg_rating"),
                func.count(Feedback.id).filter(
                    Feedback.feedback_type.in_([
                        FeedbackType.HELPFUL,
                        FeedbackType.PROJECT_SUCCESS,
                    ])
                ).label("positive_count"),
                func.count(Feedback.id).filter(
                    Feedback.feedback_type.in_([
                        FeedbackType.NOT_HELPFUL,
                        FeedbackType.PROJECT_FAILURE,
                    ])
                ).label("negative_count"),
            )
            .where(and_(
                Feedback.artifact_id == artifact_id,
                Feedback.artifact_type == artifact_type,
            ))
        )
        stats = result.one()
        
        return {
            "total_count": stats.total_count or 0,
            "avg_rating": float(stats.avg_rating or 0.5),
            "positive_count": stats.positive_count or 0,
            "negative_count": stats.negative_count or 0,
        }


class ScoreRepository(BaseRepository[Score]):
    """Repository for score operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Score)
    
    async def get_for_artifact(
        self,
        artifact_id: UUID,
        artifact_type: str,
    ) -> Score | None:
        """Get score for an artifact."""
        result = await self._session.execute(
            select(Score)
            .where(and_(
                Score.artifact_id == artifact_id,
                Score.artifact_type == artifact_type,
            ))
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(
        self,
        artifact_id: UUID,
        artifact_type: str,
    ) -> Score:
        """Get existing score or create new one."""
        score = await self.get_for_artifact(artifact_id, artifact_type)
        if not score:
            score = Score(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
            )
            self._session.add(score)
            await self._session.flush()
        return score
    
    async def update_from_feedback(
        self,
        artifact_id: UUID,
        artifact_type: str,
        feedback: Feedback,
    ) -> Score:
        """Update score based on new feedback."""
        score = await self.get_or_create(artifact_id, artifact_type)
        
        # Determine weight based on feedback tier
        weight = {
            FeedbackTier.DETAILED: 1.0,
            FeedbackTier.QUICK: 0.4,
            FeedbackTier.IMPLICIT: 0.1,
        }.get(feedback.feedback_tier, 0.4)
        
        # Update score with weighted average
        if feedback.rating is not None:
            total_weight = score.positive_feedback + score.negative_feedback + weight
            score.score = (
                score.score * (total_weight - weight) + 
                feedback.rating * weight
            ) / total_weight
        
        # Update counts
        positive_types = {
            FeedbackType.HELPFUL, FeedbackType.PROJECT_SUCCESS,
            FeedbackType.TASKS_COMPLETE, FeedbackType.ESTIMATES_ACCURATE,
            FeedbackType.RISKS_IDENTIFIED, FeedbackType.USED_AS_IS,
        }
        negative_types = {
            FeedbackType.NOT_HELPFUL, FeedbackType.PROJECT_FAILURE,
            FeedbackType.TASKS_INCOMPLETE, FeedbackType.ESTIMATES_INACCURATE,
            FeedbackType.RISKS_MISSED,
        }
        
        if feedback.feedback_type in positive_types:
            score.positive_feedback += 1
        elif feedback.feedback_type in negative_types:
            score.negative_feedback += 1
        
        if feedback.feedback_type == FeedbackType.USED:
            score.times_used += 1
            score.last_used = datetime.now(UTC)
        elif feedback.feedback_type == FeedbackType.RETRIEVED:
            score.times_retrieved += 1
            score.last_retrieved = datetime.now(UTC)
        
        score.last_feedback = datetime.now(UTC)
        
        # Update confidence
        total_samples = score.positive_feedback + score.negative_feedback + score.times_used
        score.confidence = min(1.0, total_samples / 10)
        
        await self._session.flush()
        return score
    
    async def get_top_scored(
        self,
        artifact_type: str,
        limit: int = 10,
        min_confidence: float = 0.3,
    ) -> Sequence[Score]:
        """Get top-scored artifacts of a type."""
        result = await self._session.execute(
            select(Score)
            .where(and_(
                Score.artifact_type == artifact_type,
                Score.confidence >= min_confidence,
            ))
            .order_by(Score.score.desc())
            .limit(limit)
        )
        return result.scalars().all()
```

---

## 7. Migration Path

### 7.1 Phase 2.1: Add PostgreSQL (Weeks 1-2 of next cycle)

**Goal:** Add PostgreSQL alongside Qdrant without breaking existing functionality.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    v2.1 MIGRATION TASKS                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Week 1:
  □ Set up PostgreSQL (local Docker + cloud options)
  □ Create initial schema (organizations, users, projects, templates)
  □ Implement SQLAlchemy models
  □ Implement base repositories
  □ Set up Alembic for migrations

Week 2:
  □ Implement RLS policies
  □ Implement TenantSessionManager
  □ Migrate project capture to PostgreSQL
  □ Migrate feedback/scores to PostgreSQL
  □ Integration tests
  □ Update MCP tools to use repositories
```

**Data Flow (v2.1):**

```
                    ┌─────────────────┐
                    │   MCP Tools     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌─────────────────┐          ┌─────────────────┐
      │  PostgreSQL     │          │     Qdrant      │
      │ (via SQLAlchemy)│          │  (existing)     │
      │                 │          │                 │
      │ NEW:            │          │ UNCHANGED:      │
      │ • projects      │          │ • chunks        │
      │ • templates     │          │ • patterns      │
      │ • feedback      │          │   (vectors)     │
      │ • scores        │          │                 │
      │ • relationships │          │                 │
      │ • organizations │          │                 │
      │ • users         │          │                 │
      └─────────────────┘          └─────────────────┘
```

### 7.2 v3: Consolidate to pgvector (Future)

**Goal:** Move all data to PostgreSQL, eliminate Qdrant dependency.

```
┌──────────────────────────────────────────────────────────┐
│                    v3 MIGRATION TASKS                    │
└──────────────────────────────────────────────────────────┘

Phase 1: Prepare (2 weeks)
  □ Add chunks table to PostgreSQL
  □ Add patterns table to PostgreSQL
  □ Create pgvector indexes
  □ Implement hybrid search queries
  □ Benchmark pgvector vs Qdrant

Phase 2: Dual-Write (2 weeks)
  □ Write new chunks to both Qdrant and PostgreSQL
  □ Verify data consistency
  □ Compare search results

Phase 3: Migrate Historical (1 week)
  □ Batch migrate existing chunks from Qdrant to PostgreSQL
  □ Verify migration completeness
  □ Update chunk_relationships to use PostgreSQL chunk IDs

Phase 4: Cutover (1 week)
  □ Switch reads to PostgreSQL
  □ Deprecate Qdrant writes
  □ Monitor performance
  □ Remove Qdrant dependency

Phase 5: Cleanup (1 week)
  □ Remove Qdrant code
  □ Optimize PostgreSQL indexes
  □ Update documentation
```

**Hybrid Query Example (v3):**

```sql
-- Single query: Vector similarity + relational filtering + score boosting
SELECT 
    c.id,
    c.content,
    c.document_title,
    c.authority_score,
    s.score as effectiveness_score,
    s.confidence as score_confidence,
    (1 - (c.embedding <=> :query_embedding)) as semantic_similarity,
    -- Combined ranking
    (
        (1 - (c.embedding <=> :query_embedding)) * 0.7 +
        COALESCE(s.score, 0.5) * 
        CASE 
            WHEN COALESCE(s.score, 0.5) >= 0.8 THEN 1.5
            WHEN COALESCE(s.score, 0.5) >= 0.6 THEN 1.2
            WHEN COALESCE(s.score, 0.5) >= 0.4 THEN 1.0
            WHEN COALESCE(s.score, 0.5) >= 0.2 THEN 0.8
            ELSE 0.5
        END * 0.3
    ) as combined_score
FROM chunks c
LEFT JOIN scores s ON s.artifact_id = c.id AND s.artifact_type = 'chunk'
WHERE 
    c.organization_id = current_setting('app.current_organization_id')::UUID
    AND c.document_type = 'standard'
    AND c.authority_score >= 0.7
    AND (1 - (c.embedding <=> :query_embedding)) >= 0.5
ORDER BY combined_score DESC
LIMIT 10;
```

### 7.3 Alembic Migration Setup

```python
# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from knowledge_mcp.db.base import Base
from knowledge_mcp.db.models import *  # Import all models

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
```

---

## 8. Configuration

### 8.1 Environment Variables (Additions)

```bash
# === DATABASE ===
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/knowledge_mcp
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# === MULTI-TENANCY ===
DEFAULT_ORGANIZATION_ID=  # For single-tenant mode
ENABLE_RLS=true

# === MIGRATIONS ===
ALEMBIC_CONFIG=alembic.ini
```

### 8.2 Configuration Schema (Additions)

```python
# src/knowledge_mcp/config.py

from pydantic import BaseModel, PostgresDsn


class DatabaseConfig(BaseModel):
    """PostgreSQL configuration."""
    
    url: PostgresDsn
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


class MultiTenancyConfig(BaseModel):
    """Multi-tenancy configuration."""
    
    enabled: bool = True
    enable_rls: bool = True
    default_organization_id: str | None = None  # For single-tenant mode


class KnowledgeConfig(BaseModel):
    """Root configuration (extended)."""
    
    # Existing...
    
    # New
    database: DatabaseConfig
    multi_tenancy: MultiTenancyConfig = MultiTenancyConfig()
```

---

## 9. Testing Considerations

### 9.1 Test Database Setup

```python
# tests/conftest.py

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from knowledge_mcp.db.base import Base
from knowledge_mcp.db.context import TenantContext, TenantSessionManager


@pytest.fixture(scope="session")
def database_url():
    """Test database URL."""
    return "postgresql+asyncpg://test:test@localhost:5432/knowledge_mcp_test"


@pytest_asyncio.fixture
async def engine(database_url):
    """Create test engine."""
    engine = create_async_engine(database_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def session_manager(engine):
    """Create session manager."""
    session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return TenantSessionManager(session_maker)


@pytest_asyncio.fixture
async def test_context():
    """Test tenant context."""
    return TenantContext(
        organization_id=uuid4(),
        user_id=uuid4(),
        user_role="admin",
    )


@pytest_asyncio.fixture
async def session(session_manager, test_context):
    """Get test session with tenant context."""
    async with session_manager.session(test_context) as session:
        yield session
```

### 9.2 RLS Test Cases

```python
# tests/integration/test_rls.py

import pytest
from uuid import uuid4

from knowledge_mcp.db.models.project import Project, ProjectVisibility


@pytest.mark.asyncio
async def test_tenant_isolation(session_manager):
    """Test that tenants cannot see each other's data."""
    org1_id = uuid4()
    org2_id = uuid4()
    
    # Create project in org1
    ctx1 = TenantContext(org1_id, uuid4(), "admin")
    async with session_manager.session(ctx1) as session:
        project = Project(
            organization_id=org1_id,
            name="Org1 Project",
            project_type="test",
        )
        session.add(project)
        await session.commit()
        project_id = project.id
    
    # Try to access from org2
    ctx2 = TenantContext(org2_id, uuid4(), "admin")
    async with session_manager.session(ctx2) as session:
        result = await session.get(Project, project_id)
        assert result is None  # Should not be visible


@pytest.mark.asyncio
async def test_visibility_personal(session_manager):
    """Test personal visibility only shows to owner."""
    org_id = uuid4()
    owner_id = uuid4()
    other_user_id = uuid4()
    
    # Create personal project
    ctx_owner = TenantContext(org_id, owner_id, "member")
    async with session_manager.session(ctx_owner) as session:
        project = Project(
            organization_id=org_id,
            owner_id=owner_id,
            name="Personal Project",
            project_type="test",
            visibility=ProjectVisibility.PERSONAL,
        )
        session.add(project)
        await session.commit()
    
    # Other user in same org cannot see it
    ctx_other = TenantContext(org_id, other_user_id, "member")
    async with session_manager.session(ctx_other) as session:
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        assert len(projects) == 0


@pytest.mark.asyncio
async def test_visibility_organization(session_manager):
    """Test organization visibility shows to all org members."""
    org_id = uuid4()
    owner_id = uuid4()
    other_user_id = uuid4()
    
    # Create organization-wide project
    ctx_owner = TenantContext(org_id, owner_id, "member")
    async with session_manager.session(ctx_owner) as session:
        project = Project(
            organization_id=org_id,
            owner_id=owner_id,
            name="Org Project",
            project_type="test",
            visibility=ProjectVisibility.ORGANIZATION,
        )
        session.add(project)
        await session.commit()
    
    # Other user in same org CAN see it
    ctx_other = TenantContext(org_id, other_user_id, "member")
    async with session_manager.session(ctx_other) as session:
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        assert len(projects) == 1
```

---

## 10. Appendices

### Appendix A: Dependencies (Additions)

```toml
# pyproject.toml additions

[project.dependencies]
# Database
sqlalchemy = ">=2.0.0"
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
pgvector = ">=0.2.0"

# Testing
pytest-asyncio = ">=0.23.0"
```

### Appendix B: Docker Compose (Development)

```yaml
# docker-compose.yml

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: knowledge
      POSTGRES_PASSWORD: knowledge
      POSTGRES_DB: knowledge_mcp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U knowledge"]
      interval: 5s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
```

### Appendix C: Init SQL

```sql
-- init.sql (run on container startup)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Create application user with limited privileges
CREATE USER knowledge_app WITH PASSWORD 'knowledge_app';
GRANT CONNECT ON DATABASE knowledge_mcp TO knowledge_app;
GRANT USAGE ON SCHEMA public TO knowledge_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO knowledge_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO knowledge_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO knowledge_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO knowledge_app;
```

### Appendix D: Performance Considerations

| Aspect | Recommendation |
|--------|----------------|
| **Connection pooling** | Use pgbouncer in production |
| **Index tuning** | Monitor slow queries, add indexes as needed |
| **pgvector lists** | Start with lists=100, increase for larger datasets |
| **VACUUM** | Schedule regular VACUUM ANALYZE |
| **RLS overhead** | ~5-10% overhead, acceptable for security benefits |
| **Batch operations** | Use bulk insert for feedback/scores |

---

## Document End

**Addendum Version:** 2.0.0-addendum-1  
**Status:** Draft for Review  
**Scope:** PostgreSQL, SQLAlchemy, Multi-tenancy, Migration Path

**Key Additions:**
1. PostgreSQL schema with 10 tables
2. SQLAlchemy 2.0 models with async support
3. Row-Level Security for multi-tenancy
4. Repository pattern for data access
5. Migration path from v2 hybrid to v3 consolidated
6. Test fixtures and RLS test cases

**Next Steps:**
1. Review and approve architecture
2. Set up development PostgreSQL environment
3. Implement Phase 2.1 migration
4. Update main specification to reference this addendum
