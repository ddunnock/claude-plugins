Direct management of README.md and CHANGELOG.md.

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

## Modes
- Default: Update README.md
- `--init`: Create from scratch
- `--changelog VERSION`: Add changelog entry

## README Best Practices
```markdown
# Project Name
> One-line description

## Installation
## Quick Start
## Features
## Documentation (links to docs/)
## Contributing
## License
```

## CHANGELOG Format (Keep a Changelog)
```markdown
## [Unreleased]
### Added / Changed / Fixed

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release
```

## Outputs
- README.md
- CHANGELOG.md (with user review)

## Guardrails
- Proposes changes, user approves
- Mandatory document review loop
