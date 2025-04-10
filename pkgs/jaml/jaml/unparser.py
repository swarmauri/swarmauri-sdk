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

        # Build the header based on whether the section is flagged as a table array.
        if isinstance(section_dict, dict) and section_dict.get("__is_table_array__"):
            header = f"[[{'.'.join(section_path)}]]\n"
        else:
            header = f"[{'.'.join(section_path)}]\n"
        output = header

        # If the collapsed section isn't a dict (for example, it's already a multiline inline table),
        # unparse it directly.
        if not isinstance(section_dict, dict):
            inline_result = self.unparse_inline_table(section_dict) + "\n"
            if self.debug:
                print("[DEBUG UNPARSER] Collapsed section is not a dict. Inline table result:", inline_result.strip())
            output += inline_result
            return output

        # Process assignments and nested sections in section_dict
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
                val_str = self.format_value(value["_value"])
                annot = value["_annotation"]
                cmt_str = ""
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

        output_lines = []
        config_data = self._get_config_data()
        if self.debug:
            print("[DEBUG UNPARSER] Retrieved config data:", config_data)

        # 1) Dump top-level standalone comments first.
        top_comments = config_data.get("__comments__", [])
        if self.debug:
            print("[DEBUG UNPARSER] Top-level comments found:", top_comments)
        for comment_line in top_comments:
            output_lines.append(comment_line)
        if top_comments:
            output_lines.append("")  # add an extra newline after comments

        # 2) Process all top-level keys (skipping __comments__).
        for key, value in config_data.items():
            if key == "__comments__":
                continue
            if self.debug:
                print("[DEBUG UNPARSER] Unparsing top-level key:", key)

            # If the value is a dictionary then it represents a section.
            if isinstance(value, dict):
                # Collapse nested sections (if applicable) before unparsing.
                collapsed_path, collapsed_section = self._collapse_section([key], value)
                if self.debug:
                    print("[DEBUG UNPARSER] Collapsed top-level section for key:", key, "to path:", collapsed_path)
                # Unparse the section using unparse_section.
                section_text = self.unparse_section(collapsed_section, collapsed_path)
                output_lines.append(section_text)
            else:
                # Otherwise, treat it as a top-level assignment.
                # Use unparse_node() on the value if it is an AST node; if not, use format_value().
                if hasattr(value, "unparse"):
                    # In case the node itself has an unparse method.
                    line_value = value.unparse()
                elif hasattr(value, "__class__") and str(value.__class__).find(".ast_nodes") != -1:
                    line_value = self.unparse_node(value)
                else:
                    line_value = self.format_value(value)
                line = f"{key} = {line_value}"
                output_lines.append(line)
                if self.debug:
                    print("[DEBUG UNPARSER] Formatted top-level assignment:", line)

        final_output = "\n".join(output_lines).rstrip("\n")
        if self.debug:
            print("[DEBUG UNPARSER] Final unparsed output:", final_output)
        return final_output


    def __str__(self):
        return self.unparse()

    def unparse_node(self, node):
            """
            Recursively convert AST nodes back into their DSL textual representation.
            Handles the following node types:
                1. TableArrayHeader
                2. TableArrayComprehensionHeader
                3. StringExpr
                4. ComprehensionClauses
                5. ComprehensionClause
                6. DottedExpr
                7. PairExpr
                8. AliasClause   (AS)
                9. InClause      (IN)
            If the node is not one of these types, it falls back on str(node).
            """
            # 1. TableArrayHeader: usually a static header or computed header for table arrays.
            from .ast_nodes import (
                TableArrayHeader,
                TableArraySectionNode,
                TableArrayComprehensionHeader,
                StringExpr,
                ComprehensionClauses,
                ComprehensionClause,
                DottedExpr,
                PairExpr,
                AliasClause,
                InClause,
            )

            if isinstance(node, TableArraySectionNode):
                # Produce the header using double brackets.
                header_str = self.unparse_node(node.header)  # unparse header expression
                # Unparse the body (assuming each child is an assignment or nested section)
                body_str = "\n".join(self.unparse_node(child) for child in node.body)
                return f"[[{header_str}]]\n{body_str}"

            if isinstance(node, TableArrayHeader):
                # For table array headers, we want to output using double brackets.
                # If the node has an original string (and no modifications), use it;
                # otherwise, reconstruct from its header expression.
                if hasattr(node, "original") and node.original:
                    return node.original
                else:
                    # Otherwise, compute the header value (wrapped in [[ ]]).
                    return "[[" + self.unparse_node(node.header_expr) + "]]"
            
            # 2. TableArrayComprehensionHeader: similar to TableArrayHeader, but may include additional comprehension details.
            elif isinstance(node, TableArrayComprehensionHeader):
                # If round-trip fidelity is desired, output the original text.
                if hasattr(node, "original") and node.original:
                    return node.original
                else:
                    # Otherwise, reconstruct using both header_expr and clauses.
                    header_part = self.unparse_node(node.header_expr)
                    clauses_part = self.unparse_node(node.clauses)
                    return "[[" + header_part + " " + clauses_part + "]]"
            
            # 3. StringExpr: a concatenated string expression from multiple components.
            elif isinstance(node, StringExpr):
                # If the node carries the original slice and no modifications are done,
                # return the original. Otherwise, join the parts.
                if hasattr(node, "original") and node.original:
                    return node.original
                else:
                    # Join all parts by invoking unparse_node recursively.
                    return "".join(self.unparse_node(part) for part in node.parts)
            
            # 4. ComprehensionClauses: a group of comprehension_clause nodes.
            elif isinstance(node, ComprehensionClauses):
                # Join the unparsed representation of each clause with a space.
                return " ".join(self.unparse_node(clause) for clause in node.clauses)
            
            # 5. ComprehensionClause: one clause in a comprehension.
            elif isinstance(node, ComprehensionClause):
                # Build a string with the form:
                # "for <loop_vars> in <iterable> [if <conditions>]"
                loop_vars_str = " ".join(self.unparse_node(var) for var in node.loop_vars)
                iterable_str = self.unparse_node(node.iterable)
                if node.conditions:
                    conditions_str = " ".join(self.unparse_node(cond) for cond in node.conditions)
                    return f"for {loop_vars_str} in {iterable_str} if {conditions_str}"
                else:
                    return f"for {loop_vars_str} in {iterable_str}"
            
            # 6. DottedExpr: returns the computed dotted value.
            elif isinstance(node, DottedExpr):
                return node.dotted_value
            
            # 7. PairExpr: a key-value pair.
            elif isinstance(node, PairExpr):
                key_str = self.unparse_node(node.key)
                value_str = self.unparse_node(node.value)
                return f"{key_str} = {value_str}"
            
            # 8. AliasClause (AS): output the alias keyword.
            elif isinstance(node, AliasClause):
                return node.original  # or node.keyword if you prefer.
            
            # 9. InClause (IN): output the literal "in".
            elif isinstance(node, InClause):
                return node.original
            
            # Fallback: if the node is a raw token or already a plain value, return its string representation.
            else:
                return str(node)