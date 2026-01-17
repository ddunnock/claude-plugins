# Git & CI/CD Standards

> **Applies to**: All version control and deployment workflows
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

| Type       | Purpose                 | Example                                           |
|------------|-------------------------|---------------------------------------------------|
| `feat`     | New feature             | `feat(search): add hybrid search support`         |
| `fix`      | Bug fix                 | `fix(ingest): handle malformed PDF metadata`      |
| `docs`     | Documentation only      | `docs(readme): update installation steps`         |
| `style`    | Code style (formatting) | `style(lint): apply ruff formatting`              |
| `refactor` | Code refactoring        | `refactor(chunk): extract base chunker interface` |
| `perf`     | Performance improvement | `perf(embed): add batch embedding`                |
| `test`     | Adding/updating tests   | `test(store): add Qdrant store tests`             |
| `build`    | Build system changes    | `build(deps): upgrade qdrant-client`              |
| `ci`       | CI/CD changes           | `ci(actions): add coverage reporting`             |
| `chore`    | Maintenance tasks       | `chore(deps): update lockfiles`                   |

### 1.2 Scopes for Knowledge MCP

| Scope    | Description            |
|----------|------------------------|
| `ingest` | Document ingestion     |
| `chunk`  | Chunking strategies    |
| `embed`  | Embedding generation   |
| `store`  | Vector storage         |
| `search` | Search and retrieval   |
| `server` | MCP server             |
| `cli`    | Command-line interface |
| `config` | Configuration          |
| `docs`   | Documentation          |

### 1.3 Examples

```bash
# Feature
feat(search): add hybrid search with sparse vectors

# Bug fix
fix(ingest): handle PDFs with missing metadata

Properly check for null before accessing document properties.

Closes #123

# Breaking change
feat(store)!: change search response format

BREAKING CHANGE: Search now returns structured objects instead of tuples.
Previous format: (content, score)
New format: {"content": str, "score": float, "metadata": dict}
```

---

## 2. Branch Strategy

```
main                        # Production-ready code
├── develop                 # Integration branch
│   ├── feature/ABC-123-description
│   ├── feature/ABC-124-another-feature
│   └── fix/ABC-125-bug-description
├── release/v1.2.0          # Release preparation
└── hotfix/ABC-126-critical-fix
```

### 2.1 Branch Rules

| Rule                     | Enforcement                                       |
|--------------------------|---------------------------------------------------|
| `main` always deployable | **MUST** pass all checks before merge             |
| Changes via PR only      | Direct pushes to `main` **MUST NOT** be allowed   |
| Rebase before merge      | Feature branches **MUST** be rebased on `develop` |
| Squash merge             | Feature branches **SHOULD** use squash merge      |

### 2.2 Branch Naming

```
feature/ABC-123-short-description
fix/ABC-124-bug-description
hotfix/ABC-125-critical-fix
release/v1.2.0
chore/ABC-126-maintenance-task
```

---

## 3. Pull Request Requirements

### 3.1 Before Opening PR

- [ ] All tests pass locally
- [ ] Code coverage thresholds met
- [ ] Linting passes with no warnings
- [ ] Type checking passes
- [ ] Documentation updated if needed
- [ ] Self-review completed

### 3.2 PR Template

```markdown
## Summary

Brief description of changes.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing

Describe the tests added or modified.

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have added tests proving my fix/feature works
- [ ] All new and existing tests pass
- [ ] I have updated relevant documentation
- [ ] My changes generate no new warnings

## Related Issues

Closes #[issue number]
```

---

## 4. CI Pipeline

### 4.1 Pipeline Stages

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint & Format
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

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry
      - run: poetry build
```

### 4.2 Quality Gates

**Blocking Checks** (MUST pass to merge):

- All unit tests pass
- Code coverage >= 80%
- Type checking passes (zero errors)
- Linting passes (zero errors)
- Security scan passes (zero high/critical)
- Build succeeds

**Non-Blocking Checks** (warnings only):

- Code coverage < 90% (target)
- Linting warnings
- Documentation coverage

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

### 5.2 Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry
      - run: poetry build
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
      - name: Publish to PyPI
        run: poetry publish
        env:
          POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_TOKEN }}
```

### 5.3 Changelog

Maintain `CHANGELOG.md` following Keep a Changelog format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

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
- MCP server with semantic search
- PDF and DOCX ingestion
- Qdrant Cloud integration
```

---

## 6. Development Commands

### 6.1 Quick Reference

```bash
# Install dependencies
poetry install

# Run tests with coverage
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run linting
poetry run ruff check src tests
poetry run ruff format src tests

# Run type checking
poetry run pyright

# Run MCP server
poetry run python -m knowledge_mcp

# Build package
poetry build
```

### 6.2 Pre-commit Checklist

- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Pyright passes (zero errors)
- [ ] Ruff passes (zero errors)
- [ ] Documentation updated
- [ ] Commit message follows Conventional Commits