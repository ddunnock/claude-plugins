# Project Constitution

> **Version**: 1.0.0
> **Project**: Knowledge MCP
> **Created**: 2026-01-16
> **Last Updated**: 2026-01-16

---

## Document Structure

This constitution is organized as a modular system. Global principles live here; technology-specific standards are in referenced files.

| File               | Scope                                              | When to Read                |
|--------------------|----------------------------------------------------|-----------------------------|
| `constitution.md`  | Global principles, quality gates, workflows        | Always                      |
| `python.md`        | Python ≥3.11,<3.14, Poetry, docstrings, type hints | Python development          |
| `testing.md`       | Coverage requirements, test patterns               | Writing tests               |
| `documentation.md` | Diátaxis framework, Sphinx/Furo                    | Writing documentation       |
| `git-cicd.md`      | Commits, branches, PRs, GitHub Actions             | Version control, deployment |
| `security.md`      | Dependencies, secrets, input validation            | Security concerns           |

---

## 1. Purpose and Scope

This constitution establishes the authoritative standards, patterns, and constraints governing all development activities within the Knowledge MCP project. It serves as the single source of truth for architectural decisions, coding standards, documentation requirements, and quality gates.

### 1.1 Applicability

This constitution applies to:

- All source code artifacts (Python)
- All configuration files (pyproject.toml, .env)
- All documentation and technical specifications
- All automated tests and verification procedures
- All CI/CD pipelines and deployment processes

### 1.2 Normative Language

This document uses RFC 2119 terminology:

| Term           | Meaning                                                      |
|----------------|--------------------------------------------------------------|
| **MUST**       | Absolute requirement—violation blocks merge/deploy           |
| **MUST NOT**   | Absolute prohibition—violation blocks merge/deploy           |
| **SHOULD**     | Strongly recommended—deviation requires documented rationale |
| **SHOULD NOT** | Discouraged—use only with ADR justification                  |
| **MAY**        | Optional—team preference determines behavior                 |

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

→ See `testing.md` for enforcement commands and test patterns.

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

### 3.2 Verification Commands

```bash
# Python - Check latest versions
pip index versions <package>
poetry show --outdated

# Security scanning
pip-audit --strict
```

---

## 4. Project Structure

### 4.1 Knowledge MCP Layout

```
knowledge-mcp/
├── .claude/
│   ├── commands/           # SpecKit commands
│   ├── memory/             # Project directives
│   ├── resources/          # Specifications, plans, tasks
│   └── templates/          # Document templates
├── src/
│   └── knowledge_mcp/      # Main package
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py       # MCP server implementation
│       ├── ingest/         # Document ingestion
│       ├── chunk/          # Chunking strategies
│       ├── embed/          # Embedding generation
│       ├── store/          # Vector storage
│       ├── search/         # Search and retrieval
│       ├── models/         # Data models
│       └── utils/          # Utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── scripts/
├── data/
│   ├── sources/
│   └── processed/
├── docs/
├── pyproject.toml
├── poetry.lock
└── README.md
```

### 4.2 Package Management

| Ecosystem  | Tool   | Configuration                            |
|------------|--------|------------------------------------------|
| Python     | Poetry | pyproject.toml with strict type checking |

---

## 5. Exception Handling

### 5.1 Deviation Process

Any deviation from this constitution **MUST** follow:

1. **Document the deviation** in an ADR (Architecture Decision Record)
2. **Justify the deviation** with technical rationale
3. **Get approval** from project owner
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

## 6. Performance Standards

### 6.1 MCP Server Performance

| Metric               | Target        | Blocking  |
|----------------------|---------------|-----------|
| Search P50           | <500ms        | No        |
| Search P95           | <2000ms       | Yes       |
| Embedding generation | <1s per chunk | No        |
| Memory usage         | <500MB idle   | Yes       |

---

## 7. Documentation Standards

### 7.1 Framework

All documentation **MUST** follow the Diátaxis framework, organizing content into four quadrants:

| Quadrant          | Purpose                   | User Need                |
|-------------------|---------------------------|--------------------------|
| **Tutorials**     | Learning by doing         | "Teach me"               |
| **How-To Guides** | Solving specific problems | "Help me achieve X"      |
| **Reference**     | Looking up information    | "Show me the details"    |
| **Explanation**   | Understanding concepts    | "Help me understand why" |

→ See `documentation.md` for full Diátaxis guidelines and templates.

### 7.2 Required Documents

| Document      | Location          | Update Frequency   |
|---------------|-------------------|--------------------|
| README.md     | Root              | On feature changes |
| CHANGELOG.md  | Root              | Every release      |
| API Reference | `docs/reference/` | On API changes     |

---

## Glossary

| Term         | Definition                                                                                           |
|--------------|------------------------------------------------------------------------------------------------------|
| **ADR**      | Architecture Decision Record - documents significant technical decisions                             |
| **Diátaxis** | Documentation framework organizing content into tutorials, how-to guides, reference, and explanation |
| **MCP**      | Model Context Protocol - standardized protocol for AI model tool integration                         |
| **RAG**      | Retrieval Augmented Generation - technique for enhancing LLM responses with retrieved context        |
| **SpecKit**  | Project automation package with commands, scripts, templates                                         |

---

## Revision History

| Version  | Date       | Author  | Changes                                |
|----------|------------|---------|----------------------------------------|
| 1.0.0    | 2026-01-16 | Claude  | Initial constitution for Knowledge MCP |

---

*This constitution is a living document. Propose changes via pull request.*