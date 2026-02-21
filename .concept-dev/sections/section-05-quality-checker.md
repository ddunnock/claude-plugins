Now I have enough context. Let me produce the section content.

# Section 05: Quality Checker

## Overview

This section implements the deterministic quality rules engine (`quality_rules.py`) and the quality-checker agent prompt (`agents/quality-checker.md`). The quality checker applies INCOSE GtWR v4 rules to requirement statements before registration. It has a two-tier architecture:

- **Tier 1 (Deterministic):** A standalone Python script (`quality_rules.py`) that checks requirement text against 21 rules using regex and string matching. No external dependencies -- pure stdlib.
- **Tier 2 (LLM-Assisted):** An agent (`quality-checker.md`, sonnet model) that evaluates 9 semantic rules using Chain-of-Thought prompting.

## Dependencies

- **section-02-state-management:** The quality checker needs the workspace to exist (`.requirements-dev/`) but does not directly modify `state.json`. It reads data files from the plugin directory.
- **section-01-plugin-scaffolding:** The data files (`data/vague_terms.json`, `data/escape_clauses.json`, `data/absolutes.json`, `data/pronouns.json`) and the `references/incose-rules.md` file must exist. These are created during scaffolding.

## Files to Create

| File | Purpose |
|------|---------|
| `skills/requirements-dev/scripts/quality_rules.py` | Deterministic INCOSE rule engine (21 rules) |
| `skills/requirements-dev/agents/quality-checker.md` | LLM-assisted semantic quality checks (9 rules) |
| `skills/requirements-dev/tests/test_quality_rules.py` | Golden tests for all deterministic rules + CLI |

## Tests First

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_quality_rules.py`**

All tests are golden tests: known-good and known-bad requirement statements with expected violations. The test file should import `check_requirement` and `Violation` from `quality_rules`, plus helpers for CLI testing.

```python
"""Golden tests for INCOSE deterministic quality rules.

Each test provides a requirement statement and asserts the expected
violations (or absence thereof). Tests are grouped by rule ID.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Import paths - adjust if conftest handles this
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from quality_rules import check_requirement, check_rule, list_rules, Violation


# --- Vague terms (R7) ---

# Test: "The system shall provide appropriate error handling" -> flags "appropriate"
# Test: "The system shall provide structured error responses" -> no R7 violation
# Test: "Several modules shall be loaded" -> flags "several"


# --- Escape clauses (R8) ---

# Test: "The system shall, where possible, cache results" -> flags "where possible"
# Test: "The system shall cache all query results" -> no R8 violation


# --- Open-ended clauses (R9) ---

# Test: "The system shall support formats including but not limited to JSON" -> flags clause
# Test: "The system shall support JSON, XML, and CSV formats" -> no R9 violation


# --- Combinators (R19) ---

# Test: "The system shall log errors and shall send alerts" -> flags (shall...and...shall)
# Test: "The system shall log errors and warnings" -> no R19 violation (compound subject OK)
# Test: "The system shall respond or shall queue the request" -> flags (shall...or...shall)


# --- Pronouns (R24) ---

# Test: "It shall respond within 200ms" -> flags "it"
# Test: "The API Gateway shall respond within 200ms" -> no R24 violation


# --- Absolutes (R26) ---

# Test: "The system shall always be available" -> flags "always"
# Test: "The system shall maintain 99.9% availability" -> no R26 violation


# --- Passive voice (R2) ---

# Test: "Errors shall be logged by the system" -> flags passive (be...logged)
# Test: "The system shall log errors" -> no R2 violation
# Test: "The indicator shall be green when ready" -> no R2 violation (whitelist: "green")
# Test: "The port shall be open for connections" -> no R2 violation (whitelist: "open")


# --- Purpose phrases (R20) ---

# Test: "The system shall cache results in order to improve latency" -> flags "in order to"


# --- Parentheses (R21) ---

# Test: "The system shall return status codes (200, 404, 500)" -> flags parentheses


# --- Logical and/or (R15, R17) ---

# Test: "The system shall accept JSON and/or XML" -> flags "and/or"


# --- Negatives (R16) ---

# Test: "The system shall not expose internal errors" -> flags "not"


# --- Superfluous infinitives (R10) ---

# Test: "The system shall be able to process 1000 requests" -> flags "be able to"


# --- Temporal dependencies (R35) ---

# Test: "The cache shall be invalidated before serving new data" -> flags "before"


# --- Universal quantifiers (R32) ---

# Test: "Every endpoint shall require authentication" -> flags "every"


# --- CLI interface ---

# Test: check subcommand returns JSON array of violations
# Test: check-all with registry file processes all requirements
# Test: rules subcommand lists all available rules with IDs
# Test: check with clean requirement returns empty violations array
```

Each commented test stub should be implemented as a `test_` function. The pattern for each is:

1. Call `check_requirement(statement)` and get back a `list[Violation]`.
2. For violation-expected tests: assert at least one `Violation` has the expected `rule_id` and that `matched_text` contains the flagged term.
3. For clean tests: assert no `Violation` with that `rule_id` exists in the result.
4. For CLI tests: use `subprocess.run` to invoke `quality_rules.py` with the appropriate subcommand and parse JSON stdout.

## Implementation Details

### Data Files (prerequisite from section-01)

These files are created during scaffolding but their content is critical to this section. Each is a JSON array of strings.

**`/Users/dunnock/projects/claude-plugins/skills/requirements-dev/data/vague_terms.json`**

Contains approximately 20 vague terms from INCOSE GtWR v4: `"some"`, `"any"`, `"allowable"`, `"several"`, `"many"`, `"a lot of"`, `"a few"`, `"almost always"`, `"very nearly"`, `"nearly"`, `"about"`, `"close to"`, `"adequate"`, `"sufficient"`, `"appropriate"`, `"suitable"`, `"reasonable"`, `"normal"`, `"common"`, `"typical"`.

**`/Users/dunnock/projects/claude-plugins/skills/requirements-dev/data/escape_clauses.json`**

Contains approximately 10 escape clause phrases: `"so far as is possible"`, `"as little as possible"`, `"as much as possible"`, `"if it should prove necessary"`, `"where possible"`, `"if practicable"`, `"as appropriate"`, `"as required"`, `"to the extent possible"`.

**`/Users/dunnock/projects/claude-plugins/skills/requirements-dev/data/absolutes.json`**

Contains 6 absolute terms: `"always"`, `"never"`, `"every"`, `"all"`, `"none"`, `"no"`.

**`/Users/dunnock/projects/claude-plugins/skills/requirements-dev/data/pronouns.json`**

Contains approximately 10 pronouns: `"it"`, `"they"`, `"them"`, `"this"`, `"that"`, `"these"`, `"those"`, `"which"`, `"its"`.

### Tier 1: Deterministic Quality Rules Engine

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/quality_rules.py`**

The script is both a CLI tool and an importable module. It uses only Python stdlib (`json`, `re`, `argparse`, `sys`, `pathlib`, `os`, `dataclasses`).

#### Core Data Structures

```python
@dataclass
class Violation:
    """A single quality rule violation found in a requirement statement."""
    rule_id: str        # e.g., "R7"
    rule_name: str      # e.g., "Vague terms"
    severity: str       # "error" or "warning"
    matched_text: str   # The text that triggered the violation
    position: int       # Character offset in the statement
    suggestion: str     # Suggested rewrite or action

@dataclass
class RuleInfo:
    """Metadata about an available quality rule."""
    rule_id: str
    rule_name: str
    severity: str
    description: str
    detection_tier: str  # "deterministic" or "llm"
```

#### Module Interface

Three public functions for agent integration:

```python
def check_requirement(statement: str) -> list[Violation]:
    """Run all deterministic INCOSE checks on a requirement statement.

    Loads word lists from data/*.json files relative to the script location.
    Returns list of Violation objects sorted by position in statement.
    """

def check_rule(statement: str, rule_id: str) -> Violation | None:
    """Run a single rule check. Returns Violation if triggered, None otherwise."""

def list_rules() -> list[RuleInfo]:
    """Return metadata for all available deterministic rules."""
```

#### Rule Implementations

Each rule is implemented as an internal function with signature `_check_rXX(statement: str) -> list[Violation]`. The rules and their detection approaches:

1. **R7 (Vague terms):** Load `data/vague_terms.json`. For each term, use word-boundary regex `\b{term}\b` (case-insensitive) to find matches. Multi-word terms (e.g., "a lot of") use phrase matching.

2. **R8 (Escape clauses):** Load `data/escape_clauses.json`. Use case-insensitive substring matching for each phrase. These are multi-word phrases so word-boundary regex is not needed.

3. **R9 (Open-ended clauses):** Regex patterns for `including but not limited to`, `\betc\.`, `and so on`, `such as` (when defining scope), `for example` (when defining scope).

4. **R19 (Combinators):** Regex to detect multiple "shall" clauses joined by "and" or "or": pattern `shall\s+.+?\s+(and|or)\s+.+?shall` (case-insensitive). This catches "shall X and shall Y" but not "shall handle errors and warnings" (compound objects). Severity: **warning** (not error).

5. **R24 (Pronouns):** Load `data/pronouns.json`. Word-boundary regex `\b{pronoun}\b` (case-insensitive). Match at word boundaries to avoid false positives in longer words.

6. **R26 (Absolutes):** Load `data/absolutes.json`. Word-boundary regex. Note: "all" and "no" need careful boundary handling to avoid matching inside other words.

7. **R2 (Passive voice):** Heuristic pattern. Match forms of "be" (`is|are|was|were|been|being|be`) followed within 3 words by a past participle (word ending in `-ed` or `-en`). Exemption whitelist: `{"open", "green", "broken", "driven", "written", "given"}` -- these are commonly used as predicative adjectives, not passive voice indicators. Severity: **warning**.

8. **R20 (Purpose phrases):** Regex for `in order to`, `so that`, `to ensure`, `for the purpose of`.

9. **R21 (Parentheses):** Regex `\(.*?\)` to detect any parenthetical content in the statement.

10. **R15/R17 (Logical and/or):** Regex for literal `and/or` and oblique `/` used as conjunction between words.

11. **R16 (Negatives):** Regex `\bnot\b` to flag negative requirements for review. Severity: **warning**.

12. **R10 (Superfluous infinitives):** Regex for `be able to` and `be capable of`.

13. **R35 (Temporal dependencies):** Keyword matching for `before`, `after`, `during`, `while`, `when`. Severity: **warning** (flags for review, not necessarily wrong).

14. **R32 (Universal quantifiers):** Word-boundary regex for `each`, `every`, `all`, `any`. Severity: **warning**.

15. **R40 (Decimal format):** Regex for inconsistent numeric formats (e.g., mixing comma and dot separators).

16. **R33 (Range checking):** Pattern matching for numeric ranges with missing units or bounds (e.g., "between 5 and 10" without units).

#### Data File Loading

The script resolves data file paths relative to its own location using `Path(__file__).parent.parent / "data"`. Word lists are loaded lazily on first use and cached in module-level variables.

#### CLI Interface

The script uses `argparse` with subcommands:

```bash
# Check a single requirement statement
python3 quality_rules.py check "The system shall handle requests appropriately."
# Output: JSON array of Violation dicts

# Check all requirements in a registry file
python3 quality_rules.py check-all --registry /path/to/requirements_registry.json
# Output: JSON object mapping requirement IDs to their violation arrays

# List all available rules
python3 quality_rules.py rules
# Output: JSON array of RuleInfo dicts
```

The `check-all` subcommand reads a requirements registry JSON file, extracts the `statement` field from each requirement, runs `check_requirement` on each, and maps results by requirement ID.

#### Path Validation

Following the established codebase pattern, include `_validate_path()` for the `check-all` subcommand's `--registry` argument. Reject `..` traversal and restrict to `.json` extension.

#### Security

- All user-provided requirement text is treated as data, never evaluated
- File paths validated before opening
- No network access

### Tier 2: LLM-Assisted Quality Checker Agent

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/agents/quality-checker.md`**

This is a prompt file for a sonnet-model agent. It is invoked by the `/reqdev:requirements` command after Tier 1 passes. The agent is not unit-tested (it is LLM-driven); correctness relies on the prompt engineering and few-shot examples.

The agent prompt should contain:

1. **Role definition:** You are a requirements quality checker applying INCOSE GtWR v4 semantic rules.

2. **Input specification:** The agent receives the requirement statement, its context (block name, requirement type, parent need statement), and optionally the full set of previously registered requirements for terminology consistency checking (R36).

3. **Rules to evaluate (9 rules):**
   - R31 (Solution-free): Does the requirement prescribe a specific solution or implementation?
   - R34 (Measurable): Are performance/quality criteria quantifiable and testable?
   - R18 (Single thought): Does the statement contain exactly one requirement?
   - R1 (Structured): Does it follow "The [subject] shall [action]" pattern?
   - R11 (Separate clauses): Are conditions properly separated from the main requirement?
   - R22 (Enumeration): Are lists complete and exhaustive?
   - R27 (Explicit conditions): Are all trigger conditions explicitly stated?
   - R28 (Multiple conditions): Are nested if/then/else conditions clear?
   - R36 (Consistent terms): Is terminology consistent with other requirements in the set?

4. **Few-shot examples:** 12-20 validated examples with rationales drawn from `references/incose-rules.md`. Each example shows a requirement statement, the rule being evaluated, the assessment (pass or flag), confidence level, reasoning chain, and suggested rewrite if flagged.

5. **Output format:** JSON array of findings, each with:
   - `rule_id`: string (e.g., "R31")
   - `assessment`: "pass" or "flag"
   - `confidence`: "high", "medium", or "low"
   - `reasoning`: string (Chain-of-Thought explanation)
   - `suggestion`: string (rewrite if flagged, empty if pass)

6. **Confidence gating:** Only high-confidence flags should block registration. Medium/low flags are presented as informational findings for human review.

7. **Tool access:** The agent should be able to call `quality_rules.py check` for cross-referencing deterministic results if needed.

### Quality Check Flow (integration context)

This flow is orchestrated by the `/reqdev:requirements` command (section-07), not by this section. However, understanding it informs the interface design:

1. Run Tier 1 (`check_requirement(statement)`) -- immediate deterministic results
2. If Tier 1 passes: invoke quality-checker agent for Tier 2 semantic checks
3. Present all violations to user with suggested rewrites
4. User resolves each (accept rewrite, provide own, or justify override)
5. Re-run Tier 1 on any rewritten statement to confirm resolution
6. Registration proceeds only when Tier 1 passes and Tier 2 flags are resolved/acknowledged

## Implementation Notes

- The `check_requirement` function must be pure and side-effect-free. It takes a string and returns violations. It does not read state, modify files, or print to stdout.
- The CLI wrapper handles I/O (reading registries, printing JSON output).
- Word list files are small (under 50 items each) and loaded into memory once per process invocation.
- The passive voice heuristic (R2) will have false positives. That is why it is severity "warning" not "error". The whitelist can be expanded over time.
- The R19 combinator check is intentionally conservative. It only flags `shall...and/or...shall` patterns. The LLM tier's R18 (Single thought) is the authoritative detector for compound requirements.
- For R15/R17 (and/or), the oblique "/" detection should only flag when "/" appears between words (not in paths or URLs). Use pattern `\w+/\w+` and exclude common non-conjunction patterns.
- R35 (Temporal) and R32 (Quantifiers) are informational warnings, not errors. They flag statements for human review of potential issues.

---

## Implementation Notes (Actual)

### Files Created/Modified
- `skills/requirements-dev/scripts/quality_rules.py` -- 16 deterministic rules (not 21 as plan claimed), pure stdlib
- `skills/requirements-dev/agents/quality-checker.md` -- 9 semantic LLM rules with JSON output format
- `skills/requirements-dev/tests/test_quality_rules.py` -- 32 golden tests (rule tests + CLI tests)

### Deviations from Plan
- **Rule count:** Plan said 21 deterministic rules but only detailed 16. Implemented the 16 that were specified: R2, R7, R8, R9, R10, R15, R16, R19, R20, R21, R24, R26, R32, R33, R35, R40
- **R15/R17 merged:** Plan mentioned R15 and R17 separately for "and/or" and oblique "/" -- implemented only R15 for literal `and/or`, skipped oblique "/" detection (too many false positives in technical requirements)
- **R2 whitelist expanded:** Original plan listed 6 whitelist entries. Expanded to ~20 to handle words ending in "en" that aren't past participles (when, then, often, golden, etc.)
- **R19 regex fixed:** Added `re.DOTALL` flag and word boundaries on `and|or` to correctly match multi-line combinators
- **_validate_path security fix:** Changed to check resolved path (not original) for `..` traversal to prevent symlink bypass
- **Agent prompt simplified:** Omitted few-shot examples from the agent prompt to keep it focused; the rules themselves contain flag/pass examples

### Test Count: 32 tests, all passing
### Total test count across project: 74 tests, all passing