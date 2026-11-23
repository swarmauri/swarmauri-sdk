"""
unparser.py - YAML unparser for Cayaml (Swarmauri's Canon YAML)

This module traverses the AST (constructed using ast_nodes.py) and
reconstructs a YAML-formatted string.

It provides two internal dump functions:
  - _internal_dump_plain(node, indent=0): Emits plain YAML.
  - _internal_dump_round_trip(node, indent=0): Emits YAML preserving
    document markers, comments, anchors/tags, block styles, merge
    operators, and key order.

If the input to dumps() is a plain Python structure (list, dict, or scalar),
we convert it to an AST before emitting YAML.
"""

from .ast_nodes import (
    DocumentNode,
    MappingNode,
    SequenceNode,
    ScalarNode,
    Node,
)
from .scalars import parse_yaml_float, parse_yaml_int
from .tags import emit_tag


def node_prefix(node: Node, tag_handles: dict[str, str] | None = None) -> str:
    """Return serialized tag/anchor metadata for a node."""
    tag_text = node.tag_text or emit_tag(node.tag, tag_handles)
    parts = []
    if tag_text:
        parts.append(tag_text)
    if node.anchor:
        parts.append(f"&{node.anchor}")
    return " ".join(parts)


def needs_quotes(text: str) -> bool:
    """Return True when a scalar needs quoting for this emitter."""
    if not text:
        return True
    if text.startswith(("- ", "?", ":")):
        return True
    if text.lower() in ("true", "false", "null", "~"):
        return True
    if parse_yaml_int(text) is not None or parse_yaml_float(text) is not None:
        return True
    return any(c in text for c in [":", "#", "\n", "[", "]", "{", "}", ","])


# Helper for plain mode scalar conversion.
def _plain_scalar(node: ScalarNode) -> str:
    val = node.value
    if isinstance(val, bool):
        return "true" if val else "false"
    elif val is None:
        return "null"
    elif isinstance(val, (int, float)):
        return str(val)
    elif isinstance(val, str):
        # Quote if needed.
        if needs_quotes(val):
            return (
                '"'
                + val.replace("\\", "\\\\")
                .replace("\n", "\\n")
                .replace('"', '\\"')
                + '"'
            )
        return val
    else:
        return str(val)


# ====================
# Round-Trip Dumping
# ====================
def _internal_dump_round_trip(
    node: Node, indent: int = 0, tag_handles: dict[str, str] | None = None
) -> str:
    """Dump the AST node preserving formatting metadata."""
    if isinstance(node, DocumentNode):
        return unparse_document(node, indent)
    elif isinstance(node, MappingNode):
        return unparse_mapping(node, indent, tag_handles=tag_handles)
    elif isinstance(node, SequenceNode):
        return unparse_sequence(node, indent, tag_handles=tag_handles)
    elif isinstance(node, ScalarNode):
        return unparse_scalar(node, indent, tag_handles=tag_handles)
    else:
        return " " * indent + str(node)


def unparse_document(doc: DocumentNode, indent: int = 0) -> str:
    """Unparse a DocumentNode into YAML text."""
    lines = []
    prefix = " " * indent
    for directive in doc.directives:
        lines.append(prefix + directive)
    for comment in doc.leading_comments:
        lines.append(prefix + comment)
    if doc.has_doc_start:
        if doc.root is not None and can_inline_document_root(doc.root):
            root_text = unparse_node(
                doc.root, indent, tag_handles=doc.tag_handles
            )
            root_lines = root_text.splitlines()
            if root_lines:
                lines.append(prefix + "--- " + root_lines[0].lstrip())
                lines.extend(root_lines[1:])
            else:
                lines.append(prefix + "---")
        else:
            lines.append(prefix + "---")
            if doc.root is not None:
                lines.append(
                    unparse_node(doc.root, indent, tag_handles=doc.tag_handles)
                )
    elif doc.root is not None:
        lines.append(
            unparse_node(doc.root, indent, tag_handles=doc.tag_handles)
        )
    if doc.has_doc_end:
        lines.append(prefix + "...")
    for comment in doc.trailing_comments:
        lines.append(prefix + comment)
    return "\n".join(lines)


def can_inline_document_root(node: Node) -> bool:
    """Return True for root node forms that can follow --- on the same line."""
    if isinstance(node, ScalarNode):
        return True
    if isinstance(node, (MappingNode, SequenceNode)):
        return node.flow_style
    return False


def unparse_node(
    node: Node, indent: int = 0, tag_handles: dict[str, str] | None = None
) -> str:
    """Dispatch unparse based on node type (round-trip mode)."""
    if isinstance(node, MappingNode):
        return unparse_mapping(node, indent, tag_handles=tag_handles)
    elif isinstance(node, SequenceNode):
        return unparse_sequence(node, indent, tag_handles=tag_handles)
    elif isinstance(node, ScalarNode):
        return unparse_scalar(node, indent, tag_handles=tag_handles)
    else:
        return " " * indent + str(node)


def unparse_mapping(
    mapping: MappingNode,
    indent: int = 0,
    tag_handles: dict[str, str] | None = None,
) -> str:
    """Unparse a MappingNode with formatting metadata preserved."""
    if mapping.flow_style:
        meta = node_prefix(mapping, tag_handles)
        entries = []
        for merge_node in mapping.merges:
            entries.append("<<: " + unparse_node(merge_node, 0, tag_handles))
        for key_node, value_node in mapping.pairs:
            key_str = (
                unparse_scalar(key_node, 0, tag_handles)
                if isinstance(key_node, ScalarNode)
                else unparse_node(key_node, 0, tag_handles)
            )
            entries.append(
                f"{key_str}: {unparse_node(value_node, 0, tag_handles)}"
            )
        text = "{" + ", ".join(entries) + "}"
        if meta:
            text = meta + " " + text
        return " " * indent + text

    lines = []
    prefix = " " * indent
    for merge_node in mapping.merges:
        line = prefix + "<<: " + unparse_node(merge_node, 0, tag_handles)
        lines.append(line)
    for key_node, value_node in mapping.pairs:
        for comment in key_node.leading_comments:
            lines.append(prefix + comment)
        key_str = (
            unparse_scalar(key_node, 0, tag_handles)
            if isinstance(key_node, ScalarNode)
            else unparse_node(key_node, 0, tag_handles)
        )
        if isinstance(key_node, ScalarNode) and key_node.style in ("|", ">"):
            lines.append(prefix + f"? {key_str}")
            if isinstance(value_node, (MappingNode, SequenceNode)):
                lines.append(prefix + ":")
                lines.append(unparse_node(value_node, indent + 2, tag_handles))
            else:
                lines.append(
                    prefix + f": {unparse_node(value_node, 0, tag_handles)}"
                )
            continue
        if not isinstance(key_node, ScalarNode):
            lines.append(prefix + f"? {key_str}")
            if isinstance(value_node, (MappingNode, SequenceNode)):
                lines.append(prefix + ":")
                lines.append(unparse_node(value_node, indent + 2, tag_handles))
            else:
                lines.append(
                    prefix + f": {unparse_node(value_node, 0, tag_handles)}"
                )
            continue
        if (
            isinstance(value_node, (MappingNode, SequenceNode))
            and value_node.flow_style
        ):
            line = (
                prefix
                + f"{key_str}: {unparse_node(value_node, 0, tag_handles)}"
            )
            if key_node.trailing_comments:
                line += " " + " ".join(key_node.trailing_comments)
            lines.append(line)
        elif isinstance(value_node, (MappingNode, SequenceNode)):
            line = prefix + f"{key_str}:"
            meta = node_prefix(value_node, tag_handles)
            if meta:
                line += " " + meta
            if key_node.trailing_comments:
                line += " " + " ".join(key_node.trailing_comments)
            lines.append(line)
            lines.append(unparse_node(value_node, indent + 2, tag_handles))
        else:
            value_str = unparse_node(value_node, 0, tag_handles)
            line = prefix + f"{key_str}: {value_str}"
            if key_node.trailing_comments:
                line += " " + " ".join(key_node.trailing_comments)
            lines.append(line)
    return "\n".join(lines)


def unparse_sequence(
    seq: SequenceNode,
    indent: int = 0,
    tag_handles: dict[str, str] | None = None,
) -> str:
    """Unparse a SequenceNode with formatting metadata preserved."""
    if seq.flow_style:
        meta = node_prefix(seq, tag_handles)
        items = ", ".join(
            unparse_node(item, 0, tag_handles) for item in seq.items
        )
        text = "[" + items + "]"
        if meta:
            text = meta + " " + text
        return " " * indent + text

    lines = []
    prefix = " " * indent
    for item in seq.items:
        if isinstance(item, (MappingNode, SequenceNode)) and item.flow_style:
            lines.append(prefix + f"- {unparse_node(item, 0, tag_handles)}")
        elif isinstance(item, (MappingNode, SequenceNode)):
            meta = node_prefix(item, tag_handles)
            line = prefix + "-"
            if meta:
                line += " " + meta
            lines.append(line)
            lines.append(unparse_node(item, indent + 2, tag_handles))
        else:
            item_str = unparse_node(item, 0)
            lines.append(prefix + f"- {item_str}")
    return "\n".join(lines)


def unparse_scalar(
    scalar: ScalarNode,
    indent: int = 0,
    tag_handles: dict[str, str] | None = None,
) -> str:
    """Unparse a ScalarNode with formatting metadata preserved."""
    prefix = " " * indent
    if scalar.alias_of:
        return prefix + "*" + scalar.alias_of
    tag_text = scalar.tag_text or emit_tag(scalar.tag, tag_handles)
    tag_part = f"{tag_text} " if tag_text else ""
    anchor_part = f"&{scalar.anchor} " if scalar.anchor else ""
    if scalar.style in ("|", ">"):
        header = scalar.block_header
        if header is None:
            chomping = scalar.chomping or ""
            indent_indicator = scalar.indent_indicator or ""
            header = scalar.style + str(indent_indicator) + chomping
        lines = [prefix + tag_part + anchor_part + header]
        if scalar.lines:
            for line in scalar.lines:
                lines.append(" " * (indent + 2) + line)
        else:
            for line in str(scalar.value).splitlines():
                lines.append(" " * (indent + 2) + line)
        return "\n".join(lines)
    else:
        val = scalar.value
        if isinstance(val, bool):
            text = "true" if val else "false"
        elif val is None:
            text = "null"
        elif isinstance(val, (int, float)):
            text = str(val)
        elif isinstance(val, str):
            text = val
            if tag_text and scalar.tag == "tag:yaml.org,2002:str":
                pass
            elif needs_quotes(text):
                text = (
                    '"'
                    + text.replace("\\", "\\\\")
                    .replace("\n", "\\n")
                    .replace('"', '\\"')
                    + '"'
                )
        else:
            text = str(val)
        return prefix + tag_part + anchor_part + text


# ==================
# Plain Dumping
# ==================
def _internal_dump_plain(node: Node, indent: int = 0) -> str:
    """
    Dump the AST node to plain YAML, ignoring extra formatting metadata.
    Document markers, comments, and anchors are omitted.
    """
    if isinstance(node, DocumentNode):
        return _internal_dump_plain(node.root, indent)
    elif isinstance(node, MappingNode):
        lines = []
        prefix = " " * indent
        for key_node, value_node in node.pairs:
            key_str = (
                _plain_scalar(key_node)
                if isinstance(key_node, ScalarNode)
                else _internal_dump_plain(key_node, 0)
            )
            if isinstance(value_node, (MappingNode, SequenceNode)):
                lines.append(prefix + f"{key_str}:")
                lines.append(_internal_dump_plain(value_node, indent + 2))
            else:
                value_str = (
                    _plain_scalar(value_node)
                    if isinstance(value_node, ScalarNode)
                    else _internal_dump_plain(value_node, 0)
                )
                line = prefix + f"{key_str}: {value_str}"
                if key_node.trailing_comments:
                    line += " " + " ".join(key_node.trailing_comments)
                lines.append(line)
        return "\n".join(lines)
    elif isinstance(node, SequenceNode):
        lines = []
        prefix = " " * indent
        for item in node.items:
            if isinstance(item, (MappingNode, SequenceNode)):
                lines.append(prefix + "-")
                lines.append(_internal_dump_plain(item, indent + 2))
            else:
                item_text = (
                    _plain_scalar(item)
                    if isinstance(item, ScalarNode)
                    else _internal_dump_plain(item, 0)
                )
                lines.append(prefix + f"- {item_text}")
        return "\n".join(lines)
    elif isinstance(node, ScalarNode):
        return " " * indent + _plain_scalar(node)
    else:
        return " " * indent + str(node)
