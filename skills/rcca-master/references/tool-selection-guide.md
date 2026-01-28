# Root Cause Analysis Tool Selection Guide

## Decision Tree

```
START → Is the likely cause known or strongly suspected?
  │
  ├─YES→ Use 5 Whys Analysis
  │       (Drill down the causal chain)
  │
  └─NO→ Are there many potential causes to consider?
        │
        ├─YES→ Is historical data available?
        │       │
        │       ├─YES→ Use Pareto Analysis first
        │       │       (Prioritize vital few causes)
        │       │       Then → Fishbone or 5 Whys
        │       │
        │       └─NO→ Use Fishbone Diagram
        │               (Brainstorm potential causes)
        │               Then → 5 Whys on top candidates
        │
        └─NO→ Is this safety-critical or catastrophic?
              │
              ├─YES→ Use Fault Tree Analysis
              │       (Systematic failure pathway analysis)
              │
              └─NO→ Is this a complex, multi-factor problem?
                    │
                    ├─YES→ Use Kepner-Tregoe Problem Analysis
                    │       (IS/IS NOT specification analysis)
                    │
                    └─NO→ Use Fishbone Diagram
                            Then → 5 Whys
```

---

## Tool Summaries

### 5 Whys Analysis
**Purpose**: Drill down a known or suspected causal chain to find root cause
**When to use**:
- Cause is known or strongly suspected
- Single causal thread to follow
- Quick analysis needed
- Relatively simple problems

**Skill**: `five-whys-analysis`

---

### Fishbone (Ishikawa) Diagram
**Purpose**: Brainstorm and organize potential causes by category
**When to use**:
- Cause is unknown
- Team brainstorming needed
- Multiple potential cause categories
- Need visual organization

**Categories**:
- Manufacturing: 6Ms (Man, Machine, Method, Material, Measurement, Mother Nature)
- Service: 8Ps (Product, Price, Place, Promotion, People, Process, Physical Evidence, Productivity)
- Generic: 4Ss (Surroundings, Suppliers, Systems, Skills)

**Skill**: `fishbone-diagram`

---

### Pareto Analysis
**Purpose**: Prioritize causes by frequency or impact (80/20 rule)
**When to use**:
- Historical data available
- Many defect types or causes
- Need to focus limited resources
- Quantitative prioritization needed

**Skill**: `pareto-analysis`

---

### Kepner-Tregoe Problem Analysis
**Purpose**: Systematic specification analysis using IS/IS NOT
**When to use**:
- Complex, multi-factor problems
- Need precise problem boundary
- Testing potential causes against specification
- Systematic elimination needed

**Skill**: `kepner-tregoe-analysis`

---

### Fault Tree Analysis
**Purpose**: Top-down deductive analysis of failure pathways
**When to use**:
- Safety-critical systems
- Catastrophic failure potential
- Probability calculations needed
- Regulatory requirements (aerospace, nuclear, medical)
- Redundancy assessment

**Skill**: `fault-tree-analysis`

---

## Combination Patterns

### Pattern 1: Unknown Cause, Limited Data
1. Fishbone → Brainstorm causes
2. Multi-voting → Prioritize candidates
3. 5 Whys → Drill down top candidates

### Pattern 2: Many Causes, Historical Data
1. Pareto → Identify vital few
2. 5 Whys → Drill down top causes
3. Verify with data

### Pattern 3: Complex Technical Problem
1. Kepner-Tregoe → Precise specification
2. Test hypotheses against IS/IS NOT
3. 5 Whys → Confirm root cause

### Pattern 4: Safety-Critical Investigation
1. Fault Tree → Map failure pathways
2. Calculate probabilities
3. Identify minimal cut sets
4. Design redundancy improvements
