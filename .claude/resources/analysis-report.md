# Knowledge MCP — Analysis Report

> **Generated**: 2026-01-15
> **Analyzer**: SpecKit Analyze v1.0
> **Focus**: Plan & Tasks Compliance with A-Spec and Standards

---

## Executive Summary

| Category                | Critical  | High  | Medium  | Low   |
|-------------------------|-----------|-------|---------|-------|
| COVERAGE_GAPS           | 0         | 1     | 1       | 0     |
| STANDARD_VIOLATIONS     | 1         | 2     | 1       | 0     |
| EXISTING_CODE_AWARENESS | 1         | 1     | 1       | 0     |
| ACCEPTANCE_CRITERIA     | 0         | 2     | 2       | 0     |
| PLAN_ACCURACY           | 1         | 1     | 0       | 0     |
| AD_COMPLIANCE           | 0         | 1     | 0       | 0     |
| **TOTAL**               | **3**     | **8** | **5**   | **0** |

**Overall Status**: ⚠️ AMENDMENTS REQUIRED — 3 critical issues must be addressed before implementation.

---

## Artifacts Analyzed

| Artifact            | Location                                    | Compliance Check  |
|---------------------|---------------------------------------------|-------------------|
| A-Specification     | `.claude/resources/knowledge-mcp-a-spec.md` | Reference         |
| Implementation Plan | `.claude/resources/plan.md`                 | ✗ Issues Found    |
| Task List           | `.claude/resources/tasks.md`                | ✗ Issues Found    |
| CLAUDE.md           | `/CLAUDE.md`                                | Reference         |
| python.md           | `.claude/memory/python.md`                  | Reference         |
| testing.md          | `.claude/memory/testing.md`                 | Reference         |
| security.md         | `.claude/memory/security.md`                | Reference         |

---

## Part 1: Tasks.md Compliance Findings

### COV-001 [HIGH] — 5 A-Spec Requirements Not Mapped to Tasks

**Location**: tasks.md requirements traceability

**Description**: The following A-Spec requirements have no corresponding tasks or only implicit coverage:

| Requirement      | Category                 | Priority    | Status                               |
|------------------|--------------------------|-------------|--------------------------------------|
| A-REQ-DATA-003   | document_type enum       | Must Have   | ❌ No explicit task                   |
| A-REQ-INGEST-004 | Metadata extraction      | Must Have   | ⚠️ Partial (spread across ingestors) |
| A-REQ-PERF-001   | Query latency SLO        | Should Have | ❌ No task                            |
| A-REQ-PERF-002   | Ingestion throughput SLO | Should Have | ❌ No task                            |
| A-REQ-PERF-003   | Memory management        | Must Have   | ❌ No explicit task                   |

**Standard Violated**: Constitution requires 100% requirement traceability.

**Recommendation**:
- Add Task 3.10: "Implement document_type enumeration validation" for A-REQ-DATA-003
- Add Task 3.11: "Implement streaming document processing" for A-REQ-PERF-003
- Add Task 7.7: "Performance benchmark tests" for A-REQ-PERF-001, A-REQ-PERF-002
- Consolidate A-REQ-INGEST-004 coverage across Tasks 3.2-3.4 with explicit acceptance criteria

---

### COV-002 [MEDIUM] — "(partial)" Requirement References Ambiguous

**Location**: Multiple tasks (1.1, 2.3, etc.)

**Description**: Several tasks reference requirements as "(partial)" without specifying which sub-requirements are covered:

```
TASK-001: A-REQ-MAINT-002 (partial)
TASK-008: A-REQ-IF-002 (partial)
```

**Impact**: Cannot verify complete coverage without cross-referencing all partial tasks.

**Recommendation**: Each "(partial)" reference should specify:
```
**Partial Coverage of A-REQ-IF-002:**
- This task covers: Batch embedding API calls (§5.2 bullet 3)
- Other tasks: TASK-007 covers model selection, TASK-009 covers dimension validation
```

---

### STD-001 [CRITICAL] — Python Standards Not Consistently Required in Tasks

**Location**: Tasks 3.3, 3.4, 3.6, 3.7, 3.8, 3.9

**Description**: Per `python.md` §4.1 and §3, all code must have:
- Complete type hints on all parameters and return types
- Google-style docstrings
- Pyright strict mode compliance

The following tasks lack these acceptance criteria:

| Task                            | Missing Criteria                    |
|---------------------------------|-------------------------------------|
| 3.3 (DOCX Ingestor)             | No "type hints per python.md §4.1"  |
| 3.4 (Markdown Ingestor)         | No "type hints per python.md §4.1"  |
| 3.6 (Normative Detection)       | No docstring or Pyright requirement |
| 3.7 (Chunk Type Classifier)     | No docstring or Pyright requirement |
| 3.8 (Cross-Reference Extractor) | No docstring or Pyright requirement |

**Standard Violated**: `python.md` §4.1 — "All function parameters MUST have type hints"

**Recommendation**: Add to ALL code tasks:
```yaml
acceptance_criteria:
  - "All functions have complete type hints per python.md §4.1"
  - "Includes comprehensive docstrings per python.md §3"
  - "Pyright passes with zero errors"
```

---

### STD-002 [HIGH] — Testing Standards Inconsistently Applied

**Location**: Tasks 2.4, 4.3, 5.9, 6.4

**Description**: Per `testing.md` §5.1, all tests must use AAA pattern (Arrange-Act-Assert). Only Task 2.4 (Embedder Tests) explicitly requires this. Other test tasks lack:

| Required Pattern           | Tasks Missing It       |
|----------------------------|------------------------|
| AAA pattern                | 4.3, 5.9, 6.4, 7.1-7.6 |
| Mock library specification | 4.3, 5.9, 6.4          |
| Coverage target per module | All test tasks         |

**Standard Violated**: `testing.md` §5.1 — "Uses AAA pattern (Arrange-Act-Assert)"

**Recommendation**: Standardize all test task acceptance criteria:
```yaml
acceptance_criteria:
  - "Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1"
  - "Uses unittest.mock for mocking external dependencies"
  - "Achieves ≥85% coverage for module under test"
```

---

### STD-003 [HIGH] — Branch and Function Coverage Targets Missing

**Location**: Task 7.1 (Coverage Configuration)

**Description**: Task 7.1 specifies "≥80% line coverage" but `testing.md` requires three metrics:

| Metric            | testing.md Requirement  | Task 7.1        |
|-------------------|-------------------------|-----------------|
| Line Coverage     | 80% minimum, 90% target | ✓ 80% stated    |
| Branch Coverage   | 75% minimum, 85% target | ❌ Not mentioned |
| Function Coverage | 85% minimum, 95% target | ❌ Not mentioned |

**Standard Violated**: `testing.md` §4.1 — Coverage thresholds

**Recommendation**: Update Task 7.1 acceptance criteria:
```yaml
acceptance_criteria:
  - "Line coverage ≥80% (target 90%)"
  - "Branch coverage ≥75% (target 85%)"
  - "Function coverage ≥85% (target 95%)"
  - "pytest-cov configured with --cov-branch flag"
```

---

### STD-004 [MEDIUM] — Security Standards Not Referenced in Relevant Tasks

**Location**: Tasks 1.5, 2.1, 5.1

**Description**: Per `security.md` §7.2, sensitive data must never be logged. Tasks that handle API keys lack explicit security criteria:

| Task                  | Security Concern  | Missing Criteria              |
|-----------------------|-------------------|-------------------------------|
| 1.5 (Logging Setup)   | API key redaction | No verification method        |
| 2.1 (OpenAI Embedder) | API key in errors | No error message sanitization |
| 5.1 (MCP Server)      | Request logging   | No sensitive data filtering   |

**Standard Violated**: `security.md` §7.2 — "Never log sensitive data"

**Recommendation**: Add to Tasks 1.5, 2.1, 5.1:
```yaml
acceptance_criteria:
  - "Logs do not contain API keys per security.md §7.2"
  - "Error messages sanitize config.openai_api_key, config.qdrant_api_key"
  - "Unit tests verify sensitive field redaction"
```

---

### ECA-001 [CRITICAL] — Existing Code Not Properly Characterized

**Location**: Plan §1.2 Current State Analysis

**Description**: Three files exist with implementations, but plan and tasks don't properly specify refactor vs. preserve vs. extend:

| File                    | Plan Status  | Actual Status     | Required Action                       |
|-------------------------|--------------|-------------------|---------------------------------------|
| `models/chunk.py`       | ✅ Complete   | ✅ Complete        | **PRESERVE** — No tasks should modify |
| `utils/config.py`       | ✅ Complete   | ✅ Complete        | **PRESERVE** — No tasks should modify |
| `store/qdrant_store.py` | ✅ Partial    | ⚠️ Needs refactor | **REFACTOR** — Must inherit BaseStore |

**Problem**: Task 4.2 says "Refactor QdrantStore to inherit from BaseStore" but lacks:
- Explicit preservation of existing public API
- Regression test requirement
- No-breaking-change verification

**Recommendation**: Update Task 4.2:
```yaml
description: "Refactor QdrantStore to inherit from BaseStore while preserving existing API"
acceptance_criteria:
  - "Inherits from BaseStore abstract class"
  - "Existing public API unchanged: search(), add_chunks(), get_stats()"
  - "Existing tests (if any) continue to pass"
  - "No breaking changes to method signatures"
```

---

### ECA-002 [HIGH] — Missing Code Actions for Existing Files

**Location**: Tasks.md Phase 4

**Description**: Tasks reference existing code but don't specify the action:

| Task   | References               | Missing Specification                  |
|--------|--------------------------|----------------------------------------|
| 4.1    | BaseStore abstract class | Should state "CREATE new file"         |
| 4.2    | QdrantStore              | Should state "REFACTOR existing file"  |
| 4.3    | ChromaDB store           | Should state "CREATE new file"         |
| 4.4    | RRF fusion               | Should state "CREATE search/hybrid.py" |

**Recommendation**: Add action prefix to all task descriptions:
- `[CREATE]` — New file
- `[REFACTOR]` — Modify existing file, preserve API
- `[EXTEND]` — Add to existing file without breaking changes
- `[DELETE]` — Remove file or code

---

### ECA-003 [MEDIUM] — Tasks Don't Reference Existing Test Fixtures

**Location**: Tasks 2.4, 4.3, 5.9

**Description**: `tests/conftest.py` defines fixtures (`mock_config`, `sample_chunk`, `mock_qdrant_client`, `mock_openai_client`) that test tasks should use, but no tasks reference them.

**Recommendation**: Add to test tasks:
```yaml
acceptance_criteria:
  - "Uses existing fixtures from conftest.py: mock_config, sample_chunk"
  - "Adds new fixtures to conftest.py for reuse across test modules"
```

---

### ACC-001 [HIGH] — Vague Acceptance Criteria

**Location**: Multiple tasks

**Description**: Several acceptance criteria are not verifiable:

| Task  | Vague Criterion                                                | Issue                             |
|-------|----------------------------------------------------------------|-----------------------------------|
| 1.5   | "Never logs sensitive data"                                    | How to verify "never"?            |
| 2.1   | "Raises appropriate exceptions"                                | Which exceptions in which cases?  |
| 3.5   | "Handles chunk splitting at sentence boundaries when possible" | What is "when possible"?          |
| 4.5   | "Implements RRF fusion algorithm"                              | No formula or test case specified |

**Recommendation**: Make criteria measurable:
```yaml
# Instead of "Never logs sensitive data":
- "Log output grep for 'sk-' and 'key' returns zero matches"
- "Unit test verifies config.openai_api_key not in any log message"

# Instead of "Raises appropriate exceptions":
- "Raises ConnectionError on network failure"
- "Raises TimeoutError after 3 failed retries"
- "Raises EmbeddingError if embedding dimension mismatch"

# Instead of "when possible":
- "Splits at sentence boundaries using nltk.sent_tokenize"
- "Falls back to space boundaries if sentence detection fails"
- "Never splits mid-word"

# Instead of "Implements RRF":
- "RRF_score = Σ 1/(60 + rank_i) per A-REQ-SEARCH-002"
- "Unit test with known ranks verifies formula"
```

---

### ACC-002 [HIGH] — Missing Error Path Specifications

**Location**: Tasks 3.2-3.4 (Ingestors), 5.2-5.7 (MCP Tools)

**Description**: Tasks specify success paths but not error handling:

| Task                 | Missing Error Specification                 |
|----------------------|---------------------------------------------|
| 3.2 PDF Ingestor     | What if PDF is encrypted? Corrupted?        |
| 3.3 DOCX Ingestor    | What if file is actually .doc (old format)? |
| 5.2 knowledge_search | What if vector store unreachable?           |
| 5.5 knowledge_stats  | What if collection empty?                   |

**Standard Violated**: A-REQ-REL-001 requires structured error responses.

**Recommendation**: Add error handling criteria:
```yaml
acceptance_criteria:
  - "Returns error response per A-REQ-REL-001 on failure"
  - "Error codes from A-REQ-DATA-004: connection_error, timeout_error, etc."
  - "Tests verify all error paths return valid error schema"
```

---

### ACC-003 [MEDIUM] — CLI Exit Codes Not Verified

**Location**: Tasks 6.1-6.3

**Description**: A-REQ-CLI-001 specifies exit codes (0, 1, 2, 3) but tasks don't verify them:

| Exit Code  | Meaning             | Verification Task  |
|------------|---------------------|--------------------|
| 0          | Success             | Not specified      |
| 1          | Partial failure     | Not specified      |
| 2          | Complete failure    | Not specified      |
| 3          | Configuration error | Not specified      |

**Recommendation**: Add to Task 6.4:
```yaml
acceptance_criteria:
  - "Exit code 0 on successful ingest"
  - "Exit code 1 if some files fail"
  - "Exit code 2 if no files processed"
  - "Exit code 3 on configuration error"
  - "Tests use Click's CliRunner to verify exit codes"
```

---

### ACC-004 [MEDIUM] — DocumentSection Dataclass Referenced but Not Defined

**Location**: Task 3.5 (Hierarchical Chunker)

**Description**: Task references `DocumentSection` dataclass in acceptance criteria, but no task creates this class. It's not in existing code either.

**Recommendation**: Either:
1. Add `DocumentSection` creation to Task 3.1 (Base Ingestor)
2. Or specify in Task 3.5: "Define DocumentSection dataclass in chunk/models.py"

---

## Part 2: Plan.md Compliance Findings

### PLA-001 [CRITICAL] — Current State Analysis Incomplete

**Location**: Plan §1.2 Current State Analysis

**Description**: The plan's assessment of existing code is incomplete:

| Component         | Plan Says                   | Actual State                           | Gap                                    |
|-------------------|-----------------------------|----------------------------------------|----------------------------------------|
| `server.py`       | ❌ Missing                   | ❌ Missing but imported                 | Plan should note import breaks package |
| `qdrant_store.py` | "needs response formatting" | Missing BaseStore, RRF, error handling | Understates refactor scope             |
| CLI               | ❌ Missing                   | `__main__.py` exists                   | Partial implementation present         |

**Impact**: Tasks may underestimate refactoring effort.

**Recommendation**: Update Plan §1.2:
```markdown
| QdrantStore | ⚠️ Needs Refactor | `store/qdrant_store.py` | (1) Add BaseStore inheritance, (2) Update response format, (3) Add error handling, (4) Integrate with search layer for RRF |
| server.py | ❌ BLOCKER | Import exists in __init__.py | Package cannot import until created |
```

---

### PLA-002 [HIGH] — AD-002 and AD-004 Implementation Unclear

**Location**: Plan §2 Architecture Decisions

**Description**: Architecture decisions describe WHAT but not HOW they apply to existing code:

| AD                  | Issue                                                        |
|---------------------|--------------------------------------------------------------|
| AD-002 (BaseStore)  | Doesn't specify QdrantStore refactor steps                   |
| AD-004 (RRF Fusion) | Doesn't clarify if Qdrant native hybrid or application-level |

**Recommendation**: Add implementation notes:
```markdown
### AD-002: Vector Store Abstraction
...
**Implementation Notes:**
- Create `store/base.py` with BaseStore ABC
- Refactor `qdrant_store.py` to inherit from BaseStore
- Preserve existing public API (search, add_chunks, get_stats)
- Create `chromadb_store.py` with same interface

### AD-004: Hybrid Search Implementation
...
**Implementation Notes:**
- Use Qdrant native hybrid for Qdrant backend (already configured)
- Implement application-level RRF in `search/hybrid.py` for ChromaDB parity
- RRF formula: score(d) = Σ 1/(k + rank_i(d)) where k=60
```

---

### PLA-003 [HIGH] — Verification Strategy Missing Metrics

**Location**: Plan §4 Verification Strategy

**Description**: Plan specifies "≥80% line coverage" but testing.md requires three metrics:

| Metric            | testing.md           | Plan        |
|-------------------|----------------------|-------------|
| Line Coverage     | 80% min / 90% target | ✓ Mentioned |
| Branch Coverage   | 75% min / 85% target | ❌ Missing   |
| Function Coverage | 85% min / 95% target | ❌ Missing   |

**Recommendation**: Update Plan §4.1:
```markdown
### 4.1 Unit Testing

| Metric            | Minimum   | Target   |
|-------------------|-----------|----------|
| Line Coverage     | 80%       | 90%      |
| Branch Coverage   | 75%       | 85%      |
| Function Coverage | 85%       | 95%      |
```

---

## Summary: Required Amendments

### Critical (Block Implementation)

1. **ECA-001**: Add explicit PRESERVE/REFACTOR/CREATE actions for existing files
2. **STD-001**: Add python.md type hint and docstring requirements to all code tasks
3. **PLA-001**: Update plan current state to note server.py import blocker

### High Priority (Before Phase 1 Complete)

4. **COV-001**: Add tasks for 5 unmapped requirements
5. **STD-002**: Add AAA pattern requirement to all test tasks
6. **STD-003**: Add branch and function coverage targets
7. **ACC-001**: Make all acceptance criteria measurable
8. **ACC-002**: Add error path specifications to ingestor and tool tasks
9. **PLA-002**: Add implementation notes to AD-002 and AD-004
10. **PLA-003**: Add branch/function coverage to verification strategy

### Medium Priority (Before Phase 3)

11. **COV-002**: Clarify all "(partial)" requirement references
12. **STD-004**: Add security.md criteria to logging and API tasks
13. **ECA-002**: Add action prefix to all task descriptions
14. **ECA-003**: Reference existing test fixtures
15. **ACC-003**: Add CLI exit code verification
16. **ACC-004**: Define DocumentSection dataclass location

---

## Existing Code Action Summary

| File                        | Action       | Tasks Affected                            |
|-----------------------------|--------------|-------------------------------------------|
| `models/chunk.py`           | **PRESERVE** | None — already complete                   |
| `utils/config.py`           | **PRESERVE** | None — already complete                   |
| `store/qdrant_store.py`     | **REFACTOR** | 4.2 — add BaseStore inheritance           |
| `__init__.py`               | **PRESERVE** | None — import fixed by creating server.py |
| `__main__.py`               | **EXTEND**   | 6.3 — add CLI argument parsing            |
| `tests/conftest.py`         | **EXTEND**   | Test tasks — add new fixtures             |
| `tests/unit/test_config.py` | **PRESERVE** | None — tests pass                         |

---

## Next Steps

1. **Run `/speckit.clarify`** to amend plan.md and tasks.md with corrections
2. **Or approve and proceed** with findings noted as implementation guidance

---

*End of Report*