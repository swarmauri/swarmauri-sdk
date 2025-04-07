#!/usr/bin/env python3
"""
jaml/unparser.py

This module provides the JMLUnparser class, which converts a configuration
object (a plain dict or similar) back into its textual representation
according to the custom grammar.
"""

import json

from .lark_nodes import PreservedArray, PreservedInlineTable


class JMLUnparser:
    def __init__(self, config):
        self.config = config

    def _get_config_data(self):
        if isinstance(self.config, dict):
            return self.config
        elif hasattr(self.config, "data"):
            return self.config.data
        elif hasattr(self.config, "value"):
            return self.config.value
        elif hasattr(self.config, "to_dict"):
            return self.config.to_dict()
        elif hasattr(self.config, "__dict__"):
            return self.config.__dict__
        else:
            raise AttributeError(
                "Configuration object does not have an expected dictionary interface."
            )

    def format_value(self, value):
        """
        Format a value according to the configuration syntax.
        1) If it's a PreservedInlineTable -> return verbatim original text.
        2) If it's a PreservedArray -> return verbatim original text.
        3) Strings with newlines -> triple-quoted.
        4) Booleans -> 'true'/'false'.
        5) None -> 'null'.
        6) int/float -> direct string conversion.
        7) lists -> bracketed multiline array (fallback).
        8) dict -> inline table (fallback).
        """
        # 1) Already-preserved inline table?
        if isinstance(value, PreservedInlineTable):
            return str(value)  # entire { ... } substring

        # 2) Already-preserved array?
        elif isinstance(value, PreservedArray):
            return str(value)  # entire [ ... ] substring

        # 3) String
        elif isinstance(value, str):
            if "\n" in value:
                # Format as a multiline string with triple quotes.
                return f'"""{value}"""'
            else:
                return f"\"{value}\""

        # 4) Boolean
        elif isinstance(value, bool):
            return "true" if value else "false"

        # 5) Null
        elif value is None:
            return "null"

        # 6) Numeric
        elif isinstance(value, (int, float)):
            return str(value)

        # 7) Fallback for lists
        elif isinstance(value, list):
            return self.format_list(value)

        # 8) Fallback for dictionaries => inline table
        elif isinstance(value, dict):
            items = []
            for k, v in value.items():
                items.append(f"{k} = {self.format_value(v)}")
            return "{" + ", ".join(items) + "}"

        # Fallback
        else:
            return str(value)

    def format_list(self, lst):
        """
        Produce a bracketed, multiline representation for lists.
        Example:
            [
              "red",
              "green",
              "blue"
            ]
        """
        if not lst:
            return "[]"

        lines = []
        for i, item in enumerate(lst):
            item_str = self.format_value(item)
            is_last = (i == len(lst) - 1)
            line = f"  {item_str}" + ("," if not is_last else "")
            lines.append(line)

        inner = "\n".join(lines)
        return f"[\n{inner}\n]"

    def unparse_section(self, section_dict, section_path):
        """
        Convert a section (dict) to text. 
        - If the key is a dict that is not a PreservedInlineTable,
          and it appears to contain sub-sections, we recursively
          turn it into a [section] block. 
        - If it's recognized as a PreservedInlineTable, 
          we keep it inline.
        """
        output = ""
        if section_path:
            output += f"[{'.'.join(section_path)}]\n"

        assignments = {}
        nested_sections = {}

        # Separate top-level assignments from nested sections.
        for key, value in section_dict.items():
            # We'll treat it as a nested section if it's a plain dict 
            # containing sub-dicts (like a normal TOML table).
            if isinstance(value, dict) and not isinstance(value, PreservedInlineTable):
                # Heuristic: if any inner value is itself a dict, treat as nested
                if any(isinstance(v, dict) for v in value.values()):
                    nested_sections[key] = value
                else:
                    # Otherwise, treat as direct assignment (inline table fallback)
                    assignments[key] = value
            else:
                # Normal assignment
                assignments[key] = value

        # Output assignments.
        for key, value in assignments.items():
            output += f"{key} = {self.format_value(value)}\n"
        if assignments:
            output += "\n"

        # Recursively process truly nested sections.
        for key, subsec in nested_sections.items():
            output += self.unparse_section(subsec, section_path + [key])

        return output

    def unparse(self):
        output = ""
        config_data = self._get_config_data()

        # Process default assignments (if any).
        default_section = config_data.get("__default__", {})
        for key, value in default_section.items():
            output += f"{key} = {self.format_value(value)}\n"
        if default_section:
            output += "\n"

        # Process each top-level section.
        for key, section in config_data.items():
            if key == "__default__":
                continue
            output += self.unparse_section(section, [key])

        # Remove trailing newlines
        return output.rstrip("\n")

    def __str__(self):
        return self.unparse()
