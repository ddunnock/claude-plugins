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

---

## GATE: Required Before Proceeding

**STOP after initialization. Present results and confirm before proceeding.**

After initialization, you MUST:

1. **Present the created structure** showing:
   - Directories created
   - Memory files installed
   - Detected tech stack

2. **Confirm memory file selection** is appropriate:
   - List universal files (always included)
   - List tech-specific files (based on detection)
   - Ask if any adjustments needed

3. **Wait for user confirmation** before proceeding to other commands

### Gate Response Template

```
## Initialization Complete

### Directory Structure Created
.claude/
├── commands/
├── memory/
├── resources/
├── templates/
└── scripts/

### Detected Tech Stack
- [Languages detected]
- [Frameworks detected]

### Memory Files Installed
**Universal:**
- constitution.md
- documentation.md
- git-cicd.md
- security.md
- testing.md

**Tech-Specific:**
- [Based on detection]

### Next Steps
1. Review the memory files for your project needs
2. Add specifications to .claude/resources/
3. Run `/speckit.plan` when specs are ready

**Is this configuration correct, or would you like to adjust the memory files?**
```
