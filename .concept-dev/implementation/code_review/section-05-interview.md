# Section 05: Quality Checker - Code Review Interview

## Review Findings & Decisions

### Finding 1: Docstring claims 21 rules, only 16 implemented
- **Category:** Auto-fix
- **Action:** Changed docstring from "21 deterministic INCOSE GtWR v4 quality rules" to "16 deterministic INCOSE GtWR v4 quality rules"
- **Status:** Applied

### Finding 2: R2 passive voice whitelist checks intervening words incorrectly
- **Category:** Auto-fix (bug)
- **Issue:** The R2 regex `be_forms + \s+((?:\w+\s+){0,2})(\w+(?:ed|en))\b` captures up to 2 intervening words before the participle. The original code checked ALL matched words against the whitelist, meaning a legitimate passive could be skipped if an intervening adverb happened to be in the whitelist.
- **Action:** Changed to only check the participle (group 2) against the whitelist. Expanded whitelist with words ending in "en" that aren't past participles: "when", "then", "often", "golden", "widen", "lessen", "flatten".
- **Status:** Applied

### Finding 3: `_validate_path` checks original path, not resolved
- **Category:** Auto-fix (security)
- **Issue:** `_validate_path()` checked the original filepath for `..` traversal but used `os.path.realpath()` to resolve symlinks. A symlink could bypass the `..` check.
- **Action:** Changed to check the resolved path's parts for `..` traversal instead of the original path.
- **Status:** Applied

### Finding 4: Missing `check-all` CLI test
- **Category:** Auto-fix (coverage gap)
- **Action:** Added `test_cli_check_all_processes_registry` test that creates a temp registry with 2 requirements and verifies the check-all subcommand produces correct JSON output.
- **Status:** Applied

## Test Results After Fixes

All 74 tests passing (32 quality rules + 42 from prior sections).
