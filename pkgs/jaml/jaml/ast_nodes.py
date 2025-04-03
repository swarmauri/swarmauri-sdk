# ast_nodes.py

from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Node:
    """
    Base class for all AST nodes. This allows for type hints and 
    a common interface for shared functionality (if needed).
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
    Represents a logical expression or other evaluable expression in JML.
    
    Example: if x > 3 then "yes" else "no"
    
    Attributes:
        expression: The raw expression string, which you could parse or evaluate later.
    """
    expression: str


@dataclass
class KeyValueNode(Node):
    """
    Represents a single key-value pair in a JML section.
    
    Example of a typical line:
        mykey: int = 42
    
    Attributes:
        key: The string key, e.g. 'mykey'.
        type_annotation: An optional string describing the data type (e.g. 'int', 'str'), if present.
        value: A Node representing the value, which might be:
            - ScalarNode (string, bool, number, etc.)
            - ArrayNode
            - TableNode
            - LogicExpressionNode
            - or any other Node type you define.
    """
    key: str
    type_annotation: Optional[str] = None
    value: Optional[Node] = None


@dataclass
class SectionNode(Node):
    """
    Represents a named section [section_name].
    A JML file can have multiple sections.

    Attributes:
        name: The section name (the text within [ ] or [[ ]]).
        keyvalues: A list of KeyValueNode objects belonging to this section.
    """
    name: str
    keyvalues: List[KeyValueNode] = field(default_factory=list)


@dataclass
class DocumentNode(Node):
    """
    Represents the entire JML document, composed of zero or more sections.
    
    Attributes:
        sections: A list of SectionNode objects, each representing a [section].
    """
    sections: List[SectionNode] = field(default_factory=list)

    def to_plain_data(self) -> dict:
        """
        Convert the AST into a plain dictionary (for non-round-trip usage).
        This strips out comments, extra formatting, etc.
        
        For complex cases (nested tables, arrays, or merges), adjust accordingly.

        Returns:
            A dictionary that mirrors the structure of the JML content:
            
            {
              'section_name': {
                  'key': <scalar or nested structure>,
                  ...
              },
              ...
            }
        """
        plain = {}

        for section in self.sections:
            section_data = {}

            for kv in section.keyvalues:
                # Direct ScalarNode (e.g., int, str, bool, null)
                if isinstance(kv.value, ScalarNode):
                    section_data[kv.key] = kv.value.value

                # ArrayNode
                elif isinstance(kv.value, ArrayNode):
                    # Convert each item in the array into a Python value
                    array_values = []
                    for item in kv.value.items:
                        if isinstance(item, ScalarNode):
                            array_values.append(item.value)
                        elif isinstance(item, TableNode):
                            array_values.append(self._table_to_dict(item))
                        elif isinstance(item, ArrayNode):
                            # Recursively handle nested arrays
                            array_values.append(self._array_to_list(item))
                        else:
                            array_values.append(str(item))
                    section_data[kv.key] = array_values

                # TableNode
                elif isinstance(kv.value, TableNode):
                    section_data[kv.key] = self._table_to_dict(kv.value)

                # LogicExpressionNode
                elif isinstance(kv.value, LogicExpressionNode):
                    # Option 1: store the expression string
                    # Option 2: evaluate it now (if you have an evaluation context)
                    section_data[kv.key] = f"<Expression: {kv.value.expression}>"

                # Fallback for unknown node type
                else:
                    section_data[kv.key] = str(kv.value)

            plain[section.name] = section_data

        return plain

    def _table_to_dict(self, table_node: TableNode) -> dict:
        """
        Helper to convert a TableNode into a Python dict.
        """
        result = {}
        for kv in table_node.keyvalues:
            if isinstance(kv.value, ScalarNode):
                result[kv.key] = kv.value.value
            elif isinstance(kv.value, TableNode):
                result[kv.key] = self._table_to_dict(kv.value)
            elif isinstance(kv.value, ArrayNode):
                result[kv.key] = self._array_to_list(kv.value)
            else:
                result[kv.key] = str(kv.value)
        return result

    def _array_to_list(self, array_node: ArrayNode) -> list:
        """
        Helper to convert an ArrayNode into a plain Python list.
        """
        items = []
        for item in array_node.items:
            if isinstance(item, ScalarNode):
                items.append(item.value)
            elif isinstance(item, TableNode):
                items.append(self._table_to_dict(item))
            elif isinstance(item, ArrayNode):
                items.append(self._array_to_list(item))
            else:
                items.append(str(item))
        return items
