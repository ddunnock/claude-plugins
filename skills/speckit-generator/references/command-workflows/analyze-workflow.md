# Analyze Workflow Reference

Detailed workflow for the `/speckit.analyze` command.

## Purpose

Perform a non-destructive cross-artifact consistency and quality analysis across `spec.md`, `plan.md`, and `tasks.md` before implementation. This is a **pre-implementation quality gate** that verifies your planning artifacts are internally consistent and compliant with project directives.

## Key Characteristics

- **Read-only**: Never modifies any files
- **Deterministic**: Identical inputs produce identical outputs
- **Stable Finding IDs**: IDs remain consistent across runs
- **Directive-aware**: Validates against constitution and all applicable memory files

---

## Prerequisites

This command requires all three core artifacts to exist:

1. `spec.md` - Created by `/speckit.clarify`
2. `plan.md` - Created by `/speckit.plan`
3. `tasks.md` - Created by `/speckit.tasks`

If any are missing, the command will abort with instructions to run the prerequisite command.

---

## Workflow Steps

### Step 1: Initialize Analysis Context

Run the prerequisite check script and parse JSON output:

```json
{
  "FEATURE_DIR": "speckit",
  "AVAILABLE_DOCS": ["spec.md", "plan.md", "tasks.md"]
}
```

Derive absolute paths:
- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

### Step 2: Load Directive Files

> **Architecture Note**: The `/speckit.init` command customizes the `analyze.md` command
> during installation with the specific directive files for the project's tech stack.
> The installed command will have an explicit list of directives to load, not conditional
> logic. This makes the analyze command deterministic and explicit.

**Always loaded (cross-cutting concerns):**

| File | Purpose |
|------|---------|
| `constitution.md` | Global principles, quality gates, RFC 2119 normative language |
| `security.md` | Input validation, secrets management, dependency security |
| `testing.md` | Coverage thresholds, test patterns, E2E requirements |
| `documentation.md` | Diátaxis framework, required documentation |

**Tech-specific (determined at init time):**

| Detected Stack | Directive File |
|----------------|----------------|
| TypeScript/JavaScript | `typescript.md` |
| Python | `python.md` |
| Rust | `rust.md` |
| React/Next.js | `react-nextjs.md` |
| Tailwind (personal) | `tailwind-shadcn.md` |
| Tailwind (L3Harris) | `tailwind-l3harris.md` |
| CI/CD pipelines | `git-cicd.md` |

**Example installed command (TypeScript + React project):**
```markdown
## Memory Directives

**Always loaded:**
- constitution.md, security.md, testing.md, documentation.md

**Project-specific (detected: TypeScript, React, Next.js):**
- typescript.md
- react-nextjs.md
- tailwind-shadcn.md
```

### Step 3: Build Semantic Models

Create internal representations for analysis:

**Requirements Inventory:**
```
user-can-upload-file → { source: "spec.md:L45", type: "functional" }
api-response-under-500ms → { source: "spec.md:L78", type: "non-functional" }
```

**Task Coverage Mapping:**
```
TASK-001 → [user-can-upload-file]
TASK-002 → [api-response-under-500ms, user-can-upload-file]
TASK-003 → [] ← ORPHAN
```

**Directive Rule Set:**
```
constitution.md:
  - MUST: Test coverage ≥80% line, ≥75% branch
  - MUST: All public APIs documented

security.md:
  - MUST NOT: Secrets in code
  - MUST: Parameterized SQL queries

typescript.md:
  - MUST: strict mode enabled
  - SHOULD: JSDoc on public functions
```

### Step 4: Run Detection Passes

#### Pass A: Duplication Detection

Identify semantically similar requirements:

| Check | Example |
|-------|---------|
| Near-duplicate functional requirements | "User can upload file" vs "User uploads files" |
| Redundant non-functional requirements | Same performance target stated twice |

#### Pass B: Ambiguity Detection

| Pattern | Severity |
|---------|----------|
| Vague adjectives without metrics | "fast", "scalable", "intuitive" |
| Unresolved placeholders | `TODO`, `TKTK`, `???`, `<placeholder>` |
| `[TBD]`, `[NEEDS CLARIFICATION]` markers | HIGH |

#### Pass C: Underspecification

| Check | Severity |
|-------|----------|
| Requirements with verbs but no measurable outcome | MEDIUM |
| User stories missing acceptance criteria | HIGH |
| Tasks referencing undefined components | HIGH |

#### Pass D: Directive Alignment

| Check | Source | Severity |
|-------|--------|----------|
| Test coverage not specified | testing.md | CRITICAL |
| Missing input validation tasks | security.md | CRITICAL |
| No JSDoc requirement for public APIs | typescript.md | MEDIUM |
| Missing required documentation | documentation.md | HIGH |

#### Pass E: Coverage Gaps

| Check | Severity |
|-------|----------|
| Requirements with zero tasks | CRITICAL (if core) / HIGH |
| Tasks with no mapped requirement | MEDIUM |
| Non-functional requirements not in tasks | HIGH |

#### Pass F: Inconsistency

| Check | Severity |
|-------|----------|
| Terminology drift across files | MEDIUM |
| Data entities in plan but not spec | HIGH |
| Task ordering contradictions | HIGH |
| Conflicting technology choices | CRITICAL |

### Step 5: Generate Stable Finding IDs

Finding IDs are deterministic based on:
```
FINDING_ID = CategoryPrefix + hash(location + description_normalized)
```

Prefixes:
- `A` - Duplication
- `B` - Ambiguity
- `C` - Underspecification
- `D` - Directive Alignment
- `E` - Coverage Gap
- `F` - Inconsistency

Example: `D-a1b2c3` (Directive alignment issue)

### Step 6: Assign Severity

| Level | Criteria |
|-------|----------|
| CRITICAL | Violates MUST/MUST NOT directive, blocks baseline functionality |
| HIGH | Duplicate/conflicting requirement, security/performance ambiguity |
| MEDIUM | Terminology drift, SHOULD violations, underspecified edge cases |
| LOW | Style improvements, minor redundancy |

---

## Output Format

### Findings Table

```markdown
| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| D-a1b2 | Directive | CRITICAL | plan.md:L45 | No test coverage task; violates testing.md §2.1 | Add task for test infrastructure |
| E-b2c3 | Coverage | HIGH | spec.md:L23 | REQ "user-can-export-data" has no tasks | Generate tasks or mark as deferred |
| B-c3d4 | Ambiguity | MEDIUM | spec.md:L67 | "fast response" lacks metric | Define threshold (e.g., <200ms P95) |
```

### Coverage Summary

```markdown
| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| user-can-upload-file | ✓ | T-001, T-003 | |
| api-response-under-500ms | ✓ | T-002 | |
| user-can-export-data | ✗ | — | Missing coverage |
```

### Directives Loaded

```markdown
- constitution.md ✓
- security.md ✓
- testing.md ✓
- documentation.md ✓
- typescript.md ✓ (detected: TypeScript)
- react-nextjs.md ✓ (detected: Next.js)
- python.md ✗ (not applicable)
- rust.md ✗ (not applicable)
```

### Metrics

```markdown
- Total Requirements: 15
- Total Tasks: 28
- Coverage: 93% (14/15 requirements have tasks)
- Ambiguity Count: 3
- Duplication Count: 1
- Critical Issues: 2
```

---

## Next Actions Logic

**If CRITICAL issues exist:**
```
⚠️ CRITICAL issues found. Resolve before running /speckit.implement:
1. D-a1b2: Add test coverage task (violates testing.md)
2. F-d4e5: Resolve technology conflict (Next.js vs Vue)
```

**If only MEDIUM/LOW:**
```
✓ No blocking issues. You may proceed with /speckit.implement.

Suggested improvements:
- B-c3d4: Consider adding metric for "fast response"
- C-e5f6: Clarify edge case handling for empty uploads
```

---

## Integration Points

### With /speckit.clarify

Ambiguity findings can trigger clarification:
```
3 ambiguities found. Consider running /speckit.clarify to resolve.
```

### With /speckit.plan

Inconsistency findings may require plan updates:
```
Technology conflict detected. Update plan.md to resolve.
```

### With /speckit.tasks

Coverage gaps inform task generation:
```
2 requirements have no tasks. Run /speckit.tasks to generate coverage.
```

### With /speckit.implement

Analysis gates implementation:
```
CRITICAL issues block /speckit.implement. Resolve first.
```

---

## Determinism Requirements

For identical inputs, output must be identical:

1. **Sort order**: Findings sorted by severity (CRITICAL→LOW), then category, then ID
2. **File scanning**: Consistent file order (alphabetical)
3. **ID generation**: Hash-based, not sequence-based
4. **Directive loading**: Same stack detection = same directives loaded

---

## Command Options

```bash
# Full analysis
/speckit.analyze

# Filter by category
/speckit.analyze --category directive
/speckit.analyze --category coverage

# Verbose output (include LOW findings)
/speckit.analyze --verbose

# Show only CRITICAL/HIGH
/speckit.analyze --severity high
```

---

## Continuation Format

After command completion, always present the next logical step using this standardized format:

```markdown
## ▶ Next Up
**{command}: {name}** — {one-line description}
`/{command}`
<sub>`/clear` first → fresh context window</sub>
```

### Next Step Logic for /analyze

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| No blocking issues | `/implement` | Proceed with implementation |
| CRITICAL issues found | Fix issues, re-run `/analyze` | Resolve blockers first |
| Ambiguities detected | `/clarify` | Resolve spec ambiguities |
| Coverage gaps | `/tasks` | Generate missing tasks |

### Example Output

```markdown
## ▶ Next Up
**implement: Start Phase 1** — Execute tasks with verification and compliance checks
`/implement "Phase 1"`
<sub>`/clear` first → fresh context window</sub>
```
