# Requirement Anti-Patterns

Detailed examples of common requirement mistakes and how to fix them.

## 1. The Wishful Requirement

**Problem:** Describes desired outcome without specifying what the system does.

**Bad:**
```markdown
REQ-001: Users should have a great experience.
```

**Good:**
```markdown
REQ-001: System shall display page content within 2 seconds on 3G connections.
REQ-002: System shall provide inline validation feedback within 100ms of user input.
REQ-003: System shall remember user preferences across sessions.
```

**Why it matters:** "Great experience" cannot be tested. The fixed version has measurable criteria.

---

## 2. The Compound Requirement

**Problem:** Multiple requirements bundled together, making partial compliance ambiguous.

**Bad:**
```markdown
REQ-001: System shall authenticate users, authorize access to resources,
         and log all security events.
```

**Good:**
```markdown
REQ-001: System shall authenticate users via OAuth 2.0 or username/password.
REQ-002: System shall authorize resource access based on role-based permissions.
REQ-003: System shall log all authentication attempts with timestamp and result.
REQ-004: System shall log all authorization decisions with user, resource, and result.
```

**Why it matters:** If logging fails, is REQ-001 met? Splitting allows partial completion tracking.

---

## 3. The Solution-as-Requirement

**Problem:** Specifies implementation instead of need.

**Bad:**
```markdown
REQ-001: System shall use Redis for session storage.
REQ-002: System shall implement JWT tokens for authentication.
```

**Good:**
```markdown
REQ-001: System shall maintain user sessions across requests for up to 24 hours.
REQ-002: System shall support stateless authentication for API clients.

CONSTRAINT-001: Session storage must support horizontal scaling.
CONSTRAINT-002: Authentication tokens must be validatable without database lookup.
```

**Why it matters:** Requirements should be technology-agnostic. Redis and JWT are implementation choices, not requirements. If requirements change, implementation can adapt.

---

## 4. The Assumed Context Requirement

**Problem:** Relies on unstated assumptions about environment or users.

**Bad:**
```markdown
REQ-001: System shall integrate with the standard payment provider.
REQ-002: System shall follow company security guidelines.
```

**Good:**
```markdown
REQ-001: System shall integrate with Stripe for payment processing.
REQ-002: System shall implement OWASP Top 10 security controls.
         Reference: security-standards.md for specific controls.
```

**Why it matters:** "Standard" and "company guidelines" are undefined. Different readers will interpret differently.

---

## 5. The Negative-Only Requirement

**Problem:** Only states what NOT to do, leaving positive behavior undefined.

**Bad:**
```markdown
REQ-001: System shall not expose user passwords.
```

**Good:**
```markdown
REQ-001: System shall store passwords using bcrypt with cost factor 12.
REQ-002: System shall never include passwords in logs or error messages.
REQ-003: System shall transmit passwords only over TLS 1.2+.
```

**Why it matters:** "Not expose" has infinite interpretations. Positive requirements define the expected behavior.

---

## 6. The Moving Target Requirement

**Problem:** References external sources that can change without notice.

**Bad:**
```markdown
REQ-001: System shall comply with current GDPR regulations.
REQ-002: System shall follow the latest API design trends.
```

**Good:**
```markdown
REQ-001: System shall comply with GDPR as of May 2018 regulation text.
         Specific controls: right to erasure, data portability, consent tracking.
REQ-002: System shall follow REST API conventions per our api-standards.md v2.1.
```

**Why it matters:** "Current" and "latest" will change. Pin to specific versions or dates.

---

## 7. The Orphan Requirement

**Problem:** Requirement exists without traceability to business need or user story.

**Bad:**
```markdown
REQ-047: System shall support WebSocket connections.
```

**Good:**
```markdown
REQ-047: System shall support WebSocket connections.
         Business Need: Real-time collaboration requires <100ms update latency.
         User Story: US-012 (Collaborative document editing)
         Acceptance: Multiple users see edits within 100ms of each other.
```

**Why it matters:** Without traceability, requirements can't be prioritized or validated against business goals.

---

## 8. The Incomplete Enumeration

**Problem:** Lists examples without defining completeness.

**Bad:**
```markdown
REQ-001: System shall support file uploads (PDF, DOC, images, etc.)
```

**Good:**
```markdown
REQ-001: System shall support file uploads for:
         - PDF (application/pdf)
         - Word documents (.doc, .docx)
         - Images (JPEG, PNG, GIF, WebP)
         - Maximum file size: 10MB
         - Other formats shall be rejected with clear error message.
```

**Why it matters:** "etc." is the enemy of testability. Either enumerate all, or explicitly state the rule.

---

## 9. The Performance Aspiration

**Problem:** States performance goals without measurement criteria.

**Bad:**
```markdown
REQ-001: System shall be fast.
REQ-002: System shall handle high load.
REQ-003: System shall scale well.
```

**Good:**
```markdown
REQ-001: System shall respond to API requests within 200ms (p95) under normal load.
REQ-002: System shall maintain <500ms response time (p95) with 1000 concurrent users.
REQ-003: System shall support horizontal scaling to 10x baseline capacity.

Definitions:
- Normal load: 100 requests/second
- p95: 95th percentile latency
- Baseline capacity: 1000 concurrent users
```

**Why it matters:** "Fast" and "high load" are relative. Define concrete metrics.

---

## 10. The Implicit Priority Requirement

**Problem:** All requirements appear equal, but implementation reveals hidden priorities.

**Bad:**
```markdown
REQ-001: System shall support user registration.
REQ-002: System shall support social login.
REQ-003: System shall support SSO.
```

**Good:**
```markdown
REQ-001 [MUST]: System shall support user registration via email/password.
REQ-002 [SHOULD]: System shall support social login (Google, GitHub).
REQ-003 [MAY]: System shall support enterprise SSO (SAML 2.0).

Priority definitions:
- MUST: Required for MVP
- SHOULD: Expected for v1.0
- MAY: Future consideration
```

**Why it matters:** Without explicit priority, all requirements seem equally important, leading to scope creep.

---

## Summary Table

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| Wishful | Vague outcomes | Add metrics |
| Compound | Multiple verbs | Split into separate REQs |
| Solution-as-Requirement | Technology names | State the need, not the how |
| Assumed Context | "Standard", "normal" | Define explicitly |
| Negative-Only | "Shall not" without "shall" | Add positive requirements |
| Moving Target | "Current", "latest" | Pin to version/date |
| Orphan | No traceability | Link to business need |
| Incomplete Enumeration | "etc.", "and more" | Enumerate or define rule |
| Performance Aspiration | "Fast", "scalable" | Add concrete metrics |
| Implicit Priority | No priority markers | Add MUST/SHOULD/MAY |
