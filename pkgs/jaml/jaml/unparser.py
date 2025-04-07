#!/usr/bin/env python3
"""
jaml/unparser.py

This module provides the JMLUnparser class, which converts a configuration
object (a plain dict or similar) back into its textual representation
according to the custom grammar.
"""

import json

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
            raise AttributeError("Configuration object does not have an expected dictionary interface.")

    def format_value(self, value):
        """
        Format a value according to the configuration syntax.
        1) Strings with newlines -> triple-quoted.
        2) Booleans -> 'true' / 'false'.
        3) None -> 'null'.
        4) int/float -> direct string conversion.
        5) lists -> bracketed multiline array.
        6) dict -> inline table (unchanged).
        """
        # 1) Strings
        if isinstance(value, str):
            if "\n" in value:
                # Format as a multiline string with triple quotes.
                return f'"""{value}"""'
            else:
                return f"\"{value}\""

        # 2) Boolean
        elif isinstance(value, bool):
            return "true" if value else "false"

        # 3) Null
        elif value is None:
            return "null"

        # 4) Numeric
        elif isinstance(value, (int, float)):
            return str(value)

        # 5) Lists => bracket-based multiline arrays
        elif isinstance(value, list):
            return self.format_list(value)

        # 6) Dictionaries => inline tables
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

        # We'll place each item on its own line, with commas after each except the last.
        lines = []
        for i, item in enumerate(lst):
            # Format the item itself
            item_str = self.format_value(item)
            # Decide whether to add a comma
            is_last = (i == len(lst) - 1)
            line = f"  {item_str}" + ("," if not is_last else "")
            lines.append(line)

        inner = "\n".join(lines)
        return f"[\n{inner}\n]"

    def unparse_section(self, section_dict, section_path):
        output = ""
        if section_path:
            output += f"[{'.'.join(section_path)}]\n"

        assignments = {}
        nested_sections = {}

        # Separate assignments from nested sections.
        for key, value in section_dict.items():
            if isinstance(value, dict):
                # Heuristic: if any inner value is a dict, treat it as a nested section.
                if any(isinstance(v, dict) for v in value.values()):
                    nested_sections[key] = value
                else:
                    # If inline tables are represented as dicts, you may adjust logic.
                    nested_sections[key] = value
            else:
                assignments[key] = value

        # Output assignments.
        for key, value in assignments.items():
            output += f"{key} = {self.format_value(value)}\n"
        if assignments:
            output += "\n"

        # Recursively process nested sections.
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

        # Remove any trailing newlines from the final output.
        return output.rstrip("\n")

    def __str__(self):
        return self.unparse()
