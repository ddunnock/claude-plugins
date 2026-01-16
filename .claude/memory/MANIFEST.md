# Memory Files Manifest

> **Generated**: 2026-01-16
> **Project**: Knowledge MCP
> **Detected Stack**: Python (Poetry, Pyright, pytest)

---

## Installed Memory Files

| File                | Category      | Description                                   | Last Updated  |
|---------------------|---------------|-----------------------------------------------|---------------|
| `constitution.md`   | Universal     | Global principles, quality gates, workflows   | 2026-01-16    |
| `documentation.md`  | Universal     | Diátaxis framework, Sphinx/Furo, GitHub Pages | 2026-01-16    |
| `git-cicd.md`       | Universal     | Git workflow, commits, branches, PRs, CI/CD   | 2026-01-16    |
| `security.md`       | Universal     | Dependencies, secrets, input validation       | 2026-01-16    |
| `testing.md`        | Universal     | Coverage requirements, test patterns, E2E     | 2026-01-16    |
| `python.md`         | Tech-Specific | Python ≥3.11, Poetry, docstrings, type hints  | 2026-01-16    |
| `project-status.md` | Status        | Implementation progress tracking              | 2026-01-16    |

---

## Tech Stack Detection

| Category        | Detected                | Confidence                     |
|-----------------|-------------------------|--------------------------------|
| Language        | Python 3.11-3.13        | High (pyproject.toml)          |
| Package Manager | Poetry                  | High (pyproject.toml)          |
| Type Checker    | Pyright (strict)        | High (tool.pyright config)     |
| Linter          | Ruff                    | High (tool.ruff config)        |
| Testing         | pytest + pytest-asyncio | High (tool.pytest config)      |
| Documentation   | Sphinx + Furo           | High (poetry dev dependencies) |

---

## Memory File Sources

All memory files are adapted from speckit-generator plugin templates:
```
~/.claude/plugins/cache/dunnock-plugins/speckit-generator/1.7.0/assets/memory/
```

Files have been customized for this project's specific tech stack and conventions.

---

## Excluded Files (Not Applicable)

| File                 | Reason                    |
|----------------------|---------------------------|
| `typescript.md`      | No TypeScript detected    |
| `react-nextjs.md`    | No React/Next.js detected |
| `tailwind-shadcn.md` | No Tailwind detected      |
| `rust.md`            | No Rust detected          |