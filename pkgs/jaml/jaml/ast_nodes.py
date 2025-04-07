from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class Node:
    """
    Base class for all AST nodes.
    """
    def to_plain(self) -> Any:
        # Fallback conversion: simply use string representation.
        return str(self)

@dataclass
class ScalarNode(Node):
    """
    Represents a single scalar value (string, int, float, bool, null, etc.).
    """
    value: Any

    def to_plain(self) -> Any:
        return self.value

@dataclass
class CommentNode(Node):
    comment: str

    def to_plain(self) -> str:
        return self.comment

@dataclass
class ArrayNode(Node):
    """
    Represents an array-like structure [ ... ] in JML.
    """
    items: List[Node] = field(default_factory=list)

    def to_plain(self) -> Any:
        return [item.to_plain() for item in self.items]

@dataclass
class TableNode(Node):
    """
    Represents an inline table { ... } in JML.
    """
    keyvalues: List["KeyValueNode"] = field(default_factory=list)

    def to_plain(self) -> Any:
        return {kv.key: kv.value.to_plain() for kv in self.keyvalues}

@dataclass
class LogicExpressionNode(Node):
    """
    Represents a logical or evaluable expression in JML.
    """
    expression: str

    def to_plain(self) -> Any:
        return f"<Expression: {self.expression}>"

@dataclass
class KeyValueNode(Node):
    key: str
    type_annotation: Optional[str] = None
    value: Optional[Node] = None
    comment: Optional[str] = None  # New field for inline comment

    def to_plain(self) -> Any:
        return self.value.to_plain() if self.value is not None else None


@dataclass
class SectionNode(Node):
    """
    Represents a named section [section_name] in a JML file.
    """
    name: str
    keyvalues: List[KeyValueNode] = field(default_factory=list)

    def to_plain(self) -> Dict[str, Any]:
        # Convert all key-value pairs in this section to plain data.
        return {kv.key: kv.to_plain() for kv in self.keyvalues}

@dataclass
class DocumentNode(Node):
    preamble: List[CommentNode] = field(default_factory=list)
    sections: List[SectionNode] = field(default_factory=list)

    def to_plain_data(self) -> Dict[str, Any]:
        # Your existing conversion logic here.
        plain: Dict[str, Any] = {}
        # Note: preamble comments might not be needed for plain data,
        # but they’re important for round-trip fidelity.
        for section in self.sections:
            section_plain = section.to_plain()
            parts = section.name.split('.')
            current = plain
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            if parts[-1] in current and isinstance(current[parts[-1]], dict):
                current[parts[-1]].update(section_plain)
            else:
                current[parts[-1]] = section_plain
        return plain

    @classmethod
    def from_plain_data(cls, plain: Dict[str, Any]) -> "DocumentNode":
        """
        Convert a plain Python dictionary into a DocumentNode AST.
        This is used for non-round-trip dumps.
        For simplicity, each top-level key becomes a section.
        Extend this logic if you need to handle nested sections.
        """
        document = cls()
        for section_name, section_data in plain.items():
            section = SectionNode(name=section_name)
            for key, value in section_data.items():
                # Wrap the value in a ScalarNode.
                # (Extend this if you need to support nested arrays or tables.)
                scalar = ScalarNode(value=value)
                kv = KeyValueNode(key=key, value=scalar)
                section.keyvalues.append(kv)
            document.sections.append(section)
        return document