# Fishbone Diagram (Ishikawa) Analysis

Create comprehensive Fishbone diagrams for structured root cause brainstorming.

## Overview

Systematically identify potential root causes through categorical brainstorming. The Fishbone provides **breadth** (all possible causes), while 5 Whys provides **depth** (drilling into specific causes).

## Key Features

- **Category Frameworks**: 6Ms (Manufacturing), 8Ps (Service), 4Ss (Service Ops), Custom
- **6-Phase Workflow**: Problem Definition → Category Selection → Brainstorming → Sub-cause Drilling → Prioritization → Documentation
- **Multi-Voting Prioritization**: Team-based cause prioritization
- **Visual Outputs**: SVG diagrams and HTML reports

## When to Use

Trigger phrases:
- "fishbone", "Ishikawa"
- "cause and effect diagram"
- "6Ms", "8Ps", "4Ss"
- "brainstorm causes"
- "what could cause this"

## Category Frameworks

| Framework | Context | Categories |
|-----------|---------|------------|
| 6Ms | Manufacturing | Man, Machine, Method, Material, Measurement, Mother Nature |
| 8Ps | Service/Marketing | Product, Price, Place, Promotion, People, Process, Physical Evidence, Policies |
| 4Ss | Service Ops | Surroundings, Suppliers, Systems, Skills |

## Directory Structure
```text
fishbone-diagram/
├── SKILL.md
├── references/
│   ├── category-frameworks.md
│   ├── facilitation-guide.md
│   ├── quality-rubric.md
│   ├── common-pitfalls.md
│   └── examples.md
├── scripts/
└── assets/
```

## Version History

### v1.0.0 (Current)
- Initial release with 6-phase workflow
- Multiple category frameworks
- SVG diagram generation
- Quality scoring