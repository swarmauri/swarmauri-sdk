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
    This function strips quotes if present.
    """
    value = value.strip()
    # Remove quotes if present.
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    
    lower = value.lower()
    # Handle booleans.
    if lower == "true":
        return True
    if lower == "false":
        return False
    # Handle null.
    if lower in ["null", "~"]:
        return None

    # Handle special float values explicitly.
    if lower in [".inf", "+.inf"]:
        return math.inf
    if lower == "-.inf":
        return -math.inf
    if lower == ".nan":
        return math.nan

    # Try to convert to int (using base=0 supports hex, octal, binary).
    try:
        return int(value, 0)
    except ValueError:
        pass

    # Try converting to float.
    try:
        return float(value)
    except ValueError:
        pass

    return value

def _internal_parse_stream(yaml_str: str) -> YamlStream:
    lines = yaml_str.splitlines()
    return parse_stream(lines)  # parse_stream is your existing logic

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
    Parse the entire YAML stream (which may contain multiple documents)
    into a YamlStream object.
    """
    stream = YamlStream()
    i = 0
    n = len(lines)
    while i < n:
        while i < n and lines[i].strip() == "":
            i += 1
        if i >= n:
            break

        doc = DocumentNode()
        line = lines[i].strip()
        if line.startswith("---"):
            doc.has_doc_start = True
            i += 1

        doc_lines = []
        while i < n:
            curr = lines[i]
            curr_strip = curr.strip()
            if curr_strip.startswith("..."):
                doc.has_doc_end = True
                i += 1
                break
            if curr_strip.startswith("---"):
                break
            doc_lines.append(curr)
            i += 1

        if doc_lines:
            doc.root, _ = parse_block(doc_lines, indent=0)
        stream.add_document(doc)
    return stream

def parse_block(lines: list, indent: int):
    """
    Decide whether the block is a mapping or a sequence,
    and parse accordingly.
    Returns a Node (MappingNode or SequenceNode) and any remaining lines.
    """
    if not lines:
        return None, lines

    for line in lines:
        if line.strip() == "":
            continue
        if line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("-"):
            return parse_sequence(lines, indent)
        else:
            return parse_mapping(lines, indent)
    return None, lines

def parse_mapping(lines: list, indent: int):
    """
    Parse a block of lines as a mapping.
    Returns a MappingNode and any remaining lines.
    """
    mapping = MappingNode()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        current_indent = len(line) - len(line.lstrip(" "))
        if line.strip() == "":
            i += 1
            continue
        if current_indent < indent:
            break

        if line.lstrip().startswith("#"):
            mapping.leading_comments.append(line.strip())
            i += 1
            continue

        if ":" not in line:
            break
        key_part, sep, value_part = line.strip().partition(":")
        key_node = ScalarNode(parse_scalar(key_part))
        if value_part.strip() == "":
            i += 1
            nested_lines = []
            while i < n and (len(lines[i]) - len(lines[i].lstrip(" "))) > current_indent:
                nested_lines.append(lines[i])
                i += 1
            if nested_lines:
                value_node, _ = parse_block(nested_lines, current_indent + 1)
            else:
                value_node = ScalarNode("")
        else:
            value_text = value_part.strip()
            value_node = ScalarNode(parse_scalar(value_text))
            i += 1
        mapping.add_pair(key_node, value_node)
    remaining = lines[i:]
    return mapping, remaining

def parse_sequence(lines: list, indent: int):
    """
    Parse a block of lines as a sequence.
    Returns a SequenceNode and any remaining lines.
    """
    sequence = SequenceNode()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent < indent:
            break
        stripped = line.lstrip()
        if not stripped.startswith("-"):
            break
        after_dash = stripped[1:].strip()
        if after_dash == "":
            i += 1
            nested_lines = []
            while i < n and (len(lines[i]) - len(lines[i].lstrip(" "))) > current_indent:
                nested_lines.append(lines[i])
                i += 1
            if nested_lines:
                item_node, _ = parse_block(nested_lines, current_indent + 1)
            else:
                item_node = ScalarNode("")
        else:
            item_node = ScalarNode(parse_scalar(after_dash))
            i += 1
        sequence.add_item(item_node)
    remaining = lines[i:]
    return sequence, remaining
