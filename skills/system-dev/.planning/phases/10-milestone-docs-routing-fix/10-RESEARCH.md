# Phase 10: Milestone Documentation & Routing Fix - Research

**Researched:** 2026-03-08
**Domain:** Documentation gap closure, SKILL.md command routing, stale checkpoint cleanup
**Confidence:** HIGH

## Summary

Phase 10 is a documentation and cleanup phase that closes three audit gaps (INT-01, INT-02, FLOW-01) identified in the v1.1 milestone audit. All functional code is complete and tested (503 tests passing); the gaps are purely in discoverability and documentation accuracy.

The primary issue is that `/system-dev:diagram` exists as a fully implemented command (`commands/diagram.md` + `diagram_generator.py` orchestration) but is missing from the SKILL.md commands table, making it undiscoverable by the LLM agent. Secondary issues are the missing `diagram` slot type in SKILL.md documentation and stale checkboxes in REQUIREMENTS.md and ROADMAP.md.

**Primary recommendation:** This is a straightforward documentation edit phase. Follow the exact pattern established in Phase 6b (which added `/system-dev:view` to SKILL.md) for adding the diagram command and slot type entries.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| XCUT-01 | Partial-state tolerance: gap markers on incomplete input | Already implemented in diagram_generator.py (gap placeholders). Phase 10 ensures SKILL.md documents the diagram command that exposes this capability. |
| XCUT-02 | Structured logging: every agent operation produces structured logs | Already implemented with diagram.* namespace logging. Phase 10 is documentation-only; no new logging needed. |
| XCUT-03 | Externalizable rules: config externalized, not hardcoded | Already implemented (template manifest, view-specs). Phase 10 is documentation-only. |
| XCUT-04 | Slot-api exclusivity: all access through SlotAPI | Already implemented in generate_diagram(). Phase 10 ensures SKILL.md documents the diagram slot type that SlotAPI manages. |
</phase_requirements>

## Standard Stack

Not applicable -- this phase modifies only Markdown documentation files and potentially removes unused Python imports. No new libraries or dependencies.

## Architecture Patterns

### Pattern: SKILL.md Command Table Entry (from Phase 6b)

Phase 6b established the exact pattern for adding a new command to SKILL.md. The commands table at SKILL.md lines 46-56 follows this format:

```markdown
| `/system-dev:diagram` | Generate D2/Mermaid diagrams | [commands/diagram.md](commands/diagram.md) |
```

The command file `commands/diagram.md` already exists with full specification including invocation syntax, parameters, workflow steps, built-in diagram specs, output format, and error handling.

### Pattern: SKILL.md Slot Types Table Entry

The slot types table at SKILL.md lines 59-65 follows this format:

```markdown
| diagram | `diag-` | Generated D2/Mermaid diagram source from view data |
```

This matches `registry.py` which already has:
- `SLOT_TYPE_DIRS`: `"diagram": "diagram"` (line 32)
- `SLOT_TYPE_PREFIXES`: `"diagram": "diag"` (line 51)

### Pattern: Registry Structure Section

The registry structure tree at SKILL.md lines 70-80 needs a `diagrams/` entry:

```
.system-dev/
  registry/
    components/       # One JSON file per component slot
    interfaces/       # One JSON file per interface slot
    contracts/        # One JSON file per contract slot
    requirement-refs/ # One JSON file per requirement-ref slot
    diagrams/         # One JSON file per diagram slot    <-- ADD
  ...
```

### Anti-Patterns to Avoid

- **Over-engineering:** This is a doc fix, not a code change. Do not refactor working code.
- **Incomplete pattern matching:** When adding new entries to tables, match the exact column alignment and link format of existing rows.

## Don't Hand-Roll

Not applicable for a documentation phase.

## Common Pitfalls

### Pitfall 1: Audit Claimed Unused Imports That Are Actually Used
**What goes wrong:** The v1.1 audit (line 148) claims `diagram_generator.py` has "unused imports (copy, defaultdict)". This is **incorrect**.
**Why it happens:** The auditor likely checked an earlier version of the file before `_apply_abstraction_level()` was added in Phase 9.
**How to avoid:** Verify before removing. AST analysis confirms:
- `copy`: Used in `copy.deepcopy(view)` at lines 97 and 100
- `defaultdict`: Used at lines 117, 132, and 171
**Warning signs:** If `ruff` or `pyflakes` does not flag these imports, they are genuinely used.

### Pitfall 2: Stale ROADMAP.md Checkboxes
**What goes wrong:** ROADMAP.md shows Phase 8 plan 08-02 as `[ ]` (unchecked) and Phase 9 plans 09-01, 09-02 as `[ ]` (unchecked), despite all being complete.
**Why it happens:** The gap-closure plan 08-02g replaced 08-02 but the original checkbox was never updated. Phase 9 plans completed but ROADMAP.md was not updated.
**How to avoid:** Mark all completed plan checkboxes as `[x]` and update status columns.

### Pitfall 3: Stale REQUIREMENTS.md Checkboxes
**What goes wrong:** DIAG-01, 02, 03, 04, 06, 09 show `[ ]` in REQUIREMENTS.md despite being verified complete.
**Why it happens:** These were completed during Phase 8 execution but the checkboxes were not updated (the gap-closure plan 08-02g completed the work).
**How to avoid:** Mark all six as `[x]`.

### Pitfall 4: Missing View Slot Type in SKILL.md
**What goes wrong:** The `view` slot type was added in Phase 6b but may or may not be in the slot types table. Verify before assuming.
**How to avoid:** Check current SKILL.md state before editing.

## Code Examples

### SKILL.md Commands Table Addition
```markdown
| `/system-dev:diagram` | Generate D2/Mermaid diagrams | [commands/diagram.md](commands/diagram.md) |
```

### SKILL.md Slot Types Table Addition
```markdown
| diagram | `diag-` | Generated D2/Mermaid diagram source from view data |
```

### SKILL.md Registry Structure Addition
```
    diagrams/         # One JSON file per diagram slot
```

### REQUIREMENTS.md Checkbox Fixes
Change lines for DIAG-01, DIAG-02, DIAG-03, DIAG-04, DIAG-06, DIAG-09 from `[ ]` to `[x]`.

## State of the Art

Not applicable -- this is a documentation cleanup phase, not a technology choice.

## Open Questions

1. **Are there truly unused imports in diagram_generator.py?**
   - What we know: AST analysis and grep both confirm `copy` and `defaultdict` are actively used (3+ usage sites each). The audit claim appears to be based on stale information.
   - Recommendation: Run `ruff check scripts/diagram_generator.py` or `python3 -m pyflakes scripts/diagram_generator.py` during execution to verify. If no unused imports are flagged, skip the "remove unused imports" task entirely and note the audit finding was incorrect.

2. **Should `view` slot type also be in SKILL.md?**
   - What we know: Phase 6b added `/system-dev:view` to the commands table but the `view` slot type may not appear in the slot types table or registry structure section. Views are assembled on-demand rather than stored as registry slots, so this may be intentionally omitted.
   - Recommendation: Check during planning; only add if `view` is in `SLOT_TYPE_DIRS` in registry.py.

## Sources

### Primary (HIGH confidence)
- SKILL.md (current file, lines 46-80) -- exact format patterns for commands table and slot types table
- v1.1-MILESTONE-AUDIT.md -- gap definitions INT-01, INT-02, FLOW-01
- scripts/diagram_generator.py -- verified all imports are used via AST analysis
- scripts/registry.py lines 32, 51 -- confirms diagram slot type registration
- commands/diagram.md -- full command specification already exists
- schemas/diagram.json -- diagram slot schema already exists

### Secondary (MEDIUM confidence)
- Phase 6b pattern (06b-01-PLAN.md context from STATE.md decisions) -- established the pattern for SKILL.md command routing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new tech, documentation only
- Architecture: HIGH - exact patterns already established in Phase 6b
- Pitfalls: HIGH - verified via direct source code analysis (AST, grep)

**Research date:** 2026-03-08
**Valid until:** 2026-04-08 (stable -- documentation patterns do not change)
