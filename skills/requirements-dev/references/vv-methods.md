# Verification and Validation Method Selection Guide

Reference document for selecting appropriate V&V methods based on requirement type.

## Type-to-Default-Method Mapping

| Requirement Type | Primary Method | Alternative Methods |
|-----------------|----------------|---------------------|
| Functional | System/unit test | Demonstration, inspection |
| Performance | Load/benchmark test | Analysis, simulation |
| Interface/API | Integration/contract test | Inspection, demonstration |
| Constraint | Inspection/analysis | Demonstration, test |
| Quality | Demonstration/analysis | Test, inspection |

## Method Definitions

### Test
Execution of the system under controlled conditions to verify behavior meets requirements.
- **System test:** End-to-end verification of a complete capability
- **Unit test:** Verification of individual components in isolation
- **Integration test:** Verification of component interactions
- **Load test:** Verification of performance under expected load
- **Benchmark test:** Verification of performance against quantitative thresholds

### Analysis
Examination of data, models, or documentation to verify requirement satisfaction.
- **Modeling/simulation:** Mathematical or computational models predict behavior
- **Review of design documents:** Tracing design decisions to requirements
- **Calculation:** Mathematical proof that design satisfies quantitative requirements

### Inspection
Visual or physical examination of the system or its documentation.
- **Code review:** Examination of source code for compliance
- **Configuration audit:** Verification that deployed configuration matches requirements
- **Document review:** Examination of documentation for completeness and accuracy

### Demonstration
Operation of the system to show capability without formal measurement.
- **Walkthrough:** Step-by-step execution of a scenario
- **Prototype review:** Evaluation of prototype against requirements
- **User acceptance:** Stakeholder evaluation of system behavior

## Success Criteria Templates

### For test methods:
"[Metric] shall be [comparison] [threshold] when [test condition]."

### For analysis methods:
"[Analysis method] shall confirm [property] under [conditions/assumptions]."

### For inspection methods:
"[Artifact] shall contain [required element] as verified by [review process]."

### For demonstration methods:
"[Capability] shall be observed when [demonstration scenario] is executed."
