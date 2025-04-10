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
    def __init__(self, config, debug=False):
        self.config = config
        self.debug = debug
        if self.debug:
            print("[DEBUG UNPARSER] JMLUnparser initialized with config type:", type(config))

    def _get_config_data(self):
        if self.debug:
            print("[DEBUG UNPARSER] Entering _get_config_data with config type:", type(self.config))
        if isinstance(self.config, dict):
            if self.debug:
                print("[DEBUG UNPARSER] Config is a dict.")
            return self.config
        elif hasattr(self.config, "data"):
            if self.debug:
                print("[DEBUG UNPARSER] Config has attribute 'data'.")
            return self.config.data
        elif hasattr(self.config, "value"):
            if self.debug:
                print("[DEBUG UNPARSER] Config has attribute 'value'.")
            return self.config.value
        elif hasattr(self.config, "to_dict"):
            if self.debug:
                print("[DEBUG UNPARSER] Config has method 'to_dict'.")
            return self.config.to_dict()
        elif hasattr(self.config, "__dict__"):
            if self.debug:
                print("[DEBUG UNPARSER] Config has __dict__ attribute.")
            return self.config.__dict__
        else:
            raise AttributeError(
                "Configuration object does not have an expected dictionary interface."
            )

    def format_value(self, value):
        if self.debug:
            print("[DEBUG UNPARSER] Entering format_value with value:", repr(value), "of type:", type(value))
        # New branch for DeferredDictComprehension:
        if isinstance(value, DeferredDictComprehension):
            if self.debug:
                print("[DEBUG UNPARSER] Value is DeferredDictComprehension. Returning origin:", value.origin)
            return value.origin
        
        # 0) If the value is a PreservedValue, format its inner value and append its comment.
        if isinstance(value, PreservedValue):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a PreservedValue. Formatting inner value.")
            val_str = self.format_value(value.value)
            result = f"{val_str} {value.comment}" if value.comment and not value.comment[0].isspace() else f"{val_str}{value.comment}"
            if self.debug:
                print("[DEBUG UNPARSER] Formatted PreservedValue result:", result)
            return result
        # 1) Already-preserved inline table?
        if isinstance(value, PreservedInlineTable):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a PreservedInlineTable.")
            # For single-line inline tables, simply return the origin text.
            if "\n" not in value.origin:
                if self.debug:
                    print("[DEBUG UNPARSER] Inline table is single-line. Returning origin:", value.origin)
                return value.origin
            else:
                if self.debug:
                    print("[DEBUG UNPARSER] Inline table is multiline. Proceeding to reformat.")
                # Fall through so that multiline inline tables get expanded.
        # 2) Already-preserved array?
        if isinstance(value, PreservedArray):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a PreservedArray. Returning str(value):", str(value))
            return str(value)
        elif isinstance(value, PreservedString):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a PreservedString. Returning origin:", value.origin)
            return value.origin
        elif isinstance(value, str):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a plain string.")
            if "\n" in value:
                result = f'"""{value}"""'
                if self.debug:
                    print("[DEBUG UNPARSER] String contains newline. Returning triple-quoted string:", result)
                return result
            else:
                result = f"\"{value}\""
                if self.debug:
                    print("[DEBUG UNPARSER] String is single-line. Returning quoted string:", result)
                return result
        elif isinstance(value, bool):
            result = "true" if value else "false"
            if self.debug:
                print("[DEBUG UNPARSER] Value is a boolean. Returning:", result)
            return result
        elif value is None:
            if self.debug:
                print("[DEBUG UNPARSER] Value is None. Returning 'null'")
            return "null"
        elif isinstance(value, (int, float)):
            result = str(value)
            if self.debug:
                print("[DEBUG UNPARSER] Value is numeric. Returning:", result)
            return result
        elif isinstance(value, list):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a list. Calling format_list.")
            return self.format_list(value)
        elif isinstance(value, dict):
            if self.debug:
                print("[DEBUG UNPARSER] Value is a dict. Formatting as inline table.")
            items = []
            for k, v in value.items():
                formatted_item = f"{k} = {self.format_value(v)}"
                if self.debug:
                    print(f"[DEBUG UNPARSER] Formatted dict item: {formatted_item}")
                items.append(formatted_item)
            result = "{" + ", ".join(items) + "}"
            if self.debug:
                print("[DEBUG UNPARSER] Formatted dict result:", result)
            return result
        else:
            result = str(value)
            if self.debug:
                print("[DEBUG UNPARSER] Falling back to str(value):", result)
            return result

    def format_list(self, lst):
        if self.debug:
            print("[DEBUG UNPARSER] Entering format_list with list:", lst)
        # If we have a PreservedArray and the origin text is a single line, reserialize it in one line.
        if isinstance(lst, PreservedArray) and "\n" not in lst.origin:
            formatted_items = [self.format_value(item) for item in lst]
            result = f"[{', '.join(formatted_items)}]"
            if self.debug:
                print("[DEBUG UNPARSER] PreservedArray single-line formatting result:", result)
            return result
        
        # Otherwise, fall back to multi-line formatting.
        if not lst:
            if self.debug:
                print("[DEBUG UNPARSER] List is empty. Returning []")
            return "[]"
        
        lines = []
        for i, item in enumerate(lst):
            item_str = self.format_value(item)
            is_last = (i == len(lst) - 1)
            line = f"{item_str}" + (", " if not is_last else "")
            if self.debug:
                print(f"[DEBUG UNPARSER] Formatted list item {i}: {line}")
            lines.append(line)
        
        inner = "".join(lines)
        result = f"[{inner}]"
        if self.debug:
            print("[DEBUG UNPARSER] Final formatted list result:", result)
        return result

    def unparse_inline_table(self, inline_table):
        if self.debug:
            print("[DEBUG UNPARSER] Entering unparse_inline_table with inline_table:", inline_table)
        # Use the stored text (or fallback to origin) to preserve comment layout.
        text = getattr(inline_table, "text", inline_table.origin)
        text = text.strip()
        if self.debug:
            print("[DEBUG UNPARSER] Inline table text after strip:", text)
        # Remove outer braces if present.
        if text.startswith("{") and text.endswith("}"):
            inner = text[1:-1].strip()
            if self.debug:
                print("[DEBUG UNPARSER] Removed outer braces. Inner text:", inner)
        else:
            inner = text

        lines = inner.splitlines()
        processed_lines = []
        for line in lines:
            orig_line = line
            line = line.strip()
            # Remove trailing commas while keeping inline comments.
            if line.endswith(","):
                line = line[:-1].rstrip()
            if line:
                processed_lines.append(line)
            if self.debug:
                print(f"[DEBUG UNPARSER] Processed line: Original: '{orig_line}' -> Processed: '{line}'")
        result = "\n".join(processed_lines)
        if self.debug:
            print("[DEBUG UNPARSER] Final unparsed inline table result:", result)
        return result

    def unparse_section(self, section_dict, section_path):
        if self.debug:
            print("[DEBUG UNPARSER] Entering unparse_section with section_path:", section_path)
            print("[DEBUG UNPARSER] Section dictionary keys:", list(section_dict.keys()) if isinstance(section_dict, dict) else section_dict)
        output = ""
        # Print the section header if we have a valid path.
        if section_path:
            header = f"[{'.'.join(section_path)}]\n"
            output += header
            if self.debug:
                print("[DEBUG UNPARSER] Section header added:", header.strip())

        # If the collapsed section isn't a dict (for example, it's already a multiline inline table),
        # unparse it directly.
        if not isinstance(section_dict, dict):
            inline_result = self.unparse_inline_table(section_dict) + "\n"
            if self.debug:
                print("[DEBUG UNPARSER] Collapsed section is not a dict. Inline table result:", inline_result.strip())
            output += inline_result
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

        if self.debug:
            print("[DEBUG UNPARSER] Assignments keys:", list(assignments.keys()))
            print("[DEBUG UNPARSER] Nested sections keys:", list(nested_sections.keys()))

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
                line = f"{key}: {annot} = {val_str}{cmt_str}\n"
                output += line
                if self.debug:
                    print("[DEBUG UNPARSER] Formatted annotated assignment:", line.strip())
            else:
                line = f"{key} = {self.format_value(value)}\n"
                output += line
                if self.debug:
                    print("[DEBUG UNPARSER] Formatted assignment:", line.strip())

        if assignments:
            output += "\n"

        # Recurse into nested sections.
        for key, subsec in nested_sections.items():
            # If the nested section is a multiline inline table, expand it as its own section.
            if isinstance(subsec, PreservedInlineTable) and "\n" in subsec.origin:
                new_path = section_path + [key]
                header = f"[{'.'.join(new_path)}]\n"
                inline_sec = self.unparse_inline_table(subsec) + "\n\n"
                output += header + inline_sec
                if self.debug:
                    print("[DEBUG UNPARSER] Expanded nested multiline inline table for key:", key)
            else:
                collapsed_path, collapsed_section = self._collapse_section(section_path + [key], subsec)
                if self.debug:
                    print("[DEBUG UNPARSER] Collapsed section for key:", key, "to path:", collapsed_path)
                output += self.unparse_section(collapsed_section, collapsed_path)
        return output

    def _collapse_section(self, section_path, section_dict):
        if self.debug:
            print("[DEBUG UNPARSER] Entering _collapse_section with path:", section_path, "and section_dict keys:", list(section_dict.keys()) if isinstance(section_dict, dict) else section_dict)
        if isinstance(section_dict, dict) and len(section_dict) == 1:
            only_key = list(section_dict.keys())[0]
            val = section_dict[only_key]
            # Collapse if the value is a plain dict.
            if isinstance(val, dict) and not ("_value" in val and "_annotation" in val):
                if self.debug:
                    print("[DEBUG UNPARSER] Collapsing section further for key:", only_key)
                return self._collapse_section(section_path + [only_key], val)
            # Collapse if it is a multiline inline table.
            elif isinstance(val, PreservedInlineTable) and "\n" in val.origin:
                if self.debug:
                    print("[DEBUG UNPARSER] Collapsing section to inline table for key:", only_key)
                return section_path + [only_key], val
        if self.debug:
            print("[DEBUG UNPARSER] No further collapse for path:", section_path)
        return section_path, section_dict

    def unparse(self):
        if self.debug:
            print("[DEBUG UNPARSER] Starting unparse process.")
        output = ""
        config_data = self._get_config_data()
        if self.debug:
            print("[DEBUG UNPARSER] Retrieved config data:", config_data)

        # 1) Dump any top-level standalone comments first.
        top_comments = config_data.get("__comments__", [])
        if self.debug:
            print("[DEBUG UNPARSER] Top-level comments found:", top_comments)
        for comment_line in top_comments:
            output += comment_line + "\n"
        if top_comments:
            output += "\n"

        # 2) Go through all top-level keys (skipping __comments__).
        for key, value in config_data.items():
            if key == "__comments__":
                continue
            if self.debug:
                print("[DEBUG UNPARSER] Unparsing top-level key:", key)
            # If the value is a dict, attempt to collapse nested sections into a single header.
            if isinstance(value, dict):
                collapsed_path, collapsed_section = self._collapse_section([key], value)
                if self.debug:
                    print("[DEBUG UNPARSER] Collapsed top-level section for key:", key, "to path:", collapsed_path)
                output += self.unparse_section(collapsed_section, collapsed_path)
            else:
                line = f"{key} = {self.format_value(value)}\n"
                output += line
                if self.debug:
                    print("[DEBUG UNPARSER] Formatted top-level assignment:", line.strip())

        final_output = output.rstrip("\n")
        if self.debug:
            print("[DEBUG UNPARSER] Final unparsed output:", final_output)
        return final_output

    def __str__(self):
        return self.unparse()
