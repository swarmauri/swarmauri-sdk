"""
plain_conversion.py - Helpers to convert Cayaml AST nodes to plain Python objects.

This module provides the `to_plain()` function which recursively traverses
the AST (returned by the round-trip loader) and converts each node into its plain
Python equivalent. For example:
  - DocumentNode and MappingNode are converted to dictionaries.
  - SequenceNode is converted to a list.
  - ScalarNode is converted to its underlying value.
If the node is a YamlStream containing multiple documents, a list of plain objects is returned.
"""

from .ast_nodes import DocumentNode, MappingNode, SequenceNode, ScalarNode, YamlStream


def to_plain(node):
    """
    Recursively convert the given AST node into plain Python objects.

    Parameters:
        node: An AST node (DocumentNode, MappingNode, SequenceNode, or ScalarNode)
              or a YamlStream.

    Returns:
        The equivalent plain Python data structure (dict, list, scalar) for that node.
    """
    # If node is a YamlStream, return a list of plain objects, one per document.
    if isinstance(node, YamlStream):
        return [to_plain(doc) for doc in node.documents]

    # If node is a DocumentNode, return the plain version of its root.
    if isinstance(node, DocumentNode):
        if node.root is not None:
            return to_plain(node.root)
        else:
            return {}

    # If node is a MappingNode, convert its pairs into a dictionary.
    if isinstance(node, MappingNode):
        result = {}
        for merge_node in node.merges:
            merged = to_plain(merge_node)
            if isinstance(merged, dict):
                result.update(merged)
        for key_node, value_node in node.pairs:
            # Convert the key: if it's a ScalarNode, use its value; otherwise, convert recursively.
            key = (
                key_node.value
                if isinstance(key_node, ScalarNode)
                else to_plain(key_node)
            )
            result[key] = to_plain(value_node)
        return result

    # If node is a SequenceNode, convert each item recursively.
    if isinstance(node, SequenceNode):
        return [to_plain(item) for item in node.items]

    # If node is a ScalarNode, return its underlying value.
    if isinstance(node, ScalarNode):
        if node.style in ("|", ">") and node.value is not None:
            return node.value
        if node.style == "|":
            return "\n".join(node.lines or []) + "\n"
        if node.style == ">":
            lines = node.lines or []
            folded = []
            paragraph = []
            for line in lines:
                if line:
                    paragraph.append(line.strip())
                else:
                    if paragraph:
                        folded.append(" ".join(paragraph))
                        paragraph = []
                    folded.append("")
            if paragraph:
                folded.append(" ".join(paragraph))
            return "\n".join(folded).rstrip("\n") + "\n"
        return node.value

    # Fallback: if the node is already a plain Python object or unknown type.
    return node
