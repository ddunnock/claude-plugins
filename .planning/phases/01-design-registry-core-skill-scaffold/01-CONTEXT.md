# Phase 1: Design Registry Core + Skill Scaffold - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Foundation infrastructure for the AI-Assisted Systems Design Platform. Delivers a working Design Registry with CRUD operations, schema validation, change tracking, and version history. Also delivers the complete skill scaffold (SKILL.md, directories, security rules) ready for agent development in subsequent phases.

</domain>

<decisions>
## Implementation Decisions

### Storage format & structure
- JSON files per slot, one .json file per design element
- Directory organization by slot type: `.system-dev/registry/components/`, `.system-dev/registry/interfaces/`, etc.
- Atomic writes via write-to-temp + rename strategy (write to .tmp, then atomic rename; orphaned .tmp on crash, original stays intact)
- Workspace at `.system-dev/` relative to project root (mirrors `.requirements-dev/` convention)

### Slot schema & type system
- Strict core fields + free-form `extensions` object per slot type
- Schema definitions as JSON Schema files shipped with the skill (e.g., `schemas/component.json`)
- Phase 1 defines core types only: component, interface, contract, requirement-ref (more added as later phases need them)
- Validation errors are detailed: exact field path + fix hint (e.g., "Field components[0].name is required. Add a name string to identify this component.")

### Change journal & versioning
- Append-only JSONL file at `.system-dev/journal.jsonl`, one JSON object per line per mutation
- Monotonic integer versioning per slot (v1, v2, v3...) for optimistic locking and conflict detection
- Each journal entry includes: timestamp, slot_id, slot_type, operation (create/update/delete), version_before, version_after, agent_id, summary, plus full JSON diff (RFC 6902 patch)
- Old versions reconstructed from journal diffs only (no snapshot files preserved); current version is the only file on disk

### Skill invocation & UX
- Command prefix: `/system-dev` (e.g., `/system-dev:init`, `/system-dev:status`)
- Explicit `/system-dev:init` command required to create `.system-dev/` workspace — no auto-init on first use
- Output format: structured markdown (headers, tables, bullet points) for human-readable terminal output
- SKILL.md contains overview, triggers, and command index (under 500 lines); each command's detailed workflow in `commands/` directory (e.g., `commands/init.md`, `commands/status.md`)

### Claude's Discretion
- Exact directory structure under `.system-dev/` beyond `registry/` and `journal.jsonl`
- JSON Schema draft version and validation library choice
- Internal code organization (modules, utilities)
- Error recovery strategy for orphaned .tmp files

</decisions>

<specifics>
## Specific Ideas

- Mirror `.requirements-dev/` conventions where applicable (directory naming, file organization) for consistency across the skill family
- Progressive disclosure from SKILL.md should follow the same pattern as the requirements-dev skill
- Schema validation should feel helpful, not punitive — guide the user to fix issues rather than just rejecting writes

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-design-registry-core-skill-scaffold*
*Context gathered: 2026-02-28*
