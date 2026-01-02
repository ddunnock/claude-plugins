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

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 support` |
| `fix` | Bug fix | `fix(api): handle null response` |
| `docs` | Documentation only | `docs(readme): update installation steps` |
| `style` | Code style (formatting) | `style(lint): apply biome formatting` |
| `refactor` | Code refactoring | `refactor(service): extract validation logic` |
| `perf` | Performance improvement | `perf(query): add database index` |
| `test` | Adding/updating tests | `test(auth): add login flow tests` |
| `build` | Build system changes | `build(deps): upgrade Next.js to 14.1` |
| `ci` | CI/CD changes | `ci(actions): add coverage reporting` |
| `chore` | Maintenance tasks | `chore(deps): update lockfiles` |

### 1.2 Scopes

| Scope | Description |
|-------|-------------|
| `api` | Python API service |
| `web` | Next.js web application |
| `cli` | Rust CLI tool |
| `ui` | Shared component library |
| `auth` | Authentication system |
| `db` | Database/ORM changes |
| `config` | Configuration changes |

### 1.3 Examples

```bash
# Feature
feat(auth): add OAuth2 support for Google login

# Bug fix
fix(api): handle null response in user endpoint

Properly check for null before accessing user properties.

Closes #123

# Breaking change
feat(api)!: change response format for resources endpoint

BREAKING CHANGE: The resources endpoint now returns paginated results.
Previous format: { resources: [...] }
New format: { data: [...], meta: { page, total } }
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

| Rule | Enforcement |
|------|-------------|
| `main` always deployable | **MUST** pass all checks before merge |
| Changes via PR only | Direct pushes to `main` **MUST NOT** be allowed |
| Rebase before merge | Feature branches **MUST** be rebased on `develop` |
| Squash merge | Feature branches **SHOULD** use squash merge |
| Merge commits | Release branches **MUST** use merge commits |

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

### 3.3 Review Requirements

| Check | Requirement |
|-------|-------------|
| Approvals | At least 1 approval required |
| CI Status | All checks must pass |
| Up to date | Branch must be up to date with base |
| Conversations | All conversations must be resolved |

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
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck

  test-typescript:
    name: Test (TypeScript)
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm test:coverage
      - uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
          fail_ci_if_error: true

  test-python:
    name: Test (Python)
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest --cov --cov-report=xml --cov-fail-under=80
      - uses: codecov/codecov-action@v4

  test-rust:
    name: Test (Rust)
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@cargo-llvm-cov
      - run: cargo llvm-cov --lcov --output-path lcov.info --fail-under-lines 80
      - uses: codecov/codecov-action@v4

  e2e:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [test-typescript, test-python]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps
      - run: pnpm test:e2e
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [test-typescript, test-python, test-rust]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: |
            apps/web/.next/
            apps/api/dist/
            target/release/
```

### 4.2 Quality Gates

**Blocking Checks** (MUST pass to merge):

- All unit tests pass
- All integration tests pass
- Code coverage ≥80%
- Type checking passes (zero errors)
- Linting passes (zero errors)
- Security scan passes (zero high/critical)
- Build succeeds

**Non-Blocking Checks** (warnings only):

- Code coverage <90% (target)
- Linting warnings
- Documentation coverage
- Performance benchmarks

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
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
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

## [1.0.0] - 2026-01-02

### Added
- Initial release
```

---

## 6. Branch Protection

### 6.1 GitHub Settings

```yaml
# For main branch
protection:
  required_pull_request_reviews:
    required_approving_review_count: 1
    dismiss_stale_reviews: true
    require_code_owner_reviews: false
  required_status_checks:
    strict: true
    contexts:
      - "Lint & Format"
      - "Test (TypeScript)"
      - "Test (Python)"
      - "Test (Rust)"
      - "Build"
  enforce_admins: true
  allow_force_pushes: false
  allow_deletions: false
```

---

## 7. Deployment

### 7.1 Environment Strategy

| Environment | Branch | Trigger |
|-------------|--------|---------|
| Development | `develop` | Push |
| Staging | `release/*` | Push |
| Production | `main` | Tag |

### 7.2 Deploy Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
    tags: [v*]

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      # Deploy to staging...

  deploy-production:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      # Deploy to production...
```
