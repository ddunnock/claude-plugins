# RCCA Master

Orchestrate complete Root Cause and Corrective Action (RCCA) investigations using the 8D methodology.

## Overview

RCCA Master guides systematic failure investigations through all eight disciplines (8D) with:
- **D1: Team Formation** — Domain-specific team composition recommendations
- **D2: Problem Definition** — Invokes `problem-definition` skill for 5W2H and IS/IS NOT
- **D3: Containment** — Interim protection actions
- **D4: Root Cause Analysis** — Integrated tool selection (5 Whys, Fishbone, Pareto, KT, FTA)
- **D5-D6: Corrective Action** — Selection and implementation
- **D7: Prevention** — Systemic preventive measures
- **D8: Closure** — Effectiveness verification and recognition

## Key Features

- **Gate Checkpoints**: Each phase requires explicit user confirmation before proceeding
- **Domain Assessment**: Recommends team composition based on problem domain
- **Tool Selection**: Guides selection of appropriate D4 analysis tools based on problem characteristics
- **Complexity Classification**: Scales team size and timeline to problem complexity

## When to Use

Trigger phrases:
- "RCCA", "8D", "root cause analysis"
- "corrective action", "failure investigation"
- "nonconformance analysis", "quality problem"
- "customer complaint investigation"

## Integration

This skill orchestrates:
- `problem-definition` — D2 problem statement
- `five-whys-analysis` — D4 causal chain drilling
- `fishbone-diagram` — D4 cause brainstorming
- `pareto-analysis` — D4 cause prioritization
- `kepner-tregoe-analysis` — D4/D5/D6 specification and decision analysis
- `fault-tree-analysis` — D4 safety-critical analysis

## Directory Structure
```text
rcca-master/
├── SKILL.md              # Main instructions
├── references/
│   ├── team-formation-guide.md
│   └── tool-selection-guide.md
└── templates/
    └── 8d-report-template.md
```

## Version History

### v1.0.0 (Current)
- Initial release with complete 8D workflow
- Gate checkpoint system
- Domain-based team recommendations
- Tool selection decision tree
