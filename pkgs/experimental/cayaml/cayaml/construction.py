"""Internal YAML parser support for Cayaml."""

from .ast_nodes import MappingNode, ScalarNode, SequenceNode
from .errors import YamlParseError
from .flow import parse_flow_node
from .properties import split_tag_anchor_prefix, validate_anchor_name
from .scalars import parse_scalar
from .scanner import (
    find_top_level_colon,
    is_sequence_entry,
    split_inline_comment,
)
from .tags import expand_tag


def make_scalar_node(value: str, anchors: dict[str, object]) -> ScalarNode:
    """Create a scalar node, resolving tags, anchors, and aliases."""
    raw_tag, anchor, scalar_text = split_tag_anchor_prefix(value)
    scalar_text, trailing_comment = split_inline_comment(scalar_text)
    tag = expand_tag(raw_tag, anchors)
    if (raw_tag or anchor) and is_sequence_entry(scalar_text):
        raise YamlParseError("properties cannot prefix a block sequence entry")
    if (raw_tag or anchor) and find_top_level_colon(scalar_text) != -1:
        raise YamlParseError("properties cannot prefix a block mapping entry")
    if scalar_text.startswith("*"):
        if raw_tag or anchor:
            raise YamlParseError("alias node must not specify properties")
        alias = validate_anchor_name(scalar_text[1:], "alias")
        if alias not in anchors:
            raise YamlParseError(f"undefined alias: {alias}")
        target = anchors.get(alias)
        if isinstance(target, ScalarNode):
            node = ScalarNode(target.value, style=target.style)
            node.lines = (
                list(target.lines) if target.lines is not None else None
            )
            node.tag = target.tag
        else:
            node = ScalarNode(target)
        node.alias_of = alias
    elif flow_node := parse_flow_node(scalar_text, anchors):
        node = flow_node
    else:
        node = ScalarNode(parse_scalar(scalar_text, tag=tag))
    validate_node_tag(node, tag)
    assign_node_metadata(
        node,
        tag=raw_tag,
        anchor=anchor,
        anchors=anchors,
    )
    if trailing_comment:
        node.trailing_comments.append(trailing_comment)
    return node


def make_empty_node(
    tag: str | None = None, anchor: str | None = None, anchors=None
) -> ScalarNode:
    """Create an empty YAML node, preserving optional tag/anchor metadata."""
    parts = [part for part in (tag, f"&{anchor}" if anchor else None) if part]
    if parts:
        return make_scalar_node(" ".join(parts), anchors or {})
    return ScalarNode(None)


def validate_node_tag(node, tag: str | None):
    """Validate explicit collection tags against parsed node kinds."""
    if tag == "tag:yaml.org,2002:seq" and not isinstance(node, SequenceNode):
        raise YamlParseError("invalid node kind for tag !!seq")
    if tag == "tag:yaml.org,2002:map" and not isinstance(node, MappingNode):
        raise YamlParseError("invalid node kind for tag !!map")


def materialize_anchored_container(value_node, placeholder):
    """Copy parsed container contents into an anchor placeholder."""
    if isinstance(placeholder, MappingNode) and isinstance(
        value_node, MappingNode
    ):
        placeholder.pairs = value_node.pairs
        placeholder.merges = value_node.merges
        placeholder.flow_style = value_node.flow_style
        return placeholder
    if isinstance(placeholder, SequenceNode) and isinstance(
        value_node, SequenceNode
    ):
        placeholder.items = value_node.items
        placeholder.flow_style = value_node.flow_style
        return placeholder
    return value_node


def merge_nodes_from(raw_value: str, anchors: dict[str, object]):
    """Return validated mapping nodes for a YAML merge value."""
    merge_node = parse_merge_value(raw_value, anchors)
    merge_nodes = (
        merge_node.items
        if isinstance(merge_node, SequenceNode)
        else [merge_node]
    )
    for node in merge_nodes:
        if not isinstance(node, MappingNode):
            raise YamlParseError("invalid merge value: expected mapping")
    return merge_nodes


def new_container_placeholder(nested_lines: list[str]):
    """Create a container placeholder matching the nested block shape."""
    from .block_parser import skip_blank_and_comment

    trimmed = skip_blank_and_comment(nested_lines)
    if trimmed and trimmed[0].lstrip().startswith("-"):
        return SequenceNode()
    return MappingNode()


def assign_node_metadata(
    node, tag: str | None = None, anchor: str | None = None, anchors=None
):
    """Attach tag/anchor metadata and register anchored nodes."""
    if tag:
        node.tag = expand_tag(tag, anchors)
        node.tag_text = tag
    if anchor:
        node.anchor = anchor
        if anchors is not None:
            anchors[anchor] = node
    return node


def parse_merge_value(raw_value: str, anchors: dict[str, object]):
    """Parse a merge value into a node or sequence of nodes."""
    raw_value = raw_value.strip()
    if raw_value.startswith("[") and raw_value.endswith("]"):
        sequence = SequenceNode()
        inner = raw_value[1:-1].strip()
        if inner:
            for item in inner.split(","):
                sequence.add_item(parse_merge_value(item.strip(), anchors))
        return sequence
    if raw_value.startswith("*"):
        alias = validate_anchor_name(raw_value[1:], "alias")
        if alias not in anchors:
            raise YamlParseError(f"undefined alias: {alias}")
        return anchors[alias]
    return make_scalar_node(raw_value, anchors)
