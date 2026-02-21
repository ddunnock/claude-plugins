# How to Use requirements-dev

A step-by-step guide to developing INCOSE-compliant requirements with this plugin.

## Prerequisites

- **Recommended:** A completed concept-dev session with BLACKBOX.md and JSON registries. The plugin reads these artifacts to automatically set up functional blocks, stakeholder needs, and source references.
- **Alternative:** You can manually define blocks and needs if concept-dev artifacts are not available.

## Typical Workflow

### Step 1: Initialize Session

```
/reqdev:init
```

This creates a `.requirements-dev/` workspace in your project directory. If concept-dev artifacts exist in `.concept-dev/`, the plugin ingests:
- Functional blocks from BLACKBOX.md
- Source registry entries for traceability
- Assumption registry entries flagged for formalization

If no concept-dev artifacts are found, the plugin prompts you to define blocks and stakeholders manually.

### Step 2: Formalize Needs

```
/reqdev:needs
```

For each functional block, the plugin helps you formalize stakeholder needs using INCOSE patterns. Each need gets:
- A unique NEED-xxx identifier
- A structured "stakeholder needs to..." statement
- Source traceability back to concept-dev
- Status tracking (draft, approved, deferred, rejected)

The plugin presents needs in batches of 2-3 for your review and approval.

### Step 3: Develop Requirements

```
/reqdev:requirements
```

This is the core workflow. For each block, the plugin walks through five type passes:
1. **Functional** -- What the system shall do
2. **Performance** -- How well it shall do it
3. **Interface** -- How it connects to other systems
4. **Constraint** -- Limitations it must operate within
5. **Quality** -- Non-functional characteristics

For each requirement:
1. Claude drafts the requirement statement
2. **Tier 1 check:** 21 deterministic rules run instantly (vague terms, escape clauses, passive voice, etc.)
3. **Tier 2 check:** 9 semantic rules analyzed by the quality-checker agent (necessity, feasibility, verifiability, etc.)
4. You review and approve (or revise)
5. V&V method is planned based on requirement type
6. Requirement is registered with traceability to its parent need

### Step 4: Generate Deliverables

```
/reqdev:deliver
```

The document-writer agent assembles:
- REQUIREMENTS-SPECIFICATION.md from requirement registries
- TRACEABILITY-MATRIX.md from traceability links
- VERIFICATION-MATRIX.md from V&V plans

You approve each document section by section before baselining.

## Status and Resume

### Check Progress

```
/reqdev:status
```

Shows a dashboard with: current phase, block progress, requirement counts, traceability coverage percentage, open TBD/TBR items, and quality pass rate.

### Resume After Interruption

```
/reqdev:resume
```

Reads `state.json` to determine exactly where you left off -- including the current block and type pass -- and resumes from that point. Any requirements in draft are presented for completion.

## Phase 2: Validation and Research

After generating deliverables, optionally strengthen your requirements:

### Validate the Set

```
/reqdev:validate
```

Runs set-level checks across all requirements:
- **Coverage analysis:** Every need should have at least one requirement
- **Duplicate detection:** Word-level n-gram analysis finds near-duplicates
- **Terminology consistency:** Flags inconsistent terms across requirements
- **TBD/TBR report:** Lists all open to-be-determined/to-be-resolved items
- **Cross-cutting sweep:** Checks INCOSE C10-C15 categories

### Research Benchmarks

```
/reqdev:research
```

The TPM researcher agent finds industry benchmarks for measurable requirements. For example, if you have a performance requirement about response time, the researcher finds relevant benchmarks from industry standards and published studies.

## Phase 3: Decomposition

```
/reqdev:decompose
```

For complex systems, decompose system-level requirements into subsystem allocations. Each decomposition level (max 3) re-enters the quality checking pipeline. Allocation rationale is documented for every parent-to-child trace.

## Tips for Writing Good Requirements

1. **Use "shall" for requirements, "will" for statements of fact, "should" for goals**
2. **One requirement per statement** -- avoid "and" connecting separate capabilities
3. **Be specific and measurable** -- "within 200ms" not "quickly"
4. **Avoid vague terms** -- the quality checker flags these automatically
5. **Trace everything** -- every requirement needs a parent need
6. **Think about verification** -- if you can't test it, rewrite it
