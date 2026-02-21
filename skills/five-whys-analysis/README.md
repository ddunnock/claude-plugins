# 5 Whys Root Cause Analysis

Conduct rigorous 5 Whys analysis with guided questioning, quality scoring, and professional report generation.

## Overview

The 5 Whys is an iterative interrogative technique for exploring cause-and-effect relationships. Continue asking "Why?" until reaching a fundamental, actionable cause.

## Key Features

- **6-Phase Workflow**: Problem Definition → Team & Evidence → Iterative Why → Verification → Countermeasures → Documentation
- **Quality Scoring**: 6-dimension rubric with weighted scoring (0-100 points)
- **Verification Tests**: Reversal, Prevention, Recurrence, Control, Evidence
- **Countermeasure Development**: 5 Hows framework

## When to Use

Trigger phrases:
- "5 whys", "five whys"
- "root cause", "why did this happen"
- "find the cause", "drill down"
- "causal chain"

## Quality Scoring Dimensions

| Dimension | Weight |
|-----------|--------|
| Problem Definition | 15% |
| Causal Chain Logic | 25% |
| Evidence Basis | 20% |
| Root Cause Depth | 20% |
| Actionability | 10% |
| Countermeasures | 10% |

Passing threshold: 70 points

## Directory Structure
```text
five-whys-analysis/
├── SKILL.md
├── references/
│   ├── quality-rubric.md
│   ├── common-pitfalls.md
│   └── examples.md
├── scripts/
│   ├── generate_report.py
│   └── score_analysis.py
└── assets/
```

## Version History

### v1.0.1 (Current)
- Add path validation to all scripts (reject traversal, restrict extensions)
- Add Input Handling and Content Security section to SKILL.md
- Fix HOW_TO_USE.md: remove nonexistent run_analysis.py, correct CLI flags

### v1.0.0
- Initial release with structured Q&A workflow
- Quality scoring system
- Verification tests
- Report generation