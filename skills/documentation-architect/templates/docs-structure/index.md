# Documentation Index Template

Use this template for `docs/index.md` - the documentation landing page.

---

```markdown
# {PROJECT_NAME}

> {ONE_LINE_DESCRIPTION}

## Overview

{2-3 sentence overview of what this project does and who it's for.}

## Quick Links

### For Users

- [Getting Started](user/getting-started/quickstart.md) - Start here
- [Guides](user/guides/) - Task-focused how-to guides
- [Concepts](user/concepts/) - Understanding the system
- [Reference](user/reference/) - Configuration and options

### For Developers

- [Architecture](developer/architecture/overview.md) - System design
- [Contributing](developer/contributing/getting-started.md) - How to contribute
- [API Reference](developer/reference/api/) - Technical reference

## Installation

{Brief installation command - details in getting-started}

```bash
# Example
npm install {package-name}
```

## Quick Example

{Minimal working example - 5-10 lines max}

```{language}
// Example code
```

## Getting Help

- [GitHub Issues]({repo}/issues) - Bug reports and features
- [Discussions]({repo}/discussions) - Questions and community
```

---

## Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{PROJECT_NAME}` | package.json name | "My Awesome Project" |
| `{ONE_LINE_DESCRIPTION}` | package.json description | "A library for X" |
| `{language}` | Project primary language | typescript, python |
| `{repo}` | Git remote URL | github.com/user/repo |

## Guidelines

1. **Keep it scannable** - Users should understand purpose in 30 seconds
2. **Link, don't repeat** - Point to detailed docs, don't duplicate content
3. **Show, don't tell** - Include a working quick example
4. **Clear navigation** - Obvious paths for users vs developers
