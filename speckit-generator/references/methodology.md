# Requirements to SpecKit: Complete Methodology Reference

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Phase 1: Requirements Elicitation](#phase-1-requirements-elicitation)
3. [Phase 2: Command Architecture Design](#phase-2-command-architecture-design)
4. [Phase 3: Infrastructure Design](#phase-3-infrastructure-design)
5. [Phase 4: Implementation](#phase-4-implementation)
6. [Phase 5: Validation & Integration](#phase-5-validation--integration)

## Core Philosophy

### Project vs Feature Approach

| Feature-Based (Avoid) | Project-Based (Prefer) |
|----------------------|------------------------|
| `add-component` | `generate-architecture-spec` |
| `fix-bug` | `conduct-trade-study` |
| `update-dependency` | `create-requirements-baseline` |
| Incremental changes | Complete deliverables |
| Developer-centric | Stakeholder-centric |
| Code artifacts | Engineering artifacts |

Project-based commands produce **complete, reviewable deliverables** aligned with engineering gates, reviews, and decision points.

### Grounding Principle

All automation outputs MUST be grounded in evidence:

**Evidence Markers:**
- `[VERIFIED: <source>]` - Confirmed from authoritative source
- `[DERIVED: <basis>]` - Logically derived from verified facts
- `[ASSUMPTION: <rationale>]` - Reasonable inference, needs validation
- `[TBD]` - Information not yet available

**Grounding Audit Questions:**
1. What is the source of this claim?
2. When was this information last verified?
3. What happens if this assumption is wrong?
4. How can this be validated?

---

## Phase 1: Requirements Elicitation

### 1.1 Deliverable Inventory

Catalog engineering artifacts by category:

| Category | Typical Deliverables |
|----------|---------------------|
| Requirements | SRS, ConOps, Use Cases, IRD |
| Architecture | SDD, ICD, Block Diagrams, Views |
| Trade Studies | Alternatives Analysis, Decision Docs |
| Risk | Risk Register, Mitigation Plans |
| Test | Test Plans, Procedures, Reports |
| Reviews | SRR, PDR, CDR artifacts |

### 1.2 Lifecycle Phase Mapping

For each deliverable, identify:

| Question | Purpose |
|----------|---------|
| When is it produced? | Lifecycle phase alignment |
| What inputs does it need? | Dependency chain |
| Who reviews/approves it? | Stakeholder identification |
| What decisions does it enable? | Gate/milestone linkage |
| How is it maintained? | Living document vs baseline |

### 1.3 Automation Requirements Template

```markdown
## AR-### [Deliverable Name]

**Stakeholder Need**: [What problem does this solve?]

**Inputs**:
- [ ] [Input 1] - Source: [where it comes from]
- [ ] [Input 2] - Source: [where it comes from]

**Outputs**:
- [ ] [Output 1] - Format: [format/template]
- [ ] [Output 2] - Format: [format/template]

**Quality Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Frequency**: [One-time / Periodic / Event-driven]

**Automation Potential**:
- [ ] Fully automated
- [ ] Interactive (requires decisions)
- [ ] Hybrid (automated with checkpoints)

**Grounding**:
- Evidence source: [reference]
- Assumptions: [list any]
```

### 1.4 Competitor Analysis Process

Before designing, search for existing solutions:

**Search Strategy:**
1. Web search: `"<domain>" automation`, `"<domain>" CLI tools`
2. GitHub search: similar projects, established patterns
3. Industry standards: ISO, INCOSE, IEEE references
4. Existing tools: Jira, Azure DevOps, specialized tools

**Documentation Format:**
```markdown
## Competitor Analysis: [Domain]

### Existing Solutions

| Solution | Strengths | Gaps | Source |
|----------|-----------|------|--------|
| [Tool 1] | [what it does well] | [what's missing] | [URL] |

### Design Implications
- [What to adopt from existing solutions]
- [What gaps to fill with custom automation]

### Evidence Quality
- [VERIFIED]: [list of confirmed facts]
- [ASSUMPTION]: [list of inferences]
```

---

## Phase 2: Command Architecture Design

### 2.1 Command Taxonomy

Organize commands by lifecycle phase:

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
    ├── review.conduct.md
    └── review.disposition.md
```

### 2.2 Command Pattern Selection

| Pattern | Use When | Structure |
|---------|----------|-----------|
| **Generator** | Creating structured documents | Input → Template → Output |
| **Analyzer** | Examining artifacts for insights | Read → Process → Report |
| **Orchestrator** | Multi-phase execution | Init → Phases → Complete |
| **Decision** | Guiding stakeholder choices | Criteria → Evaluate → Recommend |

### 2.3 Handoff Design

Commands flow naturally into each other:

```yaml
handoffs:
  - label: "Proceed to [Next Phase]"
    agent: [target-command]
    prompt: |
      Context: [What was accomplished]
      Inputs: [What the next command receives]
      Objective: [What the next command should do]
```

---

## Phase 3: Infrastructure Design

### 3.1 Script Identification

Identify deterministic operations for scripts:

| Command | Script | Operation |
|---------|--------|-----------|
| `requirements.trace.md` | `check-coverage.sh` | Parse requirements, check coverage |
| `trades.evaluate.md` | `calculate-scores.py` | Weighted score calculation |
| `risk.assess.md` | `risk-matrix.py` | Risk probability/impact matrix |
| `test.report.md` | `aggregate-results.py` | Test result aggregation |

**Script Requirements:**
- All scripts MUST support `--json` flag
- Include error handling with clear messages
- Document inputs, outputs, and exit codes
- Use portable paths (forward slashes)

### 3.2 Template Design

Apply INCOSE principles:

1. **Traceability**: Parent/child trace sections
2. **Maturity States**: Status field with transitions
3. **Verification Binding**: Evidence-to-claim linkage
4. **Decision Rationale**: Context/criteria/selection capture
5. **Stakeholder Abstraction**: Audience-appropriate content
6. **Temporal Context**: Timestamps, validity periods
7. **Completeness Criteria**: Done checklist

### 3.3 State Management

Define persistent state:

```
.claude/memory/
├── project-context.md       # Identity, stakeholders
├── requirements-status.md   # Requirements state
├── trades-status.md         # Active trade studies
├── risk-register.md         # Risk inventory
├── decisions-log.md         # Decision history
├── assumptions-log.md       # Tracked assumptions
└── review-tracker.md        # Action items
```

---

## Phase 4: Implementation

### 4.1 Build Order

Implement in dependency order:

1. **Foundation Layer**
   - Memory files with initial structure
   - Common validation scripts
   - Base template patterns

2. **Core Commands**
   - Entry point commands
   - Primary generators
   - Validation commands

3. **Orchestration Layer**
   - Handoff configuration
   - State update logic
   - Phase completion checks

4. **Integration Layer**
   - Cross-command references
   - Shared script libraries

### 4.2 Command Development Checklist

For each command:
- [ ] Purpose section states deliverable
- [ ] Workflow uses numbered phases
- [ ] Script references use `--json`
- [ ] Template placeholders consistent
- [ ] Completion criteria checkable
- [ ] Handoffs provide full context
- [ ] Assumptions explicitly marked

---

## Phase 5: Validation & Integration

### 5.1 Validation Gates

| Check | Method |
|-------|--------|
| YAML syntax valid | Parse all frontmatter |
| Handoff targets exist | Verify `.md` files |
| Template placeholders consistent | Cross-reference |
| Scripts executable | `bash -n` / `python -m py_compile` |
| State files defined | Check memory references |
| Assumptions documented | Audit assumption markers |

### 5.2 End-to-End Workflow Testing

Test complete workflows:

```markdown
## Workflow Test: [Name]

**Start Command**: /[domain].[command]
**End State**: [Expected deliverable]

### Test Cases

| Step | Command | Input | Expected |
|------|---------|-------|----------|
| 1 | /[cmd] | [input] | [output] |
| 2 | /[cmd] | [input] | [output] |

### Handoff Verification

| From | To | Context Preserved |
|------|----|-------------------|
| [src] | [tgt] | Yes/No |
```

### 5.3 Package Contents

Final package structure:

```
.claude/
├── commands/
│   └── [organized by lifecycle phase]
├── scripts/
│   ├── bash/
│   └── python/
├── templates/
│   └── [organized by deliverable type]
└── memory/
    └── [state files]
```
