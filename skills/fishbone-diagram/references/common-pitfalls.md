# Common Fishbone Diagram Pitfalls

## Pitfall 1: Vague Problem Statement

### Symptom
Problem statement is too broad, abstract, or undefined to guide focused analysis.

### Examples
❌ "Quality is poor"
❌ "Customers are unhappy"
❌ "Production is slow"
❌ "Things aren't working"

### Why It Matters
Vague problems lead to vague causes. Teams will generate generic causes that don't point to actionable improvements.

### Redirection Strategy
Apply 5W2H to sharpen the problem:
- **What** specifically is happening?
- **Where** is it occurring?
- **When** does it happen?
- **How much** (frequency, quantity, impact)?

### Corrected Examples
✅ "Widget A dimensional variance exceeds ±0.05mm on 15% of units from Line 3"
✅ "Customer hold time averages 12 minutes, target is <3 minutes"
✅ "Order fulfillment takes 5 days vs. 2-day SLA"

---

## Pitfall 2: Stopping at Symptoms

### Symptom
Causes identified are actually just restating the problem or describing symptoms rather than underlying factors.

### Examples
❌ Problem: "Machine downtime"
   Cause: "Machine stopped working" (restates problem)

❌ Problem: "High defect rate"
   Cause: "Parts are defective" (restates problem)

### Why It Matters
Addressing symptoms provides temporary relief but problems recur. True root causes remain hidden.

### Redirection Strategy
For each cause, ask "Why might this happen?" at least twice:
1. "Machine stopped" → "Why?" → "Bearing failure"
2. "Bearing failure" → "Why?" → "Lack of lubrication"
3. "Lack of lubrication" → "Why?" → "No PM schedule for this equipment"

### Quality Test
Can you take action on this cause? If yes, it's likely actionable. If no, dig deeper.

---

## Pitfall 3: Empty or Thin Categories

### Symptom
One or more categories have few or no causes identified.

### Examples
- "Measurement" category left blank in a quality analysis
- "Environment" category has only 1 generic cause
- Team says "That doesn't apply to us"

### Why It Matters
Empty categories often indicate blind spots. The category framework exists specifically to prompt consideration of areas teams might overlook.

### Redirection Strategy
Use category-specific prompting questions (see `category-frameworks.md`):
- "Have there been any recent changes in [Category]?"
- "What could go wrong in [Category] that would cause this problem?"
- "If this happened at a competitor, what [Category] issue might cause it?"

Force at least 2-3 causes per category before concluding it's not relevant.

---

## Pitfall 4: Person-Blame

### Symptom
Causes focus on individual people rather than systems, processes, or conditions.

### Examples
❌ "John made a mistake"
❌ "Operator error"
❌ "Supervisor didn't catch it"
❌ "New employee didn't know"

### Why It Matters
Blaming individuals:
- Doesn't prevent recurrence (another person can make same error)
- Damages team morale and psychological safety
- Misses systemic improvement opportunities
- Usually masks process/system deficiencies

### Redirection Strategy
Ask: "What process, system, or condition allowed this error to occur/go undetected?"

Transform person-blame to system-focus:
- "John made a mistake" → "No error-proofing in assembly step"
- "Operator error" → "Unclear work instructions"
- "New employee didn't know" → "Inadequate onboarding training"

### Principle
**Assume competent people trying to do good work.** If they fail, the system failed them.

---

## Pitfall 5: Groupthink

### Symptom
Team quickly converges on a few "obvious" causes, often confirming existing beliefs. Few alternative explanations explored.

### Signs
- Rapid agreement ("Yeah, that's definitely it")
- No dissenting views
- Senior person's ideas dominate
- Causes match prior assumptions

### Why It Matters
Groupthink leads to confirmation bias. Real root causes may be overlooked if they challenge existing beliefs or implicate powerful stakeholders.

### Redirection Strategy
1. **Use brainwriting first** - Silent individual brainstorming before discussion
2. **Assign devil's advocate** - Someone to challenge each cause
3. **Ask**: "What would we expect to see if this cause were true?" (then check data)
4. **Rotate facilitation** - Person with least seniority leads discussion
5. **Anonymous voting** - For prioritization

---

## Pitfall 6: Confirmation Bias

### Symptom
Team only identifies causes that confirm what they already believe, ignoring evidence that contradicts.

### Examples
- Engineering blames operations; operations blames engineering
- "It's always the supplier" (without checking data)
- Ignoring recent changes because "that couldn't be it"

### Why It Matters
Leads to solving the wrong problem. Resources wasted, problem persists.

### Redirection Strategy
1. **Seek disconfirming evidence**: "What evidence would prove this cause is NOT the issue?"
2. **Check data before prioritizing**: Verify assumed causes with actual data
3. **Include outsiders**: Fresh eyes without institutional biases
4. **List recent changes**: Often overlooked because "we already ruled that out"

---

## Pitfall 7: Insufficient Depth

### Symptom
Diagram is flat - many Level 1 causes but no sub-causes (Level 2/3).

### Examples
```
Machine
├── Equipment failure (no sub-causes)
├── Old equipment (no sub-causes)
└── Wrong tool (no sub-causes)
```

### Why It Matters
Level 1 causes are often symptoms or intermediate causes. Actionable root causes typically appear at Level 2 or 3.

### Redirection Strategy
For each major cause, ask "Why might this happen?" at least twice:
```
Machine
├── Equipment failure
│   ├── Bearing failure
│   │   ├── Lack of lubrication
│   │   └── Contamination
│   └── Motor overheating
│       ├── Blocked ventilation
│       └── Excessive load
```

**Target**: At least 2-3 sub-cause levels for major causes.

---

## Pitfall 8: Excessive Complexity

### Symptom
Diagram becomes overwhelming with hundreds of causes, multiple overlapping branches, and no clear focus.

### Why It Matters
- Analysis paralysis - too many causes to investigate
- Key causes buried in noise
- Loses visual clarity advantage
- Team exhaustion and disengagement

### Redirection Strategy
1. **Split into multiple diagrams**: One per major symptom or subsystem
2. **Focus on one process step**: Narrow scope to specific point of failure
3. **Time-box brainstorming**: Stop at 60 minutes, consolidate
4. **Merge duplicates**: Similar causes appearing in multiple categories
5. **Prioritize early**: Use multi-voting before adding more detail

---

## Pitfall 9: No Verification Plan

### Symptom
Causes are identified and prioritized, but no plan to verify whether they're actually contributing to the problem.

### Why It Matters
Fishbone generates hypotheses, not conclusions. Without verification, teams may implement countermeasures for non-causes while real causes persist.

### Redirection Strategy
For each prioritized cause, establish:
1. **Verification method**: How will we confirm/refute this cause?
   - Data analysis (defect logs, trends)
   - Observation (watch the process)
   - Experimentation (change variable, measure result)
   - Interview (talk to process owners)
2. **Owner**: Who will investigate?
3. **Timeline**: When will we have an answer?
4. **Criteria**: What evidence would confirm/refute?

---

## Pitfall 10: Solutions Masquerading as Causes

### Symptom
Items on the fishbone are actually proposed solutions rather than causes.

### Examples
❌ "Need more training" (solution)
❌ "Should automate" (solution)
❌ "Require double-check" (solution)

### Why It Matters
Embedding solutions in cause analysis:
- Skips understanding the actual cause
- May implement wrong solution
- Closes off better alternatives

### Redirection Strategy
Reframe as causes:
- "Need more training" → "Inadequate training program" or "Skill gaps"
- "Should automate" → "Manual process is error-prone"
- "Require double-check" → "No verification step in process"

**Test**: Does this describe a current state (cause) or a future state (solution)?

---

## Summary: Quality Checks Before Concluding

Before finalizing the fishbone diagram, verify:

| Check | Question | Action if Failed |
|-------|----------|------------------|
| Problem clarity | Is it specific, measurable, observable? | Apply 5W2H |
| Category coverage | Every category has 2+ causes? | Use prompting questions |
| Depth | Major causes have 2-3 sub-levels? | Ask "Why?" twice more |
| System focus | Causes are process/system issues, not people? | Reframe person-blame |
| Diversity | Multiple perspectives represented? | Use brainwriting |
| Evidence basis | Data supports or could verify causes? | Plan verification |
| Actionability | Can we do something about these causes? | Dig deeper if too abstract |
| Prioritization | Top causes identified and ranked? | Use multi-voting |
