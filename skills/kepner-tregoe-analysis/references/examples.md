# Kepner-Tregoe Worked Examples

## Example 1: Problem Analysis - Manufacturing Bearing Failure

### Scenario
A manufacturing plant produces hydraulic pumps. Recently, field returns for bearing failures have increased significantly.

### Phase 2A: Deviation Statement

**Object**: Model H-450 hydraulic pumps
**Deviation**: Premature bearing failure (seizure) at 5,000-6,000 operating cycles

**Deviation Statement**: "Model H-450 hydraulic pumps are experiencing premature bearing seizure at 5,000-6,000 operating cycles."

### Phase 2B: IS/IS NOT Specification Matrix

| Dimension | IS | IS NOT | Distinction |
|-----------|-----|--------|-------------|
| **WHAT - Object** | Model H-450 pumps | Model H-400 pumps, H-500 pumps | H-450 uses smaller housing design |
| **WHAT - Defect** | Main drive bearing seizure | Motor failure, seal leaks, shaft wear | Only bearing affected |
| **WHAT - Type** | Units manufactured Jan-Mar 2024 | Units manufactured before Jan 2024 | Manufacturing date (Q1 2024 vs earlier) |
| **WHERE - Geography** | Customers in Southwest region (AZ, NM, NV) | Customers in Midwest, Northeast | High ambient temperature environment |
| **WHERE - On Unit** | Right-side bearing only | Left-side bearing | Right side is nearest exhaust port |
| **WHERE - Process** | Final assembly Station 3 | Stations 1, 2, 4, and other assembly lines | Station 3 uses automated torque tools |
| **WHEN - First observed** | January 28, 2024 | Before January 28, 2024 | New bearing supplier contract started Jan 1 |
| **WHEN - In lifecycle** | 5,000-6,000 cycles | Before 5,000 cycles, rated life is 15,000 | Failure at 1/3 of expected life |
| **WHEN - Pattern** | Intermittent, approximately 3-5 per week | Not constant, not random | Correlates with high-temperature days |
| **EXTENT - Quantity** | 47 of 280 units (17%) | 233 units (83%) | Affected units from specific batch range |
| **EXTENT - Severity** | Bearing seizes, pump inoperable | Complete motor burnout not occurring | Thermal cutout prevents total failure |
| **EXTENT - Trend** | Increasing (5→12→15→15 per month) | Stable or decreasing | Accelerating as more units reach cycle threshold |

### Phase 2C: Key Distinctions

1. **New bearing supplier (Jan 2024)**: Changed from SteelCo to BearingPro on Jan 1
2. **High ambient temperature (Southwest)**: Operating environment 15-20°C hotter
3. **Right-side location near exhaust**: Less cooling airflow
4. **Automated torque assembly (Station 3)**: Different installation method than other stations
5. **Specific batch range**: All affected from batches 24-001 through 24-037

### Phase 2D: Possible Causes (from Distinctions)

| # | Possible Cause | Source Distinction |
|---|----------------|-------------------|
| 1 | BearingPro bearings have tighter internal tolerance than SteelCo, causing thermal binding | New supplier |
| 2 | BearingPro bearings use different lubricant grade | New supplier |
| 3 | High ambient temp + reduced airflow exceeds thermal limits | SW region + right-side |
| 4 | Automated torque tools over-preloading bearings | Station 3 |
| 5 | Combination: Tighter tolerance + high temp = thermal expansion binding | Multiple |

### Phase 2E: Cause Testing

| Possible Cause | WHAT IS | WHAT IS NOT | WHERE IS | WHERE IS NOT | WHEN IS | WHEN IS NOT | EXTENT IS | EXTENT IS NOT | Score |
|----------------|---------|-------------|----------|--------------|---------|-------------|-----------|---------------|-------|
| 1. Tighter tolerance | ✓ H-450 uses new bearing | ✓ H-400/500 use old stock | ✓ SW has high temp | ? Midwest could also overheat | ✓ After Jan | ✓ Before Jan different supplier | ✓ 17% matches batch exposure | ✓ 83% not yet at threshold | 7/8 |
| 2. Different lubricant | ✓ New bearing | ✓ Old bearing | ? Not temp related | ✗ Should affect all locations | ✓ After Jan | ✓ Before Jan | ? Would expect more | ✗ Should be higher % | 4/8 |
| 3. Thermal limits | ✓ Bearing seizes | ✓ Only bearing | ✓ SW hot | ✓ Other regions OK | ? Always hot in SW | ✗ Should have always failed | ✓ Matches pattern | ✗ Should have seen before | 5/8 |
| 4. Over-torque | ✓ H-450 | ? Why only H-450? | ✗ Not location dependent | ✗ Should affect all | ✗ Station 3 not new | ✗ Would have seen before | ✗ Higher % expected | ✗ All Station 3 units | 2/8 |
| 5. Combination | ✓ H-450 + new bearing | ✓ Other models OK | ✓ SW high temp | ✓ Other regions OK | ✓ After Jan supplier change | ✓ Before Jan OK | ✓ SW + high cycles | ✓ Other conditions OK | 8/8 |

**Most Probable Cause**: #5 - The new BearingPro bearings have tighter internal tolerance. When combined with high ambient temperatures in the Southwest, thermal expansion causes the bearing to bind and seize.

### Phase 2F: Verification Plan

1. **Compare specifications**: Request tolerance specs from BearingPro vs. SteelCo
2. **Laboratory test**: Install BearingPro bearing in thermal chamber, cycle at elevated temperature
3. **Field test**: Install SteelCo bearing in Southwest customer unit, monitor performance
4. **Batch correlation**: Confirm 100% of failures are from Jan+ batches

### Verification Results
- SteelCo spec: 0.002" clearance | BearingPro spec: 0.0012" clearance (40% tighter)
- Lab test: BearingPro bearing seized at 65°C after 5,200 cycles; SteelCo ran 15,000+ at same temp
- **ROOT CAUSE CONFIRMED**

---

## Example 2: Decision Analysis - Software Selection

### Scenario
A company needs to select a new Customer Relationship Management (CRM) system.

### Phase 3A: Decision Statement

**Decision**: "Select a CRM system to improve sales pipeline visibility, customer communication tracking, and reporting capabilities."

### Phase 3B: Objectives Classification

**MUSTS (Mandatory):**

| MUST Criterion | Measurement | Pass/Fail Test |
|----------------|-------------|----------------|
| Cloud-based SaaS | Deployment model | Is it cloud-based? |
| SOC 2 Type II compliant | Security certification | Has current SOC 2 Type II? |
| Budget ≤ $50,000/year | Annual cost | Total annual cost ≤ $50K? |
| Integrates with Salesforce | Integration capability | Has Salesforce connector? |
| Mobile app available | Platform support | iOS and Android apps? |

**WANTS (Desired):**

| WANT | Direction | Weight | Rationale |
|------|-----------|--------|-----------|
| Ease of use / user adoption | Easier is better | 9 | Critical for success; failed CRMs in past |
| Customization flexibility | More is better | 7 | Need to match our process |
| Reporting capabilities | More robust is better | 8 | Key requirement |
| Vendor support quality | Better is better | 6 | Important but manageable |
| Implementation time | Shorter is better | 5 | Want quick, but not critical |
| Total cost of ownership | Lower is better | 7 | Budget conscious |

### Phase 3C: Alternatives

Alternatives: Salesforce Sales Cloud, HubSpot CRM, Pipedrive, Zoho CRM, Microsoft Dynamics 365

**MUST Screening:**

| Alternative | Cloud SaaS | SOC 2 | Budget ≤$50K | Salesforce Int | Mobile App | PASS/FAIL |
|-------------|------------|-------|--------------|----------------|------------|-----------|
| Salesforce Sales Cloud | ✓ | ✓ | ✓ ($45K) | N/A (is Salesforce) | ✓ | **PASS** |
| HubSpot CRM | ✓ | ✓ | ✓ ($42K) | ✓ | ✓ | **PASS** |
| Pipedrive | ✓ | ✓ | ✓ ($18K) | ✓ | ✓ | **PASS** |
| Zoho CRM | ✓ | ✓ | ✓ ($24K) | ✓ | ✓ | **PASS** |
| MS Dynamics 365 | ✓ | ✓ | ✗ ($72K) | ✓ | ✓ | **FAIL** |

### Phase 3D: Alternative Scoring

| WANT (Weight) | Salesforce | Score | HubSpot | Score | Pipedrive | Score | Zoho | Score |
|---------------|------------|-------|---------|-------|-----------|-------|------|-------|
| Ease of use (9) | 6 | 54 | 9 | 81 | 8 | 72 | 6 | 54 |
| Customization (7) | 9 | 63 | 7 | 49 | 5 | 35 | 8 | 56 |
| Reporting (8) | 9 | 72 | 8 | 64 | 6 | 48 | 7 | 56 |
| Vendor support (6) | 8 | 48 | 8 | 48 | 7 | 42 | 6 | 36 |
| Implementation (5) | 5 | 25 | 7 | 35 | 9 | 45 | 7 | 35 |
| Total cost (7) | 4 | 28 | 6 | 42 | 9 | 63 | 8 | 56 |
| **TOTAL** | | **290** | | **319** | | **305** | | **293** |

### Phase 3E: Risk Assessment (Top 2)

**HubSpot (Score: 319):**

| Adverse Consequence | Probability | Seriousness | Combined |
|--------------------|-------------|-------------|----------|
| Less customization limits future growth | M | M | MEDIUM |
| Team already trained on Salesforce, learning curve | M | M | MEDIUM |
| Data migration complexity | L | M | LOW |

**Pipedrive (Score: 305):**

| Adverse Consequence | Probability | Seriousness | Combined |
|--------------------|-------------|-------------|----------|
| Limited reporting requires workarounds | H | M | HIGH |
| Smaller vendor, acquisition risk | M | M | MEDIUM |
| Limited enterprise features as we grow | M | H | HIGH |

### Phase 3F: Decision

**Selected: HubSpot CRM**

**Rationale**: 
- Highest weighted score (319)
- Risks are manageable (all MEDIUM or LOW)
- Strong ease-of-use ratings critical for user adoption
- Within budget with good reporting capabilities
- Pipedrive scored close but has HIGH risks for scalability and reporting

---

## Example 3: Potential Problem Analysis - System Migration

### Scenario
The company is migrating its ERP system over a holiday weekend. PPA is conducted to anticipate and plan for risks.

### Phase 4A: Plan Statement

**Plan**: Migrate ERP system from on-premise Oracle to cloud SAP S/4HANA over Labor Day weekend (72-hour window).

**Critical Steps:**
1. Friday 6PM: Begin data freeze
2. Friday 9PM: Start data extraction
3. Saturday 6AM: Complete extraction, begin transformation
4. Saturday 6PM: Complete transformation, begin data load
5. Sunday 6AM: Complete load, begin validation
6. Sunday 6PM: Complete validation, begin user testing
7. Monday 6AM: Go-live decision gate
8. Monday 8AM: Users begin working in new system

### Phase 4B-4C: Potential Problem Identification and Evaluation

| Step | Potential Problem | Likelihood | Seriousness | Combined Risk |
|------|------------------|------------|-------------|---------------|
| 1 | Users continue entering transactions after freeze | M | H | HIGH |
| 2 | Data extraction runs longer than planned | M | M | MEDIUM |
| 2 | Network bottleneck slows extraction | L | M | LOW |
| 3 | Transformation scripts have errors | M | H | HIGH |
| 4 | Data load fails validation checks | M | H | HIGH |
| 5 | Validation finds data integrity issues | H | H | CRITICAL |
| 6 | Key users unavailable for testing | M | M | MEDIUM |
| 7 | Testing reveals critical functionality gaps | M | H | HIGH |
| 8 | Users can't log in / authentication fails | L | H | MEDIUM |

### Phase 4D-4E: Preventive and Contingent Actions

| Risk | Preventive Actions | Contingent Actions | Trigger |
|------|-------------------|-------------------|---------|
| **CRITICAL: Validation finds data integrity issues** | • Run pre-migration data cleansing<br>• Execute 3 dry-run migrations<br>• Build automated validation scripts | • Roll back to Oracle (tested procedure)<br>• Fix issues and retry next weekend | >2% critical records fail validation by Sunday 12PM |
| **HIGH: Users continue after freeze** | • Multiple communications (email, signs, pop-ups)<br>• System access restricted at 6PM<br>• Designate freeze monitor | • Identify late transactions<br>• Manual data entry into new system | Any transaction after 6PM Friday |
| **HIGH: Transformation scripts have errors** | • Test scripts on production copy<br>• Have developer on-call<br>• Build script versioning | • Revert to last good script version<br>• Apply manual fixes<br>• Extend transformation window | Error rate >0.1% during transformation |
| **HIGH: Data load fails validation** | • Pre-validate data quality<br>• Build incremental load capability | • Identify failed records<br>• Repair and reload subset<br>• Extend load window | >100 records fail load |
| **HIGH: Testing reveals functionality gaps** | • Complete user acceptance testing pre-migration<br>• Document workarounds for known gaps | • Implement workaround procedures<br>• Defer go-live if critical | Any P1 defect discovered in Sunday testing |
| **MEDIUM: Key users unavailable** | • Confirm availability in advance<br>• Identify backup testers | • Proceed with backup testers<br>• Schedule follow-up validation | Fewer than 3 of 5 key users available |

### Go/No-Go Criteria (Monday 6AM)

**GO if:**
- [ ] Data validation shows <0.5% error rate
- [ ] All critical business processes tested successfully
- [ ] No P1 defects open
- [ ] Authentication tested for 10+ users
- [ ] Rollback procedure verified

**NO-GO if:**
- Any P1 defect unresolved
- Data validation >2% error rate
- Critical process cannot be completed
- Rollback procedure untested

---

## Example 4: Anti-Example - Poor KT Analysis

This example shows common mistakes to avoid.

### Poor Problem Statement
"The production line has quality problems."

**Issues:**
- No specific object identified
- No specific deviation described
- Vague and unmeasurable

**Better**: "CNC Lathe #7 is producing parts with ±0.005" dimensional variation on the X-axis, exceeding the ±0.002" tolerance."

### Poor IS/IS NOT Matrix

| Dimension | IS | IS NOT | Distinction |
|-----------|-----|--------|-------------|
| WHAT | Bad parts | Good parts | They're different |
| WHERE | Production | Everywhere else | It's in production |
| WHEN | Now | Before | Something changed |
| EXTENT | A lot | Not everything | Some affected |

**Issues:**
- IS column is vague ("bad parts")
- IS NOT is trivial negation, not meaningful comparison
- Distinctions are useless ("they're different")
- No factual specificity

### Poor Decision Analysis

"We should go with Vendor A because they're the best."

**Issues:**
- No decision statement
- No criteria defined
- No systematic evaluation
- Conclusion without analysis

### Poor PPA

"Things might go wrong but we'll deal with it."

**Issues:**
- No specific risks identified
- No assessment of likelihood/seriousness
- No preventive actions
- No contingency plans
- No triggers defined
