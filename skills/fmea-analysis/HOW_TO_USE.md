# How to Use: FMEA Analysis

The FMEA Analysis skill conducts Failure Mode and Effects Analysis using AIAG-VDA methodology with Action Priority (AP) risk assessment, supporting DFMEA (Design), PFMEA (Process), and FMEA-MSR.

## When to Use This Skill

- New product/process design reviews
- Proactive risk assessment before production
- APQP/PPAP submissions
- Analyzing potential failure modes
- Prioritizing design or process improvements
- Regulatory compliance (automotive, aerospace, medical)

## Quick Start

Describe what you need to analyze:

```
Help me create a DFMEA for a new electric motor controller.
Key functions: speed regulation, overcurrent protection, thermal management.
```

## FMEA Types

| Type | Focus | When to Use |
|------|-------|-------------|
| **DFMEA** | Design | New product development |
| **PFMEA** | Process | Manufacturing process analysis |
| **FMEA-MSR** | Monitoring & System Response | Diagnostic systems |

## Example Prompts

### Start a DFMEA
```
Create a DFMEA for a lithium battery pack. Focus on safety-critical
functions: cell containment, thermal runaway prevention, and BMS accuracy.
```

### Start a PFMEA
```
Build a PFMEA for our PCB assembly process. Key operations:
solder paste printing, component placement, reflow soldering, inspection.
```

### Evaluate Existing Failure Modes
```
Calculate Action Priority for these failure modes:
- Solder bridge (S=7, O=4, D=6)
- Missing component (S=8, O=3, D=8)
- Wrong polarity (S=9, O=2, D=7)
```

### Recommend Actions
```
My FMEA has 5 HIGH priority items. Help me develop corrective
actions for each and estimate revised ratings.
```

## AIAG-VDA 7-Step Methodology

| Step | Activity |
|------|----------|
| 1 | Planning & Preparation |
| 2 | Structure Analysis |
| 3 | Function Analysis |
| 4 | Failure Analysis |
| 5 | Risk Analysis (S, O, D → AP) |
| 6 | Optimization |
| 7 | Documentation |

## Risk Assessment

### Severity (S) - Effect on Customer
| Rating | Criteria |
|--------|----------|
| 10 | Safety - no warning |
| 9 | Safety - with warning, or regulatory |
| 8 | Loss of primary function |
| 7 | Degraded primary function |
| 5-6 | Loss/degradation of secondary function |
| 2-4 | Annoyance, appearance |
| 1 | No effect |

### Occurrence (O) - Likelihood
| Rating | Criteria |
|--------|----------|
| 10 | Very high (≥100 per 1000) |
| 7-9 | High (10-50 per 1000) |
| 4-6 | Moderate (1-10 per 1000) |
| 2-3 | Low (0.1-1 per 1000) |
| 1 | Very low (<0.01 per 1000) |

### Detection (D) - Likelihood of Detection Before Customer
| Rating | Criteria |
|--------|----------|
| 10 | No detection method |
| 7-9 | Low detection capability |
| 4-6 | Moderate detection |
| 2-3 | High detection (automated) |
| 1 | Almost certain detection |

### Action Priority (AP) - Replaces RPN

| Priority | Meaning | Action Required |
|----------|---------|-----------------|
| **HIGH** | Unacceptable risk | MUST improve controls |
| **MEDIUM** | Elevated risk | SHOULD improve or justify |
| **LOW** | Acceptable risk | COULD improve at discretion |

## Python Scripts

### Calculate AP for Failure Modes
```bash
python scripts/calculate_fmea.py --file fmea_data.json --mode all
```

### Interactive Calculator
```bash
python scripts/calculate_fmea.py --interactive
```

### Generate Risk Summary
```bash
python scripts/calculate_fmea.py --file fmea_data.json --mode summary
```

### Generate Report
```bash
python scripts/generate_report.py --file fmea_data.json --format html --output fmea_report.html
```

## Quality Checklist

- [ ] All functions identified (not just components)
- [ ] Failure modes are specific (not generic "fails")
- [ ] Effects include end customer impact
- [ ] Causes are root causes (not symptoms)
- [ ] Current controls documented
- [ ] Ratings are evidence-based (not guessed)
- [ ] All HIGH AP items have actions assigned
- [ ] Actions have owners and target dates

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Vague failure modes | "Motor fails" | Specify: "Motor overheats due to bearing seizure" |
| Component-focused | Misses functions | Start with functions, then failure modes |
| Optimistic ratings | Underestimates risk | Use historical data, be conservative |
| No current controls | Can't assess detection | Document what exists today |
| Actions without follow-up | Risk stays high | Track revised ratings after actions |

## Integration with Other Tools

- **Fishbone → FMEA**: Fishbone brainstorms causes, FMEA quantifies risk
- **FMEA → FTA**: FMEA identifies failures, FTA analyzes system-level propagation
- **FMEA → 8D**: High-severity field failures trigger 8D investigation

## Related Resources

- `references/rating-scales.md` - Detailed S/O/D criteria
- `references/ap-lookup-table.md` - Action Priority determination
- `references/fmea-examples/` - Worked examples by industry
- `templates/fmea-worksheet.xlsx` - Standard worksheet
