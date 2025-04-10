#!/usr/bin/env python3
"""
jaml/unparser.py

This module provides the JMLUnparser class, which converts a configuration
object (a plain dict or similar) back into its textual representation
according to the custom grammar, preserving top-level comments
and inline comments.
"""

import json
from lark import Token

from .ast_nodes import ( 
    PreservedString, 
    PreservedValue, 
    PreservedArray, 
    PreservedInlineTable,
    DeferredDictComprehension
)


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
        # New branch for DeferredDictComprehension:
        if isinstance(value, DeferredDictComprehension):
            # Re-wrap it in curly braces.
            return value.original
        
        # 0) If the value is a PreservedValue, format its inner value and append its comment.
        if isinstance(value, PreservedValue):
            val_str = self.format_value(value.value)
            if value.comment and not value.comment[0].isspace():
                return f"{val_str} {value.comment}"
            else:
                return f"{val_str}{value.comment}"
        # 1) Already-preserved inline table?
        if isinstance(value, PreservedInlineTable):
            # For single-line inline tables, preserve the original text.
            # Multiline inline tables are handled as nested sections in unparse_section.
            if "\n" not in value.original:
                return value.original
            else:
                # Fall through so that multiline inline tables get expanded.
                pass
        # 2) Already-preserved array?
        if isinstance(value, PreservedArray):
            return str(value)
        elif isinstance(value, PreservedString):
            return value.original
        elif isinstance(value, str):
            if "\n" in value:
                return f'"""{value}"""'
            else:
                return f"\"{value}\""
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "null"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            return self.format_list(value)
        elif isinstance(value, dict):
            items = []
            for k, v in value.items():
                items.append(f"{k} = {self.format_value(v)}")
            return "{" + ", ".join(items) + "}"
        else:
            return str(value)

    def format_list(self, lst):
        # If we have a PreservedArray and the original text is a single line, reserialize it in one line.
        if isinstance(lst, PreservedArray) and "\n" not in lst.original:
            formatted_items = [self.format_value(item) for item in lst]
            return f"[{', '.join(formatted_items)}]"
        
        # Otherwise, fall back to multi-line formatting.
        if not lst:
            return "[]"
        
        lines = []
        for i, item in enumerate(lst):
            item_str = self.format_value(item)
            # Append a comma to every item except the last.
            is_last = (i == len(lst) - 1)
            line = f"{item_str}" + (", " if not is_last else "")
            lines.append(line)
        
        inner = "".join(lines)
        return f"[{inner}]"

    def unparse_inline_table(self, inline_table):
        """
        Unparse a multiline inline table by extracting its inner assignments
        from the preserved text. This method removes the enclosing curly braces,
        drops any trailing commas, and (in the collapsed form) strips extra indentation.
        """
        # Use the stored text (or fallback to original) so that comment layout is preserved.
        text = getattr(inline_table, "text", inline_table.original)
        text = text.strip()
        # Remove outer braces if present.
        if text.startswith("{") and text.endswith("}"):
            inner = text[1:-1].strip()
        else:
            inner = text

        lines = inner.splitlines()
        processed_lines = []
        for line in lines:
            # First strip all indentation.
            line = line.strip()
            # Remove any trailing commas while preserving inline comments.
            if line.endswith(","):
                line = line[:-1].rstrip()
            if line:
                processed_lines.append(line)
        return "\n".join(processed_lines)

    def unparse_section(self, section_dict, section_path):
        output = ""
        # Print the section header if we have a valid path.
        if section_path:
            output += f"[{'.'.join(section_path)}]\n"

        # If the collapsed section is not a dict (e.g. a multiline inline table), unparse it directly.
        if not isinstance(section_dict, dict):
            output += self.unparse_inline_table(section_dict) + "\n"
            return output

        assignments = {}
        nested_sections = {}

        for key, value in section_dict.items():
            if isinstance(value, dict) and "_value" in value and "_annotation" in value:
                # This is an annotated assignment.
                assignments[key] = value
            elif isinstance(value, dict):
                # Treat plain dicts (that are not inline tables) as nested sections.
                nested_sections[key] = value
            else:
                assignments[key] = value

        # Output assignments first.
        for key, value in assignments.items():
            if isinstance(value, dict) and "_value" in value and "_annotation" in value:
                # Format annotated assignment.
                val_str = self.format_value(value["_value"])
                annot = value["_annotation"]
                cmt_str = ""
                # Optionally include the inline comment if it exists.
                if isinstance(value["_value"], PreservedValue):
                    cmt_str = value["_value"].comment
                output += f"{key}: {annot} = {val_str}{cmt_str}\n"
            else:
                output += f"{key} = {self.format_value(value)}\n"

        if assignments:
            output += "\n"

        # Recurse into nested sections.
        for key, subsec in nested_sections.items():
            # If the nested section is a multiline inline table, expand it as its own section.
            if isinstance(subsec, PreservedInlineTable) and "\n" in subsec.original:
                new_path = section_path + [key]
                output += f"[{'.'.join(new_path)}]\n"
                output += self.unparse_inline_table(subsec) + "\n\n"
            else:
                collapsed_path, collapsed_section = self._collapse_section(section_path + [key], subsec)
                output += self.unparse_section(collapsed_section, collapsed_path)
        return output

    def _collapse_section(self, section_path, section_dict):
        """
        Recursively collapse nested sections if there is exactly one key in the
        current dictionary and its value is a plain dictionary or a multiline inline table.
        This will merge the keys into a single dotted header.
        """
        if isinstance(section_dict, dict) and len(section_dict) == 1:
            only_key = list(section_dict.keys())[0]
            val = section_dict[only_key]
            # Allow collapsing if the value is a plain dict (without annotated assignments)...
            if isinstance(val, dict) and not ("_value" in val and "_annotation" in val):
                return self._collapse_section(section_path + [only_key], val)
            # ...or if it is a multiline inline table.
            elif isinstance(val, PreservedInlineTable) and "\n" in val.original:
                return section_path + [only_key], val
        return section_path, section_dict

    def unparse(self):
        output = ""
        config_data = self._get_config_data()

        # 1) Dump any top-level standalone comments first.
        top_comments = config_data.get("__comments__", [])
        for comment_line in top_comments:
            output += comment_line + "\n"
        if top_comments:
            output += "\n"

        # 2) Go through all top-level keys (skipping __comments__)
        for key, value in config_data.items():
            if key == "__comments__":
                continue

            # If the value is a dict, attempt to collapse nested sections into a single header.
            if isinstance(value, dict):
                collapsed_path, collapsed_section = self._collapse_section([key], value)
                output += self.unparse_section(collapsed_section, collapsed_path)
            else:
                # It's a simple assignment at top level.
                output += f"{key} = {self.format_value(value)}\n"

        final_output = output.rstrip("\n")
        return final_output

    def __str__(self):
        return self.unparse()
