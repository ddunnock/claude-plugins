# Command Patterns Reference

## Contents
- Required structure
- Pattern 1: Generator commands
- Pattern 2: Analyzer commands
- Pattern 3: Orchestrator commands
- Pattern 4: Decision commands
- Script integration
- Error handling

## Required Structure

### YAML Frontmatter

```yaml
---
description: Clear description of what command does (used for discovery)
handoffs:
  - label: Display Label
    agent: target-command-name
    prompt: Context for target
    send: true  # Optional: auto-execute
---
```

### User Input Section

```markdown
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. The user input may specify:
- Mode selection (e.g., "generate" or "validate")
- Specific targets or options
- Flags like `--force` or `--dry-run`
```

### Core Sections

```markdown
## Purpose

[1-2 paragraphs: what problem this solves, when to use it]

## Workflow

1. **Step Name**: Description
   - Sub-step details
   - Decision points: **If X** → do Y, **else** → do Z

## Completion Criteria

- [ ] Checkable success condition
```

## Pattern 1: Generator Commands

Creates new files or content.

```markdown
---
description: Generate project configuration from template
handoffs:
  - label: Validate Config
    agent: project.validate
    prompt: Validate the generated configuration
---

## User Input

```text
$ARGUMENTS
```

Parse for: project name, template type, options

## Purpose

Generate standardized project configuration files following team conventions.

## Workflow

1. **Check Prerequisites**
   - Run `.claude/scripts/bash/check-prereqs.sh --json`
   - **If missing dependencies**: Report and halt
   
2. **Gather Information**
   - Parse $ARGUMENTS for project name
   - **If not provided**: Ask user
   
3. **Generate Files**
   - Run `.claude/scripts/bash/generate-config.sh --project "$NAME" --json`
   - Report created files

4. **Validate Output**
   - Run `.claude/scripts/bash/validate-config.sh --json`
   - **If errors**: Fix and re-validate

## Output Format

Use template at `.claude/templates/config-summary.md`

## Completion Criteria

- [ ] All required files created
- [ ] Validation passes
- [ ] Summary generated
```

## Pattern 2: Analyzer Commands

Examines codebase and reports findings.

```markdown
---
description: Analyze codebase for security vulnerabilities
handoffs:
  - label: Fix Issues
    agent: security.remediate
    prompt: Address security issues found in analysis
---

## User Input

```text
$ARGUMENTS
```

Parse for: target directory, severity filter, output format

## Purpose

Scan codebase for common security vulnerabilities and report findings with remediation guidance.

## Workflow

1. **Determine Scope**
   - Parse target from $ARGUMENTS or default to current directory
   - Identify file types to scan
   
2. **Run Analysis**
   - Run `.claude/scripts/bash/security-scan.sh --target "$TARGET" --json`
   - Parse findings by severity
   
3. **Categorize Results**
   - **Critical/High**: Blockers requiring immediate action
   - **Medium**: Should fix before release
   - **Low**: Advisory for future improvement

4. **Generate Report**
   - Use template `.claude/templates/security-report.md`
   - Include remediation steps for each finding

## Completion Criteria

- [ ] All target files scanned
- [ ] Findings categorized by severity
- [ ] Report generated with remediation steps
```

## Pattern 3: Orchestrator Commands

Coordinates multi-phase execution with checkpoints.

```markdown
---
description: Execute implementation tasks with progress tracking
handoffs:
  - label: Continue
    agent: project.implement
    prompt: Resume from last checkpoint
---

## User Input

```text
$ARGUMENTS
```

Options:
- `--continue`: Resume from last task
- `--skip [ID]`: Skip task and continue
- `[TASK_ID]`: Execute specific task

## Purpose

Systematically execute implementation tasks with progress tracking and rollback capability.

## Workflow

1. **Load State**
   - Read `.claude/memory/implementation-status.md`
   - Determine current phase and next task
   
2. **Validate Prerequisites**
   - Check dependencies for next task
   - **If blocked**: Report blocker and halt
   
3. **Execute Task**
   - Run task-specific script
   - Validate output
   - **If failed**: Log error, offer retry/skip
   
4. **Update State**
   - Update status file with completion
   - Record any decisions made
   
5. **Check Phase Completion**
   - **If phase complete**: Run phase validation
   - **If more tasks**: Continue or pause for user

## State File

Progress in `.claude/memory/implementation-status.md`:

| Task | Phase | Status | Completed |
|------|-------|--------|-----------|
| T001 | 1 | ✓ Complete | 2025-01-15 |
| T002 | 1 | → Current | - |

## Completion Criteria

- [ ] Current task executed successfully
- [ ] Status file updated
- [ ] Phase validation passed (if applicable)
```

## Pattern 4: Decision Commands

Guides user through choices with branching logic.

```markdown
---
description: Initialize project with appropriate configuration
handoffs:
  - label: Create Specs
    agent: project.specify
    prompt: Create specifications for chosen architecture
---

## User Input

```text
$ARGUMENTS
```

May include: project type hint, constraints

## Purpose

Guide project initialization decisions and generate appropriate configuration.

## Decision Tree

```
1. Project Type?
   ├── Library → Use library template
   ├── Application → Use app template  
   └── Monorepo → Use monorepo template

2. Language?
   ├── Python → pyproject.toml
   ├── TypeScript → tsconfig.json + package.json
   └── Rust → Cargo.toml

3. Quality Level?
   ├── Minimal → Basic linting
   ├── Standard → Linting + testing
   └── Strict → Full CI/CD
```

## Workflow

1. **Detect Context**
   - Check existing files for hints
   - Parse $ARGUMENTS for explicit choices
   
2. **Gather Decisions**
   - For each decision point without clear answer: ask user
   - Record choices in `.claude/memory/decisions.md`
   
3. **Apply Configuration**
   - Run appropriate setup script based on decisions
   - Generate configuration files

## Completion Criteria

- [ ] All decisions recorded
- [ ] Configuration generated
- [ ] Next steps documented
```

## Script Integration

Reference scripts consistently:

```markdown
Run `.claude/scripts/bash/script-name.sh --json` from project root.

Parse JSON response:
```json
{
  "status": "success|error",
  "data": { ... },
  "errors": [ ... ]
}
```

**If status is error**: [describe handling]
```

## Error Handling

Document failure modes:

```markdown
## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| "File not found" | Missing dependency | Run setup first |
| "Validation failed" | Invalid input | Check format |
| "Permission denied" | Access issue | Check permissions |
```
