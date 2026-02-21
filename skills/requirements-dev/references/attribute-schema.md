# INCOSE Requirement Attributes (A1-A13)

Reference document defining the 13 INCOSE requirement attributes with data types, examples, and usage guidance.

## Mandatory Attributes

These three attributes are required for every registered requirement.

### A1: Statement
- **Type:** String
- **Description:** The requirement text itself, written in shall-statement form
- **Example:** "The system shall process authentication requests within 200ms at 95th percentile."

### A3: Type
- **Type:** Enum (functional, performance, interface, constraint, quality)
- **Description:** Classification of the requirement's nature
- **Example:** "performance"

### A4: Priority
- **Type:** Enum (must-have, should-have, could-have, won't-have)
- **Description:** MoSCoW priority for implementation ordering
- **Example:** "must-have"

## Expandable Attributes

These ten attributes are populated as the requirement matures.

### A2: Parent/Child
- **Type:** Reference (NEED-xxx or REQ-xxx)
- **Description:** Bidirectional traceability link to parent need or derived requirement

### A5: Rationale
- **Type:** String
- **Description:** Why this requirement exists; the reasoning behind it

### A6: Verification Method
- **Type:** Enum (test, analysis, inspection, demonstration)
- **Description:** How the requirement will be verified

### A7: Success Criteria
- **Type:** String
- **Description:** Measurable criteria for verifying the requirement is met

### A8: Responsible Party
- **Type:** String
- **Description:** Person or team accountable for implementation

### A9: V&V Status
- **Type:** Enum (planned, in-progress, passed, failed, waived)
- **Description:** Current verification and validation status

### A10: Risk
- **Type:** Enum (low, medium, high, critical)
- **Description:** Risk level if this requirement is not met

### A11: Stability
- **Type:** Enum (stable, evolving, volatile)
- **Description:** How likely this requirement is to change

### A12: Source
- **Type:** Reference (SRC-xxx)
- **Description:** Origin of the requirement (stakeholder, regulation, standard)

### A13: Allocation
- **Type:** Reference (block or subsystem ID)
- **Description:** Which subsystem or block is responsible for satisfying this requirement
