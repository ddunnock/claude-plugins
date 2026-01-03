# CHANGELOG Template

Use this template for project root `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/).

---

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- {New feature description}

### Changed

- {Changed functionality description}

### Fixed

- {Bug fix description}

## [1.0.0] - YYYY-MM-DD

### Added

- Initial release
- {Feature 1}
- {Feature 2}

[Unreleased]: https://github.com/{user}/{repo}/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/{user}/{repo}/releases/tag/v1.0.0
```

---

## Change Categories

| Category | Use For | Example |
|----------|---------|---------|
| **Added** | New features | "Added dark mode support" |
| **Changed** | Changes in existing functionality | "Changed default timeout to 30s" |
| **Deprecated** | Soon-to-be removed features | "Deprecated `oldMethod()` in favor of `newMethod()`" |
| **Removed** | Now removed features | "Removed support for Node 14" |
| **Fixed** | Bug fixes | "Fixed race condition in login" |
| **Security** | Vulnerability fixes | "Fixed XSS vulnerability in comments" |

## Principles

### Guiding Principles

1. **Changelogs are for humans**, not machines
2. **Every version gets an entry**
3. **Group by type of change**
4. **Latest version first**
5. **Release date for each version**
6. **Link versions to diffs**

### What to Include

**DO include**:
- User-facing changes
- API changes
- Breaking changes (prominently)
- Security fixes
- Deprecations

**DON'T include**:
- Internal refactoring (unless it affects users)
- CI/CD changes
- Documentation updates (unless significant)
- Dependency bumps (unless they fix bugs)

---

## Version Entry Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added

- Added `newFeature()` method for processing widgets (#123)
- Added support for configuration via environment variables

### Changed

- Changed default timeout from 10s to 30s
- Improved error messages for invalid input

### Deprecated

- Deprecated `oldMethod()` - use `newMethod()` instead (will be removed in v3.0)

### Removed

- Removed support for Node.js 14 (EOL)

### Fixed

- Fixed memory leak when processing large files (#456)
- Fixed race condition in concurrent requests

### Security

- Fixed XSS vulnerability in user input handling (CVE-YYYY-XXXX)
```

---

## Unreleased Section

Always maintain an `[Unreleased]` section at the top:

```markdown
## [Unreleased]

### Added

- Work in progress feature

### Fixed

- Bug fix ready for next release
```

When releasing:
1. Move `[Unreleased]` items to new version section
2. Add date to new version
3. Create empty `[Unreleased]` section
4. Update comparison links

---

## Comparison Links

At the bottom of the changelog, maintain version comparison links:

```markdown
[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

This allows readers to click version numbers to see full diffs.

---

## Breaking Changes

Mark breaking changes prominently:

```markdown
## [2.0.0] - 2024-01-15

### Changed

- **BREAKING**: Renamed `config.apiKey` to `config.key`
- **BREAKING**: Changed return type of `process()` from `string` to `Result`

### Migration

To migrate from v1.x:

1. Rename `apiKey` to `key` in your configuration
2. Update code that uses `process()` return value:
   ```javascript
   // Before
   const result = process(data);

   // After
   const { value } = process(data);
   ```
```

---

## Example: Full Changelog

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for custom themes

## [2.1.0] - 2024-01-20

### Added

- Added `batchProcess()` method for bulk operations
- Added TypeScript type exports

### Fixed

- Fixed timeout handling in async operations (#89)

## [2.0.0] - 2024-01-01

### Changed

- **BREAKING**: Minimum Node.js version is now 18
- **BREAKING**: Renamed `initialize()` to `init()`

### Removed

- Removed deprecated `legacyMode` option

## [1.0.0] - 2023-12-01

### Added

- Initial release
- Core processing functionality
- Configuration via JSON file
- CLI interface

[Unreleased]: https://github.com/example/project/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/example/project/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/example/project/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/example/project/releases/tag/v1.0.0
```
