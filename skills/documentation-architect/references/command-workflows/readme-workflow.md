# README Workflow

Detailed workflow for `/docs.readme` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Workflow Steps](#workflow-steps)
- [README Best Practices](#readme-best-practices)
- [CHANGELOG Management](#changelog-management)
- [Outputs](#outputs)
- [Idempotency](#idempotency)

---

## Purpose

Direct management of root documentation files:
1. Generate or update README.md following best practices
2. Maintain CHANGELOG.md using Keep a Changelog format
3. Sync with docs/ structure when present
4. Extract metadata from project configuration
5. Present changes for user approval

---

## Trigger Conditions

**Explicit**:
- `/docs.readme` - Update README.md
- `/docs.readme --init` - Create new README.md
- `/docs.readme --changelog VERSION` - Add changelog entry

**Auto-suggested**:
- After `/docs.init` completes
- After release/version bump
- When README.md is outdated vs docs/

---

## Workflow Steps

### Mode: Update README (`/docs.readme`)

#### Step 1: Analyze Current State

```
Analyzing project state...

Project: my-awesome-project
├─ Type: TypeScript library
├─ Version: 2.1.0 (from package.json)
├─ License: MIT
└─ Repository: github.com/user/repo

Current README.md:
├─ Exists: Yes
├─ Size: 2,847 characters
├─ Sections: 6 found
└─ Last modified: 2024-01-10

docs/ structure:
├─ Exists: Yes
├─ Index: docs/index.md
└─ Links to README: Yes
```

#### Step 2: Compare to Best Practices

```
README Analysis:

Required Sections:
├─ ✓ Title & description
├─ ✓ Installation
├─ ⚠ Quick start (outdated)
├─ ✓ Documentation links
├─ ✗ Features (missing)
├─ ✓ Contributing
└─ ✓ License

Recommendations:
1. Add Features section
2. Update Quick start example
3. Add badges (optional)
```

#### Step 3: Generate Updates

```markdown
## Proposed Changes to README.md

### Add: Features Section

+ ## Features
+
+ - Feature 1: Description
+ - Feature 2: Description
+ - Feature 3: Description

### Update: Quick Start

- ```javascript
- // Old example code
- ```
+ ```javascript
+ // New example code reflecting v2.1.0
+ ```

Accept these changes? [Y/n/edit]
```

#### Step 4: Apply Changes

```
Applying changes...

✓ Added Features section
✓ Updated Quick start example

README.md updated successfully.
```

---

### Mode: Initialize (`/docs.readme --init`)

#### Step 1: Extract Project Metadata

Using `readme_generator.py`:

```
Extracting project metadata...

From package.json:
├─ Name: my-awesome-project
├─ Description: A library for doing awesome things
├─ Version: 2.1.0
├─ License: MIT
├─ Author: John Doe
├─ Keywords: awesome, library, typescript
└─ Has CLI: No

Project type: Library
```

#### Step 2: Detect Features

```
Detecting project features...

From codebase analysis:
├─ TypeScript support
├─ ESM and CJS exports
├─ Full type definitions
└─ Zero dependencies

From docs/:
├─ Getting started guide
├─ API reference
└─ Contributing guide
```

#### Step 3: Generate README

```markdown
# my-awesome-project

> A library for doing awesome things

## Installation

```bash
npm install my-awesome-project
```

## Quick Start

```typescript
import { awesome } from 'my-awesome-project';

const result = awesome();
console.log(result);
```

## Features

- TypeScript support with full type definitions
- ESM and CommonJS exports
- Zero dependencies

## Documentation

- [Getting Started](docs/user/getting-started/)
- [API Reference](docs/developer/reference/api/)
- [Contributing](docs/developer/contributing/)

## Contributing

See [Contributing Guide](docs/developer/contributing/getting-started.md).

## License

MIT - see [LICENSE](LICENSE) for details.
```

#### Step 4: Create Files

```
Creating files...

Files to create:
├─ README.md (new)
└─ CHANGELOG.md (new, if not exists)

Proceed? [Y/n]

✓ Created README.md
✓ Created CHANGELOG.md

Files created successfully.
```

---

### Mode: Changelog (`/docs.readme --changelog VERSION`)

#### Step 1: Parse Existing Changelog

```
Parsing CHANGELOG.md...

Current entries:
├─ [Unreleased] - 3 items
├─ [2.0.0] - 2024-01-01
├─ [1.5.0] - 2023-12-15
└─ [1.0.0] - 2023-11-01
```

#### Step 2: Gather Changes

```
What changes are in version 2.1.0?

[A]dded - New features
[C]hanged - Changed functionality
[F]ixed - Bug fixes
[D]eprecated - Deprecated features
[R]emoved - Removed features
[S]ecurity - Security fixes

Enter changes (one per line, prefix with category letter):
> A New awesome feature
> F Fixed edge case in parsing
> C Improved performance by 50%
```

#### Step 3: Generate Entry

```markdown
## Proposed Changelog Entry

## [2.1.0] - 2024-01-20

### Added

- New awesome feature

### Changed

- Improved performance by 50%

### Fixed

- Fixed edge case in parsing

Add this entry? [Y/n/edit]
```

#### Step 4: Update Changelog

```
Updating CHANGELOG.md...

├─ Moved [Unreleased] items to [2.1.0]
├─ Added new [2.1.0] section
├─ Updated comparison links
└─ Created new empty [Unreleased]

✓ CHANGELOG.md updated successfully.
```

---

## README Best Practices

### Required Sections

| Section | Priority | Purpose |
|---------|----------|---------|
| Title + Description | Required | What is this? |
| Installation | Required | How to get it |
| Quick Start | Required | Minimum viable example |
| Documentation | High | Links to full docs |
| Features | High | Why use this? |
| Contributing | Medium | How to contribute |
| License | Required | Legal requirements |

### Optional Sections

| Section | When to Include |
|---------|-----------------|
| Badges | Public projects |
| Screenshots | Visual projects |
| API Overview | Libraries |
| CLI Reference | CLI tools |
| FAQ | Common questions |
| Acknowledgments | Credits needed |

### README Template

```markdown
# Project Name

> One-line description of what this project does.

[Badges: build status, version, license, etc.]

## Installation

[Package manager installation commands]

## Quick Start

[Minimal code example that works]

## Features

[Bullet list of key features]

## Documentation

[Links to docs/ structure]

## Contributing

[Link to contribution guide or brief instructions]

## License

[License name and link]
```

### Quality Guidelines

1. **Scannable**: Users should grasp purpose in 30 seconds
2. **Actionable**: Installation to first use in under 5 minutes
3. **Current**: Examples work with latest version
4. **Linked**: Point to deeper docs, don't repeat them
5. **Welcoming**: Make contributing easy to discover

---

## CHANGELOG Management

### Keep a Changelog Format

Following [keepachangelog.com](https://keepachangelog.com/):

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New feature in development

## [1.0.0] - 2024-01-01

### Added

- Initial release

[Unreleased]: https://github.com/user/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

### Change Categories

| Category | Use For |
|----------|---------|
| Added | New features |
| Changed | Changes in existing functionality |
| Deprecated | Soon-to-be removed features |
| Removed | Now removed features |
| Fixed | Bug fixes |
| Security | Vulnerability fixes |

### Version Links

Automatically generate comparison links:

```markdown
[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| README | `README.md` | Project overview |
| CHANGELOG | `CHANGELOG.md` | Version history |
| Backup | `.readme.md.bak` | Previous version (if updating) |

---

## Idempotency

**Safe behaviors**:
- Always shows diff before applying changes
- Creates backup before modifying
- Preserves custom sections
- Never deletes user content
- Merges intelligently

**Existing README handling**:

```
Existing README.md detected.

Analysis:
├─ Standard sections: 5 (will update)
├─ Custom sections: 2 (will preserve)
└─ Manual content: Detected

Options:
1. Update - Merge updates, keep customizations
2. Replace - Generate fresh (backup existing)
3. Skip - Keep existing unchanged
```

**Custom section preservation**:

```markdown
## Features           ← Updated (standard section)

## My Custom Section  ← Preserved (not in template)

## Installation       ← Updated (standard section)

## Special Thanks     ← Preserved (not in template)
```

**Changelog append-only**:

- New entries added at top
- Existing entries never modified
- [Unreleased] section managed automatically
- Version links kept in sync
