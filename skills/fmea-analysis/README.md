# Failure Mode and Effects Analysis (FMEA)

Systematic identification and risk assessment of potential failures using AIAG-VDA methodology.

## Overview

Proactive method for evaluating where and how a process, design, or system might fail. Prioritizes actions based on risk severity, not just likelihood.

## FMEA Types

| Type | Focus |
|------|-------|
| DFMEA | Design/Product — Component design |
| PFMEA | Process/Manufacturing — Production |
| FMEA-MSR | Monitoring & System Response — Diagnostics |

## Key Features

- **AIAG-VDA 7-Step Methodology**: Planning → Structure → Function → Failure → Risk → Optimization → Documentation
- **Action Priority (AP)**: Replaces traditional RPN for risk prioritization
- **Failure Chain Analysis**: Effect ← Mode ← Cause relationships
- **Prevention vs. Detection Controls**: Distinct control categorization

## When to Use

Trigger phrases:
- "FMEA", "failure mode"
- "DFMEA", "PFMEA"
- "severity occurrence detection"
- "RPN", "Action Priority"
- "design risk analysis"
- "APQP", "PPAP"

## Directory Structure
```text
fmea-analysis/
├── SKILL.md
├── references/
│   ├── rating-tables.md
│   ├── quality-rubric.md
│   ├── common-pitfalls.md
│   └── examples.md
├── scripts/
└── assets/
```

## Version History

### v1.0.1 (Current)
- Add HTML escaping (XSS prevention) to generate_report.py
- Add path validation to all scripts (reject traversal, restrict extensions)
- Add Input Handling and Content Security section to SKILL.md

### v1.0.0
- Initial release with AIAG-VDA 7-step workflow
- Action Priority risk assessment
- Rating tables for S/O/D
- Quality scoring system