# Section 02 Code Review Interview

## Findings Triage

| # | Finding | Severity | Action | Result |
|---|---------|----------|--------|--------|
| 1 | --state arg not path-validated | Critical | Auto-fix | Added _validate_path call in main() |
| 2 | pass_gate ignores unknown gates | Critical | Auto-fix | Added ValueError for unknown gates |
| 3 | Schema version check on resume missing | Critical | Auto-fix | Added version comparison in init_workspace |
| 4 | Duplicated _atomic_write | High | Asked user | User chose: extract to shared_io.py |
| 5 | TBD/TBR counting logic fragile | High | Let go | Registry format not yet defined |
| 6 | update_field allows arbitrary writes | High | Let go | Internal tool, called by other scripts |
| 7 | check-gate exit code untested | Medium | Auto-fix | Added via pass_gate validation test |
| 8 | sync-counts missing registry test | Medium | Auto-fix | Added test_sync_counts_with_no_registries |
| 9 | show() missing traceability | Medium | Auto-fix | Added traceability line to show() |
| 10 | Traversal check bypassable | Medium | Auto-fix | Changed to Path.parts check |
| 11 | CLI validation inconsistency | Medium | Auto-fix | Added choices= to pass-gate/check-gate |
| 12 | conftest sys.path manipulation | Minor | Let go | Works for current setup |
| 13 | Fixture naming inconsistency | Minor | Let go | tmp_workspace is more descriptive |

## Interview Decisions

### Finding 4: Duplicated _atomic_write
**Question:** Extract to shared module or keep duplicated?
**User decision:** Extract to shared module
**Action taken:** Created scripts/shared_io.py with _atomic_write, _validate_path, _validate_dir_path. Both scripts import from it.

## Auto-Fixes Applied
- Created scripts/shared_io.py with shared utilities
- Added schema version check in init_workspace resume path
- pass_gate now raises ValueError for unknown gates
- Added VALID_GATES constant, CLI choices= for pass-gate and check-gate
- show() now includes traceability coverage line
- Path validation uses Path.parts instead of str.split(os.sep)
- Added 3 new tests (19 total, up from 16)
