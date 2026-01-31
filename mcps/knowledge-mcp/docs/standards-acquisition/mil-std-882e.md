# MIL-STD-882E: System Safety

## Overview

MIL-STD-882E is the U.S. Department of Defense standard for system safety practices. It provides severity categories and hazard classification that complement FMEA analysis.

**Standard:** MIL-STD-882E
**Title:** System Safety
**Edition:** Revision E (2012), Change 1 (2023)
**Publisher:** U.S. Department of Defense

## Public Domain - FREE

**This standard is public domain and freely available.**

No purchase required. No license needed. Direct download from official government sources.

## Required For

| RCCA Skill | Usage |
|------------|-------|
| Problem Definition | Hazard severity classification (Table I) |
| FMEA Analysis | Severity category alignment with defense/aerospace domains |
| FTA (Fault Tree Analysis) | Basic event probability categories |
| RCCA Master | Multi-domain severity harmonization |

## Download Links

### Primary Source (Official)

**Link:** https://quicksearch.dla.mil/Transient/6B82F8892B184E6CB7D8A53C49FF8C55.pdf

**Alternative:** Search "MIL-STD-882E" at https://quicksearch.dla.mil/

### Mirror Sources

If the primary link is unavailable:

- **NDE-ED.org:** https://www.nde-ed.org/NDEEngineering/SafeDesign/MIL-STD-882E.pdf
- **everyspec.com:** https://everyspec.com/MIL-STD/MIL-STD-0800-0899/MIL-STD-882E_41682/

### Version Notes

| Revision | Date | Status |
|----------|------|--------|
| MIL-STD-882E Change 1 | 2023 | Current |
| MIL-STD-882E | 2012 | Superseded (but still valid for most uses) |
| MIL-STD-882D | 2000 | Obsolete |

For RCCA purposes, either MIL-STD-882E (2012) or Change 1 (2023) is acceptable. The severity categories in Table I are unchanged.

## Critical Tables

### Table I: Hazard Severity Categories

This table is essential for severity classification:

| Category | Description | Personnel | Environment | Monetary |
|----------|-------------|-----------|-------------|----------|
| 1 | Catastrophic | Death or permanent total disability | Irreversible severe environmental damage | >$10M |
| 2 | Critical | Permanent partial disability | Reversible severe environmental damage | $1M-$10M |
| 3 | Marginal | Injury requiring hospitalization | Reversible moderate environmental damage | $100K-$1M |
| 4 | Negligible | Injury not requiring hospitalization | Minimal environmental damage | <$100K |

### Table II: Probability Levels

| Level | Description | Individual Item | Fleet/Inventory |
|-------|-------------|-----------------|-----------------|
| A | Frequent | Likely to occur often | Continuously experienced |
| B | Probable | Likely to occur several times | Will occur frequently |
| C | Occasional | Likely to occur sometime | Will occur several times |
| D | Remote | Unlikely but possible | Unlikely but can be expected |
| E | Improbable | So unlikely, assumed won't occur | Unlikely to occur |
| F | Eliminated | Incapable of occurrence | N/A |

## Ingestion Command

After downloading the PDF:

```bash
cd mcps/knowledge-mcp

poetry run python -m knowledge_mcp.cli.ingest docs mil-std-882e.pdf \
  --collection rcca_standards \
  --document-id mil-std-882e \
  --validate
```

**Document ID Pattern:** Use lowercase with hyphens: `mil-std-882e`

## Expected Validation Results

```
Validating collection: rcca_standards

Critical Tables:
  [PASS] Severity Categories (Table I)
    - Categories 1-4 present (Catastrophic, Critical, Marginal, Negligible)
    - All three dimensions (personnel, environmental, monetary)
    - Descriptions complete

  [PASS] Probability Levels (Table II)
    - Levels A-F present
    - Both individual and fleet criteria

Chunks: 200-400 (typical)
Metadata: standard=MIL-STD-882E, domain=safety, version=2012
```

## Integration with FMEA

MIL-STD-882E severity categories map to AIAG-VDA FMEA severity scale:

| MIL-STD-882E | FMEA Severity |
|--------------|---------------|
| 1 (Catastrophic) | 9-10 |
| 2 (Critical) | 7-8 |
| 3 (Marginal) | 4-6 |
| 4 (Negligible) | 1-3 |

RCCA skills use this mapping for multi-standard synthesis when both standards are ingested.

## Troubleshooting

### "Table I not found in results"

1. Search explicitly: `"severity categories Table I MIL-STD-882E"`
2. Check chunk metadata for `domain=safety`
3. Verify PDF was not corrupted during download

### PDF download blocked

Some corporate firewalls block .mil domains:

1. Try everyspec.com mirror
2. Use personal network/VPN
3. Request IT to whitelist quicksearch.dla.mil

### Old revision warning

If you ingested MIL-STD-882D instead of 882E:

1. Delete the old document: `knowledge delete docs mil-std-882d`
2. Download MIL-STD-882E (linked above)
3. Re-ingest with correct document-id

## Related Standards

- **AIAG-VDA FMEA 2019:** Primary FMEA methodology with Action Priority
- **ISO 9001:2015:** Quality management CAPA processes
- **NASA-STD-8719.13:** NASA safety standard (similar severity categories)
- **SAE ARP4761:** Aerospace safety assessment methodology

---

*Document type: Standards Acquisition Guide*
*Last updated: 2026-01-31*
