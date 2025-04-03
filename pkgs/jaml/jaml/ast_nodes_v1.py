"""
ast_nodes.py

This module defines the Abstract Syntax Tree (AST) nodes required for our custom JML markup language.
These nodes store not only the structured data (sections, key–value pairs, values, etc.) but also the
original formatting and comments needed for round-trip serialization.
"""

class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self, comments=None):
        self.comments = comments or []  # List of comment strings.

    def to_jml(self) -> str:
        """Convert the AST node back to its JML string representation.
        Subclasses should override this to produce round-trip output."""
        raise NotImplementedError

    def to_plain_data(self):
        """
        Convert this node into a plain Python data structure (dict, list, str, float, bool, or None).
        By default, raise NotImplementedError so subclasses must implement it.
        """
        raise NotImplementedError


class DocumentNode(ASTNode):
    """Represents the entire JML document."""
    def __init__(self, sections, comments=None):
        super().__init__(comments)
        self.sections = sections  # List of SectionNode objects.

    def to_jml(self) -> str:
        parts = []
        for section in self.sections:
            parts.append(section.to_jml())
        return "\n\n".join(parts)

    def to_plain_data(self):
        """
        Convert the entire document into a plain dict of {section_name: dict_of_key_values}.
        """
        result = {}
        for section in self.sections:
            result[section.name] = section.to_plain_data()
        return result


class SectionNode(ASTNode):
    """Represents a section in the JML file (e.g., [section])."""
    def __init__(self, name, keyvalues, comments=None):
        super().__init__(comments)
        self.name = name          # Section name as a string.
        self.keyvalues = keyvalues  # List of KeyValueNode objects.

    def to_jml(self) -> str:
        lines = []
        # Optionally, emit comments for the section.
        for comment in self.comments:
            lines.append(f"# {comment}")
        lines.append(f"[{self.name}]")
        for kv in self.keyvalues:
            lines.append(kv.to_jml())
        return "\n".join(lines)

    def to_plain_data(self):
        """
        Convert this section's key-values into a dict of {key: plain_value}.
        """
        section_dict = {}
        for kv in self.keyvalues:
            section_dict[kv.key] = kv.to_plain_data()
        return section_dict


class KeyValueNode(ASTNode):
    """Represents a key–value pair with a type annotation (and optionally embedded logic)."""
    def __init__(self, key, type_annotation, value, logic=None, comments=None):
        super().__init__(comments)
        self.key = key                  # The key as a string.
        self.type_annotation = type_annotation  # e.g., 'str', 'int', 'list', etc.
        self.value = value              # A ScalarNode, ArrayNode, TableNode, etc.
        self.logic = logic              # A LogicExpressionNode (if this key's value is dynamic)

    def to_jml(self) -> str:
        # Emit comments if any.
        comment_lines = [f"# {c}" for c in self.comments]
        # Convert the value to its JML representation.
        value_str = self.value.to_jml() if hasattr(self.value, "to_jml") else str(self.value)
        # If there's embedded logic, preserve the original raw logic.
        if self.logic:
            value_str = self.logic.raw_text
        return "\n".join(comment_lines + [f"{self.key}: {self.type_annotation} = {value_str}"])

    def to_plain_data(self):
        """
        Convert this key-value node's 'value' to plain data (via value.to_plain_data()).
        """
        if self.logic:
            # If we want to evaluate logic, you'd do so here.
            # For now, let's just store the final plain data from self.value.
            pass
        return self.value.to_plain_data()


class ScalarNode(ASTNode):
    """Represents a scalar value (string, int, float, bool, or null)."""
    def __init__(self, value, comments=None):
        super().__init__(comments)
        self.value = value

    def to_jml(self) -> str:
        if isinstance(self.value, str):
            # Ensure strings are quoted.
            return f'"{self.value}"'
        elif self.value is None:
            return "null"
        else:
            return str(self.value)

    def to_plain_data(self):
        """
        Return the scalar value directly as a Python type: str, int, float, bool, or None.
        """
        return self.value


class ArrayNode(ASTNode):
    """Represents an array (list) value."""
    def __init__(self, items, comments=None):
        super().__init__(comments)
        self.items = items  # List of ASTNodes.

    def to_jml(self) -> str:
        # For round-trip, preserve the inline format.
        items_str = ", ".join(item.to_jml() for item in self.items)
        return f"[{items_str}]"

    def to_plain_data(self):
        """
        Convert each item to plain data and return a Python list.
        """
        return [item.to_plain_data() for item in self.items]


class TableNode(ASTNode):
    """Represents an inline table (dictionary-like structure)."""
    def __init__(self, keyvalues, comments=None):
        super().__init__(comments)
        self.keyvalues = keyvalues  # List of KeyValueNode objects for the inline table.

    def to_jml(self) -> str:
        items_str = ", ".join(
            f"{kv.key} = {kv.value.to_jml() if hasattr(kv.value, 'to_jml') else kv.value}"
            for kv in self.keyvalues
        )
        return f"{{ {items_str} }}"

    def to_plain_data(self):
        """
        Convert this table to a Python dict by iterating over each KeyValueNode
        and converting them to plain data.
        """
        table_dict = {}
        for kv in self.keyvalues:
            table_dict[kv.key] = kv.to_plain_data()
        return table_dict


class LogicExpressionNode(ASTNode):
    """Represents a logical evaluation (conditional expression) that produces a supported data type.
    The raw_text preserves the original text for round-trip purposes.
    """
    def __init__(self, expression, raw_text, comments=None):
        super().__init__(comments)
        self.expression = expression  # The evaluated expression (may be a Python lambda or similar).
        self.raw_text = raw_text      # The original raw text (e.g., '~( "Active" if @user == "Admin" else "Inactive" )')

    def to_jml(self) -> str:
        # For round-trip, output the original raw text.
        return self.raw_text

    def to_plain_data(self):
        """
        Currently, we just store the raw text as a string. If you want real logic evaluation, 
        you could parse self.expression or evaluate it. For now, let's return the raw_text or
        an unevaluated placeholder.
        """
        return self.raw_text
