# Pareto Analysis Worked Examples

Complete examples demonstrating proper Pareto Analysis methodology.

---

## Example 1: Manufacturing Defects

### Context
A electronics manufacturer wants to reduce product defects. Quality team collected defect data for one month (Q4 2024) across all product lines.

### Phase 1: Problem Scoping

**Problem Statement**: Identify which defect types contribute most to overall product defects to prioritize improvement efforts.

**Measurement**: Frequency (count of defects by type)

**Time Period**: October 2024 (one production month)

### Phase 2: Data Collection

| Defect Type | Count |
|-------------|-------|
| Solder Bridges | 142 |
| Cold Solder Joints | 98 |
| Missing Components | 67 |
| Wrong Components | 45 |
| Damaged PCB | 32 |
| ESD Damage | 28 |
| Contamination | 22 |
| Other | 16 |
| **TOTAL** | **450** |

### Phase 3: Chart Construction

| Defect Type | Count | % | Cumulative % |
|-------------|-------|---|--------------|
| Solder Bridges | 142 | 31.6% | 31.6% |
| Cold Solder Joints | 98 | 21.8% | 53.3% |
| Missing Components | 67 | 14.9% | 68.2% |
| Wrong Components | 45 | 10.0% | 78.2% |
| Damaged PCB | 32 | 7.1% | 85.3% | ← 80% threshold |
| ESD Damage | 28 | 6.2% | 91.6% |
| Contamination | 22 | 4.9% | 96.4% |
| Other | 16 | 3.6% | 100.0% |

### Phase 4: Analysis

**Pareto Effect**: Strong. Top 4 defect types account for 78.2% of all defects (close to 80/20).

**Vital Few Identified**:
1. Solder Bridges (31.6%)
2. Cold Solder Joints (21.8%)
3. Missing Components (14.9%)
4. Wrong Components (10.0%)

**Observations**:
- Two solder-related defects dominate (53.3% combined)
- Component-related issues are second tier (24.9% combined)
- "Other" appropriately small (3.6%)

**Validation Questions Asked**:
- Q: Do top categories align with intuition?
- A: Yes, soldering has been a known concern.

- Q: Should we apply weighting?
- A: Considered but not needed - all defects equally important for this product.

### Phase 5: Recommendations

1. **Immediate**: Launch Fishbone analysis on Solder Bridges
2. **Short-term**: Review solder process parameters and training
3. **Medium-term**: Investigate component placement process for missing/wrong components
4. **Metric**: Target 50% reduction in solder-related defects within 90 days

### Quality Score: 87/100

| Dimension | Score | Notes |
|-----------|-------|-------|
| Problem Clarity | 5 | Clear scope, appropriate measurement |
| Data Quality | 4 | Good sample size, one-month period |
| Category Design | 4 | MECE, appropriate level |
| Calculation Accuracy | 5 | All calculations correct |
| Pattern Interpretation | 4 | Good analysis, considered weighting |
| Actionability | 5 | Clear next steps defined |

---

## Example 2: Customer Complaints

### Context
A SaaS company wants to reduce customer complaints. Support team analyzed tickets for Q3 2024.

### Phase 1: Problem Scoping

**Problem Statement**: Identify complaint categories causing greatest customer dissatisfaction to prioritize product and service improvements.

**Measurement**: Frequency (count of complaints by category)

**Time Period**: Q3 2024 (July-September)

### Phase 2: Data Collection

| Complaint Category | Count |
|-------------------|-------|
| Login/Authentication Issues | 245 |
| Slow Performance | 198 |
| Feature Not Working | 156 |
| Billing Disputes | 89 |
| Data Sync Problems | 72 |
| UI/UX Confusion | 64 |
| Mobile App Bugs | 51 |
| Integration Failures | 43 |
| Documentation Unclear | 28 |
| Other | 34 |
| **TOTAL** | **980** |

### Phase 3: Chart Construction

| Complaint Category | Count | % | Cumulative % |
|-------------------|-------|---|--------------|
| Login/Authentication Issues | 245 | 25.0% | 25.0% |
| Slow Performance | 198 | 20.2% | 45.2% |
| Feature Not Working | 156 | 15.9% | 61.1% |
| Billing Disputes | 89 | 9.1% | 70.2% |
| Data Sync Problems | 72 | 7.3% | 77.6% |
| UI/UX Confusion | 64 | 6.5% | 84.1% | ← 80% threshold |
| Mobile App Bugs | 51 | 5.2% | 89.3% |
| Integration Failures | 43 | 4.4% | 93.7% |
| Documentation Unclear | 28 | 2.9% | 96.5% |
| Other | 34 | 3.5% | 100.0% |

### Phase 4: Analysis

**Pareto Effect**: Moderate. Top 5 categories account for 77.6% of complaints.

**Vital Few Identified**:
1. Login/Authentication Issues (25.0%)
2. Slow Performance (20.2%)
3. Feature Not Working (15.9%)
4. Billing Disputes (9.1%)
5. Data Sync Problems (7.3%)

**Decision: Apply Weighting**

The team decided frequency alone was insufficient - a billing dispute has higher impact than a minor UI complaint. Applied severity weighting:

| Category | Count | Severity (1-5) | Weighted Score |
|----------|-------|----------------|----------------|
| Login/Authentication | 245 | 5 | 1225 |
| Slow Performance | 198 | 3 | 594 |
| Feature Not Working | 156 | 4 | 624 |
| Billing Disputes | 89 | 5 | 445 |
| Data Sync Problems | 72 | 4 | 288 |

**Weighted Pareto Results**:

| Category | Weighted Score | % | Cumulative % |
|----------|---------------|---|--------------|
| Login/Authentication | 1225 | 38.5% | 38.5% |
| Feature Not Working | 624 | 19.6% | 58.1% |
| Slow Performance | 594 | 18.7% | 76.8% |
| Billing Disputes | 445 | 14.0% | 90.8% | ← 80% threshold |
| Data Sync Problems | 288 | 9.1% | 99.9% |

**Insight**: Weighting elevated "Billing Disputes" (high severity) and demoted "Slow Performance" (medium severity) in priority.

### Phase 5: Recommendations

1. **Critical**: Fix authentication system reliability (38.5% weighted impact)
2. **High**: Feature functionality audit and testing improvement
3. **Medium**: Performance optimization
4. **Process**: Billing process review to reduce disputes

### Quality Score: 92/100

| Dimension | Score | Notes |
|-----------|-------|-------|
| Problem Clarity | 5 | Clear business objective |
| Data Quality | 5 | Large sample, full quarter |
| Category Design | 4 | Good MECE, one broad category |
| Calculation Accuracy | 5 | Correct, both weighted and unweighted |
| Pattern Interpretation | 5 | Excellent - recognized need for weighting |
| Actionability | 5 | Specific recommendations by priority |

---

## Example 3: IT Incident Analysis

### Context
IT Operations team analyzing incidents to reduce downtime.

### Phase 1: Problem Scoping

**Problem Statement**: Identify incident categories causing greatest system downtime to prioritize infrastructure improvements.

**Measurement**: Downtime hours (not frequency)

**Time Period**: Q4 2024

### Phase 2: Data Collection

| Incident Category | Count | Downtime (hours) |
|-------------------|-------|------------------|
| Network Outages | 12 | 47.5 |
| Database Failures | 8 | 38.2 |
| Application Crashes | 45 | 22.8 |
| Hardware Failures | 5 | 18.5 |
| Security Incidents | 3 | 15.0 |
| Configuration Errors | 28 | 12.3 |
| Third-Party Service | 15 | 8.7 |
| Other | 22 | 5.0 |
| **TOTAL** | **138** | **168.0** |

### Phase 3: Chart Construction (by Downtime)

| Incident Category | Downtime (hrs) | % | Cumulative % |
|-------------------|----------------|---|--------------|
| Network Outages | 47.5 | 28.3% | 28.3% |
| Database Failures | 38.2 | 22.7% | 51.0% |
| Application Crashes | 22.8 | 13.6% | 64.6% |
| Hardware Failures | 18.5 | 11.0% | 75.6% |
| Security Incidents | 15.0 | 8.9% | 84.5% | ← 80% threshold |
| Configuration Errors | 12.3 | 7.3% | 91.8% |
| Third-Party Service | 8.7 | 5.2% | 97.0% |
| Other | 5.0 | 3.0% | 100.0% |

### Phase 4: Analysis

**Critical Insight**: Using downtime (impact) rather than frequency completely changed priorities!

**Comparison**:
| Category | By Frequency | By Downtime |
|----------|--------------|-------------|
| Application Crashes | #1 (45) | #3 (22.8 hrs) |
| Network Outages | #5 (12) | #1 (47.5 hrs) |
| Configuration Errors | #2 (28) | #6 (12.3 hrs) |

**Lesson**: Application crashes were frequent but quick to resolve. Network outages were rare but catastrophic.

**Vital Few (by Impact)**:
1. Network Outages (28.3% of downtime)
2. Database Failures (22.7% of downtime)
3. Application Crashes (13.6% of downtime)
4. Hardware Failures (11.0% of downtime)

### Phase 5: Recommendations

1. **Infrastructure**: Network redundancy and failover investment
2. **Database**: High-availability configuration, automated backups
3. **Monitoring**: Early warning for network and database health
4. **Application**: Continue crash reduction but lower priority than infrastructure

### Quality Score: 94/100

| Dimension | Score | Notes |
|-----------|-------|-------|
| Problem Clarity | 5 | Focused on downtime, not just incidents |
| Data Quality | 5 | Accurate downtime tracking |
| Category Design | 5 | Clear, actionable categories |
| Calculation Accuracy | 5 | Correct by both metrics |
| Pattern Interpretation | 5 | Excellent insight on frequency vs. impact |
| Actionability | 4 | Good recommendations, could add timelines |

---

## Example 4: Anti-Example (Poor Analysis)

### What Went Wrong

A team performed Pareto analysis but made several errors:

**Original Data**:

| Category | Count |
|----------|-------|
| Process Issues | 156 |
| Equipment Problems | 89 |
| People Problems | 134 |
| Material Issues | 78 |
| Other | 143 |

**Problems Identified**:

1. **Large "Other" Category**: 143 counts (24%) - should be <10%
2. **Categories Too High-Level**: "Process Issues" and "People Problems" not actionable
3. **Overlapping Categories**: "People Problems" could overlap with "Process Issues"
4. **No Definition Documentation**: Team members categorized inconsistently

### Corrected Approach

**Reviewed "Other" category** - found recurring patterns:
- Environmental factors: 45
- Supplier issues: 38
- Measurement problems: 32
- True miscellaneous: 28

**Split high-level categories** into actionable items:
- "Process Issues" → Split by process step
- "People Problems" → Recategorized as training gaps (process) vs. adherence (procedure)

**Documented definitions** with examples and decision rules.

**Re-collected data** with improved categories:

| Category | Count | % | Cumulative % |
|----------|-------|---|--------------|
| Assembly Process Step 3 | 89 | 14.8% | 14.8% |
| Training Gaps - New Hires | 78 | 13.0% | 27.8% |
| Material Incoming Quality | 67 | 11.2% | 39.0% |
| Equipment Calibration | 62 | 10.3% | 49.3% |
| Procedure Adherence | 58 | 9.7% | 59.0% |
| Environmental - Temperature | 45 | 7.5% | 66.5% |
| Supplier Quality - Vendor A | 38 | 6.3% | 72.8% |
| Assembly Process Step 1 | 34 | 5.7% | 78.5% |
| Measurement Equipment | 32 | 5.3% | 83.8% | ← 80% threshold |
| Equipment Maintenance | 27 | 4.5% | 88.3% |
| Other | 70 | 11.7% | 100.0% |

**Result**: Categories now actionable. "Other" reduced to 11.7% (still high - needs one more iteration).

**Quality Score Comparison**:
- Original analysis: 42/100 (Inadequate)
- Corrected analysis: 78/100 (Adequate)

---

## Key Takeaways from Examples

1. **Measurement matters**: Frequency vs. cost vs. downtime can yield completely different priorities

2. **Weighting is powerful**: When categories have different severities, weighted Pareto reveals true priorities

3. **Categories make or break analysis**: Invest time in MECE, actionable category design

4. **"Other" is a warning sign**: Large "Other" indicates category design problems

5. **Pareto enables, doesn't complete**: Follow Pareto with Fishbone/5 Whys for root cause investigation
