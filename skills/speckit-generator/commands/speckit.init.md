---
description: "Initialize .claude/ foundation and speckit/ directory with git validation, tech stack detection, memory files, and project commands"
argument-hint: "[--force] [--skip-plugins]"
---

Establish the `.claude/` foundation and `speckit/` directory with appropriate memory files for the project.

## Workflow

1. **Validate git** - Check git is available, initialize repo if needed
2. **Check existing state** - Detect if .claude/ and speckit/ exist
3. **Detect tech stack** - Analyze project for languages/frameworks
4. **Detect plugins** - Check for ralph-loop and other compatible plugins
5. **Present detection** - Show detected stack, plugins, and recommended memory files
6. **Create structure** - Build .claude/ directory structure and speckit/ for specifications
7. **Copy memory files** - Select and copy based on tech stack
8. **Initialize project-status.md** - Create status tracking file
9. **Install project commands** - Copy all 7 commands (plan, tasks, design, analyze, clarify, implement, revert) with customizations based on detected stack and plugins
10. **Ensure .gitignore** - Create or update .gitignore for project safety
11. **Generate project context** - Create project-context.md

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

## Plugin Detection (Step 4)

Detect installed Claude Code plugins that enhance speckit functionality.

### Ralph Loop Detection

Check if the `ralph-loop` plugin is installed and enabled:

```bash
# Check installed_plugins.json for ralph-loop
cat ~/.claude/plugins/installed_plugins.json | grep -q "ralph-loop"
```

**If ralph-loop is detected:**
- Enable autonomous implementation mode in `/implement` command
- Configure completion criteria based on acceptance criteria verification
- Add `--ralph` flag documentation to implement command

### Plugin Detection Output

```markdown
## Plugin Detection

| Plugin | Status | Integration |
|--------|--------|-------------|
| ralph-loop | ✓ Installed | Enables autonomous `/implement --ralph` mode |
| [other plugins] | ✓/✗ | [integration notes] |

### Ralph Loop Integration (if detected)

The `/implement` command will include:
- `--ralph` flag for autonomous execution mode
- Completion criteria: All task acceptance criteria verified
- Safety limit: `--max-iterations 50` (configurable)

**Example usage:**
```
/implement "Phase 1" --ralph --max-iterations 30
```

This will iterate until all Phase 1 tasks have verified acceptance criteria.
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
├── templates/          # Output templates
└── scripts/            # Project scripts

speckit/                # Specification artifacts (at project root)
├── spec.md             # Main specification file
├── plan.md             # Implementation plan
├── *-tasks.md          # Task files by phase/domain
├── plans/              # Domain-specific plans (if complex)
└── designs/            # Detailed task designs
```

## Memory File Selection

**Source Location**: Memory file templates are located in the plugin at:
```
${CLAUDE_PLUGIN_ROOT}/assets/memory/
```

To find this path, the plugin root is typically:
- `~/.claude/plugins/cache/[plugin-id]/` for installed plugins
- The directory containing this command file's parent `.claude-plugin/` folder

| Category | Files | Selection |
|----------|-------|-----------|
| Universal | constitution.md, documentation.md, git-cicd.md, security.md, testing.md | Always |
| TypeScript/JS | typescript.md | If TS/JS detected |
| React/Next.js | react-nextjs.md | If React/Next detected |
| Tailwind | tailwind-shadcn.md | If Tailwind detected |
| Python | python.md | If Python detected |
| Rust | rust.md | If Rust detected |

### Copy Process

1. **Identify plugin root** - Find where speckit-generator plugin is installed
2. **Read source files** - From `${CLAUDE_PLUGIN_ROOT}/assets/memory/[filename].md`
3. **Adapt to project context** - Customize template content for this specific project:
   - Replace placeholder examples with project-specific equivalents
   - Remove sections irrelevant to the detected tech stack
   - Add project-specific conventions if known (from existing code patterns)
   - Ensure file paths, package names, and tool references match the project
4. **Write to project** - To `.claude/memory/[filename].md`
5. **Create MANIFEST.md** - List installed memory files with timestamps

**IMPORTANT**: Memory files should NOT be copied verbatim. Adapt each file's content to reflect the actual project structure, naming conventions, and patterns discovered during tech stack detection.

## Options

```
1. Accept recommended selection
2. Add additional memory files
3. Remove memory files from selection
4. Override detected stack manually
```

---

## MANDATORY: Command Customization (Step 9)

When copying command templates to the user's project, you **MUST** customize them based on the detected tech stack. Command templates contain `<!-- INIT: ... -->` instructions that guide customization.

**Source Location**: Command templates are located in the plugin at:
```
${CLAUDE_PLUGIN_ROOT}/assets/templates/commands/
```

### Customization Process

1. **Read the template** from `${CLAUDE_PLUGIN_ROOT}/assets/templates/commands/[command].md`
2. **Find INIT instructions** in HTML comments (`<!-- INIT: ... -->`)
3. **Apply customizations** based on detected tech stack
4. **Remove all INIT comments** from the final output
5. **Write the customized command** to `.claude/commands/[command].md`

### analyze.md Customization

The `analyze.md` template has a "Memory Directives" section that must be customized:

**Template placeholder:**
```markdown
**Project-specific:**
<!-- INIT: List only the tech-specific files detected for this project -->
- `[DETECTED_TECH_FILE].md` - [Description]
```

**Customized output (example for TypeScript + React):**
```markdown
**Project-specific (detected: TypeScript, React, Next.js):**
- `typescript.md` - TypeScript standards
- `react-nextjs.md` - React/Next.js patterns
- `tailwind-shadcn.md` - Styling standards
```

### Directive File Mapping

| Detected Stack | Directive File | Description |
|----------------|----------------|-------------|
| TypeScript, JavaScript | `typescript.md` | TypeScript/JS standards |
| Python | `python.md` | Python standards |
| Rust | `rust.md` | Rust standards |
| React, Next.js | `react-nextjs.md` | React/Next.js patterns |
| Tailwind CSS | `tailwind-shadcn.md` | Styling standards (personal) |
| Tailwind CSS (L3Harris) | `tailwind-l3harris.md` | Styling standards (L3Harris) |
| CI/CD pipelines | `git-cicd.md` | Git and CI/CD workflows |

### Example: Full analyze.md Customization

**Input (detected: TypeScript, React, Next.js, Tailwind):**

Before:
```markdown
## Memory Directives

<!-- INIT: Replace this section with the actual directive files for this project -->

Load these directive files for compliance checking:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific:**
<!-- INIT: List only the tech-specific files detected for this project -->
- `[DETECTED_TECH_FILE].md` - [Description]

<!-- INIT: Remove all HTML comments from final output -->
```

After:
```markdown
## Memory Directives

Load these directive files for compliance checking:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific (detected: TypeScript, React, Next.js, Tailwind):**
- `typescript.md` - TypeScript standards
- `react-nextjs.md` - React/Next.js patterns
- `tailwind-shadcn.md` - Styling standards
```

### clarify.md Customization

The `clarify.md` template has three sections that must be customized:

**1. Memory Directives Section:**
Same as analyze.md - replace placeholder with detected tech-specific directive files.

**2. SEAMS Lens Activation:**
Enable relevant SEAMS lenses based on project type:

| Project Type | Recommended Lenses |
|--------------|-------------------|
| Web App | Structure, Execution, Stakeholders |
| API/Backend | Interface, Execution, Assumptions |
| Data Pipeline | Data, Traceability, Assumptions |
| CLI Tool | Execution, Assumptions |

**Example for a Web App:**
```markdown
**Active lenses for this project:**
- [x] **Structure**: Boundary clarity, cohesion analysis
- [x] **Execution**: Happy paths, edge cases, failure modes
- [ ] **Assumptions**: Implicit technical/organizational assumptions
- [ ] **Mismatches**: Requirements <-> design gaps
- [x] **Stakeholders**: Operator, security, end-user perspectives
```

**3. Ralph Loop Mode Section:**
Same pattern as implement.md - customize based on ralph-loop plugin detection.

**If ralph-loop IS detected:**
```markdown
## Ralph Loop Mode (Autonomous Clarification)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous clarification:
```
/clarify --ralph                    # Until all CRITICAL/HIGH resolved
/clarify --ralph --confidence 90    # Until 90% coverage confidence
```

### Exit Criteria
- All CRITICAL and HIGH impact ambiguities resolved
- Coverage confidence threshold reached (if specified)
- Hard limit: 10 questions per session
```

**If ralph-loop NOT detected:**
```markdown
## Ralph Loop Mode (Autonomous Clarification)

**Status**: ✗ Disabled (ralph-loop plugin not installed)

To enable autonomous clarification mode, install the ralph-loop plugin:
```
/install-plugin ralph-loop
```
```

---

### plan.md Customization

The `plan.md` template has four sections that must be customized:

**1. Memory Directives Section:**
Same as analyze.md - replace placeholder with detected tech-specific directive files.

**2. PLANS Taxonomy Activation:**
Enable relevant PLANS categories based on project type:

| Project Type | Heavy Categories | Rationale |
|--------------|------------------|-----------|
| Greenfield | ARCHITECTURE | New decisions needed |
| Migration | LINKAGES | Dependencies critical |
| Refactoring | ARCHITECTURE, NOTES | Preserve + improve |
| Feature Addition | SCOPE, NOTES | Fit into existing |

**Example for a Greenfield project:**
```markdown
**Active for this project:**
- [x] **Phases**: Implementation phases, milestones
- [x] **Linkages**: Inter-phase dependencies
- [x] **Architecture**: ADR-based decisions (HEAVY - greenfield project)
- [x] **Notes**: Task generation guidance
- [x] **Scope**: Requirement coverage mapping
```

**3. ADR Template Level:**
Select based on project complexity:

| Level | When to Use | Required Fields |
|-------|-------------|-----------------|
| Lightweight | Simple decisions, single-option obvious | Status, Context, Decision, Consequences |
| Standard | Multiple valid options | All except Confirmation |
| Full | Critical/security decisions | All fields |

**Example customization:**
```markdown
**Selected for this project:** Standard
```

**4. Ralph Loop Mode Section:**
Same pattern as implement.md - customize based on ralph-loop plugin detection.

**If ralph-loop IS detected:**
```markdown
## Ralph Loop Mode (Autonomous Planning)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous plan generation:
```
/plan --ralph                    # Until all ADRs have status: accepted
/plan --ralph --coverage 100     # Until 100% requirement coverage
```

### Exit Criteria
- All PLANS categories at ✓ Complete status
- All ADRs have status: accepted or rejected
- Coverage target reached (if specified)
- Hard limit: 20 iterations
```

**If ralph-loop NOT detected:**
```markdown
## Ralph Loop Mode (Autonomous Planning)

**Status**: ✗ Disabled (ralph-loop plugin not installed)

To enable autonomous planning mode, install the ralph-loop plugin:
```
/install-plugin ralph-loop
```
```

---

### tasks.md Customization

The `tasks.md` template has five sections that must be customized:

**1. Memory Directives Section:**
Same as analyze.md - replace placeholder with detected tech-specific directive files.

**2. SMART Strictness Level:**
Select based on project criticality:

| Level | Behavior | When to Use |
|-------|----------|-------------|
| Strict | Block until criterion rewritten | Critical tasks, security-related |
| Standard | Flag for review, allow with warning | Default for most tasks |
| Relaxed | Log finding only | Exploratory/research tasks |

**Example customization:**
```markdown
**Selected for this project:** Standard
```

**3. Constitution Section Mapping:**
Auto-populate based on detected constitution.md sections:

| Task Type | Constitution Sections |
|-----------|----------------------|
| Setup/Init | §3 (Structure), §7 (Security) |
| API/Backend | §4 (Error Handling), §5 (Performance) |
| UI/Frontend | §6 (Accessibility), §8 (UX) |
| Testing | §9 (Testing), §10 (Quality) |
| Documentation | §11 (Documentation) |

Read the actual constitution.md and map section numbers appropriately.

**4. Task Template Level:**
Select based on project complexity:

| Level | Fields Included | When to Use |
|-------|-----------------|-------------|
| Lightweight | Status, Priority, Description, Criteria | Small projects, quick iterations |
| Standard | + Phase, Group, Plan Reference, Dependencies | Default for most projects |
| Detailed | + Constitution Sections, Memory Files, SMART validation | Complex/regulated projects |

**Example customization:**
```markdown
**Selected for this project:** Standard
```

**5. Ralph Loop Mode Section:**
Same pattern as implement.md - customize based on ralph-loop plugin detection.

**If ralph-loop IS detected:**
```markdown
## Ralph Loop Mode (Autonomous Task Generation)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous task refinement:
```
/tasks --ralph                    # Until 100% SMART compliance
/tasks --ralph --smart-level strict   # Strict SMART validation
```

### Exit Criteria
- All tasks have SMART-compliant acceptance criteria
- 8-point validation passes
- No blocking issues remain
- Hard limit: 15 iterations
```

**If ralph-loop NOT detected:**
```markdown
## Ralph Loop Mode (Autonomous Task Generation)

**Status**: ✗ Disabled (ralph-loop plugin not installed)

To enable autonomous task generation mode, install the ralph-loop plugin:
```
/install-plugin ralph-loop
```
```

---

### implement.md Customization (Ralph Loop Integration)

The `implement.md` template has a "Ralph Loop Mode" section that must be customized based on plugin detection.

**If ralph-loop plugin IS detected:**

Include the full Ralph Loop Mode section with enabled functionality:

```markdown
## Ralph Loop Mode (Autonomous Execution)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous implementation that iterates until all acceptance criteria are verified:

```
/implement "Phase 1" --ralph
/implement TASK-001..TASK-010 --ralph --max-iterations 30
```

### How It Works

1. Wraps implementation in a ralph-loop
2. Completion promise: `<promise>ALL_CRITERIA_VERIFIED</promise>`
3. Iterates until ALL acceptance criteria for selected tasks are `[x]` checked
4. Safety limit: 50 iterations (override with `--max-iterations`)

### Exit Criteria

The loop exits ONLY when:
- Every selected task has status: COMPLETED
- Every acceptance criterion is marked `[x]` with verification evidence
- No criteria remain `[ ]` or FAILED

### Example

```
/implement "Phase 1" --ralph --max-iterations 30
```

Claude will:
1. Execute Phase 1 tasks
2. Verify each acceptance criterion
3. If any fail, iterate and fix
4. Output `<promise>ALL_CRITERIA_VERIFIED</promise>` when done
```

**If ralph-loop plugin is NOT detected:**

Include a disabled notice:

```markdown
## Ralph Loop Mode (Autonomous Execution)

**Status**: ✗ Disabled (ralph-loop plugin not installed)

To enable autonomous implementation mode, install the ralph-loop plugin:
```
/install-plugin ralph-loop
```

Then re-run `/speckit.init` to update this command.
```

---

## MANDATORY: .gitignore Setup (Step 10)

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
│   ├── design.md
│   ├── analyze.md
│   ├── clarify.md
│   ├── implement.md
│   └── revert.md
├── memory/
│   └── project-status.md (initialized)
├── templates/
└── scripts/

speckit/              # Ready for specification artifacts
├── spec.md           # (place your spec here)
├── plan.md           # (generated by /plan)
└── *-tasks.md        # (generated by /tasks)

### Detected Tech Stack
- [Languages detected]
- [Frameworks detected]

### Plugin Integrations
| Plugin | Status | Integration |
|--------|--------|-------------|
| ralph-loop | [✓ Installed / ✗ Not found] | [Autonomous /implement --ralph mode / Not available] |

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
| /tasks | Generate tasks from plans | /analyze, /design, /implement |
| /design | Generate detailed task designs | /implement, /analyze |
| /analyze | Read-only project audit | /clarify, /plan |
| /clarify | Resolve spec ambiguities | /analyze, /plan |
| /implement | Task execution with checkpoints | /revert, /analyze, /design |
| /revert | Checkpoint revert with analysis | /clarify, /plan, /implement |

### Status Tracking
- project-status.md initialized and ready for /implement updates

### Next Steps
1. Review the memory files for your project needs
2. Add specifications to speckit/
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
