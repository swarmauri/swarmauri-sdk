"""Internal YAML parser support for Cayaml."""

from .ast_nodes import MappingNode, ScalarNode, SequenceNode
from .block_scalars import (
    block_scalar_value,
    parse_block_scalar_header,
    parse_block_scalar_lines,
)
from .construction import (
    assign_node_metadata,
    make_empty_node,
    make_scalar_node,
    materialize_anchored_container,
    new_container_placeholder,
)
from .errors import YamlParseError
from .flow import fold_plain_continuation
from .properties import split_tag_anchor_prefix
from .scanner import (
    find_top_level_colon,
    indentation_width,
    is_balanced_flow,
    is_sequence_entry,
    split_inline_comment,
)


def parse_sequence(lines: list, indent: int, anchors=None):
    """
    Parse a block of lines as a sequence.
    Returns (SequenceNode, remaining_lines).
    """
    anchors = anchors if anchors is not None else {}
    sequence = SequenceNode()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        line_strip = line.strip()
        current_indent = indentation_width(line)

        if not line_strip or current_indent < indent:
            break

        if line.lstrip().startswith("#"):
            sequence.leading_comments.append(line_strip)
            i += 1
            continue

        if not is_sequence_entry(line_strip):
            break

        if line_strip.startswith("-\t") and is_sequence_entry(
            line_strip[2:].strip()
        ):
            raise YamlParseError("invalid tab-separated sequence entry")
        if line_strip.startswith("- \t") and is_sequence_entry(
            line_strip[3:].strip()
        ):
            raise YamlParseError("invalid tab-separated sequence entry")

        # Remove leading dash
        dash_part, inline_comment = split_inline_comment(
            line_strip[1:].strip()
        )
        i += 1
        tag, anchor, remaining_value = split_tag_anchor_prefix(dash_part)
        dash_part = remaining_value

        # Block scalar sequence item.
        if block_header := parse_block_scalar_header(dash_part):
            style_char, chomping, indent_indicator = block_header
            block_node = ScalarNode(None, style=style_char)
            block_node.chomping = chomping
            block_node.indent_indicator = indent_indicator
            block_node.block_header = dash_part
            block_node.lines = []

            block_node.lines, i = parse_block_scalar_lines(
                lines, i, current_indent, indent_indicator
            )
            block_node.value = block_scalar_value(
                style_char, block_node.lines, chomping=chomping
            )
            assign_node_metadata(
                block_node, tag=tag, anchor=anchor, anchors=anchors
            )
            sequence.add_item(block_node)

        elif is_sequence_entry(dash_part):
            compact_indent = line.find(dash_part)
            if compact_indent < 0:
                compact_indent = current_indent + 2
            item_lines = [" " * compact_indent + dash_part]
            while i < n:
                nested_line = lines[i]
                nested_indent = indentation_width(nested_line)
                if nested_indent <= current_indent or not nested_line.strip():
                    break
                if nested_indent < compact_indent:
                    raise YamlParseError(
                        "invalid indentation in sequence item"
                    )
                item_lines.append(nested_line)
                i += 1

            placeholder = None
            if anchor:
                placeholder = SequenceNode()
                assign_node_metadata(
                    placeholder, tag=tag, anchor=anchor, anchors=anchors
                )
            from .sequence_parser import parse_sequence

            item_node, _ = parse_sequence(
                item_lines, indent=compact_indent, anchors=anchors
            )
            if placeholder is not None:
                item_node = materialize_anchored_container(
                    item_node, placeholder
                )
            else:
                assign_node_metadata(
                    item_node, tag=tag, anchor=anchor, anchors=anchors
                )
            if inline_comment:
                item_node.trailing_comments.append(inline_comment)
            sequence.add_item(item_node)

        elif not dash_part:
            # Possibly nested structure
            nested_lines = []
            while i < n:
                nested_line = lines[i]
                nested_indent = indentation_width(nested_line)
                if nested_indent <= current_indent or not nested_line.strip():
                    break
                nested_lines.append(nested_line)
                i += 1

            if nested_lines:
                placeholder = None
                if anchor:
                    placeholder = new_container_placeholder(nested_lines)
                    assign_node_metadata(
                        placeholder, tag=tag, anchor=anchor, anchors=anchors
                    )
                from .block_parser import parse_block

                item_node, rest = parse_block(
                    nested_lines, indent=current_indent + 1, anchors=anchors
                )
                if rest:
                    raise YamlParseError("invalid nested sequence indentation")
                if placeholder is not None:
                    item_node = materialize_anchored_container(
                        item_node, placeholder
                    )
                else:
                    assign_node_metadata(
                        item_node, tag=tag, anchor=anchor, anchors=anchors
                    )
            else:
                item_node = make_empty_node(
                    tag=tag, anchor=anchor, anchors=anchors
                )
            sequence.add_item(item_node)
        elif find_top_level_colon(dash_part) != -1:
            item_lines = [" " * (current_indent + 2) + dash_part]
            while i < n:
                nested_line = lines[i]
                nested_indent = indentation_width(nested_line)
                if nested_indent <= current_indent or not nested_line.strip():
                    break
                if nested_indent < current_indent + 2:
                    raise YamlParseError(
                        "invalid indentation in sequence item"
                    )
                item_lines.append(nested_line)
                i += 1

            placeholder = None
            if anchor:
                placeholder = MappingNode()
                assign_node_metadata(
                    placeholder, tag=tag, anchor=anchor, anchors=anchors
                )
            from .mapping_parser import parse_mapping

            item_node, rest = parse_mapping(
                item_lines, indent=current_indent + 2, anchors=anchors
            )
            if rest:
                raise YamlParseError("invalid nested sequence mapping")
            if placeholder is not None:
                item_node = materialize_anchored_container(
                    item_node, placeholder
                )
            else:
                assign_node_metadata(
                    item_node, tag=tag, anchor=anchor, anchors=anchors
                )
            if inline_comment:
                item_node.trailing_comments.append(inline_comment)
            sequence.add_item(item_node)
        else:
            # Normal scalar or inline text after '-'
            continuation_lines = []
            if dash_part.startswith(("[", "{")):
                while i < n and not is_balanced_flow(
                    fold_plain_continuation(dash_part, continuation_lines)
                ):
                    stripped_line = lines[i].strip()
                    if lines[i].lstrip(" ").startswith(
                        "\t"
                    ) and stripped_line not in (
                        "",
                        "[",
                        "]",
                        "{",
                        "}",
                        "[]",
                        "{}",
                    ):
                        raise YamlParseError(
                            "tab indentation is not allowed in flow"
                        )
                    continuation_text, _ = split_inline_comment(
                        lines[i].strip()
                    )
                    if continuation_text:
                        continuation_lines.append(continuation_text)
                    i += 1
            else:
                while i < n:
                    nested_line = lines[i]
                    nested_indent = indentation_width(nested_line)
                    if (
                        nested_indent <= current_indent
                        or not nested_line.strip()
                    ):
                        break
                    continuation_text, _ = split_inline_comment(
                        nested_line.strip()
                    )
                    continuation_lines.append(continuation_text)
                    i += 1
            dash_part = fold_plain_continuation(dash_part, continuation_lines)
            item_node = make_scalar_node(
                " ".join(
                    part
                    for part in (
                        tag,
                        f"&{anchor}" if anchor else None,
                        dash_part,
                    )
                    if part
                ),
                anchors,
            )
            if inline_comment:
                item_node.trailing_comments.append(inline_comment)
            sequence.add_item(item_node)

    remaining = lines[i:]
    return sequence, remaining
