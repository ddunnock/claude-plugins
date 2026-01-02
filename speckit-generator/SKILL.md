---
name: speckit-generator
description: Transform requirements documents into complete Claude Code automation packages with commands, scripts, and templates. Use when the user provides requirements (formal SRS, informal notes, or verbal description), wants to create automation infrastructure, needs Claude Code /commands for a project, or mentions SpecKit, project automation, or requirements-to-automation workflows. Includes competitor analysis, assumption tracking, and validation loops.
---

# SpecKit Generator

Transform requirements into complete Claude Code automation infrastructure using the INCOSE-aligned, 5-phase methodology.

## Overview

This skill converts raw requirements into production-ready automation packages containing:
- Claude Code `/commands` organized by lifecycle phase
- Supporting scripts with `--json` output
- Structured templates for deliverables
- Memory files for persistent project state
- Validation and verification infrastructure

## Quick Start Workflow

```
Task Progress:
- [ ] Phase 1: Requirements Elicitation
- [ ] Phase 2: Command Architecture Design
- [ ] Phase 3: Infrastructure Design
- [ ] Phase 4: Implementation
- [ ] Phase 5: Validation & Packaging
```

## Phase 1: Requirements Elicitation

### 1.1 Input Classification

Determine input type and apply appropriate elicitation strategy:

| Input Type | Strategy |
|------------|----------|
| Formal SRS/Requirements Doc | Extract directly, clarify ambiguities |
| Informal Notes/Description | Structured elicitation interview |
| Verbal/Conceptual | Goal decomposition with examples |
| Existing Codebase | Analysis + gap identification |

### 1.2 Elicitation Questions

Ask these questions to establish project scope (2-3 per message max):

**Project Identity:**
- What is the project name and primary domain?
- Who are the key stakeholders (developers, reviewers, end users)?
- What lifecycle gates exist (SRR, PDR, CDR, or equivalent)?

**Deliverable Inventory:**
- What engineering artifacts does this project produce?
- Which deliverables are highest value for automation?
- What review/approval processes exist?

**Technical Context:**
- What programming languages/frameworks are used?
- Are there existing templates or standards to follow?
- What tools/integrations are required?

### 1.3 Competitor Analysis

Before designing, search for existing solutions. Run the competitor analysis script:

```bash
python scripts/competitor_analysis.py "<project-domain>" --output-format json
```

**Manual Search Strategy:**

1. Search web for: `"<domain>" automation tools`, `"<domain>" CLI`, `"<domain>" SDK`
2. Check GitHub for: similar projects, established patterns
3. Document findings with sources for traceability

Mark all competitive analysis with evidence sources:
- `[VERIFIED: <url>]` - Confirmed from source
- `[ASSUMPTION]` - Reasonable inference, needs validation

### 1.4 Requirements Capture Template

For each automation requirement, complete:

```markdown
## AR-### [Deliverable Name]

**Stakeholder Need**: [What problem does this solve?]

**Inputs**:
- [ ] [Input 1] - Source: [where it comes from]

**Outputs**:
- [ ] [Output 1] - Format: [format/template]

**Quality Criteria**:
- [ ] [Criterion 1]

**Frequency**: [One-time / Periodic / Event-driven]

**Automation Pattern**:
- [ ] Generator (creates structured documents)
- [ ] Analyzer (examines codebase/artifacts)
- [ ] Orchestrator (multi-phase execution)
- [ ] Decision (guides choices with criteria)

**Evidence Grounding**:
- [VERIFIED/ASSUMPTION]: [basis for requirement]
```

## Phase 2: Command Architecture Design

### 2.1 Command Taxonomy

Organize by lifecycle phase, not technical function:

```
.claude/commands/
├── requirements/
│   ├── requirements.capture.md
│   ├── requirements.trace.md
│   └── requirements.baseline.md
├── architecture/
│   ├── architecture.analyze.md
│   ├── architecture.design.md
│   └── architecture.review.md
├── trades/
│   ├── trades.initiate.md
│   ├── trades.evaluate.md
│   └── trades.document.md
├── risk/
│   ├── risk.identify.md
│   ├── risk.assess.md
│   └── risk.mitigate.md
├── test/
│   ├── test.plan.md
│   ├── test.procedure.md
│   └── test.report.md
└── review/
    ├── review.prepare.md
    └── review.disposition.md
```

### 2.2 Pattern Selection Matrix

| Deliverable Characteristic | Pattern | Command Structure |
|---------------------------|---------|-------------------|
| Creates structured documents from inputs | Generator | Single command, template-driven |
| Examines existing artifacts for insights | Analyzer | Read → Process → Report |
| Requires multiple sequential phases | Orchestrator | Main command + sub-commands |
| Involves stakeholder decisions | Decision | Criteria → Evaluate → Recommend |

### 2.3 Command Design Checklist

For each command, verify:
- [ ] Purpose section states deliverable produced
- [ ] Workflow uses numbered phases with decision points
- [ ] Script references use `--json` output for parsing
- [ ] Template references specify placeholder names
- [ ] Completion criteria are checkable conditions
- [ ] Handoffs provide context for next command
- [ ] Assumptions marked with `[ASSUMPTION]`

## Phase 3: Infrastructure Design

### 3.1 Script Identification

Map commands to supporting scripts:

| Command | Script Need | Script Purpose |
|---------|-------------|----------------|
| `requirements.trace.md` | `check-coverage.sh` | Parse requirements, check coverage |
| `trades.evaluate.md` | `calculate-scores.py` | Calculate weighted scores |
| `risk.assess.md` | `risk-matrix.py` | Generate risk matrix |
| `test.report.md` | `aggregate-results.py` | Aggregate test results |

Script requirements:
- All scripts MUST support `--json` flag for machine parsing
- Include validation and error handling
- Document expected inputs and outputs

### 3.2 Template Requirements

Apply the 7 INCOSE-derived principles to all templates:

1. **Traceability**: Parent/child trace fields
2. **Maturity States**: DRAFT → IN_REVIEW → BASELINED → SUPERSEDED
3. **Verification Binding**: Evidence linked to claims
4. **Decision Rationale**: Context, criteria, alternatives
5. **Stakeholder Abstraction**: Audience-appropriate content
6. **Temporal Context**: Timestamps, validity periods
7. **Completeness Criteria**: "Done" checklist

See `references/deliverable-principles.md` for full principle details.

### 3.3 Memory File Design

Define persistent state across command invocations:

```
.claude/memory/
├── project-context.md       # Project identity, stakeholders
├── requirements-status.md   # Requirements state tracking
├── trades-status.md         # Active trade studies
├── risk-register.md         # Current risk inventory
├── decisions-log.md         # Decision history
├── assumptions-log.md       # Tracked assumptions [CRITICAL]
└── review-tracker.md        # Review action items
```

## Phase 4: Implementation

### 4.1 Build Order

Implement in dependency order:

```
1. Foundation Layer
   ├── Memory files (project-context.md)
   ├── Common scripts (validate-output.sh)
   └── Base templates

2. Core Commands
   ├── Entry point ([domain].init.md)
   ├── Primary generator ([domain].create.md)
   └── Validation command ([domain].validate.md)

3. Orchestration Layer
   ├── Handoff configuration
   ├── State update logic
   └── Phase completion checks

4. Integration Layer
   ├── Cross-command references
   ├── Shared script libraries
   └── Template inheritance
```

### 4.2 Command Implementation

Use the command template from `assets/templates/commands/command-template.md`.

Key patterns:
- Start with clear purpose and deliverable description
- Use numbered workflow phases
- Reference scripts with exact execution syntax
- Define explicit handoffs to next commands
- Include validation checkpoints

### 4.3 Assumption Tracking

All generated content MUST track grounding:

```markdown
<!-- GROUNDING -->
## Evidence & Assumptions

### Verified Information
- [VERIFIED: url/source] Description of verified fact

### Assumptions
- [ASSUMPTION: rationale] Description of assumption
  - Validation approach: [how to verify]
  - Risk if wrong: [impact assessment]
```

## Phase 5: Validation & Packaging

### 5.1 Validation Checks

Run validation before packaging:

```bash
python scripts/validate_speckit.py <output-dir> --strict
```

Checks performed:
- YAML syntax valid in all commands
- Handoff targets exist
- Template placeholders consistent
- Scripts executable
- Memory files defined
- Assumptions documented

### 5.2 Package Generation

Generate the complete SpecKit package:

```bash
python scripts/generate_speckit.py \
  --requirements "<requirements-file>" \
  --output-dir "<project>/.claude" \
  --include-examples
```

### 5.3 Deliverable Checklist

Before delivery, verify:

```
Package Verification:
- [ ] All commands have valid YAML frontmatter
- [ ] Scripts have been tested with sample data
- [ ] Templates include all required principle fields
- [ ] Memory files have initial structure
- [ ] README documents command dependencies
- [ ] Assumptions log is complete
- [ ] Competitor analysis documented with sources
```

## Workflow Handoffs

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Phase 1    │────▶│   Phase 2    │────▶│   Phase 3    │
│  Elicitation │     │   Command    │     │    Infra     │
│              │     │   Design     │     │   Design     │
└──────────────┘     └──────────────┘     └──────────────┘
       │                                         │
       ▼                                         ▼
 • Deliverable                             • Scripts
   inventory                               • Templates
 • Lifecycle map                           • State files
 • Automation reqs                         • Validation
 • Competitor analysis
       │                                         │
       ▼                                         ▼
┌──────────────┐     ┌──────────────┐
│   Phase 4    │────▶│   Phase 5    │
│   Build      │     │  Validate    │
│              │     │  & Package   │
└──────────────┘     └──────────────┘
```

## Reference Documents

- **Methodology Details**: See `references/methodology.md` for complete 5-phase process
- **Deliverable Principles**: See `references/deliverable-principles.md` for INCOSE-aligned standards
- **Command Patterns**: See `references/command-patterns.md` for template examples
- **Validation Rules**: See `references/validation-rules.md` for check criteria

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/competitor_analysis.py` | Search for existing solutions |
| `scripts/validate_speckit.py` | Validate generated package |
| `scripts/generate_speckit.py` | Generate complete package |
| `scripts/check_assumptions.py` | Audit assumption coverage |

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Feature-scoped commands | Incomplete artifacts | Deliverable-scoped commands |
| Ungrounded claims | Unreliable outputs | Evidence markers |
| Skipping competitor analysis | Reinventing wheels | Analyze before design |
| Missing validation phase | Broken workflows | Validation gates |
| Implicit assumptions | Hidden risks | Explicit assumption tracking |
