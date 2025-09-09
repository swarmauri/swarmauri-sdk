from lark import Transformer, Token, Tree, v_args
from typing import Any, List, Union, TYPE_CHECKING
from ._ast_nodes import (
    BaseNode,
    StartNode,
    SectionNode,
    SectionNameNode,
    TableArraySectionNode,
    TableArrayHeaderNode,
    ComprehensionHeaderNode,
    AssignmentNode,
    CommentNode,
    NewlineNode,
    IntegerNode,
    BooleanNode,
    NullNode,
    FloatNode,
    StringExprNode,
    PairExprNode,
    DottedExprNode,
    ValueNode,
    InlineTableNode,
    ListComprehensionNode,
    InlineTableComprehensionNode,
    DictComprehensionNode,
    ComprehensionClausesNode,
    ComprehensionClauseNode,
    AliasClauseNode,
    FoldedExpressionNode,
    SingleQuotedStringNode,
    TripleQuotedStringNode,
    TripleBacktickStringNode,
    BacktickStringNode,
    FStringNode,
    SingleLineArrayNode,
    MultiLineArrayNode,
    GlobalScopedVarNode,
    LocalScopedVarNode,
    ContextScopedVarNode,
    WhitespaceNode,
    HspacesNode,
    InlineWhitespaceNode,
    ReservedFuncNode,
)
from ._config import Config

if TYPE_CHECKING:
    from ._ast_nodes import MLArrayItemNode, SLArrayItemNode


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

    # ─────────────────────────────── start ────────────────────────────────
    @v_args(meta=True)
    def start(self, meta, items: List[Any]) -> Config:
        """
        Build the top‑level StartNode, collect all lines (including
        table‑array sections), and prime the raw data‑dict.
        """
        from ._ast_nodes import (
            AssignmentNode,
            CommentNode,
            NewlineNode,
            SectionNode,
            TableArraySectionNode,  # <— include table‑array sections
        )

        self.debug_print("start() called with items")
        node = StartNode(data=self._root_data, contents=items, origin="", meta=meta)
        node.lines = []

        # ─────────────────── collect top‑level lines
        for item in items:
            if isinstance(
                item,
                (
                    SectionNode,
                    TableArraySectionNode,  # <— now captured
                    AssignmentNode,
                    CommentNode,
                    NewlineNode,
                ),
            ):
                node.lines.append(item)
            elif isinstance(item, Tree) and item.data == "line":
                for child in item.children:
                    if isinstance(
                        child,
                        (
                            SectionNode,
                            TableArraySectionNode,  # <— now captured in line children
                            AssignmentNode,
                            CommentNode,
                            NewlineNode,
                        ),
                    ):
                        node.lines.append(child)

        # add parent pointer so children can splice themselves later
        for ln in node.lines:
            if hasattr(ln, "meta") and ln.meta is not None:
                ln.meta.parent = node

        # ───────────────────── prime the raw mapping (unchanged) …
        self.current_section = self._root_data
        for line in node.lines:
            if not isinstance(line, AssignmentNode):
                continue

            # key = line.identifier.value  # unused for now
            # value = line.value  # unused for now

            # (static scalars, arrays, else-as-AST logic remains unchanged)
            # … [rest of existing priming logic] …

        # reset book‑keeping helpers
        self.current_section = self._root_data
        self._last_section_name = None
        self.debug_print(f"Final data structure: {self._root_data}")

        return Config(node)

    # ───────────────────────── section  ──────────────────────────
    @v_args(meta=True)
    def section(self, meta, items: List[Any]) -> SectionNode:
        """
        Handle a section header that can be either:

            • plain dotted IDENTIFIERs        → SectionNameNode
            • header comprehensions            → ComprehensionHeaderNode
            • conditional headers              → header_conditional
            • literal/string headers           → String nodes
        """
        self.debug_print(f"section() called with items '{items}'")

        node = SectionNode()
        i = 0

        # optional leading whitespace
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "HSPACES"
        ):
            node.leading_whitespace = items[i]
            i += 1

        # '['
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "L_SQ_BRACK"
        ):
            node.lbrack = items[i]
            i += 1

        # ── HEADER ─────────────────────────────────────────────────────
        if i < len(items):
            cur = items[i]

            # 1) static section name
            if isinstance(cur, SectionNameNode):
                node.header = cur

            # 2) comprehension header
            elif isinstance(cur, ComprehensionHeaderNode):
                node.header = cur

            # 3) tree-based header branches (untransformed Trees)
            elif isinstance(cur, Tree):
                if cur.data == "section_name":
                    node.header = self.section_name(meta, cur.children)
                elif cur.data == "header_comprehension":
                    # delegate to the header_comprehension transformer
                    node.header = self.header_comprehension(meta, cur.children)
                elif cur.data == "header_conditional":
                    from ._ast_nodes import TableArrayHeaderNode

                    hdr = TableArrayHeaderNode()
                    raw = "".join(
                        child.emit() if hasattr(child, "emit") else child.value
                        for child in cur.children
                    )
                    hdr.origin = raw
                    hdr.value = raw
                    hdr.meta = meta
                    node.header = hdr
                else:
                    self.debug_print(f"Unexpected item at index {i}: {cur}")

            # 4) literal string header
            elif isinstance(
                cur,
                (
                    SingleQuotedStringNode,
                    TripleQuotedStringNode,
                    BacktickStringNode,
                    FStringNode,
                    TripleBacktickStringNode,
                ),
            ):
                node.header = cur

            if node.header is not None:
                node.value = getattr(node.header, "value", None)
            i += 1

        # ']'
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "R_SQ_BRACK"
        ):
            node.rbrack = items[i]
            i += 1

        # optional trailing whitespace
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "HSPACES"
        ):
            node.trailing_whitespace = items[i]
            i += 1

        # contents (assignments, comments, …)
        node.contents = [
            itm
            for itm in items[i:]
            if not isinstance(itm, list)
            and not isinstance(itm, CommentNode)
            and itm is not None
        ]
        node.__comments__ = [
            itm.value for itm in items[i:] if isinstance(itm, CommentNode)
        ]

        # Attach inline comments to preceding assignment
        from ._ast_nodes import AssignmentNode

        for comment_text in node.__comments__:
            for c in reversed(node.contents):
                if isinstance(c, AssignmentNode):
                    c.inline_comment = Token("INLINE_COMMENT", "  " + comment_text)
                    break
        node.__comments__ = []

        node.origin = (
            node.lbrack.value
            if node.lbrack
            else (node.header.origin if node.header else "")
        )
        node.meta = meta

        # ── mount section mapping ────────────────────────────────────────
        if isinstance(node.header, SectionNameNode):
            parts = node.header.value.split(".")
            d = self.data
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            self.current_section = d.setdefault(parts[-1], {})
            self._last_section = self.current_section
            self._last_section_name = node.header.value
            self.debug_print(
                f"section(): Processing static section {node.header.value}"
            )
        else:
            raw_key = (
                node.header.emit() if hasattr(node.header, "emit") else str(node.header)
            )
            self.data[raw_key] = {}
            self.current_section = self.data[raw_key]
            self._last_section = self.current_section
            self._last_section_name = raw_key
            self.debug_print(f"section(): Processing dynamic section {raw_key}")

        # relocate assignments primed into root back into this section
        from ._ast_nodes import AssignmentNode as _AssignmentNode

        for child in node.contents:
            if isinstance(child, _AssignmentNode):
                key = child.identifier.value
                if key in self.data and self.data[key] is not self.current_section:
                    self.data.pop(key, None)
                    if hasattr(child.value, "evaluate"):
                        try:
                            child.value.resolve({}, {}, {})
                        except Exception:
                            pass
                        val = child.value.evaluate()
                    else:
                        val = child.value
                    self.current_section[key] = val
                    self.debug_print(
                        f"section(): Moved assignment '{key}' into section '{self._last_section_name}'"
                    )

        return node

    # ─────────────────────────── assignment ─────────────────────────────
    @v_args(meta=True)
    def assignment(self, meta, items: List[Any]) -> "AssignmentNode":
        self.debug_print(f"assignment() called with items '{items}'")
        from ._ast_nodes import (
            SingleLineArrayNode,
            MultiLineArrayNode,
            InlineTableNode,
            FoldedExpressionNode,
            ListComprehensionNode,
            DictComprehensionNode,
            InlineTableComprehensionNode,
            FStringNode,
            SingleQuotedStringNode,
            TripleQuotedStringNode,
            BacktickStringNode,
            TripleBacktickStringNode,
        )
        from lark import Token, Tree

        node = AssignmentNode()
        i = 0

        def _is_ws(tok) -> bool:
            return isinstance(tok, HspacesNode) or (
                isinstance(tok, Token) and tok.type == "HSPACES"
            )

        # 1) leading whitespace
        if i < len(items) and _is_ws(items[i]):
            node.leading_whitespace = items[i]
            i += 1

        # 2) identifier
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "IDENTIFIER"
        ):
            node.identifier = items[i]
            key = items[i].value
            i += 1

        # 3) optional type‐annotation + WS
        while i < len(items) and _is_ws(items[i]):
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].value == ":":
            node.colon = items[i]
            i += 1
            node.type_annotation = items[i]
            i += 1
        while i < len(items) and _is_ws(items[i]):
            i += 1

        # 4) equals sign
        if i < len(items) and isinstance(items[i], Token) and items[i].value == "=":
            node.equals = items[i]
            i += 1
        while i < len(items) and _is_ws(items[i]):
            i += 1

        # 5) right‐hand side value
        if i >= len(items):
            raise ValueError("Expected value in assignment")
        raw_value = items[i]

        if isinstance(
            raw_value,
            (
                SingleLineArrayNode,
                MultiLineArrayNode,
                InlineTableNode,
                FoldedExpressionNode,
            ),
        ):
            node.value = raw_value
            i += 1
        elif isinstance(raw_value, Token):
            t = raw_value.type
            if t == "INTEGER":
                node.value = IntegerNode(
                    value=raw_value.value, origin=raw_value.value, meta=meta
                )
            elif t == "FLOAT":
                node.value = FloatNode(
                    value=raw_value.value, origin=raw_value.value, meta=meta
                )
            elif t == "BOOLEAN":
                tmp = BooleanNode()
                tmp.value = tmp.origin = raw_value.value
                tmp.resolve({}, {})
                node.value = tmp
            elif t == "NULL":
                node.value = NullNode(
                    value=raw_value.value, origin=raw_value.value, meta=meta
                )
            elif t == "SINGLE_QUOTED_STRING":
                sq = SingleQuotedStringNode()
                sq.origin = raw_value.value
                sq.value = raw_value.value.strip("\"'")
                sq.meta = meta
                node.value = sq
            else:
                node.value = raw_value
            i += 1
        else:
            node.value = raw_value
            i += 1

        # 6) inline comment
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "INLINE_COMMENT"
        ):
            node.inline_comment = items[i]
            i += 1
        elif (
            i < len(items)
            and isinstance(items[i], Tree)
            and items[i].data == "inline_comment"
        ):
            for child in items[i].children:
                if isinstance(child, Token) and child.type == "INLINE_COMMENT":
                    node.inline_comment = child
                    break
            i += 1

        # preserve the raw origin if available
        node.origin = getattr(node.value, "origin", node.identifier.value)
        node.meta = meta

        # 7) Inference & priming into the raw data mapping
        if self.current_section is not None:
            val = node.value
            if isinstance(val, (IntegerNode, FloatNode, BooleanNode, NullNode)):
                processed = val.evaluate()
            elif isinstance(val, InlineTableNode):
                val.resolve(self.data, self.current_section)
                processed = val.evaluate()
            elif isinstance(val, (SingleLineArrayNode, MultiLineArrayNode)):
                val.resolve(self.data, self.current_section)
                processed = val.evaluate()
            elif isinstance(val, FoldedExpressionNode):
                # preserve AST for later resolve
                processed = val
            elif isinstance(
                val,
                (
                    ListComprehensionNode,
                    DictComprehensionNode,
                    InlineTableComprehensionNode,
                ),
            ):
                # store the raw comprehension text, not the node
                processed = val.origin
            elif isinstance(
                val,
                (
                    FStringNode,
                    SingleQuotedStringNode,
                    TripleQuotedStringNode,
                    BacktickStringNode,
                    TripleBacktickStringNode,
                ),
            ):
                processed = val.origin
            else:
                processed = val

            self.current_section[key] = processed
            self.debug_print(
                f"assignment(): Added {key} = {processed!r} to section {self._last_section_name or 'root'}"
            )

        return node

    @v_args(meta=True)
    def value(self, meta, items: List[Any]) -> BaseNode:
        self.debug_print("value() called with items")
        item = items[0]
        if isinstance(item, Token):
            if item.type == "SINGLE_QUOTED_STRING":
                node = SingleQuotedStringNode()
                node.value = item.value.strip(
                    "\"'"
                )  # Strip quotes, e.g., '"red"' -> 'red'
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
            elif item.type == "F_STRING":
                node = FStringNode()
                node.value = item.value
                node.origin = item.value
                node.meta = meta
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
            elif item.type == "F_STRING":
                node = FStringNode()
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

        if (
            not items
            or not isinstance(items[0], Token)
            or items[0].type != "IDENTIFIER"
        ):
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
                raise ValueError(
                    f"Expected IDENTIFIER or DOT, got {item.type} = {item}"
                )

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

    # ───────────────────────── table‑array section ─────────────────────────
    @v_args(meta=True)
    def table_array_section(self, meta, items: List[Any]) -> TableArraySectionNode:
        """
        2) Detect comprehension headers immediately after '[[' and mount them,
        deferring full expansion to render time.
        """
        self.debug_print("table_array_section() called with items")
        if not (
            items and isinstance(items[0], Token) and items[0].type == "L_DBL_SQ_BRACK"
        ):
            raise ValueError("Table-array section must start with '[['")

        # Comprehension-first: header is a ComprehensionHeaderNode
        if len(items) > 1 and isinstance(items[1], ComprehensionHeaderNode):
            comp = items[1]
            node = TableArraySectionNode()
            node.header = comp
            node.body = []
            node.__comments__ = []
            raw_key = comp.origin
            # Mount placeholder into raw data
            self.data[raw_key] = {}
            self.current_section = self.data[raw_key]
            self._last_section = self.current_section
            self._last_section_name = raw_key
            node.origin = f"[[{comp.origin}]]"
            node.value = comp.value
            node.meta = meta
            return node

        # Fallback: static or conditional header
        node = TableArraySectionNode()
        i = 1  # skip '[[' token
        # header node (TableArrayHeaderNode or ComprehensionHeaderNode)
        header = items[i]
        if not isinstance(header, (TableArrayHeaderNode, ComprehensionHeaderNode)):
            raise ValueError("Missing or invalid table‑array header")
        node.header = header
        i += 1
        # skip any newlines between header and closing
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "NEWLINE"
        ):
            i += 1
        # expect ']]'
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "R_DBL_SQ_BRACK"
        ):
            i += 1
        else:
            raise ValueError("Table‑array section header not closed with ']]'")
        # body lines (assignments, comments)
        node.body = [
            itm
            for itm in items[i:]
            if not (isinstance(itm, Token) and itm.type == "NEWLINE")
        ]
        node.__comments__ = [
            itm.value for itm in node.body if isinstance(itm, CommentNode)
        ]
        # mount into raw data
        raw_key = (
            node.header.emit() if hasattr(node.header, "emit") else str(node.header)
        )
        self.data[raw_key] = {}
        self.current_section = self.data[raw_key]
        self._last_section = self.current_section
        self._last_section_name = raw_key
        node.origin = f"[[{raw_key}]]"
        node.value = getattr(node.header, "value", raw_key)
        node.meta = meta
        return node

    @v_args(meta=True)
    def table_array_header(self, meta, items: List[Any]) -> TableArrayHeaderNode:
        self.debug_print("table_array_header() called with items")
        from ._ast_nodes import TableArrayHeaderNode, ComprehensionHeaderNode

        # If the header node is a comprehension header, let it pass through so
        # table_array_section can handle it
        first = items[0]
        if isinstance(first, ComprehensionHeaderNode):
            return first

        node = TableArrayHeaderNode()
        # Handle conditional-header trees (e.g. header_conditional)
        if isinstance(first, Tree) and first.data == "header_conditional":
            # Reconstruct the raw header expression
            raw = "".join(
                child.emit() if hasattr(child, "emit") else child.value
                for child in first.children
            )
            node.origin = raw
            node.value = raw
            node.meta = meta
            return node

        # All other cases (literal node, Token, etc.)
        if hasattr(first, "emit"):
            origin = first.emit()
        elif isinstance(first, Token):
            origin = first.value
        else:
            origin = str(first)
        node.origin = origin

        # Determine the value
        if hasattr(first, "value"):
            node.value = first.value
        elif isinstance(first, Token):
            node.value = first.value
        else:
            node.value = origin

        node.meta = meta
        return node

    # ───────────────────────── header comprehension ──────────────────────────
    @v_args(meta=True)
    def header_comprehension(self, meta, items: List[Any]) -> ComprehensionHeaderNode:
        """
        1) Parse f-string and comprehension clauses into a single node,
        capturing header_expr and clauses for later render.
        """
        self.debug_print("header_comprehension() called with items")
        node = ComprehensionHeaderNode()

        # Wrap raw F_STRING tokens into FStringNode
        head = items[0]
        if isinstance(head, Token) and head.type == "F_STRING":
            wrap = FStringNode()
            wrap.value = head.value
            wrap.origin = head.value
            wrap.meta = meta
            head = wrap
        node.header_expr = head

        # Capture the comprehension clauses
        from ._ast_nodes import ComprehensionClausesNode

        clauses = next(
            (itm for itm in items[1:] if isinstance(itm, ComprehensionClausesNode)),
            None,
        )
        node.clauses = clauses

        # Rebuild origin text for fidelity
        head_text = getattr(head, "origin", getattr(head, "value", str(head)))
        clauses_text = clauses.origin if clauses is not None else ""
        raw = head_text + ("\n" + clauses_text if clauses_text else "")
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        node.origin = "\n".join(lines)

        # Keep the unmodified value for render-phase evaluation
        node.value = raw
        node.meta = meta
        return node

    @v_args(meta=True)
    def concat_expr(self, meta, items: List[Any]) -> StringExprNode:
        """
        Build a concatenation node, dropping PLUS tokens **and** any explicit
        whitespace helpers so downstream code doesn’t have to scrub them.
        """
        from ._ast_nodes import HspacesNode, InlineWhitespaceNode

        node = StringExprNode()
        node.parts = [
            itm
            for itm in items
            if not (
                (isinstance(itm, Token) and itm.type in ("PLUS", "HSPACES"))
                or isinstance(itm, (HspacesNode, InlineWhitespaceNode))
            )
        ]
        node.origin = "".join(
            itm.emit() if hasattr(itm, "emit") else str(itm) for itm in node.parts
        )
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def string_component(
        self, meta, items: List[Any]
    ) -> Union[
        SingleQuotedStringNode,
        TripleQuotedStringNode,
        BacktickStringNode,
        FStringNode,
        TripleBacktickStringNode,
    ]:
        return items[0]

    @v_args(meta=True)
    def type_annotation(self, meta, items: List[Token]) -> Token:
        return items[0]

    @v_args(meta=True)
    def arithmetic(self, meta, items: List[Any]) -> StringExprNode:
        node = StringExprNode()
        node.parts = items
        node.origin = "".join(
            item.value if isinstance(item, Token) else item.emit() for item in items
        )
        node.value = node.origin
        node.meta = meta
        return node

    # ─────────────────────────── pair‑expr ────────────────────────────
    @v_args(meta=True)
    def pair_expr(self, meta, items: List[Any]) -> PairExprNode:
        """
        (string_expr | FStringNode | IDENTIFIER) (HSPACES? (SETTER | COLON) HSPACES? (string_expr | FStringNode | IDENTIFIER))

        Handles either plain identifiers, FStringNode, or StringExprNode‑style keys/values,
        while tolerating both raw HSPACES tokens and the HspacesNode helper
        that earlier rules may have produced.
        """
        node = PairExprNode()
        i = 0

        # ── 1. KEY ──────────────────────────────────────────────────────
        if i < len(items) and isinstance(
            items[i], (StringExprNode, FStringNode, Token)
        ):
            if isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
                key_node = DottedExprNode()
                key_node.dotted_value = key_node.origin = key_node.value = items[
                    i
                ].value
                key_node.meta = meta
                node.key = key_node
            else:
                node.key = items[i]
            i += 1

        # ── 2. skip whitespace & collect the = / : separator ───────────
        separator = "="  # default
        while i < len(items):
            itm = items[i]
            if isinstance(itm, HspacesNode) or (
                isinstance(itm, Token) and itm.type == "HSPACES"
            ):
                i += 1
                continue
            if isinstance(itm, Token) and itm.type in ("SETTER", "COLON"):
                separator = itm.value
                i += 1
                # absorb any whitespace nodes after the symbol
                while (
                    i < len(items)
                    and isinstance(items[i], (HspacesNode, Token))
                    and (
                        isinstance(items[i], HspacesNode) or items[i].type == "HSPACES"
                    )
                ):
                    i += 1
                break
            break

        # ── 3. VALUE ───────────────────────────────────────────────────
        if i < len(items) and isinstance(
            items[i], (StringExprNode, FStringNode, Token)
        ):
            if isinstance(items[i], Token) and items[i].type == "IDENTIFIER":
                value_node = DottedExprNode()
                value_node.dotted_value = value_node.origin = value_node.value = items[
                    i
                ].value
                value_node.meta = meta
                node.value = value_node
            else:
                node.value = items[i]

        # ── 4. bookkeeping ─────────────────────────────────────────────
        # Safely emit key and value (in case one is still None)
        key_emit = node.key.emit() if getattr(node, "key", None) is not None else ""
        val_emit = node.value.emit() if getattr(node, "value", None) is not None else ""
        node.origin = f"{key_emit} {separator} {val_emit}"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def dotted_expr(self, meta, items: List[Token]) -> DottedExprNode:
        node = DottedExprNode()
        node.dotted_value = "".join(item.value for item in items)
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
    def sl_array_item(self, meta, items: List[Any]) -> "SLArrayItemNode":
        self.debug_print("sl_array_item() called with items")
        from ._ast_nodes import SLArrayItemNode, CommentNode
        from lark import Tree, Token

        node = SLArrayItemNode()
        i = 0

        # 1) Process the value or comment-only line
        if i < len(items) and not isinstance(items[i], CommentNode):
            if isinstance(items[i], Tree):
                node.value = self.value(meta, items[i].children)
            else:
                node.value = items[i]
            i += 1
        else:
            # comment-only line
            node.value = None
            # capture the comment text
            if i < len(items) and isinstance(items[i], CommentNode):
                node.inline_comment = Token("INLINE_COMMENT", items[i].value)
            i += 1

        # 2) Handle comma immediately following the value
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "COMMA":
            node.has_comma = True
            i += 1

        # 3) Skip any whitespace tokens
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type in ("WHITESPACE", "HSPACES", "INLINE_WS")
        ):
            i += 1

        # 4) Handle inline comment
        if (
            i < len(items)
            and isinstance(items[i], Tree)
            and items[i].data == "inline_comment"
        ):
            for child in items[i].children:
                if isinstance(child, Token) and child.type == "INLINE_COMMENT":
                    node.inline_comment = child
                    break
            i += 1

        # 5) Set origin for round-trip fidelity
        if hasattr(node.value, "emit"):
            node.origin = node.value.emit()
        else:
            node.origin = str(node.value) if node.value is not None else ""
        node.meta = meta
        return node

    @v_args(meta=True)
    def ml_array_item(self, meta, items: List[Any]) -> "MLArrayItemNode":
        """
        Handle a multiline array item, preserving values, inline comments, and comma.
        Supports both value lines and comment-only lines.
        """
        self.debug_print("ml_array_item() called with items")
        from ._ast_nodes import (
            MLArrayItemNode,
            CommentNode,
            WhitespaceNode,
            HspacesNode,
            InlineWhitespaceNode,
            NewlineNode,
        )
        from lark import Token, Tree

        node = MLArrayItemNode()
        i = 0

        # 1) Skip indentation, whitespace, or newline nodes
        while i < len(items) and (
            isinstance(
                items[i],
                (WhitespaceNode, HspacesNode, InlineWhitespaceNode, NewlineNode),
            )
            or (
                isinstance(items[i], Token)
                and items[i].type in ("WHITESPACE", "HSPACES", "INLINE_WS")
            )
        ):
            i += 1

        # 2) Process the value or comment-only line
        if i < len(items) and not isinstance(items[i], CommentNode):
            if isinstance(items[i], Tree):
                node.value = self.value(meta, items[i].children)
            elif isinstance(items[i], Token):
                node.value = self.value(meta, [items[i]])
            else:
                node.value = items[i]
            i += 1

        # 3) Handle comma immediately following the value
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "COMMA":
            node.has_comma = True
            i += 1

        # 4) Skip any whitespace tokens
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type in ("WHITESPACE", "HSPACES", "INLINE_WS")
        ):
            i += 1

        # 5) Handle inline-comment token directly (fix)
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "INLINE_COMMENT"
        ):
            node.inline_comment = items[i]
            i += 1
        # 6) Fallback: inline-comment subtree
        elif (
            i < len(items)
            and isinstance(items[i], Tree)
            and items[i].data == "inline_comment"
        ):
            for child in items[i].children:
                if isinstance(child, Token) and child.type == "INLINE_COMMENT":
                    node.inline_comment = child
                    break
            i += 1

        # 7) Set origin for round-trip fidelity
        if hasattr(node.value, "emit"):
            node.origin = node.value.emit()
        else:
            node.origin = str(node.value) if node.value is not None else ""
        node.meta = meta

        return node

    @v_args(meta=True)
    def inline_table(self, meta, items: List[Any]) -> InlineTableNode:
        """
        Parse an inline table `{ key1 = val1, key2 = val2 }`, storing
        full AssignmentNode ASTs so annotations and formatting can be round-tripped.
        """
        self.debug_print(f"inline_table() called with items '{items}'")
        node = InlineTableNode()
        node.data = {}

        # Look for the subtree holding all inline-table items
        for itm in items:
            if isinstance(itm, Tree) and itm.data == "inline_table_items":
                for child in itm.children:
                    if isinstance(child, ValueNode) and isinstance(
                        child.value, AssignmentNode
                    ):
                        assignment = child.value
                        # Store the entire AssignmentNode to preserve the ': TYPE = value'
                        node.data[assignment.identifier.value] = assignment
                        self.debug_print(
                            f"[DEBUG INLINE_TABLE]: Added AST node for '{assignment.identifier.value}'"
                        )
                break

        # Build a best‑guess origin string (emit() will use node.data directly)
        parts = [assignment.emit() for assignment in node.data.values()]
        node.origin = "{" + ", ".join(parts) + "}"
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
            node.__comments__.extend(
                item.value
                for item in items[i]
                if isinstance(item, CommentNode) and item is not None
            )
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
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "inline_comment"
        ):
            node.inline_comment = items[i]
            i += 1
        # Handle post-item comments
        if i < len(items) and isinstance(items[i], list):
            node.__comments__.extend(
                item.value
                for item in items[i]
                if isinstance(item, CommentNode) and item is not None
            )
        # Set origin safely
        node.origin = (
            node.value.emit() if node.value and hasattr(node.value, "emit") else ""
        )
        node.meta = meta
        return node

    @v_args(meta=True)
    def inline_assignment(self, meta, items: List[Any]) -> AssignmentNode:
        """
        Handle key[: type]? = value in inline tables, preserving whitespace,
        type annotations, and comments.
        """
        self.debug_print(f"inline_assignment() called with items '{items}'")
        node = AssignmentNode()
        i = 0

        # 1) Leading whitespace
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "HSPACES"
        ):
            node.leading_whitespace = items[i]
            i += 1

        # 2) Identifier
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "IDENTIFIER"
        ):
            node.identifier = items[i]
            i += 1

        # 3) Skip whitespace before optional annotation
        while i < len(items) and (
            isinstance(items[i], HspacesNode)
            or (isinstance(items[i], Token) and items[i].type == "HSPACES")
        ):
            i += 1

        # 4) Optional type annotation
        if i < len(items) and isinstance(items[i], Token) and items[i].value == ":":
            node.colon = items[i]
            i += 1
            if (
                i < len(items)
                and isinstance(items[i], Token)
                and items[i].type == "TYPE"
            ):
                node.type_annotation = items[i]
                i += 1
            # skip whitespace after annotation
            while i < len(items) and (
                isinstance(items[i], HspacesNode)
                or (isinstance(items[i], Token) and items[i].type == "HSPACES")
            ):
                i += 1

        # 5) Whitespace before equals, then '=' and whitespace after
        if i < len(items) and (
            isinstance(items[i], HspacesNode)
            or (isinstance(items[i], Token) and items[i].type == "HSPACES")
        ):
            node.equals_leading_whitespace = (
                items[i]
                if isinstance(items[i], HspacesNode)
                else HspacesNode(items[i].value)
            )
            i += 1
        if i < len(items) and isinstance(items[i], Token) and items[i].value == "=":
            node.equals = items[i]
            i += 1
        if i < len(items) and (
            isinstance(items[i], HspacesNode)
            or (isinstance(items[i], Token) and items[i].type == "HSPACES")
        ):
            node.equals_trailing_whitespace = (
                items[i]
                if isinstance(items[i], HspacesNode)
                else HspacesNode(items[i].value)
            )
            i += 1

        # 6) Value
        if i < len(items):
            val = items[i]
            if isinstance(
                val,
                (
                    SingleQuotedStringNode,
                    IntegerNode,
                    FloatNode,
                    BooleanNode,
                    NullNode,
                    InlineTableNode,
                    SingleLineArrayNode,
                    MultiLineArrayNode,
                ),
            ):
                node.value = val
            else:
                node.value = self.value(meta, [val])
            i += 1

        # 7) Inline comment
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "inline_comment"
        ):
            node.inline_comment = items[i]
            i += 1

        # 8) Trailing whitespace
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "HSPACES"
        ):
            node.trailing_whitespace = items[i]
            i += 1

        node.origin = node.identifier
        node.meta = meta
        self.debug_print(
            f"[DEBUG INLINE_ASSIGNMENT]: Created AssignmentNode(identifier={node.identifier.value}, "
            f"type_annotation={getattr(node.type_annotation, 'value', None)}, value={node.value})"
        )
        return node

    # ────────────────────────── list comprehension ──────────────────────────
    @v_args(meta=True)
    def list_comprehension(self, meta, items: List[Any]) -> ListComprehensionNode:
        """
        "[" comprehension_expr (WS|NEWLINE|HSPACES)* comprehension_clauses NEWLINE* "]"
        """
        self.debug_print("list_comprehension() called with items")
        node = ListComprehensionNode()
        i = 0

        # skip leading '['
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "L_SQ_BRACK"
        ):
            i += 1

        # ── header expr ────────────────────────────────────────────────────
        if i >= len(items):
            raise ValueError("Missing comprehension header expression")
        header = items[i]
        i += 1

        # wrap raw tokens into AST nodes
        if isinstance(header, Token):
            if header.type == "F_STRING":
                wrap = FStringNode()
                wrap.value = header.value
                wrap.origin = header.value
                wrap.meta = meta
                header = wrap
            elif header.type in {
                "SINGLE_QUOTED_STRING",
                "TRIPLE_QUOTED_STRING",
                "BACKTICK_STRING",
                "TRIPLE_BACKTICK_STRING",
            }:
                wrap = SingleQuotedStringNode()
                wrap.value = header.value.strip("\"'" + "`")
                wrap.origin = header.value
                wrap.meta = meta
                header = wrap

        node.header_expr = header

        # ── skip whitespace/newlines before clauses ───────────────────────
        while i < len(items) and (
            (isinstance(items[i], Token) and items[i].type in ("HSPACES", "NEWLINE"))
            or isinstance(items[i], HspacesNode)
            or isinstance(items[i], NewlineNode)
        ):
            i += 1

        # ── comprehension clauses ─────────────────────────────────────────
        if i < len(items) and isinstance(items[i], ComprehensionClausesNode):
            node.clauses = items[i]
            i += 1
        else:
            node.clauses = None

        # ── skip trailing newlines ────────────────────────────────────────
        while i < len(items) and (
            (isinstance(items[i], Token) and items[i].type == "NEWLINE")
            or isinstance(items[i], NewlineNode)
        ):
            i += 1

        # ── build full origin including clauses ───────────────────────────
        origin_parts = [node.header_expr.emit()]
        if node.clauses:
            origin_parts.append(node.clauses.emit())

        node.origin = "[" + " ".join(origin_parts) + "]"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def dict_comprehension(self, meta, items: List[Any]) -> DictComprehensionNode:
        """
        Transform the 'dict_comprehension' rule: "{" NEWLINE* dict_comprehension_pair
        "for" IDENTIFIER "in" value ("if" value)? NEWLINE* "}"
        Creates a DictComprehensionNode, handling keys and values by delegating to pair_expr.
        """
        self.debug_print("dict_comprehension() called with items")
        node = DictComprehensionNode()
        i = 0

        # Skip opening brace and any newlines
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type in ("LBRACE", "L_CURL_BRACE", "NEWLINE")
        ):
            i += 1

        # dict_comprehension_pair → PairExprNode via pair_expr()
        if (
            i < len(items)
            and isinstance(items[i], Tree)
            and items[i].data == "dict_comprehension_pair"
        ):
            pair_node = self.pair_expr(meta, items[i].children)
            node.pair = pair_node
            i += 1
        elif i < len(items) and isinstance(items[i], PairExprNode):
            node.pair = items[i]
            i += 1

        # Skip "for"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "FOR":
            i += 1

        # Loop variable
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "IDENTIFIER"
        ):
            node.loop_var = items[i]
            i += 1

        # Skip "in"
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IN":
            i += 1

        # Iterable expression
        if i < len(items):
            node.iterable = items[i]
            i += 1

        # Optional "if" clause
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IF":
            i += 1
            if i < len(items):
                node.condition = items[i]
                i += 1
        else:
            node.condition = None

        # Skip any trailing newlines and the closing brace
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type in ("NEWLINE", "RBRACE", "R_CURL_BRACE")
        ):
            i += 1

        # Construct origin string
        origin_parts: List[str] = [
            node.pair.emit(),
            f"for {node.loop_var.value} in {node.iterable.emit()}",
        ]
        if node.condition:
            origin_parts.append(f"if {node.condition.emit()}")

        node.origin = "{" + " ".join(origin_parts) + "}"
        node.value = node.origin
        node.meta = meta
        return node

    # ───────────────────── inline‑table comprehension ──────────────────────
    @v_args(meta=True)
    def inline_table_comprehension(
        self, meta, items: List[Any]
    ) -> InlineTableComprehensionNode:
        """
        “{” key = value for x in iterable [if cond] “}”
        """
        self.debug_print("inline_table_comprehension() called with items")
        node = InlineTableComprehensionNode()
        i = 0

        # ── skip opening “{” and newlines ──────────────────────────────────
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type in ("LBRACE", "L_CURL_BRACE", "NEWLINE")
        ):
            i += 1

        # ── inline_comprehension_pair  →  PairExprNode ─────────────────────
        if i >= len(items):
            raise ValueError("Missing inline_comprehension_pair")

        if isinstance(items[i], Tree) and items[i].data == "inline_comprehension_pair":
            pair_items = items[i].children
            pair_index = 0
            pair_node = PairExprNode()

            # ---- helper to wrap raw tokens into nodes that own .emit() ----
            def _tok_to_node(tok: Token):
                if tok.type == "F_STRING":
                    wrap = FStringNode()
                    wrap.value = tok.value
                    wrap.origin = tok.value
                    wrap.meta = meta
                    return wrap
                if tok.type in {
                    "SINGLE_QUOTED_STRING",
                    "TRIPLE_QUOTED_STRING",
                    "BACKTICK_STRING",
                    "TRIPLE_BACKTICK_STRING",
                }:
                    wrap = SingleQuotedStringNode()
                    wrap.value = tok.value.strip("\"'`")
                    wrap.origin = tok.value
                    wrap.meta = meta
                    return wrap
                if tok.type == "IDENTIFIER":
                    wrap = DottedExprNode()
                    wrap.dotted_value = tok.value
                    wrap.origin = tok.value
                    wrap.value = tok.value
                    wrap.meta = meta
                    return wrap
                return tok  # fallback (shouldn’t happen)

            # ---- key ------------------------------------------------------
            key_tok_or_node = pair_items[pair_index]
            pair_index += 1
            if isinstance(key_tok_or_node, Token):
                pair_node.key = _tok_to_node(key_tok_or_node)
            else:
                pair_node.key = key_tok_or_node

            # ---- (=) separator & spaces -----------------------------------
            separator = "="
            while (
                pair_index < len(pair_items)
                and isinstance(pair_items[pair_index], Token)
                and pair_items[pair_index].type in ("HSPACES", "SETTER")
            ):
                if pair_items[pair_index].type == "SETTER":
                    separator = pair_items[pair_index].value
                pair_index += 1

            # ---- value ----------------------------------------------------
            val_tok_or_node = pair_items[pair_index]
            if isinstance(val_tok_or_node, Token):
                pair_node.value = _tok_to_node(val_tok_or_node)
            else:
                pair_node.value = val_tok_or_node

            pair_node.origin = (
                (
                    pair_node.key.emit()
                    if hasattr(pair_node.key, "emit")
                    else pair_node.key.value
                )
                + f" {separator} "
                + (
                    pair_node.value.emit()
                    if hasattr(pair_node.value, "emit")
                    else pair_node.value.value
                )
            )
            pair_node.value = pair_node.origin  # raw representation
            pair_node.meta = meta
            node.pair = pair_node
            i += 1
        elif isinstance(items[i], PairExprNode):
            node.pair = items[i]
            i += 1
        else:
            raise ValueError(
                f"Expected PairExprNode or inline_comprehension_pair Tree at index {i}, got {items[i]!r}"
            )

        # ── “for” IDENTIFIER “in” iterable [if cond] ───────────────────────
        if not (
            i < len(items) and isinstance(items[i], Token) and items[i].type == "FOR"
        ):
            raise ValueError("Expected 'for' in inline‑table comprehension")
        i += 1

        if not (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "IDENTIFIER"
        ):
            raise ValueError("Expected loop variable after 'for'")
        node.loop_var = items[i]
        i += 1

        if not (
            i < len(items) and isinstance(items[i], Token) and items[i].type == "IN"
        ):
            raise ValueError("Expected 'in' after loop variable")
        i += 1

        if i >= len(items):
            raise ValueError("Missing iterable after 'in'")
        node.iterable = items[i]
        i += 1

        if i < len(items) and isinstance(items[i], Token) and items[i].type == "IF":
            i += 1
            if i >= len(items):
                raise ValueError("Missing condition after 'if'")
            node.condition = items[i]
            i += 1
        else:
            node.condition = None

        # ── consume trailing newlines & closing “}” ────────────────────────
        while (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type in ("NEWLINE", "RBRACE", "R_CURL_BRACE")
        ):
            i += 1

        # ── origin string --------------------------------------------------
        origin_parts = [
            node.pair.emit() if hasattr(node.pair, "emit") else node.pair.origin,
            f"for {node.loop_var.value} in {node.iterable.emit()}",
        ]
        if node.condition:
            origin_parts.append(f"if {node.condition.emit()}")
        node.origin = "{" + " ".join(origin_parts) + "}"
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def comprehension_clauses(self, meta, items: List[Any]) -> ComprehensionClausesNode:
        self.debug_print("comprehension_clauses() called with items")
        node = ComprehensionClausesNode()
        node.clauses = items
        # Preserve each clause on its own line
        parts = [c.emit() for c in items]
        node.origin = "\n".join(parts)
        node.value = node.origin
        node.meta = meta
        return node

    @v_args(meta=True)
    def comprehension_clause(self, meta, items: List[Any]) -> ComprehensionClauseNode:
        self.debug_print("comprehension_clause() called with items")
        node = ComprehensionClauseNode()

        # Drop raw syntax tokens
        ast_items = [itm for itm in items if not isinstance(itm, Token)]
        raw_vars = ast_items[0]
        node.loop_vars = raw_vars if isinstance(raw_vars, list) else [raw_vars]
        node.iterable = ast_items[1]
        node.conditions = ast_items[2:]

        vars_txt = " ".join(
            getattr(v, "origin", v.emit() if hasattr(v, "emit") else str(v)).strip()
            for v in node.loop_vars
        )
        iterable_txt = (
            node.iterable.emit()
            if hasattr(node.iterable, "emit")
            else str(node.iterable)
        ).strip()
        cond_txt = " ".join(
            getattr(c, "origin", c.emit() if hasattr(c, "emit") else str(c)).strip()
            for c in node.conditions
        )

        origin = f"for {vars_txt} in {iterable_txt}"
        if cond_txt:
            origin += f" if {cond_txt}"

        node.origin = origin
        node.value = origin
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
            node.origin = f"{items[0].emit()} {items[1].emit()}"
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
        node.parts = [
            item
            for item in items
            if not isinstance(item, Token) or item.type != "OPERATOR"
        ]
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
        Handle `<( … )>` folded expressions:
        - Unwrap a single-child 'folded_content' Tree so our evaluator sees
          the actual expression AST (e.g. arithmetic, concatenation, etc.).
        - Preserve raw origin for round-trip fidelity.
        """
        from ._ast_nodes import FoldedExpressionNode
        from lark import Token, Tree

        node = FoldedExpressionNode()

        # items structure: [Token('<('), Tree('folded_content', [...]), Token(')>')]
        folded_wrapper = items[1]

        # If folded_wrapper is exactly one real AST subtree, unwrap it:
        if (
            isinstance(folded_wrapper, Tree)
            and folded_wrapper.data == "folded_content"
            and len(folded_wrapper.children) == 1
            and isinstance(folded_wrapper.children[0], Tree)
        ):
            node.content_tree = folded_wrapper.children[0]
        else:
            node.content_tree = folded_wrapper

        # Rebuild origin exactly as parsed (so dumps()/emit() remains unchanged)
        content_parts: List[str] = []
        for child in getattr(folded_wrapper, "children", []):
            if isinstance(child, Token):
                content_parts.append(child.value)
            else:
                content_parts.append(child.emit())
        content_str = "".join(content_parts)

        start = items[0].value  # '<('
        end = items[-1].value  # ')>'
        node.origin = f"{start} {content_str} {end}"
        node.value = node.origin
        node.meta = meta

        return node

    @v_args(meta=True)
    def folded_content(self, meta, items: List[Any]) -> Tree:
        self.debug_print("folded_content() called with items")
        return Tree("folded_content", items)

    @v_args(meta=True)
    def single_line_array(self, meta, items: List[Any]) -> SingleLineArrayNode:
        """
        Represents a single‑line array, e.g. [1, 2, "three"].
        Accumulates ValueNode children and resolves them into a Python list.
        """
        self.debug_print(f"single_line_array() called with items '{items}'")
        node = SingleLineArrayNode()
        contents: List[ValueNode] = []
        i = 0

        # match '['
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "L_SQ_BRACK"
        ):
            node.lbrack = items[i]
            i += 1

        # collect the array_content subtree
        if (
            i < len(items)
            and isinstance(items[i], Tree)
            and items[i].data == "sl_array_content"
        ):
            for child in items[i].children:
                # skip delimiters and whitespace
                if isinstance(child, Token) and child.type == "COMMA":
                    continue

                if isinstance(
                    child,
                    (NewlineNode, WhitespaceNode, HspacesNode, InlineWhitespaceNode),
                ):
                    continue

                # explicit array_item
                if isinstance(child, Tree) and child.data == "sl_array_item":
                    val_node = self.sl_array_item(meta, child.children)
                    if val_node.value is not None:
                        contents.append(val_node)
                    continue

                # raw AST nodes (IntegerNode, FloatNode, String nodes, etc.)
                if isinstance(child, BaseNode):
                    wrapped = ValueNode()
                    wrapped.value = child
                    wrapped.meta = meta
                    if wrapped.value is not None:
                        contents.append(wrapped)
                    continue

                # direct tokens (e.g., strings) — convert via value()
                if isinstance(child, Token):
                    node_val = self.value(meta, [child])
                    wrapped = ValueNode()
                    wrapped.value = node_val
                    wrapped.meta = meta
                    if wrapped.value is not None:
                        contents.append(wrapped)
                    continue

            i += 1

        # match ']'
        if (
            i < len(items)
            and isinstance(items[i], Token)
            and items[i].type == "R_SQ_BRACK"
        ):
            node.rbrack = items[i]

        node.contents = contents
        return node

    # ───────────────────── multiline array ──────────────────────
    @v_args(meta=True, inline=False)
    def multiline_array(self, meta, items: List[Any]) -> MultiLineArrayNode:
        """
        Parse a multiline array into a MultiLineArrayNode, preserving values and comments.
        Handles both raw COMMENT tokens and CommentNode instances, and ensures that
        any trailing commas on comment‑only lines are captured, and inline comments
        on value lines are correctly attached.
        """
        self.debug_print("multiline_array() called with items")
        from ._ast_nodes import (
            MultiLineArrayNode,
            ValueNode,
            CommentNode,
            NewlineNode,
            WhitespaceNode,
            HspacesNode,
            InlineWhitespaceNode,
        )
        from lark import Token, Tree

        # Remove any explicit NewlineNode instances (we'll skip raw NEWLINE tokens below)
        items = [itm for itm in items if not isinstance(itm, NewlineNode)]

        node = MultiLineArrayNode()

        for itm in items:
            # Skip purely structural whitespace/newline tokens
            if (
                isinstance(itm, Token)
                and itm.type in ("NEWLINE", "HSPACES", "INLINE_WS")
                or isinstance(
                    itm,
                    (NewlineNode, WhitespaceNode, HspacesNode, InlineWhitespaceNode),
                )
            ):
                continue

            # 1) Raw COMMENT token (e.g. "# something,"), strip and detect comma
            if isinstance(itm, Token) and itm.type == "COMMENT":
                raw = itm.value.rstrip()
                has_comma = raw.endswith(",")
                text = raw[:-1] if has_comma else raw
                vn = ValueNode()
                vn.value = None
                vn.inline_comment = Token("INLINE_COMMENT", "  " + text)
                vn.has_comma = has_comma
                vn.meta = meta
                node.contents.append(vn)
                continue

            # 2) CommentNode (from comment_line transformer)
            if isinstance(itm, CommentNode):
                raw = itm.origin.rstrip()
                has_comma = raw.endswith(",")
                text = raw[:-1] if has_comma else raw
                vn = ValueNode()
                vn.value = None
                vn.inline_comment = Token("INLINE_COMMENT", "  " + text)
                vn.has_comma = has_comma
                vn.meta = meta
                node.contents.append(vn)
                continue

            # 3) Explicit ml_array_item subtree (value lines, possibly with inline comments)
            if isinstance(itm, Tree) and itm.data == "ml_array_item":
                node.contents.append(self.ml_array_item(meta, itm.children))
                continue

            # 4) Pre‑wrapped ValueNode (unlikely here, but safe)
            if isinstance(itm, ValueNode):
                node.contents.append(itm)
                continue

            # 5) Catch standalone COMMA tokens—mark the previous entry
            if isinstance(itm, Token) and itm.type == "COMMA":
                if node.contents:
                    node.contents[-1].has_comma = True
                continue

            # 6) Fallback for any other AST node (treat as a bare value)
            if hasattr(itm, "emit"):
                vn = ValueNode()
                vn.value = itm
                vn.meta = meta
                node.contents.append(vn)
                continue

            # 7) Inline-comment subtree (rare): attach to last entry
            if isinstance(itm, Tree) and itm.data == "inline_comment":
                for child in itm.children:
                    if isinstance(child, Token) and child.type == "INLINE_COMMENT":
                        if node.contents:
                            node.contents[-1].inline_comment = child
                        break
                continue

            # Anything else is ignored

        # Merge comment-only items into preceding values when appropriate
        merged = []
        i = 0
        while i < len(node.contents):
            curr = node.contents[i]
            if curr.value is None and i > 0:
                prev = merged[-1]
                # Attach only if previous is a true value and has no inline comment yet
                if prev.value is not None and prev.inline_comment is None:
                    prev.inline_comment = curr.inline_comment
                    prev.has_comma = prev.has_comma or curr.has_comma
                    i += 1
                    continue
            merged.append(curr)
            i += 1
        node.contents = merged

        # Finally, ensure that every true value item (not comment‑only) ends with a comma
        value_idxs = [idx for idx, v in enumerate(node.contents) if v.value is not None]
        for idx in value_idxs[:-1]:
            node.contents[idx].has_comma = True

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
        self.debug_print("FLOAT() called with token")
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
        self.debug_print("SINGLE_QUOTED_STRING() called with token")
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
        self.debug_print("TRIPLE_QUOTED_STRING() called with token")
        if raw_text.startswith('"""') and raw_text.endswith('"""'):
            inner_text = raw_text[3:-3]
        else:
            inner_text = raw_text

        node = TripleQuotedStringNode()
        node.value = inner_text  # store just the contents
        node.origin = token.value  # keep the full original for debugging if desired
        return node

    def BACKTICK_STRING(self, token):
        self.debug_print("INTEGER() called with token")
        node = BacktickStringNode()
        node.value = token.value
        node.origin = token.value
        return node

    def F_STRING(self, token):
        self.debug_print("F_STRING() called with token")
        node = FStringNode()
        node.value = token.value
        node.origin = token.value
        return node

    def TRIPLE_BACKTICK_STRING(self, token):
        raw_text = token.value  # e.g. '"""\nsomething\n"""'
        # In TOML-like syntaxes, triple quotes are always at both ends (assuming valid parse).
        # Just strip the first 3 and last 3 chars. If your grammar supports both `"""` and `'''`,
        # you'd detect which is used. For now, assume `"""`.
        self.debug_print("TRIPLE_BACKTICK_STRING() called with token")
        if raw_text.startswith("```") and raw_text.endswith("```"):
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
        # self.debug_print("HSPACES() called with token")
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
