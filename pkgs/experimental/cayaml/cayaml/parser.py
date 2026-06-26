"""
parser.py - YAML parser for Cayaml (Swarmauri's Canon YAML)

This minimal parser tokenizes YAML input and builds an AST (using node classes from ast_nodes.py).
It preserves basic metadata such as document markers and comments.
Advanced features (anchors, aliases, block styles, etc.) can be added by expanding these functions.

This module exposes two internal functions:
  - _internal_load(yaml_str): Returns an AST representing the YAML input.
  - _internal_to_ast(data): Converts plain Python data into an AST.
"""

import math
from .ast_nodes import YamlStream, DocumentNode, MappingNode, SequenceNode, ScalarNode


def split_inline_comment(text: str) -> tuple[str, str | None]:
    """Split a YAML value from its inline comment while respecting quotes."""
    in_quote = False
    quote_char = ""
    escape = False

    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if char == "\\" and in_quote:
            escape = True
            continue
        if in_quote:
            if char == quote_char:
                in_quote = False
            continue
        if char in ("'", '"'):
            in_quote = True
            quote_char = char
            continue
        if char == "#" and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip(), text[index:].strip()

    return text.strip(), None


def split_tag_anchor_prefix(text: str) -> tuple[str | None, str | None, str]:
    """Return tag, anchor, and remaining scalar text from a YAML value."""
    tag = None
    anchor = None
    parts = text.strip().split()

    while parts and (parts[0].startswith("!") or parts[0].startswith("&")):
        part = parts.pop(0)
        if part.startswith("&"):
            anchor = part[1:]
        else:
            tag = part

    return tag, anchor, " ".join(parts)


def parse_scalar(value: str):
    """
    Convert a scalar string into int, float, bool, None, or leave as string.
    This function also strips quotes if present.
    """
    value = value.strip()
    # Remove quotes if present:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    lower = value.lower()
    # Handle booleans
    if lower == "true":
        return True
    if lower == "false":
        return False

    # Handle null
    if lower in ("null", "~"):
        return None

    # Handle special float values
    if lower in (".inf", "+.inf"):
        return math.inf
    if lower == "-.inf":
        return -math.inf
    if lower == ".nan":
        return math.nan

    # Try to parse int (base=0 helps with 0x, 0o, etc.)
    try:
        return int(value, 0)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    return " ".join(value.split())


def block_scalar_value(style: str, lines: list[str]) -> str:
    """Convert captured block scalar lines to their plain scalar value."""
    if style == "|":
        return "\n".join(lines) + "\n"

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


def make_scalar_node(value: str, anchors: dict[str, object]) -> ScalarNode:
    """Create a scalar node, resolving tags, anchors, and aliases."""
    tag, anchor, scalar_text = split_tag_anchor_prefix(value)
    if scalar_text.startswith("*"):
        alias = scalar_text[1:]
        target = anchors.get(alias)
        if isinstance(target, ScalarNode):
            node = ScalarNode(target.value, style=target.style)
            node.lines = list(target.lines) if target.lines is not None else None
            node.tag = target.tag
        else:
            node = ScalarNode(target)
        node.alias_of = alias
    else:
        node = ScalarNode(parse_scalar(scalar_text))
    node.tag = tag or node.tag
    node.anchor = anchor
    if anchor:
        anchors[anchor] = node
    return node


def assign_node_metadata(
    node, tag: str | None = None, anchor: str | None = None, anchors=None
):
    """Attach tag/anchor metadata and register anchored nodes."""
    if tag:
        node.tag = tag
    if anchor:
        node.anchor = anchor
        if anchors is not None:
            anchors[anchor] = node
    return node


def _internal_parse_stream(yaml_str: str) -> YamlStream:
    """
    Tokenize and parse a YAML string, returning a YamlStream (which may have multiple DocumentNodes).
    """
    lines = yaml_str.splitlines()
    return parse_stream(lines)


def _internal_load(yaml_str: str):
    """
    Parse a YAML string and return an AST.
    If there is only one document, return that DocumentNode;
    otherwise, return a YamlStream containing multiple DocumentNodes.
    """
    lines = yaml_str.splitlines()
    stream = parse_stream(lines)
    if len(stream.documents) == 1:
        return stream.documents[0]
    return stream


def _internal_to_ast(data):
    """
    Convert plain Python data (dict, list, or scalar) into our AST.
    """
    from .ast_nodes import MappingNode, SequenceNode, ScalarNode

    if isinstance(data, dict):
        node = MappingNode()
        for key, value in data.items():
            key_node = ScalarNode(key)
            value_node = _internal_to_ast(value)
            node.add_pair(key_node, value_node)
        return node
    elif isinstance(data, list):
        node = SequenceNode()
        for item in data:
            node.add_item(_internal_to_ast(item))
        return node
    else:
        return ScalarNode(data)


def parse_stream(lines: list) -> YamlStream:
    """
    Parse the entire YAML stream (which may contain multiple documents).
    Returns a YamlStream object containing DocumentNode(s).
    """
    stream = YamlStream()
    i = 0
    n = len(lines)
    anchors = {}

    while i < n:
        # Skip any leading blank lines
        while i < n and (not lines[i].strip() or lines[i].strip().startswith("%")):
            i += 1
        if i >= n:
            break

        doc = DocumentNode()
        line = lines[i].strip()

        # Check if we see a doc start marker
        if line.startswith("---"):
            doc.has_doc_start = True
            i += 1

        # Collect lines for *this* document until we see '...' or '---'
        doc_lines = []
        while i < n:
            curr = lines[i].rstrip("\n")
            curr_strip = curr.strip()
            if curr_strip.startswith("..."):
                doc.has_doc_end = True
                i += 1
                break
            if curr_strip.startswith("---"):
                # Start of next doc
                break
            doc_lines.append(curr)
            i += 1

        while doc_lines and (
            doc_lines[0].strip().startswith("%")
            or (doc_lines[0].strip().startswith("!") and ":" not in doc_lines[0])
        ):
            doc_lines.pop(0)

        # If we have lines for this document, parse them as a block
        if doc_lines:
            doc.root, _ = parse_block(doc_lines, indent=0, anchors=anchors)
        stream.add_document(doc)

    return stream


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
    if first_line.startswith("-"):
        return parse_sequence(lines, indent, anchors=anchors)
    else:
        return parse_mapping(lines, indent, anchors=anchors)


def parse_mapping(lines: list, indent: int, anchors=None):
    """
    Parse a block of lines as a mapping.
    Returns (MappingNode, remaining_lines).
    """
    anchors = anchors if anchors is not None else {}
    mapping = MappingNode()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        line_strip = line.strip()

        # Check current indentation of this line
        current_indent = len(line) - len(line.lstrip())

        # Blank lines separate entries at the current level.
        if not line_strip:
            i += 1
            continue

        # If line has less indent, we break out of this mapping.
        if current_indent < indent:
            break

        # If it's a full-line comment at this level, store as leading comment
        if line.lstrip().startswith("#"):
            mapping.leading_comments.append(line_strip)
            i += 1
            continue

        # If no colon, we presumably have reached a new block or item
        if ":" not in line_strip:
            break

        # Split key : value
        key_part, _, value_part = line_strip.partition(":")
        key_node = ScalarNode(parse_scalar(key_part.strip()))

        # Move to next line to see if there's nested content or block scalars
        i += 1
        raw_value, inline_comment = split_inline_comment(value_part.strip())
        tag, anchor, remaining_value = split_tag_anchor_prefix(raw_value)
        raw_value = remaining_value
        if inline_comment:
            key_node.trailing_comments.append(inline_comment)

        if key_node.value == "<<":
            merge_node = parse_merge_value(raw_value, anchors)
            mapping.merges.extend(
                merge_node.items
                if isinstance(merge_node, SequenceNode)
                else [merge_node]
            )
            continue

        # -- Block scalar check (| or >) --
        if raw_value in ("|", ">"):
            style_char = raw_value  # '|' or '>'
            block_node = ScalarNode(None, style=style_char)
            block_node.lines = []

            # Determine the indentation level of the block content from the
            # first line following the block indicator. YAML treats that
            # indentation as significant for the entire block, so we capture it
            # and strip exactly that amount from each subsequent line.

            block_indent = None
            while i < n:
                next_line = lines[i]
                next_line_indent = len(next_line) - len(next_line.lstrip())
                if next_line_indent <= current_indent or not next_line.strip():
                    break
                if block_indent is None:
                    block_indent = next_line_indent
                if next_line_indent < block_indent:
                    break
                block_node.lines.append(next_line[block_indent:])
                i += 1

            block_node.value = block_scalar_value(style_char, block_node.lines)
            value_node = block_node
            assign_node_metadata(value_node, tag=tag, anchor=anchor, anchors=anchors)

        # If value part is empty => The actual value is on subsequent lines
        elif not raw_value:
            nested_lines = []
            while i < n:
                nl = lines[i]
                nl_indent = len(nl) - len(nl.lstrip())
                if nl_indent <= current_indent or not nl.strip():
                    break
                nested_lines.append(nl)
                i += 1

            if nested_lines:
                value_node, _ = parse_block(
                    nested_lines, indent=current_indent + 1, anchors=anchors
                )
                assign_node_metadata(
                    value_node, tag=tag, anchor=anchor, anchors=anchors
                )
            else:
                value_node = ScalarNode("")
                assign_node_metadata(
                    value_node, tag=tag, anchor=anchor, anchors=anchors
                )
        else:
            # Normal scalar
            value_node = make_scalar_node(
                " ".join(
                    part
                    for part in (tag, f"&{anchor}" if anchor else None, raw_value)
                    if part
                ),
                anchors,
            )

        mapping.add_pair(key_node, value_node)

    remaining = lines[i:]
    return mapping, remaining


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
        current_indent = len(line) - len(line.lstrip())

        if not line_strip or current_indent < indent:
            break

        if line.lstrip().startswith("#"):
            sequence.leading_comments.append(line_strip)
            i += 1
            continue

        if not line_strip.startswith("-"):
            break

        # Remove leading dash
        dash_part, inline_comment = split_inline_comment(line_strip[1:].strip())
        i += 1
        tag, anchor, remaining_value = split_tag_anchor_prefix(dash_part)
        dash_part = remaining_value

        # If dash_part is '|' or '>', we have a block scalar in a sequence item
        if dash_part in ("|", ">"):
            style_char = dash_part
            block_node = ScalarNode(None, style=style_char)
            block_node.lines = []

            # As with mappings, determine the indentation for the block scalar
            # from the first line that follows the indicator. Each subsequent
            # line must be at least that indented; anything less signals the end
            # of the block.

            block_indent = None
            while i < n:
                nxt = lines[i]
                nxt_indent = len(nxt) - len(nxt.lstrip())
                if nxt_indent <= current_indent or not nxt.strip():
                    break
                if block_indent is None:
                    block_indent = nxt_indent
                if nxt_indent < block_indent:
                    break
                block_node.lines.append(nxt[block_indent:])
                i += 1

            block_node.value = block_scalar_value(style_char, block_node.lines)
            assign_node_metadata(block_node, tag=tag, anchor=anchor, anchors=anchors)
            sequence.add_item(block_node)

        elif not dash_part:
            # Possibly nested structure
            nested_lines = []
            while i < n:
                nested_line = lines[i]
                nested_indent = len(nested_line) - len(nested_line.lstrip())
                if nested_indent <= current_indent or not nested_line.strip():
                    break
                nested_lines.append(nested_line)
                i += 1

            if nested_lines:
                item_node, _ = parse_block(
                    nested_lines, indent=current_indent + 1, anchors=anchors
                )
                assign_node_metadata(item_node, tag=tag, anchor=anchor, anchors=anchors)
            else:
                item_node = ScalarNode("")
                assign_node_metadata(item_node, tag=tag, anchor=anchor, anchors=anchors)
            sequence.add_item(item_node)
        else:
            # Normal scalar or inline text after '-'
            item_node = make_scalar_node(
                " ".join(
                    part
                    for part in (tag, f"&{anchor}" if anchor else None, dash_part)
                    if part
                ),
                anchors,
            )
            if inline_comment:
                item_node.trailing_comments.append(inline_comment)
            sequence.add_item(item_node)

    remaining = lines[i:]
    return sequence, remaining


def skip_blank_and_comment(lines: list):
    """
    Return the subset of lines starting with the first non-blank, non-comment line.
    """
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if (
            not stripped
            or lines[i].lstrip().startswith("#")
            or stripped.startswith("%")
            or (stripped.startswith("!") and ":" not in stripped)
        ):
            i += 1
        else:
            break
    return lines[i:]


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
        return anchors.get(raw_value[1:], ScalarNode(None))
    return make_scalar_node(raw_value, anchors)
