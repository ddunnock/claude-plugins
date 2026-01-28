# 5 Whys Worked Examples

## Example 1: Manufacturing Equipment Failure

### Problem Statement
**What**: CNC Machine #3 produced parts with diameter 0.015" oversized
**Where**: Machine Shop, CNC Cell A, Part #A-1234
**When**: Discovered January 15, 2025 during first article inspection; likely started after shift change at 6:00 AM
**Extent**: 47 parts affected (full first shift run)
**Expected vs Actual**: Diameter spec 1.500" ± 0.002"; actual measured 1.515" to 1.518"

### 5 Whys Analysis

**Why 1**: Why were the parts oversized?
> **Answer**: The tool offset was set incorrectly in the machine controller.
> **Evidence**: Tool offset register showed +0.015" when it should have been 0.000"

**Why 2**: Why was the tool offset set incorrectly?
> **Answer**: The offset was not reset after the previous job which required a different offset.
> **Evidence**: Previous job setup sheet shows +0.015" offset was intentional for that part

**Why 3**: Why wasn't the offset reset before starting the new job?
> **Answer**: The setup procedure doesn't include verification of tool offsets as a standard step.
> **Evidence**: Reviewed setup procedure document - no mention of offset verification

**Why 4**: Why doesn't the setup procedure include offset verification?
> **Answer**: The procedure was written when only one part ran on this machine; offsets never changed.
> **Evidence**: Procedure dated 2019; second part number added 2023 without procedure update

**Why 5**: Why wasn't the procedure updated when the second part was added?
> **Answer**: No process exists to trigger procedure review when machine capability changes.
> **Evidence**: Engineering change for second part shows no checkbox or routing for procedure update

### Root Cause
No Management of Change (MOC) process triggers procedure review when machine capability or part mix changes.

### Verification Tests
- **Reversal Test**: ✓ "No MOC process → procedure not updated → offset verification missing → offset not reset → parts oversized"
- **Prevention Test**: ✓ If MOC process existed, procedure would have been updated, including offset verification
- **Control Test**: ✓ MOC process is within engineering's authority to implement
- **Evidence Test**: ✓ All answers verified with documentation

### Countermeasures
1. **Immediate**: Add offset verification step to current procedure (Owner: J. Smith, Due: Jan 20)
2. **Permanent**: Implement MOC process for machine capability changes (Owner: M. Johnson, Due: Feb 28)
3. **Verification**: Audit first 3 MOC triggers for procedure updates (Owner: Quality, Due: Mar 31)
4. **Sustainment**: Add MOC compliance to monthly operations review (Owner: Plant Manager, Due: Ongoing)

### Quality Score: 88/100
- Problem Definition: 5/5 (specific, measurable, complete)
- Causal Chain Logic: 4/5 (solid chain, minor gap between Why 4 and 5)
- Evidence Basis: 5/5 (all answers documented)
- Root Cause Depth: 4/5 (good systemic level)
- Actionability: 5/5 (fully within control)
- Countermeasures: 4/5 (good but could add more verification detail)

---

## Example 2: Software Deployment Failure

### Problem Statement
**What**: Production deployment of Release 4.2 failed, causing 2-hour service outage
**Where**: Production Kubernetes cluster, payment processing service
**When**: January 10, 2025, 22:00 UTC during scheduled deployment window
**Extent**: All payment processing (approximately 12,000 transactions) blocked for 2 hours
**Expected vs Actual**: Expected smooth rollout with zero downtime; actual was complete service failure

### 5 Whys Analysis (Branched)

**Problem**: Production deployment failed causing 2-hour outage

**Why 1**: Why did the deployment fail?
> **Answer A**: New service couldn't connect to database
> **Answer B**: Health checks failed so pods kept restarting
> *(Both answers pursued)*

**Branch A: Database Connection**

**Why 2A**: Why couldn't the service connect to the database?
> **Answer**: Connection string was wrong - pointed to staging database
> **Evidence**: Logs showed connection attempts to staging.db.internal

**Why 3A**: Why was the connection string wrong?
> **Answer**: Environment variable CONFIG_DB_HOST wasn't overridden for production
> **Evidence**: Deployment manifest review shows staging value used

**Why 4A**: Why wasn't the environment variable overridden?
> **Answer**: Developer copied staging manifest and forgot to update
> **Evidence**: Git history shows copy-paste from staging folder

**Why 5A**: Why was manual copy-paste the deployment process?
> **Answer**: No environment-specific manifest generation or validation exists
> **Evidence**: Deployment docs show manual manifest creation process

**Root Cause A**: No automated environment-specific configuration management; relies on manual manifest creation prone to copy-paste errors.

**Branch B: Health Check Failure**

**Why 2B**: Why did health checks fail?
> **Answer**: Readiness probe checked /health which returned 503
> **Evidence**: Probe logs show 503 responses from /health endpoint

**Why 3B**: Why did /health return 503?
> **Answer**: Health check requires database connectivity; connection failed (links to Branch A)
> **Evidence**: /health implementation checks database connection

**Why 4B**: Why does the health check fail completely on database issues?
> **Answer**: No graceful degradation - any dependency failure = unhealthy
> **Evidence**: Code review shows all-or-nothing health logic

**Why 5B**: Why wasn't graceful degradation implemented?
> **Answer**: No specification for health check behavior under partial failures
> **Evidence**: Original health check requirements don't address partial failure

**Root Cause B**: Health check specification lacks resilience requirements for graceful degradation under partial dependency failures.

### Combined Root Causes
1. No automated environment-specific configuration management
2. Health check specification lacks resilience requirements

### Verification Tests
- **Reversal Test**: ✓ Both chains pass forward and backward
- **Prevention Test**: ✓ Automated config would prevent wrong connection string; better health spec would prevent cascade
- **Control Test**: ✓ Both within development team's authority

### Countermeasures
**For Root Cause A:**
1. Implement Helm charts with environment-specific values (Owner: DevOps, Due: Feb 1)
2. Add deployment validation checking environment consistency (Owner: DevOps, Due: Feb 15)
3. Require two-person review of production manifests (Owner: Team Lead, Due: Immediate)

**For Root Cause B:**
1. Update health check spec to define partial failure behavior (Owner: Architect, Due: Jan 30)
2. Implement tiered health responses (healthy, degraded, unhealthy) (Owner: Dev Team, Due: Mar 1)
3. Add canary deployment with automatic rollback (Owner: DevOps, Due: Mar 15)

### Quality Score: 92/100
- Problem Definition: 5/5 (clear, measurable)
- Causal Chain Logic: 5/5 (excellent branching, all links verified)
- Evidence Basis: 5/5 (logs, code, documentation cited)
- Root Cause Depth: 4/5 (good process level)
- Actionability: 5/5 (fully actionable)
- Countermeasures: 5/5 (specific, assigned, measured)

---

## Example 3: Customer Complaint Investigation

### Problem Statement
**What**: Customer reported receiving wrong product (ordered Model A, received Model B)
**Where**: Order #45789, shipped from Distribution Center East to customer in Chicago
**When**: Order placed Jan 5, shipped Jan 7, complaint received Jan 12
**Extent**: Single order (but 3rd similar complaint in 30 days)
**Expected vs Actual**: Expected Model A (SKU: 12345-A); Actual shipped Model B (SKU: 12345-B)

### 5 Whys Analysis

**Why 1**: Why was the wrong product shipped?
> **Answer**: Picker selected Model B from the bin instead of Model A.
> **Evidence**: Pick ticket shows correct SKU; shipped box shows wrong SKU label

**Why 2**: Why did the picker select the wrong product?
> **Answer**: Model A and Model B are stored in adjacent bins and look nearly identical.
> **Evidence**: Walked warehouse; confirmed visual similarity and adjacent placement

**Why 3**: Why are similar-looking products stored adjacent to each other?
> **Answer**: Products are stored alphabetically by SKU, not by error risk.
> **Evidence**: Warehouse layout map shows alphabetical organization

**Why 4**: Why doesn't the slotting strategy consider error risk?
> **Answer**: Slotting criteria only consider pick efficiency (travel distance), not pick accuracy.
> **Evidence**: Slotting procedure document lists only efficiency criteria

**Why 5**: Why don't slotting criteria include pick accuracy factors?
> **Answer**: Slotting process predates product line expansion; never updated for look-alike risk.
> **Evidence**: Slotting procedure last updated 2020; similar SKUs introduced 2023

### Root Cause
Warehouse slotting criteria do not include pick error risk factors (visual similarity, adjacent placement of similar SKUs).

### Additional Contributing Factor
No verification step exists at pack station to confirm SKU matches order.

### Verification Tests
- **Reversal Test**: ✓ "No error risk in slotting → similar items adjacent → easy to mispick → wrong product shipped"
- **Prevention Test**: ✓ Risk-based slotting would separate similar items
- **Recurrence Test**: ✓ 3 similar complaints in 30 days suggests systemic issue

### Countermeasures
1. **Immediate**: Physically separate Model A and Model B bins (Owner: Warehouse Mgr, Due: Jan 15)
2. **Short-term**: Add scan verification at pack station (Owner: Operations, Due: Feb 1)
3. **Permanent**: Update slotting criteria to include error risk factors (Owner: WMS Admin, Due: Feb 28)
4. **Standardize**: Train all pickers on look-alike product awareness (Owner: Training, Due: Mar 15)
5. **Sustain**: Add pick accuracy to slotting review KPIs (Owner: Operations, Due: Ongoing)

### Quality Score: 85/100
- Problem Definition: 5/5 (specific incident with pattern context)
- Causal Chain Logic: 4/5 (good flow, could explore verification gap more)
- Evidence Basis: 4/5 (mostly verified, some assumptions on worker behavior)
- Root Cause Depth: 4/5 (good process level)
- Actionability: 5/5 (fully controllable)
- Countermeasures: 5/5 (layered approach: immediate through sustained)

---

## Example 4: Process Quality Deviation (Poor Example - Then Corrected)

### Problem Statement (Weak)
**Original**: "Quality is bad in production."

**Improved**: 
**What**: Solder joint defect rate on PCB Assembly Line 2 increased from baseline 0.5% to 2.3%
**Where**: Line 2, Wave Solder Station, affecting all board types
**When**: Increase first noted week of Jan 6; confirmed over 3-day period Jan 8-10
**Extent**: 2.3% defect rate (vs 0.5% baseline); approximately 115 defective joints per 5,000
**Expected vs Actual**: Historical defect rate 0.3-0.5%; current 2.3%

### 5 Whys Analysis (Initial Attempt - Shows Common Errors)

**Why 1**: Why is the defect rate high?
> ❌ **Bad Answer**: "Operators aren't careful enough."
> *(Person-blame - needs redirect)*

**Redirected Why 1**: Why are solder joints failing inspection?
> ✓ **Better Answer**: Joints show insufficient wetting and cold solder characteristics.
> **Evidence**: Defect photos show dull, grainy appearance typical of cold joints

**Why 2**: Why is there insufficient wetting?
> ❌ **Bad Answer**: "I think the solder temperature is too low."
> *(Assumption - needs verification)*

**Verified Answer**: Solder pot temperature measured at 465°F; spec is 480-490°F.
> **Evidence**: Temperature log and direct measurement

**Why 3**: Why is the solder temperature low?
> **Answer**: Heating element is degraded, can't maintain setpoint.
> **Evidence**: Element current draw at 85% of spec; maintenance inspection confirms degradation

**Why 4**: Why is the heating element degraded?
> **Answer**: Element has exceeded recommended service life (18 months vs 12-month recommendation).
> **Evidence**: Installation date shows 18 months ago; OEM spec says 12-month replacement

**Why 5**: Why wasn't the element replaced at 12 months?
> ❌ **Bad Answer**: "Maintenance forgot."
> *(Person-blame - needs redirect)*

**Redirected Why 5**: Why is there no system to ensure scheduled replacement?
> ✓ **Better Answer**: Heating element is not in the PM schedule; no trigger exists for replacement.
> **Evidence**: CMMS query shows no PM task for this element

**Why 6**: Why isn't the element in the PM schedule?
> **Answer**: PM schedule was set up before this equipment was installed; never updated.
> **Evidence**: PM schedule dates to 2019; wave solder machine installed 2021

### Root Cause
New equipment additions are not systematically reviewed for PM requirements; no process triggers PM schedule updates for new assets.

### Corrected Chain Summary
```
New equipment not reviewed for PM requirements
↓
Heating element not added to PM schedule  
↓
No replacement trigger existed
↓
Element exceeded service life
↓
Element degraded, can't maintain temperature
↓
Low solder temperature (465°F vs 480-490°F spec)
↓
Insufficient wetting / cold solder joints
↓
Defect rate increased from 0.5% to 2.3%
```

### Countermeasures
1. **Immediate**: Replace heating element (Owner: Maintenance, Due: Jan 13)
2. **Short-term**: Audit all post-2019 equipment for PM gaps (Owner: Maintenance Mgr, Due: Feb 15)
3. **Permanent**: Add equipment commissioning checklist requiring PM schedule setup (Owner: Engineering, Due: Mar 1)
4. **Verify**: Sample audit 3 recent equipment installs for PM compliance (Owner: Quality, Due: Mar 15)

### Quality Score: 78/100 (after corrections)
- Problem Definition: 5/5 (excellent after improvement)
- Causal Chain Logic: 4/5 (solid after redirects)
- Evidence Basis: 4/5 (good verification)
- Root Cause Depth: 4/5 (good process level)
- Actionability: 5/5 (clear path)
- Countermeasures: 3/5 (could add sustainability mechanism)

### Lessons from This Example
1. **Problem statements must be specific** - "Quality is bad" → specific defect rate and conditions
2. **Avoid person-blame** - "Operators aren't careful" → "What process gap allowed this?"
3. **Verify assumptions** - "I think temperature is low" → actually measured and confirmed
4. **Keep redirecting** - Multiple person-blame answers required redirection to process issues
