# ast_nodes.py - Updated with equality methods for SequenceNode (and MappingNode)


class Node:
    """
    Base class for all YAML AST nodes.

    Attributes:
        leading_comments (list of str): Comments preceding this node.
        trailing_comments (list of str): Comments following this node.
        tag (str or None): YAML tag/type hint (e.g., "!!str", "!CustomTag").
        anchor (str or None): Anchor name if this node is anchored (e.g., &anchorName).
        alias_of (str or None): If this node is an alias (e.g., *anchorName), this stores the referenced anchor name.
    """

    def __init__(self):
        self.leading_comments = []  # Comments before the node
        self.trailing_comments = []  # Comments after the node
        self.tag = None
        self.anchor = None
        self.alias_of = None

    def is_alias(self):
        return self.alias_of is not None

    def has_anchor(self):
        return self.anchor is not None

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} tag={self.tag!r} "
            f"anchor={self.anchor!r} alias_of={self.alias_of!r}>"
        )


class DocumentNode(Node):
    """
    Represents a single YAML document.

    Attributes:
        root (Node): The root node of the document (MappingNode, SequenceNode, or ScalarNode).
        has_doc_start (bool): True if the document start marker '---' was encountered.
        has_doc_end (bool): True if the document end marker '...' was encountered.
    """

    def __init__(self):
        super().__init__()
        self.root = None
        self.has_doc_start = False
        self.has_doc_end = False

    def __getitem__(self, key):
        if self.root and isinstance(self.root, MappingNode):
            return self.root[key]
        raise TypeError("DocumentNode does not contain a subscriptable mapping")

    def __setitem__(self, key, value):
        if self.root and isinstance(self.root, MappingNode):
            self.root[key] = value
        else:
            raise TypeError("DocumentNode does not contain a subscriptable mapping")

    def __eq__(self, other):
        # If other is a DocumentNode, compare all attributes.
        if isinstance(other, DocumentNode):
            return (
                self.has_doc_start == other.has_doc_start
                and self.has_doc_end == other.has_doc_end
                and self.leading_comments == other.leading_comments
                and self.trailing_comments == other.trailing_comments
                and self.root == other.root
            )
        # Otherwise, delegate equality to the root node.
        return self.root == other

    def __repr__(self):
        return (
            f"<DocumentNode doc_start={self.has_doc_start} "
            f"doc_end={self.has_doc_end} root={self.root!r}>"
        )


class MappingNode(Node):
    """
    Represents a YAML mapping (key-value pairs) while preserving key order and merge operators.

    Attributes:
        pairs (list of tuple(Node, Node)): An ordered list of (key, value) node pairs.
        merges (list of Node): A list of nodes specified by merge operators (<<:), if any.
    """

    def __init__(self):
        super().__init__()
        self.pairs = []  # List of tuples: (key_node, value_node)
        self.merges = []  # Nodes merged via the '<<' operator

    def add_pair(self, key_node, value_node):
        self.pairs.append((key_node, value_node))

    def __getitem__(self, key):
        for k, v in self.pairs:
            if hasattr(k, "value") and k.value == key:
                # For plain scalars (no block style, no comments, etc.), return the raw value.
                if isinstance(v, ScalarNode) and v.style is None:
                    return v.value
                return v
        raise KeyError(key)

    def __setitem__(self, key, value):
        for i, (k, _) in enumerate(self.pairs):
            if hasattr(k, "value") and k.value == key:
                self.pairs[i] = (k, value)
                return
        new_key = ScalarNode(key)
        self.add_pair(new_key, value)

    def __eq__(self, other):
        if isinstance(other, MappingNode):
            return self.pairs == other.pairs
        elif isinstance(other, dict):
            converted = {}
            for k, v in self.pairs:
                key = k.value if hasattr(k, "value") else k
                # For scalar nodes, use the unboxed value.
                if isinstance(v, ScalarNode):
                    converted[key] = v.value
                else:
                    converted[key] = v
            return converted == other
        return False

    def __repr__(self):
        return f"<MappingNode pairs={self.pairs!r} merges={self.merges!r}>"


class SequenceNode(Node):
    """
    Represents a YAML sequence (an ordered list of items).

    Attributes:
        items (list of Node): The sequence items.
    """

    def __init__(self):
        super().__init__()
        self.items = []

    def add_item(self, item_node):
        self.items.append(item_node)

    def __eq__(self, other):
        if isinstance(other, SequenceNode):
            return self.items == other.items
        elif isinstance(other, list):
            # Convert items: if an item is a ScalarNode, compare its value; otherwise, compare the item directly.
            converted = [
                item.value if hasattr(item, "value") else item for item in self.items
            ]
            return converted == other
        return False

    def __repr__(self):
        return f"<SequenceNode items={self.items!r}>"


class ScalarNode(Node):
    """
    Represents a YAML scalar value (string, int, float, etc.) and captures block style details.

    Attributes:
        value: The scalar value.
        style (str or None): The style of the scalar. Options include:
                             None for plain scalars, '|' for literal, '>' for folded.
        chomping (str or None): The chomping indicator for block scalars ('+', '-', or None).
        lines (list of str or None): The original lines of a block scalar for precise re-emission.
    """

    def __init__(self, value, style=None):
        super().__init__()
        self.value = value
        self.style = style  # None, '|', or '>' (plain, literal, folded)
        self.chomping = None
        self.lines = None

    def __repr__(self):
        return (
            f"<ScalarNode value={self.value!r} style={self.style!r} tag={self.tag!r}>"
        )

    def __eq__(self, other):
        if isinstance(other, ScalarNode):
            return (
                self.value == other.value
                and self.style == other.style
                and self.tag == other.tag
            )
        else:
            return self.value == other


class YamlStream:
    """
    Represents an entire YAML stream which may contain multiple documents.

    Attributes:
        documents (list of DocumentNode): The list of documents in the stream.
    """

    def __init__(self):
        self.documents = []

    def add_document(self, doc: DocumentNode):
        self.documents.append(doc)

    def __eq__(self, other):
        if not isinstance(other, YamlStream):
            return False
        return self.documents == other.documents

    def __repr__(self):
        return f"<YamlStream documents={self.documents!r}>"
