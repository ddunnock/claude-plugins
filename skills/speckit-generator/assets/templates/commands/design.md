---
description: "Generate detailed implementation designs for specific tasks"
handoffs:
  - label: Implement Task
    agent: implement
    prompt: Implement the designed task
  - label: View All Tasks
    agent: tasks
    prompt: Show task summary
---

# Design

Generate detailed implementation designs with algorithms, method signatures, and test cases for specific tasks.

## User Input

```text
$ARGUMENTS
```

You **MUST** parse the TASK-ID from arguments before proceeding. If no TASK-ID provided, show available tasks and prompt for selection.

---

## Usage

```
/design TASK-007           # Design specific task
/design TASK-003,TASK-004  # Design multiple tasks
/design --list             # List tasks available for design
/design --show TASK-007    # Show existing design without regenerating
```

---

## Memory Directives

<!-- INIT: Replace this section with the actual directive files for this project -->

Load these directive files for design generation:

**Always loaded:**
- `constitution.md` - Core principles, design patterns
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific:**
<!-- INIT: List only the tech-specific files detected for this project -->
- `[DETECTED_TECH_FILE].md` - [Description]

<!-- INIT: Remove all HTML comments from final output -->

---

## Tech Stack Detection

<!-- INIT: Set detected tech stack for designer agent selection -->

The `/design` command detects the project's tech stack from MANIFEST.md to invoke the appropriate designer agent:

| Tech Stack | Agent | Specialization |
|------------|-------|----------------|
| Python | `python-designer` | Pydantic models, async patterns, type hints |
| TypeScript | `typescript-designer` | Type definitions, Zod schemas, async/await |
| React/Next.js | `react-designer` | Component patterns, hooks, server actions |
| Rust | `rust-designer` | Ownership patterns, error handling, traits |
| Generic | `design-agent` | Language-agnostic algorithm design |

**Detected for this project:** <!-- INIT: Python | TypeScript | React | Rust | Generic --> Generic

---

## Workflow

### Phase 1: Task Loading

1. **Parse TASK-ID** from arguments
2. **Load task** from `speckit/*-tasks.md`
3. **Extract context**:
   - Task description and acceptance criteria
   - Plan reference (Phase, ADR)
   - Constitution sections referenced
   - Memory file references
   - Dependencies (other tasks)

### Phase 2: Context Gathering

1. **Load plan.md** - Extract ADR and phase context for the task
2. **Load spec.md** - Extract related requirements
3. **Load memory files** - Get tech-specific patterns and constraints
4. **Analyze existing code** - Find related patterns in codebase (if code exists)

### Phase 3: Designer Agent Selection

Based on detected tech stack, select the appropriate designer agent:

```
Read MANIFEST.md → Extract "Tech Stack" field → Select agent
```

**Agent Selection Logic:**
- If Python detected → `python-designer`
- If TypeScript/JavaScript detected → `typescript-designer`
- If React/Next.js detected → `react-designer`
- If Rust detected → `rust-designer`
- Otherwise → `design-agent` (generic)

### Phase 4: Design Generation (Agent Invocation)

**Invoke via Task tool:**
```
subagent_type: "speckit-generator:[selected-designer]"
prompt: |
  Generate detailed implementation design for [TASK-ID].

  Task: [task description]
  Acceptance Criteria: [criteria list]
  Plan Reference: [phase/ADR]
  Constitution Sections: [sections]
  Memory Files: [relevant directives]
  Dependencies: [dependent tasks]

  Existing code patterns to follow: [patterns found in codebase]
```

The agent will generate:
- Data models and type definitions
- Method signatures with full type annotations
- Algorithm pseudo-code
- Test cases with expected behavior
- Edge cases and error handling
- Implementation notes

### Phase 5: Output Generation

1. **Create design file** at `speckit/designs/design-[TASK-ID].md`
2. **Update design index** if multiple designs exist
3. **Log design creation** for traceability

---

## Design Output Format

```markdown
# Design: [TASK-ID] [Task Title]

## Summary
[One-paragraph summary of what this design covers]

## Dependencies
- [TASK-XXX]: [Brief description] (must be complete)
- [TASK-YYY]: [Brief description] (can proceed in parallel)

## Plan Context
**Phase**: [Phase N: Phase Name]
**ADR**: [ADR-XXX: Decision Title]
**Requirements**: [REQ-XXX, REQ-YYY]

## Data Models

```[language]
[Full data model definitions with field types and validation]
```

## Interface

```[language]
[Method/function signatures with full type annotations]
```

## Algorithm

```[language]
[Detailed pseudo-code or implementation skeleton]
[Annotated with comments explaining key decisions]
```

## Test Cases

```[language]
[Test functions covering:
 - Happy path
 - Edge cases
 - Error conditions]
```

## Edge Cases

| Case | Input | Expected Behavior |
|------|-------|-------------------|
| [case name] | [input description] | [expected output/behavior] |

## Error Handling

| Error Condition | Response | Recovery |
|-----------------|----------|----------|
| [condition] | [error type/message] | [recovery action] |

## Implementation Notes

- [Key implementation detail 1]
- [Key implementation detail 2]
- [Library/dependency notes]

## Verification Commands

```bash
[Commands to verify implementation correctness]
```
```

---

## Output Location

| Output | Location |
|--------|----------|
| Design file | `speckit/designs/design-[TASK-ID].md` |
| Design index | `speckit/designs/index.md` |

---

## Validation Checklist

Before completing design generation, verify:

| # | Check | Status |
|---|-------|--------|
| 1 | Task ID exists in *-tasks.md | [ ] |
| 2 | All acceptance criteria addressed in design | [ ] |
| 3 | Data models include all required fields | [ ] |
| 4 | Method signatures have full type annotations | [ ] |
| 5 | Algorithm covers happy path and edge cases | [ ] |
| 6 | Test cases cover acceptance criteria | [ ] |
| 7 | Error handling defined | [ ] |
| 8 | Constitution directives respected | [ ] |

---

## GATE: Required Before Proceeding

**STOP after design generation. Present design for review before implementation.**

After generating design, you MUST:

1. **Present a design summary** showing:
   - Task being designed
   - Key data models created
   - Methods/functions defined
   - Number of test cases
   - Edge cases covered

2. **Highlight design decisions**:
   - Trade-offs considered
   - Alternatives rejected
   - Assumptions made

3. **Wait for explicit user approval** before implementation

### Gate Response Template

```markdown
## Design Complete: [TASK-ID]

### Overview
Designed implementation for: [Task Title]
Design file: `speckit/designs/design-[TASK-ID].md`

### Data Models
- `[ModelName]`: [purpose]
- `[ModelName]`: [purpose]

### Methods/Functions
| Name | Purpose |
|------|---------|
| `function_name()` | [what it does] |

### Test Coverage
- [N] test cases covering:
  - Happy path: [count]
  - Edge cases: [count]
  - Error handling: [count]

### Design Decisions
| Decision | Rationale |
|----------|-----------|
| [choice made] | [why] |

### Assumptions
- [assumption 1]
- [assumption 2]

### Validation Checklist
- [x] Task exists and criteria addressed
- [x] Data models complete
- [x] Method signatures typed
- [x] Algorithm covers all cases
- [x] Tests cover criteria
- [x] Error handling defined
- [x] Constitution compliant

**Awaiting your approval before implementation.**

### Next Steps
1. Review the full design in `speckit/designs/design-[TASK-ID].md`
2. Provide feedback or request changes
3. Approve to proceed with `/implement TASK-ID`
```

---

## Multi-Task Design

When designing multiple tasks (`/design TASK-003,TASK-004`):

1. **Check dependencies** - Design dependent tasks first
2. **Share context** - Pass shared data models between designs
3. **Create separate files** - One design file per task
4. **Update index** - Add all designs to index.md

---

## Design Refresh

To regenerate an existing design:

```
/design TASK-007 --refresh
```

This will:
1. Archive existing design to `speckit/designs/archive/`
2. Re-read current task definition (may have changed)
3. Generate fresh design

---

## Integration with /implement

The `/implement` command checks for design files:

1. If `design-[TASK-ID].md` exists → Use as implementation guide
2. If no design exists → Prompt to run `/design [TASK-ID]` first
3. Implementation verifies against design's test cases

---

## Handoffs

### Implement Task
After design is approved, implement the task using the design as a guide.

Use: `/implement [TASK-ID]`

### View All Tasks
See all tasks and their design status.

Use: `/tasks --status`
