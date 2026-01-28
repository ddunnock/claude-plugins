# Phase 5: Extended Features - User Acceptance Tests

**Created:** 2026-01-27
**Status:** PASSED
**Tester:** User

## Test Overview

Phase 5 delivered:
- CLI framework with Typer (`knowledge` command)
- Document ingestion command (`knowledge ingest docs`)
- Local embeddings via sentence-transformers
- Reranker (Cohere + local cross-encoder)
- Collection verify command (`knowledge verify`)

---

## Test 1: CLI Help Display

**What we're testing:** The `knowledge` CLI shows helpful usage information.

**Steps:**
```bash
poetry run knowledge --help
```

**Expected:** Shows "Knowledge MCP" description with available commands.

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Test 2: Ingest Docs Help

**What we're testing:** The `knowledge ingest docs` subcommand shows its options.

**Steps:**
```bash
poetry run knowledge ingest docs --help
```

**Expected:** Shows path argument, `--collection/-c` option, `--recursive/-r` flag.

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Test 3: Verify Command Help

**What we're testing:** The `knowledge verify` command shows its options.

**Steps:**
```bash
poetry run knowledge verify --help
```

**Expected:** Shows `--collection/-c` option and `--embeddings/-e` flag for dimension validation.

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Test 4: LocalEmbedder Import

**What we're testing:** LocalEmbedder can be imported and used.

**Steps:**
```bash
poetry run python -c "from knowledge_mcp.embed import LocalEmbedder; e = LocalEmbedder(); print(f'Dimensions: {e.dimensions}')"
```

**Expected:** Prints "Dimensions: 384" (all-MiniLM-L6-v2 model).

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Test 5: create_embedder Factory

**What we're testing:** Factory function selects embedder based on config.

**Steps:**
```bash
poetry run python -c "
from knowledge_mcp.embed import create_embedder, LocalEmbedder
from knowledge_mcp.utils.config import KnowledgeConfig
config = KnowledgeConfig(embedding_provider='local')
embedder = create_embedder(config)
print(f'Type: {type(embedder).__name__}')
print(f'Dimensions: {embedder.dimensions}')
"
```

**Expected:** Type is LocalEmbedder, Dimensions is 384.

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Test 6: Reranker Import

**What we're testing:** Reranker class can be imported and initialized with local provider.

**Steps:**
```bash
poetry run python -c "from knowledge_mcp.search.reranker import Reranker; r = Reranker(provider='local'); print('Reranker initialized')"
```

**Expected:** Prints "Reranker initialized" without errors.

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Test 7: All Tests Pass

**What we're testing:** The complete test suite passes.

**Steps:**
```bash
poetry run pytest tests/ -v --tb=short 2>&1 | tail -20
```

**Expected:** All tests pass, no failures.

**Status:** [ ] Pass / [ ] Fail / [ ] Skip

**Notes:**

---

## Summary

| Test | Description | Status |
|------|-------------|--------|
| 1 | CLI Help Display | PASS |
| 2 | Ingest Docs Help | PASS |
| 3 | Verify Command Help | PASS |
| 4 | LocalEmbedder Import | PASS |
| 5 | create_embedder Factory | PASS |
| 6 | Reranker Import | PASS |
| 7 | All Tests Pass | PASS (400/400, 86.8% coverage) |

**Overall Result:** PASSED

## Notes

During verification, 7 test failures were discovered and fixed:
1. `test_validate_missing_openai_key` - Updated assertion to match new validation message that includes "when embedding_provider=openai"
2. `test_main.py` tests (6 tests) - Updated to reflect that `__main__.py` now delegates to Typer CLI instead of calling asyncio.run + server.main

All tests now pass with 86.80% coverage (exceeds 80% threshold).
