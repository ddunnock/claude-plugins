# Project Constitution

> **Version**: 2.0.0  
> **Classification**: Project-Based SpecKit  
> **Owner**: David Dunnock  
> **Created**: 2026-01-02  
> **Last Updated**: 2026-01-02

---

<!-- 
================================================================================
SKILL AGENT INSTRUCTIONS
================================================================================
This constitution template contains placeholders that must be resolved before
generating the final SpecKit. The agent MUST ask the user for clarification
on the following before proceeding:

PLACEHOLDER: ${PROJECT_CONTEXT}
Question: "Is this a personal project or an L3Harris project?"
Options:
  - "personal" → Use tailwind-shadcn.md (distinctive typography, anti-AI-slop)
  - "l3harris"  → Use tailwind-l3harris.md (official brand compliance)

This affects:
  - ${STYLING_STANDARDS} in Document Structure table
  - ${FONT_IMPORTS} in react-nextjs.md
  - ${FONT_VARIABLES} in react-nextjs.md
  - ${GLOBALS_CSS} theme file selection

Replacement mappings:
┌─────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ Placeholder         │ Personal Project             │ L3Harris Project             │
├─────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ ${STYLING_STANDARDS}│ tailwind-shadcn.md           │ tailwind-l3harris.md         │
│ ${GLOBALS_CSS}      │ globals.css (from shadcn)    │ globals-l3harris.css         │
│ ${PRIMARY_FONT}     │ Playfair Display / IBM Plex  │ Inter                        │
│ ${MONO_FONT}        │ JetBrains Mono               │ IBM Plex Mono                │
│ ${COLOR_PRIMARY}    │ oklch(55% 0.15 250)          │ #305195 (Air 2)              │
│ ${COLOR_ACCENT}     │ User's brand color           │ #FF000A (Vibrant Red)        │
└─────────────────────┴──────────────────────────────┴──────────────────────────────┘

After determining project context, the agent should:
1. Replace all placeholders with appropriate values
2. Include only the relevant styling file in the generated SpecKit
3. Remove these instruction comments from the final output
================================================================================
-->

---

## Document Structure

This constitution is organized as a modular system. Global principles live here; technology-specific standards are in referenced files.

| File | Scope | When to Read |
|------|-------|--------------|
| `constitution.md` | Global principles, quality gates, workflows | Always |
| `python.md` | Python ≥3.11,<3.14, Poetry, docstrings, type hints | Python development |
| `rust.md` | Rust ≥1.75, Cargo, doc comments, Clippy | Rust development |
| `typescript.md` | TypeScript, Node.js ≥20, JSDoc, Biome | TypeScript/JavaScript development |
| `react-nextjs.md` | React ≥18, Next.js ≥14, components, App Router | Frontend development |
| `${STYLING_STANDARDS}` | Design system, colors, typography, TailwindCSS v4 | UI/styling work |
| `testing.md` | Coverage requirements, test patterns, E2E | Writing tests |
| `documentation.md` | Diátaxis framework, Sphinx/Furo, GitHub Pages | Writing documentation |
| `git-cicd.md` | Commits, branches, PRs, GitHub Actions | Version control, deployment |
| `security.md` | Dependencies, secrets, input validation | Security concerns |

<!-- 
SKILL AGENT INSTRUCTION: ${STYLING_STANDARDS}
Ask the user: "Is this a personal project or an L3Harris project?"
- If personal project → Replace with `tailwind-shadcn.md` (distinctive typography, anti-AI-slop design)
- If L3Harris project → Replace with `tailwind-l3harris.md` (official brand compliance)
-->

---

## 1. Purpose and Scope

This constitution establishes the authoritative standards, patterns, and constraints governing all development activities within this project. It serves as the single source of truth for architectural decisions, coding standards, documentation requirements, and quality gates.

### 1.1 Applicability

This constitution applies to:

- All source code artifacts (Python, Rust, TypeScript, JavaScript, CSS)
- All configuration files and infrastructure-as-code
- All documentation and technical specifications
- All automated tests and verification procedures
- All CI/CD pipelines and deployment processes

### 1.2 Normative Language

This document uses RFC 2119 terminology:

| Term | Meaning |
|------|---------|
| **MUST** | Absolute requirement—violation blocks merge/deploy |
| **MUST NOT** | Absolute prohibition—violation blocks merge/deploy |
| **SHOULD** | Strongly recommended—deviation requires documented rationale |
| **SHOULD NOT** | Discouraged—use only with ADR justification |
| **MAY** | Optional—team preference determines behavior |

---

## 2. Global Quality Standards

### 2.1 Test Coverage Requirements

All code **MUST** meet or exceed the following coverage thresholds:

| Metric | Minimum | Target | Blocking |
|--------|---------|--------|----------|
| Line Coverage | 80% | 90% | Yes |
| Branch Coverage | 75% | 85% | Yes |
| Function Coverage | 85% | 95% | Yes |
| Statement Coverage | 80% | 90% | Yes |

**Exclusions** (MUST be documented with rationale):

- Generated code (e.g., Prisma client, protobuf)
- Configuration files
- Type declaration files (`.d.ts`)
- Test fixtures and mocks

→ See `testing.md` for enforcement commands and test patterns.

### 2.2 Documentation Requirements

All public APIs **MUST** have 100% documentation coverage. Internal APIs **SHOULD** have 80% coverage.

| Language | Documentation Standard | Reference |
|----------|----------------------|-----------|
| Python | Google-style docstrings + type hints | `python.md` §3 |
| TypeScript/JavaScript | JSDoc with full typing | `typescript.md` §3 |
| Rust | Doc comments with examples | `rust.md` §3 |

### 2.3 Type Safety

All code **MUST** pass strict type checking with zero errors:

| Language | Tool | Mode | Reference |
|----------|------|------|-----------|
| Python | pyright | strict | `python.md` §4 |
| TypeScript | tsc | strict + extras | `typescript.md` §4 |
| Rust | rustc + clippy | pedantic | `rust.md` §4 |

---

## 3. Dependency Management

### 3.1 Freshness Policy

All dependencies **MUST** use the latest stable version unless a specific conflict exists.

| Rule | Enforcement |
|------|-------------|
| Default to `@latest` | All new dependencies **MUST** be added at their latest stable version |
| Verify actively | Version selection **MUST** be verified via registry lookup (npm, PyPI, crates.io), NOT from cached/training knowledge |
| Document conflicts | Any dependency pinned below latest **MUST** document the conflict |
| Regular audits | Dependencies **SHOULD** be audited for updates monthly |

**Anti-Pattern:** Using outdated model knowledge to select dependency versions. Always query the live registry.

### 3.2 Verification Commands

```bash
# Node.js - Check latest versions
pnpm outdated
npm view <package> version

# Python - Check latest versions  
pip index versions <package>
poetry show --outdated

# Rust - Check latest versions
cargo outdated
cargo search <crate>
```

### 3.3 Conflict Documentation

For Node.js, document in `DEPENDENCY_PINS.md` (JSON doesn't support comments):

```markdown
| Package | Pinned Version | Latest | Reason | Reference |
|---------|----------------|--------|--------|-----------|
| some-package | ^2.1.0 | 3.2.0 | v3.x incompatible with other-package@4.x | ADR-012 |
```

For Python/Rust, use inline comments:

```toml
# PINNED: v3.x breaks API compatibility, see ADR-012
some-package = ">=2.1.0,<3.0.0"
```

---

## 4. Project Structure

### 4.1 Monorepo Layout

```
project-root/
├── .claude/
│   ├── commands/           # Claude Code automation commands
│   │   ├── development/    # Dev lifecycle commands
│   │   ├── review/         # Code review commands
│   │   ├── test/           # Testing commands
│   │   └── deploy/         # Deployment commands
│   ├── memory/             # Persistent project state
│   ├── templates/          # Document templates
│   └── scripts/            # Supporting automation scripts
├── apps/
│   ├── web/                # Next.js web application
│   ├── api/                # Python API service
│   └── cli/                # Rust CLI application
├── packages/
│   ├── ui/                 # Shared React components (shadcn/ui)
│   ├── config/             # Shared configuration
│   └── utils/              # Shared utilities
├── crates/                 # Shared Rust crates
├── docs/                   # Sphinx documentation (Diátaxis)
│   ├── conf.py             # Sphinx configuration
│   ├── index.md            # Documentation home
│   ├── tutorials/          # Learning-oriented
│   ├── how-to/             # Task-oriented
│   ├── reference/          # Information-oriented
│   │   └── api/            # Auto-generated API docs
│   ├── explanation/        # Understanding-oriented
│   ├── _static/            # Custom CSS, images
│   └── _templates/         # Custom Sphinx templates
├── constitution/           # This directory
│   ├── constitution.md     # Global principles (this file)
│   ├── python.md
│   ├── rust.md
│   ├── typescript.md
│   ├── react-nextjs.md
│   ├── tailwind-shadcn.md
│   ├── testing.md
│   ├── documentation.md
│   ├── git-cicd.md
│   └── security.md
├── pnpm-workspace.yaml
├── Cargo.toml              # Rust workspace
└── pyproject.toml          # Python workspace (if applicable)
```

### 4.2 Package Management

| Ecosystem | Tool | Configuration |
|-----------|------|---------------|
| Node.js | pnpm | Workspace monorepo with strict peer dependencies |
| Python | Poetry or venv | See `python.md` §2 for complexity threshold |
| Rust | Cargo | Workspace with shared dependencies |

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

## 6. Workflow Recommendations

Based on your development context:

### 6.1 Obsidian Integration

- **Memory files** in `.claude/memory/` **SHOULD** use markdown compatible with Obsidian
- **Risk registers** and **decision logs** **MAY** include YAML frontmatter for Dataview queries
- **Project documentation** **SHOULD** follow the same structure as your Obsidian vault

### 6.2 Tauri Desktop Applications

- Rust backend code **MUST** follow `rust.md` standards
- Tauri commands **MUST** have comprehensive doc comments
- IPC types **MUST** be shared between Rust and TypeScript via `ts-rs` or similar

### 6.3 AWS GovCloud Considerations

- Infrastructure code **MUST** include compliance tags
- Deployment scripts **SHOULD** validate region configuration
- Secrets **MUST** use AWS Secrets Manager or Parameter Store

### 6.4 Claude Code Integration

- Commands **SHOULD** be organized by lifecycle phase (not feature)
- Scripts **MUST** support `--json` output for Claude parsing
- Memory files **SHOULD** track project state across sessions
- Templates **SHOULD** include INCOSE-derived maturity states

---

## 7. Performance Standards

### 7.1 Frontend Performance

| Metric | Target | Blocking |
|--------|--------|----------|
| Largest Contentful Paint (LCP) | <2.5s | Yes |
| First Input Delay (FID) | <100ms | Yes |
| Cumulative Layout Shift (CLS) | <0.1 | Yes |
| Time to First Byte (TTFB) | <200ms | No |
| Bundle Size (initial) | <200KB | No |

### 7.2 API Performance

| Metric | Target | Blocking |
|--------|--------|----------|
| P50 Response Time | <100ms | No |
| P95 Response Time | <500ms | Yes |
| P99 Response Time | <1000ms | Yes |
| Error Rate | <0.1% | Yes |

---

## 8. Documentation Standards

### 8.1 Framework

All documentation **MUST** follow the Diátaxis framework, organizing content into four quadrants:

| Quadrant | Purpose | User Need |
|----------|---------|-----------|
| **Tutorials** | Learning by doing | "Teach me" |
| **How-To Guides** | Solving specific problems | "Help me achieve X" |
| **Reference** | Looking up information | "Show me the details" |
| **Explanation** | Understanding concepts | "Help me understand why" |

→ See `documentation.md` for full Diátaxis guidelines and templates.

### 8.2 Tooling

| Tool | Purpose | Configuration |
|------|---------|---------------|
| Sphinx | Documentation generator | `docs/conf.py` |
| Furo | Theme (clean, responsive) | Via `html_theme` |
| MyST Parser | Markdown support | All docs in `*.md` |
| GitHub Pages | Hosting | Automated via CI |

### 8.3 Required Documents

| Document | Location | Quadrant | Update Frequency |
|----------|----------|----------|------------------|
| Getting Started | `docs/tutorials/` | Tutorial | On major changes |
| Installation Guide | `docs/how-to/` | How-To | On dependency changes |
| API Reference | `docs/reference/` | Reference | On API changes |
| Architecture | `docs/explanation/` | Explanation | On architecture changes |
| README.md | Root | Mixed (acceptable) | On feature changes |
| CHANGELOG.md | Root | Reference | Every release |
| CONTRIBUTING.md | Root | How-To | Annually |

### 8.4 Code Documentation Coverage

| Scope | Requirement |
|-------|-------------|
| Public APIs | **MUST** have 100% documentation |
| Internal APIs | **SHOULD** have 80% documentation |
| Complex algorithms | **MUST** include explanatory comments |
| Non-obvious code | **SHOULD** include inline comments |

→ See language-specific files for docstring/JSDoc/doc-comment formats.

---

## Glossary

| Term | Definition |
|------|------------|
| **ADR** | Architecture Decision Record - documents significant technical decisions |
| **CVA** | Class Variance Authority - type-safe variant styling for components |
| **Diátaxis** | Documentation framework organizing content into tutorials, how-to guides, reference, and explanation |
| **E2E** | End-to-End testing - tests complete user workflows |
| **Furo** | Sphinx theme providing clean, responsive documentation |
| **JSDoc** | JavaScript documentation comments standard |
| **LCP** | Largest Contentful Paint - web performance metric |
| **MBSE** | Model-Based Systems Engineering |
| **MyST** | Markedly Structured Text - Markdown parser for Sphinx |
| **SpecKit** | Project automation package with commands, scripts, templates |
| **Sphinx** | Documentation generator for Python projects (also supports other languages) |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-02 | Claude | Initial constitution |
| 2.0.0 | 2026-01-02 | Claude | Modularized into separate concern files |

---

*This constitution is a living document. Propose changes via pull request.*
