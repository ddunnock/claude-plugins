# Integration Notes: Opus Review Feedback

## Suggestions INTEGRATED

### 1. State Schema / Resume Granularity (Review #5) — MUST FIX
**Why:** The plan references `state.json` but never shows its template. Without `current_block`, `current_type_pass`, and in-progress tracking, `/reqdev:resume` cannot report granular position. This is foundational.
**Action:** Add `state.json` template to Section 3.1 showing block-level and type-pass-level progress tracking.

### 2. Combinator Rule Noise (Review #6) — MUST FIX
**Why:** Flagging every "and" and "or" will cause quality-checker fatigue and undermine trust. The reviewer is correct that compound subjects ("errors and warnings") are legitimate.
**Action:** Restrict R19 to detect combinators between "shall" clauses only. Downgrade from error to warning severity. Add note that R18 (LLM single-thought check) is the authoritative check.

### 3. Concept Ingestion Parsing Strategy (Review #8) — MUST FIX
**Why:** Parsing free-form LLM-generated Markdown with regex is fragile. The plan doesn't specify the approach, which will cause implementation confusion.
**Action:** Clarify that ingestion is LLM-assisted (Claude reads and extracts, guided by the command prompt) for Markdown documents. The Python script handles only JSON registries (source_registry.json, assumption_registry.json, state.json) which have reliable structure. Add this distinction to Section 3.1.

### 4. Baselining Workflow (Review #11) — MUST FIX
**Why:** Phase 3 requires `status: "baselined"` but no mechanism transitions requirements to that status.
**Action:** Add baselining as a step within `/reqdev:deliver` — after deliverables are approved, all registered requirements transition to "baselined". Add this to Section 3.7 and reference it in Section 5.1.

### 5. Registry Versioning (Review #7) — SHOULD FIX
**Why:** Schema evolution will break existing workspaces silently. Low cost to add, high cost to retrofit later.
**Action:** Add `schema_version` field to all registry JSON files. Add migration check in `init_session.py`.

### 6. ReqIF Dependency Specifics (Review #4) — SHOULD FIX
**Why:** Multiple `reqif` packages exist on PyPI. Unspecified version will cause confusion.
**Action:** Specify `reqif` by strictdoc, pin version, add graceful ImportError handling with install instructions.

### 7. Requirement Withdrawal (Review #14) — SHOULD FIX
**Why:** No mechanism to remove a registered requirement while preserving audit trail. Standard RE practice.
**Action:** Add `withdraw` subcommand to `requirement_tracker.py` with rationale field. Withdrawn requirements excluded from coverage but preserved in registries.

### 8. Manual Mode Specification (Review #15) — SHOULD FIX
**Why:** Without specified interaction pattern, the LLM will improvise differently each session.
**Action:** Add manual mode interaction pattern to `/reqdev:init`: prompt for block names, descriptions, capabilities. Present summary table for approval.

### 9. Passive Voice Whitelist (Review #2) — NICE TO HAVE
**Why:** False positives on words like "green", "open" ending in -en are real. Low cost to add a small whitelist.
**Action:** Add exemption note for common -en adjectives in the R2 rule description. Classify as warning, not error.

### 10. Duplicate Detection Calibration (Review #3) — NICE TO HAVE
**Why:** Word-level n-grams are more semantically meaningful than character-level for short requirement statements.
**Action:** Clarify as word-level n-grams (1+2-grams). Note threshold is tunable and will be calibrated during development.

### 11. Conflict Tracking (Review #13) — NICE TO HAVE
**Why:** Adding a `conflict` link type is low cost and enables structured conflict resolution.
**Action:** Add `conflict` to traceability link types with resolution status and rationale fields.

## Suggestions NOT INTEGRATED

### 12. Scale Limits Documentation (Review #1)
**Why not:** The concept document targets solo developers and small teams. Hundreds of requirements across decomposed subsystems is an edge case for this audience. Adding scale documentation now is premature — better to observe real usage patterns first. The atomic-write pattern already handles the actual crash-safety concern.

### 13. Quality Checker Batching (Review #10)
**Why not:** The plan already specifies metered interaction (2-3 requirements per round). Tier 2 runs per-requirement which is the right granularity for inline quality checking — the whole point is immediate feedback. Batching would break the "inline quality" architectural principle. Token cost is a valid concern but should be managed via model selection (sonnet) rather than changing the interaction pattern.

### 14. Hook Path Pattern (Review #9)
**Why not:** The reviewer acknowledges this matches concept-dev's pattern and is consistent. Changing it preemptively for a hypothetical reorganization violates YAGNI. If deliverables are ever reorganized, the hook pattern is trivially updated.

### 15. HTML Escaping Clarification (Review #12)
**Why not:** The reviewer is technically correct that `html.escape()` in Markdown is unusual, but the plan follows the established codebase pattern (see the recent security commits). Consistency with the existing 66+ scripts that use this pattern is more valuable than theoretical correctness. The real mitigation is that requirement text is treated as data, not as instructions.
