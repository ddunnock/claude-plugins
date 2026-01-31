# How to Ingest RCCA Standards

This guide walks through ingesting RCCA (Root Cause and Corrective Action) standards into the knowledge-mcp for use with RCCA skills.

## Prerequisites

### 1. Knowledge MCP Installed

```bash
cd mcps/knowledge-mcp
poetry install
```

### 2. Environment Configured

Ensure your `.env` file or environment has:

```bash
# Required
OPENAI_API_KEY=sk-...

# For Qdrant Cloud (recommended)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Or use local ChromaDB (automatic fallback)
# CHROMADB_PATH=./data/chromadb
```

### 3. Standards Documents Acquired

Obtain the PDF files for standards you want to ingest. See the acquisition guides:

- [AIAG-VDA FMEA 2019](../standards-acquisition/aiag-vda-2019.md) - ~$495 or use NASA alternative
- [MIL-STD-882E](../standards-acquisition/mil-std-882e.md) - FREE (public domain)
- [ISO 9001:2015](../standards-acquisition/iso-9001-2015.md) - ~$180 or institutional access

## Quick Start

Ingest all three core RCCA standards:

```bash
cd mcps/knowledge-mcp

# 1. Ingest AIAG-VDA FMEA (or NASA alternative)
poetry run python -m knowledge_mcp.cli.ingest docs ./standards/aiag-vda-fmea-2019.pdf \
  --collection rcca_standards \
  --document-id aiag-vda-fmea-2019 \
  --validate

# 2. Ingest MIL-STD-882E (free)
poetry run python -m knowledge_mcp.cli.ingest docs ./standards/mil-std-882e.pdf \
  --collection rcca_standards \
  --document-id mil-std-882e \
  --validate

# 3. Ingest ISO 9001:2015
poetry run python -m knowledge_mcp.cli.ingest docs ./standards/iso-9001-2015.pdf \
  --collection rcca_standards \
  --document-id iso-9001-2015 \
  --validate
```

## Step-by-Step Process

### Step 1: Place Standards in a Directory

Create a directory for your standards:

```bash
mkdir -p mcps/knowledge-mcp/data/standards
```

Copy your PDF files there:

```
data/standards/
  aiag-vda-fmea-2019.pdf
  mil-std-882e.pdf
  iso-9001-2015.pdf
```

### Step 2: Ingest Each Standard

Run the ingest command for each document:

```bash
poetry run python -m knowledge_mcp.cli.ingest docs ./data/standards/aiag-vda-fmea-2019.pdf \
  --collection rcca_standards \
  --document-id aiag-vda-fmea-2019 \
  --validate
```

**Command options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--collection` | Target collection name | `rcca_standards` |
| `--document-id` | Unique identifier for the document | `aiag-vda-fmea-2019` |
| `--validate` | Run validation tests after ingestion | (flag) |
| `--verbose` | Show detailed progress | (flag) |
| `--chunk-size` | Override target chunk size in tokens | `500` |

### Step 3: Review Validation Results

After ingestion with `--validate`, you'll see validation output:

```
Ingesting 1 document(s)...

  [OK] aiag-vda-fmea-2019.pdf: 1,247 chunks
    Parsing: 100% ========================
    Chunking: 100% =======================
    Embedding: 100% ======================
    Storing: 100% ========================

Running validation tests...

  [PASS] Action Priority Matrix (10x10 S*O table)
    - Severity scale 1-10 complete
    - Occurrence scale 1-10 complete
    - AP values (H/M/L) present
    - Matrix structure intact

Summary:
  Processed: 1/1 documents
  Total chunks: 1,247
  Validation: PASSED

Ingestion complete.
```

### Step 4: Validate the Full Collection

After ingesting all standards, run a full collection validation:

```bash
poetry run python -m knowledge_mcp.cli.validate collection rcca_standards --verbose
```

Expected output for a complete RCCA collection:

```
Validating collection: rcca_standards

Critical Tables:
  [PASS] AIAG-VDA Action Priority Matrix: 3 chunks
  [PASS] MIL-STD-882E Severity Categories: 2 chunks
  [PASS] ISO 9001:2015 CAPA Process: 4 chunks

Metadata Coverage:
  [OK] 1,547/1,547 chunks have 'standard' field
  [OK] 1,547/1,547 chunks have 'domain' field
  [OK] 1,547/1,547 chunks have 'version' field

Query Tests:
  [PASS] "Action Priority severity 8 occurrence 3" -> 5 results
  [PASS] "Severity category catastrophic" -> 3 results
  [PASS] "corrective action process ISO 9001" -> 4 results

Overall: 9/9 tests passed (100%)

[OK] Collection ready for RCCA skills
```

## Understanding Validation Results

### Pass/Fail Status

| Status | Meaning | Action |
|--------|---------|--------|
| PASS | Critical table found and complete | None needed |
| WARN | Table found but incomplete | Review manually |
| FAIL | Table not found | Re-ingest or check source |

### Chunk Counts by Standard

Expected chunk counts (approximate):

| Standard | Typical Chunks | Min Expected |
|----------|----------------|--------------|
| AIAG-VDA FMEA 2019 | 1,200-1,500 | 500 |
| MIL-STD-882E | 200-400 | 100 |
| ISO 9001:2015 | 100-200 | 50 |

Low chunk counts may indicate:
- Scanned PDF without text layer
- DRM protection blocking parsing
- Corrupted or incomplete PDF

### Metadata Fields

Each chunk is enriched with RCCA metadata:

| Field | Description | Example |
|-------|-------------|---------|
| `standard` | Full standard name | `AIAG-VDA FMEA 2019` |
| `domain` | Subject domain | `fmea`, `safety`, `quality` |
| `version` | Edition/revision | `2019`, `2012`, `2015` |
| `standard_family` | Classification | `fmea_methodology`, `safety`, `quality` |

## Troubleshooting

### "No text extracted from PDF"

**Cause:** PDF is a scanned image without OCR text layer.

**Solution:**
1. Use Adobe Acrobat or similar to run OCR
2. Or obtain a native PDF (not scanned) from the source

### "Validation failed: Table not found"

**Cause:** Critical lookup table wasn't detected during parsing.

**Solutions:**
1. Check you have the correct standard version
2. Run with `--verbose` to see parsing details
3. Manually verify the table exists in the PDF

### "Connection refused" or "API timeout"

**Cause:** Qdrant Cloud or OpenAI API unreachable.

**Solutions:**
1. Check your API keys are valid
2. Verify network connectivity
3. Try using local ChromaDB fallback (remove QDRANT_URL)

### "Embedding limit exceeded"

**Cause:** OpenAI rate limits hit for large documents.

**Solutions:**
1. Wait and retry (rate limits reset)
2. Use `--batch-size 50` to reduce concurrent requests
3. Enable embedding cache (default) to reuse on retries

### Re-ingesting a Standard

To replace an existing standard (e.g., with updated version):

```bash
# Delete existing document chunks
poetry run python -m knowledge_mcp.cli.delete docs aiag-vda-fmea-2019 \
  --collection rcca_standards

# Ingest new version
poetry run python -m knowledge_mcp.cli.ingest docs ./standards/aiag-vda-fmea-2019-updated.pdf \
  --collection rcca_standards \
  --document-id aiag-vda-fmea-2019 \
  --validate
```

## Metadata Extraction

Document IDs are used to extract RCCA metadata automatically:

| Document ID Pattern | Extracted Standard | Domain |
|--------------------|-------------------|--------|
| `aiag-vda-fmea-2019` | AIAG-VDA FMEA 2019 | fmea |
| `mil-std-882e` | MIL-STD-882E | safety |
| `iso-9001-2015` | ISO 9001:2015 | quality |
| `sae-j1739-2009` | SAE J1739:2009 | fmea |
| `iec-61025-2006` | IEC 61025:2006 | reliability |

Use consistent document ID patterns for proper metadata extraction.

## Collection Naming

Recommended collection name includes the embedding model for clarity:

```bash
# With embedding model suffix
--collection rcca_standards_te3small

# Or simple name
--collection rcca_standards
```

If you change embedding models, create a new collection (embeddings are not compatible across models).

## Next Steps

After successful ingestion:

1. **Use RCCA Skills:** Skills automatically query the ingested standards
2. **Run FMEA Analysis:** Action Priority lookup uses AIAG-VDA tables
3. **Perform 5 Whys:** Root cause patterns validated against standards
4. **Execute RCCA Master:** Full workflow with standards-grounded citations

---

*Document type: How-To Guide*
*Last updated: 2026-01-31*
