# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — AI-Assisted Systems Design Platform

**Shipped:** 2026-03-02
**Phases:** 5 | **Plans:** 13 | **Sessions:** 4

### What Was Built
- Design Registry with 14 slot types, schema validation, atomic writes, optimistic locking, change journal
- Requirements ingestion pipeline with delta detection for 5 upstream registry types
- 3 domain agents (decomposition, interface, contract) following identical data-prep-then-AI-reasoning pattern
- Generic config-driven approval gate reusable across all proposal types
- End-to-end traceability graph with chain validation and BFS impact analysis
- Write-time trace enforcement with warn-but-allow policy
- 12,498 LOC Python, 303 tests, 14 JSON schemas

### What Worked
- **Wave-based phase execution** — sequential dependency ordering within GSD prevented integration issues; each phase built cleanly on the previous
- **Data-prep-then-AI-reasoning agent pattern** — agents prepare structured data and format output; Claude reasons in command workflows. This made agents fully testable without AI and kept the separation clean
- **Generic ApprovalGate** — investing time in Phase 3 to make the gate config-driven paid off immediately in Phase 4 where it handled interface and contract proposals with zero gate code changes
- **Warn-but-allow trace validation** — never blocked writes, injected gap markers automatically, zero impact on existing tests when added in Phase 5
- **Tight SUMMARY/VERIFICATION cycle** — verifier caught real issues (type safety in trace_validator, None guard in traceability_agent) that the test suite missed

### What Was Inefficient
- **ROADMAP.md progress table** — the table became stale across phases; only phase 5 showed accurate status. Manual maintenance of this table is error-prone
- **Code simplifier agent sandbox** — 4 parallel simplifier agents were spawned but all blocked on Edit/Bash permissions. Changes had to be applied manually in the main session, negating the parallelism benefit
- **Pyright false positives** — reportMissingImports cascaded across all test files due to missing pyproject.toml src layout config. Noise in every diagnostic run

### Patterns Established
- **Agent pattern:** prepare() → Claude analysis → create_proposals() → ApprovalGate.decide()
- **Stale detection:** timestamp comparison between dependent slot types (req→comp→intf→cntr)
- **Schema convention:** Draft 2020-12, additionalProperties: false, slot_id pattern per type
- **Test organization:** unit tests per module + integration tests per phase + full regression on every commit
- **Singleton slot:** deterministic ID via api.ingest() with api.update() for refreshes (e.g., tgraph-current)
- **Command workflow:** init_workspace() → SlotAPI setup → agent.prepare() → display → Claude reasoning → agent.create_proposals() → report

### Key Lessons
1. **Invest in generic infrastructure early** — the ApprovalGate took extra effort in Phase 3 but saved significant time in Phase 4 and would save more in future phases
2. **Warn-but-allow is better than strict enforcement** — trace validation that blocks writes would have required backfilling all existing tests; gap markers achieve the same awareness without friction
3. **Forward-replay beats reverse-apply** — RFC 6902 diffs store old→new; reconstructing old versions via reverse-apply would require values not in the diff. Forward replay from initial state is simpler and correct
4. **One-level cascade prevents explosion** — stale detection that cascades (req→comp→intf→cntr) is useful, but auto-cascading would create noise; each agent checking independently gives the right granularity

### Cost Observations
- Model mix: ~60% Sonnet (subagents), ~40% Opus (orchestration)
- Sessions: 4 (project init, phases 1-3, phases 4-5, simplification + audit)
- Notable: 13 plans executed in 57 minutes total (~4.4 min/plan average)

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 4 | 5 | Established agent pattern, generic gate, trace enforcement |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 303 | — | 13 (no new pip deps beyond jsonschema) |

### Top Lessons (Verified Across Milestones)

1. Generic infrastructure investments compound across phases
2. Warn-but-allow policies integrate better than strict enforcement in evolving systems
