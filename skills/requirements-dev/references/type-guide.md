# Requirement Type Definitions and Examples

Reference document defining the five requirement types with examples, identification guidance, and block-pattern hints.

## Functional Requirements

**Definition:** Describe what the system shall do -- actions, behaviors, transformations.

**Examples:**
- "The system shall authenticate users via OAuth 2.0 before granting access to protected resources."
- "The system shall generate a PDF report summarizing all transactions for the selected date range."
- "The system shall notify administrators via email when disk usage exceeds 90%."

**When to expect:** Every functional block should have at least one. These form the core of what the system does.

**Block pattern:** Look at each block's purpose statement -- each verb maps to a functional requirement.

## Performance Requirements

**Definition:** Describe how well the system shall perform -- speed, throughput, capacity, resource usage.

**Examples:**
- "The system shall respond to API requests within 200ms at the 95th percentile under normal load."
- "The system shall support 10,000 concurrent user sessions without degradation."
- "The system shall consume no more than 512MB of memory during standard operation."

**When to expect:** Any block with timing, load, or resource constraints. Critical for interfaces between blocks.

**Block pattern:** Look for implicit "fast enough" or "big enough" assumptions in block descriptions.

## Interface/API Requirements

**Definition:** Describe how the system connects to external systems, users, or other blocks -- protocols, formats, contracts.

**Examples:**
- "The system shall expose a REST API conforming to OpenAPI 3.0 specification."
- "The system shall accept input data in JSON format with UTF-8 encoding."
- "The system shall integrate with the payment gateway via its published SDK (version 4.x)."

**When to expect:** Every block boundary, external system integration, and user-facing interface.

**Block pattern:** Look at block relationship arrows in the architecture -- each arrow implies interface requirements.

## Constraint Requirements

**Definition:** Describe limitations the system shall operate within -- regulatory, environmental, technological, organizational.

**Examples:**
- "The system shall store personal data only in EU-region data centers to comply with GDPR."
- "The system shall be implemented using Python 3.11 or later."
- "The system shall operate in environments with ambient temperatures between 0C and 50C."

**When to expect:** Regulatory blocks, technology selection blocks, deployment environment considerations.

**Block pattern:** Look for "must use", "limited to", "compliant with" language in block descriptions.

## Quality Requirements

**Definition:** Describe non-functional characteristics -- reliability, maintainability, security, usability.

**Examples:**
- "The system shall achieve 99.9% uptime measured monthly."
- "The system shall log all authentication attempts with timestamps and source IP addresses."
- "The system shall provide user documentation with a Flesch-Kincaid readability score of 60 or higher."

**When to expect:** Cross-cutting concerns that apply across multiple blocks. Often derived from stakeholder quality expectations.

**Block pattern:** Quality requirements often emerge from "how good" questions applied to the system as a whole.
