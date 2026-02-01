# Severity Classification Scales

Embedded severity scales for offline use when knowledge-mcp is unavailable.

## MIL-STD-882E Severity Categories (Safety-Critical Systems)

Source: MIL-STD-882E, Department of Defense Standard Practice: System Safety (2012)

| Category | Name | Description |
|----------|------|-------------|
| I | Catastrophic | Could result in death, permanent total disability, irreversible significant environmental impact, or monetary loss ≥$10M |
| II | Critical | Could result in permanent partial disability, injuries or occupational illness that may result in hospitalization of at least three personnel, reversible significant environmental impact, or monetary loss ≥$1M but <$10M |
| III | Marginal | Could result in injury or occupational illness resulting in one or more lost workday(s), reversible moderate environmental impact, or monetary loss ≥$100K but <$1M |
| IV | Negligible | Could result in injury or occupational illness not resulting in a lost workday, minimal environmental impact, or monetary loss <$100K |

**Use for:** Safety-critical systems, aerospace, defense, medical devices, high-consequence industries

**Selection guidance:**
- Consider worst credible outcome
- Include environmental and financial impacts
- Default to higher severity when uncertain

## AIAG-VDA FMEA Severity Scale (Quality/Manufacturing)

Source: AIAG-VDA FMEA Handbook (2019), Table 5.1

| Rating | Severity | Effect Description | Customer Impact |
|--------|----------|-------------------|-----------------|
| 10 | Very High | Safety-related, non-compliance with government regulations | Product causes safety hazard without warning |
| 9 | Very High | Product inoperable, loss of primary function | Customer very dissatisfied |
| 8 | High | Product operable but at reduced performance level | Customer dissatisfied |
| 7 | High | Product operable but comfort/convenience functions inoperable | Customer somewhat dissatisfied |
| 6 | Moderate | Product operable with some items inoperable | Customer experiences some dissatisfaction |
| 5 | Moderate | Product operable with degraded comfort/convenience | Customer experiences some dissatisfaction |
| 4 | Low | Fit and finish items, slight noise, defect noticed by most customers (>75%) | Average customer will notice defect |
| 3 | Low | Fit and finish items, defect noticed by discriminating customers (50%) | Discriminating customer will notice defect |
| 2 | Very Low | Fit and finish items, defect noticed by very few customers (<25%) | Very few customers will notice defect |
| 1 | None | No effect | No customer impact |

**Use for:** Product quality, manufacturing processes, customer satisfaction, FMEA severity ratings

**Selection guidance:**
- Focus on end customer effect
- Consider regulatory implications (10 = regulatory non-compliance)
- Severity 9-10 always requires action regardless of occurrence/detection

## Scale Comparison

| MIL-STD-882E | AIAG-VDA | General Interpretation |
|--------------|----------|----------------------|
| I (Catastrophic) | 10 | Safety hazard, death possible |
| II (Critical) | 9 | Major function loss, serious injury |
| II-III | 7-8 | Significant performance loss |
| III (Marginal) | 4-6 | Moderate effect, customer notices |
| IV (Negligible) | 1-3 | Minor or no effect |

## Citation Format

When MCP unavailable, cite as:
- "Severity: I (Catastrophic) per MIL-STD-882E (embedded reference data)"
- "Severity: 7 (High) per AIAG-VDA FMEA Handbook (2019) embedded severity scale"

**Never fabricate section numbers** when knowledge-mcp unavailable.

## Related Standards

For industry-specific severity scales:
- **Medical devices:** ISO 14971 (Risk Management)
- **Automotive functional safety:** ISO 26262 (ASIL levels)
- **Aerospace:** SAE ARP4761 (Safety assessment)
- **Process industry:** IEC 61511 (SIL levels)

Query `/lookup-standard [industry] severity classification` when knowledge-mcp connected.

---

**Document Version**: 1.0
**Source:** MIL-STD-882E (2012), AIAG-VDA FMEA Handbook (2019)
**Last Updated**: 2026-01-31
