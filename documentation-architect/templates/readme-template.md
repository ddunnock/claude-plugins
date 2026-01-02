# README Template

Use this template for project root `README.md`.

---

```markdown
# {PROJECT_NAME}

> {One-line description of what this project does}

{Optional: Badges - build status, version, license, etc.}

## Installation

```bash
{primary installation method}
```

{Alternative methods if applicable}

## Quick Start

{Minimal working example in 5-10 lines}

```{language}
{example code that actually works}
```

## Features

- **{Feature 1}**: {Brief description}
- **{Feature 2}**: {Brief description}
- **{Feature 3}**: {Brief description}

## Documentation

{If docs/ exists:}
- [Getting Started](docs/user/getting-started/quickstart.md)
- [Guides](docs/user/guides/)
- [API Reference](docs/developer/reference/api/)
- [Contributing](docs/developer/contributing/)

{If no docs/:}
See the [wiki]({repo}/wiki) for documentation.

## Contributing

{If CONTRIBUTING.md exists:}
See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute.

{If docs/developer/contributing exists:}
See [Contributing Guide](docs/developer/contributing/getting-started.md).

{Otherwise:}
Contributions welcome! Please open an issue first to discuss changes.

## License

{License name} - see [LICENSE](LICENSE) for details.
```

---

## Template Variables

| Variable | Source | Required |
|----------|--------|----------|
| `{PROJECT_NAME}` | package.json name or directory | Yes |
| `{language}` | Primary language | Yes |
| `{repo}` | Git remote URL | If linking to issues |

## Sections Breakdown

### Required Sections

| Section | Purpose | Length |
|---------|---------|--------|
| Title + Description | What is this? | 1-2 lines |
| Installation | How to get it | 3-5 lines |
| Quick Start | First working example | 5-15 lines |
| License | Legal requirements | 1 line |

### Recommended Sections

| Section | Purpose | When to Include |
|---------|---------|-----------------|
| Features | Why use this? | Always helpful |
| Documentation | Where to learn more | If docs exist |
| Contributing | How to help | If accepting PRs |

### Optional Sections

| Section | When to Include |
|---------|-----------------|
| Badges | Public/mature projects |
| Screenshots | Visual applications |
| Requirements | Complex prerequisites |
| Configuration | Many config options |
| FAQ | Common questions |
| Acknowledgments | Credits needed |
| Changelog | If not separate file |

## Quality Checklist

- [ ] Title clearly states project name
- [ ] Description explains purpose in one line
- [ ] Installation command is copy-pasteable
- [ ] Quick Start example actually works
- [ ] All links are valid
- [ ] License is specified
- [ ] Contact/help info provided

## README vs Documentation

**README should**:
- Be scannable in 30 seconds
- Get users started immediately
- Link to detailed docs

**README should NOT**:
- Duplicate documentation content
- Include exhaustive API reference
- Have multiple installation variants
- Contain long configuration guides

---

## Example: Library README

```markdown
# awesome-lib

> A fast, lightweight library for processing widgets

[![npm version](https://badge.fury.io/js/awesome-lib.svg)](https://www.npmjs.com/package/awesome-lib)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Installation

```bash
npm install awesome-lib
```

## Quick Start

```javascript
import { processWidget } from 'awesome-lib';

const result = processWidget({ type: 'standard' });
console.log(result);
// Output: { processed: true, timestamp: ... }
```

## Features

- **Fast**: Processes 10k widgets/second
- **Lightweight**: Zero dependencies, 5KB gzipped
- **TypeScript**: Full type definitions included

## Documentation

- [Getting Started](docs/user/getting-started/)
- [API Reference](docs/developer/reference/api/)

## Contributing

See [Contributing Guide](docs/developer/contributing/).

## License

MIT - see [LICENSE](LICENSE)
```

---

## Example: CLI README

```markdown
# awesome-cli

> A command-line tool for managing projects

## Installation

```bash
npm install -g awesome-cli
```

## Quick Start

```bash
# Initialize a new project
awesome init my-project

# Run the project
cd my-project
awesome run
```

## Commands

| Command | Description |
|---------|-------------|
| `awesome init <name>` | Create new project |
| `awesome run` | Run the project |
| `awesome build` | Build for production |

## Documentation

Full documentation at [docs/](docs/).

## License

MIT
```
