#!/usr/bin/env python3
"""
jaml/unparser.py

This module provides the JMLUnparser class, which converts a configuration
object (a plain dict or similar) back into its textual representation
according to the custom grammar, preserving top-level comments
and inline comments.
"""

import json

from .lark_nodes import PreservedString, PreservedArray, PreservedInlineTable

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

        elif isinstance(value, PreservedString):
            # Output the original quoted text as-is.
            return value.original

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
            # If it's a "normal" dict, produce inline table syntax:
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
         - If 'value' is a dict with sub-dicts, treat it as a nested section.
         - Otherwise treat it as a direct assignment.
         - If it's a 'PreservedInlineTable', do not break it up.
         - If it's an 'inline comment' dict (with '_value' and '_inline_comment'), 
           put the comment on the same line.
        """
        output = ""
        if section_path:
            output += f"[{'.'.join(section_path)}]\n"

        assignments = {}
        nested_sections = {}

        # Separate top-level assignments from nested sections.
        for key, value in section_dict.items():
            # Heuristic: if a plain dict has sub-dicts, treat as nested section
            if (
                isinstance(value, dict)
                and not isinstance(value, PreservedInlineTable)
                and "_value" not in value   # i.e. not an inline-comment structure
            ):
                if any(isinstance(v, dict) for v in value.values()):
                    nested_sections[key] = value
                else:
                    # treat as direct assignment (inline table fallback)
                    assignments[key] = value
            else:
                # Normal assignment (including inline comment or preserved table)
                assignments[key] = value

        # Output assignments, including inline comments on the same line
        for key, value in assignments.items():
            # Detect the special "commented assignment" structure:
            if (
                isinstance(value, dict)
                and "_value" in value
                and "_inline_comment" in value
            ):
                # e.g. { "_value": "Hello, World!", "_inline_comment": "# inline stuff" }
                val_str = self.format_value(value["_value"])
                cmt_str = value["_inline_comment"]
                # Put the comment on the same line:
                output += f"{key} = {val_str}  {cmt_str}\n"
            else:
                # Normal approach
                output += f"{key} = {self.format_value(value)}\n"

        if assignments:
            output += "\n"

        # Recursively process nested sections
        for key, subsec in nested_sections.items():
            output += self.unparse_section(subsec, section_path + [key])

        return output

    def unparse(self):
        output = ""
        config_data = self._get_config_data()

        # 1) Dump any top-level standalone comments first
        top_comments = config_data.get("__comments__", [])
        for comment_line in top_comments:
            output += comment_line + "\n"
        if top_comments:
            output += "\n"

        # 2) Dump default assignments if any
        default_section = config_data.get("__default__", {})
        for key, value in default_section.items():
            # Check if it's an inline-comment dict
            if (
                isinstance(value, dict)
                and "_value" in value
                and "_inline_comment" in value
            ):
                val_str = self.format_value(value["_value"])
                cmt_str = value["_inline_comment"]
                output += f"{key} = {val_str}  {cmt_str}\n"
            else:
                output += f"{key} = {self.format_value(value)}\n"

        if default_section:
            output += "\n"

        # 3) Dump named sections
        for key, section in config_data.items():
            if key in ("__default__", "__comments__"):
                continue
            output += self.unparse_section(section, [key])

        return output.rstrip("\n")

    def __str__(self):
        return self.unparse()
