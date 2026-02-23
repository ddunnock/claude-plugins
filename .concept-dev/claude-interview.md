# Deep-Plan Interview Transcript

## Q1: Implementation Scope

**Question:** The concept doc identifies 3 maturation phases. Are you building Phase 1 only, Phases 1-2, or all 3 phases?

**Answer:** All 3 phases. Full plan covering foundation, validation/research, and decomposition. Implement incrementally.

## Q2: Quality Checker Approach

**Question:** The Quality Checker has a key design decision: keyword/pattern-based syntactic checks vs. LLM-only vs. hybrid. Research shows 21 rules are fully automatable via regex/NLP. Which approach?

**Answer:** Hybrid (Recommended). Regex/NLP for 21 syntactic rules + LLM with CoT for 9 semantic rules. Best precision, more implementation work.

## Q3: Attribute Elicitation UX

**Question:** 13 mandatory INCOSE attributes per requirement. Metered questioning vs. batch-fill-then-review vs. minimal+expand. How should attribute collection work?

**Answer:** Minimal + expand. Require only statement + type + priority. Offer to expand full attributes on demand.

## Q4: Workspace Pattern

**Question:** Separate `.requirements-dev/` workspace or extend existing `.concept-dev/`?

**Answer:** Separate `.requirements-dev/`. Clean separation. Concept-dev artifacts are read-only inputs. Clear lifecycle boundary.

## Q5: Specification Document Format

**Question:** MIL-STD-498 SRS vs. block-centric custom vs. hybrid structure for REQUIREMENTS-SPECIFICATION.md?

**Answer:** Block-centric custom. Organized by functional blocks from concept-dev, then by type within each block. Matches user mental model.

## Q6: Standalone vs. Concept-Dev Dependency

**Question:** Strictly require concept-dev output, or support standalone use?

**Answer:** Concept-dev preferred, manual fallback. Optimized for concept-dev input but gracefully handles partial or missing artifacts with manual entry.

## Q7: TPM Research Approach

**Question:** Same tiered research tool approach as concept-dev, or simpler WebSearch-only?

**Answer:** Same tiered approach as concept-dev. Reuse check_tools.py pattern. Proven approach.

## Q8: Export Format

**Question:** JSON only or JSON + ReqIF export?

**Answer:** JSON + ReqIF export. Include ReqIF XML export from the start for tool interoperability.

## Q9: Open Items

**Question:** Any additional constraints, concerns, or priorities not in the concept document?

**Answer:** No additional context. The concept document and interview answers cover everything needed.
