import re
from typing import Optional
from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode,
)
from ._helpers import _find_table_in_ast, _process_table_merges, _split_top_level_commas

class JMLParser:
    """
    JMLParser that combines features:
      - Preserves one-liner backslash+`n` literal strings.
      - Handles triple-quoted multiline strings (\"\"\" or \'\'\').
      - Handles block scalar with the pipe character (|).
      - Supports other types: int, float, bool, null, list, table, plus logic expressions (~(...)).
    """

    # Regular expressions for sections, key-values, comments, and logic
    SECTION_PATTERN = re.compile(r'^\[(.+)\]$')
    KV_PATTERN = re.compile(r'^([\w-]+)(?::\s*([\w-]+))?\s*=\s*(.+)$')
    COMMENT_PATTERN = re.compile(r'^\s*#(.*)$')
    LOGIC_PATTERN = re.compile(r'^~\((.+)\)$')  # Must start with '~(' and end with ')'

    def __init__(self):
        self.sections = []
        self.current_section = None
        self.pending_comments = []

    def parse(self, text: str) -> DocumentNode:
        """
        Parse the given JML text into a DocumentNode.

        This parser supports:
          - Single-line key-value pairs.
          - Triple-quoted multiline strings (\"\"\" or \'\'\').
          - If a string value starts with a single/double quote but does not end with it on
            that same line, additional lines are joined (with "\n") until the closing quote is found.
          - Logic expressions of the form ~( ... ).
          - Various data types: int, float, bool, null, list, and inline table.
        """
        lines = text.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Check for comment
            comment_match = self.COMMENT_PATTERN.match(line)
            if comment_match:
                self.pending_comments.append(comment_match.group(1).strip())
                i += 1
                continue

            # Check for section header
            section_match = self.SECTION_PATTERN.match(line)
            if section_match:
                self._start_new_section(section_match.group(1).strip())
                i += 1
                continue

            # Check for key-value pair
            kv_match = self.KV_PATTERN.match(line)
            if kv_match:
                key, type_annotation, raw_value = kv_match.groups()
                key = key.strip()

                # If no explicit type, infer it
                if type_annotation is None:
                    type_annotation = self._infer_type(raw_value)
                else:
                    type_annotation = type_annotation.strip()

                raw_value = raw_value.strip()

                # Handle triple-quoted multiline strings explicitly
                if type_annotation == "str" and (raw_value.startswith('"""') or raw_value.startswith("'''")):
                    quote_seq = raw_value[:3]
                    # If the triple-quoted string is not fully closed on the same line:
                    if not (raw_value.endswith(quote_seq) and len(raw_value) > 3):
                        i += 1
                        multiline_lines = [raw_value[3:]]  # Start after the triple-quote
                        while i < len(lines):
                            current_line = lines[i]
                            # If we find the closing triple-quote on this line:
                            if current_line.rstrip().endswith(quote_seq):
                                multiline_lines.append(current_line.rstrip()[: -len(quote_seq)])
                                break
                            else:
                                multiline_lines.append(current_line.rstrip("\r\n"))
                            i += 1
                        # Combine lines with newlines and remove leading/trailing whitespace
                        raw_value = "\n".join(multiline_lines).strip()
                    else:
                        # Closed on the same line; just strip the triple quotes
                        raw_value = raw_value[3:-3].strip()
                    i += 1
                    self._add_key_value(key, type_annotation, raw_value)
                    continue

                # Handle multi-line single/double quoted strings (non-triple-quote scenario)
                if (
                    type_annotation == "str"
                    and len(raw_value) > 0
                    and raw_value[0] in ('"', "'")
                    and not (len(raw_value) >= 2 and raw_value.endswith(raw_value[0]))
                ):
                    # We found the start of a quoted string but it doesn't end on this line
                    quote_char = raw_value[0]
                    parts = [raw_value]
                    i += 1
                    while i < len(lines):
                        parts.append(lines[i])
                        # If the line ends with that same quote, we assume it's closed
                        if lines[i].rstrip().endswith(quote_char):
                            break
                        i += 1
                    raw_value = "\n".join(parts).strip()
                    i += 1
                    self._add_key_value(key, type_annotation, raw_value)
                    continue


                # Otherwise, it's a normal single-line key-value
                self._add_key_value(key, type_annotation, raw_value)
                i += 1
                continue

            # If none of the above matched, just proceed
            i += 1

        return DocumentNode(self.sections)

    def _start_new_section(self, section_name: str):
        self.current_section = SectionNode(
            name=section_name,
            keyvalues=[],
            comments=self.pending_comments,
        )
        self.sections.append(self.current_section)
        self.pending_comments = []

    def _add_key_value(self, key: str, type_annotation: str, raw_value: str):
        """
        Create a KeyValueNode for the given key, type, and raw value.
        For strings:
          - If wrapped in quotes/triple-quotes, remove them.
          - Convert backslash-escapes as JSON does (so "\n" => newline).
        For logic:
          - If it matches `~(...)`, store the expression in logic_node.
        """
        logic_node = None
        value_node = None

        if type_annotation == "str":
            trimmed = raw_value.strip()
            # If fully single/double-quoted (not triple), remove those quotes
            if (
                len(trimmed) >= 2
                and (
                    (trimmed.startswith('"') and trimmed.endswith('"'))
                    or (trimmed.startswith("'") and trimmed.endswith("'"))
                )
            ):
                inner = trimmed[1:-1]
            else:
                inner = raw_value

            # Check if it's a logic expression ~(...)
            logic_match = self.LOGIC_PATTERN.match(inner)
            if logic_match:
                logic_node = LogicExpressionNode(expression=None, raw_text=inner)
                value_node = ScalarNode(value=inner)
            else:
                # Decode escape sequences
                try:
                    decoded = bytes(inner, "utf-8").decode("unicode_escape")
                except Exception:
                    decoded = inner
                value_node = ScalarNode(value=decoded)
        else:
            # Possibly logic for non-string
            logic_match = self.LOGIC_PATTERN.match(raw_value)
            if logic_match:
                logic_node = LogicExpressionNode(expression=None, raw_text=raw_value)
                value_node = ScalarNode(value=raw_value)
            else:
                # Parse as int, float, bool, etc.
                value_node = self._parse_non_string_value(type_annotation, raw_value)

        kv_node = KeyValueNode(
            key=key,
            type_annotation=type_annotation,
            value=value_node,
            logic=logic_node,
            comments=self.pending_comments,
        )
        self.pending_comments = []

        # If no section has been started yet, create a default one
        if self.current_section is None:
            self._start_new_section("default")

        self.current_section.keyvalues.append(kv_node)

    def _parse_non_string_value(self, type_annotation: str, value_str: str) -> ScalarNode | ArrayNode | TableNode:
        """
        Parse non-string types, including int, float, bool, null, list, and table.
        """
        if type_annotation == "int":
            try:
                return ScalarNode(value=int(value_str, 0))
            except ValueError as e:
                raise ValueError(f"Error converting {value_str} to int: {e}")
        elif type_annotation == "float":
            try:
                return ScalarNode(value=float(value_str))
            except ValueError:
                return ScalarNode(value=value_str)
        elif type_annotation == "bool":
            norm = value_str.lower()
            if norm in ("true", "yes", "on"):
                return ScalarNode(value=True)
            elif norm in ("false", "no", "off"):
                return ScalarNode(value=False)
            else:
                raise ValueError(f"Invalid boolean '{value_str}' for type 'bool'.")
        elif type_annotation == "null":
            return ScalarNode(value=None)
        elif type_annotation == "list":
            inside = value_str.strip()
            if inside.startswith("[") and inside.endswith("]"):
                inside = inside[1:-1].strip()
            parts = [p.strip() for p in inside.split(",")] if inside else []
            items = []
            for part in parts:
                t = self._infer_type(part)
                items.append(self._parse_value_by_type(t, part))
            return ArrayNode(items=items)
        elif type_annotation == "table":
            return self._parse_inline_table(value_str)
        else:
            return ScalarNode(value=value_str)

    def _infer_type(self, raw_value: str) -> str:
        """
        Infer a type for the given raw_value if no explicit type was given.
        """
        stripped = raw_value.strip()

        # If fully single/double-quoted, treat as string
        if (
            len(stripped) >= 2
            and (
                (stripped.startswith('"') and stripped.endswith('"'))
                or (stripped.startswith("'") and stripped.endswith("'"))
            )
        ):
            return "str"

        # If looks like a list
        if stripped.startswith("[") and stripped.endswith("]"):
            return "list"

        # If looks like an inline table
        if stripped.startswith("{") and stripped.endswith("}"):
            return "table"

        # Check booleans
        lower_val = stripped.lower()
        if lower_val in ("true", "false", "yes", "no", "on", "off"):
            return "bool"

        # Some special floats
        if lower_val in ("inf", "-inf", "nan"):
            return "float"

        # null type
        if lower_val == "null":
            return "null"

        # Try int
        try:
            int(stripped, 0)
            return "int"
        except ValueError:
            pass

        # Try float
        try:
            float(stripped)
            return "float"
        except ValueError:
            pass

        # Default to string
        return "str"

    def _parse_value_by_type(self, t: str, raw_val: str):
        """
        Helper method for sub-values in a list or table.
        """
        raw_val = raw_val.strip()

        if t == "str":
            if (
                len(raw_val) >= 2
                and (
                    (raw_val.startswith('"') and raw_val.endswith('"'))
                    or (raw_val.startswith("'") and raw_val.endswith("'"))
                )
            ):
                inner = raw_val[1:-1]
            else:
                inner = raw_val
            try:
                decoded = bytes(inner, "utf-8").decode("unicode_escape")
            except Exception:
                decoded = inner
            return ScalarNode(value=decoded)
        elif t in ("int", "float", "bool", "null"):
            return self._parse_non_string_value(t, raw_val)
        elif t == "list":
            inside = raw_val
            if inside.startswith("[") and inside.endswith("]"):
                inside = inside[1:-1].strip()
            parts = [p.strip() for p in inside.split(",")] if inside else []
            items = []
            for part in parts:
                sub_t = self._infer_type(part)
                items.append(self._parse_value_by_type(sub_t, part))
            return ArrayNode(items=items)
        elif t == "table":
            return self._parse_inline_table(raw_val)
        else:
            return ScalarNode(value=raw_val)

    def _parse_inline_table(self, table_str: str) -> TableNode:
        """
        Parse inline tables in the form { key = value, key2 = value2 }.
        Also supports merges with '<<: some_other_table'.
        """
        inside = table_str.strip()
        if inside.startswith("{") and inside.endswith("}"):
            inside = inside[1:-1].strip()

        pairs = []
        if inside:
            entries = _split_top_level_commas(inside)
            for part in entries:
                part = part.strip()
                if not part:
                    continue

                # Merge operator
                if part.startswith("<<:"):
                    merge_value = part[3:].strip()
                    kv_node = KeyValueNode(
                        key="<<",
                        type_annotation="merge",
                        value=ScalarNode(value=merge_value),
                    )
                    pairs.append(kv_node)
                    continue

                if "=" not in part:
                    raise ValueError(f"Invalid inline table entry '{part}'. Expected 'key = value'.")

                sub_k, sub_v = part.split("=", 1)
                sub_k = sub_k.strip()
                sub_v = sub_v.strip()
                sub_type = self._infer_type(sub_v)
                val_node = self._parse_value_by_type(sub_type, sub_v)
                kv_node = KeyValueNode(key=sub_k, type_annotation=sub_type, value=val_node)
                pairs.append(kv_node)

        return TableNode(keyvalues=pairs)
