# Section 04 Code Review Interview

## Applied Fixes

### Auto-fixed: _validate_dir_path return value captured (Critical)
- All 7 public functions now use `workspace = _validate_dir_path(workspace)`
- Ensures resolved path is used for all file operations, preventing symlink traversal

### Auto-fixed: Protected fields in update_need (Medium)
- Added `_PROTECTED_FIELDS = {"id", "status", "registered_at"}`
- `update_need` now raises ValueError if caller tries to overwrite these fields
- Status changes must go through `defer_need`/`reject_need`

### Auto-fixed: CLI truthiness check (Low)
- Changed `if args.statement:` to `if args.statement is not None:` in CLI update handler
- Allows setting empty string values if needed

## Let Go

- Missing atomic write test: `shared_io._atomic_write` is already tested in `test_update_state.py`
- Duplicate fixture: Intentional - needs tracker fixture has `init` gate True (differs from conftest)
- `update_need` not syncing counts: Plan explicitly says sync on "add, defer, reject" only
- `query_needs` OR semantics: CLI only passes one filter at a time, behavior is reasonable
- Schema version validation: Low risk, can add in future section
- `_sync_counts` silent skip: Appropriate when workspace not initialized
- CLI error handling in main(): Error messages are clear enough from argparse + ValueError
