# Specification Refiner Skill

**Version**: 2.0.0

Systematic analysis and refinement of specifications, requirements, architecture designs, and project plans using the SEAMS gap analysis framework with sequential clarification questioning.

## Features

- **SEAMS Framework Analysis**: Structure, Execution, Assumptions, Mismatches, Stakeholders
- **Sequential Clarification (CLARIFY Phase)**: One question at a time with constrained answer formats
- **11-Category Ambiguity Taxonomy**: Comprehensive coverage mapping
- **Multi-Phase Workflow**: 9 phases from ASSESS through VALIDATE
- **Immediate Integration**: Atomic updates after each clarification answer
- **Dual Mode Support**: SIMPLE (single domain) and COMPLEX (multi-domain with RTM)

## Phases

| Phase | Name | Description |
|-------|------|-------------|
| 0 | ASSESS | Evaluate complexity, select mode |
| 1 | INGEST | Load document, confirm understanding |
| 2 | ANALYZE | Run SEAMS + Critical Path analysis |
| 3 | CLARIFY | Sequential questions with immediate integration |
| 4 | PRESENT | Surface detailed findings |
| 5 | ITERATE | Accept changes, re-analyze |
| 6 | SYNTHESIZE | Comprehensive summary for approval |
| 7 | OUTPUT | Generate refined specification(s) |
| 8 | VALIDATE | Review, validate traceability, advance status |

## CLARIFY Phase Highlights (v2.0.0)

The new CLARIFY phase uses sequential questioning to reduce cognitive load:

- **One question at a time** - Never batches multiple questions
- **Constrained answers** - Multiple choice (2-5 options) OR short phrase (5 words max)
- **Recommended answers** - Always provides a recommendation with reasoning
- **Immediate integration** - Updates spec/analysis state after each answer
- **Question limits** - 5 per session, 10 total across analysis
- **Coverage mapping** - Tracks clarity across 11 ambiguity categories

### Ambiguity Categories

1. Functional Scope & Behavior
2. Domain & Data Model
3. Interaction & UX Flow
4. Non-Functional Quality Attributes
5. Integration & External Dependencies
6. Edge Cases & Failure Handling
7. Constraints & Tradeoffs
8. Terminology & Consistency
9. Completion Signals
10. Assumptions & Risks
11. Misc & Placeholders

## Usage

The skill triggers on:
- Gap analysis requests
- Specification review
- Requirements analysis
- Architecture critique
- Design validation
- Plan assessment
- Weakness identification
- Assumption auditing

## Files

```
specification-refiner/
├── SKILL.md                              # Main skill definition
├── README.md                             # This file
├── .claude-plugin/
│   └── plugin.json                       # Plugin metadata
├── assets/
│   ├── analysis-state-template.md        # State tracking template
│   └── traceability-matrix-template.md   # RTM template (COMPLEX mode)
└── references/
    ├── gate-templates.md                 # Phase gate output templates
    ├── seams-framework.md                # SEAMS methodology reference
    ├── critical-path-analysis.md         # Critical path analysis guide
    └── spec-hierarchy.md                 # A-Spec/B-Spec hierarchy guide
```

## Changelog

### v2.0.0
- Added Phase 3: CLARIFY with sequential questioning
- Implemented 11-category ambiguity taxonomy
- Added constrained answer formats (multiple choice / short phrase)
- Added recommended answer generation with reasoning
- Implemented immediate integration protocol
- Added coverage map tracking
- Set question limits (5/session, 10/total)
- Updated phase numbering (now 0-8)
- Added coverage map to analysis-state-template.md
- Added CLARIFY gate templates

### v1.0.0
- Initial release with SEAMS framework
- 8-phase workflow (ASSESS through VALIDATE)
- SIMPLE and COMPLEX mode support
- Traceability matrix for COMPLEX mode
