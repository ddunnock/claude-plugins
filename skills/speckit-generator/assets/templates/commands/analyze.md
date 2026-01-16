---
description: "Perform a non-destructive cross-artifact consistency and quality analysis"
handoffs:
  - label: Clarify Issues
    agent: clarify
    prompt: Resolve ambiguities found in analysis
  - label: Update Plan
    agent: plan
    prompt: Revise plan to address gaps
---

<!--
================================================================================
INIT AGENT INSTRUCTIONS
================================================================================
When copying this template to the user's project, you MUST customize the
"Memory Directives" section below based on the detected tech stack.

REPLACE the placeholder section with the actual directive files for this project.

Example for a TypeScript + React + Next.js project:
```markdown
## Memory Directives

Load these directive files for compliance checking:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific (detected: TypeScript, React, Next.js):**
- `typescript.md` - TypeScript standards
- `react-nextjs.md` - React/Next.js patterns
- `tailwind-shadcn.md` - Styling standards
```

Example for a Python + Rust project:
```markdown
## Memory Directives

Load these directive files for compliance checking:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements
- `testing.md` - Test coverage requirements
- `documentation.md` - Documentation standards

**Project-specific (detected: Python, Rust):**
- `python.md` - Python standards
- `rust.md` - Rust standards
```

REMOVE these instruction comments from the final output.
================================================================================
-->

# Analyze

Perform a non-destructive cross-artifact consistency and quality analysis across `spec.md`, `plan.md`, and `tasks.md` before implementation.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts before implementation. This is a **pre-implementation quality gate**.

---

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report.

**Directive Authority**: The project directives in `/memory/` are **non-negotiable**. Directive conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks.

---

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

---

## Artifacts to Analyze

| Artifact | Source |
|----------|--------|
| spec.md | `.claude/resources/features/[feature]/spec.md` |
| plan.md | `.claude/resources/features/[feature]/plan.md` |
| tasks.md | `.claude/resources/features/[feature]/tasks.md` |

---

## Detection Passes

### A. Duplication Detection
- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

### B. Ambiguity Detection
- Flag vague adjectives (fast, scalable, secure) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`)

### C. Underspecification
- Requirements with verbs but missing measurable outcome
- User stories missing acceptance criteria
- Tasks referencing undefined components

### D. Directive Alignment (Agent)

**Invoke compliance-checker agent:**
```
subagent_type: "speckit-generator:compliance-checker"
prompt: "Check compliance of .claude/resources/*.md against .claude/memory/constitution.md and all tech-specific memory files"
```

The agent checks:
- Any element conflicting with MUST/MUST NOT from loaded directives
- Missing mandated quality gates (test coverage, documentation)
- Security violations, language-specific violations

### E. Coverage Gaps (Agent)

**Invoke coverage-mapper agent:**
```
subagent_type: "speckit-generator:coverage-mapper"
prompt: "Map coverage between .claude/resources/spec.md, .claude/resources/plan.md, and .claude/resources/*-tasks.md"
```

The agent identifies:
- Requirements with zero associated tasks
- Tasks with no mapped requirement
- Non-functional requirements not reflected in tasks

### F. Inconsistency
- Terminology drift across files
- Data entities in plan but absent in spec
- Task ordering contradictions
- Conflicting technology choices

---

## Severity Assignment

| Level | Criteria |
|-------|----------|
| CRITICAL | Violates MUST/MUST NOT directive, blocks baseline functionality |
| HIGH | Duplicate/conflicting requirement, security/performance ambiguity |
| MEDIUM | Terminology drift, SHOULD violations, underspecified edge cases |
| LOW | Style improvements, minor redundancy |

---

## Output Format

### Findings Table

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|

### Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

### Directive Alignment

**Directives Loaded:**
- [List all loaded directive files with ✓]

**Violations:** (if any, grouped by source file)

### Metrics

- Total Requirements
- Total Tasks
- Coverage %
- Critical Issues Count

---

## Next Actions

- If CRITICAL issues: Recommend resolving before `/implement`
- If only MEDIUM/LOW: User may proceed with suggestions
- Provide command suggestions: `/clarify`, `/plan`, `/tasks`

---

## Remediation Offer

Ask: "Would you like me to suggest concrete remediation edits for the top N issues?"

*(Read-only analysis. No changes without explicit approval.)*

---

## Handoffs

### Clarify Issues
Resolve ambiguities and unclear items found in analysis.
Use: `/clarify`

### Update Plan
Revise the plan to address gaps or inconsistencies.
Use: `/plan`
