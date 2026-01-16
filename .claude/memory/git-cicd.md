# Git & CI/CD Standards

> **Applies to**: All version control and deployment workflows in Knowledge MCP
> **Parent**: `constitution.md`

---

## 1. Commit Message Format

All commits **MUST** follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 1.1 Types

| Type       | Purpose                 | Example                                      |
|------------|-------------------------|----------------------------------------------|
| `feat`     | New feature             | `feat(search): add hybrid search support`    |
| `fix`      | Bug fix                 | `fix(ingest): handle malformed PDF metadata` |
| `docs`     | Documentation only      | `docs(readme): update installation steps`    |
| `style`    | Code style (formatting) | `style(lint): apply ruff formatting`         |
| `refactor` | Code refactoring        | `refactor(store): extract base class`        |
| `perf`     | Performance improvement | `perf(embed): batch embedding calls`         |
| `test`     | Adding/updating tests   | `test(store): add QdrantStore tests`         |
| `build`    | Build system changes    | `build(deps): upgrade qdrant-client`         |
| `ci`       | CI/CD changes           | `ci(actions): add coverage reporting`        |
| `chore`    | Maintenance tasks       | `chore(deps): update lockfile`               |

### 1.2 Scopes

| Scope    | Description          |
|----------|----------------------|
| `ingest` | Document ingestion   |
| `chunk`  | Chunking strategies  |
| `embed`  | Embedding generation |
| `store`  | Vector storage       |
| `search` | Search and retrieval |
| `server` | MCP server           |
| `config` | Configuration        |
| `cli`    | CLI interface        |

### 1.3 Examples

```bash
# Feature
feat(search): add hybrid search with BM25

Combines semantic search with keyword matching for better results
on technical terminology.

# Bug fix
fix(ingest): handle PDFs with missing metadata

Properly check for None values before accessing document properties.

Closes #123

# Breaking change
feat(store)!: change collection schema for metadata

BREAKING CHANGE: Existing collections must be migrated.
See docs/how-to/migrate-collection.md for instructions.
```

---

## 2. Branch Strategy

```
main                        # Production-ready code
├── feature/description     # New features
├── fix/description         # Bug fixes
└── chore/description       # Maintenance
```

### 2.1 Branch Rules

| Rule                     | Enforcement                                     |
|--------------------------|-------------------------------------------------|
| `main` always deployable | **MUST** pass all checks before merge           |
| Changes via PR only      | Direct pushes to `main` **MUST NOT** be allowed |
| Descriptive names        | Branch names **MUST** describe the change       |

### 2.2 Branch Naming

```
feature/add-hybrid-search
fix/pdf-metadata-parsing
chore/update-dependencies
docs/update-readme
```

---

## 3. Pull Request Requirements

### 3.1 Before Opening PR

- [ ] All tests pass locally (`poetry run pytest`)
- [ ] Code coverage thresholds met (80%+)
- [ ] Linting passes (`poetry run ruff check`)
- [ ] Type checking passes (`poetry run pyright`)
- [ ] Documentation updated if needed

### 3.2 PR Template

```markdown
## Summary

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe tests added or modified.

## Checklist

- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Tests added
- [ ] Documentation updated
```

---

## 4. CI Pipeline

### 4.1 Main Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check src tests
      - run: poetry run ruff format --check src tests
      - run: poetry run pyright

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest --cov --cov-report=xml --cov-fail-under=80
      - uses: codecov/codecov-action@v4

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry pip-audit
      - run: poetry install
      - run: pip-audit --strict
```

### 4.2 Quality Gates

**Blocking Checks** (MUST pass to merge):

- All unit tests pass
- Code coverage ≥80%
- Type checking passes (zero errors)
- Linting passes (zero errors)
- Security scan passes (zero high/critical)

---

## 5. Release Process

### 5.1 Versioning

Follow Semantic Versioning (SemVer):

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
```

### 5.2 Changelog

Maintain `CHANGELOG.md` following Keep a Changelog format:

```markdown
# Changelog

## [Unreleased]

### Added
- Feature description

### Changed
- Change description

### Fixed
- Fix description

## [0.1.0] - 2026-01-16

### Added
- Initial release
- Semantic search over technical documents
- PDF, DOCX, Markdown ingestion
- Qdrant Cloud integration
```

---

## 6. Development Workflow

### 6.1 Feature Development

```bash
# 1. Create branch
git checkout -b feature/add-reranking

# 2. Make changes
# ...

# 3. Run checks locally
poetry run ruff check src tests
poetry run pyright
poetry run pytest

# 4. Commit
git add .
git commit -m "feat(search): add Cohere reranking support"

# 5. Push and create PR
git push -u origin feature/add-reranking
```

### 6.2 Pre-commit Hooks (Optional)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff Check
        entry: poetry run ruff check
        language: system
        types: [python]

      - id: ruff-format
        name: Ruff Format
        entry: poetry run ruff format --check
        language: system
        types: [python]

      - id: pyright
        name: Pyright
        entry: poetry run pyright
        language: system
        types: [python]
```

---

## 7. Quick Reference

### 7.1 Common Commands

```bash
# Run all checks
poetry run ruff check src tests && poetry run pyright && poetry run pytest

# Format code
poetry run ruff format src tests

# Fix linting issues
poetry run ruff check --fix src tests

# Security scan
poetry run pip-audit
```

### 7.2 Pre-commit Checklist

- [ ] All tests pass
- [ ] Coverage ≥80%
- [ ] Pyright passes (zero errors)
- [ ] Ruff passes (zero errors)
- [ ] Commit message follows Conventional Commits