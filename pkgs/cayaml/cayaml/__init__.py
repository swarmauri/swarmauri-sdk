"""
Minimal YAML Parser and Unparser

This module provides a very basic YAML parser and unparser that supports a subset
of YAML syntax (mappings and sequences, with simple scalars). It uses only Python's
built-in libraries and is intended for simple use cases.

Usage:
    data = parse_yaml(yaml_string)
    yaml_string = unparse_yaml(data)
"""


def get_indent(line):
    """Return the number of leading spaces in a line."""
    return len(line) - len(line.lstrip(" "))


def parse_scalar(value):
    """Convert a scalar string into int, float, bool, None or leave as string."""
    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in ["null", "~"]:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_mapping(lines, indent):
    """Parse a block of lines representing a mapping."""
    mapping = {}
    while lines and get_indent(lines[0]) >= indent:
        if get_indent(lines[0]) != indent:
            break
        line = lines.pop(0)
        # Ignore comment lines
        if line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue  # Skip lines that do not look like key: value pairs
        key, _, value = line.strip().partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            # If no inline value, check if a nested block follows.
            if lines and get_indent(lines[0]) > indent:
                value, _ = parse_block(lines, get_indent(lines[0]))
            else:
                value = None
        else:
            value = parse_scalar(value)
        mapping[key] = value
    return mapping


def parse_list(lines, indent):
    """Parse a block of lines representing a list."""
    lst = []
    while (
        lines and get_indent(lines[0]) == indent and lines[0].lstrip().startswith("-")
    ):
        line = lines.pop(0)
        # Remove the dash marker and get the content.
        content = line.lstrip()[1:].strip()
        if content == "":
            # If nothing follows the dash, check for an indented block.
            if lines and get_indent(lines[0]) > indent:
                item, _ = parse_block(lines, get_indent(lines[0]))
            else:
                item = None
        else:
            item = parse_scalar(content)
            # If the next line is indented more, treat it as a nested block.
            if lines and get_indent(lines[0]) > indent:
                extra, _ = parse_block(lines, get_indent(lines[0]))
                # If the inline value is a mapping, merge the extra block.
                if isinstance(item, dict) and isinstance(extra, dict):
                    item.update(extra)
                else:
                    item = extra
        lst.append(item)
    return lst


def parse_block(lines, indent):
    """Determine if the current block is a list or mapping and parse accordingly."""
    if not lines:
        return None, lines
    # If the current line starts with a dash, treat as a list; otherwise, a mapping.
    if lines[0].lstrip().startswith("-"):
        result = parse_list(lines, indent)
    else:
        result = parse_mapping(lines, indent)
    return result, lines


def parse_yaml(yaml_str):
    """
    Parse a YAML string and return the corresponding Python data structure.
    Supports a minimal subset of YAML.
    """
    lines = yaml_str.splitlines()
    # Remove completely blank lines.
    lines = [line for line in lines if line.strip() != ""]
    result, _ = parse_block(lines, 0)
    return result


def format_scalar(value):
    """Format a scalar value as a YAML string."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Quote the string if it contains spaces or special characters.
        if not value or any(c in value for c in [" ", ":", "-", "#"]):
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        return value
    return str(value)


def unparse_yaml(data, indent=0):
    """
    Convert a Python data structure into a YAML-formatted string.
    Supports a minimal subset of YAML.
    """
    lines = []
    prefix = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(unparse_yaml(value, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {format_scalar(value)}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(unparse_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {format_scalar(item)}")
    else:
        lines.append(f"{prefix}{format_scalar(data)}")
    return "\n".join(lines)


# Public API
__all__ = ["parse_yaml", "unparse_yaml"]
