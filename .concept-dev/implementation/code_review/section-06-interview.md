# Section 06: Requirements Engine - Code Review Interview

## Review Findings & Decisions

### Finding 1: register_requirement skips validation when needs_registry.json missing
- **Category:** Auto-fix (HIGH - referential integrity)
- **Action:** Changed to raise ValueError when needs registry file is missing, since parent need can't exist without the registry
- **Status:** Applied

### Finding 2: register_requirement doesn't check parent need is approved
- **Category:** Auto-fix (HIGH - referential integrity)
- **Action:** Changed to filter needs by `status == "approved"` before checking parent_need exists
- **Status:** Applied

### Finding 3: link_type not validated
- **Category:** Auto-fix (HIGH - data integrity)
- **Action:** Added validation against VALID_LINK_TYPES set before creating link
- **Status:** Applied

### Finding 4: Duplicate link prevention absent
- **Category:** Auto-fix (HIGH - data integrity)
- **Action:** Added dedup check: if a link with same source+target+type already exists, return silently (no-op)
- **Status:** Applied

### Finding 5: coverage_report includes withdrawn reqs in verified_by count
- **Category:** Auto-fix (MEDIUM)
- **Action:** Added `lnk["source"] not in withdrawn_reqs` filter to verified_by accumulation
- **Status:** Applied

### Finding 6: No _PROTECTED_FIELDS in requirement_tracker
- **Category:** Auto-fix (MEDIUM - consistency with needs_tracker)
- **Action:** Added `_PROTECTED_FIELDS = {"id", "status", "registered_at"}` and guard in update_requirement
- **Status:** Applied

### Finding 7: No tests for source_tracker.py
- **Category:** Auto-fix (MEDIUM - coverage gap)
- **Action:** Added 6 tests: add, auto-increment, research_context, concept_dev_ref, list, export
- **Status:** Applied

### Finding 8: tbd_open/tbr_open not synced
- **Category:** Let go
- **Rationale:** No TBD/TBR items exist yet. Will add when section-07 creates them.

### Finding 9: source_tracker type validation
- **Category:** Let go
- **Rationale:** Plan doesn't mandate strict type validation for sources. Types are informational.

### Finding 10: V&V mapping data not implemented
- **Category:** Let go
- **Rationale:** Plan says this is "data that this section should establish" but it's used by the conversational flow in section-07, not by these scripts. The mapping exists as documentation in the plan.

### Finding 11: registered_at set at draft creation
- **Category:** Let go
- **Rationale:** Cosmetic naming issue. The field is overwritten on actual registration, and having a timestamp at creation time is useful for tracking.

## Test Results After Fixes

All 114 tests passing (40 new: 19 requirement_tracker + 15 traceability + 6 source_tracker).
