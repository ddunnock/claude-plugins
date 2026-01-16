# ADR Examples

Real-world examples of well-written Architecture Decision Records.

---

## Example 1: Database Selection (Standard Level)

```markdown
### ADR-001: Use PostgreSQL for Primary Database

**Status**: accepted
**Date**: 2024-01-15
**Decision-makers**: Tech Lead, Senior Backend Developer

**Context and Problem Statement**
We need to select a primary database for our new SaaS application. The application
will handle user accounts, subscription data, and transactional workflows. We
expect 10,000 active users in year one, growing to 100,000 by year three.

**Decision Drivers**
- Must support ACID transactions for payment processing
- Team has strongest experience with relational databases
- Need JSON support for flexible metadata storage
- Budget constraint: < $500/month for database hosting

**Considered Options**
1. PostgreSQL (self-managed on AWS RDS)
2. MySQL (self-managed on AWS RDS)
3. MongoDB Atlas (managed)
4. CockroachDB (managed)

**Decision Outcome**
Chosen option: "PostgreSQL on AWS RDS" because it provides the ACID guarantees
we need for payments, excellent JSON support via JSONB, and our team has 5+
years of PostgreSQL experience. RDS pricing fits our budget at ~$200/month for
our expected load.

**Consequences**
- Good: Strong ACID compliance for payment transactions
- Good: JSONB provides NoSQL-like flexibility where needed
- Good: Team can be productive immediately (no learning curve)
- Good: Excellent tooling ecosystem (pgAdmin, psql, etc.)
- Bad: Horizontal scaling requires more effort than CockroachDB
- Bad: Self-managed RDS requires some operational overhead
- Neutral: Will need to implement connection pooling (PgBouncer) at scale
```

---

## Example 2: Authentication Strategy (Full Level)

```markdown
### ADR-002: Implement OAuth 2.0 with JWT for Authentication

**Status**: accepted
**Date**: 2024-01-20
**Decision-makers**: Security Lead, Tech Lead, Product Owner
**Consulted**: DevOps Engineer, Frontend Lead

**Context and Problem Statement**
Our application needs user authentication. We're building a B2B SaaS product
where enterprise customers expect SSO integration. We also need API
authentication for our mobile app and third-party integrations.

**Decision Drivers**
1. Enterprise customers require SSO compatibility (SAML/OIDC)
2. Mobile app needs stateless authentication
3. API consumers need long-lived tokens for integrations
4. Must support MFA for compliance (SOC 2)
5. Team has limited security expertise

**Considered Options**
1. **OAuth 2.0 + JWT**: Industry standard, self-implemented
2. **Auth0**: Managed authentication service
3. **AWS Cognito**: AWS-native authentication
4. **Session-based auth**: Traditional server-side sessions

**Pros and Cons of Options**

#### Option 1: OAuth 2.0 + JWT (Self-implemented)
- Good: Full control over authentication flow
- Good: No per-user costs at scale
- Good: Deep integration possible
- Bad: Significant implementation effort
- Bad: Security responsibility on our team
- Bad: Must maintain and update ourselves

#### Option 2: Auth0
- Good: Enterprise SSO out of the box
- Good: MFA, passwordless, social login included
- Good: SOC 2 compliant
- Bad: $23,000/year at 10,000 MAU
- Bad: Vendor lock-in for critical infrastructure
- Neutral: Some customization limits

#### Option 3: AWS Cognito
- Good: Low cost (~$0.0055/MAU)
- Good: AWS ecosystem integration
- Good: Built-in MFA
- Bad: Limited SSO customization
- Bad: UI customization is painful
- Bad: Documentation gaps

#### Option 4: Session-based
- Good: Simple to implement
- Good: No token management complexity
- Bad: Doesn't work for mobile/API
- Bad: No SSO support
- Bad: Scaling requires sticky sessions

**Decision Outcome**
Chosen option: "Auth0" because enterprise SSO is a critical requirement and
our team lacks deep security expertise. The cost is justified by reduced
implementation time (estimated 3 months saved) and the security assurance
of a SOC 2 compliant provider. We accept the vendor dependency as a trade-off.

**Consequences**
- Good: Enterprise SSO available from day one
- Good: MFA and compliance features included
- Good: Reduced security burden on team
- Good: 3+ months faster to market
- Bad: $23K/year ongoing cost
- Bad: Auth0 becomes critical dependency
- Bad: Some UX flows limited by Auth0 capabilities

**Confirmation**
- Success metric: Zero authentication-related security incidents
- Success metric: < 2 hours to onboard new SSO customer
- 90-day review: Evaluate Auth0 customization pain points
- 1-year review: Reassess build vs. buy as team grows

**Traceability**
- Requirements: REQ-AUTH-001, REQ-AUTH-002, REQ-SEC-003
- Tasks: TASK-015, TASK-016, TASK-017
```

---

## Example 3: API Versioning (Lightweight Level)

```markdown
### ADR-003: Use URL Path Versioning for API

**Status**: accepted

**Context and Problem Statement**
We need a versioning strategy for our public API. Breaking changes will occur
as we evolve the product, and we need to support older clients during migration.

**Decision Outcome**
Chosen option: "URL path versioning" (e.g., `/api/v1/users`)

We chose this over header-based versioning because:
- It's immediately visible and debuggable
- Works with all HTTP clients without special configuration
- Easy to route different versions to different services if needed

**Consequences**
- Good: Clear, visible versioning in URLs
- Good: Easy to test different versions
- Good: Simple routing configuration
- Bad: URLs are "ugly" with version prefix
- Bad: Can't version individual endpoints differently
```

---

## Example 4: Rejected Decision

```markdown
### ADR-004: Do Not Use GraphQL for Public API

**Status**: rejected

**Context and Problem Statement**
The frontend team suggested using GraphQL instead of REST for our public API
to reduce over-fetching and simplify client-side data requirements.

**Decision Drivers**
- Frontend wants flexible queries
- Mobile app has bandwidth constraints
- We have limited backend resources
- Public API must be stable and documented

**Considered Options**
1. GraphQL for all APIs
2. GraphQL for internal, REST for public
3. REST with sparse fieldsets

**Decision Outcome**
Chosen option: "REST with sparse fieldsets" - We rejected GraphQL because:

1. **Security complexity**: GraphQL query depth attacks require additional
   protection that our small team can't properly implement and maintain.

2. **Caching difficulty**: REST caching is straightforward; GraphQL requires
   custom caching solutions that add operational burden.

3. **Documentation**: REST APIs are self-documenting with OpenAPI; GraphQL
   requires different tooling our team doesn't know.

4. **Client diversity**: Our public API serves many third-party integrations
   that expect REST; GraphQL would increase their integration burden.

We will implement sparse fieldsets (`?fields=id,name,email`) to address
over-fetching concerns while maintaining REST simplicity.

**Consequences**
- Good: Simpler security model
- Good: Standard HTTP caching works
- Good: OpenAPI documentation
- Good: Lower learning curve for API consumers
- Bad: Some over-fetching will occur
- Bad: Frontend must make multiple requests in some cases
```

---

## Example 5: Technology Migration (Superseding)

```markdown
### ADR-005: Migrate from Redis to Valkey for Caching

**Status**: accepted
**Date**: 2024-06-01
**Supersedes**: ADR-012 (Use Redis for Caching)

**Context and Problem Statement**
Redis changed to a non-open-source license (RSALv2) in March 2024. Our legal
team has concerns about the new license terms for our SaaS product. Valkey
is an open-source fork maintained by the Linux Foundation with backing from
AWS, Google, and Oracle.

**Decision Drivers**
- Legal requires truly open-source dependencies
- Must maintain API compatibility (no application changes)
- Cannot have downtime during migration
- Team has no capacity for major changes

**Considered Options**
1. Valkey (Redis fork, Linux Foundation)
2. KeyDB (Redis fork, Snap Inc.)
3. Dragonfly (Redis-compatible, different architecture)
4. Accept Redis license

**Decision Outcome**
Chosen option: "Valkey" because it's a drop-in replacement with identical
API, backed by major cloud providers, and maintained by Linux Foundation
(strong governance). Migration requires only infrastructure changes, no
application code modifications.

**Consequences**
- Good: Resolves licensing concerns
- Good: Zero application code changes
- Good: Strong community backing
- Good: Can use AWS ElastiCache for Valkey
- Bad: Some uncertainty as newer project
- Bad: Documentation still maturing
- Neutral: Need to update infrastructure-as-code

**Traceability**
- Supersedes: ADR-012
- Tasks: TASK-089 (Infrastructure migration)
```

---

## Anti-Pattern Examples (What NOT to Do)

### Bad: Missing Context

```markdown
### ADR-006: Use React

**Status**: accepted

**Decision**
We will use React.

**Consequences**
- Good: React is popular
```

**Problems:**
- No context explaining why a decision was needed
- No alternatives considered
- No meaningful consequences
- No drivers or rationale

### Bad: Solution as Context

```markdown
### ADR-007: Implement Microservices

**Context**
We need to implement microservices because they are better than monoliths.

**Decision**
Use microservices architecture.
```

**Problems:**
- Context already assumes the solution
- No actual problem statement
- No alternatives (monolith should be an option)
- Circular reasoning

### Bad: Too Vague

```markdown
### ADR-008: Improve Performance

**Context**
The system is slow.

**Decision**
Make it faster by optimizing things.

**Consequences**
- Good: Better performance
- Bad: Takes time
```

**Problems:**
- No specific metrics or targets
- "Optimizing things" is not a decision
- Consequences don't say anything meaningful
