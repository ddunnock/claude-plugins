# Pareto Analysis Category Guidelines

Best practices for defining effective categories that enable actionable Pareto Analysis.

## The MECE Principle

**M**utually **E**xclusive, **C**ollectively **E**xhaustive

### Mutually Exclusive
Each item can be classified into one and only one category.

**Good Example**:
- Category A: Defects detected at Station 1
- Category B: Defects detected at Station 2
- Category C: Defects detected at Station 3

**Bad Example** (overlapping):
- Category A: Operator errors
- Category B: Training issues ← Overlaps with operator errors
- Category C: Process failures ← May include operator errors

### Collectively Exhaustive
All possible items fit into at least one category.

**Good Example**:
- All defect types covered
- "Other" category for truly miscellaneous items (<5% of total)

**Bad Example**:
- Missing categories force items into "Other"
- "Other" becomes dominant category

---

## Category Design Principles

### 1. Actionable Level

Categories should be at a level where you can take direct action.

**Too High (not actionable)**:
```
"Equipment Problems" → What equipment? What kind of problem?
"Human Error" → Too broad to address
```

**Too Detailed (no patterns)**:
```
"Screw #47B missing from assembly" → One of 200 similar issues
```

**Just Right (actionable)**:
```
"Fastener missing - Assembly Station 3"
"Calibration drift - Torque tools"
```

### 2. Observable Symptoms, Not Assumed Causes

Categories should describe what you observe, not why you think it happened.

**Good (observable)**:
```
"Product arrived damaged"
"Label missing"
"Wrong item shipped"
```

**Bad (assumed cause)**:
```
"Poor packaging design" ← Assumes root cause
"Warehouse training gap" ← Assumes root cause
```

### 3. Consistent Abstraction Level

All categories should be at similar levels of specificity.

**Bad (mixed levels)**:
```
"Assembly defects" (high level)
"Paint scratches" (medium level)
"Screw #12 missing from left panel" (very detailed)
```

**Good (consistent)**:
```
"Assembly defects - fasteners"
"Assembly defects - alignment"
"Cosmetic defects - paint"
"Cosmetic defects - finish"
```

---

## Recommended Category Count

| Situation | Category Count | Rationale |
|-----------|----------------|-----------|
| Initial analysis | 5-8 | Enough to see patterns, not overwhelming |
| Detailed follow-up | 8-12 | Drilling into a top category |
| Maximum practical | 10-12 | Beyond this, consider rolling up |

**If you have more than 12 categories:**
- Consider grouping related categories
- Create hierarchical categories (primary → secondary)
- Use nested Pareto (drill into top category)

**If you have fewer than 5 categories:**
- May be too high-level for action
- Consider splitting large categories
- Check if categories are truly distinct

---

## The "Other" Category

### Guidelines

- Keep "Other" below 10% of total (ideally <5%)
- "Other" should never be a top-3 contributor
- Document what falls into "Other"
- Review "Other" periodically for emerging patterns

### When "Other" is Too Large

1. Review raw data in "Other"
2. Look for recurring themes (3+ occurrences)
3. Create new categories for themes
4. Re-categorize historical data
5. Update data collection forms

### Legitimate Uses of "Other"

- True one-off events
- Transitional items pending new categories
- Combined tail of many truly minor items

---

## Category Definition Template

For each category, document:

```
Category Name: [Clear, concise name]

Definition: [What this category includes]

Includes:
- [Specific example 1]
- [Specific example 2]
- [Specific example 3]

Excludes (belongs in other category):
- [Example that might be confused] → Goes to [other category]

Decision Rule for Borderline Cases:
[How to classify ambiguous items]
```

**Example**:

```
Category Name: Packaging Damage - Transit

Definition: Product damage that occurred during shipping,
evidenced by external package damage.

Includes:
- Crushed boxes with product damage inside
- Water damage from weather exposure
- Puncture damage from handling equipment

Excludes:
- Damage with intact packaging → "Manufacturing Defect"
- Damage from incorrect packaging → "Packaging Process"

Decision Rule:
If external packaging shows damage AND product inside is damaged,
classify as "Packaging Damage - Transit"
```

---

## Common Category Frameworks by Domain

### Manufacturing (Product Defects)

```
Primary Categories:
- Assembly defects
- Material defects
- Process defects
- Cosmetic defects
- Dimensional defects
- Functional defects
```

### Customer Service (Complaints)

```
Primary Categories:
- Product quality
- Delivery issues
- Service experience
- Pricing/billing
- Communication
- Returns/refunds
```

### IT Operations (Incidents)

```
Primary Categories:
- Hardware failures
- Software bugs
- Network issues
- Security events
- User errors
- Configuration problems
```

### Healthcare (Patient Safety)

```
Primary Categories:
- Medication events
- Falls
- Infections
- Documentation errors
- Equipment issues
- Communication failures
```

### Project Management (Delays)

```
Primary Categories:
- Resource constraints
- Scope changes
- Dependencies
- Technical issues
- External factors
- Decision delays
```

---

## Category Validation Checklist

Before finalizing categories, verify:

- [ ] Each category has a clear, documented definition
- [ ] Categories are mutually exclusive (MECE)
- [ ] Categories are collectively exhaustive (everything fits)
- [ ] All categories at consistent abstraction level
- [ ] Categories describe symptoms, not assumed causes
- [ ] Each category is actionable
- [ ] Category count is 5-12
- [ ] "Other" is <10% of expected volume
- [ ] Data collectors understand and can apply definitions
- [ ] Decision rules exist for borderline cases

---

## Iterating on Categories

Categories may need refinement after initial analysis:

### When to Combine Categories
- Two categories always occur together
- Combined they're still actionable
- Separation doesn't add insight

### When to Split Categories
- Category dominates (>40%) but needs root cause detail
- Subcategories would drive different actions
- "Vital few" needs drilling down

### When to Create New Categories
- "Other" exceeds 10%
- Recurring pattern in "Other"
- New problem type emerges

### Documentation When Changing Categories
- Preserve original data with original categories
- Create mapping from old to new
- Note effective date of change
- Re-run historical analysis with new categories if needed
