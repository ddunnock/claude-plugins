# Memory Files Manifest

> **Generated**: 2026-01-15
> **Tech Stack**: Python 3.11+ / Poetry / MCP SDK

---

## Installed Memory Files

### Universal (Always Included)

| File               | Purpose                                                     |
|--------------------|-------------------------------------------------------------|
| `constitution.md`  | Core principles and constraints for all Claude interactions |
| `documentation.md` | Diátaxis documentation framework standards                  |
| `git-cicd.md`      | Git workflow and CI/CD best practices                       |
| `security.md`      | Security guidelines and vulnerability prevention            |
| `testing.md`       | Testing standards and coverage requirements                 |

### Tech-Specific

| File        | Trigger         | Purpose                                 |
|-------------|-----------------|-----------------------------------------|
| `python.md` | Python detected | Python coding standards, typing, Poetry |

---

## Source

Memory files sourced from: `docs/reference/claude-standards/`

## Customization

To add project-specific memory:
1. Create custom `.md` files in this directory
2. Update this manifest
3. Files are read by Claude during context loading