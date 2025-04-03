# unparser.py

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
        """
        Main entry point: returns the entire JML as a string.
        """
        lines = []
        for section in self.ast.sections:
            lines.append(self._unparse_section(section))
        return "\n".join(lines)

    def _unparse_section(self, section: SectionNode) -> str:
        """
        Unparse a single section into JML lines.
        
        Format:
        
            [section_name]
            key: type_annotation = value
            ...
        """
        result_lines = []
        # Section header line
        result_lines.append(f"[{section.name}]")

        # Key-value lines
        for kv in section.keyvalues:
            kv_line = self._unparse_keyvalue(kv)
            # If you prefer to avoid blank lines, you can omit them
            if kv_line:
                result_lines.append(kv_line)

        # Blank line after each section
        result_lines.append("")
        return "\n".join(result_lines)

    def _unparse_keyvalue(self, kv_node: KeyValueNode) -> str:
        """
        Convert a single KeyValueNode to a string like:
            my_key: str = "hello"
        or:
            my_list: list = [1, 2, 3]
        """
        key = kv_node.key
        # Use the node's type_annotation if present; otherwise guess
        type_ann = kv_node.type_annotation or self._guess_type_annotation(kv_node.value)
        value_str = self._unparse_value(kv_node.value)
        return f"{key}: {type_ann} = {value_str}"

    def _unparse_value(self, node) -> str:
        """
        Convert a value node (ScalarNode, ArrayNode, TableNode, LogicExpressionNode) into JML syntax.
        """
        if isinstance(node, ScalarNode):
            return self._unparse_scalar(node)
        elif isinstance(node, ArrayNode):
            return self._unparse_array(node)
        elif isinstance(node, TableNode):
            return self._unparse_table(node)
        elif isinstance(node, LogicExpressionNode):
            # You might store the raw string or reconstruct from sub-nodes if you had them
            return f"<Expression: {node.expression}>"
        else:
            # Fallback
            return str(node)

    def _unparse_scalar(self, scalar: ScalarNode) -> str:
        """
        Convert a ScalarNode (string, bool, int, float, null, etc.) to a JML-compliant string.
        """
        val = scalar.value

        # Strings: wrap in quotes
        if isinstance(val, str):
            # Naive approach: does not escape quotes inside the string
            return f"\"{val}\""
        # Booleans
        elif isinstance(val, bool):
            return "true" if val else "false"
        # Null
        elif val is None:
            return "null"
        # Everything else (int, float, etc.)
        else:
            return str(val)

    def _unparse_array(self, array_node: ArrayNode) -> str:
        """
        Convert an ArrayNode into JML array syntax:
          [item1, item2, item3]
        """
        items_str = []
        for item in array_node.items:
            items_str.append(self._unparse_value(item))
        return f"[{', '.join(items_str)}]"

    def _unparse_table(self, table_node: TableNode) -> str:
        """
        Convert a TableNode into JML inline table syntax:
          { key1 = val1, key2 = val2 }
        """
        pairs = []
        for kv in table_node.keyvalues:
            val_str = self._unparse_value(kv.value)
            pairs.append(f"{kv.key} = {val_str}")
        # You can add spacing/formatting as you prefer
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
