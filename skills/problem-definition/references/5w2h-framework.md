# 5W2H Framework for Problem Definition

The 5W2H technique systematically captures essential information about a problem. In RCCA problem definition, **exclude Why** — that belongs to root cause analysis.

## The Questions

### WHAT

**What (Object):** Identify the specific item, part, product, or system with the problem.
- Use precise nomenclature (part numbers, model designations)
- Avoid generic terms ("the part", "the thing")

**What (Defect):** Describe the specific defect, failure mode, or nonconformance.
- Use technical, measurable terms
- Avoid subjective descriptions ("bad", "poor quality")

Good: "Weld spatter and incomplete fusion on joint"
Bad: "Bad welding"

### WHERE

**Where (Geographic):** Location where problem was detected or originated.
- Facility, production line, workstation, country/region
- Detection point vs. origin point may differ

**Where (On Object):** Physical location on the item.
- Be specific: "locking tab area" not "on the connector"
- Reference drawings or specifications when possible

### WHEN

**When (Calendar):** Date/time of first observation.
- Specific dates narrow investigation window
- Note any patterns (shift, day of week, season)

**When (Lifecycle):** Point in process, product lifecycle, or operation sequence.
- Manufacturing stage, test phase, field operation
- Time-to-failure if applicable

### WHO

**Who (Reporter):** Person or entity who detected/reported the problem.
- Customer, inspector, operator, automated system
- Important for traceability, not for blame

**Who (Affected):** Stakeholders impacted by the problem.
- Internal departments, customers, end users

### HOW

**How (Detection):** Method by which problem was discovered.
- Visual inspection, functional test, measurement, customer complaint
- Notes whether detection was planned or incidental

**How (Manifestation):** Observable symptoms or behaviors.
- What does the failure look like in operation?
- Intermittent vs. consistent occurrence

### HOW MUCH

**Extent:** Scale and magnitude of the problem.
- Quantity affected (units, lots, shipments)
- Rate or frequency (defects per million, failure rate)
- Severity classification (critical, major, minor)
- Financial or operational impact when known

## Adapting 5W2H by Context

| Context | Key Emphasis |
|---------|--------------|
| Manufacturing defect | What (defect type), Where (line/station), How Much (reject rate) |
| Field failure | When (time-to-failure), How (operating conditions), How Much (affected population) |
| Customer complaint | What (symptom reported), Who (customer segment), How (detection by customer) |
| Process deviation | What (parameter out of spec), When (process stage), How Much (deviation magnitude) |

## Data Sources

- Inspection records and test data
- Production logs (lot numbers, shift records, machine settings)
- Photos, videos, physical samples
- Customer reports and complaint records
- FMEA and control plan documents
- Prior nonconformance history
