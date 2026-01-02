# Validation Rules Reference

## Table of Contents

1. [Validation Overview](#validation-overview)
2. [Command Validation](#command-validation)
3. [Script Validation](#script-validation)
4. [Template Validation](#template-validation)
5. [State File Validation](#state-file-validation)
6. [Grounding Validation](#grounding-validation)
7. [Integration Validation](#integration-validation)

---

## Validation Overview

SpecKit packages must pass all validation checks before delivery.

### Validation Levels

| Level | Scope | When Applied |
|-------|-------|--------------|
| **Syntax** | Individual files | Continuous |
| **Structure** | Directory layout | After Phase 4 |
| **Semantic** | Cross-references | After Phase 4 |
| **Integration** | End-to-end workflows | Phase 5 |
| **Grounding** | Evidence markers | Continuous |

### Quick Validation Command

```bash
python scripts/validate_speckit.py <output-dir> --level all --strict
```

---

## Command Validation

### Rule C1: Valid YAML Frontmatter

All `.md` files in `commands/` MUST have valid YAML frontmatter.

**Required Fields:**
- `description`: Non-empty string, max 200 chars

**Optional Fields:**
- `agent.model`: Valid model name (sonnet, opus, haiku)

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check commands-yaml
```

**Valid Example:**
```yaml
---
description: "Generate SRS from stakeholder needs"
agent:
  model: sonnet
---
```

**Invalid Examples:**
```yaml
# Missing description
---
agent:
  model: sonnet
---

# Invalid model
---
description: "Generate SRS"
agent:
  model: invalid-model
---
```

### Rule C2: Workflow Structure

Commands MUST have numbered phases with decision points.

**Required Sections:**
- `## Purpose`
- `## Prerequisites` (with checkbox list)
- `## Workflow` (with numbered phases)
- `## Outputs`
- `## Completion Criteria` (with checkbox list)

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check commands-structure
```

### Rule C3: Script References

All script references MUST:
- Use `--json` flag for machine parsing
- Reference existing scripts in `scripts/`
- Use forward slashes in paths

**Valid:**
```bash
python scripts/validate-output.py data.json --json
```

**Invalid:**
```bash
python scripts\validate-output.py data.json
python scripts/nonexistent.py --json
```

### Rule C4: Template References

All template references MUST:
- Reference existing files in `templates/`
- Specify placeholder format consistently

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check template-refs
```

### Rule C5: Handoff Targets

All handoff targets MUST:
- Reference existing command files
- Provide context, inputs, and objective

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check handoffs
```

---

## Script Validation

### Rule S1: Syntax Validity

All scripts MUST pass syntax validation.

**Bash:**
```bash
bash -n scripts/bash/*.sh
```

**Python:**
```bash
python -m py_compile scripts/python/*.py
```

### Rule S2: JSON Output Support

All scripts MUST support `--json` flag for machine-readable output.

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check script-json
```

**Required Output Format:**
```json
{
  "success": true,
  "data": {},
  "errors": [],
  "warnings": []
}
```

### Rule S3: Error Handling

All scripts MUST:
- Return non-zero exit code on failure
- Provide meaningful error messages
- Log errors to stderr

**Example Pattern:**
```python
import sys
import json

def main():
    try:
        result = do_work()
        print(json.dumps({"success": True, "data": result}))
        return 0
    except Exception as e:
        print(json.dumps({"success": False, "errors": [str(e)]}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Rule S4: Documentation

All scripts MUST include:
- Purpose description
- Input parameters
- Output format
- Exit codes

**Example Header:**
```python
"""
validate-srs.py - Validate Software Requirements Specification

Usage: python validate-srs.py <srs-path> [--json]

Inputs:
  - srs-path: Path to SRS document

Outputs:
  - Validation results (text or JSON)

Exit Codes:
  - 0: Validation passed
  - 1: Validation failed
  - 2: Input error
"""
```

---

## Template Validation

### Rule T1: Required Sections

All templates MUST include:
- Document Control section
- Purpose & Scope section
- Traceability section
- Completeness Checklist

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check template-structure
```

### Rule T2: Placeholder Consistency

Placeholders MUST use consistent format: `[PLACEHOLDER_NAME]`

**Valid:**
```markdown
| Document ID | [DOC_ID] |
| Version | [VERSION] |
```

**Invalid:**
```markdown
| Document ID | {{DOC_ID}} |
| Version | <VERSION> |
```

### Rule T3: Principle Compliance

Templates MUST implement the 7 INCOSE principles:

| Principle | Required Element |
|-----------|------------------|
| Traceability | Trace tables |
| Maturity States | Status field |
| Verification Binding | Verification matrix |
| Decision Rationale | Decision record (if applicable) |
| Stakeholder Abstraction | Audience definition |
| Temporal Context | Date fields |
| Completeness | Done checklist |

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check template-principles
```

---

## State File Validation

### Rule M1: Required Files

The `memory/` directory MUST contain:
- `project-context.md`
- `assumptions-log.md`

**Optional but recommended:**
- `requirements-status.md`
- `decisions-log.md`
- `risk-register.md`

### Rule M2: Structure Compliance

Each memory file MUST have:
- Consistent heading structure
- Table format for tracked items
- Date fields where applicable

**Example Structure:**
```markdown
# Project Context

## Project Identity

| Field | Value |
|-------|-------|
| Project Name | [NAME] |
| Domain | [DOMAIN] |

## Stakeholders

| Role | Name | Concern |
|------|------|---------|
| [ROLE] | [NAME] | [CONCERN] |

## Last Updated

[ISO_DATE]
```

### Rule M3: Cross-Reference Integrity

All references in memory files MUST:
- Point to existing artifacts
- Use consistent ID formats

---

## Grounding Validation

### Rule G1: Evidence Markers

All factual claims MUST include evidence markers:

| Marker | Usage |
|--------|-------|
| `[VERIFIED: <source>]` | Confirmed from authoritative source |
| `[DERIVED: <basis>]` | Logically derived from verified facts |
| `[ASSUMPTION: <rationale>]` | Reasonable inference |
| `[TBD]` | Information not yet available |

**Check:**
```bash
python scripts/check_assumptions.py <dir> --report
```

### Rule G2: Assumption Documentation

All assumptions MUST be logged in `memory/assumptions-log.md`:

```markdown
## Assumptions Log

| ID | Assumption | Rationale | Validation | Risk if Wrong |
|----|------------|-----------|------------|---------------|
| A-001 | [Statement] | [Why assumed] | [How to verify] | [Impact] |
```

### Rule G3: Source Attribution

Competitor analysis and external references MUST include:
- Source URL
- Access date
- Verification status

**Example:**
```markdown
## Competitor Analysis

| Solution | Source | Accessed | Status |
|----------|--------|----------|--------|
| Tool X | https://example.com | 2025-01-15 | [VERIFIED] |
```

---

## Integration Validation

### Rule I1: End-to-End Workflow

At least one complete workflow MUST be tested:

```markdown
## Workflow Test: [Name]

| Step | Command | Input | Expected | Actual | Pass |
|------|---------|-------|----------|--------|------|
| 1 | /[cmd] | [input] | [expected] | [actual] | Y/N |
```

### Rule I2: Handoff Preservation

Context MUST be preserved across handoffs:

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check handoff-context
```

### Rule I3: State Consistency

Memory files MUST remain consistent after workflow execution:

**Check:**
```bash
python scripts/validate_speckit.py <dir> --check state-consistency
```

---

## Validation Summary Checklist

Before packaging, verify:

### Commands
- [ ] All commands have valid YAML frontmatter
- [ ] All commands have required sections
- [ ] All script references are valid
- [ ] All template references are valid
- [ ] All handoff targets exist

### Scripts
- [ ] All scripts pass syntax validation
- [ ] All scripts support `--json` flag
- [ ] All scripts have error handling
- [ ] All scripts are documented

### Templates
- [ ] All templates have required sections
- [ ] All placeholders use consistent format
- [ ] All templates implement 7 principles

### State
- [ ] Required memory files present
- [ ] Memory files have correct structure
- [ ] Cross-references are valid

### Grounding
- [ ] Evidence markers present
- [ ] Assumptions logged
- [ ] Sources attributed

### Integration
- [ ] At least one workflow tested
- [ ] Handoffs preserve context
- [ ] State remains consistent
