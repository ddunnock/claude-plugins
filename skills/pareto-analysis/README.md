# Pareto Analysis (80/20 Rule)

Identify and prioritize the "vital few" causes that contribute to the majority of problems.

## Overview

Based on the Pareto Principle: roughly 80% of effects come from 20% of causes. Use Pareto to prioritize which problems or causes deserve attention first.

## Key Features

- **5-Phase Workflow**: Problem Scoping → Data Collection → Chart Construction → Analysis → Documentation
- **Multiple Measurement Types**: Frequency, Cost, Time, Weighted Severity
- **Cumulative Percentage Calculation**: Identify the 80% threshold
- **Visual Outputs**: SVG Pareto charts and HTML reports

## When to Use

Trigger phrases:
- "Pareto", "80/20 rule"
- "vital few", "trivial many"
- "prioritize defects", "prioritize causes"
- "which problems to focus on"

## Integration Pattern
```text
Pareto → Fishbone → 5 Whys
(Prioritize)  (Brainstorm)  (Drill)
```

## Directory Structure
```text
pareto-analysis/
├── SKILL.md
├── references/
│   ├── category-guidelines.md
│   ├── quality-rubric.md
│   ├── common-pitfalls.md
│   └── examples.md
├── scripts/
└── assets/
```

## Version History

### v1.0.1
- Add path validation to generate_chart.py and generate_report.py
- Add Input Handling and Content Security section to SKILL.md

### v1.0.0 (Current)
- Initial release with 5-phase workflow
- Chart generation
- Pattern recognition guidance
- Quality scoring