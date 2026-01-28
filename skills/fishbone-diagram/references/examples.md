# Fishbone Diagram Examples

## Example 1: Manufacturing Defect (6Ms)

### Problem Statement
"Widget A dimensional variance exceeds ±0.05mm on 15% of units from CNC Machine #3, occurring since January 15th"

### Category Framework: 6Ms

### Fishbone Analysis

```
PROBLEM: Widget A dimensional variance >±0.05mm on 15% of units

MAN (People)
├── Operator inexperience
│   ├── New operator assigned Dec 28
│   └── Training incomplete (2 of 4 modules)
├── Measurement technique variation
│   ├── Inconsistent caliper positioning
│   └── No standardized measurement procedure
└── Fatigue on night shift
    └── Overtime increased 30% in January

MACHINE (Equipment)
├── CNC spindle wear
│   ├── 2,500 hours since last rebuild
│   │   └── Spec is 2,000 hours
│   └── Vibration readings elevated
├── Coolant system degradation
│   ├── Filter not changed (overdue by 2 weeks)
│   └── Coolant concentration low
└── Fixture wear
    ├── Locating pins worn
    └── Clamps not holding firmly

METHOD (Process)
├── Tool offset not verified
│   ├── Procedure skipped under time pressure
│   └── No automated verification
├── Warm-up cycle inadequate
│   ├── Reduced from 15 to 5 min
│   └── Thermal expansion not stabilized
└── In-process inspection reduced
    └── Changed from 100% to sampling

MATERIAL (Inputs)
├── New material lot arrived January 10
│   ├── Hardness variation within spec but at edge
│   └── Different supplier
└── Bar stock diameter variation
    └── At upper limit of tolerance

MEASUREMENT (Data)
├── Calibration overdue
│   ├── Caliper last calibrated December 1
│   └── CMM drift not verified
├── SPC chart not reviewed
│   └── Trend visible but not acted upon
└── Sampling plan inadequate
    └── Missing early shifts

MOTHER NATURE (Environment)
├── Temperature fluctuation
│   ├── HVAC issues in January cold snap
│   └── Door opened frequently for deliveries
└── Humidity variation
    └── New humidifier not working properly
```

### Prioritization (Multi-voting results)
1. CNC spindle wear - 8 votes
2. New operator training incomplete - 6 votes
3. Tool offset verification skipped - 5 votes

### Recommended Next Steps
- Apply 5 Whys to spindle wear cause
- Schedule spindle rebuild
- Complete operator training
- Reinstate tool offset verification procedure

---

## Example 2: Customer Service Complaint (8Ps)

### Problem Statement
"Customer satisfaction scores dropped from 4.2 to 3.1 (scale 1-5) for phone support in Q4, with 'long wait times' cited in 68% of negative feedback"

### Category Framework: 8Ps

### Fishbone Analysis

```
PROBLEM: Customer satisfaction dropped from 4.2 to 3.1 in Q4 phone support

PRODUCT
├── New features increased complexity
│   ├── 3 major releases in Q4
│   └── Documentation lagging
└── Bug reports increased 40%
    └── Rushed releases for holiday

PRICE
└── Premium support tier confusion
    └── Customers unclear on what's included

PLACE (Distribution)
├── Self-service portal hard to find
│   └── Buried 3 clicks deep
└── Chat option not prominently displayed
    └── Phone default even for simple issues

PROMOTION (Communication)
├── No proactive communication about known issues
│   └── Customers call to report already-known bugs
└── Email updates going to spam
    └── Domain authentication issue

PEOPLE (Staff)
├── Staffing reduced 20% in Q3
│   └── Budget cuts
├── New hires not fully trained
│   ├── 8 new agents, avg 2 weeks tenure
│   └── Mentorship program paused
└── Experienced agents leaving
    └── 3 senior agents left in October

PROCESS
├── Call handling time increased
│   ├── New CRM system learning curve
│   │   └── Implemented November 1
│   └── More escalations required
├── Queue routing inefficient
│   └── Skills-based routing not working
└── After-call work time extended
    └── Additional documentation requirements

PHYSICAL EVIDENCE
├── Hold music/messaging not updated
│   └── "3 minutes" message plays at 10+ min wait
└── IVR menu confusing
    └── Options don't match common issues

POLICIES
├── Strict handle time targets
│   ├── Agents rushing calls
│   └── Quality sacrificed for speed
└── Escalation approval requirements
    └── Supervisors overloaded
```

### Prioritization (Impact-Effort Matrix)
**Quick Wins** (High Impact, Low Effort):
- Update hold messaging to accurate wait times
- Promote chat option more visibly
- Fix email domain authentication

**Major Projects** (High Impact, High Effort):
- Restore staffing levels
- Improve CRM training
- Revise handle time policies

### Root Cause Hypothesis
Primary driver: Staff reduction + CRM transition occurring simultaneously overwhelmed capacity and capability.

---

## Example 3: Healthcare Incident (4Ss + Custom)

### Problem Statement
"Patient fall resulting in hip fracture occurred in Room 312 at 2:15 AM on January 20. Patient was attempting unassisted transfer from wheelchair to toilet."

### Category Framework: Custom (Healthcare - Equipment, Environment, Process, People, Patient Factors)

### Fishbone Analysis

```
PROBLEM: Patient fall with hip fracture during unassisted transfer

EQUIPMENT
├── Lift equipment unavailable
│   ├── Battery dead
│   │   ├── Charger outlet faulty
│   │   └── No backup battery on unit
│   └── Other lift being used
├── Call light out of reach
│   └── Moved during earlier assessment
└── Wheelchair brake not engaged
    └── Brake mechanism stiff

ENVIRONMENT
├── Low lighting conditions
│   ├── Night mode active
│   └── Bathroom light not working
├── Floor wet
│   └── Previous toileting assistance
└── Distance from bed to bathroom
    └── 15 feet without grab bars

PROCESS
├── Fall risk not communicated at shift change
│   ├── Handoff incomplete
│   └── New fall risk assessment not in chart
├── Hourly rounding not completed
│   ├── Staffing shortage
│   └── Other patient emergency
├── No toileting schedule established
│   └── Patient's pattern not assessed
└── Care plan not updated
    └── Transfer status changed but not documented

PEOPLE (Staff)
├── Aide unaware of lift requirement
│   ├── Care card not updated
│   └── Change occurred during shift
├── RN covering multiple patients
│   └── 1:8 ratio instead of 1:5
└── Communication breakdown
    └── Physical therapy recommendation not shared

PATIENT FACTORS
├── Anxiety about toileting accidents
│   └── Previous incontinence embarrassment
├── Cognitive status change
│   ├── New medication started
│   └── Delirium risk factors present
├── Overestimated own ability
│   └── "I've done this before"
└── Reluctance to use call light
    └── Didn't want to "bother" staff
```

### Prioritization (Multi-voting)
1. Communication breakdown at shift change - 9 votes
2. Lift equipment unavailability (no backup battery) - 7 votes
3. Care plan/care card not updated - 6 votes

### System Issues Identified
- No process ensures lift batteries are always available
- Care plan updates don't automatically update care cards
- Shift handoff doesn't include equipment status
- Hourly rounding compliance not monitored

---

## Example 4: Software Deployment Failure (Custom - PEOPLE Framework)

### Problem Statement
"Production deployment of Release 2.4.1 failed at 2:00 AM on January 18, causing 4-hour outage. Database migration script threw 'foreign key constraint violation' error."

### Category Framework: Custom (PEOPLE - Process, Environment, Operations, People, Libraries, Equipment)

### Fishbone Analysis

```
PROBLEM: Production deployment failed causing 4-hour outage

PROCESS
├── Migration script not tested on production-like data
│   ├── Staging has 10% of production volume
│   └── Test data doesn't include edge cases
├── Rollback procedure unclear
│   ├── Documentation outdated
│   └── No practiced rollback drill
├── Deployment window too short
│   ├── 2-hour window, needed 4+
│   └── No contingency time
└── Code review missed migration issue
    └── Reviewer unfamiliar with legacy schema

ENVIRONMENT
├── Database schema drift between environments
│   ├── Production has legacy data
│   │   └── Records from 2018 with old format
│   └── Staging recently rebuilt
├── Configuration differences
│   ├── Production has strict FK enforcement
│   └── Staging runs in permissive mode
└── Resource constraints
    └── Memory limit hit during migration

OPERATIONS
├── Monitoring didn't catch early warnings
│   ├── Database locks not alerted
│   └── Slow query not flagged
├── On-call engineer unfamiliar with system
│   └── Regular on-call sick, backup called
└── Escalation delayed
    └── Database team paged 45 min late

PEOPLE
├── Developer new to legacy system
│   ├── Joined 6 weeks ago
│   └── Migration written without guidance
├── DBA review skipped
│   └── "Minor change" exemption used
└── Communication gaps
    └── Schema change not announced to team

LIBRARIES/DEPENDENCIES
├── ORM version mismatch
│   └── Production on v2.1, dev on v2.3
├── Migration tool limitation
│   └── Doesn't support FK constraints properly
└── Legacy stored procedure conflict
    └── Triggered unexpected constraint

EQUIPMENT (Infrastructure)
├── Database server near capacity
│   └── 87% storage used
├── Backup system slow
│   └── Delayed snapshot availability
└── CI/CD pipeline gaps
    └── No production-like environment in pipeline
```

### Root Cause Chain
1. Migration script not tested on production-like data → Script worked on staging
2. Staging environment lacks legacy data → Data from 2018 has old format
3. Old format records violate new FK constraint → Script fails
4. Why no production-like test data? → Cost and security concerns
5. Why was this risk not identified? → No DBA review of "minor" change

### Countermeasures
1. Require DBA review for all schema changes (no exemptions)
2. Create anonymized production data snapshot for staging
3. Add FK constraint validation to CI pipeline
4. Extend deployment window for migrations
5. Conduct quarterly rollback drills

---

## Anti-Example: Poorly Executed Fishbone (With Corrections)

### Original (Problematic)

**Problem Statement**: "Quality problems"

**Causes identified**:
- Man: "John messed up", "People don't care"
- Machine: "Old equipment"
- Method: "Bad processes"
- Material: "Cheap materials"
- Measurement: (empty)
- Environment: (empty)

### Issues
1. ❌ Problem statement vague
2. ❌ Person-blame in Man category
3. ❌ Causes too generic
4. ❌ Two categories empty
5. ❌ No sub-causes
6. ❌ No prioritization

### Corrected Version

**Problem Statement**: "Dimensional tolerance failures (>±0.1mm) on Part #4521 increased from 2% to 8% reject rate in December"

**Corrected causes**:
```
MAN (People)
├── Training gap on new tolerance spec
│   ├── Spec change in November
│   └── No retraining conducted
├── Inspection technique inconsistent
│   └── No standardized method documented
└── Fatigue during overtime
    └── 20% overtime increase in Dec

MACHINE
├── Press #2 alignment degraded
│   ├── Last aligned 6 months ago
│   └── Spec is quarterly
└── Die wear exceeds spec
    └── 50,000 cycles since last refurb

METHOD
├── Setup procedure not followed
│   └── Steps skipped under time pressure
└── In-process check frequency reduced
    └── Changed from hourly to per-shift

MATERIAL
├── Supplier changed in November
│   └── Cost reduction initiative
└── Hardness at edge of spec
    └── 3 lots at upper limit

MEASUREMENT
├── Gauge R&R not conducted
│   └── Unknown measurement system variation
└── SPC chart trends ignored
    └── Upward trend visible since Nov 15

ENVIRONMENT
├── Temperature swings in December
│   └── HVAC struggling in cold weather
└── Humidity dropped below spec
    └── No humidifier in press area
```

### Improvements Made
- Specific, measurable problem statement
- Person-blame converted to system focus
- All categories populated with specific causes
- Multiple levels of sub-causes
- Evidence-based where possible
- Ready for prioritization and verification
