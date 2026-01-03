# Critical Path Analysis - Detailed Reference

Methods for identifying and analyzing critical dependencies, bottlenecks, and failure chains.

## Table of Contents
- [Dependency Mapping](#dependency-mapping)
  - [N² (N-Squared) Diagram](#n²-n-squared-diagram)
  - [Dependency Types](#dependency-types)
- [Critical Path Identification](#critical-path-identification)
  - [Definition](#definition)
  - [Finding Critical Paths](#finding-critical-paths)
  - [Critical Path Metrics](#critical-path-metrics)
- [Single Points of Failure (SPOF)](#single-points-of-failure-spof)
  - [Identification Questions](#identification-questions)
  - [SPOF Categories](#spof-categories)
  - [SPOF Remediation Patterns](#spof-remediation-patterns)
- [Bottleneck Detection](#bottleneck-detection)
  - [Bottleneck Indicators](#bottleneck-indicators)
  - [Common Bottleneck Locations](#common-bottleneck-locations)
  - [Bottleneck Analysis Template](#bottleneck-analysis-template)
- [Temporal Analysis](#temporal-analysis)
  - [Sequencing Issues](#sequencing-issues)
  - [Timing Dependency Analysis](#timing-dependency-analysis)
  - [Timeout Strategy Evaluation](#timeout-strategy-evaluation)
- [Cascade Failure Analysis](#cascade-failure-analysis)
  - [Failure Propagation Paths](#failure-propagation-paths)
  - [Blast Radius Estimation](#blast-radius-estimation)
  - [Circuit Breaker Placement](#circuit-breaker-placement)
- [Risk Scoring Matrix](#risk-scoring-matrix)

---

## Dependency Mapping

### N² (N-Squared) Diagram

Matrix showing component interactions:

```
           Component A  Component B  Component C  Component D
Component A     -           →             →            
Component B     ←           -                          →
Component C                              -             →
Component D                 ←             ←            -

Legend: → provides to, ← receives from
```

**Interpretation**:
- Row shows what component provides
- Column shows what component receives
- Dense rows = potential single point of failure
- Dense columns = high dependency (fragile)
- Empty cells = possible gaps or true independence

### Dependency Types

| Type | Characteristics | Risk Level |
|------|-----------------|------------|
| Compile-time | Must exist to build | High - blocks development |
| Runtime | Must exist to run | High - blocks operation |
| Optional | Enhances but not required | Low - graceful degradation |
| Temporal | Must happen in order | Medium - sequencing issues |
| Data | Shares data structures | Medium - coupling smell |

## Critical Path Identification

### Definition

The critical path is the longest sequence of dependent activities that determines minimum completion time (for projects) or maximum latency (for systems).

### Finding Critical Paths

1. **List all activities/components** with duration/latency
2. **Map dependencies** (what must complete before what)
3. **Calculate forward pass** (earliest start/finish times)
4. **Calculate backward pass** (latest start/finish without delay)
5. **Identify zero-float activities** (no slack = critical)

### Critical Path Metrics

| Metric | Meaning |
|--------|---------|
| Path length | Sum of durations on critical path |
| Float/slack | How much delay before path becomes critical |
| Path convergence | Where multiple paths meet (risky) |
| Path density | How many activities on critical path vs total |

## Single Points of Failure (SPOF)

### Identification Questions

For each component:
1. If this fails, what else stops working?
2. Is there a redundant alternative?
3. How quickly can it be replaced/restarted?
4. Who knows how to fix it?

### SPOF Categories

| Category | Examples |
|----------|----------|
| Infrastructure | Single database, single region, single DNS |
| Knowledge | One person knows the system |
| Process | One approval required, single environment |
| Data | Single source of truth with no backup |
| External | Single vendor, single API, single network path |

### SPOF Remediation Patterns

| Pattern | Description |
|---------|-------------|
| Redundancy | Multiple instances, failover capability |
| Degradation | Function reduced but not eliminated |
| Caching | Stale data better than no data |
| Circuit breaker | Fail fast, prevent cascade |
| Timeout + retry | Transient failures handled |
| Documentation | Knowledge captured, not just in heads |

## Bottleneck Detection

### Bottleneck Indicators

- Queue buildup at a component
- Consistent full utilization while others idle
- Performance scales with this component's capacity
- Removing other limits doesn't improve throughput

### Common Bottleneck Locations

| Location | Signs |
|----------|-------|
| Database | Connection pool exhaustion, slow queries |
| Network | Bandwidth saturation, high latency |
| CPU | 100% utilization, processing delay |
| Memory | Swapping, OOM errors |
| I/O | Disk queue depth, write latency |
| External API | Rate limiting, timeouts |
| Shared lock | Contention, deadlock potential |

### Bottleneck Analysis Template

```markdown
**Component**: [Name]
**Type**: [CPU/Memory/I/O/Network/Lock/External]
**Current capacity**: [Measured value]
**Demand pattern**: [Steady/Bursty/Growing]
**Headroom**: [% capacity remaining at peak]
**Scaling options**:
  - Vertical: [What's possible, cost]
  - Horizontal: [What's possible, complexity]
**Short-term mitigation**: [Quick wins]
**Long-term solution**: [Architectural change needed]
```

## Temporal Analysis

### Sequencing Issues

| Issue | Description | Detection |
|-------|-------------|-----------|
| Race condition | Outcome depends on timing | Multiple valid orderings produce different results |
| Deadlock | Circular wait | Processes blocked forever |
| Livelock | Active but no progress | Busy loop with no advancement |
| Starvation | Some never get resources | Long tail latency, fairness issues |
| Priority inversion | Low priority blocks high | High-priority waits on low-priority |

### Timing Dependency Analysis

Questions to answer:
1. What happens if component A is slower than expected?
2. What happens if clock skew exists between systems?
3. What happens if network partition occurs?
4. What happens if backpressure isn't respected?
5. What happens if operations arrive out of order?

### Timeout Strategy Evaluation

For each cross-component call:
| Aspect | Current State | Risk |
|--------|---------------|------|
| Timeout configured? | Yes/No | |
| Timeout value reasonable? | [value] | |
| Retry policy defined? | [policy] | |
| Circuit breaker in place? | Yes/No | |
| Fallback behavior defined? | [behavior] | |

## Cascade Failure Analysis

### Failure Propagation Paths

Map how failures spread:

```
Component A fails
    ↓
Component B times out waiting for A
    ↓
Component B's clients retry aggressively
    ↓
Component C (shared with B) overloads
    ↓
Components D, E, F lose access to C
    ↓
System-wide degradation
```

### Blast Radius Estimation

For each component:
- Immediate dependencies (directly affected)
- Transitive dependencies (indirectly affected)
- Shared resources (collateral damage)
- User-facing impact (visible degradation)

### Circuit Breaker Placement

Priority for circuit breakers:
1. External service calls
2. Database connections
3. Cross-service calls
4. Resource-intensive operations

## Risk Scoring Matrix

Combine probability and impact:

| Probability → | Rare | Unlikely | Possible | Likely | Certain |
|---------------|------|----------|----------|--------|---------|
| **Catastrophic** | Medium | High | Critical | Critical | Critical |
| **Major** | Low | Medium | High | Critical | Critical |
| **Moderate** | Low | Low | Medium | High | Critical |
| **Minor** | Low | Low | Low | Medium | High |
| **Negligible** | Low | Low | Low | Low | Medium |

Use this to prioritize which critical paths and SPOFs to address first.
