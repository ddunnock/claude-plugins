# Fault Tree Analysis (FTA)

Systematically identify and analyze causes of system failures using Boolean logic gates.

## Overview

Top-down, deductive failure analysis method that maps how combinations of lower-level events (basic events) lead to an undesired system-level event (top event). Uses AND/OR gates to represent relationships.

## Key Features

- **7-Phase Workflow**: System Definition → Top Event → Tree Construction → Qualitative → Quantitative → CCF → Documentation
- **Minimal Cut Sets**: Identify smallest combinations causing top event
- **Single Point of Failure Detection**: Order 1 cut sets
- **Common Cause Failure Analysis**: Beta-factor model

## Analysis Types

| Type | Purpose |
|------|---------|
| Qualitative | Failure pathways, minimal cut sets, single points of failure |
| Quantitative | Failure probabilities, importance measures |

## When to Use

Trigger phrases:
- "fault tree", "FTA"
- "system failure analysis"
- "minimal cut sets", "single point of failure"
- "safety analysis", "reliability analysis"
- "failure probability", "AND/OR gates"

## Directory Structure
```text
fault-tree-analysis/
├── SKILL.md
├── references/
│   ├── quality-rubric.md
│   ├── common-pitfalls.md
│   └── examples.md
├── scripts/
└── assets/
```

## Version History

### v1.0.0 (Current)
- Initial release with 7-phase workflow
- Qualitative and quantitative analysis
- Minimal cut set identification
- Common cause failure analysis