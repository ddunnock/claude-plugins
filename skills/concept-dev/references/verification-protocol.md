# Verification Protocol

Source confidence hierarchy and verification rules for concept development research.

## Source Confidence Hierarchy

| Level | Definition | Source Types | When to Assign |
|-------|-----------|-------------|----------------|
| **HIGH** | Verified via authoritative, peer-reviewed, or official source | Peer-reviewed papers, official documentation, government/standards publications, verified test data | Source is from a recognized authority in the domain AND can be independently accessed |
| **MEDIUM** | Credible source, not independently verified | Vendor documentation, well-cited blog posts, conference presentations, industry reports, reputable news coverage | Source appears credible but hasn't been cross-referenced OR is from a single authoritative source |
| **LOW** | Single source, informal, or uncertain | Forum discussions, single blog post, undated content, anonymous sources, extrapolations from related domains | Only one source found, OR source quality is questionable, OR claim is extrapolated from adjacent domain |
| **UNGROUNDED** | No external source available | Training data inference, general knowledge, logical deduction | You "know" this but can't point to a specific, retrievable source |

## Training Data as Hypothesis

This is the most critical rule in the verification protocol.

**The Problem:** Claude's training data contains vast technical knowledge, but this knowledge:
- May be outdated
- May be wrong (trained on incorrect sources)
- May be confidently stated but not verifiable
- May conflate similar-sounding concepts
- Cannot be cited (no retrievable source)

**The Rule:** When you "know" something from training data but cannot find an external source to verify it:

1. **Do NOT present it as fact.** Instead, present it as a hypothesis:
   > "Based on general knowledge, [X] may be the case. I was unable to find a specific, citable source to verify this."

2. **Register as UNGROUNDED** in source_tracker.py

3. **Flag for verification** in the drill-down output

4. **Offer to help the user verify** by suggesting specific searches or asking if they have direct experience

## Verification Workflow

For each claim in research output:

```
Is there a cited, retrievable source?
├── YES → Confidence = HIGH or MEDIUM (based on source quality)
│         ├── Peer-reviewed / official → HIGH
│         └── Other credible → MEDIUM
└── NO → Is this from training data?
    ├── YES → Register as UNGROUNDED
    │         ├── Attempt verification via WebSearch
    │         │   ├── Found source → Register, upgrade confidence
    │         │   └── Not found → Keep UNGROUNDED, flag as hypothesis
    │         └── Mark for skeptic review
    └── NO → This is an assumption
              └── Register in assumption_tracker
```

## Known Pitfalls

### Confidence Inflation
- **Pitfall:** Stating training-data claims with the same confidence as cited sources
- **Fix:** Always distinguish cited findings from general knowledge

### Citation Without Verification
- **Pitfall:** Providing a source URL that might not actually support the claim
- **Fix:** When using WebFetch to read a source, verify the specific claim exists in the content

### Recency Bias
- **Pitfall:** Assuming training data reflects current state of a fast-moving domain
- **Fix:** Explicitly search for recent developments; note dates of all sources

### Survivorship Bias
- **Pitfall:** Only finding success stories, missing failure cases
- **Fix:** Actively search for "[approach] limitations", "[approach] failure cases"

### Authority Bias
- **Pitfall:** Treating vendor claims as independent verification
- **Fix:** Vendor documentation is MEDIUM confidence at best; look for independent validation

### Conflation
- **Pitfall:** Confusing similar technologies, standards, or approaches
- **Fix:** Be specific — "[specific version]" not "[general category]"

## Skeptic Integration

The [skeptic agent](../agents/skeptic.md) applies this protocol retroactively:
1. Extract all claims from research output
2. Check each claim against this confidence hierarchy
3. Flag mismatches (e.g., HIGH confidence claimed but source is a blog post)
4. Downgrade as needed
5. Identify claims that need user verification
