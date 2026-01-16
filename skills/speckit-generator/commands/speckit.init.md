Establish the `.claude/` foundation with appropriate memory files for the project.

## Workflow

1. **Validate git** - Check git is available, initialize repo if needed
2. **Check existing state** - Detect if .claude/ exists
3. **Detect tech stack** - Analyze project for languages/frameworks
4. **Present detection** - Show detected stack and recommended memory files
5. **Create structure** - Build directory structure
6. **Copy memory files** - Select and copy based on tech stack
7. **Initialize project-status.md** - Create status tracking file
8. **Install project commands** - Copy all 6 commands (plan, tasks, analyze, clarify, implement, revert) with hooks embedded
9. **Ensure .gitignore** - Create or update .gitignore for project safety
10. **Generate project context** - Create project-context.md

---

## MANDATORY: Git Validation (Step 1)

**CRITICAL**: Git must be available for checkpoint/revert functionality.

### Git Check Process

```bash
# 1. Verify git is installed
git --version

# 2. Check if in a git repository
git rev-parse --git-dir 2>/dev/null

# 3. If not in a repo, offer to initialize
git init
```

### Git Check Outcomes

| State | Action |
|-------|--------|
| Git not installed | **STOP** - Instruct user to install git |
| Not a git repo | Offer to run `git init` |
| Git repo exists | Continue |
| Git repo with uncommitted changes | Warn user, recommend commit before proceeding |

### Git Check Output

```markdown
## Git Status Check

| Check | Status |
|-------|--------|
| Git installed | ✓ v2.x.x |
| Git repository | ✓ Initialized |
| Working tree | ✓ Clean / ⚠ [N] uncommitted changes |

[If uncommitted changes:]
**Recommendation**: Commit current changes before running /speckit.init
```bash
git add . && git commit -m "Pre-speckit checkpoint"
```
```

---

## Directory Structure Created

```
.claude/
├── commands/           # Project commands (with hooks embedded)
│   ├── plan.md         # Create implementation plans
│   ├── tasks.md        # Generate tasks from plans
│   ├── analyze.md      # Read-only project audit
│   ├── clarify.md      # Resolve spec ambiguities
│   ├── implement.md    # Task execution with mandatory hooks
│   └── revert.md       # Checkpoint revert with analysis
├── memory/             # constitution.md + tech-specific files
│   ├── MANIFEST.md
│   └── project-status.md  # Implementation progress tracking
├── resources/          # Specifications, designs
├── templates/          # Output templates
└── scripts/            # Project scripts
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

---

## MANDATORY: .gitignore Setup (Step 9)

### Check and Create .gitignore

**IF .gitignore does not exist**, create with speckit-appropriate defaults:

```gitignore
# SpecKit Generator - Default .gitignore
# Created by /speckit.init

# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc
target/

# Build outputs
dist/
build/
*.egg-info/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Environment
.env
.env.local
*.local

# Logs
*.log
logs/

# SpecKit session tracking (local only)
.claude/sessions/
.claude/.cache/
```

**IF .gitignore exists**, check for and append if missing:

```gitignore
# SpecKit additions
.claude/sessions/
.claude/.cache/
```

---

## Idempotency
- Skips existing directories
- Updates changed memory files only
- Preserves project customizations
- Does not overwrite existing .gitignore entries

---

## GATE: Required Before Proceeding

**STOP after initialization. Present results and confirm before proceeding.**

After initialization, you MUST:

1. **Present the created structure** showing:
   - Git status and any warnings
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

### Git Status
- Git version: [VERSION]
- Repository: [Initialized / Already existed]
- .gitignore: [Created / Updated / Already configured]

### Directory Structure Created
.claude/
├── commands/
│   ├── plan.md
│   ├── tasks.md
│   ├── analyze.md
│   ├── clarify.md
│   ├── implement.md
│   └── revert.md
├── memory/
│   └── project-status.md (initialized)
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

### Commands Installed
| Command | Description | Handoffs To |
|---------|-------------|-------------|
| /plan | Create implementation plans | /analyze, /clarify, /tasks |
| /tasks | Generate tasks from plans | /analyze, /implement |
| /analyze | Read-only project audit | /clarify, /plan |
| /clarify | Resolve spec ambiguities | /analyze, /plan |
| /implement | Task execution with checkpoints | /revert, /analyze |
| /revert | Checkpoint revert with analysis | /clarify, /plan, /implement |

### Status Tracking
- project-status.md initialized and ready for /implement updates

### Next Steps
1. Review the memory files for your project needs
2. Add specifications to .claude/resources/
3. Run `/plan` when specs are ready

### Command Flow
```
/plan → /tasks → /implement
   ↓       ↓          ↓
/analyze  /analyze   /revert
   ↓                   ↓
/clarify            /clarify
```

**Is this configuration correct, or would you like to adjust the memory files?**
```
