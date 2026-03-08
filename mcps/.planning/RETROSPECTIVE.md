# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-08
**Phases:** 3 | **Plans:** 7 | **Sessions:** ~4

### What Was Built
- MCP server with 9 tools (parse, detect, validate, read, write, patch, register, list, heal)
- Multi-format engine (JSON, YAML, XML, TOML) with round-trip fidelity
- Schema registry with discovery, composition, and JSON Schema wire format
- Self-healing engine with conservative coercion and unknown field preservation
- Security layer: path validation, atomic writes, schema load validation
- 135 tests, 322 assertions, zero regressions across all phases

### What Worked
- TDD approach in Phase 3 caught a real bug (healData not applying defaults after re-validation)
- 3-phase architecture (foundation → core value → differentiator) gave clean dependency ordering
- Wave-based execution kept phases independent — no cross-phase merge conflicts
- Coarse planning (2-3 plans per phase) avoided over-specification while keeping focus
- FormatHandler interface made adding new formats trivial

### What Was Inefficient
- ROADMAP.md checkbox states got stale (Phase 2 showed "In progress", some plans unchecked despite completion) — required manual fixup at milestone
- Performance metrics in STATE.md had zeroed-out summary tables even though per-plan data was recorded
- Nyquist VALIDATION.md files were created but wave_0 never executed — ceremony without value

### Patterns Established
- JSON Schema as wire format for MCP schema registration (Zod can't cross stdio)
- safeParse for non-throwing validation, parse for CRUD operations
- Conservative coercion strategy: only safe type conversions, mark unfixable as manual
- Raw data mutation for healing (preserves unknown fields vs. Zod output stripping them)

### Key Lessons
1. Zod `_def` internals are accessible and stable enough for default extraction — no need for wrapper abstractions
2. MCP tool parameters can't pass complex objects (Zod schemas); wire formats like JSON Schema bridge the gap
3. Single-day milestones are feasible for focused MCP servers with clear requirements

### Cost Observations
- Model mix: ~70% sonnet (executors, verifiers), ~30% opus (orchestration)
- Sessions: ~4 (init/research, phase 1 execution, phase 2 execution, phase 3 + completion)
- Notable: 24 minutes total execution across 7 plans — averaging ~3.4 min/plan

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | ~4 | 3 | Initial baseline — GSD workflow established |

### Cumulative Quality

| Milestone | Tests | Assertions | LOC (src+test) |
|-----------|-------|------------|----------------|
| v1.0 | 135 | 322 | 4,260 |

### Top Lessons (Verified Across Milestones)

1. (Awaiting v1.1+ to cross-validate)
