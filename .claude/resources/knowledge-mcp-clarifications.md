# Knowledge MCP — Clarifications

> **Document ID**: KMCP-CLARIFY
> **Version**: 1.0.0
> **Status**: Approved
> **Created**: 2026-01-16
> **Supplements**: KMCP-A-SPEC v0.1.0

---

## Session Summary

**Date**: 2026-01-16
**Questions Asked**: 6
**Categories Resolved**: ERROR, BEHAVIOR, DATA, RECOVERY, TEMPORAL

---

## Clarifications

### CLARIFY-001 [ERROR] — PDF Parsing Failures

**Affects**: A-REQ-INGEST-001 (§3.2.1)

**Question**: How should the system handle malformed or inaccessible PDF files (corrupted, encrypted, password-protected) during ingestion?

**Resolution**: Interactive prompt to let user decide whether to continue or fail.

**Specification Addition** (append to A-REQ-INGEST-001):

```markdown
**Error Handling for Inaccessible Documents:**

When encountering corrupted, encrypted, or password-protected files during ingestion:

1. Pause ingestion and display error details to user
2. Prompt user with options:
   - **Continue**: Skip problematic file(s), continue with remaining files (exit code 1)
   - **Abort**: Stop ingestion entirely (exit code 2)
3. Log skipped files with ERROR level including file path and reason
4. Include skipped file count in final summary

This allows users to make informed decisions before incurring embedding costs.

| Condition | User Options | Behavior |
|-----------|--------------|----------|
| Corrupted PDF | Continue / Abort | Prompt user before proceeding |
| Encrypted PDF | Continue / Abort | Prompt user, suggest decryption |
| Password-protected | Continue / Abort | Prompt user, request password or skip |
| Empty document | Continue / Abort | Prompt user with warning |
```

---

### CLARIFY-002 [ERROR] — OpenAI API Failures

**Affects**: A-REQ-IF-002 (§5.2)

**Question**: What should happen when OpenAI embedding requests fail due to quota exhaustion or content policy violations?

**Resolution**: Fail immediately with clear error code; user resolves externally.

**Specification Addition** (append to A-REQ-IF-002):

```markdown
**Error Handling for OpenAI API:**

| OpenAI Error | Error Code | Action |
|--------------|------------|--------|
| 401 Unauthorized | `auth_error` | Fail immediately, exit code 3 |
| 429 Rate Limited (temporary) | `rate_limited` | Retry with backoff per §6.2.2 |
| 429 Quota Exceeded | `rate_limited` | Fail with clear message, suggest billing check |
| 400 Invalid Request | `invalid_input` | Skip content, log ERROR with chunk details |
| 500+ Server Error | `internal_error` | Retry with backoff per §6.2.2 |

For quota exhaustion: The system shall fail with a clear error message indicating:
- Current quota status (if available from API response)
- Suggestion to check OpenAI billing dashboard
- No local embedding fallback (preserves embedding space consistency)
```

---

### CLARIFY-003 [BEHAVIOR] — Similar Terms Algorithm

**Affects**: A-REQ-TOOL-002 (§3.1.2)

**Question**: How should "similar_terms" be computed for the knowledge_lookup not-found response?

**Resolution**: Semantic similarity search with fuzzy string fallback.

**Specification Addition** (append after Not Found Response in §3.1.2):

```markdown
**Similar Terms Algorithm:**

1. Search definition chunks using query term with semantic embedding similarity
2. Return top 3 results with similarity score > 0.5
3. If fewer than 3 semantic matches found, supplement with fuzzy string matching:
   - Use Levenshtein edit distance ≤ 2 against indexed definition terms
   - Exclude duplicates already found via semantic search
4. Return empty array if no similar terms found by either method

**Example:**
- Query: "requiremnt" (typo)
- Semantic search: ["system requirement", "functional requirement"]
- Fuzzy match: ["requirement"] (edit distance = 1)
- Result: ["requirement", "system requirement", "functional requirement"]
```

---

### CLARIFY-004 [DATA] — Deep Hierarchy Handling

**Affects**: A-REQ-INGEST-003 (§3.2.3)

**Question**: How should documents with more than 6 hierarchy levels be handled?

**Resolution**: Truncate section_hierarchy array to 6 entries; preserve full clause_number.

**Specification Addition** (append to A-REQ-INGEST-003):

```markdown
**Hierarchy Depth Handling:**

For documents with section hierarchy exceeding 6 levels:

1. Store full `clause_number` as-is (e.g., "5.3.1.2.4.1.3")
2. Truncate `section_hierarchy` array to first 6 entries
3. Log INFO message indicating hierarchy truncation with document ID
4. Filtering by `section_hierarchy` limited to 6 levels; use `clause_number` prefix match for deeper navigation

**Example:**
- Document has 8-level heading: "5.3.1.2.4.1.3.2 Detailed Subprocess"
- `clause_number`: "5.3.1.2.4.1.3.2" (preserved)
- `section_hierarchy`: ["5", "5.3", "5.3.1", "5.3.1.2", "5.3.1.2.4", "5.3.1.2.4.1"] (truncated)
```

---

### CLARIFY-005 [ERROR] — Vector Store Fallback Chain

**Affects**: A-REQ-IF-003 (§5.3)

**Question**: What should happen if both Qdrant AND ChromaDB are unavailable?

**Resolution**: Fail startup with connection_error, exit code 3.

**Specification Addition** (append to A-REQ-IF-003):

```markdown
**Fallback Chain and Failure Handling:**

| Scenario | Behavior |
|----------|----------|
| Qdrant available | Use Qdrant (primary) |
| Qdrant unavailable, ChromaDB available | Use ChromaDB with WARNING log |
| Both unavailable | Fail with `connection_error`, exit code 3 |

**Startup Requirement**: At least one operational vector store is required.

The system shall NOT:
- Start in degraded read-only mode
- Queue operations for later
- Fall back to in-memory storage

Error message shall indicate:
- Which stores were attempted
- Connection failure reasons
- Configuration variables to check
```

---

### CLARIFY-006 [RECOVERY] — Partial Ingestion Failures

**Affects**: A-REQ-INGEST-006 (§3.2.6)

**Question**: How should partial ingestion failures be handled (e.g., 500 of 1000 chunks processed before failure)?

**Resolution**: Idempotent re-run design; --force replaces all chunks for document.

**Specification Addition** (append to A-REQ-INGEST-006):

```markdown
**Partial Failure Recovery:**

The ingestion pipeline uses idempotent upsert semantics:

1. Each chunk upserted individually by `(document_id, chunk_id)` key
2. Partial failures leave successfully processed chunks in store
3. Re-running ingestion (with `--force`) safely replaces all chunks for affected documents
4. No checkpoint/resume mechanism required

**Recovery Workflow:**
1. Ingestion fails at chunk 500/1000
2. User fixes underlying issue (e.g., API quota, network)
3. User re-runs: `knowledge-ingest --force <source>`
4. All chunks for document replaced with fresh ingestion

**CLI Reporting:**
- Display progress: "Processing chunk 500/1000..."
- On failure: "Ingestion failed at chunk 500. 499 chunks successfully stored."
- Suggestion: "Re-run with --force after resolving the issue to replace partial ingestion."
```

---

### CLARIFY-007 [TEMPORAL] — Health Check Thresholds

**Affects**: A-REQ-TOOL-006 (§3.1.6)

**Question**: What latency thresholds should determine health check status?

**Resolution**: 500ms threshold, configurable via environment variable.

**Specification Addition** (append to A-REQ-TOOL-006):

```markdown
**Health Status Determination:**

| Condition | Status |
|-----------|--------|
| All checks up AND all latency < 500ms | `healthy` |
| All checks up AND any latency ≥ 500ms | `degraded` |
| Any check down | `unhealthy` |

**Configuration:**
- `HEALTH_LATENCY_THRESHOLD_MS`: Latency threshold in milliseconds (default: 500)

**Example Response:**
```json
{
  "status": "degraded",
  "checks": {
    "vector_store": {"status": "up", "latency_ms": 750, "message": "Latency above threshold"},
    "embedding_service": {"status": "up", "latency_ms": 200, "message": "OK"}
  }
}
```
```

---

## Coverage Summary

| Category | Status | Resolution |
|----------|--------|------------|
| SCOPE | ○ Clear | No ambiguities identified |
| BEHAVIOR | ✓ Resolved | CLARIFY-003: similar_terms algorithm |
| SEQUENCE | ○ Clear | No ambiguities identified |
| AUTHORITY | ○ Clear | No ambiguities identified |
| DATA | ✓ Resolved | CLARIFY-004: hierarchy truncation |
| INTERFACE | ○ Clear | Sparse vector encoding deferred to implementation |
| CONSTRAINT | ○ Clear | Performance targets sufficient |
| TEMPORAL | ✓ Resolved | CLARIFY-007: health thresholds |
| ERROR | ✓ Resolved | CLARIFY-001, CLARIFY-002, CLARIFY-005 |
| RECOVERY | ✓ Resolved | CLARIFY-006: idempotent re-run |
| ASSUMPTION | ○ Clear | No critical assumptions |
| STAKEHOLDER | ○ Clear | No ambiguities identified |
| TRACEABILITY | ○ Clear | No ambiguities identified |

**Legend:**
- ✓ Resolved: Was ambiguous, now clarified
- ○ Clear: Already sufficient, no clarification needed

---

## Implementation Notes

### Task Updates Required

The following tasks should incorporate these clarifications:

| Task | Clarification | Update Needed |
|------|---------------|---------------|
| TASK-003 (PDF Ingestor) | CLARIFY-001 | Add interactive error prompting |
| TASK-004 (DOCX Ingestor) | CLARIFY-001 | Add interactive error prompting |
| TASK-005 (Markdown Ingestor) | CLARIFY-001 | Add interactive error prompting |
| TASK-017 (knowledge_lookup) | CLARIFY-003 | Implement similar_terms algorithm |
| TASK-007 (Standards Chunker) | CLARIFY-004 | Implement hierarchy truncation |
| TASK-014 (Hybrid Search) | CLARIFY-005 | Implement fallback chain |
| TASK-021 (knowledge_health) | CLARIFY-007 | Implement latency thresholds |
| TASK-024 (Ingest Implementation) | CLARIFY-006 | Document idempotent behavior |

### New Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEALTH_LATENCY_THRESHOLD_MS` | `500` | Latency threshold for degraded status |

---

*End of Clarifications Document*