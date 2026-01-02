# Tech Stack Detection Reference

Patterns and rules for detecting project technology stacks to enable automatic memory file selection.

## Table of Contents
- [Detection Strategy](#detection-strategy)
- [Configuration File Indicators](#configuration-file-indicators)
- [Package Dependency Patterns](#package-dependency-patterns)
- [Memory File Mapping](#memory-file-mapping)
- [Confidence Levels](#confidence-levels)
- [Idempotency Rules](#idempotency-rules)

---

## Detection Strategy

Tech stack detection follows a deterministic, multi-pass approach:

1. **Configuration Files** - Check for presence of config files (highest signal)
2. **Package Dependencies** - Parse dependency manifests for framework indicators
3. **File Extensions** - Scan for language-specific file extensions (fallback)

Results are merged with highest confidence winning for duplicate technologies.

---

## Configuration File Indicators

### TypeScript

| File | Confidence | Notes |
|------|------------|-------|
| `tsconfig.json` | HIGH | Primary indicator |
| `tsconfig.*.json` | HIGH | Extended configs |
| `*.ts` files | MEDIUM | Could be declaration files |
| `*.tsx` files | HIGH | React + TypeScript |

### JavaScript/Node

| File | Confidence | Notes |
|------|------------|-------|
| `package.json` | HIGH | Node.js project |
| `*.js` files | LOW | Ubiquitous, low signal |
| `*.mjs` files | MEDIUM | ES modules |

### Next.js

| File | Confidence | Notes |
|------|------------|-------|
| `next.config.js` | HIGH | Config file |
| `next.config.mjs` | HIGH | ES module config |
| `next.config.ts` | HIGH | TypeScript config |
| `.next/` directory | HIGH | Build output |
| `app/layout.tsx` | HIGH | App router |
| `pages/_app.tsx` | HIGH | Pages router |

### Tailwind CSS

| File | Confidence | Notes |
|------|------------|-------|
| `tailwind.config.js` | HIGH | Config file |
| `tailwind.config.ts` | HIGH | TypeScript config |
| `tailwind.config.mjs` | HIGH | ES module config |

### Python

| File | Confidence | Notes |
|------|------------|-------|
| `pyproject.toml` | HIGH | Modern Python |
| `setup.py` | HIGH | Traditional |
| `requirements.txt` | HIGH | Pip dependencies |
| `Pipfile` | HIGH | Pipenv |
| `poetry.lock` | HIGH | Poetry |
| `*.py` files | MEDIUM | Could be scripts |

### Rust

| File | Confidence | Notes |
|------|------------|-------|
| `Cargo.toml` | HIGH | Cargo manifest |
| `Cargo.lock` | HIGH | Lock file |
| `*.rs` files | MEDIUM | Source files |

### Testing Frameworks

| File | Confidence | Framework |
|------|------------|-----------|
| `jest.config.js` | HIGH | Jest |
| `jest.config.ts` | HIGH | Jest |
| `vitest.config.ts` | HIGH | Vitest |
| `pytest.ini` | HIGH | Pytest |
| `conftest.py` | HIGH | Pytest |
| `.pytest_cache/` | MEDIUM | Pytest |

---

## Package Dependency Patterns

### package.json Dependencies

| Pattern | Technology | Confidence |
|---------|------------|------------|
| `react` | react | HIGH |
| `react-dom` | react | HIGH |
| `next` | nextjs | HIGH |
| `@next/*` | nextjs | MEDIUM |
| `tailwindcss` | tailwind | HIGH |
| `@tailwindcss/*` | tailwind | MEDIUM |
| `typescript` | typescript | HIGH |
| `jest` | jest | HIGH |
| `@jest/*` | jest | MEDIUM |
| `vitest` | vitest | HIGH |
| `@testing-library/*` | testing-library | HIGH |
| `playwright` | playwright | HIGH |
| `@playwright/*` | playwright | MEDIUM |
| `cypress` | cypress | HIGH |
| `@radix-ui/*` | shadcn | MEDIUM |

### pyproject.toml Dependencies

| Pattern | Technology | Confidence |
|---------|------------|------------|
| `pytest` | pytest | HIGH |
| `django` | django | HIGH |
| `flask` | flask | HIGH |
| `fastapi` | fastapi | HIGH |
| `sqlalchemy` | sqlalchemy | MEDIUM |

---

## Memory File Mapping

### Universal Files (Always Included)

These files contain foundational standards applicable to all projects:

| File | Purpose |
|------|---------|
| `constitution.md` | Core development principles |
| `documentation.md` | Documentation standards |
| `git-cicd.md` | Git workflow and CI/CD |
| `security.md` | Security requirements |
| `testing.md` | Testing strategies |

### Tech-Specific Files

| Technology Triggers | Memory File |
|--------------------|-------------|
| typescript, javascript, node | `typescript.md` |
| react, nextjs | `react-nextjs.md` |
| tailwind, shadcn | `tailwind-shadcn.md` |
| python, django, flask, fastapi | `python.md` |
| rust | `rust.md` |

### Selection Logic

```
selected_files = UNIVERSAL_FILES + tech_specific_files(detected_technologies)
```

Example for a Next.js + Tailwind project:
- Universal: constitution.md, documentation.md, git-cicd.md, security.md, testing.md
- Tech-specific: typescript.md, react-nextjs.md, tailwind-shadcn.md

---

## Confidence Levels

| Level | Meaning | Usage |
|-------|---------|-------|
| HIGH | Strong, unambiguous indicator | Config files, explicit deps |
| MEDIUM | Good indicator with some ambiguity | File extensions, transitive deps |
| LOW | Weak indicator, needs corroboration | Common extensions, generic patterns |

When merging detections:
- Higher confidence overwrites lower for same technology
- All indicators are collected for reporting

---

## Idempotency Rules

Detection is designed to be **safe to run repeatedly**:

1. **Deterministic Output** - Same project always produces same detection results
2. **No Side Effects** - Detection reads only, never modifies
3. **Stable Ordering** - Results sorted by confidence then alphabetically

For file copying (select_memory.py):

1. **Skip Identical** - Files with matching content hashes are skipped
2. **Update Changed** - Files with different content are updated (by default)
3. **Never Delete** - Existing files not in selection are preserved
4. **Create Missing** - New files are added

### Catch-up Mode

When running on an existing project:
- New tech-specific files are added based on current detection
- Existing memory files are updated if templates changed
- Project-specific customizations in memory files are preserved via `--no-update` flag

---

## CLI Usage

### detect_stack.py

```bash
# Detect stack in current directory
python detect_stack.py

# Detect stack in specific directory
python detect_stack.py /path/to/project

# Output (JSON):
{
  "primary_language": "typescript",
  "frameworks": ["nextjs", "tailwind"],
  "detections": [
    {"technology": "typescript", "confidence": "HIGH", "indicators": ["File: tsconfig.json"]},
    {"technology": "nextjs", "confidence": "HIGH", "indicators": ["File: next.config.js"]}
  ],
  "memory_files": ["constitution.md", "documentation.md", "git-cicd.md", ...]
}
```

### select_memory.py

```bash
# Select and copy memory files
python select_memory.py /path/to/project

# Dry run (show what would happen)
python select_memory.py --dry-run /path/to/project

# Override detected technologies
python select_memory.py --techs typescript react tailwind /path/to/project

# Include all memory files
python select_memory.py --all /path/to/project

# List selected files without copying
python select_memory.py --list /path/to/project
```
