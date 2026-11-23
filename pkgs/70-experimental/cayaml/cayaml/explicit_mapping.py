"""Explicit block mapping entry parsing for Cayaml."""

from .ast_nodes import ScalarNode
from .block_scalars import (
    block_scalar_value,
    parse_block_scalar_header,
    parse_block_scalar_lines,
)
from .errors import YamlParseError
from .flow import fold_plain_continuation
from .mapping_keys import add_mapping_pair
from .scanner import (
    find_top_level_colon,
    indentation_width,
    is_explicit_key_entry,
    is_sequence_entry,
    split_inline_comment,
)


def parse_explicit_mapping_entry(
    lines: list,
    index: int,
    current_indent: int,
    anchors: dict,
    mapping,
) -> int:
    """Parse one explicit block mapping entry and return the next index."""
    from .block_parser import parse_block

    key_text = lines[index].strip()[1:].strip()
    index += 1
    key_node = None
    compact_value_node = None
    if key_text:
        key_node, compact_value_node, index = explicit_key_from_text(
            key_text, lines, index, current_indent, anchors
        )
    else:
        key_lines = collect_indented_lines(lines, index, current_indent)
        index += len(key_lines)
        if key_lines:
            key_node, _ = parse_block(
                key_lines, indent=current_indent + 1, anchors=anchors
            )
    if key_node is None:
        raise YamlParseError("explicit mapping key is missing")

    if compact_value_node is not None:
        if index < len(lines):
            next_indent = indentation_width(lines[index])
            if next_indent == current_indent and lines[
                index
            ].strip().startswith(":"):
                raise YamlParseError("explicit mapping key has extra value")
        add_mapping_pair(mapping, key_node, compact_value_node)
        return index

    index, value_node, should_continue = explicit_value_node(
        lines, index, current_indent, anchors
    )
    add_mapping_pair(mapping, key_node, value_node)
    return index if should_continue else index


def explicit_key_from_text(
    key_text: str,
    lines: list,
    index: int,
    current_indent: int,
    anchors: dict,
):
    """Build an explicit key node from compact key text."""
    from .block_parser import parse_block
    from .construction import make_scalar_node

    compact_value_node = None
    compact_text, compact_comment = split_inline_comment(key_text)
    compact_colon = find_top_level_colon(compact_text)
    if compact_colon != -1:
        key_text = compact_text[:compact_colon].strip()
        compact_value_text = compact_text[compact_colon + 1 :].strip()
        compact_value_node = (
            make_scalar_node(compact_value_text, anchors)
            if compact_value_text
            else ScalarNode(None)
        )
        if compact_comment:
            compact_value_node.trailing_comments.append(compact_comment)
    else:
        key_text = compact_text
    if is_sequence_entry(key_text):
        key_lines = [" " * (current_indent + 2) + key_text]
        extra_lines = collect_indented_lines(lines, index, current_indent)
        key_lines.extend(extra_lines)
        index += len(extra_lines)
        key_node, _ = parse_block(
            key_lines, indent=current_indent + 1, anchors=anchors
        )
    elif block_header := parse_block_scalar_header(key_text):
        style_char, chomping, indent_indicator = block_header
        key_node = ScalarNode(None, style=style_char)
        key_node.chomping = chomping
        key_node.indent_indicator = indent_indicator
        key_node.block_header = key_text
        key_node.lines, index = parse_block_scalar_lines(
            lines, index, current_indent, indent_indicator
        )
        key_node.value = block_scalar_value(
            style_char, key_node.lines, chomping=chomping
        )
    else:
        continuation_lines = []
        while index < len(lines):
            key_line = lines[index]
            key_indent = indentation_width(key_line)
            key_strip = key_line.strip()
            if (
                key_indent <= current_indent
                or not key_strip
                or key_strip.startswith(":")
            ):
                break
            key_value, _ = split_inline_comment(key_strip)
            continuation_lines.append(key_value)
            index += 1
        key_text = fold_plain_continuation(key_text, continuation_lines)
        key_node = make_scalar_node(key_text, anchors)
    return key_node, compact_value_node, index


def explicit_value_node(lines: list, index: int, current_indent: int, anchors):
    """Parse the value paired with an explicit mapping key."""
    if index >= len(lines):
        return index, ScalarNode(None), True
    while index < len(lines) and (
        not lines[index].strip() or lines[index].lstrip().startswith("#")
    ):
        index += 1
    if index >= len(lines):
        return index, ScalarNode(None), True
    value_line = lines[index]
    value_indent = indentation_width(value_line)
    value_strip = value_line.strip()
    if value_indent != current_indent or not value_strip.startswith(":"):
        return index, ScalarNode(None), True
    if value_strip.startswith((":\t", ": \t")):
        raise YamlParseError("invalid tab-separated explicit value")
    index += 1
    value_text, inline_comment = split_inline_comment(value_strip[1:].strip())
    value_node, index = explicit_value_from_text(
        value_text, lines, index, value_line, value_indent, anchors
    )
    if inline_comment:
        value_node.trailing_comments.append(inline_comment)
    return index, value_node, True


def explicit_value_from_text(
    value_text: str,
    lines: list,
    index: int,
    value_line: str,
    value_indent: int,
    anchors,
):
    """Parse an explicit value from compact value text or nested lines."""
    from .block_parser import parse_block
    from .construction import make_scalar_node

    if value_text:
        if is_sequence_entry(value_text):
            compact_indent = value_line.find(value_text)
            if compact_indent < 0:
                compact_indent = value_indent
            value_lines = [" " * compact_indent + value_text]
            while index < len(lines):
                nested_line = lines[index]
                nested_indent = indentation_width(nested_line)
                if nested_indent < compact_indent or not nested_line.strip():
                    break
                value_lines.append(nested_line)
                index += 1
            value_node, _ = parse_block(
                value_lines, indent=compact_indent, anchors=anchors
            )
            return value_node, index
        continuation_lines = []
        while index < len(lines):
            nested_line = lines[index]
            nested_indent = indentation_width(nested_line)
            nested_strip = nested_line.strip()
            if (
                nested_indent <= value_indent
                or not nested_strip
                or is_sequence_entry(nested_strip)
                or is_explicit_key_entry(nested_strip)
                or find_top_level_colon(nested_strip) != -1
            ):
                break
            nested_value, _ = split_inline_comment(nested_strip)
            continuation_lines.append(nested_value)
            index += 1
        value_text = fold_plain_continuation(value_text, continuation_lines)
        return make_scalar_node(value_text, anchors), index
    nested_lines = []
    while index < len(lines):
        nested_line = lines[index]
        nested_indent = indentation_width(nested_line)
        if not nested_line.strip():
            if nested_lines:
                nested_lines.append(nested_line)
                index += 1
                continue
            break
        if nested_indent <= value_indent:
            break
        nested_lines.append(nested_line)
        index += 1
    if nested_lines:
        child_indent = indentation_width(nested_lines[0])
        value_node, _ = parse_block(
            nested_lines, indent=child_indent, anchors=anchors
        )
        return value_node, index
    return ScalarNode(None), index


def collect_indented_lines(lines: list, index: int, current_indent: int):
    """Collect lines indented deeper than the current explicit-key line."""
    collected = []
    while index < len(lines):
        key_line = lines[index]
        key_indent = indentation_width(key_line)
        if key_indent <= current_indent or not key_line.strip():
            break
        collected.append(key_line)
        index += 1
    return collected
