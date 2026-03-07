# Slot Types Reference

Catalog of Phase 1 slot types for the Design Registry. Each type has a JSON Schema definition in `${CLAUDE_PLUGIN_ROOT}/schemas/`.

## Contents

- component -- system/subsystem building blocks
- interface -- connections between components
- contract -- behavioral obligations
- requirement-ref -- references to upstream requirements

---

## component

**Purpose:** Represents a system or subsystem building block in the design decomposition.

**ID Prefix:** `comp-`
**Schema:** `schemas/component.json`

**Required fields:**
| Field | Type | Description |
|-------|------|-------------|
| slot_id | string | `comp-<uuid4>` |
| slot_type | const | `"component"` |
| name | string (1-200 chars) | Component name |
| version | integer (>= 1) | Monotonic version number |
| created_at | date-time | UTC creation timestamp |
| updated_at | date-time | UTC last-update timestamp |

**Optional fields:**
| Field | Type | Description |
|-------|------|-------------|
| description | string | Component description |
| source_block | string | Architecture block this component derives from |
| status | enum | `proposed`, `approved`, `rejected`, `modified`, `deprecated` |
| parent_requirements | array of strings | Upstream requirement IDs |
| rationale | string | Design rationale for this component |
| extensions | object | Free-form custom fields |

---

## interface

**Purpose:** Defines a connection or communication path between two components.

**ID Prefix:** `intf-`
**Schema:** `schemas/interface.json`

**Required fields:**
| Field | Type | Description |
|-------|------|-------------|
| slot_id | string | `intf-<uuid4>` |
| slot_type | const | `"interface"` |
| name | string (1-200 chars) | Interface name |
| version | integer (>= 1) | Monotonic version number |
| created_at | date-time | UTC creation timestamp |
| updated_at | date-time | UTC last-update timestamp |

**Optional fields:**
| Field | Type | Description |
|-------|------|-------------|
| description | string | Interface description |
| source_component | string | Providing component slot ID |
| target_component | string | Consuming component slot ID |
| protocol | string | Communication protocol (e.g., REST, gRPC, event) |
| data_format | string | Data serialization format (e.g., JSON, protobuf) |
| status | enum | `proposed`, `approved`, `rejected`, `modified`, `deprecated` |
| parent_requirements | array of strings | Upstream requirement IDs |
| extensions | object | Free-form custom fields |

---

## contract

**Purpose:** Specifies behavioral obligations for an interface or component interaction.

**ID Prefix:** `cntr-`
**Schema:** `schemas/contract.json`

**Required fields:**
| Field | Type | Description |
|-------|------|-------------|
| slot_id | string | `cntr-<uuid4>` |
| slot_type | const | `"contract"` |
| name | string (1-200 chars) | Contract name |
| version | integer (>= 1) | Monotonic version number |
| created_at | date-time | UTC creation timestamp |
| updated_at | date-time | UTC last-update timestamp |

**Optional fields:**
| Field | Type | Description |
|-------|------|-------------|
| description | string | Contract description |
| component_id | string | Component this contract applies to |
| interface_id | string | Interface this contract governs |
| obligations | array of objects | List of behavioral obligations |
| vv_method | enum | `test`, `analysis`, `inspection`, `demonstration` |
| status | enum | `proposed`, `approved`, `rejected`, `modified`, `deprecated` |
| parent_requirements | array of strings | Upstream requirement IDs |
| extensions | object | Free-form custom fields |

---

## requirement-ref

**Purpose:** References an upstream requirement from an external requirements registry, enabling traceability.

**ID Prefix:** `rref-`
**Schema:** `schemas/requirement-ref.json`

**Required fields:**
| Field | Type | Description |
|-------|------|-------------|
| slot_id | string | `rref-<uuid4>` |
| slot_type | const | `"requirement-ref"` |
| name | string (1-200 chars) | Reference name |
| version | integer (>= 1) | Monotonic version number |
| created_at | date-time | UTC creation timestamp |
| updated_at | date-time | UTC last-update timestamp |

**Optional fields:**
| Field | Type | Description |
|-------|------|-------------|
| description | string | Reference description |
| upstream_id | string | The REQ-NNN ID from the upstream registry |
| upstream_source | string | Path to the source requirements registry |
| category | string | Requirement category (functional, performance, etc.) |
| priority | string | Priority level |
| status | enum | `proposed`, `approved`, `rejected`, `modified`, `deprecated` |
| trace_links | array of strings | Design slot IDs this requirement traces to |
| extensions | object | Free-form custom fields |

---

## View-Only Slot Types

These slot types appear only in assembled view output (not in the Design Registry).

### unlinked

**Purpose:** Contains orphan slots (interfaces and contracts) that could not be linked to a parent component within the view's scope.

**When it appears:** During hierarchical view organization, interfaces without a matching `source_component` or `target_component` in the view, and contracts without a matching `interface_id`, are grouped into an `"unlinked"` section rather than being dropped.

**For diagram consumers (Phase 8+):** When generating diagrams from view output, `slot_type: "unlinked"` sections should be rendered as a separate group or with visual distinction (e.g., dashed borders, "Unlinked" label) to indicate these slots lack structural connections in the current view scope.

**Schema:** Unlinked section slots have the same fields as their original slot type (interface or contract). The `slot_type` field on each individual slot retains its original value (e.g., `"interface"`, `"contract"`); only the section-level `slot_type` is `"unlinked"`.

---

## Future Slot Types

Additional slot types will be added in later phases:
- **decision** (Phase 3): Design decisions with rationale and alternatives
- **trade-study** (Phase 3): Comparative analysis records
- **risk** (Phase 4): Risk items with likelihood and impact
- **verification** (Phase 5): V&V records linked to contracts
