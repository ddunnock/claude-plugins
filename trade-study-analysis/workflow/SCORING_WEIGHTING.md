# Scoring & Weighting Workflow

Workflow guide for Steps 4-7 of the DAU 9-Step Trade Study Process.

---

## MANDATORY BEHAVIORAL REQUIREMENTS

**This phase CANNOT proceed without:**
1. Confirmed data collection from Phase 3
2. User selection of weighting method
3. User confirmation of all weight assignments
4. User selection of normalization method
5. User selection of scoring function

**PROHIBITED:**
- Suggesting "recommended" weights without user input
- Auto-selecting normalization methods based on data characteristics
- Applying scoring functions without explicit user approval
- Making judgments about criteria importance

---

## Phase 1: Weight Assignment Method Selection

### MANDATORY — User must select weighting approach

```
═══════════════════════════════════════════════════════════════════════════════
❓ WEIGHT ASSIGNMENT — Method Selection
═══════════════════════════════════════════════════════════════════════════════

Criteria weights determine relative importance. I need you to select a method.

───────────────────────────────────────────────────────────────────────────────
AVAILABLE METHODS:
───────────────────────────────────────────────────────────────────────────────

  [A] DIRECT ASSIGNMENT
      You directly specify each weight (must sum to 1.0 or 100%)
      Best for: When you have clear priorities
      
  [B] RANK ORDER CENTROID (ROC)
      You rank criteria by importance; weights are calculated
      Best for: When you know relative order but not exact weights
      
  [C] POINT ALLOCATION
      You distribute 100 points across criteria
      Best for: Intuitive allocation when exact weights are unclear
      
  [D] ANALYTIC HIERARCHY PROCESS (AHP)
      Pairwise comparison of criteria importance
      Best for: Rigorous, defensible weight derivation
      Note: Requires [N*(N-1)/2] comparisons for [N] criteria

───────────────────────────────────────────────────────────────────────────────
QUESTION 1: Which weighting method do you want to use?

Your selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 2: Do you have documented rationale for weights?

  [A] Yes — Weights are derived from requirements document
      Source: _______________________________________________
  [B] Yes — Weights are based on stakeholder input
      Source: _______________________________________________
  [C] No — I will assign weights based on my judgment
      ⚠️  This will be logged as methodology assumption

Your selection: _______________________________________________

⚠️  I will NOT proceed until you select a weighting method.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 2A: Direct Weight Assignment

### MANDATORY — User must provide and confirm each weight

```
═══════════════════════════════════════════════════════════════════════════════
⚖️  DIRECT WEIGHT ASSIGNMENT
═══════════════════════════════════════════════════════════════════════════════

Assign a weight to each criterion. Weights must sum to 1.0 (or 100%).

───────────────────────────────────────────────────────────────────────────────
WEIGHT ENTRY:
───────────────────────────────────────────────────────────────────────────────

CRITERION: [Criterion 1 Name]
  Description: [description]
  Weight (0.0 - 1.0): _______________________________________________
  Rationale for this weight: _______________________________________________
  Source (if documented): _______________________________________________

CRITERION: [Criterion 2 Name]
  Description: [description]
  Weight (0.0 - 1.0): _______________________________________________
  Rationale for this weight: _______________________________________________
  Source (if documented): _______________________________________________

[Repeat for all criteria]

───────────────────────────────────────────────────────────────────────────────
WEIGHT VALIDATION:

  Total assigned: [X.XX]
  Required total: 1.00
  Status: [VALID / INVALID - must adjust]

⚠️  I will NOT proceed until weights sum to 1.0 and you confirm.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 2B: AHP Pairwise Comparison

### MANDATORY — User must complete ALL pairwise comparisons

```
═══════════════════════════════════════════════════════════════════════════════
⚖️  AHP PAIRWISE COMPARISON — [X] of [Y]
═══════════════════════════════════════════════════════════════════════════════

Compare the relative importance of these two criteria:

  CRITERION A: [Criterion Name A]
  CRITERION B: [Criterion Name B]

───────────────────────────────────────────────────────────────────────────────
COMPARISON SCALE:
───────────────────────────────────────────────────────────────────────────────

  9 = A is EXTREMELY more important than B
  7 = A is VERY STRONGLY more important than B
  5 = A is STRONGLY more important than B
  3 = A is MODERATELY more important than B
  1 = A and B are EQUALLY important
  1/3 = B is MODERATELY more important than A
  1/5 = B is STRONGLY more important than A
  1/7 = B is VERY STRONGLY more important than A
  1/9 = B is EXTREMELY more important than A

───────────────────────────────────────────────────────────────────────────────
QUESTION: How does [Criterion A] compare to [Criterion B]?

Your rating (9, 7, 5, 3, 1, 1/3, 1/5, 1/7, or 1/9): _______________

Rationale for this comparison: _______________________________________________

Source (if documented): _______________________________________________

⚠️  I will NOT proceed to the next comparison until you respond.
═══════════════════════════════════════════════════════════════════════════════
```

### AHP Consistency Check — MANDATORY review if CR > 0.10

```
═══════════════════════════════════════════════════════════════════════════════
⚠️  AHP CONSISTENCY WARNING
═══════════════════════════════════════════════════════════════════════════════

Your pairwise comparisons have a Consistency Ratio (CR) of [X.XX].

  CR threshold: 0.10
  Your CR: [X.XX]
  Status: [ACCEPTABLE / INCONSISTENT]

───────────────────────────────────────────────────────────────────────────────
INCONSISTENCY DETECTED:

The following comparisons appear inconsistent:
  • [Criterion A] vs [Criterion B]: You rated [X]
  • [Criterion B] vs [Criterion C]: You rated [Y]
  • [Criterion A] vs [Criterion C]: You rated [Z]
  
  These imply conflicting relative importances.

───────────────────────────────────────────────────────────────────────────────
QUESTION: How do you want to proceed?

  [A] REVISE COMPARISONS — I'll adjust my ratings
  [B] ACCEPT ANYWAY — Use these weights despite inconsistency
      ⚠️  This will be logged as ASSUMPTION A-[XXX]
  [C] SWITCH METHODS — Use a different weighting approach

Your selection: _______________________________________________

⚠️  I will NOT proceed until you address the consistency issue.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 3: Weight Confirmation

### MANDATORY — User must explicitly approve final weights

```
═══════════════════════════════════════════════════════════════════════════════
✓ WEIGHT ASSIGNMENT — Confirmation Required
═══════════════════════════════════════════════════════════════════════════════

DERIVED WEIGHTS:

| Criterion | Weight | Rationale | Source |
|-----------|--------|-----------|--------|
| [C1]      | [0.XX] | [reason]  | [src]  |
| [C2]      | [0.XX] | [reason]  | [src]  |
| [C3]      | [0.XX] | [reason]  | [src]  |
| ...       | ...    | ...       | ...    |
| TOTAL     | 1.00   |           |        |

───────────────────────────────────────────────────────────────────────────────
METHOD USED: [Direct / ROC / Point Allocation / AHP]
CONSISTENCY (if AHP): CR = [X.XX]

───────────────────────────────────────────────────────────────────────────────
ASSUMPTIONS IN WEIGHT ASSIGNMENT:
───────────────────────────────────────────────────────────────────────────────

  A-[XXX]: [Description] — Status: PENDING
  A-[XXX]: [Description] — Status: PENDING

───────────────────────────────────────────────────────────────────────────────
CONFIRMATION REQUIRED:

  [A] APPROVE — These weights are correct
  [B] ADJUST — I want to change these weights: _______________________
  [C] RESTART — Use a different weighting method

Your selection: _______________________________________________

⚠️  I will NOT proceed to normalization until you approve weights.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 4: Normalization Method Selection

### MANDATORY — User must select normalization approach

```
═══════════════════════════════════════════════════════════════════════════════
❓ NORMALIZATION — Method Selection
═══════════════════════════════════════════════════════════════════════════════

Raw data must be normalized for comparison. I need you to select a method.

───────────────────────────────────────────────────────────────────────────────
DATA CHARACTERISTICS (for your reference):
───────────────────────────────────────────────────────────────────────────────

| Criterion | Min Value | Max Value | Range | Order of Magnitude |
|-----------|-----------|-----------|-------|-------------------|
| [C1]      | [min]     | [max]     | [rng] | [10^X]            |
| [C2]      | [min]     | [max]     | [rng] | [10^X]            |
| ...       | ...       | ...       | ...   | ...               |

───────────────────────────────────────────────────────────────────────────────
AVAILABLE METHODS:
───────────────────────────────────────────────────────────────────────────────

  [A] MIN-MAX NORMALIZATION
      Formula: (x - min) / (max - min)
      Output range: [0, 1]
      Use when: Bounds are known and meaningful
      
  [B] Z-SCORE NORMALIZATION
      Formula: (x - mean) / std_dev
      Output range: Unbounded (typically -3 to +3)
      Use when: Comparing relative positions
      
  [C] LOGARITHMIC NORMALIZATION
      Formula: log(x) / log(max)
      Output range: [0, 1]
      Use when: Values span multiple orders of magnitude
      
  [D] PERCENTILE RANK
      Formula: rank / n
      Output range: [0, 1]
      Use when: Relative ranking matters more than absolute values

───────────────────────────────────────────────────────────────────────────────
QUESTION 1: Which normalization method do you want to use?

  [A] Use ONE method for all criteria: _______________
  [B] Use DIFFERENT methods per criterion (specify below)

Your selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 2 (if different methods): Specify method per criterion

| Criterion | Method | Rationale |
|-----------|--------|-----------|
| [C1]      | [A/B/C/D] | _______ |
| [C2]      | [A/B/C/D] | _______ |

───────────────────────────────────────────────────────────────────────────────
QUESTION 3: For criteria where "lower is better" (minimize), confirm direction:

| Criterion | Direction | Confirm |
|-----------|-----------|---------|
| [C1]      | Maximize  | [Y/N]   |
| [C2]      | Minimize  | [Y/N]   |

⚠️  I will NOT proceed until you confirm normalization method and directions.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 5: Scoring Function Selection

### MANDATORY — User must select scoring approach

```
═══════════════════════════════════════════════════════════════════════════════
❓ SCORING FUNCTION — Selection Required
═══════════════════════════════════════════════════════════════════════════════

After normalization, scores can be transformed using scoring functions.

───────────────────────────────────────────────────────────────────────────────
AVAILABLE SCORING FUNCTIONS:
───────────────────────────────────────────────────────────────────────────────

  [A] LINEAR (Default)
      Score = Normalized value (no transformation)
      Use when: Proportional relationship between value and utility
      
  [B] STEP FUNCTION
      Score = Discrete levels based on thresholds
      Use when: Pass/fail or tiered requirements
      Requires: You specify threshold values
      
  [C] EXPONENTIAL
      Score = base^(normalized value)
      Use when: Increasing/decreasing marginal utility
      Requires: You specify base value
      
  [D] SIGMOID (S-CURVE)
      Score = 1 / (1 + e^(-k*(x-midpoint)))
      Use when: Diminishing returns at extremes
      Requires: You specify midpoint and steepness
      
  [E] PIECEWISE LINEAR
      Score = Different slopes in different regions
      Use when: Non-linear but interpretable relationship
      Requires: You specify breakpoints and slopes

───────────────────────────────────────────────────────────────────────────────
QUESTION 1: Which scoring function do you want to use?

  [A] Use LINEAR for all criteria (most common)
  [B] Use DIFFERENT functions per criterion (specify below)

Your selection: _______________________________________________

───────────────────────────────────────────────────────────────────────────────
QUESTION 2 (if Step Function selected): Specify thresholds

For criterion [Name]:
  Threshold 1 (score = 0): value < _______________
  Threshold 2 (score = 0.5): value < _______________
  Threshold 3 (score = 1.0): value >= _______________
  
Source for thresholds: _______________________________________________

[Repeat for each criterion using step function]

⚠️  I will NOT proceed until you confirm scoring function selection.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 6: Aggregation Method Selection

### MANDATORY — User must select aggregation approach

```
═══════════════════════════════════════════════════════════════════════════════
❓ AGGREGATION METHOD — Selection Required
═══════════════════════════════════════════════════════════════════════════════

How should criterion scores be combined into overall alternative scores?

───────────────────────────────────────────────────────────────────────────────
AVAILABLE METHODS:
───────────────────────────────────────────────────────────────────────────────

  [A] WEIGHTED SUM (Most common)
      Formula: Σ(weight_i × score_i)
      Properties: Compensatory (high score can offset low score)
      
  [B] WEIGHTED PRODUCT
      Formula: Π(score_i ^ weight_i)
      Properties: Less compensatory than weighted sum
      
  [C] TOPSIS
      Formula: Distance from ideal/anti-ideal solutions
      Properties: Considers both best and worst cases

───────────────────────────────────────────────────────────────────────────────
QUESTION: Which aggregation method do you want to use?

Your selection: _______________________________________________

Rationale (optional): _______________________________________________

⚠️  I will NOT proceed until you select an aggregation method.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 7: Scoring Results Confirmation

### MANDATORY — User must review and approve results

```
═══════════════════════════════════════════════════════════════════════════════
✓ SCORING RESULTS — Confirmation Required
═══════════════════════════════════════════════════════════════════════════════

DECISION MATRIX:

| Criterion | Weight | Alt 1 | Alt 2 | Alt 3 |
|-----------|--------|-------|-------|-------|
| [C1]      | [w1]   | [s1a] | [s1b] | [s1c] |
| [C2]      | [w2]   | [s2a] | [s2b] | [s2c] |
| ...       | ...    | ...   | ...   | ...   |
|-----------|--------|-------|-------|-------|
| WEIGHTED TOTAL     | [T1]  | [T2]  | [T3]  |
| RANK               | [R1]  | [R2]  | [R3]  |

───────────────────────────────────────────────────────────────────────────────
METHODOLOGY SUMMARY:
───────────────────────────────────────────────────────────────────────────────

  Weighting method: [method]
  Normalization: [method(s)]
  Scoring function: [function(s)]
  Aggregation: [method]

───────────────────────────────────────────────────────────────────────────────
SOURCE GROUNDING FOR RESULTS:
───────────────────────────────────────────────────────────────────────────────

  Data points with High confidence: [N]%
  Data points with Medium confidence: [N]%
  Data points with Low confidence: [N]%
  Data gaps addressed via assumptions: [N]

───────────────────────────────────────────────────────────────────────────────
ASSUMPTIONS IN SCORING:
───────────────────────────────────────────────────────────────────────────────

  A-[XXX]: [Description] — Status: PENDING
  A-[XXX]: [Description] — Status: PENDING

───────────────────────────────────────────────────────────────────────────────
CONFIRMATION REQUIRED:

  [A] APPROVE — Results are correct, proceed to sensitivity analysis
  [B] ADJUST — I need to change: _______________________
  [C] REVIEW DATA — Go back to data collection
  [D] REVIEW WEIGHTS — Go back to weight assignment

Your selection: _______________________________________________

⚠️  I will NOT proceed to sensitivity analysis until you approve results.
═══════════════════════════════════════════════════════════════════════════════
```

---

## Prohibited Behaviors in This Workflow

| ❌ DO NOT | ✅ INSTEAD |
|-----------|-----------|
| Suggest weights are "appropriate" or "reasonable" | Present options and wait for user assignment |
| Auto-select normalization based on data shape | Ask user to select method explicitly |
| Apply scoring functions without parameters | Ask user for all required parameters |
| Recommend aggregation methods | Present options and wait for selection |
| Interpret what "higher priority" means | Ask for explicit numerical weight |
| Assume linear scoring is default | Ask user to confirm linear or select alternative |
| Skip consistency check for AHP | Always report CR and require action if > 0.10 |
