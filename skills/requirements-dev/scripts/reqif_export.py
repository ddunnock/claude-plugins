"""ReqIF XML export from JSON registries.

Requires: pip install reqif (strictdoc's reqif package)
Gracefully handles missing package - prints install instructions and exits 0.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile


def _validate_path(path: str, allowed_extensions: list[str]) -> str:
    """Validate path: reject traversal, restrict extensions, return resolved path."""
    if ".." in Path(path).parts:
        print(f"Error: Path contains '..' traversal: {path}", file=sys.stderr)
        sys.exit(1)
    resolved = os.path.realpath(path)
    ext = os.path.splitext(resolved)[1].lower()
    if ext not in allowed_extensions:
        print(f"Error: Extension '{ext}' not in {allowed_extensions}", file=sys.stderr)
        sys.exit(1)
    return resolved


def _atomic_write_text(filepath: str, content: str) -> None:
    """Write text atomically using temp-file-then-rename."""
    target_dir = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(target_dir, exist_ok=True)
    fd = NamedTemporaryFile(mode="w", dir=target_dir, suffix=".tmp", delete=False)
    try:
        fd.write(content)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.rename(fd.name, filepath)
    except Exception:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def export_reqif(requirements_path: str, needs_path: str,
                 traceability_path: str, output_path: str) -> None:
    """Generate ReqIF XML from JSON registries.

    Uses the reqif package (strictdoc) for model construction and unparsing.
    If the reqif package is not installed, prints a user-friendly install message
    and returns without creating the output file.
    """
    try:
        from reqif.models.reqif_core_content import ReqIFCoreContent
        from reqif.models.reqif_namespace_info import ReqIFNamespaceInfo
        from reqif.models.reqif_req_if_content import ReqIFReqIFContent
        from reqif.models.reqif_reqif_header import ReqIFReqIFHeader
        from reqif.models.reqif_spec_hierarchy import ReqIFSpecHierarchy
        from reqif.models.reqif_spec_object import ReqIFSpecObject, SpecObjectAttribute
        from reqif.models.reqif_spec_object_type import ReqIFSpecObjectType, SpecAttributeDefinition
        from reqif.models.reqif_spec_relation import ReqIFSpecRelation
        from reqif.models.reqif_spec_relation_type import ReqIFSpecRelationType
        from reqif.models.reqif_specification import ReqIFSpecification
        from reqif.models.reqif_types import SpecObjectAttributeType
        from reqif.object_lookup import ReqIFObjectLookup
        from reqif.reqif_bundle import ReqIFBundle
        from reqif.unparser import ReqIFUnparser
    except ImportError:
        print("ReqIF export requires the 'reqif' package.")
        print("Install with: pip install reqif")
        print("ReqIF export skipped. Other deliverables are unaffected.")
        return

    # Load registries
    with open(requirements_path) as f:
        req_data = json.load(f)
    with open(needs_path) as f:
        needs_data = json.load(f)
    with open(traceability_path) as f:
        trace_data = json.load(f)

    requirements = req_data.get("requirements", [])
    links = trace_data.get("links", [])
    now = datetime.now(timezone.utc).isoformat()

    # Build SPEC-TYPEs - one per requirement type
    req_types = {"functional", "performance", "interface", "constraint", "quality"}
    spec_object_types = []
    type_id_map = {}

    # Common attribute definitions for all types
    def _make_attr_defs(type_name):
        return [
            SpecAttributeDefinition(
                attribute_type=SpecObjectAttributeType.STRING,
                identifier=f"AD-{type_name}-statement",
                datatype_definition="DT-STRING",
                long_name="Statement",
            ),
            SpecAttributeDefinition(
                attribute_type=SpecObjectAttributeType.STRING,
                identifier=f"AD-{type_name}-priority",
                datatype_definition="DT-STRING",
                long_name="Priority",
            ),
            SpecAttributeDefinition(
                attribute_type=SpecObjectAttributeType.STRING,
                identifier=f"AD-{type_name}-status",
                datatype_definition="DT-STRING",
                long_name="Status",
            ),
            SpecAttributeDefinition(
                attribute_type=SpecObjectAttributeType.STRING,
                identifier=f"AD-{type_name}-parent-need",
                datatype_definition="DT-STRING",
                long_name="Parent Need",
            ),
        ]

    for rtype in sorted(req_types):
        type_id = f"SPEC-TYPE-{rtype.upper()}"
        type_id_map[rtype] = type_id
        spec_object_types.append(
            ReqIFSpecObjectType(
                identifier=type_id,
                long_name=f"{rtype.capitalize()} Requirement",
                attribute_definitions=_make_attr_defs(rtype),
            )
        )

    # Relation type
    relation_type = ReqIFSpecRelationType(
        identifier="REL-TYPE-TRACE",
        long_name="Traceability Link",
    )

    # Build SPEC-OBJECTs from requirements
    spec_objects = []
    hierarchy_children = []
    for req in requirements:
        rtype = req.get("type", "functional")
        spec_type_id = type_id_map.get(rtype, type_id_map["functional"])
        obj_id = f"SO-{req['id']}"

        attrs = [
            SpecObjectAttribute(
                attribute_type=SpecObjectAttributeType.STRING,
                definition_ref=f"AD-{rtype}-statement",
                value=req.get("statement", ""),
            ),
            SpecObjectAttribute(
                attribute_type=SpecObjectAttributeType.STRING,
                definition_ref=f"AD-{rtype}-priority",
                value=req.get("priority", ""),
            ),
            SpecObjectAttribute(
                attribute_type=SpecObjectAttributeType.STRING,
                definition_ref=f"AD-{rtype}-status",
                value=req.get("status", ""),
            ),
            SpecObjectAttribute(
                attribute_type=SpecObjectAttributeType.STRING,
                definition_ref=f"AD-{rtype}-parent-need",
                value=req.get("parent_need", ""),
            ),
        ]

        spec_objects.append(
            ReqIFSpecObject(
                identifier=obj_id,
                attributes=attrs,
                spec_object_type=spec_type_id,
                long_name=req["id"],
            )
        )

        hierarchy_children.append(
            ReqIFSpecHierarchy(
                xml_node=None,
                identifier=f"SH-{req['id']}",
                last_change=now,
                long_name=req["id"],
                spec_object=obj_id,
                children=[],
                ref_then_children_order=True,
                level=1,
            )
        )

    # Build SPEC-OBJECTs for needs (so SPEC-RELATIONs can reference them)
    needs = needs_data.get("needs", [])
    need_type_id = "SPEC-TYPE-NEED"
    spec_object_types.append(
        ReqIFSpecObjectType(
            identifier=need_type_id,
            long_name="Stakeholder Need",
        )
    )
    for need in needs:
        obj_id = f"SO-{need['id']}"
        spec_objects.append(
            ReqIFSpecObject(
                identifier=obj_id,
                attributes=[
                    SpecObjectAttribute(
                        attribute_type=SpecObjectAttributeType.STRING,
                        definition_ref="AD-need-statement",
                        value=need.get("statement", ""),
                    ),
                ],
                spec_object_type=need_type_id,
                long_name=need["id"],
            )
        )

    # Build SPEC-RELATIONs from traceability links
    spec_relations = []
    for i, link_entry in enumerate(links):
        source_id = f"SO-{link_entry['source']}"
        target_id = f"SO-{link_entry['target']}"
        spec_relations.append(
            ReqIFSpecRelation(
                identifier=f"SR-{i:04d}",
                relation_type_ref="REL-TYPE-TRACE",
                source=source_id,
                target=target_id,
                long_name=link_entry.get("type", "derives_from"),
            )
        )

    # Build specification (top-level container)
    specification = ReqIFSpecification(
        identifier="SPEC-001",
        long_name="Requirements Specification",
        children=hierarchy_children,
    )

    # Assemble content
    content = ReqIFReqIFContent(
        spec_types=[*spec_object_types, relation_type],
        spec_objects=spec_objects,
        spec_relations=spec_relations,
        specifications=[specification],
    )

    core_content = ReqIFCoreContent(req_if_content=content)

    header = ReqIFReqIFHeader(
        identifier="HEADER-001",
        creation_time=now,
        req_if_tool_id="requirements-dev",
        req_if_version="1.0",
        source_tool_id="requirements-dev-plugin",
        title="Requirements Export",
    )

    namespace_info = ReqIFNamespaceInfo(
        original_reqif_tag_dump=None,
        doctype_is_present=False,
        encoding="UTF-8",
        namespace="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd",
        configuration=None,
        namespace_id=None,
        namespace_xhtml=None,
        schema_namespace=None,
        schema_location=None,
        language=None,
    )

    # Build lookup dictionaries
    spec_types_lookup = {st.identifier: st for st in [*spec_object_types, relation_type]}
    spec_objects_lookup = {so.identifier: so for so in spec_objects}
    # Parent lookup: map each spec object to its parent relation sources
    spec_relations_parent_lookup = {}
    for sr in spec_relations:
        spec_relations_parent_lookup.setdefault(sr.target, []).append(sr.source)

    lookup = ReqIFObjectLookup(
        data_types_lookup={},
        spec_types_lookup=spec_types_lookup,
        spec_objects_lookup=spec_objects_lookup,
        spec_relations_parent_lookup=spec_relations_parent_lookup,
    )

    bundle = ReqIFBundle(
        namespace_info=namespace_info,
        req_if_header=header,
        core_content=core_content,
        tool_extensions_tag_exists=False,
        lookup=lookup,
        exceptions=[],
    )

    xml_output = ReqIFUnparser.unparse(bundle)

    _atomic_write_text(output_path, xml_output)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Export requirements to ReqIF XML")
    parser.add_argument("--requirements", required=True, help="Path to requirements_registry.json")
    parser.add_argument("--needs", required=True, help="Path to needs_registry.json")
    parser.add_argument("--traceability", required=True, help="Path to traceability_registry.json")
    parser.add_argument("--output", required=True, help="Path for output .reqif file")

    args = parser.parse_args()

    req_path = _validate_path(args.requirements, [".json"])
    needs_path = _validate_path(args.needs, [".json"])
    trace_path = _validate_path(args.traceability, [".json"])

    output_path = _validate_path(args.output, [".reqif"])
    export_reqif(req_path, needs_path, trace_path, output_path)


if __name__ == "__main__":
    main()
