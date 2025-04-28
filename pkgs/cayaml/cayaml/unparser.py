"""
unparser.py - YAML unparser for Cayaml (Swarmauri's Canon YAML)

This module traverses the AST (constructed using ast_nodes.py) and
reconstructs a YAML-formatted string.

It provides two internal dump functions:
  - _internal_dump_plain(node, indent=0): Emits plain YAML (ignoring extra formatting metadata).
  - _internal_dump_round_trip(node, indent=0): Emits YAML preserving document markers,
    comments, anchors/tags, block styles (folded/literal), merge operators, and key order.

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
        if not val or any(c in val for c in [" ", ":", "-", "#"]):
            return '"' + val.replace('"', '\\"') + '"'
        return val
    else:
        return str(val)


# ====================
# Round-Trip Dumping
# ====================
def _internal_dump_round_trip(node: Node, indent: int = 0) -> str:
    """Dump the AST node preserving formatting metadata."""
    if isinstance(node, DocumentNode):
        return unparse_document(node, indent)
    elif isinstance(node, MappingNode):
        return unparse_mapping(node, indent)
    elif isinstance(node, SequenceNode):
        return unparse_sequence(node, indent)
    elif isinstance(node, ScalarNode):
        return unparse_scalar(node, indent)
    else:
        return " " * indent + str(node)


def unparse_document(doc: DocumentNode, indent: int = 0) -> str:
    """Unparse a DocumentNode into YAML text, preserving document markers and comments."""
    lines = []
    prefix = " " * indent
    for comment in doc.leading_comments:
        lines.append(prefix + comment)
    if doc.has_doc_start:
        lines.append(prefix + "---")
    if doc.root is not None:
        lines.append(unparse_node(doc.root, indent))
    if doc.has_doc_end:
        lines.append(prefix + "...")
    for comment in doc.trailing_comments:
        lines.append(prefix + comment)
    return "\n".join(lines)


def unparse_node(node: Node, indent: int = 0) -> str:
    """Dispatch unparse based on node type (round-trip mode)."""
    if isinstance(node, MappingNode):
        return unparse_mapping(node, indent)
    elif isinstance(node, SequenceNode):
        return unparse_sequence(node, indent)
    elif isinstance(node, ScalarNode):
        return unparse_scalar(node, indent)
    else:
        return " " * indent + str(node)


def unparse_mapping(mapping: MappingNode, indent: int = 0) -> str:
    """Unparse a MappingNode with formatting metadata preserved."""
    lines = []
    prefix = " " * indent
    for merge_node in mapping.merges:
        line = prefix + "<<: " + unparse_node(merge_node, 0)
        lines.append(line)
    for key_node, value_node in mapping.pairs:
        for comment in key_node.leading_comments:
            lines.append(prefix + comment)
        key_str = (
            unparse_scalar(key_node, 0)
            if isinstance(key_node, ScalarNode)
            else unparse_node(key_node, 0)
        )
        if isinstance(value_node, (MappingNode, SequenceNode)):
            line = prefix + f"{key_str}:"
            if key_node.trailing_comments:
                line += " " + " ".join(key_node.trailing_comments)
            lines.append(line)
            lines.append(unparse_node(value_node, indent + 2))
        else:
            value_str = unparse_node(value_node, 0)
            line = prefix + f"{key_str}: {value_str}"
            if key_node.trailing_comments:
                line += " " + " ".join(key_node.trailing_comments)
            lines.append(line)
    return "\n".join(lines)


def unparse_sequence(seq: SequenceNode, indent: int = 0) -> str:
    """Unparse a SequenceNode with formatting metadata preserved."""
    lines = []
    prefix = " " * indent
    for item in seq.items:
        if isinstance(item, (MappingNode, SequenceNode)):
            lines.append(prefix + "-")
            lines.append(unparse_node(item, indent + 2))
        else:
            item_str = unparse_node(item, 0)
            lines.append(prefix + f"- {item_str}")
    return "\n".join(lines)


def unparse_scalar(scalar: ScalarNode, indent: int = 0) -> str:
    """Unparse a ScalarNode with formatting metadata preserved."""
    prefix = " " * indent
    if scalar.alias_of:
        return prefix + "*" + scalar.alias_of
    tag_part = f"{scalar.tag} " if scalar.tag else ""
    anchor_part = f"&{scalar.anchor} " if scalar.anchor else ""
    if scalar.style in ("|", ">"):
        lines = [prefix + tag_part + anchor_part + scalar.style]
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
            if not text or any(c in text for c in [" ", ":", "-", "#"]):
                text = '"' + text.replace('"', '\\"') + '"'
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
                lines.append(prefix + f"{key_str}: {value_str}")
        return "\n".join(lines)
    elif isinstance(node, SequenceNode):
        lines = []
        prefix = " " * indent
        for item in node.items:
            if isinstance(item, (MappingNode, SequenceNode)):
                lines.append(prefix + "-")
                lines.append(_internal_dump_plain(item, indent + 2))
            else:
                lines.append(
                    prefix
                    + f"- {_plain_scalar(item) if isinstance(item, ScalarNode) else _internal_dump_plain(item, 0)}"
                )
        return "\n".join(lines)
    elif isinstance(node, ScalarNode):
        return " " * indent + _plain_scalar(node)
    else:
        return " " * indent + str(node)


# The plain scalar conversion is similar to our helper in round-trip mode.
def _plain_scalar(node: ScalarNode) -> str:
    val = node.value
    if isinstance(val, bool):
        return "true" if val else "false"
    elif val is None:
        return "null"
    elif isinstance(val, (int, float)):
        return str(val)
    elif isinstance(val, str):
        if not val or any(c in val for c in [" ", ":", "-", "#"]):
            return '"' + val.replace('"', '\\"') + '"'
        return val
    else:
        return str(val)
