# 8D Worked Examples

## Overview

This document provides worked examples of complete 8D investigations across different domains. Each example demonstrates the full 8D methodology from initial assessment through closure.

---

## Example 1: Manufacturing Defect — Cracked Connector Housing

### D0: Initial Assessment

**Domain**: Manufacturing/Production defect
**Severity**: High — Customer complaint, potential warranty cost
**Urgency**: Days — Not safety-critical but affecting shipments
**Scope**: Multiple occurrences (47 units) over 2-week period

### D1: Team Formation

| Role | Name | Function |
|------|------|----------|
| Team Leader | J. Smith | Quality Engineer |
| Facilitator | M. Johnson | Continuous Improvement |
| Champion | R. Davis | Plant Manager |
| SME: Production | K. Williams | Production Supervisor |
| SME: Process | T. Brown | Process Engineer |
| SME: Design | A. Garcia | Product Engineer |

**Cross-functional coverage**: ✓ Quality, Production, Engineering, Management
**Implementation owners included**: ✓ Production Supervisor can implement changes

### D2: Problem Definition (5W2H + IS/IS NOT)

**5W2H Analysis**:

| Element | Finding |
|---------|---------|
| **What** (Object) | Connector housing P/N 12345-A, Rev C |
| **What** (Defect) | Crack at locking tab base, 2-4mm length |
| **Where** (Geographic) | Final assembly, Station 3 |
| **Where** (On object) | Locking tab connection to housing body |
| **When** (Calendar) | Production weeks 12-13, 2025 |
| **When** (Lifecycle) | Discovered during torque verification |
| **Who** | QC Inspector during final inspection |
| **How** (Detection) | Visual inspection, confirmed by microscope |
| **How Much** | 47 of 1,580 units (3.0% reject rate) |

**IS / IS NOT Analysis**:

| Dimension | IS | IS NOT | Clues |
|-----------|-----|---------|-------|
| What | Connector housing P/N 12345-A | Other connector types (12345-B, C) | Unique to -A variant |
| Where | Station 3 only | Stations 1, 2 | Station-specific factor |
| When | Weeks 12-13 | Weeks 1-11 | Recent change? |
| Who | All operators at Station 3 | — | Not operator-specific |

**Problem Statement**:
> Connector housing P/N 12345-A exhibited cracking at locking tab base (2-4mm) at final assembly Station 3 during production weeks 12-13, affecting 47 of 1,580 units (3.0%), detected by visual inspection.

### D3: Containment Actions

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| 1 | Quarantine all Station 3 output from weeks 12-13 | K. Williams | Immediate | Complete |
| 2 | 100% inspection of quarantined inventory | QC Team | 24 hours | Complete |
| 3 | Add 100% visual inspection at Station 3 | K. Williams | Immediate | In place |
| 4 | Review shipped product from weeks 12-13 | Customer Service | 48 hours | In progress |

### D4: Root Cause Analysis

**Tool Selection**: Fishbone → 5 Whys (unknown cause, several possibilities)

**Fishbone Categories Explored**:
- **Machine**: Torque driver calibration, fixture wear
- **Material**: Housing material lot, supplier change
- **Method**: Assembly procedure, torque sequence
- **Man**: Training, technique variation
- **Measurement**: Inspection capability
- **Environment**: Temperature, humidity

**Multi-voting Results**: Top 3 causes selected for 5 Whys:
1. Torque sequence changed (8 votes)
2. Material lot variation (5 votes)
3. Fixture wear (3 votes)

**5 Whys Analysis** (Primary chain):

| Why | Question | Answer | Evidence |
|-----|----------|--------|----------|
| 1 | Why did the locking tabs crack? | Excessive stress during torque application | Fractography shows stress cracking pattern |
| 2 | Why was there excessive stress? | Torque applied before housing fully seated | Video analysis of Station 3 operation |
| 3 | Why was torque applied early? | Torque sequence changed to improve cycle time | Work instruction revision dated Week 11 |
| 4 | Why was sequence changed without validation? | Process change didn't go through change control | Engineering change request bypassed |
| 5 | Why was change control bypassed? | No MOC trigger for work instruction updates | MOC procedure gap identified |

**Root Cause Verification**:
- ✓ Reversal test: Passes "therefore" logic
- ✓ Prevention test: Proper change control would have required validation
- ✓ Evidence test: Document trail supports all links

**Verified Root Cause**:
> Work instruction change (torque sequence) was implemented without validation testing because the Management of Change (MOC) procedure did not require review for work instruction updates.

### D5: Corrective Action Selection

| # | Corrective Action | Addresses | Effectiveness |
|---|-------------------|-----------|---------------|
| 1 | Revert to original torque sequence | Immediate cause | High — Eliminates stress |
| 2 | Update MOC procedure to include work instructions | Root cause | High — Prevents recurrence |
| 3 | Validate new sequence properly before implementation | Future prevention | Medium — Allows improvement |

**Selected**: Actions 1 (immediate) and 2 (systemic)

### D6: Implementation Plan

| Step | Action | Owner | Target Date | Verification |
|------|--------|-------|-------------|--------------|
| 1 | Revise work instruction to original sequence | T. Brown | 2025-03-20 | Document approval |
| 2 | Train Station 3 operators on revised WI | K. Williams | 2025-03-21 | Training records |
| 3 | Validate corrective action (first 100 units) | J. Smith | 2025-03-22 | 0% crack rate |
| 4 | Update MOC procedure to include WI scope | M. Johnson | 2025-04-01 | Procedure approval |
| 5 | Train engineering on updated MOC | M. Johnson | 2025-04-15 | Training records |

### D7: Prevention

**Systemic Actions**:

| Action | Scope | Owner | Target |
|--------|-------|-------|--------|
| Audit all WI changes from past 12 months for validation gaps | Plant-wide | Quality | 2025-04-30 |
| Add "process validation required" flag to WI template | All WIs | Engineering | 2025-04-15 |
| Quarterly MOC compliance audit | Plant-wide | Quality | Ongoing |

**Horizontal Deployment**:
- Applied MOC expansion to all production lines (not just Assembly)
- Shared lesson learned in monthly quality review

### D8: Closure

**Effectiveness Verification**:
- Corrective action implemented: 2025-03-21
- Verification period: 2025-03-22 to 2025-04-22 (30 days)
- Units produced: 4,200
- Cracked housings: 0 (0.0%)
- **Verification: PASSED**

**Containment Removal**:
- 100% inspection removed: 2025-04-23
- Normal sampling inspection resumed

**Documentation**:
- ✓ 8D report finalized
- ✓ CAPA closed in quality system
- ✓ Lesson learned added to knowledge base

---

## Example 2: Software Deployment Failure

### D0: Initial Assessment

**Domain**: Software/IT system failure
**Severity**: Critical — Production system unavailable for 4 hours
**Urgency**: Immediate — Revenue-impacting incident
**Scope**: Single occurrence, widespread impact (all users)

### D1: Team Formation

| Role | Name | Function |
|------|------|----------|
| Team Leader | S. Chen | SRE Manager |
| Facilitator | L. Patel | Engineering Manager |
| Champion | D. Kim | VP Engineering |
| SME: Platform | R. Torres | Platform Engineer |
| SME: Application | M. Lee | Senior Developer |
| SME: Database | J. Wang | DBA |

### D2: Problem Definition

**Problem Statement**:
> Production e-commerce application became unavailable at 14:32 UTC on 2025-03-15 following deployment of release v2.4.1, resulting in 4 hours of downtime affecting all users, resolved by rollback at 18:45 UTC.

**IS / IS NOT**:
| IS | IS NOT |
|----|---------|
| Production environment | Staging, dev environments |
| v2.4.1 deployment | Previous releases |
| Database timeout errors | Application crashes |
| All users | Subset of users |

### D3: Containment

1. ✓ Rolled back to v2.4.0 at 18:45 UTC
2. ✓ Halted all deployments pending investigation
3. ✓ Increased monitoring thresholds on database connections
4. ✓ Customer communication sent

### D4: Root Cause Analysis

**5 Whys Analysis**:

| Why | Answer | Evidence |
|-----|--------|----------|
| 1 | Why did the application become unavailable? | Database connection pool exhausted | Connection pool metrics, error logs |
| 2 | Why was connection pool exhausted? | New query in v2.4.1 held connections 10x longer | Query execution traces |
| 3 | Why did new query hold connections so long? | Missing index on JOIN clause | Query plan analysis |
| 4 | Why was missing index not detected? | Query not tested with production-scale data | Test database has 1% of prod data |
| 5 | Why no production-scale testing? | Performance testing only uses synthetic data | Test environment configuration |

**Root Cause**:
> Performance testing environment does not replicate production data scale, allowing database queries with missing indexes to pass testing but fail under production load.

### D5-D6: Corrective Actions

| Action | Type | Owner | Status |
|--------|------|-------|--------|
| Add missing index to production | Immediate | J. Wang | Complete |
| Implement production data subset in staging | Systemic | R. Torres | 2025-04-15 |
| Add query execution time gates to CI/CD | Detection | S. Chen | 2025-03-30 |
| Create database change review checklist | Prevention | J. Wang | 2025-03-25 |

### D7: Prevention

- Added "database impact assessment" to PR template
- Implemented automated slow query detection in pre-production
- Quarterly production data refresh to staging environments

### D8: Closure

- No recurrence in 60-day verification period
- Post-mortem shared with engineering organization
- Incident playbook updated

---

## Example 3: Customer Complaint — Early Field Failure

### D0: Initial Assessment

**Domain**: Field failure / Customer complaint
**Severity**: High — Safety-adjacent (brake system sensor)
**Urgency**: Immediate — Regulatory notification threshold approaching
**Scope**: 12 field failures from population of 8,000 (0.15%)

### D1: Team Formation

| Role | Name |
|------|------|
| Team Leader | Customer Quality Engineer |
| Champion | VP Quality |
| SMEs | Design, Manufacturing, Supplier Quality, Field Service |

### D2: Problem Definition

**Problem Statement**:
> Brake pressure sensor P/N 98765 exhibited intermittent signal loss in 12 of 8,000 deployed vehicles (0.15%) within first 6 months of operation, manifesting as ABS warning light illumination during cold weather conditions (below 0°C / 32°F).

**Key IS/IS NOT Insight**:
- IS: Cold weather conditions (0°C to -20°C)
- IS NOT: Warm weather (above 10°C)
- IS: Early production units (SN range 0001-2000)
- IS NOT: Later production (SN 2001+)

### D3: Containment

1. Field service bulletin issued for affected serial number range
2. Dealer inspection campaign initiated
3. Affected sensors replaced with updated version

### D4: Root Cause Analysis

**Kepner-Tregoe Problem Analysis** (Selected due to specification-based nature):

**Distinction Analysis**:
- Early production used Supplier A solder paste
- Later production used Supplier B solder paste (changed at SN 2001)
- Cold temperature causes differential thermal contraction
- Supplier A paste had different thermal expansion coefficient

**Root Cause**:
> Supplier A solder paste had thermal expansion coefficient mismatch with PCB substrate, causing solder joint micro-cracking under cold temperature cycling, leading to intermittent electrical opens.

### D5-D6: Corrective Actions

1. Qualify Supplier B paste as permanent replacement
2. Add thermal cycling test to incoming inspection
3. Update solder paste specification with CTE requirements

### D7: Prevention

- Added CTE matching requirement to material specifications
- DFMEA updated with thermal expansion failure mode
- Supplier qualification procedure expanded

### D8: Closure

- All known affected units replaced in field
- No new failures in 12-month monitoring period
- Regulatory reporting completed

---

## Key Takeaways from Examples

1. **Problem definition bounds the investigation** — Precise IS/IS NOT analysis reveals critical clues (Example 1: Station 3 only; Example 3: Cold weather only)

2. **Tool selection matters** — Use Fishbone for unknown causes, 5 Whys for drilling depth, KT-PA for specification-based problems

3. **Root cause is systemic** — All examples reached process/system level (MOC gap, test environment, material specification) not person-blame

4. **Verification is mandatory** — Each example includes measured verification period confirming corrective action effectiveness

5. **Prevention extends beyond the incident** — Horizontal deployment and systemic changes prevent similar problems across the organization
