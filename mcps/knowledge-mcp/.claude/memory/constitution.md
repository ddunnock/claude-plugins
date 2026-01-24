# Project Constitution

> **Version**: 2.0.0
> **Classification**: Project-Based SpecKit
> **Owner**: David Dunnock
> **Created**: 2026-01-16
> **Last Updated**: 2026-01-16

---

## Document Structure

This constitution is organized as a modular system. Global principles live here; technology-specific standards are in referenced files.

| File               | Scope                                               | When to Read                |
|--------------------|-----------------------------------------------------|-----------------------------|
| `constitution.md`  | Global principles, quality gates, workflows         | Always                      |
| `python.md`        | Python >=3.11,<3.14, Poetry, docstrings, type hints | Python development          |
| `testing.md`       | Coverage requirements, test patterns                | Writing tests               |
| `documentation.md` | Diataxis framework, Sphinx/Furo, documentation      | Writing documentation       |
| `git-cicd.md`      | Commits, branches, PRs, GitHub Actions              | Version control, deployment |
| `security.md`      | Dependencies, secrets, input validation             | Security concerns           |

---

## 1. Purpose and Scope

This constitution establishes the authoritative standards, patterns, and constraints governing all development activities within the Knowledge MCP project. It serves as the single source of truth for architectural decisions, coding standards, documentation requirements, and quality gates.

### 1.1 Applicability

This constitution applies to:

- All Python source code in `src/knowledge_mcp/`
- All configuration files and infrastructure-as-code
- All documentation and technical specifications
- All automated tests in `tests/`
- All CI/CD pipelines and deployment processes

### 1.2 Normative Language

This document uses RFC 2119 terminology:

| Term           | Meaning                                                        |
|----------------|----------------------------------------------------------------|
| **MUST**       | Absolute requirement - violation blocks merge/deploy           |
| **MUST NOT**   | Absolute prohibition - violation blocks merge/deploy           |
| **SHOULD**     | Strongly recommended - deviation requires documented rationale |
| **SHOULD NOT** | Discouraged - use only with ADR justification                  |
| **MAY**        | Optional - team preference determines behavior                 |

---

## 2. Global Quality Standards

### 2.1 Test Coverage Requirements

All code **MUST** meet or exceed the following coverage thresholds:

| Metric             | Minimum  | Target  | Blocking  |
|--------------------|----------|---------|-----------|
| Line Coverage      | 80%      | 90%     | Yes       |
| Branch Coverage    | 75%      | 85%     | Yes       |
| Function Coverage  | 85%      | 95%     | Yes       |
| Statement Coverage | 80%      | 90%     | Yes       |

**Exclusions** (MUST be documented with rationale):

- Generated code
- Configuration files
- Test fixtures and mocks

> See `testing.md` for enforcement commands and test patterns.

### 2.2 Documentation Requirements

All public APIs **MUST** have 100% documentation coverage. Internal APIs **SHOULD** have 80% coverage.

| Language  | Documentation Standard               | Reference      |
|-----------|--------------------------------------|----------------|
| Python    | Google-style docstrings + type hints | `python.md` §3 |

### 2.3 Type Safety

All code **MUST** pass strict type checking with zero errors:

| Language  | Tool    | Mode   | Reference      |
|-----------|---------|--------|----------------|
| Python    | pyright | strict | `python.md` §4 |

---

## 3. Dependency Management

### 3.1 Freshness Policy

All dependencies **MUST** use the latest stable version unless a specific conflict exists.

| Rule                 | Enforcement                                                                                           |
|----------------------|-------------------------------------------------------------------------------------------------------|
| Default to `@latest` | All new dependencies **MUST** be added at their latest stable version                                 |
| Verify actively      | Version selection **MUST** be verified via registry lookup (PyPI), NOT from cached/training knowledge |
| Document conflicts   | Any dependency pinned below latest **MUST** document the conflict                                     |
| Regular audits       | Dependencies **SHOULD** be audited for updates monthly                                                |

**Anti-Pattern:** Using outdated model knowledge to select dependency versions. Always query the live registry.

### 3.2 Verification Commands

```bash
# Python - Check latest versions
pip index versions <package>
poetry show --outdated
```

### 3.3 Conflict Documentation

For Python, use inline comments:

```toml
# PINNED: v3.x breaks API compatibility, see ADR-012
some-package = ">=2.1.0,<3.0.0"
```

---

## 4. Project Structure

```
knowledge-mcp/
├── .claude/
│   ├── commands/           # SpecKit commands
│   ├── memory/             # Project directives
│   ├── templates/          # Document templates
│   └── scripts/            # Supporting automation scripts
├── src/
│   └── knowledge_mcp/      # Main package
├── tests/
├── docs/                   # Sphinx documentation (Diataxis)
├── speckit/                # Specification artifacts
├── data/
│   ├── sources/            # Source documents
│   └── processed/          # Intermediate processing output
├── scripts/                # Project scripts
├── pyproject.toml          # Poetry configuration
└── poetry.lock             # Locked dependencies (committed)
```

### 4.1 Package Management

| Ecosystem   | Tool   | Configuration                                  |
|-------------|--------|------------------------------------------------|
| Python      | Poetry | `pyproject.toml` with strict peer dependencies |

---

## 5. Exception Handling

### 5.1 Deviation Process

Any deviation from this constitution **MUST** follow:

1. **Document the deviation** in an ADR (Architecture Decision Record)
2. **Justify the deviation** with technical rationale
3. **Get approval** from at least one senior engineer
4. **Set an expiration** for temporary deviations
5. **Track the deviation** in the project's deviation log

### 5.2 ADR Template

```markdown
# ADR-NNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing?

## Constitution Deviation
Which constitution file(s) and section(s) does this deviate from?

## Consequences
What becomes easier or more difficult because of this change?

## Expiration
[Permanent | Date for review]
```

---

## 6. API Performance

| Metric            | Target  | Blocking  |
|-------------------|---------|-----------|
| P50 Response Time | <100ms  | No        |
| P95 Response Time | <500ms  | Yes       |
| P99 Response Time | <1000ms | Yes       |
| Error Rate        | <0.1%   | Yes       |

---

## 7. Documentation Standards

### 7.1 Framework

All documentation **MUST** follow the Diataxis framework, organizing content into four quadrants:

| Quadrant          | Purpose                   | User Need                |
|-------------------|---------------------------|--------------------------|
| **Tutorials**     | Learning by doing         | "Teach me"               |
| **How-To Guides** | Solving specific problems | "Help me achieve X"      |
| **Reference**     | Looking up information    | "Show me the details"    |
| **Explanation**   | Understanding concepts    | "Help me understand why" |

> See `documentation.md` for full Diataxis guidelines and templates.

### 7.2 Tooling

| Tool         | Purpose                   | Configuration      |
|--------------|---------------------------|--------------------|
| Sphinx       | Documentation generator   | `docs/conf.py`     |
| Furo         | Theme (clean, responsive) | Via `html_theme`   |
| MyST Parser  | Markdown support          | All docs in `*.md` |
| GitHub Pages | Hosting                   | Automated via CI   |

### 7.3 Code Documentation Coverage

| Scope              | Requirement                           |
|--------------------|---------------------------------------|
| Public APIs        | **MUST** have 100% documentation      |
| Internal APIs      | **SHOULD** have 80% documentation     |
| Complex algorithms | **MUST** include explanatory comments |
| Non-obvious code   | **SHOULD** include inline comments    |

---

## Glossary

| Term         | Definition                                                                                           |
|--------------|------------------------------------------------------------------------------------------------------|
| **ADR**      | Architecture Decision Record - documents significant technical decisions                             |
| **Diataxis** | Documentation framework organizing content into tutorials, how-to guides, reference, and explanation |
| **Furo**     | Sphinx theme providing clean, responsive documentation                                               |
| **MCP**      | Model Context Protocol - standard for AI model interactions                                          |
| **MyST**     | Markedly Structured Text - Markdown parser for Sphinx                                                |
| **RAG**      | Retrieval Augmented Generation - technique for enhancing LLM responses with relevant context         |
| **SpecKit**  | Project automation package with commands, scripts, templates                                         |
| **Sphinx**   | Documentation generator for Python projects                                                          |

---

## Revision History

| Version  | Date       | Author     | Changes                              |
|----------|------------|------------|--------------------------------------|
| 2.0.0    | 2026-01-16 | D. Dunnock | Customized for Knowledge MCP project |

---

*This constitution is a living document. Propose changes via pull request.*