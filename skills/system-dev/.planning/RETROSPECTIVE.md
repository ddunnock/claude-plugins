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

## Milestone: v1.1 — Views & Diagrams

**Shipped:** 2026-03-08
**Phases:** 6 (incl. 6b gap closure) | **Plans:** 13 | **Sessions:** ~8

### What Was Built
- View assembly engine with scope matching, gap indicators, 5 built-in view specs, hierarchical organization
- Relationship-aware views with edge extraction, relevance ranking, content-hash determinism
- D2 structural and Mermaid behavioral diagram generation with gap placeholders
- Diagram orchestration layer (view -> format selection -> generation -> SlotAPI write)
- Jinja2 template system with manifest registry and two-tier resolution
- Structured logging across both subsystems (view.* and diagram.* namespaces)
- 17,463 LOC Python, 503 tests, 3 Jinja2 templates

### What Worked
- **Declarative view specs** — BUILTIN_SPECS defined as data, not code. Adding new view types (gap-report, interface-map) was trivial: just add a dict entry with scope patterns
- **Phase 6b gap closure pattern** — catching integration issues early (missing SKILL.md routing, schema gaps) via UAT before downstream phases prevented compounding errors
- **Template-driven diagram generation** — Jinja2 templates made D2/Mermaid output independently testable and user-overridable without modifying skill source
- **Consistent structured logging pattern** — view.* and diagram.* namespaces followed identical INFO/DEBUG conventions from Phase 7 through Phase 9
- **Content-hash determinism** — SHA-256 snapshot_id and pre-sorted template contexts ensured byte-identical output, simplifying testing and caching

### What Was Inefficient
- **Phase 8 orchestration gap** — Plan 08-02 SUMMARY claimed orchestration was complete, but generate_diagram() was never actually implemented. Required 08-02g gap closure plan to fix. Verification caught it but the false positive wasted a plan cycle
- **Stale REQUIREMENTS.md checkboxes** — DIAG-01..04, 06, 09 remained unchecked despite code being complete. Multiple phases had to fix documentation that should have been updated atomically with code commits
- **Audit found doc-only gaps at milestone boundary** — Phase 10 was entirely documentation fixes (SKILL.md routing, slot type table). Better to catch these during phase verification, not at milestone audit

### Patterns Established
- **View assembly pipeline:** snapshot_capture -> scope_match -> gap_build -> hierarchical_org -> rank -> schema_validate
- **Diagram pipeline:** view_assembly -> format_resolve -> template_load -> context_build -> render -> SlotAPI.ingest()
- **Two-tier resolution:** workspace_root/{dir}/ overrides built-in {dir}/ by filename (view-specs, templates)
- **Abstraction layers:** parent_id field enables system/component collapsing with count badges
- **Gap rendering:** view gap indicators -> diagram gap placeholders with visual distinction (dashed borders, color coding)

### Key Lessons
1. **Verify orchestration layers exist, not just unit functions** — Phase 8 had passing tests for generate_d2/generate_mermaid but no actual generate_diagram() wiring. SUMMARY self-check should verify the integration entry point
2. **Update documentation atomically with code** — stale checkboxes in REQUIREMENTS.md and missing SKILL.md entries accumulated across phases. Each commit should include the documentation update
3. **Template-driven output separates structure from content** — Jinja2 templates let users customize diagram rendering without understanding the generation pipeline
4. **Content-hash IDs enable efficient dedup** — unchanged diagram detection via hash comparison avoids unnecessary SlotAPI writes

### Cost Observations
- Model mix: ~55% Sonnet (executor subagents), ~45% Opus (orchestration, verification)
- Sessions: ~8 (planning, phases 6-6b, phase 7, phase 8, phase 8 gap, phase 9, phase 10, milestone)
- Notable: 13 plans executed across 6 phases; gap closure patterns (6b, 08-02g, 10) added 3 plans for quality

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 4 | 5 | Established agent pattern, generic gate, trace enforcement |
| v1.1 | ~8 | 6 | Gap closure pattern (6b, 08-02g, 10), template-driven output, structured logging convention |

### Cumulative Quality

| Milestone | Tests | LOC | New Deps |
|-----------|-------|-----|----------|
| v1.0 | 303 | 12,498 | jsonschema |
| v1.1 | 503 | 17,463 | jinja2 |

### Top Lessons (Verified Across Milestones)

1. Generic infrastructure investments compound across phases (ApprovalGate in v1.0, BUILTIN_SPECS in v1.1)
2. Warn-but-allow policies integrate better than strict enforcement in evolving systems
3. Gap closure phases are expected, not failures — catching integration issues early prevents compounding
4. Documentation must update atomically with code — stale checkboxes/routing accumulate otherwise
