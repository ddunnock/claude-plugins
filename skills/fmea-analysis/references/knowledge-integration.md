# Knowledge Integration Reference

## Overview

This document describes how fmea-analysis integrates with knowledge-mcp for standards-grounded failure mode identification and risk assessment.

The integration enables the skill to:
- Query failure mode catalogs from AIAG-VDA, ISO 26262, MIL-STD-882
- Retrieve detailed severity/occurrence/detection rating criteria
- Provide inline citations from authoritative FMEA standards
- Ground Action Priority methodology in AIAG-VDA 2019 source text
- Gracefully degrade when MCP is unavailable (using embedded tables)

## MCP Tool Interface

### knowledge_search

Query the knowledge base for FMEA-related standards content.

**Input Schema**:
```json
{
  "query": "string (required)",
  "n_results": "integer (default: 5)",
  "filter_dict": {
    "domain": "fmea",
    "standard_family": "fmea_methodology | safety | quality"
  }
}
```

**Output Format**:
```json
{
  "query": "common failure modes for brushless DC motor",
  "results": [
    {
      "citation": "AIAG-VDA FMEA Handbook (2019), Section 4.3.2",
      "content": "Electric motor failure modes include...",
      "relevance": "92%",
      "metadata": {
        "domain": "fmea",
        "standard": "AIAG-VDA",
        "version": "2019"
      }
    }
  ],
  "count": 5
}
```

**Tool Availability Check**:
Check MCP availability ONCE at FMEA session start:
```python
if "knowledge_search" in available_tools:
    standards_mode = True
    display_connected_banner()
else:
    standards_mode = False
    display_unavailable_banner()
```

## FMEA-Specific Query Patterns

### Step 4: Failure Mode Queries

| Component Type | Query Pattern | Expected Sources |
|---------------|---------------|------------------|
| Electric motor | "common failure modes for electric motor" | AIAG-VDA, ISO 26262 |
| Sensor | "sensor failure modes automotive" | ISO 26262, MIL-STD-882 |
| Software | "software failure modes FMEA" | ISO 26262-6, IEC 61508 |
| Mechanical | "mechanical failure modes bearing gear" | AIAG-VDA, SAE J1739 |

**Query construction:**
```
Query: "common failure modes for [component/function type]"
Filter: {"domain": "fmea"}
n_results: 10 (show top 5, offer "show more")
```

### Step 5: Rating Criteria Queries

| Rating Type | Query Pattern | Expected Sources |
|-------------|---------------|------------------|
| DFMEA Severity | "DFMEA severity rating criteria scale 1-10" | AIAG-VDA Table 5.2 |
| PFMEA Severity | "PFMEA severity rating criteria manufacturing" | AIAG-VDA Table 5.3 |
| Occurrence | "FMEA occurrence rating probability" | AIAG-VDA Table 5.4 |
| Detection | "FMEA detection rating control effectiveness" | AIAG-VDA Table 5.6 |

**Query construction:**
```
Query: "[DFMEA|PFMEA] [severity|occurrence|detection] rating criteria"
Filter: {"domain": "fmea", "standard": "AIAG-VDA"}
n_results: 5
```

### Action Priority Queries (Optional Verification)

AP calculation uses embedded decision tables (deterministic). MCP query is optional verification only:

```
Query: "AIAG-VDA Action Priority table Severity Occurrence"
Filter: {"domain": "fmea", "standard": "AIAG-VDA", "version": "2019"}
n_results: 3
```

**Important:** Do NOT query MCP for every AP calculation. Embedded table in rating-tables.md is authoritative. Query only if user explicitly requests standards text verification.

## Citation Formatting

### Standard Format

Format all citations inline within failure mode documentation:

- **Full format:** "AIAG-VDA FMEA Handbook (2019), Section 5.2.1"
- **Section only (no page numbers):** Pages vary by edition, use section/clause
- **Multi-source:** "per AIAG-VDA 2019 Section 5.2; see also ISO 26262-9 Section 8.4"

### Examples in FMEA Outputs

**Failure Mode with Citation:**
```markdown
**Failure Mode:** Loss of speed regulation (complete failure)

Per AIAG-VDA FMEA Handbook (2019), Section 4.3.2, this is a "loss of function"
failure mode category. Common causes for motor controllers include Hall sensor
failure and PWM controller latchup.
```

**Severity Rating with Citation:**
```markdown
**Severity:** 8 (Very High)
Product inoperable, loss of primary function per AIAG-VDA FMEA Handbook (2019),
Table 5.2: DFMEA Severity Scale. Customer very dissatisfied if speed regulation fails.
```

**Action Priority with Citation:**
```markdown
**Action Priority:** M (Medium) based on S=8, O=3, D=4 per AIAG-VDA 2019 Table 5.4

Per AIAG-VDA methodology, Medium priority items SHOULD identify action to improve
Prevention or Detection controls, or justify why current controls are adequate.
```

### Citation Rules

1. **Never fabricate citations.** If MCP unavailable, cite source without section:
   - Good: "per AIAG-VDA FMEA Handbook (2019) embedded severity scale"
   - Bad: "per AIAG-VDA 2019, Section 5.2.1, page 46" (fabricated when MCP unavailable)

2. **Include all relevant sources** when multiple standards apply:
   - "Per AIAG-VDA 2019 Section 4.3; see also ISO 26262-9 Section 8.4.3"

3. **Cite normative language** (SHALL, MUST) over informative when available

4. **Match citation to domain:**
   - Automotive FMEA → AIAG-VDA, ISO 26262
   - Aerospace/Defense → MIL-STD-882E
   - General safety → IEC 61508

## Error Handling

### MCP Unavailable

Detected once at session start. If unavailable:

1. Display warning banner (single time)
2. Skip all auto-query prompts at Steps 4 and 5
3. Use embedded tables from references/rating-tables.md
4. Note in outputs: "per AIAG-VDA 2019 (embedded reference data)"

**Do NOT:**
- Fabricate citations
- Show repeated warnings
- Attempt reconnection mid-session (unless user explicitly requests)

### No Results

If query returns empty results:

```markdown
No relevant standards found for "custom authentication flow".

Proceeding with failure modes based on your design knowledge.

Consider querying for related topics:
- "authentication system failure modes"
- "security feature FMEA"
- "software failure modes"
```

**Do NOT silently fall back to embedded data.** Tell user explicitly that MCP returned no results.

### Query Failure

If query fails during execution:

```markdown
Standards lookup failed for this query. Proceeding with embedded reference data.
```

Log the failure but continue FMEA workflow.

## Best Practices

### When to Query

**Do query for:**
- Failure mode catalogs (component-specific patterns)
- Rating scale detailed definitions (user needs understanding, not just numbers)
- Industry benchmarks for occurrence rates
- Regulatory requirements for specific industries

**Don't query for:**
- AP calculation (use embedded table)
- Every minor failure mode (query for significant/unfamiliar ones)
- Re-verification of same scale multiple times per session

### Performance Tips

- Set n_results=5 for rating scales (fewer examples needed)
- Set n_results=10 for failure modes (more variety useful)
- Cache results within session when topics repeat
- Use filter_dict to narrow by domain/standard

## Integration with Embedded Data

FMEA skill has complete embedded reference data in:
- `references/rating-tables.md` - AIAG-VDA 2019 AP tables, severity/occurrence/detection scales
- `references/common-pitfalls.md` - Anti-patterns and common mistakes
- `references/examples.md` - Worked FMEA examples

**Relationship:**
- Embedded data: Authoritative for methodology, sufficient for offline FMEA
- MCP queries: Enrich with failure mode catalogs, detailed examples, regulatory context
- AP calculation: Always use embedded table (deterministic), MCP for verification only

## Integration Workflow

### Step 4: Failure Mode Identification with Standards

**Step-by-step flow**:

1. **Check MCP Availability** (done at session start)
   ```
   if standards_mode == True:
       enable auto-query prompts
   else:
       skip to user brainstorming
   ```

2. **User Describes Component/Function**
   ```
   User: "Motor controller for brushless DC motor"
   ```

3. **Auto-Query for Failure Modes** (if MCP available)
   ```
   Query: "common failure modes for brushless DC motor controller"
   Filter: {"domain": "fmea"}
   n_results: 10
   ```

4. **Present Results with Citation**
   ```markdown
   Found 8 relevant failure modes from AIAG-VDA and ISO 26262:

   1. Loss of speed regulation (AIAG-VDA 2019, Section 4.3.2)
   2. Motor overheating due to control failure (ISO 26262-9, Section 8.4.3)
   3. Hall sensor signal loss (AIAG-VDA 2019, Appendix C)
   ...

   [Show top 5, "show more" for remaining]

   Would you like to use these as starting points or identify different modes?
   ```

5. **User Selects or Adds Modes**
   ```
   User can:
   - Select from standards-sourced list
   - Add custom failure modes
   - Combine both
   ```

### Step 5: Rating with Standards Context

**For Severity Rating**:

1. **Show Rating Scale** (from embedded rating-tables.md)
   ```markdown
   DFMEA Severity Scale (1-10):
   10: Hazard without warning
   9: Hazard with warning
   8: Product inoperable, loss of primary function
   ...
   ```

2. **Optional Auto-Query** (if user requests detail)
   ```
   User: "Explain severity 8 in detail"
   Query: "DFMEA severity rating 8 criteria examples"
   → Present detailed text from AIAG-VDA Table 5.2
   ```

3. **User Assigns Rating**
   ```
   Severity: 8 (Very High)
   Rationale: Motor controller failure prevents vehicle operation
   ```

**For Occurrence and Detection**: Same pattern - show embedded scale, query for details if requested.

### Action Priority Calculation

**Always use embedded table** - NO automatic query:

1. **Calculate from S, O, D** using rating-tables.md AP table
2. **Display Result with Citation**
   ```markdown
   Action Priority: M (Medium)
   Based on S=8, O=3, D=4 per AIAG-VDA 2019 Table 5.4

   Medium priority recommendation: SHOULD identify action to improve
   Prevention or Detection controls, or justify adequacy.
   ```

3. **Only Query if User Explicitly Requests**
   ```
   User: "Show me the AIAG-VDA source for AP table"
   Query: "AIAG-VDA Action Priority table 2019"
   → Display full table text with citation
   ```

## Manual Command: /lookup-standard

### Usage Patterns for FMEA

**Failure Mode Catalog Lookup**:
```
/lookup-standard failure modes for hydraulic valve
```

**Rating Criteria Details**:
```
/lookup-standard AIAG-VDA severity rating 7 criteria
```

**Industry-Specific Examples**:
```
/lookup-standard automotive FMEA examples ISO 26262
```

**Methodology Questions**:
```
/lookup-standard when to use DFMEA vs PFMEA
```

### Response Template

```markdown
## Standards Lookup: [query]

### Result 1 (94% relevant)
**Source**: AIAG-VDA FMEA Handbook (2019), Section 4.3.2

Common failure modes for hydraulic valves include:
- Internal leakage (seal degradation)
- External leakage (body crack, fitting failure)
- Stuck in position (contamination, corrosion)
- Slow response (wear, fluid viscosity issues)

### Result 2 (87% relevant)
**Source**: MIL-STD-882E, Appendix D

Hydraulic system failure modes in aerospace applications...

### Result 3 (82% relevant)
**Source**: ISO 26262-9, Section 8.4.6

For safety-critical hydraulic actuators in automotive braking systems...

---
Showing 3 of 6 results. Say "show more" for additional results.
```

### No Results Response

```markdown
## Standards Lookup: [query]

No direct matches found for "custom IoT sensor failure modes".

Did you mean:
- "sensor failure modes general"
- "electronic component failure modes"
- "embedded system FMEA"

Try querying for component type (temperature sensor, pressure sensor) or
industry context (automotive, industrial, medical).
```

## Example Complete FMEA Session Flow

```
FMEA SESSION START

[Check MCP] knowledge_search available ✓
Standards mode: ENABLED (AIAG-VDA, ISO 26262, MIL-STD-882)

[Step 1-3: Setup - user provides context]
Item: Brushless DC motor controller
Type: DFMEA
Industry: Automotive

[Step 4: Failure Modes]
[Auto-query] "common failure modes for brushless DC motor controller automotive"
→ Found 10 results from AIAG-VDA 2019, ISO 26262-9

Presenting top 5 failure modes:
1. Loss of speed regulation (AIAG-VDA 2019, Section 4.3.2)
2. Motor overheating (ISO 26262-9, Section 8.4.3)
...

User selects: #1 Loss of speed regulation

[Step 5: Rate Failure Mode #1]
**Severity:**
Show embedded scale → User assigns 8 (Very High)
Citation: "per AIAG-VDA 2019 Table 5.2"

**Occurrence:**
Show embedded scale → User assigns 3 (Low)
Citation: "per AIAG-VDA 2019 Table 5.4"

**Detection:**
Show embedded scale → User assigns 4 (Moderate)
Citation: "per AIAG-VDA 2019 Table 5.6"

**Action Priority:**
Calculate: S=8, O=3, D=4 → M (Medium)
Citation: "per AIAG-VDA 2019 Table 5.4 AP decision table"
No query (embedded table is authoritative)

[Step 6: Recommended Actions]
User defines actions based on M priority guidance

[Summary]
FMEA grounded in 4 citations from 2 standards:
- AIAG-VDA FMEA Handbook 2019 (3 citations)
- ISO 26262-9:2018 (1 citation)
```

## Troubleshooting

### Issue: Too Generic Failure Modes

**Cause**: Query lacks component specificity
**Solution**: Add component type and industry context

Before: `"failure modes"`
After: `"failure modes for brushless DC motor controller automotive"`

### Issue: Wrong Standard Family

**Cause**: Domain mismatch (querying automotive standards for aerospace system)
**Solution**: Use filter_dict to specify standard_family

```json
{
  "query": "failure modes for hydraulic actuator",
  "filter_dict": {
    "domain": "fmea",
    "standard_family": "safety",
    "industry": "aerospace"
  }
}
```

### Issue: AP Table Query Returns Different Version

**Cause**: Multiple FMEA standard versions in knowledge base
**Solution**: ALWAYS use embedded table for AP calculation, ignore query results unless user explicitly requested verification

### Issue: Fabricated Section Numbers

**Symptom**: User reports section doesn't exist in their copy of standard
**Cause**: Either MCP returned outdated citation OR knowledge base has different edition
**Solution**: Acknowledge discrepancy, fall back to "per AIAG-VDA 2019 (no specific section available)"

## Citation Validation

### Never Fabricate Rule

**CRITICAL**: If MCP unavailable or query fails, NEVER make up section numbers.

**Correct fallbacks:**
- "per AIAG-VDA FMEA Handbook (2019) embedded severity scale"
- "per AIAG-VDA 2019 methodology (embedded reference data)"
- "based on AIAG-VDA 2019 Action Priority framework"

**NEVER do this:**
- "per AIAG-VDA 2019, Section 5.2.1, page 46" (when you don't have the source)
- "ISO 26262-9, Clause 8.4.3.2.1" (fabricated clause structure)

### Verification Pattern

When presenting a citation from MCP:
1. Include relevance score if <80% → user should verify
2. If multiple standards conflict → present both, note difference
3. If citation is from unofficial source → mark as "reference" not "per standard"

---

**Document Version**: 1.0
**Last Updated**: 2026-01-31
**Maintained By**: fmea-analysis skill development
