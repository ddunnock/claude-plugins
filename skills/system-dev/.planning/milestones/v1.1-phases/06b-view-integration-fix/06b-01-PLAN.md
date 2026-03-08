---
phase: 06b-view-integration-fix
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - SKILL.md
  - commands/view.md
  - scripts/init_workspace.py
  - tests/test_init_workspace.py
autonomous: true
requirements: []
gap_closure: true

must_haves:
  truths:
    - "/system-dev:view appears in SKILL.md command table and links to commands/view.md"
    - "commands/view.md workflow branches on file path input and calls load_view_spec() with schemas_dir"
    - "init_workspace() creates .system-dev/view-specs/ directory alongside registry dirs"
  artifacts:
    - path: "SKILL.md"
      provides: "Command table entry for /system-dev:view"
      contains: "/system-dev:view"
    - path: "commands/view.md"
      provides: "File-based spec loading branch in workflow"
      contains: "load_view_spec"
    - path: "scripts/init_workspace.py"
      provides: "view-specs/ directory creation"
      contains: "view-specs"
  key_links:
    - from: "SKILL.md"
      to: "commands/view.md"
      via: "command table link"
      pattern: "system-dev:view.*commands/view\\.md"
    - from: "commands/view.md"
      to: "scripts/view_assembler.py"
      via: "load_view_spec() invocation for file paths"
      pattern: "load_view_spec"
---

<objective>
Wire the /system-dev:view command into SKILL.md, add file-based spec loading to the view command workflow, and create view-specs/ directory during workspace init.

Purpose: Close 3 integration gaps and 1 broken flow from the v1.1 audit so file-based view specs work end-to-end.
Output: Updated SKILL.md, commands/view.md, scripts/init_workspace.py with tests.
</objective>

<execution_context>
@/Users/dunnock/.claude/get-shit-done/workflows/execute-plan.md
@/Users/dunnock/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/v1.1-MILESTONE-AUDIT.md
@.planning/phases/06-view-assembly-core/06-02-SUMMARY.md

<interfaces>
<!-- Key functions the executor needs from view_assembler.py -->

From scripts/view_assembler.py:
```python
def load_view_spec(
    spec_path: str,
    parameters: dict | None = None,
    schemas_dir: str | None = None,
) -> dict:
    """Load a view-spec JSON file and resolve parameter placeholders.
    When schemas_dir is provided, validates against view-spec.json schema."""

def get_builtin_spec(name: str, parameters: dict | None = None) -> dict:
    """Look up a built-in view spec by name and resolve parameters."""

def create_ad_hoc_spec(patterns: list[str]) -> dict:
    """Create a transient view spec from ad-hoc inline scope patterns.
    Pattern format: <slot_type>:<name_glob>"""

BUILTIN_SPECS: dict[str, dict]  # Keys: system-overview, traceability-chain, component-detail, interface-map, gap-report
```

From scripts/init_workspace.py:
```python
def init_workspace(project_root: str) -> dict:
    """Create .system-dev/ workspace. Returns dict with status, paths, warnings, cleaned_temps."""
    # registry_dirs list at line 69-80 is where new dirs are added
```

From scripts/shared_io.py:
```python
def ensure_directory(dir_path: str) -> None
def validate_path(path: str, root: str) -> None
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add /system-dev:view to SKILL.md command table</name>
  <files>SKILL.md</files>
  <action>
Add a row to the Commands table in SKILL.md (after the `/system-dev:history` row):

```
| `/system-dev:view` | Assemble a contextual view | [commands/view.md](commands/view.md) |
```

This is the only change needed in SKILL.md. The command file already exists from Phase 6 Plan 02.
  </action>
  <verify>
    <automated>cd /Users/dunnock/projects/claude-plugins/skills/system-dev && grep -q "system-dev:view.*commands/view.md" SKILL.md && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>/system-dev:view appears in SKILL.md command table with correct link to commands/view.md</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Add file-based spec branch to commands/view.md and view-specs/ to init_workspace</name>
  <files>commands/view.md, scripts/init_workspace.py, tests/test_init_workspace.py</files>
  <behavior>
    - Test: init_workspace creates .system-dev/view-specs/ directory
    - Test: init_workspace returns view-specs path in created paths list
    - Test: existing workspace (status=exists) does not fail due to view-specs
  </behavior>
  <action>
**commands/view.md** -- Replace step 1 ("Determine spec") with a 3-way branch:

```
1. **Determine spec**:
   a. If `spec_name_or_pattern` matches a built-in spec name (one of: system-overview, traceability-chain, component-detail, interface-map, gap-report), use `get_builtin_spec()`.
   b. If `spec_name_or_pattern` is a file path (ends with `.json` or contains `/`), load it with `load_view_spec(spec_path, parameters, schemas_dir)` where `schemas_dir` is `${CLAUDE_PLUGIN_ROOT}/schemas`. This enables schema validation of user-authored specs.
   c. Otherwise, treat it as an ad-hoc scope pattern and call `create_ad_hoc_spec()`.
```

Also update the Invocation section to mention file paths:
```
- `spec_name_or_pattern` (required): Name of a built-in spec, a file path to a view-spec JSON file (e.g., `.system-dev/view-specs/my-spec.json`), OR an ad-hoc scope pattern (e.g., `component:Auth*`)
```

Also add a "File-Based Specs" section after "Built-in Views" explaining that users can create custom view-spec JSON files in `.system-dev/view-specs/` and invoke them by path.

**scripts/init_workspace.py** -- Add `"view-specs"` to the `registry_dirs` list (line ~69-80). Despite the variable name `registry_dirs`, this is the list of all subdirectories created under `.system-dev/`. Add it after the `registry/` entries:

```python
registry_dirs = [
    "registry/components",
    "registry/interfaces",
    "registry/contracts",
    "registry/requirement-refs",
    "registry/needs",
    "registry/requirements",
    "registry/sources",
    "registry/assumptions",
    "registry/traceability-links",
    "registry/component-proposals",
    "view-specs",  # User-authored view specifications
]
```

**tests/test_init_workspace.py** -- Add a test that verifies `.system-dev/view-specs/` is created by `init_workspace()` and appears in the returned paths list. Follow the existing test patterns in this file.
  </action>
  <verify>
    <automated>cd /Users/dunnock/projects/claude-plugins/skills/system-dev && uv run python -m pytest tests/test_init_workspace.py -x -q 2>&1 | tail -5</automated>
  </verify>
  <done>
    - commands/view.md step 1 has 3 branches: built-in, file path, ad-hoc pattern
    - commands/view.md mentions load_view_spec() with schemas_dir for file-based specs
    - init_workspace() creates view-specs/ directory
    - Tests pass confirming view-specs/ creation
  </done>
</task>

</tasks>

<verification>
1. `grep "system-dev:view" SKILL.md` shows command table entry
2. `grep "load_view_spec" commands/view.md` shows file-based spec branch
3. `grep "view-specs" scripts/init_workspace.py` shows directory creation
4. `uv run python -m pytest tests/test_init_workspace.py -x -q` passes
5. `uv run python -m pytest tests/ -x -q` full regression passes
</verification>

<success_criteria>
- /system-dev:view is routable from SKILL.md command table
- File-based view spec flow is documented in commands/view.md with load_view_spec() + schemas_dir
- init_workspace() creates .system-dev/view-specs/ for user-authored specs
- All existing tests continue to pass
</success_criteria>

<output>
After completion, create `.planning/phases/06b-view-integration-fix/06b-01-SUMMARY.md`
</output>
