#!/usr/bin/env python3
"""
jaml/unparser.py

This module provides the JMLUnparser class, which converts a configuration
object (a plain dict or similar) back into its textual representation
according to the custom grammar, preserving top-level comments
and inline comments.
"""

import json

from .lark_nodes import ( 
    PreservedString, 
    PreservedValue, 
    PreservedArray, 
    PreservedInlineTable,
    DeferredExpression,
    DeferredComprehension
)

from lark import Token

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
        if isinstance(value, DeferredExpression):
            return f"<{{ {value.expr} }}>"

        # New branch for DeferredComprehension:
        if isinstance(value, DeferredComprehension):
            # Re-wrap it in curly braces.
            return "{" + value.text + "}"
        
        # 0) If the value is a PreservedValue, format its inner value and append its comment.
        if isinstance(value, PreservedValue):
            val_str = self.format_value(value.value)
            if value.comment and not value.comment[0].isspace():
                return f"{val_str} {value.comment}"
            else:
                return f"{val_str}{value.comment}"
        # 1) Already-preserved inline table?
        if isinstance(value, PreservedInlineTable):
            return str(value)
        # 2) Already-preserved array?
        elif isinstance(value, PreservedArray):
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
        if isinstance(lst, PreservedArray) and "\n" not in lst.original_text:
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




    def unparse_section(self, section_dict, section_path):
        output = ""
        if section_path:
            output += f"[{'.'.join(section_path)}]\n"

        assignments = {}
        nested_sections = {}

        for key, value in section_dict.items():
            if isinstance(value, dict) and "_value" in value and "_annotation" in value:
                # This is an annotated assignment.
                assignments[key] = value
            elif isinstance(value, dict) and any(isinstance(v, dict) for v in value.values()):
                nested_sections[key] = value
            else:
                assignments[key] = value

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

        for key, subsec in nested_sections.items():
            output += self.unparse_section(subsec, section_path + [key])

        return output


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

            # If the value is a dict => it's a "section"
            if isinstance(value, dict):
                output += self.unparse_section(value, [key])
            else:
                # It's a simple assignment at top level
                output += f"{key} = {self.format_value(value)}\n"

        final_output = output.rstrip("\n")
        return final_output


    def __str__(self):
        return self.unparse()
