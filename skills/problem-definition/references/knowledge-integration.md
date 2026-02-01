# Knowledge Integration Reference

## Overview

This document describes how problem-definition integrates with knowledge-mcp for standards-grounded severity classification during problem definition.

The integration enables the skill to:
- Query severity classification scales from MIL-STD-882E, AIAG-VDA FMEA
- Provide domain-specific severity criteria (safety, quality, financial)
- Include inline citations from authoritative standards
- Support cross-tool knowledge flow (severity → 5 Whys → FMEA)
- Gracefully degrade when MCP is unavailable (using embedded scales)

## MCP Tool Interface

### knowledge_search

Query the knowledge base for RCCA-related standards content.

**Input Schema**:
```json
{
  "query": "string (required)",
  "n_results": "integer (default: 5)",
  "filter_dict": {
    "domain": "rcca",
    "standard_family": "severity_classification | safety | quality"
  }
}
```

**Output Format**:
```json
{
  "query": "severity classification scale safety-critical systems",
  "results": [
    {
      "citation": "MIL-STD-882E, Section 3.1",
      "content": "Severity categories: I (Catastrophic), II (Critical)...",
      "relevance": "94%",
      "metadata": {
        "domain": "rcca",
        "standard": "MIL-STD-882E",
        "version": "2012"
      }
    }
  ],
  "count": 5
}
```

**Tool Availability Check**:
Check MCP availability ONCE at Problem Definition session start:
```python
if "knowledge_search" in available_tools:
    standards_mode = True
    display_connected_banner()
else:
    standards_mode = False
    display_unavailable_banner()
```

## Problem Definition-Specific Query Patterns

### Severity Classification Queries

| Problem Domain | Query Pattern | Expected Sources |
|---------------|---------------|------------------|
| Safety-critical | "severity classification safety hazard impact" | MIL-STD-882E, ISO 26262 |
| Manufacturing quality | "FMEA severity rating customer impact" | AIAG-VDA Table 5.1 |
| Financial impact | "severity classification financial monetary loss" | MIL-STD-882E (Category III/IV) |
| Regulatory compliance | "severity non-compliance government regulations" | AIAG-VDA severity 10 |

**Query construction:**
```
Query: "severity classification scale [domain inferred from problem description]"
Filter: {"domain": "rcca"} or {"domain": "fmea"}
n_results: 5 (show top 2-3 scales, user selects)
```

### Trigger Point

Query severity classification AFTER "How Much" (extent) is quantified:
- User has described the problem impact and consequences
- Numerical quantification available (e.g., "12 of 400 units (3%)")
- Natural segue: "You've described the extent. Would you like to classify severity?"

**Do NOT query:**
- Before impact is described (user lacks context to select severity)
- Automatically without asking (prompted opt-in required)
- Repeatedly after user declines (session memory)

## Citation Formatting

### Standard Format

Format all citations inline within problem definition outputs:

- **Full format:** "Severity: 7 (AIAG-VDA FMEA Handbook (2019), Table 5.1)"
- **MIL-STD format:** "Severity: II (Critical) per MIL-STD-882E, Section 3.1"
- **Section only (no page numbers):** Pages vary by edition, use section/table

### Examples in Problem Definition Outputs

**Severity Classification with Citation:**
```markdown
SEVERITY CLASSIFICATION:
Severity: 7 (AIAG-VDA FMEA Handbook (2019), Table 5.1)
- Product inoperable, loss of primary function
- Customer very dissatisfied
- Justification: 3% failure rate with complete loss of primary function
```

**MIL-STD Safety Classification:**
```markdown
SEVERITY CLASSIFICATION:
Severity: II (Critical) per MIL-STD-882E, Section 3.1
- Could result in permanent partial disability
- Reversible significant environmental impact
- Monetary loss ≥$1M but <$10M
```

### Citation Rules

1. **Never fabricate citations.** If MCP unavailable, cite source without section:
   - Good: "Severity: 7 per AIAG-VDA FMEA Handbook (2019) embedded severity scale"
   - Bad: "Severity: 7 per AIAG-VDA 2019, Table 5.1, page 23" (fabricated when MCP unavailable)

2. **Include justification** linking severity to problem description

3. **Cite table/section** when available from MCP query results

4. **Match scale to domain:**
   - Safety-critical → MIL-STD-882E (I/II/III/IV)
   - Manufacturing/Quality → AIAG-VDA (1-10)
   - Medical devices → ISO 14971 (if available)

## Error Handling

### MCP Unavailable

Detected once at session start. If unavailable:

1. Display warning banner (single time)
2. Skip severity classification prompt at step 5
3. Use embedded scales from references/severity-scales.md if user requests
4. Note in outputs: "per MIL-STD-882E (embedded reference data)"

**Do NOT:**
- Fabricate citations
- Show repeated warnings
- Prevent problem definition completion (severity is optional enrichment)

### No Results

If query returns empty results:

```markdown
No relevant severity scales found for "[query]".

Using embedded severity scales. Available options:
- MIL-STD-882E (safety-critical systems): Catastrophic/Critical/Marginal/Negligible
- AIAG-VDA FMEA (manufacturing/quality): 1-10 scale

Which scale best fits your problem context?
```

### Query Failure

If query fails during execution:

```markdown
Standards lookup failed. Proceeding with embedded severity scales.

Available from references/severity-scales.md:
- MIL-STD-882E (4-level safety scale)
- AIAG-VDA (10-level quality scale)
```

Log the failure but continue problem definition workflow.

## Cross-Tool Knowledge Flow

### Output Available to Downstream Skills

Problem Definition outputs are available to subsequent skills in the same session:

**Available context:**
```json
{
  "problem_statement": "Connector housing P/N 12345-A...",
  "severity": {
    "level": 7,
    "scale": "AIAG-VDA",
    "description": "Product inoperable, loss of primary function",
    "citation": "AIAG-VDA FMEA Handbook (2019), Table 5.1"
  },
  "5w2h": { "what_object": "...", "what_defect": "...", ... },
  "is_is_not": { "what": { "is": "...", "is_not": "..." }, ... }
}
```

**Downstream consumers:**
- **5 Whys**: Inherits full context, displays at Phase 1
- **FMEA**: Severity pre-populated from Problem Definition
- **RCCA Master (8D)**: D2 flows to D4, D5, D6

### Context Availability

Cross-tool knowledge flow works within same conversation session.
- Problem Definition outputs remain in conversation history
- 5 Whys checks for prior Problem Definition outputs
- If not found, prompts user to run /problem-definition or elicits minimal context

## Integration with Embedded Data

Problem Definition skill has embedded reference data in:
- `references/severity-scales.md` - MIL-STD-882E and AIAG-VDA severity scales (Phase 8)
- `references/5w2h-framework.md` - 5W2H methodology guidance
- `references/is-is-not-analysis.md` - IS/IS NOT analysis patterns
- `references/pitfalls.md` - Common problem definition mistakes

**Relationship:**
- Embedded data: Authoritative for methodology, sufficient for offline problem definition
- MCP queries: Enrich with detailed severity criteria, industry-specific definitions
- Severity classification: Use embedded scales when MCP unavailable, cite as "(embedded reference data)"

---

**Document Version**: 1.0
**Last Updated**: 2026-01-31
**Maintained By**: problem-definition skill development
