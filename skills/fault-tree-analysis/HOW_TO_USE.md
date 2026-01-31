# How to Use: Fault Tree Analysis

The Fault Tree Analysis (FTA) skill conducts systematic top-down deductive analysis of system failures using Boolean logic gates, minimal cut sets, and probability calculations.

## When to Use This Skill

- Safety-critical system analysis
- Complex system failure investigation
- When multiple failure paths exist
- Reliability engineering studies
- Regulatory compliance (aerospace, nuclear, medical)
- Understanding failure propagation

## Quick Start

Describe your top event (undesired outcome) and request FTA:

```
Help me build a fault tree for: "Complete loss of braking
capability in the vehicle."
```

## Key Concepts

### Top Event
The undesired outcome you're analyzing (placed at top of tree).

### Gates
- **AND Gate (∧)**: All inputs must occur for output
- **OR Gate (∨)**: Any input can cause output

### Basic Events
Lowest level events that cannot be further decomposed (leaf nodes).

### Minimal Cut Sets
Smallest combinations of basic events that cause the top event.

## Example Prompts

### Build a Fault Tree
```
Create a fault tree for "Server cluster unavailability."
We have 3 servers with shared storage and network.
```

### Calculate Probabilities
```
Given these basic event probabilities, calculate the top event
probability:
- Pump A fails: 0.001
- Pump B fails: 0.001
- Power loss: 0.0001
- Control system failure: 0.0005
[Provide tree structure]
```

### Find Minimal Cut Sets
```
Identify the minimal cut sets for this fault tree:
[Provide tree structure]
```

### Evaluate Redundancy
```
Our system has redundant pumps (A and B) with a common power supply.
Is this truly redundant? Build the fault tree to analyze.
```

## Tree Structure Example

```
         ┌─────────────────┐
         │   TOP EVENT     │
         │ System Failure  │
         └────────┬────────┘
                  │
             ┌────┴────┐
             │   OR    │
             └────┬────┘
           ┌──────┼──────┐
           │      │      │
      ┌────┴──┐ ┌─┴─┐ ┌──┴────┐
      │  AND  │ │ E3│ │  AND  │
      └───┬───┘ └───┘ └───┬───┘
        ┌─┴─┐           ┌─┴─┐
       E1   E2         E4   E5
```

**Cut Sets**: {E3}, {E1, E2}, {E4, E5}

## Analysis Phases

| Phase | Activity | Output |
|-------|----------|--------|
| 1 | Define top event | Clear undesired outcome |
| 2 | Construct tree | Gates and events |
| 3 | Qualitative analysis | Minimal cut sets |
| 4 | Quantitative analysis | Probabilities (if data available) |
| 5 | Evaluate results | Identify vulnerabilities |
| 6 | Document | Report with recommendations |

## Python Scripts

### Generate Tree Diagram (SVG)
```bash
python scripts/generate_tree.py --file ft_data.json --output fault_tree.svg
```

### Calculate Minimal Cut Sets
```bash
python scripts/calculate_cutsets.py --file ft_data.json
```

### Calculate Top Event Probability
```bash
python scripts/calculate_probability.py --file ft_data.json
```

### Generate Report
```bash
python scripts/generate_report.py --file ft_data.json --format html --output report.html
```

## Common Patterns

### Redundancy Analysis
```
AND gate with parallel components = true redundancy
OR gate reveals single points of failure
```

### Common Cause Failures
Watch for:
- Shared power supplies
- Common software
- Same maintenance crew
- Environmental factors affecting multiple components

## Quality Checklist

- [ ] Top event is clearly defined
- [ ] Tree is logically complete (no gaps)
- [ ] Basic events are truly basic (can't decompose further)
- [ ] Gate logic is correct (AND vs OR)
- [ ] Common cause failures identified
- [ ] Cut sets are minimal (no redundant events)

## Interpretation Guidelines

| Cut Set Order | Meaning | Priority |
|---------------|---------|----------|
| 1st order (single event) | Single point of failure | Critical - eliminate |
| 2nd order (2 events) | Dual failure required | High - add redundancy |
| 3rd+ order | Multiple failures needed | Lower - often acceptable |

## When to Use FTA vs Other Tools

| Use FTA When | Use Alternatives When |
|--------------|----------------------|
| System-level analysis | Process problems (→ Fishbone) |
| Safety-critical | Simple cause-effect (→ 5 Whys) |
| Quantitative probability needed | Prioritizing categories (→ Pareto) |
| Regulatory requirement | Design risk assessment (→ FMEA) |

## Related Resources

- `references/gate-types.md` - AND, OR, and special gates
- `references/probability-math.md` - Calculation methods
- `references/common-cause-analysis.md` - CCF identification
- `assets/tree-template.svg` - Blank template
