# Skill Anti-Patterns Catalog

Reference for skill-tester code review. These are known failure modes observed in skill scripts
that cause subtle bugs, poor maintainability, or unreliable behavior when skills are tested or
composed.

---

## AP-001: Stdout Pollution

**Pattern:** Debug `print()` statements mixed into scripts that produce structured JSON output.

**Why it breaks things:** The test harness and calling code parses stdout as JSON. A stray
`print("debugging now")` before the JSON output causes a parse failure.

**Detection:** Look for `print(...)` in scripts that also use `json.dumps()` to write to stdout.

**Fix:** Use `print(..., file=sys.stderr)` for all diagnostic output. Reserve stdout for the
structured payload.

---

## AP-002: Hardcoded Session Paths

**Pattern:**
```python
output_dir = "/home/user/skill-runs/output"
log_file = "/tmp/skill-debug.log"
```

**Why it breaks things:** Fails on any machine other than the developer's. Fails in CI.
Causes collisions when multiple test runs occur.

**Fix:** Accept paths as CLI arguments with sensible defaults:
```python
parser.add_argument("--output-dir", default="session/output")
```

---

## AP-003: Missing Exit Code on Failure

**Pattern:**
```python
except Exception as e:
    print(f"Error: {e}")
    # falls through, exits 0
```

**Why it breaks things:** The script runner sees exit code 0 and marks the run as successful
even though nothing was produced. Silent failures are the worst kind.

**Fix:**
```python
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

---

## AP-004: No `--help` / Missing Argparse

**Pattern:** Script uses `sys.argv[1]` directly without argparse.

**Why it breaks things:** The script runner calls `--help` as a dry-run to discover the
script's interface. Without argparse, this fails. Also makes scripts opaque to maintainers.

**Fix:** Always use `argparse.ArgumentParser` with descriptions.

---

## AP-005: Append-Mode Duplicates

**Pattern:**
```python
with open("results.jsonl", "a") as f:
    f.write(json.dumps(result) + "\n")
```
Run twice → duplicate entries.

**Why it breaks things:** Test reruns accumulate data. Downstream readers see duplicates.

**Fix:** Either truncate on start, or use a unique run ID as a key and deduplicate on read.
Or document clearly that append behavior is intentional (e.g., event log).

---

## AP-006: Monolithic Scripts

**Pattern:** A 600-line script with one main() function and no helper functions.

**Why it breaks things:** Impossible to unit test, hard to modify, context-expensive to
review.

**Fix:** Break into logical functions of < 50 lines each. For very long scripts, split into
modules and have a thin CLI entry point.

---

## AP-007: Undocumented Output Schema

**Pattern:** Script produces JSON but there's no docstring, comment, or reference file
explaining the structure.

**Why it breaks things:** Every consumer of the output has to reverse-engineer the schema.
When the schema changes, nothing documents what changed or why.

**Fix:** Add a comment block above the output-writing code:
```python
# Output schema: {"result": str, "score": float, "issues": [{"line": int, "text": str}]}
```
Or reference a schema file.

---

## AP-008: Env Var Assumptions Without Checks

**Pattern:**
```python
client = anthropic.Anthropic()  # implicitly needs ANTHROPIC_API_KEY
```
No check, no documentation, no helpful error if missing.

**Fix:**
```python
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)
client = anthropic.Anthropic(api_key=api_key)
```

---

## AP-009: Unguarded `shutil.rmtree`

**Pattern:**
```python
shutil.rmtree(output_dir)
os.makedirs(output_dir)
```
If `output_dir` is misconfigured (e.g., points to `/`), data loss occurs.

**Fix:**
```python
output_dir = Path(output_dir).resolve()
if not str(output_dir).startswith(str(base_dir)):
    raise ValueError(f"Output dir {output_dir} is outside allowed base {base_dir}")
if output_dir.exists():
    shutil.rmtree(output_dir)
```

---

## AP-010: Non-Pinned Anthropic SDK Version

**Pattern:**
```
# requirements.txt
anthropic
```

**Why it breaks things:** The Anthropic SDK changes API significantly between major versions.
A skill that works on 0.28.x may silently fail on 0.40.x.

**Fix:**
```
anthropic>=0.28.0,<1.0.0
```

---

## AP-011: SKILL.md / Script Drift

**Pattern:** SKILL.md references `scripts/generate_report.py` but the actual file is
`scripts/report_generator.py`, or the expected CLI args differ.

**Why it breaks things:** Claude follows SKILL.md instructions and calls the wrong script
or passes wrong arguments. Fails silently or with a confusing error.

**Detection:** Cross-reference every script filename and CLI arg mentioned in SKILL.md
against the actual files and their argparse definitions.

**Fix:** Keep SKILL.md in sync. Add a validation step to the skill's test suite.

---

## AP-012: Relative Imports in Runnable Scripts

**Pattern:**
```python
from ..utils import helper_function
```
in a script that's also meant to be run directly.

**Why it breaks things:** Relative imports only work when the module is imported as part of
a package. Direct execution (`python scripts/foo.py`) causes `ImportError`.

**Fix:** Use absolute imports, or add a `__init__.py` and always run via
`python -m scripts.foo`.
