# Phase 3: Feedback + Scoring - Context

**Gathered:** 2026-01-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Three-tier feedback collection (implicit, quick, detailed) and simple effectiveness scoring to boost search results. Creates the learning loop where Claude's feedback improves future recommendations. One new MCP tool: `knowledge_feedback`.

</domain>

<decisions>
## Implementation Decisions

### Feedback Collection Flow
- Inline feedback collection — Claude provides feedback immediately after using results
- Both implicit and explicit feedback supported:
  - **Implicit:** Track when Claude references a chunk_id from previous search
  - **Explicit:** Via standalone `knowledge_feedback` tool
- Standalone tool design — `knowledge_feedback` references previous search/results

### Scoring Formula
- Fixed 70/30 weights — `combined = (semantic * 0.7) + (effectiveness * 0.3)`
- Cold start default — New content starts at 0.5 effectiveness (neutral)
- Minimum 3 feedback required — Effectiveness term only contributes after 3+ data points

### Feedback Granularity
- Individual result level — Rate specific chunks by chunk_id
- 3-point scale — helpful / neutral / unhelpful
- No text comments — Keep feedback simple, just the rating
- Project outcomes — Track project success/failure (not individual decision outcomes)

### Score Transparency
- Hidden by default — Scores are internal, not in normal API response
- Debug mode via parameter — `debug=true` shows scoring breakdown
- Full breakdown in debug — semantic_score, effectiveness_score, combined_score, feedback_count, formula, recent feedback history
- Indicator on boosted results — Flag like "highly effective" when effectiveness significantly boosted a result

### Claude's Discretion
- Time decay implementation (whether and how to decay old feedback)
- Exact thresholds for "highly effective" indicator
- Internal storage schema for feedback records

</decisions>

<specifics>
## Specific Ideas

- The learning loop is the core value: Claude uses knowledge → provides feedback → future searches improve
- Three tiers from roadmap: implicit (usage tracking), quick (thumbs), detailed (outcomes)
- Implicit tracking via chunk_id reference detection — when Claude quotes or cites a specific result

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-feedback-scoring*
*Context gathered: 2026-01-28*
