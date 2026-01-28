---
phase: 02
name: Workflow Support
status: discussed
created: 2026-01-27
---

# Phase 2: Workflow Support - Context Document

## Phase Goal
Specialized retrieval tools for SE workflows: RCCA analysis, trade studies, exploratory research, and project capture. Delivers 4 new MCP tools with extensible architecture.

## Discussion Summary

### 1. RCCA Tool Behavior

**Search Mode:** Unified search
- Search symptoms and root causes simultaneously
- Rank by relevance across both symptom and cause content
- Don't force caller to decide search mode upfront

**Output Format:** Rich metadata
- Extract structured fields from RCCA content:
  - `symptoms` - Observable behaviors, error messages
  - `root_cause` - Underlying cause identified
  - `contributing_factors` - Secondary causes
  - `resolution` - How the issue was resolved
- Enables Claude to synthesize failure analysis from structured data

### 2. Trade Study Support

**Result Format:** Alternative-grouped
- Group results by alternative/option
- Show all evaluation criteria for each alternative
- Format: `{ alternative: "Option A", criteria: [ {name, evidence, score}... ] }`

**Source Strategy:** Synthesize always
- Don't limit to pre-tagged trade study documents
- Find any relevant information about alternatives
- Structure scattered information as comparison
- Enables trade studies even when formal comparisons don't exist in corpus

### 3. Planning + Capture

**Explore Mode:** Multi-facet search
- Automatically search multiple aspects of a query:
  - Definitions and terminology
  - Examples and case studies
  - Related standards and requirements
  - Best practices and guidance
- Returns organized by facet, not just flat list

**Project Capture:** Comprehensive (all of the above)
- **Query history:** Past queries + results for "what did I search before?"
- **Project profile:** Domain, applicable standards, constraints
- **Decision trail:** Decisions, alternatives considered, rationale with source links
- Forms a project knowledge graph for personalized future searches

### 4. Tool Architecture

**Pattern:** Strategy pattern
- Shared search core with swappable strategy objects
- `RCCAStrategy`, `TradeStrategy`, `ExploreStrategy`, `PlanStrategy`
- Strategies modify:
  - Query preprocessing (expansion, faceting)
  - Ranking/scoring adjustments
  - Output formatting and enrichment

**Extensibility:** Both levels
- **Simple tools:** Config-driven (query mods, filters, output format)
- **Complex tools:** Python plugin directory with auto-discovery
- Clean internal API for adding new strategies

## Technical Implications

### Strategy Interface

```python
class SearchStrategy(ABC):
    """Base class for specialized search strategies."""

    @abstractmethod
    def preprocess_query(self, query: str, params: dict) -> SearchQuery:
        """Transform user query into internal search representation."""

    @abstractmethod
    def adjust_ranking(self, results: list[SearchResult]) -> list[SearchResult]:
        """Apply strategy-specific ranking adjustments."""

    @abstractmethod
    def format_output(self, results: list[SearchResult]) -> dict:
        """Structure output according to strategy requirements."""
```

### Database Schema Extensions

Phase 2 requires new tables for project capture:
- `projects` - Project profiles with domain/standards metadata
- `query_history` - Past queries linked to projects
- `decisions` - Decision records with alternatives and rationale
- `decision_sources` - Links decisions to supporting chunks

### Config-Driven Extension Point

```yaml
# Example: custom tool via config
custom_strategies:
  safety_analysis:
    description: "Find safety-related requirements and hazards"
    query_expansion:
      - "safety requirement"
      - "hazard analysis"
      - "risk mitigation"
    filters:
      document_type: ["standard", "handbook"]
    output_fields:
      - hazard_id
      - severity
      - mitigation
```

## Dependencies

- Phase 1: PostgreSQL foundation (for project capture tables)
- Phase 1: Async database patterns (session management)
- Phase 1: MCP tool registration (for 4 new tools)

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| RCCA search mode? | Unified (symptoms + causes together) |
| RCCA output structure? | Rich metadata (symptoms, root_cause, etc.) |
| Trade study format? | Alternative-grouped |
| Trade study sources? | Synthesize from any relevant content |
| Explore vs search? | Multi-facet (auto-search definitions, examples, standards) |
| Project capture scope? | Comprehensive (queries + profile + decisions) |
| Tool architecture? | Strategy pattern with shared core |
| Future extensibility? | Config-driven simple + code plugins for complex |

## Success Criteria Derived

1. **knowledge_rcca** tool returns structured failure analysis with extracted metadata
2. **knowledge_trade** tool groups results by alternative with criteria evidence
3. **knowledge_explore** tool returns multi-facet results (definitions, examples, standards)
4. **knowledge_plan** tool captures queries, profile, and decisions
5. Strategy pattern enables adding new search modes without modifying core
6. Config file can define simple specialized tools
7. Plugin directory supports complex custom strategies
8. Project capture persists across sessions
