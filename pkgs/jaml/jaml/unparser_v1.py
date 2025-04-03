"""
unparser.py

This module implements the unparser for our custom JML markup language.
It converts an AST (DocumentNode) into a JML-formatted string or file.
The round-trip methods rely on the AST nodes' to_jml() methods to preserve
formatting, comments, and original logical expressions.
This version outputs inline string values with surrounding quotes to ensure
that string values are rendered as expected.
"""

from .ast_nodes import DocumentNode, SectionNode, KeyValueNode, ScalarNode, ArrayNode, TableNode, LogicExpressionNode

class JMLUnparser:
    """
    A class to unparse a DocumentNode AST back into a JML-formatted string.
    """
    def __init__(self, ast: DocumentNode, strip_inline_quotes: bool = True):
        """
        Initialize the unparser with the AST.
        
        :param ast: The DocumentNode representing the entire JML document.
        :param strip_inline_quotes: Whether to remove surrounding quotes for inline string values.
                                    (This option is now overridden for string types.)
        """
        self.ast = ast
        self.strip_inline_quotes = strip_inline_quotes

    def unparse(self) -> str:
        """
        Convert the stored AST to its JML string representation.
        Inline string values are output with surrounding quotes, ensuring that the
        output meets expected formatting (e.g., preserving trailing newlines exactly).
        """
        lines = []
        for section in self.ast.sections:
            # Output section comments if available.
            if hasattr(section, "comments") and section.comments:
                for comment in section.comments:
                    lines.append(f"# {comment}")
            # Section header.
            lines.append(f"[{section.name}]")

            for kv in section.keyvalues:
                # Output key-value comments if available.
                if hasattr(kv, "comments") and kv.comments:
                    for comment in kv.comments:
                        lines.append(f"# {comment}")

                if (kv.type_annotation == "str" and 
                    isinstance(kv.value, ScalarNode) and 
                    isinstance(kv.value.value, str)):
                    # Get the raw value and escape special characters.
                    value = kv.value.value
                    escaped_value = value.encode("unicode_escape").decode("utf-8")
                    # Always output inline string with surrounding quotes.
                    lines.append(f'{kv.key}: {kv.type_annotation} = "{escaped_value}"')
                else:
                    # For non-string types (or strings not stored as ScalarNode), format them inline.
                    value_str = self._format_value(kv.value, kv.type_annotation)
                    lines.append(f"{kv.key}: {kv.type_annotation} = {value_str}")

            # Blank line between sections.
            lines.append("")
        return "\n".join(lines)

    def _format_value(self, node, type_annotation: str) -> str:
        """
        Format a node that is not a multiline string.
        For inline strings (type "str") we output the value as-is (without quotes).
        For other types, we use a default string conversion.
        
        :param node: The AST node to format.
        :param type_annotation: The type annotation for the node.
        :return: A string representation of the node.
        """
        if isinstance(node, ScalarNode):
            if type_annotation == "str" and isinstance(node.value, str):
                # Output inline string as-is with escape sequences.
                return node.value.encode("unicode_escape").decode("utf-8")
            elif node.value is None:
                return "null"
            else:
                return str(node.value)
        elif isinstance(node, ArrayNode):
            items = [self._format_value(item, "str") if isinstance(item, ScalarNode) and isinstance(item.value, str)
                     else self._format_value(item, "") for item in node.items]
            return f"[{', '.join(items)}]"
        elif isinstance(node, TableNode):
            pairs = []
            for kv in node.keyvalues:
                val_str = self._format_value(kv.value, kv.type_annotation)
                pairs.append(f"{kv.key} = {val_str}")
            return f"{{ {', '.join(pairs)} }}"
        elif hasattr(node, "to_jml"):
            return node.to_jml()
        else:
            return str(node)

def unparse_to_string(ast: DocumentNode) -> str:
    """
    Helper function to unparse a DocumentNode AST to a JML string.
    
    :param ast: A DocumentNode instance representing the parsed JML.
    :return: A JML-formatted string.
    """
    return JMLUnparser(ast).unparse()

def unparse_to_file(ast: DocumentNode, file_path: str) -> None:
    """
    Write the JML string representation of the AST to a file.
    
    :param ast: A DocumentNode instance representing the parsed JML.
    :param file_path: The path of the file to write.
    """
    jml_str = unparse_to_string(ast)
    with open(file_path, "w") as f:
        f.write(jml_str)
