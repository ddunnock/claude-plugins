# Section 07 Code Review Interview

## Auto-fixes Applied

### Fix 1: `_parse_value` JSON array handling (Critical)
- Issue: `_parse_value()` doesn't handle JSON arrays/objects, causing `requirements_in_draft` to be stored as a string
- Fix: Add `json.loads()` attempt before string fallback in `_parse_value`
- Also fix the test to assert `isinstance(list)` instead of relying on string containment

### Fix 2: Regression test for sync_counts fix
- Issue: No dedicated test verifying sync_counts handles dict-wrapped registries
- Fix: Add targeted regression test

### Fix 3: `update_requirement` unknown field validation
- Issue: Silently ignores unknown field names
- Fix: Raise ValueError for fields not in the Requirement dataclass
- User decision: Add ValueError for unknowns

## Items Let Go
- #4: Quality blocking is by-design a Claude instruction, not code enforcement
- #5: V&V planning is a Claude instruction, not testable
- #7: Reference files already exist
- #8: --state dual-mode is working as designed
