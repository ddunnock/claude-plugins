# Python Anti-Patterns Reference

> **Purpose**: Detailed detection patterns and remediation for Python anti-patterns
> **Parent**: `python.md` (Section 13)
> **Usage**: Reference for antipattern-detector agent and /lint command

---

## Detection Patterns

Use these patterns to identify anti-patterns in code review:

### AP-PY-01: Mutable Default Arguments

**Detection**:
```python
# Pattern: def func(arg=[]) or def func(arg={}) or def func(arg=SomeClass())
Pattern: /def\s+\w+\([^)]*=\s*(\[\]|\{\}|\w+\(\))/g
```

**Severity**: HIGH
**Auto-fixable**: Yes

**Why It's Dangerous**:
- Default mutable objects are created once at function definition
- Shared across all calls without explicit argument
- Leads to mysterious state accumulation bugs

**Remediation**:
```python
# ❌ Bad
def append_item(item, items=[]):
    items.append(item)
    return items

# ✅ Good
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

### AP-PY-02: Bare `except` Clauses

**Detection**:
```python
Pattern: /except\s*:/g
Pattern: /except\s+Exception\s*:/g (catches too broadly)
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Dangerous**:
- Catches `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`
- Hides bugs and makes debugging impossible
- Prevents graceful shutdown

**Remediation**:
```python
# ❌ Bad
try:
    risky_operation()
except:
    pass

# ✅ Good
try:
    risky_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Operation failed: {e}")
    raise
```

---

### AP-PY-03: Using `type()` Instead of `isinstance()`

**Detection**:
```python
Pattern: /type\(\w+\)\s*==\s*/g
Pattern: /type\(\w+\)\s*is\s+/g
```

**Severity**: MEDIUM
**Auto-fixable**: Yes

**Why It's Wrong**:
- Breaks inheritance (subclasses won't match)
- Less Pythonic
- Doesn't support multiple type checking

**Remediation**:
```python
# ❌ Bad
if type(obj) == dict:
    process_dict(obj)

# ✅ Good
if isinstance(obj, dict):
    process_dict(obj)

# ✅ Multiple types
if isinstance(obj, (list, tuple)):
    process_sequence(obj)
```

---

### AP-PY-04: Manual Resource Management

**Detection**:
```python
Pattern: /(\w+)\s*=\s*open\([^)]+\)(?!.*with)/g
Pattern: /\.close\(\)/g without context manager
Pattern: /try:.*finally:.*\.close\(\)/g
```

**Severity**: MEDIUM
**Auto-fixable**: Partially

**Why It's Wrong**:
- Resources may not be released on exceptions
- Verbose and error-prone
- Context managers handle edge cases

**Remediation**:
```python
# ❌ Bad
f = open('file.txt')
try:
    content = f.read()
finally:
    f.close()

# ✅ Good
with open('file.txt') as f:
    content = f.read()

# ✅ Multiple resources
with open('input.txt') as fin, open('output.txt', 'w') as fout:
    fout.write(fin.read())
```

---

### AP-PY-05: String Concatenation in Loops

**Detection**:
```python
Pattern: /for.*:\s*\n.*\+=\s*['"]/ or /\+=\s*str\(/
Pattern: /result\s*=\s*['"]['"].*for.*result\s*\+=/g
```

**Severity**: MEDIUM
**Auto-fixable**: Yes

**Why It's Slow**:
- Strings are immutable; each `+=` creates new string
- O(n²) time complexity for n concatenations
- Memory churn from intermediate strings

**Remediation**:
```python
# ❌ Bad - O(n²)
result = ""
for item in items:
    result += str(item) + ", "

# ✅ Good - O(n)
result = ", ".join(str(item) for item in items)

# ✅ For complex formatting
parts = []
for item in items:
    parts.append(f"{item.name}: {item.value}")
result = "\n".join(parts)
```

---

### AP-PY-06: Wildcard Imports

**Detection**:
```python
Pattern: /from\s+\w+\s+import\s+\*/g
```

**Severity**: MEDIUM
**Auto-fixable**: Partially (requires analysis)

**Why It's Wrong**:
- Pollutes namespace unpredictably
- Hides where names come from
- Can cause silent name shadowing
- Breaks static analysis tools

**Remediation**:
```python
# ❌ Bad
from os.path import *
from mymodule import *

# ✅ Good
from os.path import join, dirname, exists
from mymodule import MyClass, helper_function

# ✅ For many imports
from mymodule import (
    ClassOne,
    ClassTwo,
    function_one,
    function_two,
)
```

---

### AP-PY-07: Nested Try/Except Blocks

**Detection**:
```python
Pattern: /try:\s*\n.*try:/g (nested try blocks)
Pattern: Multiple except blocks at same level with similar handling
```

**Severity**: LOW
**Auto-fixable**: No

**Why It's Wrong**:
- Hard to follow exception flow
- Often indicates missing abstraction
- Makes testing difficult

**Remediation**:
```python
# ❌ Bad
try:
    try:
        result = parse_data(raw)
    except ParseError:
        result = default_parse(raw)
    try:
        save_result(result)
    except IOError:
        log_failure(result)
except Exception:
    handle_catastrophe()

# ✅ Good - Extract to functions
def safe_parse(raw):
    try:
        return parse_data(raw)
    except ParseError:
        return default_parse(raw)

def safe_save(result):
    try:
        save_result(result)
    except IOError:
        log_failure(result)

result = safe_parse(raw)
safe_save(result)
```

---

### AP-PY-08: Ignoring Return Values

**Detection**:
```python
Pattern: Function calls not assigned or used
Pattern: /^\s*\w+\.\w+\([^)]*\)\s*$/g (method call as statement)
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Common Offenders**:
- `list.sort()` returns None (sorted in place)
- `dict.update()` returns None
- `set.add()` returns None
- Functions that return error codes

**Remediation**:
```python
# ❌ Bad - sorted() returns new list, original unchanged
sorted_items = items
sorted(items)

# ✅ Good
sorted_items = sorted(items)
# or
items.sort()  # modifies in place

# ❌ Bad - ignoring error return
result = api_call()  # might return error dict

# ✅ Good
result = api_call()
if result.get('error'):
    raise ApiError(result['error'])
```

---

### AP-PY-09: God Objects

**Detection**:
```python
Pattern: Classes with >20 methods
Pattern: Classes with >10 instance attributes
Pattern: Methods >50 lines
Pattern: Files >500 lines
```

**Severity**: HIGH
**Auto-fixable**: No

**Indicators**:
- Class named `Manager`, `Handler`, `Processor`, `Utils`
- Class handling unrelated responsibilities
- Difficulty testing in isolation
- Frequent changes for unrelated features

**Remediation**:
1. Identify distinct responsibilities
2. Extract to separate classes (Single Responsibility)
3. Use composition over inheritance
4. Apply domain-driven design patterns

---

### AP-PY-10: Dynamic Execution of Untrusted Input

**Detection**:
```python
Pattern: /eval\(/g
Pattern: /exec\(/g
Pattern: /compile\([^)]*,\s*['"]exec['"]/g
Pattern: /__import__\(/g with user input
```

**Severity**: CRITICAL
**Auto-fixable**: No

**Why It's Dangerous**:
- Remote code execution vulnerability
- Can access/modify any system resource
- Impossible to sanitize safely

**Safe Alternatives**:
- For math expressions: use `ast.literal_eval()` for literals only
- For configuration: use JSON/YAML parsers
- For dynamic dispatch: use dictionary mapping to functions
- For templating: use Jinja2 or similar sandboxed engines

**NEVER** pass user input to dynamic code execution functions.

---

## Quick Reference Table

| Code | Name | Severity | Fixable |
|------|------|----------|---------|
| AP-PY-01 | Mutable Default Arguments | HIGH | Yes |
| AP-PY-02 | Bare `except` Clauses | HIGH | No |
| AP-PY-03 | `type()` vs `isinstance()` | MEDIUM | Yes |
| AP-PY-04 | Manual Resource Management | MEDIUM | Partial |
| AP-PY-05 | String Concatenation in Loops | MEDIUM | Yes |
| AP-PY-06 | Wildcard Imports | MEDIUM | Partial |
| AP-PY-07 | Nested Try/Except | LOW | No |
| AP-PY-08 | Ignoring Return Values | MEDIUM | No |
| AP-PY-09 | God Objects | HIGH | No |
| AP-PY-10 | Dynamic Execution | CRITICAL | No |

---

## Ruff/Flake8 Rules for Detection

```toml
# pyproject.toml
[tool.ruff]
select = [
    "B006",  # mutable-argument-default
    "B007",  # unused-loop-control-variable
    "E722",  # bare-except
    "F401",  # unused-import
    "F403",  # wildcard-imports
    "F405",  # undefined-from-star-import
    "S102",  # exec-builtin
    "S307",  # suspicious-eval-usage
    "SIM105", # use-contextlib-suppress
    "C901",  # complex-structure (god objects)
]
```

---

## Type Checking Integration

```python
# mypy.ini
[mypy]
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_any_generics = true
```
