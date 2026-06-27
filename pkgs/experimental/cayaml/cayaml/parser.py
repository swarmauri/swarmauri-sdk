"""
parser.py - YAML parser for Cayaml (Swarmauri's Canon YAML)

This parser tokenizes YAML input and builds an AST.
It preserves basic metadata such as document markers and comments.

This module exposes two internal functions:
  - _internal_load(yaml_str): Returns an AST representing the YAML input.
  - _internal_to_ast(data): Converts plain Python data into an AST.
"""

import math
from .ast_nodes import (
    YamlStream,
    DocumentNode,
    MappingNode,
    SequenceNode,
    ScalarNode,
)


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


def parse_quoted_scalar(value: str):
    """Decode YAML single- and double-quoted scalar text."""
    if len(value) < 2:
        return value
    quote = value[0]
    inner = value[1:-1]
    if quote == "'":
        return inner.replace("''", "'")

    escapes = {
        "0": "\0",
        "a": "\a",
        "b": "\b",
        "t": "\t",
        "\t": "\t",
        "n": "\n",
        "v": "\v",
        "f": "\f",
        "r": "\r",
        "e": "\x1b",
        '"': '"',
        "/": "/",
        "\\": "\\",
        " ": " ",
    }
    result = []
    i = 0
    while i < len(inner):
        char = inner[i]
        if char != "\\":
            result.append(char)
            i += 1
            continue
        i += 1
        if i >= len(inner):
            result.append("\\")
            break
        escape = inner[i]
        if escape in escapes:
            result.append(escapes[escape])
            i += 1
        elif escape == "x" and i + 2 < len(inner):
            result.append(chr(int(inner[i + 1 : i + 3], 16)))
            i += 3
        elif escape == "u" and i + 4 < len(inner):
            result.append(chr(int(inner[i + 1 : i + 5], 16)))
            i += 5
        elif escape == "U" and i + 8 < len(inner):
            result.append(chr(int(inner[i + 1 : i + 9], 16)))
            i += 9
        else:
            result.append(escape)
            i += 1
    return "".join(result)


def parse_scalar(value: str, tag: str | None = None):
    """
    Convert a scalar string into int, float, bool, None, or leave as string.
    This function also strips quotes if present.
    """
    value = value.strip()
    # Remove quotes if present:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        unquoted = parse_quoted_scalar(value)
    else:
        unquoted = value

    if tag in ("!!str", "tag:yaml.org,2002:str"):
        return unquoted
    if tag in ("!!int", "tag:yaml.org,2002:int"):
        return int(str(unquoted).replace("_", ""), 0)
    if tag in ("!!float", "tag:yaml.org,2002:float"):
        return float(str(unquoted).replace("_", ""))
    if tag in ("!!bool", "tag:yaml.org,2002:bool"):
        return str(unquoted).lower() == "true"
    if tag in ("!!null", "tag:yaml.org,2002:null"):
        return None

    if unquoted != value:
        return unquoted

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
        return int(value.replace("_", ""), 0)
    except ValueError:
        pass

    # Try float
    try:
        return float(value.replace("_", ""))
    except ValueError:
        pass

    return " ".join(value.split())


def block_scalar_value(
    style: str, lines: list[str], chomping: str | None = None
) -> str:
    """Convert captured block scalar lines to their plain scalar value."""
    if style == "|":
        value = "\n".join(lines) + "\n"
    else:
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
        value = "\n".join(folded).rstrip("\n") + "\n"

    if chomping == "-":
        return value.rstrip("\n")
    if chomping == "+":
        return value
    return value.rstrip("\n") + "\n"


def parse_block_scalar_header(raw_value: str) -> tuple[str, str | None] | None:
    """Parse block scalar style/chomping indicators from |, >, |-, >+, etc."""
    if not raw_value or raw_value[0] not in ("|", ">"):
        return None
    style = raw_value[0]
    chomping = None
    for char in raw_value[1:]:
        if char in ("+", "-"):
            chomping = char
        elif char.isdigit():
            continue
        else:
            return None
    return style, chomping


def split_top_level(text: str, delimiter: str) -> list[str]:
    """Split on a delimiter outside quotes and flow brackets."""
    parts = []
    start = 0
    depth = 0
    quote = ""
    escape = False

    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char in "[{":
            depth += 1
            continue
        if char in "]}":
            depth -= 1
            continue
        if char == delimiter and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1

    parts.append(text[start:].strip())
    return parts


def find_top_level_colon(text: str) -> int:
    """Return the index of the first top-level mapping colon, or -1."""
    depth = 0
    quote = ""
    escape = False
    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char in "[{":
            depth += 1
            continue
        if char in "]}":
            depth -= 1
            continue
        if char == ":" and depth == 0:
            return index
    return -1


def parse_flow_node(text: str, anchors: dict[str, object]):
    """Parse a flow-style sequence or mapping into AST nodes."""
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        sequence = SequenceNode()
        sequence.flow_style = True
        inner = text[1:-1].strip()
        if inner:
            for item in split_top_level(inner, ","):
                if item:
                    sequence.add_item(make_scalar_node(item, anchors))
        return sequence

    if text.startswith("{") and text.endswith("}"):
        mapping = MappingNode()
        mapping.flow_style = True
        inner = text[1:-1].strip()
        if inner:
            for item in split_top_level(inner, ","):
                colon = find_top_level_colon(item)
                if colon == -1:
                    key_text = item
                    value_text = ""
                else:
                    key_text = item[:colon].strip()
                    value_text = item[colon + 1 :].strip()
                mapping.add_pair(
                    make_scalar_node(key_text, anchors),
                    make_scalar_node(value_text, anchors),
                )
        return mapping

    return None


def make_scalar_node(value: str, anchors: dict[str, object]) -> ScalarNode:
    """Create a scalar node, resolving tags, anchors, and aliases."""
    tag, anchor, scalar_text = split_tag_anchor_prefix(value)
    if scalar_text.startswith("*"):
        alias = scalar_text[1:]
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
    assign_node_metadata(node, tag=tag, anchor=anchor, anchors=anchors)
    return node


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


def new_container_placeholder(nested_lines: list[str]):
    """Create a container placeholder matching the nested block shape."""
    trimmed = skip_blank_and_comment(nested_lines)
    if trimmed and trimmed[0].lstrip().startswith("-"):
        return SequenceNode()
    return MappingNode()


def parse_block_scalar_lines(
    lines: list[str], start: int, current_indent: int, style_char: str
):
    """Capture block scalar lines and return (lines, next_index)."""
    block_lines = []
    block_indent = None
    i = start
    while i < len(lines):
        next_line = lines[i]
        if not next_line.strip():
            if block_indent is not None:
                block_lines.append("")
            i += 1
            continue
        next_line_indent = len(next_line) - len(next_line.lstrip())
        if next_line_indent <= current_indent:
            break
        if block_indent is None:
            block_indent = next_line_indent
        if next_line_indent < block_indent:
            break
        block_lines.append(next_line[block_indent:])
        i += 1
    return block_lines, i


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
    Tokenize and parse YAML into a YamlStream.
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
        while i < n and (
            not lines[i].strip() or lines[i].strip().startswith("%")
        ):
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
            or (
                doc_lines[0].strip().startswith("!")
                and ":" not in doc_lines[0]
            )
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

        if line_strip.startswith("?"):
            key_text = line_strip[1:].strip()
            i += 1
            if i >= n:
                value_node = ScalarNode("")
            else:
                value_line = lines[i]
                value_indent = len(value_line) - len(value_line.lstrip())
                value_strip = value_line.strip()
                if (
                    value_indent != current_indent
                    or not value_strip.startswith(":")
                ):
                    value_node = ScalarNode("")
                else:
                    i += 1
                    value_text, inline_comment = split_inline_comment(
                        value_strip[1:].strip()
                    )
                    value_node = make_scalar_node(value_text, anchors)
                    if inline_comment:
                        value_node.trailing_comments.append(inline_comment)
            mapping.add_pair(make_scalar_node(key_text, anchors), value_node)
            continue

        colon_index = find_top_level_colon(line_strip)

        # If no top-level colon, we presumably have reached a new block or item
        if colon_index == -1:
            break

        # Split key : value
        key_part = line_strip[:colon_index]
        value_part = line_strip[colon_index + 1 :]
        key_node = make_scalar_node(key_part.strip(), anchors)

        # Move to next line to see if there's nested content or block scalars
        i += 1
        raw_value, inline_comment = split_inline_comment(value_part.strip())
        tag, anchor, remaining_value = split_tag_anchor_prefix(raw_value)
        raw_value = remaining_value
        if inline_comment:
            key_node.trailing_comments.append(inline_comment)

        key_value = (
            key_node.value if isinstance(key_node, ScalarNode) else None
        )
        if key_value == "<<":
            merge_node = parse_merge_value(raw_value, anchors)
            mapping.merges.extend(
                merge_node.items
                if isinstance(merge_node, SequenceNode)
                else [merge_node]
            )
            continue

        # -- Block scalar check (| or >) --
        if block_header := parse_block_scalar_header(raw_value):
            style_char, chomping = block_header
            block_node = ScalarNode(None, style=style_char)
            block_node.chomping = chomping
            block_node.lines = []

            block_node.lines, i = parse_block_scalar_lines(
                lines, i, current_indent, style_char
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
            while i < n:
                nl = lines[i]
                nl_indent = len(nl) - len(nl.lstrip())
                if nl_indent <= current_indent or not nl.strip():
                    break
                nested_lines.append(nl)
                i += 1

            if nested_lines:
                placeholder = None
                if anchor:
                    placeholder = new_container_placeholder(nested_lines)
                    assign_node_metadata(
                        placeholder, tag=tag, anchor=anchor, anchors=anchors
                    )
                value_node, _ = parse_block(
                    nested_lines, indent=current_indent + 1, anchors=anchors
                )
                if placeholder is not None:
                    value_node = materialize_anchored_container(
                        value_node, placeholder
                    )
                else:
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
                    for part in (
                        tag,
                        f"&{anchor}" if anchor else None,
                        raw_value,
                    )
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
        dash_part, inline_comment = split_inline_comment(
            line_strip[1:].strip()
        )
        i += 1
        tag, anchor, remaining_value = split_tag_anchor_prefix(dash_part)
        dash_part = remaining_value

        # Block scalar sequence item.
        if block_header := parse_block_scalar_header(dash_part):
            style_char, chomping = block_header
            block_node = ScalarNode(None, style=style_char)
            block_node.chomping = chomping
            block_node.lines = []

            block_node.lines, i = parse_block_scalar_lines(
                lines, i, current_indent, style_char
            )
            block_node.value = block_scalar_value(
                style_char, block_node.lines, chomping=chomping
            )
            assign_node_metadata(
                block_node, tag=tag, anchor=anchor, anchors=anchors
            )
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
                placeholder = None
                if anchor:
                    placeholder = new_container_placeholder(nested_lines)
                    assign_node_metadata(
                        placeholder, tag=tag, anchor=anchor, anchors=anchors
                    )
                item_node, _ = parse_block(
                    nested_lines, indent=current_indent + 1, anchors=anchors
                )
                if placeholder is not None:
                    item_node = materialize_anchored_container(
                        item_node, placeholder
                    )
                else:
                    assign_node_metadata(
                        item_node, tag=tag, anchor=anchor, anchors=anchors
                    )
            else:
                item_node = ScalarNode("")
                assign_node_metadata(
                    item_node, tag=tag, anchor=anchor, anchors=anchors
                )
            sequence.add_item(item_node)
        elif find_top_level_colon(dash_part) != -1:
            item_lines = [" " * (current_indent + 2) + dash_part]
            while i < n:
                nested_line = lines[i]
                nested_indent = len(nested_line) - len(nested_line.lstrip())
                if nested_indent <= current_indent or not nested_line.strip():
                    break
                item_lines.append(nested_line)
                i += 1

            placeholder = None
            if anchor:
                placeholder = MappingNode()
                assign_node_metadata(
                    placeholder, tag=tag, anchor=anchor, anchors=anchors
                )
            item_node, _ = parse_mapping(
                item_lines, indent=current_indent + 2, anchors=anchors
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
        else:
            # Normal scalar or inline text after '-'
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
