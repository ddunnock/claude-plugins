# Developer Documentation Section Template

Use this template for organizing `docs/developer/` content.

---

## Directory Structure

```
docs/developer/
├── architecture/             # System Design
│   ├── overview.md           # High-level architecture
│   ├── decisions/            # Architecture Decision Records
│   │   ├── index.md
│   │   └── ADR-001-{title}.md
│   └── diagrams/             # Architecture diagrams
│
├── contributing/             # Contribution Guides
│   ├── getting-started.md    # How to contribute
│   ├── development-setup.md  # Dev environment
│   ├── coding-standards.md   # Code style
│   └── pull-requests.md      # PR process
│
└── reference/                # Technical Reference
    ├── api/                  # API documentation
    │   ├── index.md
    │   └── {module}.md
    └── internals/            # Internal documentation
```

---

## architecture/overview.md Template

```markdown
# Architecture Overview

High-level overview of {PROJECT_NAME}'s architecture.

## System Context

{Diagram or description of where this system fits in the larger context.}

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────>│  {PROJECT}  │────>│  External   │
│             │<────│             │<────│  Service    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Core Components

### {Component 1}

**Purpose**: {What it does}
**Location**: `{path/to/code}`

{Brief description of responsibilities.}

### {Component 2}

**Purpose**: {What it does}
**Location**: `{path/to/code}`

{Brief description of responsibilities.}

## Data Flow

{Description of how data moves through the system.}

```
Request → {Step 1} → {Step 2} → {Step 3} → Response
```

## Key Design Decisions

| Decision | Rationale | See Also |
|----------|-----------|----------|
| {Decision 1} | {Why} | [ADR-001](decisions/ADR-001-title.md) |
| {Decision 2} | {Why} | [ADR-002](decisions/ADR-002-title.md) |

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| {Layer} | {Tech} | {Why chosen} |

## Related Documentation

- [API Reference](../reference/api/)
- [Contributing](../contributing/getting-started.md)
```

---

## architecture/decisions/ADR-{NNN}-{title}.md Template

```markdown
# ADR-{NNN}: {Title}

**Status**: {Proposed | Accepted | Deprecated | Superseded}
**Date**: {YYYY-MM-DD}
**Superseded by**: {ADR-XXX if applicable}

## Context

{What is the issue that we're seeing that is motivating this decision?}

## Decision

{What is the change that we're proposing and/or doing?}

## Consequences

### Positive

- {Benefit 1}
- {Benefit 2}

### Negative

- {Drawback 1}
- {Drawback 2}

### Neutral

- {Observation 1}

## Alternatives Considered

### {Alternative 1}

{Description and why it was rejected.}

### {Alternative 2}

{Description and why it was rejected.}

## References

- {Link to relevant discussion}
- {Link to related documentation}
```

---

## contributing/getting-started.md Template

```markdown
# Contributing to {PROJECT_NAME}

Thank you for your interest in contributing!

## Ways to Contribute

- **Bug Reports**: Found a bug? [Open an issue]({repo}/issues/new)
- **Feature Requests**: Have an idea? [Start a discussion]({repo}/discussions)
- **Code**: Fix bugs or add features via pull requests
- **Documentation**: Help improve these docs

## Quick Start

### 1. Fork and Clone

```bash
git clone https://github.com/{your-username}/{repo}.git
cd {repo}
```

### 2. Set Up Development Environment

See [Development Setup](development-setup.md) for detailed instructions.

```bash
{setup commands}
```

### 3. Create a Branch

```bash
git checkout -b {type}/{description}
# Examples: fix/login-bug, feat/new-feature
```

### 4. Make Changes

- Follow [Coding Standards](coding-standards.md)
- Write tests for new functionality
- Update documentation as needed

### 5. Submit Pull Request

See [Pull Request Guide](pull-requests.md) for our PR process.

## Code of Conduct

This project follows [Contributor Covenant](https://www.contributor-covenant.org/).
Be respectful and constructive.

## Getting Help

- Questions: [GitHub Discussions]({repo}/discussions)
- Chat: {Discord/Slack link if applicable}
```

---

## reference/api/{module}.md Template

```markdown
# {Module Name} API

API reference for the `{module}` module.

## Overview

{Brief description of what this module provides.}

## Classes

### `{ClassName}`

{Description of the class.}

#### Constructor

```{language}
new {ClassName}(options: {OptionsType})
```

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `options.{param}` | `{type}` | Yes/No | {description} |

#### Methods

##### `{methodName}()`

{Description of what the method does.}

```{language}
{signature}
```

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `{param}` | `{type}` | {description} |

**Returns**: `{ReturnType}` - {description}

**Example**:

```{language}
{example code}
```

## Functions

### `{functionName}()`

{Description}

```{language}
{signature}
```

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `{param}` | `{type}` | {description} |

**Returns**: `{ReturnType}` - {description}

**Throws**: `{ErrorType}` - {when thrown}

## Types

### `{TypeName}`

```{language}
{type definition}
```

| Property | Type | Description |
|----------|------|-------------|
| `{prop}` | `{type}` | {description} |

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `{CONSTANT}` | `{value}` | {description} |
```

---

## Guidelines for Developer Docs

### Architecture Documentation
- Keep diagrams up to date
- Link ADRs to code changes
- Explain "why" not just "what"

### Contributing Guides
- Lower the barrier to entry
- Be explicit about expectations
- Provide clear examples

### API Reference
- Auto-generate where possible
- Include all public APIs
- Provide usage examples
- Document error cases
