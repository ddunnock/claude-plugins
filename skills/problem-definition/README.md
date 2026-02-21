# Problem Definition

Guide RCCA/8D problem definition using 5W2H and IS/IS NOT analysis.

## Overview

Transforms scattered failure observations into precise, bounded problem statements that enable effective root cause analysis. The problem statement describes the deviation between expected and actual — without inferring cause or prescribing solution.

## Key Features

- **5W2H Framework**: Systematically captures What, Where, When, Who, How, How Much (excludes Why)
- **IS/IS NOT Analysis**: Sharpens boundaries and reveals investigation clues
- **Gap Quantification**: Expresses deviation numerically
- **Pitfall Validation**: Checks for embedded cause, solution, vagueness, or blame

## When to Use

Trigger phrases:
- "problem definition", "problem statement"
- "define the problem", "what went wrong"
- "D2", "8D problem definition"
- "5W2H", "IS/IS NOT"

## Workflow

1. **Assess available information** — Identify known vs. missing 5W2H elements
2. **Elicit missing data** — Ask structured questions (2-3 per turn)
3. **Apply 5W2H framework** — Populate all dimensions except Why
4. **Sharpen with IS/IS NOT** — Contrast what IS vs. IS NOT affected
5. **Quantify the gap** — Express deviation numerically
6. **Synthesize statement** — Combine into single problem statement
7. **Validate** — Check for embedded cause/solution

## Output Format
```text
[Object] exhibited [defect/failure mode] at [location] during [phase/operation], 
affecting [extent/quantity], detected by [method].
```

## Directory Structure
```text
problem-definition/
├── SKILL.md
└── references/
    ├── 5w2h-framework.md
    ├── is-is-not-analysis.md
    ├── question-bank.md
    ├── pitfalls.md
    └── examples.md
```

## Version History

### v1.0.1
- Add path validation to generate_report.py
- Add Input Handling and Content Security section to SKILL.md

### v1.0.0 (Current)
- Initial release with 5W2H and IS/IS NOT frameworks
- Structured elicitation workflow
- Validation checklist