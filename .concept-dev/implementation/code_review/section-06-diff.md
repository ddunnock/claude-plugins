diff --git a/skills/requirements-dev/scripts/requirement_tracker.py b/skills/requirements-dev/scripts/requirement_tracker.py
index b36a0ed..3a8aea1 100644
--- a/skills/requirements-dev/scripts/requirement_tracker.py
+++ b/skills/requirements-dev/scripts/requirement_tracker.py
@@ -1 +1,309 @@
-"""Requirements registry management with type-guided tracking."""
+#!/usr/bin/env python3
+"""Requirements registry management with type-guided tracking.
+
+Usage:
+    python3 requirement_tracker.py --workspace <path> add --statement "..." --type functional --priority high --source-block blk
+    python3 requirement_tracker.py --workspace <path> register --id REQ-001 --parent-need NEED-001
+    python3 requirement_tracker.py --workspace <path> baseline --id REQ-001
+    python3 requirement_tracker.py --workspace <path> withdraw --id REQ-001 --rationale "..."
+    python3 requirement_tracker.py --workspace <path> list [--include-withdrawn]
+    python3 requirement_tracker.py --workspace <path> query [--type X] [--source-block Y] [--level N]
+    python3 requirement_tracker.py --workspace <path> export
+
+All mutations use atomic write (temp-file-then-rename) and sync counts to state.json.
+"""
+import argparse
+import json
+import os
+from dataclasses import asdict, dataclass, field
+from datetime import datetime, timezone
+
+from shared_io import _atomic_write, _validate_dir_path
+
+REGISTRY_FILENAME = "requirements_registry.json"
+NEEDS_REGISTRY_FILENAME = "needs_registry.json"
+STATE_FILENAME = "state.json"
+SCHEMA_VERSION = "1.0.0"
+
+VALID_TYPES = {"functional", "performance", "interface", "constraint", "quality"}
+VALID_PRIORITIES = {"high", "medium", "low"}
+
+
+@dataclass
+class Requirement:
+    id: str
+    statement: str
+    type: str
+    priority: str
+    status: str = "draft"
+    parent_need: str = ""
+    source_block: str = ""
+    level: int = 0
+    attributes: dict = field(default_factory=dict)
+    quality_checks: dict = field(default_factory=dict)
+    tbd_tbr: dict | None = None
+    rationale: str | None = None
+    registered_at: str = ""
+
+
+def _load_registry(workspace: str) -> dict:
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    if os.path.isfile(path):
+        with open(path) as f:
+            return json.load(f)
+    return {"schema_version": SCHEMA_VERSION, "requirements": []}
+
+
+def _save_registry(workspace: str, registry: dict) -> None:
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    _atomic_write(path, registry)
+
+
+def _sync_counts(workspace: str, registry: dict) -> None:
+    state_path = os.path.join(workspace, STATE_FILENAME)
+    if not os.path.isfile(state_path):
+        return
+    with open(state_path) as f:
+        state = json.load(f)
+    reqs = registry["requirements"]
+    state["counts"]["requirements_total"] = len(reqs)
+    state["counts"]["requirements_registered"] = sum(1 for r in reqs if r.get("status") == "registered")
+    state["counts"]["requirements_baselined"] = sum(1 for r in reqs if r.get("status") == "baselined")
+    state["counts"]["requirements_withdrawn"] = sum(1 for r in reqs if r.get("status") == "withdrawn")
+    _atomic_write(state_path, state)
+
+
+def _next_id(registry: dict) -> str:
+    existing = registry.get("requirements", [])
+    if not existing:
+        return "REQ-001"
+    max_num = 0
+    for req in existing:
+        try:
+            num = int(req["id"].split("-")[1])
+            if num > max_num:
+                max_num = num
+        except (IndexError, ValueError):
+            continue
+    return f"REQ-{max_num + 1:03d}"
+
+
+def _find_requirement(registry: dict, req_id: str) -> tuple[int, dict]:
+    for i, req in enumerate(registry["requirements"]):
+        if req["id"] == req_id:
+            return i, req
+    raise ValueError(f"Requirement not found: {req_id}")
+
+
+def add_requirement(
+    workspace: str,
+    statement: str,
+    type: str,
+    priority: str,
+    source_block: str,
+    level: int = 0,
+) -> str:
+    """Add a requirement in draft status. Returns the assigned ID."""
+    workspace = _validate_dir_path(workspace)
+    if type not in VALID_TYPES:
+        raise ValueError(f"Invalid type '{type}'. Must be one of: {sorted(VALID_TYPES)}")
+    if priority not in VALID_PRIORITIES:
+        raise ValueError(f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}")
+
+    registry = _load_registry(workspace)
+    req = Requirement(
+        id=_next_id(registry),
+        statement=statement,
+        type=type,
+        priority=priority,
+        source_block=source_block,
+        level=level,
+        registered_at=datetime.now(timezone.utc).isoformat(),
+    )
+    registry["requirements"].append(asdict(req))
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+    return req.id
+
+
+def register_requirement(workspace: str, req_id: str, parent_need: str) -> None:
+    """Transition a draft requirement to registered status."""
+    if not parent_need or not parent_need.strip():
+        raise ValueError("parent_need is required for registration")
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, req = _find_requirement(registry, req_id)
+
+    # Validate parent need exists
+    needs_path = os.path.join(workspace, NEEDS_REGISTRY_FILENAME)
+    if os.path.isfile(needs_path):
+        with open(needs_path) as f:
+            needs_reg = json.load(f)
+        need_ids = {n["id"] for n in needs_reg.get("needs", [])}
+        if parent_need not in need_ids:
+            raise ValueError(f"Parent need not found: {parent_need}")
+
+    if req["status"] != "draft":
+        raise ValueError(f"Can only register a draft requirement (current status: {req['status']})")
+
+    req["status"] = "registered"
+    req["parent_need"] = parent_need
+    req["registered_at"] = datetime.now(timezone.utc).isoformat()
+    registry["requirements"][idx] = req
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+
+
+def baseline_requirement(workspace: str, req_id: str) -> None:
+    """Transition a registered requirement to baselined status."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, req = _find_requirement(registry, req_id)
+    if req["status"] != "registered":
+        raise ValueError(f"Can only baseline a registered requirement (current status: {req['status']})")
+    req["status"] = "baselined"
+    registry["requirements"][idx] = req
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+
+
+def withdraw_requirement(workspace: str, req_id: str, rationale: str) -> None:
+    """Withdraw a requirement with rationale."""
+    if not rationale or not rationale.strip():
+        raise ValueError("rationale is required for withdrawal")
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, req = _find_requirement(registry, req_id)
+    req["status"] = "withdrawn"
+    req["rationale"] = rationale
+    registry["requirements"][idx] = req
+    _save_registry(workspace, registry)
+    _sync_counts(workspace, registry)
+
+
+def list_requirements(workspace: str, include_withdrawn: bool = False) -> list[dict]:
+    """List requirements, excluding withdrawn by default."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    results = registry["requirements"]
+    if not include_withdrawn:
+        results = [r for r in results if r.get("status") != "withdrawn"]
+    return results
+
+
+def query_requirements(
+    workspace: str,
+    type: str | None = None,
+    source_block: str | None = None,
+    level: int | None = None,
+    status: str | None = None,
+) -> list[dict]:
+    """Query requirements with filters."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    results = registry["requirements"]
+    if type is not None:
+        results = [r for r in results if r.get("type") == type]
+    if source_block is not None:
+        results = [r for r in results if r.get("source_block") == source_block]
+    if level is not None:
+        results = [r for r in results if r.get("level") == level]
+    if status is not None:
+        results = [r for r in results if r.get("status") == status]
+    return results
+
+
+def update_requirement(workspace: str, req_id: str, **fields) -> None:
+    """Update fields on an existing requirement. Merges into attributes dict."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    idx, req = _find_requirement(registry, req_id)
+
+    for key, value in fields.items():
+        if key == "attributes" and isinstance(value, dict):
+            req.setdefault("attributes", {}).update(value)
+        elif key in req:
+            req[key] = value
+
+    registry["requirements"][idx] = req
+    _save_registry(workspace, registry)
+
+
+def export_requirements(workspace: str) -> dict:
+    """Export full registry as dict."""
+    workspace = _validate_dir_path(workspace)
+    return _load_registry(workspace)
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Manage requirements registry")
+    parser.add_argument("--workspace", required=True, help="Path to .requirements-dev/ directory")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    # add
+    sp = subparsers.add_parser("add")
+    sp.add_argument("--statement", required=True)
+    sp.add_argument("--type", required=True, choices=sorted(VALID_TYPES))
+    sp.add_argument("--priority", required=True, choices=sorted(VALID_PRIORITIES))
+    sp.add_argument("--source-block", required=True)
+    sp.add_argument("--level", type=int, default=0)
+
+    # register
+    sp = subparsers.add_parser("register")
+    sp.add_argument("--id", required=True)
+    sp.add_argument("--parent-need", required=True)
+
+    # baseline
+    sp = subparsers.add_parser("baseline")
+    sp.add_argument("--id", required=True)
+
+    # withdraw
+    sp = subparsers.add_parser("withdraw")
+    sp.add_argument("--id", required=True)
+    sp.add_argument("--rationale", required=True)
+
+    # list
+    sp = subparsers.add_parser("list")
+    sp.add_argument("--include-withdrawn", action="store_true")
+
+    # query
+    sp = subparsers.add_parser("query")
+    sp.add_argument("--type", default=None, choices=sorted(VALID_TYPES))
+    sp.add_argument("--source-block", default=None)
+    sp.add_argument("--level", type=int, default=None)
+    sp.add_argument("--status", default=None)
+
+    # export
+    subparsers.add_parser("export")
+
+    args = parser.parse_args()
+
+    if args.command == "add":
+        req_id = add_requirement(
+            args.workspace, args.statement, args.type, args.priority,
+            args.source_block, args.level,
+        )
+        print(json.dumps({"id": req_id}))
+    elif args.command == "register":
+        register_requirement(args.workspace, args.id, args.parent_need)
+        print(json.dumps({"registered": args.id}))
+    elif args.command == "baseline":
+        baseline_requirement(args.workspace, args.id)
+        print(json.dumps({"baselined": args.id}))
+    elif args.command == "withdraw":
+        withdraw_requirement(args.workspace, args.id, args.rationale)
+        print(json.dumps({"withdrawn": args.id}))
+    elif args.command == "list":
+        result = list_requirements(args.workspace, args.include_withdrawn)
+        print(json.dumps(result, indent=2))
+    elif args.command == "query":
+        result = query_requirements(args.workspace, args.type, args.source_block, args.level, args.status)
+        print(json.dumps(result, indent=2))
+    elif args.command == "export":
+        result = export_requirements(args.workspace)
+        print(json.dumps(result, indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/scripts/source_tracker.py b/skills/requirements-dev/scripts/source_tracker.py
index 0c48288..a8c12aa 100644
--- a/skills/requirements-dev/scripts/source_tracker.py
+++ b/skills/requirements-dev/scripts/source_tracker.py
@@ -1 +1,138 @@
-"""Source registry management adapted from concept-dev."""
+#!/usr/bin/env python3
+"""Source registry management adapted from concept-dev.
+
+Usage:
+    python3 source_tracker.py --workspace <path> add --title "..." --url "..." --type research
+    python3 source_tracker.py --workspace <path> list
+    python3 source_tracker.py --workspace <path> export
+
+Manages source references used during requirements development.
+"""
+import argparse
+import json
+import os
+from dataclasses import asdict, dataclass, field
+from datetime import datetime, timezone
+
+from shared_io import _atomic_write, _validate_dir_path
+
+REGISTRY_FILENAME = "source_registry.json"
+SCHEMA_VERSION = "1.0.0"
+
+
+@dataclass
+class Source:
+    id: str
+    title: str
+    url: str
+    type: str  # research, standard, stakeholder, concept_dev
+    research_context: str = ""
+    concept_dev_ref: str = ""
+    metadata: dict = field(default_factory=dict)
+    registered_at: str = ""
+
+
+def _load_registry(workspace: str) -> dict:
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    if os.path.isfile(path):
+        with open(path) as f:
+            return json.load(f)
+    return {"schema_version": SCHEMA_VERSION, "sources": []}
+
+
+def _save_registry(workspace: str, registry: dict) -> None:
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    _atomic_write(path, registry)
+
+
+def _next_id(registry: dict) -> str:
+    existing = registry.get("sources", [])
+    if not existing:
+        return "SRC-001"
+    max_num = 0
+    for src in existing:
+        try:
+            num = int(src["id"].split("-")[1])
+            if num > max_num:
+                max_num = num
+        except (IndexError, ValueError):
+            continue
+    return f"SRC-{max_num + 1:03d}"
+
+
+def add_source(
+    workspace: str,
+    title: str,
+    url: str,
+    type: str,
+    research_context: str = "",
+    concept_dev_ref: str = "",
+) -> str:
+    """Add a source to the registry. Returns the assigned ID."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    src = Source(
+        id=_next_id(registry),
+        title=title,
+        url=url,
+        type=type,
+        research_context=research_context,
+        concept_dev_ref=concept_dev_ref,
+        registered_at=datetime.now(timezone.utc).isoformat(),
+    )
+    registry["sources"].append(asdict(src))
+    _save_registry(workspace, registry)
+    return src.id
+
+
+def list_sources(workspace: str) -> list[dict]:
+    """List all sources."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    return registry["sources"]
+
+
+def export_sources(workspace: str) -> dict:
+    """Export full registry as dict."""
+    workspace = _validate_dir_path(workspace)
+    return _load_registry(workspace)
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Manage source registry")
+    parser.add_argument("--workspace", required=True, help="Path to .requirements-dev/ directory")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    # add
+    sp = subparsers.add_parser("add")
+    sp.add_argument("--title", required=True)
+    sp.add_argument("--url", required=True)
+    sp.add_argument("--type", required=True)
+    sp.add_argument("--research-context", default="")
+    sp.add_argument("--concept-dev-ref", default="")
+
+    # list
+    subparsers.add_parser("list")
+
+    # export
+    subparsers.add_parser("export")
+
+    args = parser.parse_args()
+
+    if args.command == "add":
+        src_id = add_source(
+            args.workspace, args.title, args.url, args.type,
+            args.research_context, args.concept_dev_ref,
+        )
+        print(json.dumps({"id": src_id}))
+    elif args.command == "list":
+        result = list_sources(args.workspace)
+        print(json.dumps(result, indent=2))
+    elif args.command == "export":
+        result = export_sources(args.workspace)
+        print(json.dumps(result, indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/scripts/traceability.py b/skills/requirements-dev/scripts/traceability.py
index fd03938..5724b3e 100644
--- a/skills/requirements-dev/scripts/traceability.py
+++ b/skills/requirements-dev/scripts/traceability.py
@@ -1 +1,224 @@
-"""Bidirectional traceability link management."""
+#!/usr/bin/env python3
+"""Bidirectional traceability link management.
+
+Usage:
+    python3 traceability.py --workspace <path> link --source REQ-001 --target NEED-001 --type derives_from --role requirement
+    python3 traceability.py --workspace <path> query --entity REQ-001 --direction both
+    python3 traceability.py --workspace <path> coverage
+    python3 traceability.py --workspace <path> orphans
+
+All mutations use atomic write (temp-file-then-rename).
+"""
+import argparse
+import json
+import os
+from datetime import datetime, timezone
+
+from shared_io import _atomic_write, _validate_dir_path
+
+REGISTRY_FILENAME = "traceability_registry.json"
+SCHEMA_VERSION = "1.0.0"
+
+VALID_LINK_TYPES = {
+    "derives_from", "verified_by", "sources", "informed_by",
+    "allocated_to", "parent_of", "conflicts_with",
+}
+
+# Maps ID prefixes to their registry files and list keys
+_ID_REGISTRY_MAP = {
+    "REQ": ("requirements_registry.json", "requirements"),
+    "NEED": ("needs_registry.json", "needs"),
+    "SRC": ("source_registry.json", "sources"),
+    "ASN": ("assumption_registry.json", "assumptions"),
+}
+
+
+def _load_registry(workspace: str) -> dict:
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    if os.path.isfile(path):
+        with open(path) as f:
+            return json.load(f)
+    return {"schema_version": SCHEMA_VERSION, "links": []}
+
+
+def _save_registry(workspace: str, registry: dict) -> None:
+    path = os.path.join(workspace, REGISTRY_FILENAME)
+    _atomic_write(path, registry)
+
+
+def _entity_exists(workspace: str, entity_id: str) -> bool:
+    """Check if an entity ID exists in its corresponding registry."""
+    prefix = entity_id.split("-")[0]
+    entry = _ID_REGISTRY_MAP.get(prefix)
+    if entry is None:
+        return False
+    filename, list_key = entry
+    path = os.path.join(workspace, filename)
+    if not os.path.isfile(path):
+        return False
+    with open(path) as f:
+        data = json.load(f)
+    return any(item["id"] == entity_id for item in data.get(list_key, []))
+
+
+def link(workspace: str, source_id: str, target_id: str, link_type: str, role: str) -> None:
+    """Create a traceability link with referential integrity validation."""
+    workspace = _validate_dir_path(workspace)
+
+    if not _entity_exists(workspace, source_id):
+        raise ValueError(f"Source entity not found: {source_id}")
+    if not _entity_exists(workspace, target_id):
+        raise ValueError(f"Target entity not found: {target_id}")
+
+    registry = _load_registry(workspace)
+    link_entry = {
+        "source": source_id,
+        "target": target_id,
+        "type": link_type,
+        "role": role,
+        "created_at": datetime.now(timezone.utc).isoformat(),
+    }
+    if link_type == "conflicts_with":
+        link_entry["resolution_status"] = "open"
+        link_entry["rationale"] = None
+
+    registry["links"].append(link_entry)
+    _save_registry(workspace, registry)
+
+
+def query(workspace: str, entity_id: str, direction: str = "both") -> list[dict]:
+    """Find all links for an entity."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+    results = []
+    for lnk in registry["links"]:
+        if direction in ("forward", "both") and lnk["source"] == entity_id:
+            results.append(lnk)
+        elif direction in ("backward", "both") and lnk["target"] == entity_id:
+            results.append(lnk)
+    return results
+
+
+def coverage_report(workspace: str) -> dict:
+    """Compute traceability coverage: percentage of needs with requirements."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+
+    # Load needs
+    needs_path = os.path.join(workspace, "needs_registry.json")
+    if not os.path.isfile(needs_path):
+        return {"needs_covered": 0, "needs_total": 0, "coverage_pct": 0.0, "requirements_with_vv": 0}
+    with open(needs_path) as f:
+        needs_data = json.load(f)
+    approved_needs = [n for n in needs_data.get("needs", []) if n.get("status") == "approved"]
+
+    # Load requirements to check withdrawn status
+    reqs_path = os.path.join(workspace, "requirements_registry.json")
+    withdrawn_reqs = set()
+    if os.path.isfile(reqs_path):
+        with open(reqs_path) as f:
+            reqs_data = json.load(f)
+        withdrawn_reqs = {r["id"] for r in reqs_data.get("requirements", []) if r.get("status") == "withdrawn"}
+
+    # Find needs covered by non-withdrawn requirements
+    covered_needs = set()
+    vv_reqs = set()
+    for lnk in registry["links"]:
+        if lnk["type"] == "derives_from" and lnk["source"] not in withdrawn_reqs:
+            covered_needs.add(lnk["target"])
+        if lnk["type"] == "verified_by":
+            vv_reqs.add(lnk["source"])
+
+    need_ids = {n["id"] for n in approved_needs}
+    covered = len(covered_needs & need_ids)
+    total = len(need_ids)
+    pct = (covered / total * 100.0) if total > 0 else 0.0
+
+    return {
+        "needs_covered": covered,
+        "needs_total": total,
+        "coverage_pct": pct,
+        "requirements_with_vv": len(vv_reqs),
+    }
+
+
+def orphan_check(workspace: str) -> dict:
+    """Find needs with no requirements and requirements with no parent needs."""
+    workspace = _validate_dir_path(workspace)
+    registry = _load_registry(workspace)
+
+    # Load needs
+    needs_path = os.path.join(workspace, "needs_registry.json")
+    need_ids = set()
+    if os.path.isfile(needs_path):
+        with open(needs_path) as f:
+            needs_data = json.load(f)
+        need_ids = {n["id"] for n in needs_data.get("needs", []) if n.get("status") == "approved"}
+
+    # Load requirements
+    reqs_path = os.path.join(workspace, "requirements_registry.json")
+    req_ids = set()
+    if os.path.isfile(reqs_path):
+        with open(reqs_path) as f:
+            reqs_data = json.load(f)
+        req_ids = {r["id"] for r in reqs_data.get("requirements", []) if r.get("status") != "withdrawn"}
+
+    # Find covered needs and linked requirements via derives_from
+    covered_needs = set()
+    linked_reqs = set()
+    for lnk in registry["links"]:
+        if lnk["type"] == "derives_from":
+            covered_needs.add(lnk["target"])
+            linked_reqs.add(lnk["source"])
+
+    orphan_needs = sorted(need_ids - covered_needs)
+    orphan_requirements = sorted(req_ids - linked_reqs)
+
+    return {
+        "orphan_needs": orphan_needs,
+        "orphan_requirements": orphan_requirements,
+    }
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="Manage traceability links")
+    parser.add_argument("--workspace", required=True, help="Path to .requirements-dev/ directory")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    # link
+    sp = subparsers.add_parser("link")
+    sp.add_argument("--source", required=True)
+    sp.add_argument("--target", required=True)
+    sp.add_argument("--type", required=True)
+    sp.add_argument("--role", required=True)
+
+    # query
+    sp = subparsers.add_parser("query")
+    sp.add_argument("--entity", required=True)
+    sp.add_argument("--direction", default="both", choices=["forward", "backward", "both"])
+
+    # coverage
+    subparsers.add_parser("coverage")
+
+    # orphans
+    subparsers.add_parser("orphans")
+
+    args = parser.parse_args()
+
+    if args.command == "link":
+        link(args.workspace, args.source, args.target, args.type, args.role)
+        print(json.dumps({"linked": f"{args.source} -> {args.target}"}))
+    elif args.command == "query":
+        result = query(args.workspace, args.entity, args.direction)
+        print(json.dumps(result, indent=2))
+    elif args.command == "coverage":
+        result = coverage_report(args.workspace)
+        print(json.dumps(result, indent=2))
+    elif args.command == "orphans":
+        result = orphan_check(args.workspace)
+        print(json.dumps(result, indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/test_requirement_tracker.py b/skills/requirements-dev/tests/test_requirement_tracker.py
new file mode 100644
index 0000000..d26dab8
--- /dev/null
+++ b/skills/requirements-dev/tests/test_requirement_tracker.py
@@ -0,0 +1,175 @@
+"""Tests for requirement_tracker.py."""
+import json
+
+import pytest
+
+from requirement_tracker import (
+    add_requirement,
+    baseline_requirement,
+    export_requirements,
+    list_requirements,
+    query_requirements,
+    register_requirement,
+    update_requirement,
+    withdraw_requirement,
+)
+
+VALID_TYPES = ["functional", "performance", "interface", "constraint", "quality"]
+VALID_PRIORITIES = ["high", "medium", "low"]
+
+
+def _add_need(ws, need_id="NEED-001", statement="The operator needs monitoring"):
+    """Helper to seed a need in needs_registry.json."""
+    reg = {"schema_version": "1.0.0", "needs": [
+        {"id": need_id, "statement": statement, "stakeholder": "Operator",
+         "source_block": "monitoring", "status": "approved", "rationale": None}
+    ]}
+    (ws / "needs_registry.json").write_text(json.dumps(reg))
+
+
+def test_add_creates_req_with_correct_fields(tmp_workspace):
+    req_id = add_requirement(
+        str(tmp_workspace), "The API shall respond within 200ms",
+        type="performance", priority="high", source_block="api-gateway",
+    )
+    assert req_id == "REQ-001"
+    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
+    req = reg["requirements"][0]
+    assert req["statement"] == "The API shall respond within 200ms"
+    assert req["type"] == "performance"
+    assert req["priority"] == "high"
+    assert req["status"] == "draft"
+
+
+def test_add_auto_increments_id(tmp_workspace):
+    id1 = add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
+    id2 = add_requirement(str(tmp_workspace), "Req 2", type="functional", priority="high", source_block="blk")
+    id3 = add_requirement(str(tmp_workspace), "Req 3", type="functional", priority="high", source_block="blk")
+    assert id1 == "REQ-001"
+    assert id2 == "REQ-002"
+    assert id3 == "REQ-003"
+
+
+def test_add_validates_type(tmp_workspace):
+    with pytest.raises(ValueError, match="type"):
+        add_requirement(str(tmp_workspace), "Req", type="invalid", priority="high", source_block="blk")
+
+
+def test_add_validates_priority(tmp_workspace):
+    with pytest.raises(ValueError, match="priority"):
+        add_requirement(str(tmp_workspace), "Req", type="functional", priority="critical", source_block="blk")
+
+
+def test_register_transitions_to_registered(tmp_workspace):
+    _add_need(tmp_workspace)
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
+    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
+    assert reg["requirements"][0]["status"] == "registered"
+    assert reg["requirements"][0]["parent_need"] == "NEED-001"
+
+
+def test_register_requires_parent_need(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    with pytest.raises(ValueError, match="parent_need"):
+        register_requirement(str(tmp_workspace), "REQ-001", parent_need="")
+
+
+def test_baseline_transitions_from_registered(tmp_workspace):
+    _add_need(tmp_workspace)
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
+    baseline_requirement(str(tmp_workspace), "REQ-001")
+    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
+    assert reg["requirements"][0]["status"] == "baselined"
+
+
+def test_baseline_on_non_registered_raises_error(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    with pytest.raises(ValueError, match="registered"):
+        baseline_requirement(str(tmp_workspace), "REQ-001")
+
+
+def test_withdraw_sets_status_with_rationale(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Superseded")
+    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
+    assert reg["requirements"][0]["status"] == "withdrawn"
+    assert reg["requirements"][0]["rationale"] == "Superseded"
+
+
+def test_withdraw_without_rationale_raises_error(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    with pytest.raises(ValueError, match="rationale"):
+        withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="")
+
+
+def test_withdraw_preserves_requirement(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Obsolete")
+    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
+    assert len(reg["requirements"]) == 1  # not deleted
+
+
+def test_list_excludes_withdrawn_by_default(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
+    add_requirement(str(tmp_workspace), "Req 2", type="functional", priority="high", source_block="blk")
+    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Gone")
+    result = list_requirements(str(tmp_workspace))
+    assert len(result) == 1
+    assert result[0]["id"] == "REQ-002"
+
+
+def test_list_with_include_withdrawn(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
+    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Gone")
+    result = list_requirements(str(tmp_workspace), include_withdrawn=True)
+    assert len(result) == 1
+    assert result[0]["status"] == "withdrawn"
+
+
+def test_query_by_type(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Perf req", type="performance", priority="high", source_block="blk")
+    add_requirement(str(tmp_workspace), "Func req", type="functional", priority="high", source_block="blk")
+    result = query_requirements(str(tmp_workspace), type="performance")
+    assert len(result) == 1
+    assert result[0]["type"] == "performance"
+
+
+def test_query_by_source_block(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="api")
+    add_requirement(str(tmp_workspace), "Req 2", type="functional", priority="high", source_block="db")
+    result = query_requirements(str(tmp_workspace), source_block="api")
+    assert len(result) == 1
+    assert result[0]["source_block"] == "api"
+
+
+def test_query_by_level(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Sys req", type="functional", priority="high", source_block="blk")
+    add_requirement(str(tmp_workspace), "Sub req", type="functional", priority="high", source_block="blk", level=1)
+    result = query_requirements(str(tmp_workspace), level=0)
+    assert len(result) == 1
+
+
+def test_update_modifies_attributes(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    update_requirement(str(tmp_workspace), "REQ-001", attributes={"A6_verification_method": "system test"})
+    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
+    assert reg["requirements"][0]["attributes"]["A6_verification_method"] == "system test"
+
+
+def test_export_produces_correct_structure(tmp_workspace):
+    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
+    result = export_requirements(str(tmp_workspace))
+    assert "schema_version" in result
+    assert "requirements" in result
+    assert len(result["requirements"]) == 1
+
+
+def test_sync_counts_updates_state(tmp_workspace):
+    _add_need(tmp_workspace)
+    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
+    register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
+    state = json.loads((tmp_workspace / "state.json").read_text())
+    assert state["counts"]["requirements_total"] == 1
+    assert state["counts"]["requirements_registered"] == 1
diff --git a/skills/requirements-dev/tests/test_traceability.py b/skills/requirements-dev/tests/test_traceability.py
new file mode 100644
index 0000000..8a1f00d
--- /dev/null
+++ b/skills/requirements-dev/tests/test_traceability.py
@@ -0,0 +1,160 @@
+"""Tests for traceability.py."""
+import json
+
+import pytest
+
+from traceability import coverage_report, link, orphan_check, query
+
+
+def _seed_registries(ws, needs=None, reqs=None):
+    """Seed needs and requirements registries."""
+    if needs is None:
+        needs = [
+            {"id": "NEED-001", "statement": "Need 1", "stakeholder": "Op", "status": "approved"},
+            {"id": "NEED-002", "statement": "Need 2", "stakeholder": "Op", "status": "approved"},
+        ]
+    if reqs is None:
+        reqs = [
+            {"id": "REQ-001", "statement": "Req 1", "type": "functional", "status": "registered",
+             "parent_need": "NEED-001", "source_block": "blk"},
+            {"id": "REQ-002", "statement": "Req 2", "type": "functional", "status": "registered",
+             "parent_need": "NEED-002", "source_block": "blk"},
+        ]
+    (ws / "needs_registry.json").write_text(json.dumps({"schema_version": "1.0.0", "needs": needs}))
+    (ws / "requirements_registry.json").write_text(json.dumps({"schema_version": "1.0.0", "requirements": reqs}))
+    # Ensure traceability registry exists
+    if not (ws / "traceability_registry.json").exists():
+        (ws / "traceability_registry.json").write_text(json.dumps({"schema_version": "1.0.0", "links": []}))
+
+
+# --- Link creation ---
+
+def test_link_creates_valid_link(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    reg = json.loads((tmp_workspace / "traceability_registry.json").read_text())
+    assert len(reg["links"]) == 1
+    assert reg["links"][0]["source"] == "REQ-001"
+    assert reg["links"][0]["target"] == "NEED-001"
+    assert reg["links"][0]["type"] == "derives_from"
+
+
+def test_link_validates_source_exists(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    with pytest.raises(ValueError, match="not found"):
+        link(str(tmp_workspace), "REQ-999", "NEED-001", "derives_from", "requirement")
+
+
+def test_link_validates_target_exists(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    with pytest.raises(ValueError, match="not found"):
+        link(str(tmp_workspace), "REQ-001", "NEED-999", "derives_from", "requirement")
+
+
+def test_link_conflicts_with_has_resolution(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "REQ-002", "conflicts_with", "conflict")
+    reg = json.loads((tmp_workspace / "traceability_registry.json").read_text())
+    lnk = reg["links"][0]
+    assert lnk["type"] == "conflicts_with"
+    assert lnk["resolution_status"] == "open"
+
+
+# --- Query ---
+
+def test_query_forward(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    result = query(str(tmp_workspace), "REQ-001", "forward")
+    assert len(result) == 1
+    assert result[0]["target"] == "NEED-001"
+
+
+def test_query_backward(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    result = query(str(tmp_workspace), "NEED-001", "backward")
+    assert len(result) == 1
+    assert result[0]["source"] == "REQ-001"
+
+
+def test_query_both(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    link(str(tmp_workspace), "REQ-002", "REQ-001", "parent_of", "hierarchy")
+    result = query(str(tmp_workspace), "REQ-001", "both")
+    assert len(result) == 2
+
+
+def test_query_no_links(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    result = query(str(tmp_workspace), "REQ-001", "both")
+    assert result == []
+
+
+# --- Coverage ---
+
+def test_coverage_full(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    link(str(tmp_workspace), "REQ-002", "NEED-002", "derives_from", "requirement")
+    report = coverage_report(str(tmp_workspace))
+    assert report["coverage_pct"] == 100.0
+    assert report["needs_covered"] == 2
+
+
+def test_coverage_partial(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    report = coverage_report(str(tmp_workspace))
+    assert report["coverage_pct"] == 50.0
+    assert report["needs_covered"] == 1
+    assert report["needs_total"] == 2
+
+
+def test_coverage_excludes_withdrawn(tmp_workspace):
+    reqs = [
+        {"id": "REQ-001", "statement": "Req 1", "type": "functional", "status": "withdrawn",
+         "parent_need": "NEED-001", "source_block": "blk"},
+    ]
+    _seed_registries(tmp_workspace, reqs=reqs)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    report = coverage_report(str(tmp_workspace))
+    # Withdrawn requirement doesn't count for coverage
+    assert report["needs_covered"] == 0
+
+
+# --- Orphan detection ---
+
+def test_orphan_finds_uncovered_needs(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    # NEED-002 has no requirement
+    result = orphan_check(str(tmp_workspace))
+    assert "NEED-002" in result["orphan_needs"]
+
+
+def test_orphan_finds_unlinked_requirements(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    # REQ-001 has no derives_from link
+    result = orphan_check(str(tmp_workspace))
+    assert "REQ-001" in result["orphan_requirements"]
+    assert "REQ-002" in result["orphan_requirements"]
+
+
+def test_orphan_empty_when_all_linked(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    link(str(tmp_workspace), "REQ-002", "NEED-002", "derives_from", "requirement")
+    result = orphan_check(str(tmp_workspace))
+    assert result["orphan_needs"] == []
+    assert result["orphan_requirements"] == []
+
+
+# --- Schema ---
+
+def test_schema_version_present(tmp_workspace):
+    _seed_registries(tmp_workspace)
+    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
+    reg = json.loads((tmp_workspace / "traceability_registry.json").read_text())
+    assert reg["schema_version"] == "1.0.0"
