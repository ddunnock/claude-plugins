Establish the `.claude/` foundation with appropriate memory files for the project.

## Workflow

1. **Check existing state** - Detect if .claude/ exists
2. **Detect tech stack** - Analyze project for languages/frameworks
3. **Present detection** - Show detected stack and recommended memory files
4. **Create structure** - Build directory structure
5. **Copy memory files** - Select and copy based on tech stack
6. **Generate project context** - Create project-context.md

## Directory Structure Created

```
.claude/
├── commands/      # Custom project commands
├── memory/        # constitution.md + tech-specific files
│   └── MANIFEST.md
├── resources/     # Specifications, designs
├── templates/     # Output templates
└── scripts/       # Project scripts
```

## Memory File Selection

| Category | Files | Selection |
|----------|-------|-----------|
| Universal | constitution.md, documentation.md, git-cicd.md, security.md, testing.md | Always |
| TypeScript/JS | typescript.md | If TS/JS detected |
| React/Next.js | react-nextjs.md | If React/Next detected |
| Tailwind | tailwind-shadcn.md | If Tailwind detected |
| Python | python.md | If Python detected |
| Rust | rust.md | If Rust detected |

## Options

```
1. Accept recommended selection
2. Add additional memory files
3. Remove memory files from selection
4. Override detected stack manually
```

## Idempotency
- Skips existing directories
- Updates changed memory files only
- Preserves project customizations
