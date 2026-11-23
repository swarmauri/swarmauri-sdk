"""Internal YAML parser support for Cayaml."""

import math

from .ast_nodes import DocumentNode, MappingNode, ScalarNode, SequenceNode
from .errors import YamlParseError


def node_key_identity(node):
    """Return a comparable identity for duplicate mapping-key detection."""
    if isinstance(node, ScalarNode):
        value = node.value
        if isinstance(value, float) and math.isnan(value):
            return ("scalar", float, "nan")
        if isinstance(
            value, (DocumentNode, MappingNode, SequenceNode, ScalarNode)
        ):
            return ("scalar-node", node_key_identity(value))
        return ("scalar", type(value), value)
    if isinstance(node, SequenceNode):
        return ("seq", tuple(node_key_identity(item) for item in node.items))
    if isinstance(node, MappingNode):
        return (
            "map",
            tuple(
                (node_key_identity(key), node_key_identity(value))
                for key, value in node.pairs
            ),
        )
    return ("object", type(node), repr(node))


def add_mapping_pair(mapping: MappingNode, key_node, value_node):
    """Append a mapping pair after enforcing YAML key uniqueness."""
    key_identity = node_key_identity(key_node)
    for existing_key, _ in mapping.pairs:
        if node_key_identity(existing_key) == key_identity:
            raise YamlParseError("duplicate mapping key")
    mapping.add_pair(key_node, value_node)
