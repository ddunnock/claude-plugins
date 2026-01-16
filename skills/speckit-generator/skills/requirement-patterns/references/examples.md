# Requirement Examples by Domain

Complete, well-structured requirement examples for common domains.

## Authentication System

### User Stories

```markdown
### US-AUTH-001: User Registration
As a new visitor,
I want to create an account with my email,
So that I can access personalized features.

**Acceptance Criteria:**
- Given a valid email and password (8+ chars, 1 uppercase, 1 number)
- When I submit the registration form
- Then my account is created
- And I receive a verification email within 60 seconds
- And I cannot access protected features until verified

### US-AUTH-002: Password Reset
As a registered user who forgot my password,
I want to reset it via email,
So that I can regain access without contacting support.

**Acceptance Criteria:**
- Given I request a password reset for a valid email
- When the system processes the request
- Then I receive a reset link within 60 seconds
- And the link expires after 24 hours
- And the link can only be used once
- And using the link invalidates any previous reset links
```

### Formal Requirements

```markdown
## Authentication Requirements

### REQ-AUTH-001 [MUST]: Email/Password Authentication
System shall authenticate users via email and password combination.
- Passwords must be 8+ characters with 1 uppercase and 1 number
- Failed attempts shall be rate-limited to 5 per 15 minutes per IP
- Successful login shall create session valid for 24 hours

### REQ-AUTH-002 [MUST]: Password Storage
System shall store passwords using bcrypt with cost factor 12.
- Plain text passwords shall never be stored or logged
- Password comparison shall use constant-time comparison

### REQ-AUTH-003 [SHOULD]: OAuth Integration
System should support OAuth 2.0 authentication with:
- Google (OpenID Connect)
- GitHub
- Microsoft Azure AD

### REQ-AUTH-004 [MUST]: Session Management
System shall manage user sessions with:
- Session tokens: cryptographically random, 256-bit minimum
- Session storage: server-side with encrypted cookie reference
- Session expiry: 24 hours inactive, 7 days absolute maximum
- Concurrent sessions: unlimited per user (configurable)
```

---

## E-Commerce Cart

### User Stories

```markdown
### US-CART-001: Add Item to Cart
As a shopper,
I want to add products to my cart,
So that I can purchase multiple items together.

**Acceptance Criteria:**
- Given I am viewing a product with available inventory
- When I click "Add to Cart"
- Then the item appears in my cart within 500ms
- And the cart total updates to reflect the new item
- And I can continue shopping without page reload

### US-CART-002: Persistent Cart
As a returning shopper,
I want my cart to persist across sessions,
So that I don't lose items I added earlier.

**Acceptance Criteria:**
- Given I have items in my cart and close the browser
- When I return within 30 days
- Then my cart contains the same items
- And prices are updated to current prices
- And unavailable items are flagged but not removed
```

### Formal Requirements

```markdown
## Cart Requirements

### REQ-CART-001 [MUST]: Item Addition
System shall allow adding items to cart with:
- Product ID and quantity validation
- Inventory check before addition
- Maximum 99 units per line item
- Maximum 50 distinct items per cart

### REQ-CART-002 [MUST]: Price Calculation
System shall calculate cart totals with:
- Line item subtotal: unit price × quantity
- Cart subtotal: sum of line item subtotals
- Tax calculation: based on shipping destination
- Discount application: in priority order (item, cart, shipping)
- All calculations shall use decimal precision (2 decimal places, ROUND_HALF_UP)

### REQ-CART-003 [SHOULD]: Cart Persistence
System should persist carts for:
- Authenticated users: 30 days from last modification
- Anonymous users: 7 days via cookie
- Cart merge on login: anonymous cart items added to user cart

### REQ-CART-004 [MUST]: Inventory Validation
System shall validate inventory at:
- Add to cart: warn if low stock, block if zero
- Checkout start: reserve inventory for 15 minutes
- Payment completion: decrement inventory atomically
- Payment failure: release reserved inventory
```

---

## API Design

### User Stories

```markdown
### US-API-001: Resource Listing
As an API consumer,
I want to list resources with pagination,
So that I can efficiently browse large datasets.

**Acceptance Criteria:**
- Given I request GET /api/v1/resources
- When the request is authenticated
- Then I receive a paginated response with:
  - data: array of resources (default 20, max 100)
  - meta: { total, page, per_page, total_pages }
  - links: { self, first, last, next, prev }
- And response time is < 200ms for uncached requests
```

### Formal Requirements

```markdown
## API Requirements

### REQ-API-001 [MUST]: REST Conventions
System shall follow REST conventions:
- Resources as nouns: /users, /orders, /products
- HTTP verbs for actions: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove)
- Plural resource names: /users not /user
- Nested resources for relationships: /users/{id}/orders

### REQ-API-002 [MUST]: Response Format
System shall return JSON responses with:
- Content-Type: application/json
- Consistent envelope: { data, meta, errors }
- ISO 8601 timestamps: 2024-01-15T10:30:00Z
- Snake_case field names

### REQ-API-003 [MUST]: Error Responses
System shall return errors with:
- Appropriate HTTP status codes (400, 401, 403, 404, 422, 500)
- Error body: { errors: [{ code, message, field?, detail? }] }
- No stack traces in production
- Correlation ID for support reference

### REQ-API-004 [MUST]: Rate Limiting
System shall enforce rate limits:
- Anonymous: 60 requests/minute
- Authenticated: 1000 requests/minute
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- Exceeded: 429 Too Many Requests with Retry-After header
```

---

## Data Processing Pipeline

### User Stories

```markdown
### US-PIPE-001: File Upload Processing
As a data analyst,
I want to upload CSV files for processing,
So that I can analyze data without manual transformation.

**Acceptance Criteria:**
- Given I upload a valid CSV file (< 100MB)
- When the upload completes
- Then processing begins within 5 seconds
- And I receive progress updates every 10 seconds
- And processing completes within 5 minutes for 1M rows
- And I can download results as CSV or JSON
```

### Formal Requirements

```markdown
## Pipeline Requirements

### REQ-PIPE-001 [MUST]: File Ingestion
System shall accept files with:
- Formats: CSV, JSON, Parquet
- Maximum size: 100MB per file
- Encoding: UTF-8 (auto-detect with fallback to Latin-1)
- Validation: schema check before processing

### REQ-PIPE-002 [MUST]: Processing Guarantees
System shall process data with:
- At-least-once delivery (idempotent operations required)
- Checkpointing every 10,000 records
- Resume from checkpoint on failure
- Maximum 3 retry attempts per record

### REQ-PIPE-003 [MUST]: Performance Targets
System shall meet performance targets:
- Throughput: 10,000 records/second minimum
- Latency: < 100ms per record transformation
- Memory: < 500MB per worker process
- Scalability: linear scaling to 10 workers

### REQ-PIPE-004 [SHOULD]: Observability
System should provide:
- Real-time progress: records processed, estimated completion
- Error reporting: failed records with error details
- Metrics: throughput, latency histograms, error rates
- Alerting: notification on failure or SLA breach
```

---

## Template: Blank Requirement Document

```markdown
# [Feature Name] Requirements

## Overview
[1-2 sentence description of the feature]

## User Stories

### US-[FEATURE]-001: [Story Title]
As a [specific role],
I want [concrete action],
So that [measurable benefit].

**Acceptance Criteria:**
- Given [precondition]
- When [action]
- Then [expected result]
- And [additional expectations]

## Functional Requirements

### REQ-[FEATURE]-001 [MUST/SHOULD/MAY]: [Requirement Title]
System shall [specific behavior].
- [Detail 1]
- [Detail 2]
- [Constraint or limit]

## Non-Functional Requirements

### NFR-[FEATURE]-001: Performance
- [Specific metric with target]

### NFR-[FEATURE]-002: Security
- [Specific security control]

## Constraints

### CON-[FEATURE]-001: [Constraint Title]
[Technology, budget, timeline, or other constraint]

## Open Questions

- [ ] [Question 1 - TBD]
- [ ] [Question 2 - TBD]

## References

- [Link to related documents]
- [Link to standards or guidelines]
```
