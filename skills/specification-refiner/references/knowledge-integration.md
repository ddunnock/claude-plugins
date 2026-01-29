# Knowledge Integration Reference

## Overview

This document describes how specification-refiner integrates with knowledge-mcp for standards-grounded analysis.

The integration enables the skill to:
- Automatically query engineering standards during analysis
- Provide inline citations from authoritative sources (IEEE, ISO, INCOSE)
- Ground findings in established best practices
- Gracefully degrade when MCP is unavailable

## MCP Tool Interface

### knowledge_search

Query the knowledge base for relevant standards content.

**Input Schema**:
```json
{
  "query": "string (required)",
  "n_results": "integer (default: 5)",
  "filter_dict": {
    "document_type": "standard | handbook | guide",
    "normative": "boolean"
  }
}
```

**Output Format**:
```json
{
  "query": "traceability requirements",
  "results": [
    {
      "citation": "ISO/IEC/IEEE 12207:2017, Clause 6.4.2, p.23",
      "content": "Requirements SHALL be traceable...",
      "relevance": "87%",
      "metadata": {...}
    }
  ],
  "count": 5
}
```

**Tool Availability Check**:
Before any query, verify the tool is available:
```python
# Check if knowledge_search is in available tools
if "knowledge_search" in available_tools:
    proceed_with_query()
else:
    warn_user_and_skip()
```

## Auto-Query Patterns

### Finding Validation

For each analysis finding, query:
```
[finding topic] [domain] standards requirements
```

**Example**: Finding about missing verification criteria
- Query: "verification criteria requirements engineering standards"
- Use top result to cite in finding
- Format: "Per ISO/IEC/IEEE 12207:2017, Clause 6.4.2: [relevant excerpt]"

### Phase-Specific Queries

| Phase | Trigger | Query Pattern | Purpose |
|-------|---------|---------------|---------|
| ANALYZE (start) | Before SEAMS | "requirements engineering best practices [domain]" | Context for analysis |
| ANALYZE (start) | Before Critical Path | "dependency analysis systems engineering" | Context for critical path |
| ANALYZE (finding) | Each gap identified | "[finding topic] [domain] standards" | Validate with standards |

### Domain-Specific Queries

| Domain | Query Pattern | Example |
|--------|---------------|---------|
| Software | "[topic] software engineering IEEE 12207" | "traceability software engineering IEEE 12207" |
| Systems | "[topic] systems engineering ISO 15288" | "verification systems engineering ISO 15288" |
| Safety | "[topic] functional safety ISO 26262" | "hazard analysis functional safety ISO 26262" |
| Requirements | "[topic] requirements INCOSE handbook" | "requirements attributes INCOSE handbook" |

## Citation Formatting

### Standard Format

Always format citations as received from knowledge-mcp:
- `ISO/IEC/IEEE 12207:2017, Clause 6.4.2, p.23`
- `INCOSE SE Handbook, Section 4.2, pp.45-47`
- `IEEE 15288-2015, Clause 6.4.3, p.31`

### Inline Citation in Findings

Include citations directly within finding descriptions:

**Example 1: Structure Finding**
> **Finding**: Requirements lack verification criteria
>
> Per ISO/IEC/IEEE 12207:2017, Clause 6.4.2: "Each requirement SHALL include verification criteria that define how conformance will be demonstrated."

**Example 2: Traceability Finding**
> **Finding**: No traceability matrix provided
>
> ISO/IEC/IEEE 12207:2017, Clause 6.3.3 mandates: "Requirements SHALL be traceable to their source and through to implementation and test cases."

**Example 3: Multiple Citations**
> **Finding**: Stakeholder needs not documented
>
> Both INCOSE SE Handbook (Section 4.1) and ISO/IEC/IEEE 15288:2015 (Clause 6.2.1) emphasize documenting stakeholder needs before defining requirements.

## Error Handling

### MCP Unavailable

Check before any query:
```
if knowledge_search tool not available:
    warn("Knowledge base unavailable. Proceeding without standards context.")
    skip all auto-queries
    mark findings as "ungrounded"
```

**User Warning Format**:
> Note: Knowledge base unavailable. Analysis proceeds without standards context.

### Query Failure

If individual query fails during execution:
```
try:
    results = knowledge_search(query)
except:
    log("Standards lookup failed for: " + query)
    continue without citation
    note: "Standards citation unavailable"
```

**Finding Annotation**:
> Standards citation unavailable for this finding.

### No Results

If query returns empty results:
- Do not fabricate citations
- State: "No relevant standards found for [topic]"
- Offer to search with different terms
- Continue analysis without citation

**Example**:
> No relevant standards found for "custom authentication flow". Consider querying for related topics: "authentication standards", "identity management", or "access control".

## Integration Workflow

### Phase 2 ANALYZE with Standards Integration

**Step-by-step flow**:

1. **Check MCP Availability**
   ```
   if knowledge_search available:
       standards_mode = True
   else:
       warn("Knowledge base unavailable...")
       standards_mode = False
   ```

2. **Begin SEAMS Analysis**
   ```
   if standards_mode:
       context = knowledge_search("requirements engineering best practices [domain]")
       use context to inform analysis
   ```

3. **For Each Lens (Structure, Execution, etc.)**
   - Identify gaps and issues
   - For each significant finding:
     ```
     if standards_mode:
         citation = knowledge_search("[finding topic] standards")
         add inline citation to finding
     ```

4. **Begin Critical Path Analysis**
   ```
   if standards_mode:
       context = knowledge_search("dependency analysis systems engineering")
       use context to inform analysis
   ```

5. **For Each Critical Finding**
   - Query relevant standards
   - Include citations in finding descriptions

6. **Summarize**
   - If standards_mode: "Analysis grounded in N citations from M standards"
   - If not: "Analysis completed without standards context"

### Example Complete Flow

```
PHASE 2: ANALYZE

[Check MCP] knowledge_search available ✓

[Auto-query] "requirements engineering best practices software"
→ Found 5 results from ISO 12207, INCOSE Handbook

[SEAMS: Structure Lens]
Finding S-001: Missing verification criteria
[Query] "verification criteria requirements standards"
→ ISO/IEC/IEEE 12207:2017, Clause 6.4.2
→ Added inline citation

Finding S-002: No traceability matrix
[Query] "traceability matrix requirements"
→ ISO/IEC/IEEE 12207:2017, Clause 6.3.3
→ Added inline citation

[SEAMS: Execution Lens]
...

[Critical Path Analysis]
[Auto-query] "dependency analysis systems engineering"
→ Found 3 results from ISO 15288, INCOSE

[Summary]
Analysis grounded in 12 citations from 3 standards:
- ISO/IEC/IEEE 12207:2017 (8 citations)
- ISO/IEC/IEEE 15288:2015 (3 citations)
- INCOSE SE Handbook (1 citation)
```

## Manual Command: /lookup-standard

### Usage Patterns

**Direct Standard Reference**:
```
/lookup-standard ISO 12207 verification
```

**Conceptual Query**:
```
/lookup-standard what are requirements attributes
```

**Domain-Specific**:
```
/lookup-standard safety-critical requirements ISO 26262
```

### Response Template

```markdown
## Standards Lookup: [query]

### Result 1 (87% relevant)
**Source**: ISO/IEC/IEEE 12207:2017, Clause 6.4.2, p.23

Requirements verification criteria SHALL define:
- Methods to be used (inspection, analysis, demonstration, test)
- Expected outcomes
- Pass/fail criteria
- Resource requirements

### Result 2 (74% relevant)
**Source**: INCOSE SE Handbook, Section 4.2, pp.45-47

Verification confirms that each requirement is correctly implemented...

### Result 3 (68% relevant)
**Source**: IEEE 15288-2015, Clause 6.4.3, p.31

Verification activities SHALL be planned before implementation...

---
Showing 3 of 8 results. Say "show more" for additional results.
```

### No Results Response

```markdown
## Standards Lookup: [query]

No direct matches found for "[query]".

Did you mean:
- "requirements verification methods"
- "verification and validation standards"
- "test criteria requirements"

Try refining your query with specific standard names (ISO 12207, IEEE 15288) or broader terms.
```

## Best Practices

### When to Auto-Query

✅ **Do query for**:
- Missing critical elements (verification criteria, traceability)
- Process-related findings (lifecycle stages, stakeholder engagement)
- Quality attributes (reliability, maintainability)
- Standard terminology clarification

❌ **Don't query for**:
- Project-specific design choices
- Technology selection rationale
- Custom domain logic
- Implementation-specific details

### Citation Quality

**Good Citations**:
- Directly relevant to finding
- Normative language (SHALL, MUST)
- Specific clause/section references
- Add authority to finding

**Poor Citations**:
- Tangentially related
- Informative language only
- Entire standard reference without specifics
- Don't strengthen the finding

### Performance Considerations

- Limit queries to significant findings (avoid querying every minor issue)
- Cache query results within session when topics repeat
- Use filter_dict to narrow search when domain is known
- Set n_results=3 for faster responses when fewer examples needed

## Troubleshooting

### Issue: Irrelevant Results

**Cause**: Query too broad or ambiguous
**Solution**: Add domain context and specific keywords

Before: `"requirements"`
After: `"requirements verification criteria software engineering"`

### Issue: No Results for Valid Topic

**Cause**: Terminology mismatch or coverage gap
**Solution**: Try synonyms or related terms

- "verification" → "V&V", "validation", "testing"
- "requirements" → "specifications", "needs"
- "traceability" → "linkage", "coverage", "mapping"

### Issue: Too Many Results

**Cause**: Query too generic
**Solution**: Use filter_dict to narrow by document_type or add specific standard names

```json
{
  "query": "verification methods",
  "n_results": 3,
  "filter_dict": {
    "document_type": "standard",
    "normative": true
  }
}
```

## Future Enhancements

Potential improvements to knowledge integration:

1. **Learning from feedback**: Track which citations users find most valuable
2. **Cross-reference validation**: Verify cited clauses are current/applicable
3. **Citation clustering**: Group related standards citations
4. **Coverage metrics**: Report % of findings with standards backing
5. **Regulatory mapping**: Link standards to compliance requirements

---

**Document Version**: 1.0
**Last Updated**: 2026-01-29
**Maintained By**: specification-refiner skill development
