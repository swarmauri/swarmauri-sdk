from lark import Transformer, Token, Tree, v_args
from typing import Any, Dict, List, Optional, Union
from ._ast_nodes import (
    BaseNode, StartNode, SectionNode, SectionNameNode, TableArraySectionNode, TableArrayHeaderNode,
    ComprehensionHeaderNode, AssignmentNode, CommentNode, NewlineNode, IntegerNode, BooleanNode, 
    NullNode, FloatNode, StringExprNode, PairExprNode, DottedExprNode, ValueNode,
    InlineTableNode, 
    ListComprehensionNode, InlineTableComprehensionNode, DictComprehensionNode, 
    ComprehensionClausesNode, ComprehensionClauseNode, AliasClauseNode, FoldedExpressionNode,
    SingleQuotedStringNode, TripleQuotedStringNode, TripleBacktickStringNode, BacktickStringNode, FStringNode,
    SingleLineArrayNode, MultiLineArrayNode, 
    GlobalScopedVarNode, LocalScopedVarNode, ContextScopedVarNode, 
    WhitespaceNode, HspacesNode, InlineWhitespaceNode,
    ReservedFuncNode

)
from ._config import Config

class ConfigTransformer(Transformer):
    def __init__(self, debug=True):
        super().__init__()
        self.debug = debug
        self.debug_print("Initializing ConfigTransformer")
        self.data = {"__comments__": []}
        self.current_section = self.data
        self._current_ta_header = None
        self._root_data = self.data
        self.global_env = {}
        self._last_section = None
        self._last_section_name = None

    def debug_print(self, message):
        if self.debug:
            print("[DEBUG TRANSFORMER]", message)

    @v_args(meta=True)
    def start(self, meta, items: List[Any]) -> Config:
        self.debug_print("start() called with items")
        node = StartNode(data=self._root_data, contents=items, origin="", meta=meta)
        node.lines = []
        for item in items:
            if isinstance(item, (SectionNode, AssignmentNode, CommentNode, NewlineNode)):
                node.lines.append(item)
            elif isinstance(item, Tree) and item.data == 'line':
                for child in item.children:
                    if isinstance(child, (SectionNode, AssignmentNode, CommentNode, NewlineNode)):
                        node.lines.append(child)
        node.__comments__ = [item.value for item in node.lines if isinstance(item, CommentNode)]
        node.origin = "source_file"
        node.value = None
        node.meta = meta
        node.global_env = {}

        # Reset current_section to root for top-level assignments
        self.current_section = self._root_data
        for line in node.lines:
            if isinstance(line, AssignmentNode):
                # Handle top-level assignments
                try:
                    key = line.identifier.value
                    value = line.value
                    if isinstance(value, (IntegerNode, FloatNode, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, BooleanNode, NullNode)):
                        value.resolve({}, {})
                        evaluated = value.evaluate()
                        self.current_section[key] = evaluated
                    elif isinstance(value, (SingleLineArrayNode, MultiLineArrayNode)):
                        value.resolve({}, {})
                        self.current_section[key] = value
                    else:
                        self.current_section[key] = value.value
                    self.debug_print(f"assignment(): Added {key} to root")
                except ValueError as e:
                    self.debug_print(f"Evaluation error for {key}: {e}")
                    self.current_section[key] = value.value
            elif isinstance(line, (CommentNode, NewlineNode)):
                pass

        self.current_section = self._root_data
        self._last_section_name = None
        self.debug_print(f"Final data structure: {self._root_data}")
        return Config(node)

    @v_args(meta=True)
    def section(self, meta, items: List[Any]) -> SectionNode:
        self.debug_print(f"section() called with items '{items}'")
        node = SectionNode()
        i = 0
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "HSPACES":
            node.leading_whitespace = items[i]
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "L_SQ_BRACK":
            node.lbrack = items[i]
            i += 1

        # Handle section_name explicitly
        if i < len(items):
            if isinstance(items[i], SectionNameNode):
                node.header = items[i]
            elif isinstance(items[i], Tree) and items[i].data == "section_name":
                # Transform section_name subtree if not already done
                node.header = self.section_name(meta, items[i].children)
            elif isinstance(items[i], (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode)):
                node.header = items[i]
            else:
                self.debug_print(f"Unexpected item at index {i}: {items[i]}")
            if node.header:
                self.debug_print(f"section(): Processing section {node.header.value or 'unknown'}")
                node.value = node.header.value
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "R_SQ_BRACK":
            node.rbrack = items[i]
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "HSPACES":
            node.trailing_whitespace = items[i]
            i += 1
        node.contents = [item for item in items[i:] if not isinstance(item, list) and not isinstance(item, CommentNode) and item is not None]
        node.__comments__ = [item.value for item in items[i:] if isinstance(item, CommentNode)]
        node.origin = node.lbrack.value if node.lbrack else (node.header.origin if node.header else "")
        node.meta = meta
        return node

    @v_args(meta=True)
    def assignment(self, meta, items: List[Any]) -> AssignmentNode:
        self.debug_print(f"assignment() called with items {items}")
        node = AssignmentNode()
        i = 0
        # Optional leading whitespace
        if i < len(items) and ((isinstance(items[i], Token) and items[i].type == "HSPACES") or isinstance(items[i], HspacesNode)):
            node.leading_whitespace = items[i]
            i += 1
        # IDENTIFIER token: e.g., "single"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
            node.identifier = items[i]
            key = items[i].value
            i += 1
        else:
            raise ValueError(f"Expected IDENTIFIER in assignment, got {items[i] if i < len(items) else 'nothing'}")
        
        # Optional type annotation (skip whitespace if any before ':')
        while i < len(items) and (((isinstance(items[i], Token) and items[i].type == "HSPACES") or isinstance(items[i], HspacesNode))):
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].value == ":":
            node.colon = items[i]
            i += 1
            if i < len(items):
                node.type_annotation = items[i]
                i += 1

        # Skip any whitespace tokens before the equals sign
        while i < len(items) and (((isinstance(items[i], Token) and items[i].type == "HSPACES") or isinstance(items[i], HspacesNode))):
            i += 1

        # Equals sign token
        if i < len(items) and isinstance(items[i], Token) and items[i].value == "=":
            node.equals = items[i]
            i += 1
        else:
            raise ValueError(f"Expected '=' at index {i}, got {items[i] if i < len(items) else 'nothing'}")

        # Skip any whitespace tokens after the equals sign
        while i < len(items) and (((isinstance(items[i], Token) and items[i].type == "HSPACES") or isinstance(items[i], HspacesNode))):
            i += 1

        # Now process the value token
        if i < len(items):
            value = items[i]
            if isinstance(value, Token):
                if value.type == "INTEGER":
                    value_node = IntegerNode()
                    value_node.value = value.value
                    value_node.origin = value.value
                    value_node.meta = meta
                    value = value_node
                elif value.type == "FLOAT":
                    value_node = FloatNode()
                    value_node.value = value.value
                    value_node.origin = value.value
                    value_node.meta = meta
                    value = value_node
                elif value.type == "SINGLE_QUOTED_STRING":
                    value_node = SingleQuotedStringNode()
                    # Unquote the string by stripping both single and double quotes.
                    value_node.value = value.value.strip('"\'')
                    value_node.origin = value.value
                    value_node.meta = meta
                    value = value_node
                elif value.type == "BOOLEAN":
                    value_node = BooleanNode()
                    value_node.value = value.value
                    value_node.origin = value.value
                    value_node.meta = meta
                    value_node.resolve({}, {})
                    value = value_node
                elif value.type == "NULL":
                    value_node = NullNode()
                    value_node.value = value.value
                    value_node.origin = value.value
                    value_node.meta = meta
                    value = value_node
            elif isinstance(value, (SingleLineArrayNode, MultiLineArrayNode)):
                value.resolve({}, {})
                self.current_section[key] = value
            node.value = value
            i += 1
        else:
            raise ValueError(f"Expected value in assignment, got {items[i] if i < len(items) else 'nothing'}")
        
        # Handle inline comment (if present)
        if i < len(items) and isinstance(items[i], Tree) and items[i].data == "inline_comment":
            comment_tree = items[i]
            inline_ws = None
            comment = None
            for child in comment_tree.children:
                if isinstance(child, InlineWhitespaceNode):
                    inline_ws = child
                elif isinstance(child, CommentNode):
                    comment = child
            if comment:
                node.inline_comment = Token("INLINE_COMMENT", (inline_ws.value if inline_ws else "") + comment.value)
            i += 1

        node.origin = node.identifier
        node.meta = meta

        # Add to current_section
        if self.current_section is not None:
            key = node.identifier.value
            if isinstance(value, (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode,
                                  TripleBacktickStringNode, IntegerNode, FloatNode, BooleanNode, NullNode,
                                  SingleLineArrayNode, MultiLineArrayNode)):
                processed_value = value.evaluate()
            else:
                processed_value = value.value if hasattr(value, 'value') else value
            if node.type_annotation:
                processed_value = {"_value": processed_value, "_annotation": node.type_annotation}
            self.current_section[key] = processed_value
            self.debug_print(f"assignment(): Added {key} = {processed_value} to section {self._last_section_name or 'root'}")
        else:
            self.debug_print(f"Skipping assignment {key} as no section is active")

        return node




    @v_args(meta=True)
    def value(self, meta, items: List[Any]) -> BaseNode:
        self.debug_print("value() called with items")
        item = items[0]
        if isinstance(item, Token):
            if item.type == "SINGLE_QUOTED_STRING":
                node = SingleQuotedStringNode()
                node.value = item.value.strip('"\'')  # Strip quotes, e.g., '"red"' -> 'red'
                node.origin = item.value
                node.meta = meta
                return node
            if item.type == "INTEGER":
                node = IntegerNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
            elif item.type == "FLOAT":
                node = FloatNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
            elif item.type == "BOOLEAN":
                node = BooleanNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
            elif item.type == "NULL":
                node = NullNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
        return item

    @v_args(meta=True)
    def assignment_value(self, meta, items: List[Any]) -> BaseNode:
        return self.value(meta, items)

    @v_args(meta=True)
    def expr_item(self, meta, items: List[Any]) -> BaseNode:
        item = items[0]
        if isinstance(item, Token):
            if item.type == "INTEGER":
                node = IntegerNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
            elif item.type == "FLOAT":
                node = FloatNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
            elif item.type == "SINGLE_QUOTED_STRING":
                node = SingleQuotedStringNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
                return node
            elif item.type == "IDENTIFIER":
                node = DottedExprNode()
                node.dotted_value = item.value
                node.origin = item.value
                node.value = item.value
                node.meta = meta
                return node
        return item

    @v_args(meta=True)
    def comment_line(self, meta, items: List[Any]) -> CommentNode:
        self.debug_print("comment_line() called with items")
        node = CommentNode()
        node.value = items[0].value
        node.origin = items[0].value + items[1].value
        node.meta = meta
        return node

    @v_args(meta=True)
    def blank_line(self, meta, items: List[Token]) -> NewlineNode:
        self.debug_print("blank_line() called with items")
        node = NewlineNode()
        node.value = "".join(item.value for item in items)
        node.origin = node.value
        node.meta = meta
        return node

    @v_args(meta=True)
    def section_name(self, meta, items: List[Any]) -> SectionNameNode:
        """
        Transform the 'section_name' rule: IDENTIFIER ("." IDENTIFIER)*
        Creates a SectionNameNode with parts, handling IDENTIFIER tokens,
        and also keeps track of DOT tokens.
        Sets self.current_section for subsequent assignments.
        """
        self.debug_print("section_name() called with items")
        node = SectionNameNode()

        if not items or not isinstance(items[0], Token) or items[0].type != "IDENTIFIER":
            raise ValueError(
                f"Expected at least one IDENTIFIER in section_name, got {items[0] if items else 'nothing'}"
            )

        node.parts = []
        node.dots = []
        for item in items:
            if not isinstance(item, Token):
                raise ValueError(f"Expected Token, got {type(item)} = {item}")

            if item.type == "IDENTIFIER":
                node.parts.append(item)
            elif item.type == "DOT":
                # Keep track of the DOT tokens as well
                node.dots.append(item)
            else:
                # If anything else sneaks in, raise an error
                raise ValueError(f"Expected IDENTIFIER or DOT, got {item.type} = {item}")

        # Build the final value from the IDENTIFIER tokens only
        node.value = ".".join(part.value for part in node.parts)

        # Keep original string form, meta info, etc.
        node.origin = node.value
        node.meta = meta

        # If you need the same number of DOT tokens as the "gaps" between identifiers:
        # node.dots = [Token("DOT", ".") for _ in range(len(node.parts) - 1)]
        # or keep them as read from the grammar (the above loop).

        # Build nested dicts for the config data
        parts = node.value.split(".")
        d = self.data
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        section_name = parts[-1]
        self.current_section = d.setdefault(section_name, {})
        self._last_section = self.current_section
        self._last_section_name = node.value
        self.debug_print(f"section_name(): Set current_section to {node.value}")

        return node

    @v_args(meta=True)
    def table_array_section(self, meta, items: List[Any]) -> TableArraySectionNode:
        self.debug_print("table_array_section() called with items")
        node = TableArraySectionNode()
        node.header = items[0]
        node.body = items[1] if len(items) > 1 else []
        node.__comments__ = [item.value for item in node.body if isinstance(item, CommentNode)]
        node.body = [item for item in node.body if not isinstance(item, (CommentNode, NewlineNode))]
        node.origin = f"[[{node.header.emit()}]]"
        node.value = node.header.value
        node.meta = meta
        return node

    @v_args(meta=True)
    def table_array_header(self, meta, items: List[Any]) -> TableArrayHeaderNode:
        self.debug_print("table_array_header() called with items")
        node = TableArrayHeaderNode()
        node.origin = items[0].emit() if hasattr(items[0], "emit") else items[0].value
        node.value = items[0].value
        node.meta = meta
        return node

    @v_args(meta=True)
    def header_comprehension(self, meta, items: List[Any]) -> ComprehensionHeaderNode:
        self.debug_print("header_comprehension() called with items")
        node = ComprehensionHeaderNode()
        node.header_expr = items[0]
        node.clauses = items[1:-1] if len(items) > 2 else []
        node.origin = "".join(item.value if isinstance(item, Token) else item.emit() for item in items)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def concat_expr(self, meta, items: List[Any]) -> StringExprNode:
        """
        Transform the 'concat_expr' rule: string_component (HSPACES? "+" HSPACES? string_component)*
        Creates a StringExprNode with concatenated parts, ignoring HSPACES and '+' tokens.
        """
        node = StringExprNode()
        # Filter items to include only StringNode (from string_component)
        node.parts = [item for item in items if isinstance(item, (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode))]
        # Construct origin using emit() for StringNode objects
        node.origin = " + ".join(item.emit() for item in node.parts)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def string_component(self, meta, items: List[Any]) -> Union[SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode]:
        return items[0]

    @v_args(meta=True)
    def type_annotation(self, meta, items: List[Token]) -> Token:
        return items[0]

    @v_args(meta=True)
    def arithmetic(self, meta, items: List[Any]) -> StringExprNode:
        node = StringExprNode()
        node.parts = items
        node.origin = "".join(item.value if isinstance(item, Token) else item.emit() for item in items)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def pair_expr(self, meta, items: List[Any]) -> PairExprNode:
        """
        Transform the 'pair_expr' rule: (string_expr | IDENTIFIER) (HSPACES? (EQ | COLON) HSPACES? (string_expr | IDENTIFIER))
        Creates a PairExprNode with key and value, handling tokens correctly.
        """
        node = PairExprNode()
        i = 0
        # Handle key (string_expr or IDENTIFIER)
        if i < len(items) and isinstance(items[i], (StringExprNode, Token)):
            if isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
                key_node = DottedExprNode()
                key_node.dotted_value = items[i].value
                key_node.origin = items[i].value
                key_node.value = items[i].value
                key_node.meta = meta
                node.key = key_node
            else:
                node.key = items[i]
            i += 1
        else:
            raise ValueError(f"Expected string_expr or IDENTIFIER at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Skip HSPACES, EQ/COLON, HSPACES
        while i < len(items) and isinstance(items[i], Token) and items[i].type in ("HSPACES", "EQ", "COLON"):
            separator = items[i].value if items[i].type in ("EQ", "COLON") else "="
            i += 1
        # Handle value (string_expr or IDENTIFIER)
        if i < len(items) and isinstance(items[i], (StringExprNode, Token)):
            if isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
                value_node = DottedExprNode()
                value_node.dotted_value = items[i].value
                value_node.origin = items[i].value
                value_node.value = items[i].value
                value_node.meta = meta
                node.value = value_node
            else:
                node.value = items[i]
        else:
            raise ValueError(f"Expected string_expr or IDENTIFIER at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Construct origin safely
        node.origin = f"{node.key.emit()} {separator} {node.value.emit()}"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def dotted_expr(self, meta, items: List[Token]) -> DottedExprNode:
        node = DottedExprNode()
        node.dotted_value = ".".join(item.value for item in items)
        node.origin = node.dotted_value
        node.value = node.dotted_value
        node.meta = meta
        return node

    @v_args(meta=True)
    def string_expr(self, meta, items: List[Any]) -> StringExprNode:
        node = StringExprNode()
        node.parts = items
        node.origin = " + ".join(item.emit() for item in items)
        node.value = node.origin
        node.meta = meta
        return node


    @v_args(meta=True)
    def array_item(self, meta, items: List[Any]) -> ValueNode:
        self.debug_print("array_item() called with items")
        node = ValueNode()
        i = 0

        # Process the value (if present)
        if i < len(items) and items[i] is not None and not (isinstance(items[i], Token) and items[i].type == "COMMENT"):
            if isinstance(items[i], Tree):
                node.value = self.value(meta, items[i].children)
            else:
                node.value = items[i]
            i += 1
        else:
            node.value = None  # No value; likely a comment-only item

        # Handle inline comment
        if i < len(items) and isinstance(items[i], Tree) and items[i].data == "inline_comment":
            inline_ws = None
            comment = None
            for child in items[i].children:
                if isinstance(child, InlineWhitespaceNode):
                    inline_ws = child
                elif isinstance(child, CommentNode):
                    comment = child
            if comment:
                node.inline_comment = Token("INLINE_COMMENT", (inline_ws.value if inline_ws else "") + comment.value)
            i += 1

        # Handle post-item comments
        if i < len(items) and (isinstance(items[i], list) or (isinstance(items[i], Tree) and items[i].data == "post_item_comments")):
            if isinstance(items[i], list):
                extra_comments = [item.value for item in items[i] if item is not None and hasattr(item, "value")]
            else:
                extra_comments = [child.value for child in items[i].children if child is not None and hasattr(child, "value")]
            node.__comments__.extend(extra_comments)
            i += 1

        node.origin = node.value.emit() if node.value and hasattr(node.value, "emit") else ""
        node.meta = meta
        return node


    @v_args(meta=True)
    def inline_table(self, meta, items: List[Any]) -> InlineTableNode:
        self.debug_print(f"inline_table() called with items '{items}'")
        node = InlineTableNode()
        node.data = {}
        # Note: the inline_table_items Tree is at index 2.
        if len(items) > 2 and isinstance(items[2], Tree) and items[2].data == "inline_table_items":
            for item in items[2].children:
                if isinstance(item, ValueNode) and isinstance(item.value, AssignmentNode):
                    assignment = item.value
                    # Evaluate the assignment value to convert "10" (string) to 10 (int)
                    evaluated_value = assignment.value.evaluate() if hasattr(assignment.value, "evaluate") else assignment.value
                    node.data[assignment.identifier.value] = evaluated_value
                    self.debug_print(
                        f"[DEBUG INLINE_TABLE]: Added assignment {assignment.identifier.value} with evaluated value {evaluated_value}"
                    )
        emit_items = []
        if len(items) > 2 and isinstance(items[2], Tree) and items[2].children:
            for child in items[2].children:
                if isinstance(child, ValueNode) and isinstance(child.value, AssignmentNode):
                    emit_items.append(child.value.emit())
        node.origin = f"{{{', '.join(emit_items) if emit_items else ''}}}"
        node.value = node.data
        node.meta = meta
        return node


    @v_args(meta=True)
    def inline_table_item(self, meta, items: List[Any]) -> ValueNode:
        self.debug_print(f"inline_table_item() called with items '{items}'")
        node = ValueNode()
        i = 0
        # Handle pre-item comments
        if i < len(items) and isinstance(items[i], list):
            node.__comments__.extend(item.value for item in items[i] if isinstance(item, CommentNode) and item is not None)
            i += 1
        # Handle main item
        if i < len(items):
            if items[i] is None:
                i += 1
            elif isinstance(items[i], Tree) and items[i].data == "inline_assignment":
                # Transform inline_assignment tree to AssignmentNode
                node.value = self.inline_assignment(meta, items[i].children)
                i += 1
            elif isinstance(items[i], (AssignmentNode, CommentNode)):
                node.value = items[i]
                i += 1
            else:
                self.debug_print(f"Skipping unexpected item at index {i}: {items[i]}")
                i += 1
        # Handle inline comment
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "inline_comment":
            node.inline_comment = items[i]
            i += 1
        # Handle post-item comments
        if i < len(items) and isinstance(items[i], list):
            node.__comments__.extend(item.value for item in items[i] if isinstance(item, CommentNode) and item is not None)
        # Set origin safely
        node.origin = node.value.emit() if node.value and hasattr(node.value, "emit") else ""
        node.meta = meta
        return node

    @v_args(meta=True)
    def inline_assignment(self, meta, items: List[Any]) -> AssignmentNode:
        self.debug_print(f"inline_assignment() called with items '{items}'")
        node = AssignmentNode()
        i = 0
        # Leading whitespace
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "HSPACES":
            node.leading_whitespace = items[i]
            i += 1
        # Identifier
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
            node.identifier = items[i]
            i += 1
        else:
            raise ValueError(f"Expected IDENTIFIER at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Whitespace before equals (now supporting HspacesNode or Token('HSPACES'))
        if i < len(items) and (isinstance(items[i], HspacesNode) or (isinstance(items[i], Token) and items[i].type == "HSPACES")):
            node.equals_leading_whitespace = items[i] if isinstance(items[i], HspacesNode) else HspacesNode(items[i].value)
            i += 1
        # Equals sign
        if i < len(items) and isinstance(items[i], Token) and items[i].value == "=":
            node.equals = items[i]
            i += 1
        else:
            raise ValueError(f"Expected '=' at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Whitespace after equals
        if i < len(items) and (isinstance(items[i], HspacesNode) or (isinstance(items[i], Token) and items[i].type == "HSPACES")):
            node.equals_trailing_whitespace = items[i] if isinstance(items[i], HspacesNode) else HspacesNode(items[i].value)
            i += 1
        # Value
        if i < len(items):
            if isinstance(items[i], (SingleQuotedStringNode, IntegerNode, FloatNode, BooleanNode, NullNode, InlineTableNode, SingleLineArrayNode, MultiLineArrayNode)):
                node.value = items[i]
            else:
                node.value = self.value(meta, [items[i]])
            i += 1
        else:
            raise ValueError(f"Expected value at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Inline comment
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "inline_comment":
            node.inline_comment = items[i]
            i += 1
        # Trailing whitespace
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "HSPACES":
            node.trailing_whitespace = items[i]
            i += 1
        node.origin = node.identifier
        node.meta = meta
        self.debug_print(f"[DEBUG INLINE_ASSIGNMENT]: Created AssignmentNode(identifier={node.identifier.value}, value={node.value}, equals_leading_whitespace={node.equals_leading_whitespace}, equals_trailing_whitespace={node.equals_trailing_whitespace})")
        return node

    @v_args(meta=True)
    def list_comprehension(self, meta, items: List[Any]) -> ListComprehensionNode:
        """
        Transform the 'list_comprehension' rule: "[" comprehension_expr (HSPACES | NEWLINE)* comprehension_clauses NEWLINE* "]"
        Creates a ListComprehensionNode with header_expr and clauses, ignoring HSPACES and NEWLINE tokens.
        """
        self.debug_print("list_comprehension() called with items")
        node = ListComprehensionNode()
        i = 0
        # Skip LBRACK
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "LBRACK":
            i += 1
        # Handle comprehension_expr
        if i < len(items):
            node.header_expr = items[i]
            i += 1
        else:
            raise ValueError(f"Expected comprehension_expr at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Skip HSPACES or NEWLINE tokens
        while i < len(items) and isinstance(items[i], Token) and items[i].type in ("HSPACES", "NEWLINE"):
            i += 1
        # Handle comprehension_clauses
        if i < len(items) and isinstance(items[i], ComprehensionClausesNode):
            node.clauses = items[i]
            i += 1
        else:
            node.clauses = None
        # Skip remaining NEWLINE tokens
        while i < len(items) and isinstance(items[i], Token) and items[i].type == "NEWLINE":
            i += 1
        # Construct origin using only header_expr and clauses
        origin_parts = [node.header_expr.emit()]
        if node.clauses:
            origin_parts.append(node.clauses.emit())
        node.origin = f"[{', '.join(origin_parts)}]"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def dict_comprehension(self, meta, items: List[Any]) -> DictComprehensionNode:
        """
        Transform the 'dict_comprehension' rule: "{" NEWLINE* dict_comprehension_pair "for" IDENTIFIER "in" value ("if" value)? NEWLINE* "}"
        Creates a DictComprehensionNode, handling (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode) in dict_comprehension_pair.
        """
        self.debug_print("dict_comprehension() called with items")
        node = DictComprehensionNode()
        i = 0
        # Skip opening brace and NEWLINE*
        while i < len(items) and isinstance(items[i], Token) and items[i].type in ("LBRACE", "NEWLINE"):
            i += 1
        # Handle dict_comprehension_pair
        if i < len(items):
            if isinstance(items[i], Tree) and items[i].data == "dict_comprehension_pair":
                # Transform Tree to PairExprNode
                pair_node = PairExprNode()
                pair_items = items[i].children
                pair_index = 0
                # Handle key
                if pair_index < len(pair_items) and isinstance(pair_items[pair_index], (StringExprNode, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, Token)):
                    if isinstance(pair_items[pair_index], Token) and pair_items[pair_index].type == "IDENTIFIER":
                        key_node = DottedExprNode()
                        key_node.dotted_value = pair_items[pair_index].value
                        key_node.origin = pair_items[pair_index].value
                        key_node.value = pair_items[pair_index].value
                        key_node.meta = meta
                        pair_node.key = key_node
                    else:
                        pair_node.key = pair_items[pair_index]  # StringExprNode or SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode
                    pair_index += 1
                else:
                    raise ValueError(f"Expected string_expr, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, or IDENTIFIER in dict_comprehension_pair at index {pair_index}, got {pair_items[pair_index] if pair_index < len(pair_items) else 'nothing'}")
                # Skip HSPACES, EQ/COLON, HSPACES
                separator = "="
                while pair_index < len(pair_items) and isinstance(pair_items[pair_index], Token) and pair_items[pair_index].type in ("HSPACES", "COLON"):
                    if pair_items[pair_index].type in ("COLON"):
                        separator = pair_items[pair_index].value
                    pair_index += 1
                # Handle value
                if pair_index < len(pair_items) and isinstance(pair_items[pair_index], (StringExprNode, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, Token)):
                    if isinstance(pair_items[pair_index], Token) and pair_items[pair_index].type == "IDENTIFIER":
                        value_node = DottedExprNode()
                        value_node.dotted_value = pair_items[pair_index].value
                        value_node.origin = pair_items[pair_index].value
                        value_node.value = pair_items[pair_index].value
                        value_node.meta = meta
                        pair_node.value = value_node
                    else:
                        pair_node.value = pair_items[pair_index]  # StringExprNode or SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode
                else:
                    raise ValueError(f"Expected string_expr, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, or IDENTIFIER in dict_comprehension_pair at index {pair_index}, got {pair_items[pair_index] if pair_index < len(pair_items) else 'nothing'}")
                pair_node.origin = f"{pair_node.key.emit()} {separator} {pair_node.value.emit()}"
                pair_node.value = pair_node.origin
                pair_node.meta = meta
                node.pair = pair_node
                i += 1
            elif isinstance(items[i], PairExprNode):
                node.pair = items[i]
                i += 1
            else:
                raise ValueError(f"Expected PairExprNode or dict_comprehension_pair Tree at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        else:
            raise ValueError(f"Expected dict_comprehension_pair at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Skip "for"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "FOR":
            i += 1
        else:
            raise ValueError(f"Expected FOR token at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Handle IDENTIFIER
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
            node.loop_var = items[i]
            i += 1
        else:
            raise ValueError(f"Expected IDENTIFIER at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Skip "in"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IN":
            i += 1
        else:
            raise ValueError(f"Expected IN token at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Handle value
        if i < len(items):
            node.iterable = items[i]
            i += 1
        else:
            raise ValueError(f"Expected value at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Handle optional "if" value
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IF":
            i += 1
            if i < len(items):
                node.condition = items[i]
                i += 1
            else:
                raise ValueError(f"Expected value after IF at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        else:
            node.condition = None
        # Skip trailing NEWLINE* and closing brace
        while i < len(items) and isinstance(items[i], Token) and items[i].type in ("NEWLINE", "RBRACE"):
            i += 1
        # Construct origin
        origin_parts = []
        if node.pair:
            origin_parts.append(node.pair.emit())
        origin_parts.append(f"for {node.loop_var.value} in {node.iterable.emit()}")
        if node.condition:
            origin_parts.append(f"if {node.condition.emit()}")
        node.origin = f"{{{', '.join(origin_parts)}}}"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def inline_table_comprehension(self, meta, items: List[Any]) -> InlineTableComprehensionNode:
        """
        Transform the 'inline_table_comprehension' rule: "{" NEWLINE* inline_comprehension_pair "for" IDENTIFIER "in" value ("if" value)? NEWLINE* "}"
        Creates a DictComprehensionNode, handling (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode) in inline_comprehension_pair.
        """
        self.debug_print("inline_table_comprehension() called with items")
        node = InlineTableComprehensionNode()
        i = 0
        # Skip opening brace and NEWLINE*
        while i < len(items) and isinstance(items[i], Token) and items[i].type in ("LBRACE", "NEWLINE"):
            i += 1
        # Handle inline_comprehension_pair
        if i < len(items):
            if isinstance(items[i], Tree) and items[i].data == "inline_comprehension_pair":
                # Transform Tree to PairExprNode
                pair_node = PairExprNode()
                pair_items = items[i].children
                pair_index = 0
                # Handle key
                if pair_index < len(pair_items) and isinstance(pair_items[pair_index], (StringExprNode, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, Token)):
                    if isinstance(pair_items[pair_index], Token) and pair_items[pair_index].type == "IDENTIFIER":
                        key_node = DottedExprNode()
                        key_node.dotted_value = pair_items[pair_index].value
                        key_node.origin = pair_items[pair_index].value
                        key_node.value = pair_items[pair_index].value
                        key_node.meta = meta
                        pair_node.key = key_node
                    else:
                        pair_node.key = pair_items[pair_index]  # StringExprNode or SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode
                    pair_index += 1
                else:
                    raise ValueError(f"Expected string_expr, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, or IDENTIFIER in inline_comprehension_pair at index {pair_index}, got {pair_items[pair_index] if pair_index < len(pair_items) else 'nothing'}")
                # Skip HSPACES, EQ/COLON, HSPACES
                separator = "="
                while pair_index < len(pair_items) and isinstance(pair_items[pair_index], Token) and pair_items[pair_index].type in ("HSPACES", "EQ"):
                    if pair_items[pair_index].type in ("EQ"):
                        separator = pair_items[pair_index].value
                    pair_index += 1
                # Handle value
                if pair_index < len(pair_items) and isinstance(pair_items[pair_index], (StringExprNode, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, Token)):
                    if isinstance(pair_items[pair_index], Token) and pair_items[pair_index].type == "IDENTIFIER":
                        value_node = DottedExprNode()
                        value_node.dotted_value = pair_items[pair_index].value
                        value_node.origin = pair_items[pair_index].value
                        value_node.value = pair_items[pair_index].value
                        value_node.meta = meta
                        pair_node.value = value_node
                    else:
                        pair_node.value = pair_items[pair_index]  # StringExprNode or SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode
                else:
                    raise ValueError(f"Expected string_expr, SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode, or IDENTIFIER in inline_comprehension_pair at index {pair_index}, got {pair_items[pair_index] if pair_index < len(pair_items) else 'nothing'}")
                pair_node.origin = f"{pair_node.key.emit()} {separator} {pair_node.value.emit()}"
                pair_node.value = pair_node.origin
                pair_node.meta = meta
                node.pair = pair_node
                i += 1
            elif isinstance(items[i], PairExprNode):
                node.pair = items[i]
                i += 1
            else:
                raise ValueError(f"Expected PairExprNode or inline_comprehension_pair Tree at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        else:
            raise ValueError(f"Expected inline_comprehension_pair at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Skip "for"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "FOR":
            i += 1
        else:
            raise ValueError(f"Expected FOR token at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Handle IDENTIFIER
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
            node.loop_var = items[i]
            i += 1
        else:
            raise ValueError(f"Expected IDENTIFIER at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Skip "in"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IN":
            i += 1
        else:
            raise ValueError(f"Expected IN token at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Handle value
        if i < len(items):
            node.iterable = items[i]
            i += 1
        else:
            raise ValueError(f"Expected value at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        # Handle optional "if" value
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IF":
            i += 1
            if i < len(items):
                node.condition = items[i]
                i += 1
            else:
                raise ValueError(f"Expected value after IF at index {i}, got {items[i] if i < len(items) else 'nothing'}")
        else:
            node.condition = None
        # Skip trailing NEWLINE* and closing brace
        while i < len(items) and isinstance(items[i], Token) and items[i].type in ("NEWLINE", "RBRACE"):
            i += 1
        # Construct origin
        origin_parts = []
        if node.pair:
            origin_parts.append(node.pair.emit())
        origin_parts.append(f"for {node.loop_var.value} in {node.iterable.emit()}")
        if node.condition:
            origin_parts.append(f"if {node.condition.emit()}")
        node.origin = f"{{{', '.join(origin_parts)}}}"
        node.value = node.origin
        node.meta = meta
        return node


    @v_args(meta=True)
    def comprehension_clauses(self, meta, items: List[Any]) -> ComprehensionClausesNode:
        self.debug_print("comprehension_clauses() called with items")
        node = ComprehensionClausesNode()
        node.clauses = items
        node.origin = " ".join(item.emit() for item in items)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def comprehension_clause(self, meta, items: List[Any]) -> ComprehensionClauseNode:
        self.debug_print("comprehension_clause() called with items")
        """
        Transform the 'comprehension_clause' rule: FOR loop_vars IN value (IF comprehension_condition)* NEWLINE*
        Creates a ComprehensionClauseNode with loop_vars, iterable, and conditions.
        """
        node = ComprehensionClauseNode()
        node.loop_vars = items[0] if isinstance(items[0], list) else []
        node.iterable = items[1]
        node.conditions = items[2:] if len(items) > 2 else []
        # Construct origin safely
        loop_vars_str = " ".join(v.emit() if hasattr(v, "emit") else str(v) for v in node.loop_vars)
        iterable_str = node.iterable.emit() if hasattr(node.iterable, "emit") else str(node.iterable)
        conditions_str = " ".join(c.emit() if hasattr(c, "emit") else str(c) for c in node.conditions) if node.conditions else ""
        node.origin = f"for {loop_vars_str} in {iterable_str}" + (f" if {conditions_str}" if conditions_str else "")
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def loop_vars(self, meta, items: List[Any]) -> List:
        self.debug_print("loop_vars() called with items")
        return items

    @v_args(meta=True)
    def loop_var(self, meta, items: List[Any]) -> Any:
        """
        Transform the 'loop_var' rule: dotted_expr alias_clause?
        Creates an AliasClauseNode if alias_clause is present, else returns DottedExprNode.
        """
        self.debug_print("loop_var() called with items")
        if len(items) > 1:
            node = AliasClauseNode()
            node.keyword = "as"
            node.scoped_var = items[1]
            node.origin = f"{items[0].emit()} as {items[1].emit()}"
            node.value = node.origin
            node.meta = meta
            return node
        return items[0]  # DottedExprNode, not string

    @v_args(meta=True)
    def comprehension_condition(self, meta, items: List[Any]) -> StringExprNode:
        """
        Transform the 'comprehension_condition' rule: comp_expr (OPERATOR comp_expr)?
        Creates a StringExprNode with parts, handling OPERATOR tokens correctly.
        """
        self.debug_print("comprehension_condition() called with items")
        node = StringExprNode()
        # Store only comp_expr nodes in parts
        node.parts = [item for item in items if not isinstance(item, Token) or item.type != "OPERATOR"]
        # Construct origin with emit() for nodes and value for tokens
        origin_parts = []
        for item in items:
            if isinstance(item, Token) and item.type == "OPERATOR":
                origin_parts.append(item.value)
            elif hasattr(item, "emit"):
                origin_parts.append(item.emit())
            else:
                origin_parts.append(str(item))  # Fallback
        node.origin = "".join(origin_parts)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def alias_clause(self, meta, items: List[Any]) -> AliasClauseNode:
        self.debug_print("alias_clause() called with items")
        node = AliasClauseNode()
        node.keyword = items[0].value
        node.scoped_var = items[1]
        node.origin = f"{items[0].value} {items[1].emit()}"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def paren_expr(self, meta, items: List[Any]) -> StringExprNode:
        self.debug_print("paren_expr() called with items")
        node = StringExprNode()
        node.parts = items[1:-1]
        node.origin = f"({''.join(item.emit() for item in node.parts)})"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def folded_expr(self, meta, items: List[Any]) -> FoldedExpressionNode:
        """
        Transform the 'folded_expr' rule: FOLDED_START folded_content FOLDED_END
        Creates a FoldedExpressionNode with content_tree.
        """
        self.debug_print("folded_expr() called with items")
        node = FoldedExpressionNode()
        content_items = items[1].children if isinstance(items[1], Tree) else []
        content_str = "".join(item.value if isinstance(item, Token) else item.emit() for item in content_items)
        node.origin = f"<({content_str})>"
        node.content_tree = Tree("folded_content", content_items)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def folded_content(self, meta, items: List[Any]) -> Tree:
        self.debug_print("folded_content() called with items")
        return Tree("folded_content", items)

    @v_args(meta=True)
    def single_line_array(self, meta, items: List[Any]) -> Union[SingleLineArrayNode, MultiLineArrayNode]:
        self.debug_print(f"single_line_array() called with items '{items}'")
        
        # Check for multiline characteristics (NEWLINE tokens, comments, or inline comments)
        has_multiline_features = any(
            isinstance(item, (Token, Tree)) and (
                (isinstance(item, Token) and item.type in ("NEWLINE", "COMMENT")) or
                (isinstance(item, Tree) and (
                    item.data == "inline_comment" or
                    any(
                        isinstance(child, (Token, Tree)) and (
                            (isinstance(child, Token) and child.type in ("NEWLINE", "COMMENT")) or
                            (isinstance(child, Tree) and child.data == "inline_comment")
                        )
                        for child in item.children
                    )
                ))
            )
            for item in items
        )
        
        if has_multiline_features:
            self.debug_print("Delegating to multiline_array due to multiline features")
            return self.multiline_array(meta, items)
        
        # Existing single-line array logic...
        node = SingleLineArrayNode()
        lbrack = None
        rbrack = None
        inline_comment = None
        contents = []
        i = 0

        if i < len(items) and isinstance(items[i], Token) and items[i].type == "L_SQ_BRACK":
            lbrack = items[i]
            i += 1
        
        if i < len(items) and isinstance(items[i], Tree) and items[i].data == "array_content":
            for child in items[i].children:
                if isinstance(child, Tree) and child.data == "array_item":
                    # Transform array_item tree to ValueNode
                    value_node = self.array_item(meta, child.children)
                    if value_node.value is not None:
                        contents.append(value_node)
                elif isinstance(child, ValueNode):
                    contents.append(child)
                elif isinstance(child, Token):
                    # Handle raw value tokens (e.g., INTEGER, STRING, etc.)
                    if child.type == "INTEGER":
                        value_node = IntegerNode()
                        value_node.value = child.value
                        value_node.origin = child.value
                        value_node.meta = meta
                        contents.append(ValueNode(value=value_node))
                    elif child.type == "FLOAT":
                        value_node = FloatNode()
                        value_node.value = child.value
                        value_node.origin = child.value
                        value_node.meta = meta
                        contents.append(ValueNode(value=value_node))
                    elif child.type == "SINGLE_QUOTED_STRING":
                        value_node = SingleQuotedStringNode()
                        value_node.value = child.value.strip('"\'')
                        value_node.origin = child.value
                        value_node.meta = meta
                        contents.append(ValueNode(value=value_node))
                    elif child.type == "BOOLEAN":
                        value_node = BooleanNode()
                        value_node.value = child.value
                        value_node.origin = child.value
                        value_node.meta = meta
                        value_node.resolve({}, {})
                        contents.append(ValueNode(value=value_node))
                    elif child.type == "NULL":
                        value_node = NullNode()
                        value_node.value = child.value
                        value_node.origin = child.value
                        value_node.meta = meta
                        contents.append(ValueNode(value=value_node))
                    # Add other token types as needed
                elif isinstance(child, Token) and child.type == "COMMA":
                    continue
            i += 1
        elif i < len(items) and isinstance(items[i], Token) and items[i].type == "inline_comment":
            inline_comment = items[i]
            i += 1
        elif i < len(items) and isinstance(items[i], InlineWhitespaceNode):
            i += 1
            if i < len(items) and isinstance(items[i], Token) and items[i].type == "inline_comment":
                inline_comment = items[i]
                i += 1
        
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "R_SQ_BRACK":
            rbrack = items[i]
            i += 1
        
        # Build content string safely
        content_parts = []
        for item in contents:
            if item.value:
                value_str = item.value.emit() if hasattr(item.value, "emit") else str(item.value)
                # Safely handle inline_comment
                if hasattr(item, "inline_comment") and item.inline_comment:
                    content_parts.append(f"{value_str} {item.inline_comment.value}")
                else:
                    content_parts.append(value_str)
        content_str = ", ".join(content_parts) if content_parts else ""
        if inline_comment and not contents:
            content_str += f" {inline_comment.value}" if content_str else inline_comment.value
        origin = f"[{content_str}]"
        
        node.origin = origin
        node.lbrack = lbrack
        node.rbrack = rbrack
        node.contents = contents
        node.inline_comment = inline_comment
        node.value = [item.value.evaluate() for item in contents if item.value] if contents else []
        node.meta = meta
        node.resolve({}, {})
        self.debug_print(f"single_line_array(): Created node with value {node.value}, origin {node.origin}")
        return node

    @v_args(meta=True)
    def multiline_array(self, meta, items: List[Any]) -> MultiLineArrayNode:
        self.debug_print(f"multiline_array() called with items '{items}'")
        node = MultiLineArrayNode()
        i = 0
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "L_SQ_BRACK":
            node.lbrack = items[i]
            i += 1
        while i < len(items) and isinstance(items[i], Token) and items[i].type == "NEWLINE":
            node.leading_newlines = node.leading_newlines or []
            node.leading_newlines.append(items[i])
            i += 1
        if i < len(items) and isinstance(items[i], Tree) and items[i].data == "array_content":
            node.contents = []
            node.__comments__ = []
            array_content = items[i].children
            j = 0
            while j < len(array_content):
                child = array_content[j]
                if isinstance(child, Tree) and child.data == "array_item":
                    # Transform array_item (e.g., '3' with '# third')
                    value_node = self.array_item(meta, child.children)
                    node.contents.append(value_node)
                    if value_node.inline_comment:
                        node.__comments__.append(value_node.inline_comment.value)
                    if value_node.__comments__:
                        node.__comments__.extend(value_node.__comments__)
                    j += 1
                # NEW: if the child is already a ValueNode, add it directly.
                elif isinstance(child, ValueNode):
                    node.contents.append(child)
                    j += 1
                # Handle children already built as AST value nodes.
                elif isinstance(child, (IntegerNode, FloatNode, SingleQuotedStringNode, BooleanNode, NullNode)):
                    wrapped = ValueNode()
                    wrapped.value = child
                    wrapped.meta = meta
                    j += 1
                    # Check for succeeding inline comment (e.g., '# first')
                    if j < len(array_content) and isinstance(array_content[j], Tree) and array_content[j].data == "inline_comment":
                        inline_ws = None
                        comment = None
                        for subchild in array_content[j].children:
                            if isinstance(subchild, InlineWhitespaceNode):
                                inline_ws = subchild
                            elif isinstance(subchild, CommentNode):
                                comment = subchild
                        if comment:
                            wrapped.inline_comment = Token("INLINE_COMMENT", (inline_ws.value if inline_ws else "") + comment.value)
                            node.__comments__.append(wrapped.inline_comment.value)
                        j += 1
                    # Skip comma if present.
                    if j < len(array_content) and isinstance(array_content[j], Token) and array_content[j].type == "COMMA":
                        j += 1
                    node.contents.append(wrapped)
                elif isinstance(child, Token) and child.type in ("INTEGER", "FLOAT", "SINGLE_QUOTED_STRING", "BOOLEAN", "NULL"):
                    # Create a new ValueNode for a raw token.
                    value_node = {
                        "INTEGER": IntegerNode,
                        "FLOAT": FloatNode,
                        "SINGLE_QUOTED_STRING": SingleQuotedStringNode,
                        "BOOLEAN": BooleanNode,
                        "NULL": NullNode
                    }[child.type]()
                    value_node.value = child.value if child.type != "SINGLE_QUOTED_STRING" else child.value.strip('"\'')
                    value_node.origin = child.value
                    value_node.meta = meta
                    if child.type == "BOOLEAN":
                        value_node.resolve({}, {})
                    wrapped = ValueNode()
                    wrapped.value = value_node
                    wrapped.meta = meta
                    j += 1
                    if j < len(array_content) and isinstance(array_content[j], Tree) and array_content[j].data == "inline_comment":
                        inline_ws = None
                        comment = None
                        for subchild in array_content[j].children:
                            if isinstance(subchild, InlineWhitespaceNode):
                                inline_ws = subchild
                            elif isinstance(subchild, CommentNode):
                                comment = subchild
                        if comment:
                            wrapped.inline_comment = Token("INLINE_COMMENT", (inline_ws.value if inline_ws else "") + comment.value)
                            node.__comments__.append(wrapped.inline_comment.value)
                        j += 1
                    if j < len(array_content) and isinstance(array_content[j], Token) and array_content[j].type == "COMMA":
                        j += 1
                    node.contents.append(wrapped)
                elif isinstance(child, Tree) and child.data == "inline_comment":
                    # Handle standalone inline comment.
                    inline_ws = None
                    comment = None
                    for subchild in child.children:
                        if isinstance(subchild, InlineWhitespaceNode):
                            inline_ws = subchild
                        elif isinstance(subchild, CommentNode):
                            comment = subchild
                    if comment:
                        wrapped = ValueNode()
                        wrapped.meta = meta
                        wrapped.inline_comment = Token("INLINE_COMMENT", (inline_ws.value if inline_ws else "") + comment.value)
                        wrapped.__comments__.append(wrapped.inline_comment.value)
                        node.contents.append(wrapped)
                        node.__comments__.append(wrapped.inline_comment.value)
                    j += 1
                elif isinstance(child, CommentNode):
                    # Wrap standalone CommentNode.
                    wrapped = ValueNode()
                    wrapped.__comments__.append(child.value)
                    wrapped.meta = meta
                    node.contents.append(wrapped)
                    node.__comments__.append(child.value)
                    j += 1
                elif isinstance(child, Token) and child.type == "NEWLINE":
                    j += 1
                else:
                    j += 1
            i += 1
        while i < len(items) and isinstance(items[i], Token) and items[i].type == "NEWLINE":
            node.trailing_newlines = node.trailing_newlines or []
            node.trailing_newlines.append(items[i])
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "R_SQ_BRACK":
            node.rbrack = items[i]
            i += 1

        # Compute evaluated values, excluding comment-only nodes.
        node.value = [item.value.evaluate() for item in node.contents if item.value is not None]
        node.meta = meta
        node.resolve({}, {})
        self.debug_print(f"multiline_array(): Created node with value {node.value}, comments {node.__comments__}")
        return node


        
    def NEWLINE(self, token: Token) -> NewlineNode:
        """
        Transform the NEWLINE terminal: /\r?\n/
        Creates a NewlineNode with the newline text.
        """
        self.debug_print("NEWLINE() called with token")
        node = NewlineNode()
        return node

    def COMMENT(self, token: Token) -> CommentNode:
        """
        Transform the COMMENT terminal: /#[^\n]*/
        Creates a CommentNode with the comment text.
        """
        self.debug_print("COMMENT() called with token")
        node = CommentNode()
        node.value = token.value
        node.origin = token.value
        return node

    def INLINE_COMMENT(self, token: Token) -> Token:
        """
        Transform the INLINE_COMMENT terminal: /[ \t]+#[^\n]*/
        Returns the token directly for storage in AssignmentNode.inline_comment.
        """
        self.debug_print("INLINE_COMMENT() called with token")
        return token

    def IDENTIFIER(self, token: Token) -> Token:
        """
        Transform the IDENTIFIER terminal: /(?!\b(?:is|not|and|...)\b)\b[a-zA-Z_][a-zA-Z0-9_-]*\b/
        Returns the token directly for use in AssignmentNode, SectionNameNode, etc.
        """
        self.debug_print("IDENTIFIER() called with token")
        return token

    def FLOAT(self, token: Token) -> IntegerNode:
        """
        Transform the FLOAT terminal: /[+-]?(?:\\d+\\.\\d*|\\.\\d+)(?:[eE][+-]?\\d+)?|[+-]?(?:inf|nan)/
        Creates an IntegerNode (simplified; FloatNode could be used if distinct).
        """
        self.debug_print(f"FLOAT() called with token")
        node = FloatNode()
        node.value = token.value
        node.origin = token.value
        return node

    def INTEGER(self, token: Token) -> IntegerNode:
        """
        Transform the INTEGER terminal: /0[oO][0-7]+|0[xX][0-9a-fA-F]+|0[bB][01]+|[+-]?(?:0|[1-9]\\d*)/
        Creates an IntegerNode with the numeric value.
        """
        self.debug_print("INTEGER() called with token")
        node = IntegerNode()
        node.value = token.value
        node.origin = token.value
        return node

    def SINGLE_QUOTED_STRING(self, token):
        node = SingleQuotedStringNode()
        node.value = token.value
        node.origin = token.value
        node.meta = token
        return node

    def TRIPLE_QUOTED_STRING(self, token):
        raw_text = token.value  # e.g. '"""\nsomething\n"""'
        # In TOML-like syntaxes, triple quotes are always at both ends (assuming valid parse).
        # Just strip the first 3 and last 3 chars. If your grammar supports both `"""` and `'''`,
        # you'd detect which is used. For now, assume `"""`.
        if raw_text.startswith('"""') and raw_text.endswith('"""'):
            inner_text = raw_text[3:-3]
        else:
            inner_text = raw_text

        node = TripleQuotedStringNode()
        node.value = inner_text  # store just the contents
        node.origin = token.value  # keep the full original for debugging if desired
        return node

    def BACKTICK_STRING(self, token):
        node = BacktickStringNode()
        node.value = token.value
        node.origin = token.value
        return node

    def F_STRING(self, token):
        node = FStringNode()
        node.value = token.value
        node.origin = token.value
        return node

    def TRIPLE_BACKTICK_STRING(self, token):
        raw_text = token.value  # e.g. '"""\nsomething\n"""'
        # In TOML-like syntaxes, triple quotes are always at both ends (assuming valid parse).
        # Just strip the first 3 and last 3 chars. If your grammar supports both `"""` and `'''`,
        # you'd detect which is used. For now, assume `"""`.
        if raw_text.startswith('```') and raw_text.endswith('```'):
            inner_text = raw_text[3:-3]
        else:
            inner_text = raw_text
        node = TripleBacktickStringNode()
        node.value = inner_text  # store just the contents
        node.origin = token.value  # keep the full original for debugging if desired
        return node

    def RESERVED_FUNC(self, token: Token) -> ReservedFuncNode:
        """
        Transform the RESERVED_FUNC terminal: (File()|Git())
        Creates a ReservedFuncNode for function calls.
        """
        self.debug_print("RESERVED_FUNC() called with token")
        node = ReservedFuncNode()
        node.value = token.value
        node.origin = token.value
        return node

    def BOOLEAN(self, token: Token) -> BooleanNode:
        """
        Transform the BOOLEAN terminal: /(true|false)\b/
        Creates a BooleanNode with boolean value.
        """
        self.debug_print("BOOLEAN() called with token")
        node = BooleanNode()
        node.value = token.value
        node.origin = token.value
        node.resolve({}, {})  # Resolve immediately to set self.resolved
        return node


    def NULL(self, token: Token) -> NullNode:
        self.debug_print("NULL() called with token")
        node = NullNode()
        node.value = token.value  # e.g., "null"
        node.origin = token.value
        node.meta = None
        return node

    def OPERATOR(self, token: Token) -> Token:
        """
        Transform the OPERATOR terminal: |==|!=|>=|<=|->|<<|+|-|*|/|%|>|<(?!{)/
        Returns the token directly for use in StringExprNode or FoldedExpressionNode.
        """
        self.debug_print("OPERATOR() called with token")
        return token


    def GLOBAL_SCOPED_VAR(self, token: Token) -> GlobalScopedVarNode:
        self.debug_print("GLOBAL_SCOPED_VAR() called with token")
        node = GlobalScopedVarNode()
        node.value = token.value
        node.origin = token.value
        node.meta = token  # Optionally, attach token as meta information
        return node

    def LOCAL_SCOPED_VAR(self, token: Token) -> LocalScopedVarNode:
        self.debug_print("LOCAL_SCOPED_VAR() called with token")
        node = LocalScopedVarNode()
        node.value = token.value
        node.origin = token.value
        node.meta = token
        return node

    def CONTEXT_SCOPED_VAR(self, token: Token) -> ContextScopedVarNode:
        self.debug_print("CONTEXT_SCOPED_VAR() called with token")
        node = ContextScopedVarNode()
        node.value = token.value
        node.origin = token.value
        node.meta = token
        return node

    def WHITESPACE(self, token: Token) -> WhitespaceNode:
        self.debug_print("WHITESPACE() called with token")
        node = WhitespaceNode(token.value)
        node.origin = token.value
        node.meta = token  # Attach token meta information
        return node

    def HSPACES(self, token: Token) -> HspacesNode:
        self.debug_print("HSPACES() called with token")
        node = HspacesNode(token.value)
        node.origin = token.value
        node.meta = token
        return node

    def INLINE_WS(self, token: Token) -> InlineWhitespaceNode:
        self.debug_print("INLINE_WS() called with token")
        node = InlineWhitespaceNode(token.value)
        node.origin = token.value
        node.meta = token
        return node
