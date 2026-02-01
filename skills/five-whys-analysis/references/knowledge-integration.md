# Knowledge Integration Reference

## Overview

This document describes how five-whys-analysis integrates with knowledge-mcp for standards-grounded root cause validation during iterative Why analysis.

The integration enables the skill to:
- Validate proposed root causes against documented failure patterns
- Query root cause catalogs from AIAG-VDA, ISO 26262, MIL-STD-882
- Provide confidence levels (High/Medium/Low) for pattern matches
- Inherit severity and problem context from Problem Definition skill
- Gracefully degrade when MCP is unavailable (using embedded patterns)

## MCP Tool Interface

### knowledge_search

Query the knowledge base for root cause patterns and failure mechanisms.

**Input Schema**:
```json
{
  "query": "string (required)",
  "n_results": "integer (default: 5)",
  "filter_dict": {
    "domain": "rcca",
    "standard_family": "root_cause_analysis | fmea | safety"
  }
}
```

**Output Format**:
```json
{
  "query": "root cause pattern inadequate process control",
  "results": [
    {
      "citation": "AIAG-VDA FMEA Handbook (2019), Section 4.3.2",
      "content": "Process control failures include: lack of SPC...",
      "relevance": "91%",
      "metadata": {
        "domain": "rcca",
        "standard": "AIAG-VDA",
        "category": "process_control"
      }
    }
  ],
  "count": 5
}
```

**Tool Availability Check**:
Check MCP availability ONCE at 5 Whys session start:
```python
if "knowledge_search" in available_tools:
    standards_mode = True
    display_connected_banner()
else:
    standards_mode = False
    display_unavailable_banner()
```

## 5 Whys-Specific Query Patterns

### Root Cause Validation Queries

| Cause Category | Query Pattern | Expected Sources |
|---------------|---------------|------------------|
| Process control | "root cause pattern process control variation" | AIAG-VDA Section 4.3 |
| Equipment failure | "common causes equipment machine failure" | AIAG-VDA, ISO 26262 |
| Material defect | "root cause material variation supplier quality" | AIAG-VDA |
| Human error | "systematic failure human factors procedure" | ISO 26262-9 |
| Design deficiency | "design failure mode inadequate validation" | AIAG-VDA, MIL-STD-882 |
| Calibration | "measurement calibration root cause" | AIAG-VDA, ISO 17025 |

**Query construction:**
```
Query: "root cause pattern [answer from Why iteration] failure mechanism common causes"
Filter: {"domain": "rcca"} or {"domain": "fmea"}
n_results: 5 (show top 3 matches with confidence)
```

### Trigger Point

Offer root cause validation AFTER each "Why" answer is recorded:
- User has provided an answer to "Why did [X] occur?"
- Answer recorded verbatim
- Standard validation questions completed (fact vs assumption, logical flow)
- Natural segue: "Would you like me to validate this against documented patterns?"

**Query frequency:**
- Offer at every iteration (different causes may benefit)
- If user declines 3+ times consecutively, stop offering
- User can always invoke `/lookup-standard` manually

## Confidence Level Assessment

### Determining Confidence

Based on relevance score and semantic match quality:

| Relevance | Confidence | Interpretation |
|-----------|------------|----------------|
| >=90% | High | Strong match to documented pattern |
| 70-89% | Medium | Partial match, related factors may apply |
| <70% | Low | Weak match, may be novel or needs refinement |

### Confidence Response Templates

**High Confidence (>=90%):**
```markdown
**High confidence match**

This matches documented pattern: "[pattern name]"
(AIAG-VDA FMEA Handbook (2019), Section X.Y)

Common related causes from standards:
- [Related cause 1]
- [Related cause 2]
- [Related cause 3]

This is a recognized root cause pattern. Consider if any related factors apply.
```

**Medium Confidence (70-89%):**
```markdown
**Medium confidence match**

Partial match to documented patterns in [Standard Section]:
- [Matching pattern 1]
- [Matching pattern 2]

Consider these related factors:
- [Suggested factor 1]
- [Suggested factor 2]

You may want to explore another "Why" level to strengthen the causal link.
```

**Low Confidence (<70%):**
```markdown
**Low confidence match**

No exact match found for "[answer]" in documented root cause patterns.

This could indicate:
- Novel root cause (not previously documented in standards)
- Opportunity to explore another "Why" level
- Need to refine the causal statement

Recommendations:
1. Consider another Why level or alternative cause paths
2. Search related terms: [suggested queries]
3. Continue with this cause if supported by strong evidence/expertise
```

## Citation Formatting

### Standard Format

Format all citations inline within root cause documentation:

- **Full format:** "This matches pattern X (AIAG-VDA FMEA Handbook (2019), Section 4.3.2)"
- **ISO format:** "Per ISO 26262-9 Section 8.4.3, systematic failures require..."
- **Section only (no page numbers):** Pages vary by edition

### Examples in 5 Whys Outputs

**Root Cause with Citation:**
```markdown
**Root Cause (Why #5):** Calibration procedure did not specify environmental conditions

Per AIAG-VDA FMEA Handbook (2019), Section 4.3.2, this matches documented
pattern: "Inadequate measurement system validation." Common related causes
include insufficient gage R&R studies and undocumented calibration intervals.
```

**Pattern Match in Analysis:**
```markdown
**Why #3:** The fixture was not aligned correctly

Validation: Medium confidence match
- Partial match to "Equipment maintenance inadequacy" per AIAG-VDA Section 4.3
- Consider: Was alignment check part of preventive maintenance?

Recommendation: Explore another Why level - "Why was the fixture not aligned?"
```

### Citation Rules

1. **Never fabricate citations.** If MCP unavailable, cite source without section:
   - Good: "Matches 5M root cause pattern: Method (embedded reference data)"
   - Bad: "Per AIAG-VDA Section 4.3.2, page 47" (fabricated when MCP unavailable)

2. **Include confidence level** when reporting pattern matches

3. **Cite section** when available from MCP query results

4. **Frame as augmentation, not judgment:**
   - Good: "This could indicate an opportunity to explore another Why level"
   - Bad: "This is not a valid root cause according to standards"

## Error Handling

### MCP Unavailable

Detected once at session start. If unavailable:

1. Display warning banner (single time)
2. Skip root cause validation prompts at each iteration
3. Use embedded patterns from references/root-cause-patterns.md if user requests
4. Note in outputs: "per 5M root cause framework (embedded reference data)"

**Do NOT:**
- Fabricate citations
- Show repeated warnings at each iteration
- Block root cause identification (validation is optional enrichment)

### No Results

If query returns empty results:

```markdown
No exact match found for "[answer]" in documented root cause patterns.

This could indicate a novel root cause. Consider:
1. Explore another "Why" level for deeper investigation
2. Use /lookup-standard with related terms: [suggestions]
3. Proceed with this cause if supported by evidence

Embedded reference available: See references/root-cause-patterns.md for 5M categories.
```

### Query Failure

If query fails during execution:

```markdown
Standards lookup failed for this query. Continuing with 5 Whys methodology.

Use embedded 5M categories for root cause classification:
- Man, Machine, Material, Method, Measurement

See references/root-cause-patterns.md for common patterns.
```

Log the failure but continue 5 Whys workflow.

## Cross-Tool Knowledge Flow

### Inheriting from Problem Definition

When 5 Whys starts, check for Problem Definition context in conversation:

**If context available:**
- Display problem statement, severity, 5W2H summary
- Use severity for root cause prioritization context
- Reference IS/IS NOT boundaries during causal analysis

**If context not available:**
- Prompt: "Recommend running /problem-definition first"
- Allow standalone execution with minimal elicitation
- Note: severity context not available

### Context Display Format

```
===============================================================================
5 WHYS ROOT CAUSE ANALYSIS
===============================================================================

**Inherited Context** (from Problem Definition)

Problem Statement:
[Full problem statement from Problem Definition]

Severity: [X] ([Standard], [Table/Section])
- [Severity description]

[Expandable] Full 5W2H + IS/IS NOT analysis
[Table content...]

===============================================================================
```

### Severity-Aware Validation

When severity context available, inform validation recommendations:
- High severity (8-10, Catastrophic/Critical): "Given severity X, thorough root cause validation is critical"
- Medium severity (4-7, Marginal): Standard validation recommendations
- Low severity (1-3, Negligible): May skip validation per user preference

## Integration with Embedded Data

5 Whys skill has embedded reference data in:
- `references/root-cause-patterns.md` - 5M categories, systematic vs random failures (Phase 8)
- `references/common-pitfalls.md` - 5 Whys anti-patterns
- `references/quality-rubric.md` - Analysis scoring criteria
- `references/examples.md` - Worked 5 Whys examples

**Relationship:**
- Embedded data: Authoritative for methodology, sufficient for offline root cause analysis
- MCP queries: Enrich with industry-specific patterns, detailed failure mechanisms
- Root cause validation: Use embedded 5M categories when MCP unavailable, cite as "(embedded reference data)"

## Best Practices

### When to Query

**Do query for:**
- Unfamiliar failure mechanisms (user uncertain about pattern)
- High-severity problems (thorough validation warranted)
- Regulatory context (documented patterns strengthen compliance evidence)
- When user explicitly requests validation

**Don't query for:**
- Every iteration without asking (prompted opt-in required)
- Obviously valid causes (user has strong evidence)
- After user has declined 3+ times (stop offering)

### Performance Tips

- Set n_results=5 (show top 3 with confidence)
- Cache results within session when similar causes appear
- Use filter_dict to narrow by domain/standard
- Batch related queries when multiple causes identified

## Example Complete 5 Whys Session Flow

```
5 WHYS SESSION START

[Check MCP] knowledge_search available
Standards mode: ENABLED (AIAG-VDA, ISO 26262, MIL-STD-882)

[Check Context] Problem Definition found in conversation
Displaying inherited context...

Problem Statement: Connector housing P/N 12345-A exhibited cracked locking
tabs at final assembly station 3, affecting 12 of 400 units (3%)

Severity: 7 (AIAG-VDA FMEA Handbook (2019), Table 5.1)
- Product inoperable, loss of primary function

[Phase 3: Why Iterations]

Why #1: "Why did the locking tabs crack?"
Answer: "The tabs experienced excessive stress during assembly"
Offer validation? User: Yes
Query: "root cause pattern excessive stress failure mechanism"
Result: High confidence (92%) - matches "Mechanical overstress"
Citation: AIAG-VDA FMEA Handbook (2019), Section 4.3.1

Why #2: "Why did the tabs experience excessive stress?"
Answer: "The torque applied was too high"
Offer validation? User: Yes
Query: "root cause pattern torque control failure"
Result: High confidence (88%) - matches "Process control inadequacy"
Citation: AIAG-VDA Section 4.3.2

Why #3: "Why was the torque too high?"
Answer: "The torque wrench was not calibrated correctly"
Offer validation? User: No
Continue to next Why...

Why #4: "Why was the torque wrench not calibrated correctly?"
Answer: "Calibration procedure did not specify frequency"
Offer validation? User: Yes
Query: "root cause pattern calibration procedure inadequate"
Result: High confidence (91%) - matches "Measurement system inadequacy"
Citation: AIAG-VDA Section 4.3.2, ISO 17025

[Stopping criteria met]
Root cause identified: Calibration procedure did not specify frequency

[Phase 4: Verification]
All verification tests pass
Root cause validated against standards with high confidence

[Summary]
5 Whys grounded in 3 citations from 2 standards:
- AIAG-VDA FMEA Handbook 2019 (3 citations)
- ISO 17025 (1 citation)
```

## Troubleshooting

### Issue: Low Confidence on Valid Root Cause

**Cause**: Query terms too specific or novel domain
**Solution**:
- Generalize query (remove product-specific terms)
- Note that low confidence doesn't mean invalid - may be novel
- User expertise + evidence can override low confidence

### Issue: Multiple High-Confidence Matches

**Cause**: Root cause spans multiple documented patterns
**Solution**: Present all matches, let user select most applicable

### Issue: Query Returns Wrong Domain

**Cause**: Filter not narrow enough
**Solution**: Add standard_family filter to narrow by safety/quality/process

### Issue: Confidence Scores Inconsistent

**Cause**: Semantic search variance between similar queries
**Solution**:
- Use consistent query construction pattern
- Cache results within session for similar causes
- Treat confidence as guidance, not absolute

---

**Document Version**: 1.0
**Last Updated**: 2026-01-31
**Maintained By**: five-whys-analysis skill development
