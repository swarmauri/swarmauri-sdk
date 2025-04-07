# unparser.py
import json

from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode
)


class JMLUnparser:
    """
    Converts a DocumentNode AST back into a JML-formatted string.
    
    Usage Example:
        unparser = JMLUnparser(document_node)
        jml_output = unparser.unparse()
    """

    def __init__(self, ast: DocumentNode):
        """
        Initialize the unparser with an AST (DocumentNode).
        """
        self.ast = ast

    def unparse(self) -> str:
        lines = []
        # Emit preamble comments (standalone comments before any section)
        if hasattr(self.ast, "preamble") and self.ast.preamble:
            for comment in self.ast.preamble:
                # Emit the comment exactly as captured (including the "#")
                lines.append(comment.comment)
            lines.append("")  # Blank line after preamble comments

        for section in self.ast.sections:
            lines.append(f"[{section.name}]")
            # Instead of printing section.comments as separate lines,
            # collect them so they can be merged into key–value lines.
            inline_comments = []
            if hasattr(section, "comments") and section.comments:
                inline_comments.extend(comment.comment for comment in section.comments)
            for kv in section.keyvalues:
                # Use the dedicated key–value unparser to generate the line.
                line = self._unparse_keyvalue(kv, inline_comments)
                lines.append(line)
            lines.append("")  # Blank line between sections

        result = "\n".join(lines)
        if not result.startswith("\n"):
            result = "\n" + result
        if not result.endswith("\n"):
            result = result + "\n"
        return result

    def _unparse_keyvalue(self, kv: KeyValueNode, inline_comments=None) -> str:
        """
        Convert a single KeyValueNode to a string while preserving inline comments,
        including the exact whitespace between the closing quote and the comment marker.
        
        Produces output like:
            key = value  # Inline comment: greeting message
        or, if a type annotation exists:
            key: type_annotation = value  # Inline comment: greeting message
        """
        # Build the key-value portion.
        value_str = self._unparse_node(kv.value)
        if kv.type_annotation:
            kv_line = f"{kv.key}: {kv.type_annotation} = {value_str}"
        else:
            kv_line = f"{kv.key} = {value_str}"
        
        # Use the key–value node's inline comment if present,
        # otherwise try to merge a comment from the section.
        comment_text = kv.comment
        if not comment_text and inline_comments:
            comment_text = inline_comments.pop(0)
        
        if comment_text:
            # Count the number of leading spaces in the comment.
            leading_spaces = len(comment_text) - len(comment_text.lstrip(" "))
            # If there are fewer than 2 leading spaces, ensure exactly 2.
            if leading_spaces < 2:
                comment_text = "  " + comment_text.lstrip(" ")
            # If there are 2 or more, leave them as captured.
            kv_line += comment_text
        return kv_line


    def _unparse_node(self, node):
        # For string scalar nodes, use the raw text if available.
        if isinstance(node, ScalarNode) and isinstance(node.value, str):
            if hasattr(node, "raw"):
                return node.raw
            else:
                return json.dumps(node.value)
        elif isinstance(node, ArrayNode):
            # Use the raw representation if it contains newlines.
            if hasattr(node, "raw") and "\n" in node.raw:
                return node.raw
            else:
                return self._unparse_array(node)
        elif isinstance(node, TableNode):
            if hasattr(node, "raw"):
                return node.raw
            parts = []
            for kv in node.keyvalues:
                parts.append(f"{kv.key} = {self._unparse_node(kv.value)}")
            return "{ " + ", ".join(parts) + " }"
        elif isinstance(node, LogicExpressionNode):
            return "{~ " + node.expression + " ~}"
        elif isinstance(node, ScalarNode):
            if isinstance(node.value, bool):
                return "true" if node.value else "false"
            elif node.value is None:
                return "null"
            else:
                return str(node.value)

        else:
            return str(node.to_plain())

    def _unparse_array(self, array_node: ArrayNode) -> str:
        items_str = [self._unparse_node(item) for item in array_node.items]
        return f"[{', '.join(items_str)}]"

    def _unparse_table(self, table_node: TableNode) -> str:
        """
        Convert a TableNode into JML inline table syntax:
          { key1 = val1, key2 = val2 }
        """
        pairs = []
        for kv in table_node.keyvalues:
            pairs.append(f"{kv.key} = {self._unparse_node(kv.value)}")
        return "{ " + ", ".join(pairs) + " }"

    def _guess_type_annotation(self, node) -> str:
        """
        Guess the type of a node if type_annotation is missing.
        """
        if isinstance(node, ScalarNode):
            val = node.value
            if isinstance(val, str):
                return "str"
            elif isinstance(val, bool):
                return "bool"
            elif isinstance(val, int):
                return "int"
            elif isinstance(val, float):
                return "float"
            elif val is None:
                return "null"
            else:
                return "unknown"
        elif isinstance(node, ArrayNode):
            return "list"
        elif isinstance(node, TableNode):
            return "table"
        elif isinstance(node, LogicExpressionNode):
            return "expr"
        else:
            return "unknown"
