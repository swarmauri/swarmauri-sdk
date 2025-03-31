"""
canonical_toml.py

A minimal TOML parser and unparser using only Python’s built-in libraries.
This module supports a subset of TOML:
  - Top-level key/value pairs
  - Tables (using [table] headers, including nested tables via dot notation)
  - Arrays of tables (using [[table]] headers) per the TOML spec.
  - Inline tables (using the { ... } notation) are preserved via the InlineTable class.
  - Arrays of simple values

Note: This is a simple implementation and does not cover the full TOML spec.
"""

import re

# A regex to detect bare keys (letters, numbers, underscore and dash)
_bare_key_re = re.compile(r"^[A-Za-z0-9_-]+$")


class QuotedKey(str):
    """
    A subclass of str that marks a key as having been originally quoted.
    When dumping, such keys are always re-quoted.
    """

    pass


def clean_key(key: str) -> str:
    """
    If the key is surrounded by quotes, return a QuotedKey;
    otherwise return the key unchanged.
    """
    key = key.strip()
    if (key.startswith('"') and key.endswith('"')) or (
        key.startswith("'") and key.endswith("'")
    ):
        return QuotedKey(key[1:-1])
    return key


def quote_key(key: str) -> str:
    """
    Return the key unquoted if it is a bare key; otherwise, return it quoted.
    Additionally, if the key is an instance of QuotedKey, always quote it.
    """
    if isinstance(key, QuotedKey):
        return f'"{key}"'
    if _bare_key_re.match(key) and "." not in key:
        return key
    else:
        return f'"{key}"'


def reformat_prefix(prefix_list: list) -> str:
    """
    Given a list of keys (each a str or QuotedKey), join them with a dot.
    Each key is passed through quote_key so that keys that need quoting are quoted.
    """
    return ".".join(quote_key(k) for k in prefix_list)


def split_table_key(header: str) -> list:
    """
    Split a table header (the contents between [ and ]) into its components,
    but do not split dots that appear within quoted keys.
    For example, 'tool.uv.groups."banan.anasd"' returns
       ["tool", "uv", "groups", "\"banan.anasd\""]
    """
    keys = []
    current = []
    in_quote = False
    quote_char = None
    escape = False

    for char in header:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if in_quote:
            current.append(char)
            if char == quote_char:
                in_quote = False
            continue
        if char in ('"', "'"):
            in_quote = True
            quote_char = char
            current.append(char)
            continue
        if char == ".":
            key = "".join(current).strip()
            if key:
                keys.append(key)
            current = []
        else:
            current.append(char)
    if current:
        keys.append("".join(current).strip())
    return keys


def preprocess_toml_lines(toml_string: str) -> list:
    """
    Preprocess the input by joining lines that are part of a multi-line array
    or inline table. This is a simple (and not full‐proof) approach.
    """
    lines = toml_string.splitlines()
    result = []
    buffer = ""
    in_multiline = False
    for line in lines:
        stripped = line.split("#", 1)[0].rstrip()
        if not stripped:
            continue
        if not in_multiline:
            buffer = stripped
        else:
            buffer += " " + stripped
        open_sq = buffer.count("[")
        close_sq = buffer.count("]")
        open_curly = buffer.count("{")
        close_curly = buffer.count("}")
        if (open_sq > close_sq) or (open_curly > close_curly):
            in_multiline = True
            continue
        else:
            in_multiline = False
            result.append(buffer.strip())
            buffer = ""
    if buffer:
        result.append(buffer.strip())
    return result


class InlineTable(dict):
    """
    A dict subclass representing an inline table.
    When dumping a TOML document, instances of InlineTable are formatted
    using the inline table syntax (i.e. { key = value, ... }).
    """

    pass


def split_inline_table(text: str) -> list:
    """
    Split the inner content of an inline table (without the surrounding braces)
    into a list of key-value pair strings.
    This simple state-machine splits on commas that are not within quotes.
    """
    pairs = []
    current = []
    in_quote = False
    quote_char = ""
    escape = False

    for char in text:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            escape = True
            current.append(char)
            continue
        if in_quote:
            current.append(char)
            if char == quote_char:
                in_quote = False
            continue
        if char in ('"', "'"):
            in_quote = True
            quote_char = char
            current.append(char)
            continue
        if char == ",":
            pair_str = "".join(current).strip()
            if pair_str:
                pairs.append(pair_str)
            current = []
        else:
            current.append(char)
    pair_str = "".join(current).strip()
    if pair_str:
        pairs.append(pair_str)
    return pairs


def parse_value(s: str):
    """
    Convert a TOML value (as a string) into an appropriate Python type.
    Supports inline tables, arrays, booleans, numbers, and quoted strings.
    """
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        return parse_inline_table(s)
    if s.startswith("[") and s.endswith("]"):
        return parse_array(s)
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        return s[1:-1]
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def parse_inline_table(s: str) -> InlineTable:
    """
    Parse an inline table (e.g. { key = 42, name = "foo" }) and return an InlineTable.
    """
    inner = s.strip()[1:-1].strip()
    table = InlineTable()
    if not inner:
        return table
    pairs = split_inline_table(inner)
    for pair in pairs:
        if "=" not in pair:
            continue
        key, val = pair.split("=", 1)
        key = key.strip()
        val = val.strip()
        table[key] = parse_value(val)
    return table


def parse_array(s: str) -> list:
    """
    Parse a TOML array (e.g. [ 1, 2, 3 ]) into a Python list.
    (This implementation does not support nested arrays with commas inside values.)
    """
    inner = s.strip()[1:-1].strip()
    if not inner:
        return []
    items = [item.strip() for item in inner.split(",")]
    return [parse_value(item) for item in items]


def loads(toml_string: str) -> dict:
    """
    Parse a TOML string into a Python dictionary.
    Supports:
      - Top-level key/value pairs
      - Table headers (e.g. [table] and nested tables via dot notation)
      - Array-of-tables headers (e.g. [[table]])
    Inline tables are preserved as InlineTable instances.
    """
    data = {}
    lines = preprocess_toml_lines(toml_string)
    current_table = data
    for line in lines:
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            header = line[2:-2].strip()
            keys = [clean_key(k) for k in split_table_key(header)]
            current_table = data
            for key in keys[:-1]:
                if key not in current_table:
                    current_table[key] = {}
                elif isinstance(current_table[key], list):
                    if not current_table[key]:
                        current_table[key].append({})
                    current_table = current_table[key][-1]
                    continue
                current_table = current_table[key]
            last_key = keys[-1]
            if last_key not in current_table:
                current_table[last_key] = []
            elif not isinstance(current_table[last_key], list):
                raise ValueError(f"Conflicting table definition for key: {last_key}")
            new_table = {}
            current_table[last_key].append(new_table)
            current_table = new_table
            continue
        if line.startswith("[") and line.endswith("]"):
            header = line[1:-1].strip()
            keys = [clean_key(k) for k in split_table_key(header)]
            current_table = data
            for key in keys:
                if key not in current_table:
                    current_table[key] = {}
                elif isinstance(current_table[key], list):
                    if not current_table[key]:
                        current_table[key].append({})
                    current_table = current_table[key][-1]
                    continue
                current_table = current_table[key]
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            current_table[key] = parse_value(value)
    return data


def load(fp) -> dict:
    """
    Read a TOML document from a file-like object or filename and return the parsed dict.
    """
    if isinstance(fp, str):
        with open(fp, "r", encoding="utf-8") as f:
            return loads(f.read())
    elif hasattr(fp, "read"):
        return loads(fp.read())
    else:
        raise TypeError("fp must be a filename or a file-like object.")


def dumps_value(value, multiline_arrays=True, indent=0) -> str:
    """
    Return a TOML-compatible string representation of a Python value.
    Only InlineTable instances are dumped in inline table syntax.
    Normal dictionaries are meant to be output as table sections.
    Arrays of simple values are dumped in square-brackets.

    If multiline_arrays is True, lists are dumped with one element per line.
    """
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, InlineTable):
        items = [
            f"{k} = {dumps_value(v, multiline_arrays, indent)}"
            for k, v in value.items()
        ]
        return "{ " + ", ".join(items) + " }"
    elif isinstance(value, list):
        if multiline_arrays:
            inner_indent = " " * (indent + 4)
            items = [dumps_value(item, multiline_arrays, indent + 4) for item in value]
            return (
                "[\n"
                + ",\n".join(inner_indent + item for item in items)
                + "\n"
                + (" " * indent)
                + "]"
            )
        else:
            items = [dumps_value(item, multiline_arrays, indent) for item in value]
            return "[ " + ", ".join(items) + " ]"
    else:
        return str(value)


def is_array_of_tables(value) -> bool:
    """
    Returns True if the value is a non-empty list of dictionaries (and not InlineTable instances),
    indicating an array-of-tables.
    """
    if isinstance(value, list) and value:
        return all(
            isinstance(item, dict) and not isinstance(item, InlineTable)
            for item in value
        )
    return False


def has_direct_values(table: dict) -> bool:
    """
    Returns True if the table has any direct key/value pairs (i.e. values that are not dicts
    or arrays-of-tables). This is used to decide whether to emit a header for an intermediate container.
    """
    for v in table.values():
        if not (
            (isinstance(v, dict) and not isinstance(v, InlineTable))
            or (isinstance(v, list) and is_array_of_tables(v))
        ):
            return True
    return False


def _dumps_section(
    prefix_list: list, table: dict, multiline_arrays=False, indent=0
) -> list:
    """
    Recursively dump key/value pairs for a table.
    prefix_list is a list of keys representing the current header.
    Direct key/value pairs are output first, then nested tables and arrays-of-tables.
    Intermediate containers with no direct values are flattened.
    """
    lines = []
    for k, v in table.items():
        if not (
            (isinstance(v, dict) and not isinstance(v, InlineTable))
            or (isinstance(v, list) and is_array_of_tables(v))
        ):
            lines.append(f"{k} = {dumps_value(v, multiline_arrays, indent)}")
    for k, v in table.items():
        if isinstance(v, dict) and not isinstance(v, InlineTable):
            new_prefix = prefix_list + [k]
            if has_direct_values(v):
                lines.append("")
                lines.append(f"[{reformat_prefix(new_prefix)}]")
                lines.extend(_dumps_section(new_prefix, v, multiline_arrays, indent))
            else:
                lines.extend(_dumps_section(new_prefix, v, multiline_arrays, indent))
        elif isinstance(v, list) and is_array_of_tables(v):
            new_prefix = prefix_list + [k]
            for item in v:
                lines.append("")
                lines.append(f"[[{reformat_prefix(new_prefix)}]]")
                lines.extend(_dumps_section(new_prefix, item, multiline_arrays, indent))
    return lines


def dumps(data: dict, multiline_arrays=True) -> str:
    """
    Convert a Python dictionary (as returned by loads) into a TOML-formatted string.
    Top-level non-dictionary values and InlineTable instances are dumped inline.
    Top-level dictionaries are dumped as tables.
    Arrays of tables are output using double-bracket headers.
    Intermediate containers with no direct values are flattened.

    If multiline_arrays is True, arrays (e.g. classifiers) are dumped with one element per line.
    """
    lines = []
    for key, value in data.items():
        if not (
            (isinstance(value, dict) and not isinstance(value, InlineTable))
            or (isinstance(value, list) and is_array_of_tables(value))
        ):
            lines.append(f"{key} = {dumps_value(value, multiline_arrays, indent=0)}")
    for key, value in data.items():
        if isinstance(value, dict) and not isinstance(value, InlineTable):
            prefix_list = [key]
            if has_direct_values(value):
                lines.append("")
                lines.append(f"[{reformat_prefix(prefix_list)}]")
                lines.extend(
                    _dumps_section(prefix_list, value, multiline_arrays, indent=0)
                )
            else:
                lines.extend(
                    _dumps_section(prefix_list, value, multiline_arrays, indent=0)
                )
        elif isinstance(value, list) and is_array_of_tables(value):
            prefix_list = [key]
            for item in value:
                lines.append("")
                lines.append(f"[[{reformat_prefix(prefix_list)}]]")
                lines.extend(
                    _dumps_section(prefix_list, item, multiline_arrays, indent=0)
                )
    return "\n".join(lines)


def dump(data: dict, fp):
    """
    Write the TOML representation of the given dict to a file-like object or filename.
    """
    toml_str = dumps(data)
    if isinstance(fp, str):
        with open(fp, "w", encoding="utf-8") as f:
            f.write(toml_str)
    elif hasattr(fp, "write"):
        fp.write(toml_str)
    else:
        raise TypeError("fp must be a filename or a file-like object.")
