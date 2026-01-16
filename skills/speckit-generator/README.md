# SpecKit Generator

Project-focused specification and task management system for Claude Code with git checkpoint safety, mandatory approval gates, and implementation hooks.

## Overview

SpecKit Generator transforms specifications into executed implementations through a structured workflow with 7 commands. Each command produces artifacts that require user review before proceeding, ensuring quality and alignment at every step.

```
/speckit.init → /speckit.plan → /speckit.tasks → /speckit.implement
                     ↑              ↑                    ↓
              /speckit.analyze  /speckit.clarify   /speckit.revert
```

### Key Features

- **Git Checkpoint Safety**: Automatic checkpoints before implementation enable safe rollback
- **Memory-Driven Compliance**: Constitution and tech-specific memory files guide all execution
- **Mandatory Gates**: Each command requires explicit user approval before proceeding
- **Intelligent Failure Analysis**: Revert command analyzes failures and recommends fixes
- **Idempotent Operations**: All commands safe to run repeatedly

## Installation

### As a Claude Code Plugin

1. Clone or copy this directory to your Claude Code plugins location
2. Enable the plugin in Claude Code settings
3. Commands will be available as `/speckit.*`

### As a Skill

The skill is automatically available when the skill files are in the skills directory.

## Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/speckit.init` | Establish .claude/ foundation with git | New projects or incomplete setup |
| `/speckit.plan` | Create plans from specifications | After specs exist in resources/ |
| `/speckit.tasks` | Generate tasks from plans | After plans are approved |
| `/speckit.analyze` | Audit project consistency | Anytime for health check |
| `/speckit.clarify` | Resolve ambiguities | When specs have open questions |
| `/speckit.implement` | Execute tasks with git checkpoint | When ready to implement |
| `/speckit.revert` | Revert to checkpoint with analysis | When implementation fails |

## Quick Start

### 1. Initialize a Project

```bash
/speckit.init
```

This will:
- Validate git is available (required for checkpoints)
- Detect your tech stack
- Create the `.claude/` directory structure
- Install all 6 project commands (plan, tasks, analyze, clarify, implement, revert)
- Install appropriate memory files
- Set up `.gitignore` for speckit

### 2. Add Your Specification

Place your specification document in `.claude/resources/`:

```
.claude/resources/my-feature-spec.md
```

### 3. Generate a Plan

```bash
/speckit.plan
```

Review the generated plan and approve before proceeding.

### 4. Generate Tasks

```bash
/speckit.tasks
```

Review the generated tasks with their acceptance criteria.

### 5. Implement

```bash
/speckit.implement "Phase 1"
```

This will:
- Create a git checkpoint (revertable)
- Execute tasks in the specified phase
- Update task statuses with verification evidence
- Update project-status.md with progress

### 6. If Something Goes Wrong

```bash
/speckit.revert
```

This will:
- Revert to the last checkpoint
- Analyze what went wrong
- Recommend spec/plan/task updates

## Directory Structure

After initialization, your project will have:

```
.claude/
├── commands/              # Project-specific commands (all 6 installed)
│   ├── plan.md            # Create implementation plans
│   ├── tasks.md           # Generate tasks from plans
│   ├── analyze.md         # Read-only project audit
│   ├── clarify.md         # Resolve spec ambiguities
│   ├── implement.md       # Task execution with hooks
│   └── revert.md          # Checkpoint revert with analysis
├── memory/                # Constitution + tech-specific guidelines
│   ├── constitution.md    # Core principles
│   ├── MANIFEST.md        # Memory file index
│   └── project-status.md  # Implementation progress tracking
├── resources/             # Specifications, plans, tasks
│   ├── spec.md            # Your specification
│   ├── plan.md            # Generated plan
│   └── *-tasks.md         # Generated tasks
├── templates/             # Output templates
└── scripts/               # Project scripts
```

## Memory Files

SpecKit uses memory files to provide consistent guidelines across all commands.

### Universal (Always Included)

| File | Purpose |
|------|---------|
| `constitution.md` | Core principles and mandatory constraints |
| `documentation.md` | Documentation standards |
| `git-cicd.md` | Git workflow and CI/CD practices |
| `security.md` | Security requirements |
| `testing.md` | Testing strategies |

### Tech-Specific (Auto-Detected)

| File | Detected By |
|------|-------------|
| `typescript.md` | tsconfig.json, .ts files |
| `react-nextjs.md` | next.config.js, React imports |
| `tailwind-shadcn.md` | tailwind.config.js |
| `python.md` | setup.py, pyproject.toml, .py files |
| `rust.md` | Cargo.toml, .rs files |

## Git Checkpoint System

### How It Works

1. **Before `/speckit.implement`**: A checkpoint tag is created
   ```
   speckit-checkpoint-20240115_143500
   ```

2. **During implementation**: Normal git operations continue

3. **If something goes wrong**: Use `/speckit.revert` to return to checkpoint

### Checkpoint Commands

```bash
# List all checkpoints
/speckit.revert --list

# Revert to most recent
/speckit.revert

# Revert to specific checkpoint
/speckit.revert speckit-checkpoint-20240115_143500

# Preview without reverting
/speckit.revert --dry-run
```

## Hooks

SpecKit enforces workflow integrity through hooks.

### Pre-Implementation Hooks

| Hook | Purpose |
|------|---------|
| Load project-status.md | Understand current state |
| Validate argument | Show status if missing/invalid |
| Verify tasks actionable | Filter completed, check dependencies |
| Present execution plan | Get user confirmation |
| Create git checkpoint | Enable safe rollback |

### Post-Implementation Hooks

| Hook | Purpose |
|------|---------|
| Update tasks.md | Status and acceptance criteria with evidence |
| Update project-status.md | Progress metrics and activity log |
| Output summary | Completed tasks, next steps, revert option |

## Failure Analysis

When you revert, SpecKit analyzes what went wrong:

| Category | Indicators | Recommendation |
|----------|------------|----------------|
| SPEC_GAP | Requirements unclear | `/speckit.clarify` |
| APPROACH_WRONG | Architecture mismatch | `/speckit.plan --revise` |
| DEPENDENCY_ISSUE | External problems | Update dependencies |
| TEST_MISMATCH | Tests don't match | Update test fixtures |
| SCOPE_CREEP | Too much at once | Decompose tasks |
| KNOWLEDGE_GAP | Unfamiliar technology | Research first |

## Workflow Best Practices

### Do

- Run `/speckit.analyze` before approving plans
- Run `/speckit.clarify` when specs have [TBD] items
- Review each command's output before proceeding
- Use git commits between major phases
- Check project-status.md for current state

### Don't

- Chain commands without reviewing output
- Skip the analyze step before implementation
- Ignore failed acceptance criteria
- Force push after checkpoint (breaks revert)
- Delete checkpoint tags manually

## Configuration

### Plugin Configuration

The plugin is configured via `.claude-plugin/plugin.json`:

```json
{
  "name": "speckit-generator",
  "version": "1.3.0",
  "hooks": "../hooks/hooks.json",
  "commands": [...]
}
```

### Project Configuration

Project-specific settings are in `.claude/memory/`:

- `constitution.md` - Customize core principles
- Tech-specific files - Adjust guidelines per technology

## Troubleshooting

### "Git not found"

Install git before running `/speckit.init`:
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# Download from https://git-scm.com/
```

### "No checkpoints found"

Checkpoints are created by `/speckit.implement`. If none exist:
1. You haven't run implement yet, or
2. Checkpoint tags were deleted

### "Project not initialized"

Run `/speckit.init` first to create the `.claude/` structure.

### Tasks not updating

Ensure you're running the full implement workflow. Post-implementation hooks only run when the command completes normally.

## Version History

### v1.4.0 (Current)
- `/speckit.init` now installs all 6 commands as project-local `/plan`, `/tasks`, `/analyze`, `/clarify`, `/implement`, `/revert`
- Added `handoffs` YAML frontmatter to all command templates for command flow navigation
- Added `$ARGUMENTS` user input support to all command templates

### v1.3.0
- Added `/speckit.revert` command with intelligent failure analysis
- Added git checkpoint system to `/speckit.implement`
- Added git validation to `/speckit.init`
- Added `.gitignore` setup
- Added 3 new hook scripts for git operations

### v1.2.0
- Added pre-implementation hooks
- Added project-status.md tracking
- Added project-level command templates

### v1.1.0
- Added post-implementation hooks
- Added acceptance criteria verification

### v1.0.0
- Initial release with 6 commands
- Memory file system
- Gate enforcement

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure:
1. All commands follow the gate pattern
2. Hooks are properly documented
3. Memory files are idempotent
4. Tests pass before submitting

## Support

For issues and feature requests, please open an issue in the repository.
