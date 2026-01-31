# AIAG-VDA FMEA Handbook (2019 Edition)

## Overview

The AIAG-VDA FMEA Handbook is the primary reference for Failure Mode and Effects Analysis methodology used by RCCA skills.

**Standard:** AIAG-VDA FMEA Handbook
**Edition:** 1st Edition (2019)
**Publisher:** Automotive Industry Action Group (AIAG)

## Required For

| RCCA Skill | Usage |
|------------|-------|
| FMEA Analysis | Action Priority (AP) calculation, severity/occurrence/detection scales |
| Problem Definition | Severity classification lookup |
| RCCA Master | Risk prioritization, failure mode patterns |

## Critical Version Requirement

**You MUST use the 2019 Edition, NOT older editions.**

| Edition | Published | Risk Metric | Compatible |
|---------|-----------|-------------|------------|
| AIAG-VDA FMEA Handbook | 2019 | Action Priority (AP) | YES |
| AIAG FMEA-4 | 2008 | Risk Priority Number (RPN) | NO |
| AIAG FMEA-3 | 2001 | RPN | NO |

The 2019 edition replaced RPN (Risk Priority Number) with Action Priority (AP) methodology. RCCA skills are designed for AP-based analysis. Using older editions will result in:

- Missing Action Priority lookup tables
- Incompatible severity/occurrence definitions
- Validation failures during ingestion

## Acquisition Options

### 1. AIAG Store (Official)

**Link:** https://www.aiag.org/store/publications/details?ProductCode=FMEA-2

**Price:** ~$495 USD (PDF + Print bundle) or ~$350 USD (PDF only)

**Format:** PDF

**Notes:**
- Most comprehensive option with full tables and examples
- Required for regulatory compliance in automotive industry
- Includes both Process FMEA and Design FMEA guidance

### 2. Institutional Access

Many organizations have AIAG membership or standards subscriptions:

- **Automotive OEMs:** Ford, GM, Stellantis typically provide to suppliers
- **Tier 1 Suppliers:** Often have site licenses
- **Universities:** Some engineering programs have access via libraries
- **Standards Subscriptions:** SAE Mobilus, Techstreet may include

**Check with:**
- Your organization's quality department
- Engineering standards library
- Procurement/purchasing team

### 3. Free Alternative: NASA FMEA Handbook

If the AIAG-VDA handbook is not available, NASA provides a public domain alternative:

**Link:** https://www.nasa.gov/reference/fmea-handbook
**Price:** Free (public domain)
**Format:** PDF

**Limitations:**
- Does NOT include AIAG-VDA Action Priority tables
- Different severity/occurrence definitions
- Aerospace-focused rather than automotive
- RCCA skills may show warnings about missing AP tables

**Use when:**
- Budget constraints prevent AIAG purchase
- Learning FMEA methodology (not production use)
- Aerospace/defense applications

## Ingestion Command

After acquiring the PDF, ingest with validation:

```bash
cd mcps/knowledge-mcp

poetry run python -m knowledge_mcp.cli.ingest docs aiag-vda-fmea-2019.pdf \
  --collection rcca_standards \
  --document-id aiag-vda-fmea-2019 \
  --validate
```

**Document ID Pattern:** Use lowercase with hyphens: `aiag-vda-fmea-2019`

## Expected Validation Results

After successful ingestion, validation should report:

```
Validating collection: rcca_standards

Critical Tables:
  [PASS] Action Priority Matrix (10x10 S*O table)
    - Severity scale 1-10 complete
    - Occurrence scale 1-10 complete
    - AP values (H/M/L) present
    - Matrix structure intact

  [PASS] Severity Rating Scale
    - 10 severity levels defined
    - Effect descriptions present

  [PASS] Occurrence Rating Scale
    - 10 occurrence levels defined
    - Frequency criteria present

  [PASS] Detection Rating Scale
    - 10 detection levels defined
    - Control method descriptions present

Chunks: 1,200-1,500 (typical)
Metadata: standard=AIAG-VDA FMEA 2019, domain=fmea, version=2019
```

## Troubleshooting

### "Action Priority table not found"

1. Verify you have the 2019 edition (check document title/cover page)
2. Check PDF pages 40-60 for the AP table manually
3. Re-ingest with `--verbose` to see parsing details

### "Table structure not preserved"

1. Run `knowledge validate collection rcca_standards --verbose`
2. Check if table spans multiple chunks (expected for large tables)
3. Verify hybrid search retrieves related chunks together

### Chunks count too low (<500)

1. Check if PDF has text layer (not scanned image)
2. Try re-downloading the PDF from AIAG
3. Check for DRM protection that may block parsing

## Related Standards

- **MIL-STD-882E:** Complements FMEA with hazard severity categories
- **ISO 9001:2015:** Provides CAPA (Corrective/Preventive Action) templates
- **SAE J1739:** Alternative FMEA standard (uses RPN, not AP)

---

*Document type: Standards Acquisition Guide*
*Last updated: 2026-01-31*
