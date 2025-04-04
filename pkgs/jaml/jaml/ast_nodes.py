from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Node:
    """
    Base class for all AST nodes.
    """
    pass


@dataclass
class ScalarNode(Node):
    """
    Represents a single scalar value (string, int, float, bool, null, etc.).
    Attributes:
        value: The underlying Python data (e.g., str, int, float, bool, None).
    """
    value: Any


@dataclass
class ArrayNode(Node):
    """
    Represents an array-like structure [ ... ] in JML.
    Attributes:
        items: A list of Node objects that comprise the elements of the array.
    """
    items: List[Node] = field(default_factory=list)


@dataclass
class TableNode(Node):
    """
    Represents an inline table { ... } in JML.
    Attributes:
        keyvalues: A list of KeyValueNode objects representing the table's content.
    """
    keyvalues: List["KeyValueNode"] = field(default_factory=list)


@dataclass
class LogicExpressionNode(Node):
    """
    Represents a logical or evaluable expression in JML.
    Attributes:
        expression: The raw expression string.
    """
    expression: str


@dataclass
class KeyValueNode(Node):
    """
    Represents a single key-value pair in a JML section.
    Attributes:
        key: The string key (e.g. 'mykey').
        type_annotation: An optional string describing the data type (e.g. 'int', 'str').
        value: A Node representing the value.
    """
    key: str
    type_annotation: Optional[str] = None
    value: Optional[Node] = None


@dataclass
class SectionNode(Node):
    """
    Represents a named section [section_name] in a JML file.
    Attributes:
        name: The section name.
        keyvalues: A list of KeyValueNode objects belonging to this section.
    """
    name: str
    keyvalues: List[KeyValueNode] = field(default_factory=list)


@dataclass
class DocumentNode(Node):
    """
    Represents the entire JML document.
    Attributes:
        sections: A list of SectionNode objects.
    """
    sections: List[SectionNode] = field(default_factory=list)

    def to_plain_data(self) -> dict:
        """
        Convert the AST into a plain dictionary (for non-round-trip usage).
        This method uses the helper function `node_to_plain` to convert
        each AST node into its underlying Python value.
        """
        plain = {}

        for section in self.sections:
            section_data = {}
            for kv in section.keyvalues:
                # Convert each value node to its plain Python value.
                section_data[kv.key] = node_to_plain(kv.value)
            # Namespace merging: split section name by '.' and nest accordingly.
            parts = section.name.split('.')
            current = plain
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            # Merge if the last part already exists.
            if parts[-1] in current and isinstance(current[parts[-1]], dict):
                current[parts[-1]].update(section_data)
            else:
                current[parts[-1]] = section_data

        return plain


def node_to_plain(node: Optional[Node]) -> Any:
    """
    Recursively convert an AST node into its plain Python value.
      - For ScalarNode: return the underlying value.
      - For ArrayNode: return a list of plain values.
      - For TableNode: return a dict of key-values.
      - For LogicExpressionNode: return a representation of the expression.
      - Fallback: return the string representation.
    """
    if node is None:
        return None
    if isinstance(node, ScalarNode):
        return node.value
    elif isinstance(node, ArrayNode):
        return [node_to_plain(item) for item in node.items]
    elif isinstance(node, TableNode):
        return {kv.key: node_to_plain(kv.value) for kv in node.keyvalues}
    elif isinstance(node, LogicExpressionNode):
        return f"<Expression: {node.expression}>"
    else:
        return str(node)
