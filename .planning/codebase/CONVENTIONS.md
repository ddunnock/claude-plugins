# Coding Conventions

**Analysis Date:** 2026-01-23

## Naming Patterns

**Files:**
- Script files: `snake_case.py` (e.g., `validate_plan.py`, `detect_stack.py`)
- Plugin files: `snake_case.py` (e.g., `generic.py`, `spec_refiner.py`)
- Configuration files: `config.json`, `.env`, `pyproject.toml`
- Markdown documentation: `UPPERCASE.md` (e.g., `SKILL.md`, `MCP.md`, `CLAUDE.md`)

**Functions:**
- Snake_case for all functions (e.g., `validate_plan()`, `_resume_from_checkpoint()`)
- Private/internal functions prefixed with underscore (e.g., `_init_storage()`, `_load_config()`)
- Public methods on classes without underscore prefix

**Variables:**
- Snake_case for local variables and module-level variables
- Uppercase with underscores for constants (e.g., `DEFAULT_CONFIG`, `SIMPLE_PLAN_SECTIONS`, `RESERVED_WORDS`)
- Private attributes on classes with leading underscore (e.g., `self._lock`, `self._checkpoint_timer`)

**Types:**
- Classes use PascalCase (e.g., `SessionPlugin`, `PluginState`, `ValidationResult`, `Finding`)
- TypedDict definitions use PascalCase (e.g., `ValidationIssue`, `StackDetection`, `DetectionResult`)
- Enums use PascalCase (e.g., `Severity`, `Category`)

## Code Style

**Formatting:**
- Ruff is used for formatting in reference projects (pyproject.toml specifies Ruff)
- Line length: 100 characters (see `tool.ruff` configuration)
- Double quotes for strings (enforced by Ruff: `quote-style = "double"`)
- Indent style: spaces (4 spaces standard in Python)

**Linting:**
- Ruff is the primary linter with rules: `E`, `F`, `I`, `W`, `UP`, `S`, `B`
- Ignored rules include `E501` (line too long), `S101` (assert in tests), `S301` (pickle for demo code), etc.
- See `/Users/dunnock/projects/claude-plugins/_references/claude-cookbooks/pyproject.toml` for Ruff configuration

## Import Organization

**Order:**
1. Standard library imports (builtins): `import sys`, `import json`, `from pathlib import Path`
2. Third-party library imports: `from dataclasses import dataclass`, `from typing import Dict, List`
3. Local/relative imports: `from .base import SessionPlugin`, `from plugins.base import PluginState`

**Pattern observed in codebase:**
```python
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Blank line before local imports
from .base import SessionPlugin, PluginState
```

**Path Aliases:**
- Absolute imports used (not relative dot imports) when crossing package boundaries
- Relative imports used within same package (`.base`, `.generic`)
- Standard library imported before local modules

## Error Handling

**Patterns observed:**
- Try-except blocks wrap ImportError for optional dependencies (graceful degradation pattern)
- Example from `server.py`: loads optional feature modules with graceful degradation
  ```python
  try:
      from modules.learning import LearningService
      self.learning_service = LearningService(str(self.db_path))
  except ImportError:
      pass
  ```
- ValueError raised for invalid arguments with descriptive messages
- Exit codes: 0 for success, 1 for validation failure, 2 for input errors
- Custom exception classes defined (e.g., `ValidationIssue` as TypedDict)

**Pattern for dict/object return codes:**
- Success: `{"status": "success", "data": ...}` or boolean `"valid": True`
- Error: `{"error": str(e)}` or `{"available": False, "error": "message"}`
- No exceptions raised in tool methods; errors returned as dict values

## Logging

**Framework:** Console-based using `print()` and stderr

**Patterns observed:**
- Direct `print()` for normal output
- `print(..., file=sys.stderr)` for errors and warnings
- Example: `print("Warning: MCP detected without MCP.md manifest...", file=sys.stderr)`
- No structured logging framework detected; plain text output

## Comments

**When to Comment:**
- Docstrings required for all public functions and classes (PEP 257)
- Complex algorithms or non-obvious logic receive inline comments
- Section markers for major code blocks (e.g., `# =========================================================================`)

**JSDoc/TSDoc:**
- Python uses triple-quoted docstrings (not JSDoc)
- Format: One-line summary, blank line, detailed description, Args/Returns sections
- Example from `server.py`:
  ```python
  def session_init(
      self,
      skill_name: Optional[str] = None,
      session_id: Optional[str] = None,
      resume_from_checkpoint: Optional[str] = None,
      config: Optional[Dict] = None
  ) -> Dict[str, Any]:
      """Initialize a new session or resume from checkpoint."""
  ```

## Function Design

**Size:** Functions typically 20-50 lines; complex validations can be longer (e.g., `validate_plan` is 395 lines)

**Parameters:**
- Named arguments preferred over positional for optional parameters
- Type hints required for all parameters (e.g., `plan_path: str | Path`)
- Default values use `None` for optional, `False` for booleans
- Variadic args with `*args, **kwargs` avoided; explicit parameters preferred

**Return Values:**
- Functions return Dict for multiple values: `Dict[str, Any]`
- Single return type preferred over tuple unpacking
- None used for no return value (functions with side effects only)

## Module Design

**Exports:**
- Public API defined implicitly by module structure; no `__all__` observed
- Private functions/classes prefixed with underscore for internal use only
- Classes inherit from ABC (abstract base class) when defining interfaces

**Barrel Files:**
- Not observed in this codebase; each module imports what it needs directly
- Plugin modules import from `.base` module within plugins directory

## Type Hints

**Style:**
- Type hints mandatory on all function signatures: `def validate_plan(plan_path: str | Path) -> ValidationResult:`
- Union types use pipe operator (`str | Path`) instead of Union types (Python 3.10+ syntax)
- Optional types use `Optional[T]` or `T | None`
- Dict/List from typing module: `Dict[str, Any]`, `List[Finding]`
- TypedDict used for structured dictionaries (e.g., `ValidationIssue`, `StackDetection`)
- Dataclasses preferred for data structures: `@dataclass class Finding: ...`

## Code Organization

**Pattern - Classes and Functions:**
- Dataclasses used for data structures with `@dataclass` decorator
- Abstract base classes for interfaces using ABC and `@abstractmethod`
- Property decorators used for read-only attributes: `@property`
- Static/class methods marked with `@staticmethod` or `@classmethod`

**Pattern - Threading and Locks:**
- Threading used with `threading.RLock()` for thread safety
- Methods use `with self._lock:` context manager for critical sections
- Timer callbacks scheduled with `threading.Timer()`

**Pattern - Dataclass Fields:**
- Default factory for mutable defaults: `field(default_factory=dict)`
- Not direct assignment: `field_name: List = []` (avoid anti-pattern)

---

*Convention analysis: 2026-01-23*
