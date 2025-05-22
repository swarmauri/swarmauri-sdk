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

    return value


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

    while i < n:
        # Skip any leading blank lines
        while i < n and not lines[i].strip():
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

        # If we have lines for this document, parse them as a block
        if doc_lines:
            doc.root, _ = parse_block(doc_lines, indent=0)
        stream.add_document(doc)

    return stream


def parse_block(lines: list, indent: int):
    """
    Decide whether the block is a mapping or a sequence, then parse.
    Returns (Node, remaining_lines).
    """
    # Skip blank or comment lines to see what's next
    trimmed = skip_blank_and_comment(lines)
    if not trimmed:
        return None, []

    first_line = trimmed[0].lstrip()
    if first_line.startswith("-"):
        return parse_sequence(lines, indent)
    else:
        return parse_mapping(lines, indent)


def parse_mapping(lines: list, indent: int):
    """
    Parse a block of lines as a mapping.
    Returns (MappingNode, remaining_lines).
    """
    print("DEBUG parse_mapping lines:", repr(lines), "indent=", indent)
    mapping = MappingNode()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        line_strip = line.strip()

        # Check current indentation of this line
        current_indent = len(line) - len(line.lstrip())

        # If line is blank or has less indent, we break out of this mapping
        if not line_strip or current_indent < indent:
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
        raw_value = value_part.strip()

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

            value_node = block_node

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
                value_node, _ = parse_block(nested_lines, indent=current_indent + 1)
            else:
                value_node = ScalarNode("")
        else:
            # Normal scalar
            value_node = ScalarNode(parse_scalar(raw_value))

        mapping.add_pair(key_node, value_node)

    remaining = lines[i:]
    return mapping, remaining


def parse_sequence(lines: list, indent: int):
    """
    Parse a block of lines as a sequence.
    Returns (SequenceNode, remaining_lines).
    """
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
        dash_part = line_strip[1:].strip()  # everything after '-'
        i += 1

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
                item_node, _ = parse_block(nested_lines, indent=current_indent + 1)
            else:
                item_node = ScalarNode("")
            sequence.add_item(item_node)
        else:
            # Normal scalar or inline text after '-'
            item_node = ScalarNode(parse_scalar(dash_part))
            sequence.add_item(item_node)

    remaining = lines[i:]
    return sequence, remaining


def skip_blank_and_comment(lines: list):
    """
    Return the subset of lines starting with the first non-blank, non-comment line.
    """
    i = 0
    while i < len(lines):
        if not lines[i].strip() or lines[i].lstrip().startswith("#"):
            i += 1
        else:
            break
    return lines[i:]
