---
plan: 02-06
phase: 02
title: "Plan Strategy + ProjectRepository"
subsystem: workflow-infrastructure
tags: [planning, repository, strategy-pattern, async-crud, state-machine]
one_liner: "Planning workflow strategy with category-based retrieval + Project repository with async CRUD and state validation"

# Dependencies
requires:
  - 02-01  # Project models with state machine
  - 02-02  # SearchStrategy ABC

provides:
  - ProjectRepository with async CRUD operations
  - PlanStrategy for planning workflow queries
  - Category-based result organization (templates, risks, lessons_learned, precedents)

affects:
  - 02-07  # MCP tools will use ProjectRepository
  - future-phases  # Other strategies can follow PlanStrategy pattern

# Technical Details
tech-stack:
  added: []
  patterns:
    - Repository pattern for Project CRUD
    - Strategy pattern for planning-specific search
    - Category-based result organization

key-files:
  created:
    - src/knowledge_mcp/db/repositories.py (ProjectRepository class)
    - src/knowledge_mcp/search/strategies/plan.py
    - tests/unit/test_search/test_plan_strategy.py
  modified:
    - src/knowledge_mcp/db/__init__.py (export ProjectRepository)
    - tests/unit/test_db/test_repositories.py (added TestProjectRepository)

decisions:
  - decision: "ProjectRepository uses UUID primary keys"
    alternatives: ["Integer IDs", "UUID"]
    rationale: "Consistent with Project model design from 02-01, prevents distributed ID collision"

  - decision: "list_active filters PLANNING and ACTIVE states"
    alternatives: ["List all projects", "Parameterized filter"]
    rationale: "Most common use case is finding non-terminal projects; simple and efficient"

  - decision: "PlanStrategy categorizes results into 4 categories"
    alternatives: ["Flat results", "User-defined categories"]
    rationale: "Fixed categories (templates, risks, lessons_learned, precedents) cover planning needs; simpler than dynamic categorization"

  - decision: "Uncategorized results default to templates category"
    alternatives: ["Separate 'other' category", "Discard uncategorized"]
    rationale: "Planning content is often template-like; better UX than 'other' bucket"

# Metrics
duration: "4.2 min"
completed: "2026-01-28"
---

# Phase 02 Plan 06: Plan Strategy + ProjectRepository Summary

**One-liner:** Planning workflow strategy with category-based retrieval + Project repository with async CRUD and state validation

## What Was Built

### ProjectRepository
Implemented async repository for Project entities with:
- **CRUD operations**: create, get_by_id, get_by_name, list_active, update
- **State machine integration**: transition_state validates allowed transitions
- **SQLAlchemy 2.0 async patterns**: Uses AsyncSession throughout
- **Comprehensive error handling**: ValueError for invalid transitions or missing projects

### PlanStrategy
Implemented planning workflow search strategy with:
- **Category support**: templates, risks, lessons_learned, precedents
- **Keyword boosting**: Planning-specific terms (planning, template, framework, etc.)
- **Smart categorization**: Automatically organizes results by content keywords
- **Dual output modes**: Flat list for specific category, categorized structure for general queries

## Commits

| Hash    | Type | Description                                           |
|---------|------|-------------------------------------------------------|
| 2cff3ec | feat | Add ProjectRepository with async CRUD operations      |
| 21ca9ab | feat | Implement PlanStrategy for planning workflows         |
| d65b6e0 | test | Add comprehensive unit tests for ProjectRepository    |
| 72d196e | test | Add comprehensive unit tests for PlanStrategy         |

## Decisions Made

### 1. Repository Pattern for Project Access
**Context:** Need to encapsulate database queries for Project entities

**Decision:** Implement full repository pattern with 6 methods (create, get_by_id, get_by_name, list_active, update, transition_state)

**Alternatives Considered:**
- Direct SQLAlchemy queries in MCP tools
- Partial repository (only get methods)

**Rationale:**
- Encapsulates session management
- Enables easier testing with mocked repositories
- Provides single source of truth for Project queries
- Future-proofs for query optimization

**Impact:** Clean separation between data access and business logic

### 2. Category-Based Result Organization
**Context:** Planning workflows need different types of knowledge

**Decision:** Fixed 4 categories with keyword-based auto-categorization

**Alternatives Considered:**
- Flat results list
- User-defined categories
- LLM-based categorization

**Rationale:**
- Categories (templates, risks, lessons_learned, precedents) cover planning needs
- Keyword matching is fast and deterministic
- Simpler than dynamic or AI-based categorization
- Easy to extend if needed

**Impact:** Users get organized results without extra effort

### 3. State Machine Validation in Repository
**Context:** Project status transitions must follow state machine rules

**Decision:** Delegate validation to Project.transition_to() model method

**Alternatives Considered:**
- Implement validation in repository
- Skip validation (trust caller)

**Rationale:**
- Model owns state machine logic (single responsibility)
- Repository remains thin data access layer
- Consistent with 02-01 design

**Impact:** Clean separation of concerns, consistent validation

## Test Coverage

### ProjectRepository Tests (13 tests)
- ✅ Create project with all fields
- ✅ Create project with minimal fields (defaults)
- ✅ Get by ID (found and not found)
- ✅ Get by name (found and not found)
- ✅ List active projects (filters PLANNING/ACTIVE)
- ✅ List active when empty
- ✅ Update project
- ✅ Valid state transitions (PLANNING→ACTIVE, ACTIVE→COMPLETED)
- ✅ Invalid state transitions raise ValueError
- ✅ Transition sets completed_at for terminal states
- ✅ Transition with missing project raises ValueError

### PlanStrategy Tests (14 tests)
- ✅ Preprocess query without category (adds all facets)
- ✅ Preprocess with each category (templates, risks, lessons_learned, precedents)
- ✅ Preprocess preserves filters from params
- ✅ Adjust ranking boosts planning keywords
- ✅ Adjust ranking boosts template document types
- ✅ Adjust ranking maintains sort order
- ✅ Adjust ranking caps score at 1.0
- ✅ Format output with category returns flat structure
- ✅ Format output without category categorizes results
- ✅ Uncategorized results default to templates
- ✅ Format output includes all required fields

**All 27 tests pass** ✅

## Verification Results

```bash
# Unit tests
poetry run pytest tests/unit/test_search/test_plan_strategy.py tests/unit/test_db/test_repositories.py::TestProjectRepository -v
# Result: 27 passed, 1 warning

# Type checking
poetry run pyright src/knowledge_mcp/search/strategies/plan.py src/knowledge_mcp/db/repositories.py
# Result: 0 errors, 0 warnings, 0 informations
```

## Integration Points

### Upstream Dependencies
- **02-01**: Uses Project model with STATE_TRANSITIONS and transition_to()
- **02-02**: Extends SearchStrategy ABC (preprocess_query, adjust_ranking, format_output)

### Downstream Consumers
- **02-07**: MCP tools will use ProjectRepository for project CRUD operations
- **Future strategies**: PlanStrategy demonstrates category-based organization pattern

## Deviations from Plan

None - plan executed exactly as written.

## Technical Notes

### ProjectRepository Implementation
- Uses `session.get()` for primary key lookups (efficient)
- Uses `select()` + `execute()` for filtered queries
- Calls `session.flush()` after mutations (lets caller control commit)
- Returns None for not-found queries (Pythonic pattern)

### PlanStrategy Implementation
- Keyword lists are class constants (easy to extend)
- Categorization is first-match (predictable behavior)
- Score boosting is additive with 1.0 cap (prevents score inflation)
- Async preprocess_query enables future LLM integration

### Type Safety
- All functions fully type-hinted
- Pyright strict mode passes with 0 errors
- Used explicit `list[str]` types to avoid inference issues

## Next Phase Readiness

### What's Ready
- ✅ ProjectRepository ready for MCP tool integration
- ✅ PlanStrategy ready for WorkflowSearcher integration
- ✅ Category-based organization pattern established
- ✅ All tests passing

### What's Needed
- **02-07**: Implement MCP tools that use ProjectRepository
- **Integration test**: End-to-end test with WorkflowSearcher + PlanStrategy

### Potential Issues
- None identified

## Performance Notes

- **Execution time**: 4.2 minutes (under target)
- **Test execution**: 8.31 seconds for 27 tests
- **Type checking**: 0.819 seconds for 2 files

## Learning & Improvements

### What Worked Well
1. **Repository pattern**: Clean separation of data access
2. **Category system**: Simple keyword matching is sufficient
3. **Type annotations**: Caught type issues early with explicit list types
4. **Test-first mindset**: Tests written immediately after implementation

### What Could Be Better
1. **Category matching**: Could support multi-category assignment (currently first-match)
2. **Score boosting**: Could be more sophisticated (TF-IDF style)

### Patterns Established
- Repository methods return None for not-found (not exceptions)
- Strategy methods use type-hinted async signatures
- Tests use AAA pattern with descriptive names
- Category-based result organization for workflow-specific needs
