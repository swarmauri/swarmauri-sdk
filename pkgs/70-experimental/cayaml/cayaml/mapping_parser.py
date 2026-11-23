"""Internal YAML parser support for Cayaml."""

from .ast_nodes import MappingNode, ScalarNode
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
    merge_nodes_from,
    new_container_placeholder,
)
from .errors import YamlParseError
from .explicit_mapping import parse_explicit_mapping_entry
from .flow import fold_plain_continuation
from .mapping_keys import add_mapping_pair
from .properties import split_tag_anchor_prefix
from .scanner import (
    find_top_level_colon,
    has_unclosed_quote,
    indentation_width,
    is_balanced_flow,
    is_explicit_key_entry,
    is_sequence_entry,
    split_inline_comment,
)


def parse_mapping(lines: list, indent: int, anchors=None):
    """
    Parse a block of lines as a mapping.
    Returns (MappingNode, remaining_lines).
    """
    anchors = anchors if anchors is not None else {}
    mapping = MappingNode()
    i = 0
    n = len(lines)
    entry_indent = None

    while i < n:
        line = lines[i]
        line_strip = line.strip()

        # Check current indentation of this line
        current_indent = indentation_width(line)

        # Blank lines separate entries at the current level.
        if not line_strip:
            i += 1
            continue

        # If line has less indent, we break out of this mapping.
        if current_indent < indent:
            break
        if line.startswith("\t") and find_top_level_colon(line_strip) != -1:
            raise YamlParseError("tab indentation is not allowed")

        # If it's a full-line comment at this level, store as leading comment
        if line.lstrip().startswith("#"):
            mapping.leading_comments.append(line_strip)
            i += 1
            continue

        if line_strip.startswith(("?\t", "? \t")):
            raise YamlParseError("invalid tab-separated explicit key")

        if entry_indent is None:
            entry_indent = current_indent
        elif current_indent != entry_indent:
            if current_indent < entry_indent:
                break
            raise YamlParseError("invalid mapping indentation")

        if is_explicit_key_entry(line_strip):
            i = parse_explicit_mapping_entry(
                lines, i, current_indent, anchors, mapping
            )
            continue

        commentless_line, _ = split_inline_comment(line_strip)
        colon_index = find_top_level_colon(commentless_line)

        # If no top-level colon, we presumably have reached a new block or item
        if colon_index == -1:
            raise YamlParseError(f"invalid mapping entry: {line_strip}")

        # Split key : value
        key_part = line_strip[:colon_index]
        value_part = line[current_indent + colon_index + 1 :]
        key_node = make_scalar_node(key_part.strip(), anchors)

        # Move to next line to see if there's nested content or block scalars
        i += 1
        raw_value, inline_comment = split_inline_comment(value_part.lstrip())
        tag, anchor, remaining_value = split_tag_anchor_prefix(raw_value)
        raw_value = remaining_value
        if inline_comment:
            key_node.trailing_comments.append(inline_comment)
        if (
            raw_value
            and not raw_value.startswith(("[", "{"))
            and find_top_level_colon(raw_value) != -1
        ):
            raise YamlParseError(
                "plain mapping value contains a mapping colon"
            )

        key_value = (
            key_node.value if isinstance(key_node, ScalarNode) else None
        )
        if key_value == "<<":
            mapping.merges.extend(merge_nodes_from(raw_value, anchors))
            continue

        # -- Block scalar check (| or >) --
        if block_header := parse_block_scalar_header(raw_value):
            style_char, chomping, indent_indicator = block_header
            block_node = ScalarNode(None, style=style_char)
            block_node.chomping = chomping
            block_node.indent_indicator = indent_indicator
            block_node.block_header = raw_value
            block_node.lines = []

            block_node.lines, i = parse_block_scalar_lines(
                lines, i, current_indent, indent_indicator
            )
            block_node.value = block_scalar_value(
                style_char, block_node.lines, chomping=chomping
            )
            value_node = block_node
            assign_node_metadata(
                value_node, tag=tag, anchor=anchor, anchors=anchors
            )

        # If value part is empty => The actual value is on subsequent lines
        elif not raw_value:
            nested_lines = []
            if i < n and is_sequence_entry(lines[i].lstrip()):
                while i < n:
                    nl = lines[i]
                    nl_indent = indentation_width(nl)
                    nl_strip = nl.strip()
                    if not nl_strip:
                        break
                    if nl_indent == current_indent and not is_sequence_entry(
                        nl_strip
                    ):
                        break
                    if nl_indent < current_indent:
                        break
                    nested_lines.append(nl)
                    i += 1
            else:
                while i < n:
                    nl = lines[i]
                    nl_indent = indentation_width(nl)
                    if not nl.strip():
                        if nested_lines:
                            nested_lines.append(nl)
                            i += 1
                            continue
                        break
                    nl_strip = nl.strip()
                    if nl_indent <= current_indent:
                        property_only_prefix = False
                        if nested_lines:
                            first_nested = nested_lines[0].strip()
                            prop_tag, prop_anchor, prop_rest = (
                                split_tag_anchor_prefix(first_nested)
                            )
                            property_only_prefix = (
                                prop_tag or prop_anchor
                            ) and not prop_rest
                        same_indent_sequence = (
                            nl_indent == current_indent
                            and is_sequence_entry(nl_strip)
                            and (
                                property_only_prefix
                                or any(
                                    is_sequence_entry(item.strip())
                                    for item in nested_lines
                                )
                            )
                        )
                        if same_indent_sequence:
                            nested_lines.append(nl)
                            i += 1
                            continue
                        break
                    nested_lines.append(nl)
                    i += 1

            if nested_lines:
                if anchor and nested_scalar_property(nested_lines):
                    raise YamlParseError(
                        "nested scalar has conflicting anchor"
                    )
                placeholder = None
                if anchor:
                    placeholder = new_container_placeholder(nested_lines)
                    assign_node_metadata(
                        placeholder, tag=tag, anchor=anchor, anchors=anchors
                    )
                child_indent = nested_child_indent(
                    nested_lines, current_indent
                )
                from .block_parser import parse_block

                value_node, rest = parse_block(
                    nested_lines, indent=child_indent, anchors=anchors
                )
                if rest:
                    raise YamlParseError("invalid nested mapping indentation")
                if placeholder is not None:
                    value_node = materialize_anchored_container(
                        value_node, placeholder
                    )
                else:
                    assign_node_metadata(
                        value_node, tag=tag, anchor=anchor, anchors=anchors
                    )
            else:
                value_node = make_empty_node(
                    tag=tag, anchor=anchor, anchors=anchors
                )
        else:
            continuation_lines = []
            while i < n:
                candidate_value = fold_plain_continuation(
                    raw_value, continuation_lines
                )
                if raw_value.startswith(("[", "{")) and is_balanced_flow(
                    candidate_value
                ):
                    break
                next_line = lines[i]
                next_indent = indentation_width(next_line)
                next_strip = next_line.strip()
                if not next_strip:
                    lookahead = i + 1
                    while lookahead < n and not lines[lookahead].strip():
                        lookahead += 1
                    if (
                        lookahead < n
                        and indentation_width(lines[lookahead])
                        > current_indent
                    ):
                        continuation_lines.append("")
                        i += 1
                        continue
                    break
                if raw_value.startswith(("[", "{")):
                    if next_indent < current_indent:
                        break
                    if next_indent == current_indent and next_strip not in (
                        "]",
                        "}",
                    ):
                        raise YamlParseError(
                            "invalid flow collection indentation"
                        )
                elif next_indent <= current_indent:
                    break
                if (
                    not raw_value.startswith(("[", "{"))
                    and find_top_level_colon(next_strip) != -1
                ):
                    break
                if not raw_value.startswith(
                    ("[", "{")
                ) and next_strip.startswith(("-", "?", ":")):
                    break
                next_value, next_comment = split_inline_comment(next_strip)
                if next_comment and not raw_value.startswith(("[", "{")):
                    lookahead = i + 1
                    while lookahead < n and not lines[lookahead].strip():
                        lookahead += 1
                    if (
                        lookahead < n
                        and indentation_width(lines[lookahead])
                        > current_indent
                    ):
                        raise YamlParseError(
                            "plain scalar continuation after comment"
                        )
                continuation_lines.append(next_value)
                i += 1
                if not has_unclosed_quote(
                    raw_value
                ) and not raw_value.startswith(("[", "{")):
                    continue
                if not raw_value.startswith(
                    ("[", "{")
                ) and not has_unclosed_quote(
                    fold_plain_continuation(raw_value, continuation_lines)
                ):
                    break
            raw_value = fold_plain_continuation(raw_value, continuation_lines)
            # Normal scalar
            value_node = make_scalar_node(
                " ".join(
                    part
                    for part in (
                        tag,
                        f"&{anchor}" if anchor else None,
                        raw_value,
                    )
                    if part
                ),
                anchors,
            )

        add_mapping_pair(mapping, key_node, value_node)

    remaining = lines[i:]
    return mapping, remaining


def nested_scalar_property(nested_lines: list[str]) -> bool:
    """Return True for property-only nested scalar content."""
    first = nested_lines[0].strip()
    first_tag, first_anchor, first_rest = split_tag_anchor_prefix(first)
    if not (first_tag or first_anchor) or not first_rest:
        return False
    return not (
        first_rest.startswith(("[", "{", "|", ">"))
        or is_sequence_entry(first_rest)
        or find_top_level_colon(first_rest) != -1
    )


def nested_child_indent(nested_lines: list[str], current_indent: int) -> int:
    """Return the parser indent for a nested mapping value block."""
    first_indent = indentation_width(nested_lines[0])
    if (
        nested_lines[0].lstrip().startswith("-")
        and first_indent == current_indent
    ):
        return current_indent
    first_tag, first_anchor, first_rest = split_tag_anchor_prefix(
        nested_lines[0].strip()
    )
    if (
        (first_tag or first_anchor)
        and not first_rest
        and len(nested_lines) > 1
    ):
        second_indent = indentation_width(nested_lines[1])
        if second_indent < first_indent:
            return current_indent + 1
    return first_indent
