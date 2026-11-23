"""Internal YAML parser support for Cayaml."""

from .ast_nodes import ScalarNode
from .block_scalars import (
    block_scalar_value,
    parse_block_scalar_header,
    parse_block_scalar_lines,
)
from .construction import assign_node_metadata, make_scalar_node
from .flow import collect_flow_text, fold_plain_continuation
from .properties import split_tag_anchor_prefix
from .scanner import (
    find_top_level_colon,
    indentation_width,
    is_explicit_key_entry,
    is_sequence_entry,
    split_inline_comment,
)


def fold_plain_block_lines(lines: list[str]) -> str:
    """Fold plain scalar continuation lines."""
    if (
        lines
        and lines[0].startswith(("'", '"'))
        and (len(lines[0]) == 1 or not lines[0].endswith(lines[0][0]))
    ):
        return fold_plain_continuation(lines[0], lines[1:])
    value = ""
    pending_break = False
    for line in lines:
        if line == "":
            pending_break = True
            continue
        if not value:
            value = line
        elif pending_break:
            value += "\n" + line
        else:
            value += " " + line
        pending_break = False
    return value


def parse_block(lines: list, indent: int, anchors=None):
    """
    Decide whether the block is a mapping or a sequence, then parse.
    Returns (Node, remaining_lines).
    """
    # Skip blank or comment lines to see what's next
    anchors = anchors if anchors is not None else {}
    trimmed = skip_blank_and_comment(lines)
    if not trimmed:
        return None, []

    first_line = trimmed[0].lstrip()
    first_indent = indentation_width(trimmed[0])
    tag, anchor, remaining = split_tag_anchor_prefix(first_line.strip())
    if (tag or anchor) and not remaining:
        next_indent = (
            indentation_width(trimmed[1]) if len(trimmed) > 1 else indent
        )
        node, rest = parse_block(
            trimmed[1:], min(indent, next_indent), anchors=anchors
        )
        if node is not None:
            assign_node_metadata(node, tag=tag, anchor=anchor, anchors=anchors)
        return node, rest
    if (tag or anchor) and remaining.startswith(("[", "{")):
        flow_result = collect_flow_text([remaining, *trimmed[1:]])
        if flow_result:
            flow_text, consumed = flow_result
            property_parts = [tag, f"&{anchor}" if anchor else None, flow_text]
            node = make_scalar_node(
                " ".join(part for part in property_parts if part), anchors
            )
            return node, trimmed[consumed:]
    if flow_result := collect_flow_text(trimmed):
        flow_text, consumed = flow_result
        return make_scalar_node(flow_text, anchors), trimmed[consumed:]
    first_header, _ = split_inline_comment(first_line)
    if block_header := parse_block_scalar_header(first_header):
        style_char, chomping, indent_indicator = block_header
        scalar_base_indent = first_indent
        if indent_indicator is not None and first_indent >= indent and indent:
            scalar_base_indent = max(indent - 1, 0)
        elif indent_indicator is not None and first_indent > indent:
            scalar_base_indent = max(indent - 1, 0)
        block_node = ScalarNode(None, style=style_char)
        block_node.chomping = chomping
        block_node.indent_indicator = indent_indicator
        block_node.block_header = first_header
        block_node.lines, next_index = parse_block_scalar_lines(
            trimmed,
            1,
            scalar_base_indent,
            indent_indicator,
            allow_same_indent=first_indent == 0,
        )
        block_node.value = block_scalar_value(
            style_char, block_node.lines, chomping=chomping
        )
        return block_node, trimmed[next_index:]
    if is_sequence_entry(first_line):
        from .sequence_parser import parse_sequence

        return parse_sequence(lines, indent, anchors=anchors)
    if find_top_level_colon(first_line) == -1 and not is_explicit_key_entry(
        first_line
    ):
        first_value, first_comment = split_inline_comment(first_line)
        scalar_lines = [first_value]
        scalar_has_comment = first_comment is not None
        consumed = 1
        for line in trimmed[1:]:
            line_indent = indentation_width(line)
            if not line.strip():
                scalar_lines.append("")
                consumed += 1
                continue
            line_text = line.strip()
            if scalar_has_comment:
                break
            if line_indent < first_indent:
                break
            if (
                find_top_level_colon(line_text) != -1
                or is_sequence_entry(line_text)
                or is_explicit_key_entry(line_text)
            ):
                break
            line_value, line_comment = split_inline_comment(line_text)
            scalar_lines.append(line_value)
            scalar_has_comment = line_comment is not None
            consumed += 1
        return make_scalar_node(
            fold_plain_block_lines(scalar_lines), anchors
        ), trimmed[consumed:]
    else:
        from .mapping_parser import parse_mapping

        return parse_mapping(lines, indent, anchors=anchors)


def skip_blank_and_comment(lines: list):
    """
    Return lines starting with the first non-blank, non-comment line.
    """
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if (
            not stripped
            or lines[i].lstrip().startswith("#")
            or stripped.startswith("%")
        ):
            i += 1
        else:
            break
    return lines[i:]
