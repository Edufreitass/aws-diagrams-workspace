# validate_drawio.py

import argparse
import base64
import json
import pathlib
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from collections import Counter


def parse_arguments():
    parser = argparse.ArgumentParser(description="Validate draw.io XML structure and AWS diagram conventions")
    parser.add_argument("diagram", type=pathlib.Path)
    parser.add_argument("--page", help="Validate only a zero-based page index or exact page name")
    parser.add_argument("--strict-mx", action="store_true", help="Treat non-AWS generic vertices as errors")
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser.parse_args()


def decode_diagram(diagram):
    model = diagram.find("mxGraphModel")
    if model is not None:
        return model
    payload = (diagram.text or "").strip()
    if not payload:
        raise ValueError("Diagram has no mxGraphModel or compressed payload")
    compressed = base64.b64decode(payload)
    encoded_xml = zlib.decompress(compressed, -15).decode("utf-8")
    return ET.fromstring(urllib.parse.unquote(encoded_xml))


def load_model(path):
    document = ET.parse(path).getroot()
    if document.tag == "mxGraphModel":
        return "bare-mxGraphModel", [("Diagram 1", document)]
    if document.tag == "diagram":
        return "diagram", [(document.get("name", "Diagram 1"), decode_diagram(document))]
    if document.tag == "mxfile":
        if not document:
            raise ValueError("mxfile contains no diagram")
        return "mxfile", [(diagram.get("name", f"Diagram {index + 1}"), decode_diagram(diagram)) for index, diagram in enumerate(document)]
    raise ValueError(f"Unsupported root element: {document.tag}")


def select_models(models, selector):
    if selector is None:
        return models
    if selector.isdigit():
        index = int(selector)
        if index >= len(models):
            raise ValueError(f"Page index {index} is out of range for {len(models)} pages")
        return [models[index]]
    selected = [model for model in models if model[0] == selector]
    if not selected:
        raise ValueError(f"Page not found: {selector}")
    return selected


def compact_label(value):
    if not value:
        return "<unlabeled>"
    text = value.replace("<br/>", " ").replace("<br>", " ")
    return text[:100] + ("..." if len(text) > 100 else "")


def style_property(style, name):
    prefix = f"{name}="
    for item in style.split(";"):
        if item.startswith(prefix):
            return item[len(prefix):]
    return None


def numeric_value(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_model(name, model, strict_mx):
    graph_root = model.find("root")
    errors = []
    warnings = []

    if graph_root is None:
        return {
            "name": name,
            "nodes": 0,
            "edges": 0,
            "mx_vertices": 0,
            "generic_vertices": 0,
            "embedded_images": 0,
            "errors": ["mxGraphModel has no root element"],
            "warnings": [],
        }

    elements_with_ids = [item for item in graph_root.iter() if item.get("id")]
    ids = [item.get("id") for item in elements_with_ids]
    known_ids = set(ids)
    duplicates = sorted([identifier for identifier, count in Counter(ids).items() if count > 1])
    if duplicates:
        errors.append(f"Duplicate IDs: " + ", ".join(duplicates))

    cells = list(graph_root.iter("mxCell"))
    vertices = [cell for cell in cells if cell.get("vertex") == "1"]
    edges = [cell for cell in cells if cell.get("edge") == "1"]
    mx_vertices = []
    generic_vertices = []
    embedded_images = []
    aws_generations = set()

    for cell in cells:
        for reference in ("parent", "source", "target"):
            target = cell.get(reference)
            if target and target not in known_ids:
                errors.append(f"Cell {cell.get('id', '<unwrapped>')} has missing {reference} reference {target}")

    for edge in edges:
        if not edge.get("source"):
            warnings.append(f"Edge {edge.get('id', '<unidentified>')} has no source cell")
        if not edge.get("target"):
            warnings.append(f"Edge {edge.get('id', '<unidentified>')} has no target cell")

    for vertex in vertices:
        style = vertex.get("style", "")
        value = vertex.get("value", "")
        label = compact_label(value)

        if "mxgraph.aws" in style:
            mx_vertices.append(vertex)
            aws_generations.add("AWS3")
        elif "mxgraph.aws4" in style:
            mx_vertices.append(vertex)
            aws_generations.add("AWS4")
            if "shape=mxgraph.aws4.resourceIcon" in style and (style_property(style, "fillColor") or "").upper() == "#F78E04":
                warnings.append(f"AWS4 resource icon {vertex.get('id', '<unwrapped>')} uses global orange fill (color=#F78E04)")
        elif "shape=image" in style or "image=data:image" in style:
            embedded_images.append(vertex)
        elif style.startswith("text;") or "strokeColor=none;fillColor=none" in style:
            pass
        elif vertex.get("id") is None:
            pass
        else:
            generic_vertices.append(vertex)
            message = f"Generic vertex {vertex.get('id', '<unwrapped>')} ({label})"
            if strict_mx:
                errors.append(message)
            else:
                warnings.append(message)

        geometry = vertex.find("mxGeometry")
        if geometry is None:
            warnings.append(f"Vertex {vertex.get('id', '<unwrapped>')} has no geometry")
        else:
            width = numeric_value(geometry.get("width"))
            height = numeric_value(geometry.get("height"))
            if width in (None, 0) and height in (None, 0) and len(value) > 120:
                warnings.append(f"Zero-size vertex {vertex.get('id', '<unwrapped>')} carries {len(value)} characters of hidden content")

        if len(value) > 140 and "image=data:image" not in style:
            warnings.append(f"Long vertex label {vertex.get('id', '<unwrapped>')} ({len(value)} characters)")

    if len(aws_generations) > 1:
        warnings.append(f"Mixed AWS icon generations: " + ", ".join(sorted(aws_generations)))

    for edge in edges:
        value = edge.get("value", "")
        if len(value) > 140:
            warnings.append(f"Long edge label {edge.get('id', '<unidentified>')} ({len(value)} characters)")
        stroke_width = numeric_value(style_property(edge.get("style", ""), "strokeWidth"))
        if stroke_width is not None and stroke_width != 1:
            warnings.append(f"Edge {edge.get('id', '<unidentified>')} uses strokeWidth={stroke_width} pt instead of the 1 pt default")

    return {
        "name": name,
        "nodes": len(cells),
        "edges": len(edges),
        "mx_vertices": len(mx_vertices),
        "generic_vertices": len(generic_vertices),
        "embedded_images": len(embedded_images),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def print_test_report(path, document_format, results):
    print(f"File: {path}")
    print(f"Format: {document_format}")
    print(f"Pages validated: {len(results)}\n")

    for index, result in enumerate(results):
        print(f"[{index}] {result['name']}")
        print(f"  Nodes: {result['nodes']} (Vertices: {result['mx_vertices']} AWS, {result['generic_vertices']} generic, {result['embedded_images']} images | Edges: {result['edges']})")
        for warning in result["warnings"]:
            print(f"  WARN: {warning}")
        for error in result["errors"]:
            print(f"  ERROR: {error}")

    error_count = sum(len(result["errors"]) for result in results)
    warning_count = sum(len(result["warnings"]) for result in results)

    status = "FAIL" if error_count else ("PASS WITH WARNINGS" if warning_count else "PASS")
    print(f"\nResult: [{status}] ({error_count} errors, {warning_count} warnings)")


def main():
    arguments = parse_arguments()
    try:
        document_format, models = load_model(arguments.diagram)
        selected_models = select_models(models, arguments.page)
        results = [validate_model(name, model, arguments.strict_mx) for name, model in selected_models]
    except (OSError, ET.ParseError, ValueError, base64.binascii.Error, zlib.error) as error:
        if arguments.json_output:
            json.dump({"file": str(arguments.diagram), "fatal_error": str(error)}, sys.stdout, ensure_ascii=False, indent=2)
        else:
            print(f"FAIL (error): {error}", file=sys.stderr)
        return 1

    if arguments.json_output:
        json.dump(
            {
                "file": str(arguments.diagram),
                "format": document_format,
                "pages": results
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2
        )
        print()
    else:
        print_test_report(arguments.diagram, document_format, results)

    return 1 if any(result["errors"] for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
