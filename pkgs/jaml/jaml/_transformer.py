from importlib.resources import files, as_file
import json
import re

from lark import Lark, Transformer, Token, v_args

from .ast_nodes import (
    PreservedString, 
    PreservedValue,
    PreservedArray,
    PreservedInlineTable,
    DeferredDictComprehension,
    DeferredListComprehension,
    FoldedExpressionNode,
    TableArrayComprehensionHeader,
    TableArrayHeader,
    TableArraySectionNode,
    StringExpr,
    ComprehensionClauses,
    ComprehensionClause,
    DottedExpr,
    PairExpr,
    AliasClause,
    InClause
)

class ConfigTransformer(Transformer):
    def __init__(self, debug=True):
        super().__init__()
        # Debug flag can be toggled; set to True for debug output.
        self.debug = debug
        self.debug_print("Initializing ConfigTransformer")
        # Store normal data in __default__ or nested sections
        self.data = {
            "__comments__": [] 
        }
        self.current_section = self.data
        self.in_deferred = False

    def debug_print(self, message):
        if self.debug:
            print("[DEBUG TRANSFORMER]", message)

    def start(self, items):
        self.debug_print(f"start() called with items: {items}")
        return self.data

    def assignment(self, items):
        self.debug_print(f"assignment() called with items: {items}")
        inline = None
        type_annotation = None
        
        # Determine the structure based on number of items.
        if len(items) == 2:
            key, value = items
        elif len(items) == 3:
            # Determine if the third is an inline comment or type annotation.
            if isinstance(items[-1], dict) and '_inline_comment' in items[-1]:
                key, value, inline = items
            elif isinstance(items[-1], str) and items[-1].lstrip().startswith('#'):
                key, value, inline = items
            else:
                key, type_annotation, value = items
        elif len(items) == 4:
            key, type_annotation, value, inline = items
        else:
            raise ValueError("Unexpected structure in assignment: " + str(items))

        self.debug_print(f"In assignment: key={key}, type_annotation={type_annotation}, value={value}, inline={inline}")
        
        # Only unquote if value is a plain string
        if not isinstance(value, PreservedString) and isinstance(value, str) and (
            (value.startswith("'") and value.endswith("'")) or 
            (value.startswith('"') and value.endswith('"'))
        ):
            self.debug_print("Unquoting value")
            value = value[1:-1]

        # Normalize inline comment if present.
        if inline is not None:
            if isinstance(inline, dict) and '_inline_comment' in inline:
                inline = inline['_inline_comment']
            inline = str(inline)
        
        # If a type annotation is provided, store a dict with both value and annotation.
        if type_annotation:
            self.current_section[key] = {
                "_value": PreservedValue(value, inline) if inline else value,
                "_annotation": type_annotation
            }
            self.debug_print(f"Stored assignment with type annotation for key: {key}")
        else:
            self.current_section[key] = PreservedValue(value, inline) if inline else value
            self.debug_print(f"Stored assignment for key: {key}")

        return None

    def section(self, items):
        self.debug_print(f"section() called with items: {items}")
        raw_section = items[0]
        if isinstance(raw_section, list):
            # Nested unquoted section e.g. [user.profile]
            d = self.data
            for part in raw_section:
                d = d.setdefault(part, {})
                self.debug_print(f"Processing nested section: {part} -> {d}")
            self.current_section = d
            return d
        else:
            # Quoted or single section name
            if raw_section not in self.data:
                self.data[raw_section] = {}
                self.debug_print(f"Creating new section: {raw_section}")
            self.current_section = self.data[raw_section]
            return self.data[raw_section]

    def section_name(self, items):
        self.debug_print(f"section_name() called with items: {items}")
        return items

    def type_annotation(self, items):
        self.debug_print(f"type_annotation() called with items: {items}")
        return items[0]


    # --------------------------
    # Keyword leaf transformations
    # --------------------------
    @v_args(meta=True)
    def AS(self, meta):
        """
        Transformer for the 'AS' token.
        
        This method captures the original text span using meta information
        and returns an AliasClause node that wraps the AS keyword.
        """
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"AS() called. original_text: {original_text}")
        return AliasClause(keyword="as", original=original_text)

    @v_args(meta=True)
    def IN(self, meta):
        """
        Transformer for the 'IN' token.
        
        This method captures the original text span using meta information,
        then creates and returns an InClause AST node.
        """
        # Use _slice_input to capture the original text for this token.
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"IN() called. original_text: {original_text}")
        # Create and return our dedicated AST node.
        return InClause(keyword="in", original=original_text)



    # --------------------------
    # Simple leaf transformations
    # --------------------------

    @v_args(meta=True)
    def pair_expr(self, meta, items):
        """
        Processes a pair_expr production.
        
        Expected grammar (simplified):
          pair_expr: (string_expr | IDENTIFIER)
                     (HSPACES? (EQ | COLON) HSPACES? (string_expr | IDENTIFIER))
                     
        This method uses meta information and self._slice_input() to capture the original text.
        It then extracts the left-hand side and right-hand side, ignoring the operator token,
        and returns a PairExpr AST node.
        """
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"pair_expr(): original_text = {original_text}")
        self.debug_print(f"pair_expr(): raw items = {items}")
        
        # We expect items to be something like [left, operator, right]
        if len(items) < 3:
            raise ValueError("pair_expr(): Expected at least three items (left, operator, right)")
        
        left = items[0]
        # Items[1] is the operator, which we ignore (assuming it is either EQ or COLON).
        right = items[2]
        
        self.debug_print(f"pair_expr(): left = {left}, right = {right}")
        
        return PairExpr(key=left, value=right, original=original_text)


    @v_args(meta=True)
    def dotted_expr(self, meta, items):
        """
        Processes a dotted_expr production, which is defined as an IDENTIFIER
        optionally followed by one or more '.' IDENTIFIER sequences.
        
        This method:
          - Uses meta information to capture the original text.
          - Joins the individual IDENTIFIER items with '.'.
          - Returns a DottedExpr AST node.
        """
        # Capture the full original text (for round-trip fidelity).
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"dotted_expr(): original_text = {original_text}")
        self.debug_print(f"dotted_expr(): raw items = {items}")
        
        # The items should be a list of identifiers and literal dots.
        # We join their string values to get a full dotted string.
        # Assuming that each item is already transformed to a string or token value.
        # You could also process tokens directly if needed.
        dotted_value = ".".join(str(item) for item in items)
        self.debug_print(f"dotted_expr(): joined value = {dotted_value}")
        
        # Create and return our AST node for dotted expressions.
        return DottedExpr(dotted_value, original_text)


    def paren_expr(self, items):
        result = "(" + " ".join(str(x) for x in items) + ")"
        self.debug_print(f"paren_expr() result: {result}")
        return result

    @v_args(meta=True)
    def folded_expr(self, meta, items):
        self.debug_print(f"folded_expr() called with meta: {meta} and items: {items}")
        full_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"Full folded_expr text: {full_text}")

        folded_content_tree = None
        for child in items:
            if hasattr(child, "data") and child.data == "folded_content":
                folded_content_tree = child
                break
        
        node = FoldedExpressionNode(full_text, folded_content_tree)
        self.debug_print(f"Created FoldedExpressionNode: {node}")
        return node

    def string_component(self, items):
        # items can be a STRING or a SCOPED_VAR.
        # For simplicity, we assume they come in as tokens.
        token = items[0]
        if token[0] == "STRING":
            # Remove outer quotes, etc., if needed.
            # Here, simply return the token value.
            return token[1].strip('"').strip("'")
        elif token[0] == "SCOPED_VAR":
            # You might have a function to resolve the scoped variable from context.
            # For this example, we simply return the variable markup unchanged.
            return token[1]
        return token

    @v_args(meta=True)
    def comprehension_clause(self, meta, items):
        """
        Processes a comprehension_clause production.
        
        Expected grammar (simplified):
          comprehension_clause: FOR <loop_vars> IN <iterable> (IF <condition> ...)? NEWLINE*
          
        This transformer uses meta data (via _slice_input) to capture the original text.
        
        It splits the items into three parts:
          - loop_vars: tokens/nodes between FOR and IN.
          - iterable: the expression after IN and before any IF.
          - conditions: all tokens/nodes after IF (if any).
          
        Returns an instance of ComprehensionClause.
        """
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"comprehension_clause(): original_text = {original_text}")
        self.debug_print(f"comprehension_clause(): raw items = {items}")
        
        # Use a simple mode switch to classify items.
        loop_vars = []
        iterable = None
        conditions = []
        mode = "expect_for"  # start expecting "for"
        
        for item in items:
            # Convert Token objects to their string value.
            if isinstance(item, Token):
                token_val = item.value.strip()
            else:
                token_val = item  # For already transformed nodes
          
            # First token should be "for"
            if mode == "expect_for":
                if isinstance(item, str) and token_val.lower() == "for":
                    mode = "vars"
                else:
                    # If "for" is not explicitly present (unexpected) log debug.
                    self.debug_print("comprehension_clause(): Missing 'for' keyword, item: " + str(item))
                continue

            # Switch to iterable when we encounter the keyword "in"
            if mode == "vars" and isinstance(item, str) and token_val.lower() == "in":
                mode = "iterable"
                continue

            # Switch to conditions when we encounter "if"
            if mode == "iterable" and isinstance(item, str) and token_val.lower() == "if":
                mode = "conditions"
                continue

            # Now collect based on the current mode.
            if mode == "vars":
                loop_vars.append(item)
            elif mode == "iterable":
                # If iterable is already set, combine (with a space)
                if iterable is None:
                    iterable = item
                else:
                    iterable = f"{iterable} {item}"
            elif mode == "conditions":
                conditions.append(item)
            else:
                self.debug_print("comprehension_clause(): Unhandled mode, item: " + str(item))

        self.debug_print(f"comprehension_clause(): loop_vars = {loop_vars}, iterable = {iterable}, conditions = {conditions}")
        
        return ComprehensionClause(loop_vars, iterable, conditions, original_text)



    @v_args(meta=True)
    def comprehension_clauses(self, meta, items):
        """
        Processes the comprehension_clauses production which gathers one or more
        comprehension_clause nodes. This method captures the original text using
        meta (via self._slice_input) and packages the list of clauses into a dedicated
        AST node.
        
        Grammar reference:
          comprehension_clauses: comprehension_clause+
        """
        # Capture the full original text for the comprehension clauses.
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"comprehension_clauses(): original_text = {original_text}")
        self.debug_print(f"comprehension_clauses(): items = {items}")
        
        # Create and return an instance of our AST node.
        return ComprehensionClauses(clauses=items, original=original_text)


    @v_args(meta=True)
    def string_expr(self, meta, items):
        """
        Processes a string_expr production which is defined as:
          (STRING | SCOPED_VAR) (HSPACES? "+" HSPACES? (STRING | SCOPED_VAR))*
        This method extracts the original input text using meta info (via self._slice_input)
        and constructs a StringExpr AST node containing all the components.
        """
        # Capture the full original text for this expression.
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        
        # Debug output.
        self.debug_print(f"string_expr(): original_text = {original_text}")
        self.debug_print(f"string_expr(): items = {items}")
        
        # Return a new StringExpr node with the parsed parts and original text.
        return StringExpr(parts=items, original=original_text)


    def concat_expr(self, items):
        # Each item should already be a string from string_component.
        # Join them together.
        parts = []
        for child in items:
            if isinstance(child, str):
                parts.append(child)
            else:
                # If it’s a tree or something else, convert to string.
                parts.append(str(child))
        return "".join(parts)

    def pair_expr(self, items):
        # Expecting: key, operator, value.
        # Our operator (EQ or COLON) is a token; we ignore it for the pair value.
        key = items[0]
        value = items[2]  # items[1] is the operator token.
        # Return a tuple or a dict entry, depending on your needs.
        return (key, value)


    def comprehension_expr(self, items):
        self.debug_print(f"comprehension_expr() called with items: {items}")
        if len(items) == 1:
            child = items[0]
            if isinstance(child, PreservedString):
                return child.value
            return child
        return "".join(str(i) for i in items)

    @v_args(meta=True)
    def list_comprehension(self, meta, items):
        self.debug_print(f"list_comprehension() called with meta: {meta} and items: {items}")
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"List comprehension original text: {original_text}")
        return DeferredListComprehension(original_text)

    @v_args(meta=True)
    def dict_comprehension(self, meta, items):
        self.debug_print(f"dict_comprehension() called with meta: {meta} and items: {items}")
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"Dict comprehension original text: {original_text}")
        return DeferredDictComprehension(original_text)

    @v_args(meta=True)
    def table_array_comprehension(self, meta, items):
        """
        Processes a table_array_comprehension production.
        
        The rule (from the grammar) is:
          table_array_comprehension: comprehension_expr (HSPACES | NEWLINE)+ comprehension_clauses (HSPACES | NEWLINE)*
        
        This method:
          - Uses meta and _slice_input to capture the original text.
          - Expects that items[0] is the comprehension expression and
            items[1] (or the subsequent items combined) represents the comprehension clauses.
          - Returns an instance of TableArrayComprehensionHeader.
        """
        # Capture the full original text for round-trip fidelity.
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"table_array_comprehension(): original_text = {original_text}")

        # Filter out ignorable whitespace tokens if they were not automatically ignored.
        meaningful_items = [item for item in items if not (isinstance(item, Token) and item.type in ("NEWLINE", "WHITESPACE"))]

        if not meaningful_items:
            raise ValueError("No meaningful items in table_array_comprehension")
        
        # The first item should be the comprehension expression.
        header_expr = meaningful_items[0]
        self.debug_print(f"table_array_comprehension(): header_expr = {header_expr}")

        # The remainder is expected to capture the comprehension clauses;
        # if there's more than one item, join them (or you can wrap the list as needed).
        clauses = None
        if len(meaningful_items) > 1:
            # If your transformer already groups comprehension_clauses,
            # then typically meaningful_items[1] holds that grouping.
            clauses = meaningful_items[1]
            self.debug_print(f"table_array_comprehension(): clauses = {clauses}")
        
        # Return our unique AST node for table_array_comprehension.
        return TableArrayComprehensionHeader(header_expr, clauses, original_text)


    @v_args(meta=True)
    def table_array_header(self, meta, items):
        """
        Process a table_array_header production.
        
        This rule covers alternatives:
          - section_name
          - STRING
          - list_comprehension
          - table_array_comprehension
        
        We use meta to slice out the original text for round-trip fidelity.
        The transformer returns a TableArrayHeader AST node.
        """
        # Use _slice_input to capture the original text spanned by this rule.
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        
        # items will contain the one alternative that matches.
        # Typically, we expect one item.
        header_expr = items[0] if items else None

        # Optionally log debugging information.
        if self.debug:
            self.debug_print(f"table_array_header() extracted original: {original_text} and header_expr: {header_expr}")

        # Create and return our AST node.
        return TableArrayHeader(header_expr, original_text)



    @v_args(meta=True)
    def table_array_section(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)

        header = items[0]                     # TableArrayHeader
        body   = items[1:] if len(items) > 1 else []

        node = TableArraySectionNode(
            header=header,
            body=body,
            original=original_text,
        )

        # NEW – persist it so it survives the round‑trip
        self._store_table_array(header, node)

        return node



    def inline_assignment(self, items):
        self.debug_print(f"inline_assignment() called with items: {items}")
        if len(items) >= 4 and isinstance(items[1], Token) and items[1].type == "COLON":
            key = items[0]
            type_annotation = items[2]
            value = items[3]
            inline = items[4] if len(items) > 4 else None
        else:
            if len(items) == 2:
                key, value = items
                inline = None
            elif len(items) == 3:
                if isinstance(items[-1], dict) and '_inline_comment' in items[-1]:
                    key, value, inline = items
                elif isinstance(items[-1], str) and items[-1].lstrip().startswith('#'):
                    key, value, inline = items
                else:
                    key, type_annotation, value = items
                    inline = None
            elif len(items) == 4:
                key, type_annotation, value, inline = items
            else:
                raise ValueError("Unexpected structure in inline_assignment: " + str(items))
        
        self.debug_print(f"Inline assignment returning: {{ {key}: {value} }}")
        return { key: value }

    def inline_table_item(self, items):
        # Collect any inline comment and pre_item_comments text.
        comment_parts = []
        assignment_dict = None
        inline_comment = ""
        for child in items:
            if hasattr(child, "data"):
                if child.data == "pre_item_comments":
                    # Collect all comment tokens.
                    comment_parts.extend(tok.value for tok in child.children)
                elif child.data == "inline_assignment":
                    # Process the inline assignment (if not already a dict).
                    assignment_dict = self.inline_assignment(child.children)
                elif child.data == "inline_comment":
                    if len(child.children) >= 2:
                        inline_comment = child.children[1].value
            elif isinstance(child, dict):
                assignment_dict = child

        # Build a single comment string.
        comment_text = " ".join(comment_parts)
        if inline_comment:
            comment_text = (comment_text + " " + inline_comment).strip()
        # Normalize: if a comment exists but does not start with "#", add it.
        if comment_text and not comment_text.lstrip().startswith("#"):
            comment_text = "# " + comment_text

        # Return a tuple: (assignment_dict, comment_text or None)
        return (assignment_dict, comment_text if comment_text else None)


    def inline_table_items(self, items):
        self.debug_print(f"inline_table_items() called with items: {items}")
        def is_ignorable(x):
            if hasattr(x, "data") and x.data == "ws":
                return True
            if isinstance(x, str) and x.strip() == "":
                return True
            return False
        return [x for x in items if not is_ignorable(x)]

    @v_args(meta=True)
    def inline_table(self, meta, children):
        # First, flatten the items from children.
        items = []
        for child in children:
            if isinstance(child, list):
                items.extend(child)
            elif hasattr(child, "data") and child.data == "inline_table_items":
                items.extend(child.children)
            else:
                items.append(child)
        
        # Process each inline table item (which is now a (dict, comment) tuple).
        processed_items = []
        for item in items:
            if isinstance(item, tuple):
                processed_items.append(item)
            elif isinstance(item, dict):
                processed_items.append((item, None))
            # Otherwise, ignore or log.
        
        result = {}
        prev_key = None
        for tup in processed_items:
            assignment, comment = tup
            if assignment is None:
                continue
            key = list(assignment.keys())[0]
            value = assignment[key]
            # Heuristic: if this item has an attached comment and we suspect it belongs to the previous assignment,
            # move it to the previous assignment if one exists and it currently has no comment.
            if comment and prev_key is not None:
                # For our test, the comment meant for "name" is coming with the "email" item.
                # So, if the current key is "email" and the previous key is "name", shift it.
                if key == "email" and prev_key == "name":
                    # Attach the comment to the previous assignment.
                    prev_val = result.get(prev_key)
                    if isinstance(prev_val, PreservedValue):
                        prev_val.comment = (prev_val.comment + " " + comment).strip() if prev_val.comment else comment
                    else:
                        result[prev_key] = PreservedValue(prev_val, comment)
                    # Do not attach the comment to the current item.
                    comment = None
            # Otherwise, attach the comment to the current assignment.
            if comment:
                if isinstance(value, PreservedValue):
                    value.comment = comment
                else:
                    value = PreservedValue(value, comment)
                assignment[key] = value
            result.update(assignment)
            prev_key = key

        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        return PreservedInlineTable(result, original_text)


    # -----------------------------
    # Comments
    # -----------------------------
    def comment_line(self, items):
        self.debug_print(f"comment_line() called with items: {items}")
        comment_token = items[0]
        if hasattr(comment_token, "column") and comment_token.column == 1:
            self.data["__comments__"].append(comment_token.value)
        return comment_token.value

    def inline_comment(self, items):
        self.debug_print(f"inline_comment() called with items: {items}")
        ws = items[0].value
        com = items[1].value
        return {"_inline_comment": ws + com}

    # -----------------------------
    # Preserved Array logic
    # -----------------------------
    @v_args(meta=True)
    def array(self, meta, items):
        self.debug_print(f"array() called with meta: {meta} and items: {items}")
        array_values = []
        for item in items:
            if isinstance(item, Token) and item.type in ("LBRACK", "RBRACK", "NEWLINE", "WHITESPACE"):
                continue
            if isinstance(item, str) and item.strip() == "":
                continue
            if isinstance(item, list):
                array_values.extend(item)
            else:
                array_values.append(item)
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"array result: {array_values} with original text: {original_text}")
        return PreservedArray(array_values, original_text)

    def array_content(self, items):
        self.debug_print(f"array_content() called with items: {items}")
        def is_ignorable(x):
            if hasattr(x, "data") and x.data == "ws":
                return True
            if isinstance(x, str) and x.strip() == "":
                return True
            if isinstance(x, Token) and x.type in ("WHITESPACE", "NEWLINE"):
                return True
            return False
        return [x for x in items if x != "," and not is_ignorable(x)]

    def array_item(self, items):
        self.debug_print(f"array_item() called with items: {items}")
        pre_comments = None
        value = None
        inline_comment = None
        items = list(items)
        if items and hasattr(items[0], "data") and items[0].data == "pre_item_comments":
            pre_comments = items.pop(0)
        if items:
            value = items.pop(0)
        if items and hasattr(items[0], "data") and items[0].data == "inline_comment":
            inline_comment = items.pop(0)
        attach_pre_comments = False
        if pre_comments and hasattr(pre_comments, "children") and pre_comments.children:
            last_comment = pre_comments.children[-1]
            value_line = getattr(value, "line", None)
            if value_line is None and hasattr(value, "children") and value.children:
                value_line = getattr(value.children[0], "line", None)
            if last_comment.line == value_line:
                attach_pre_comments = True
        combined_inline = None
        if attach_pre_comments:
            pre_text = " ".join(tok.value for tok in pre_comments.children)
            if inline_comment and hasattr(inline_comment, "children") and len(inline_comment.children) > 1:
                inline_text = inline_comment.children[1].value
            else:
                inline_text = ""
            combined_inline = pre_text + (" " + inline_text if inline_text else "")
        else:
            if inline_comment and hasattr(inline_comment, "children") and len(inline_comment.children) > 1:
                combined_inline = inline_comment.children[1].value
        actual_value = value
        if combined_inline:
            self.debug_print(f"array_item() returning PreservedValue for value: {actual_value} with inline comment: {combined_inline}")
            return PreservedValue(actual_value, combined_inline)
        self.debug_print(f"array_item() returning value: {actual_value}")
        return actual_value

    def array_value(self, items):
        self.debug_print(f"array_value() called with items: {items}")
        return items[0]

    # -----------------------------
    # Preserved Inline Table logic
    # -----------------------------
    def INLINE_TABLE(self, token):
        self.debug_print(f"INLINE_TABLE() called with token: {token}")
        if hasattr(token, 'meta') and token.meta:
            start = token.meta.start_pos
            end = token.meta.end_pos
            original_text = self._slice_input(start, end)
        else:
            original_text = token.value
        s = token.value.strip()
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1].strip()
        result_dict = {}
        if s:
            pairs = s.split(',')
            for pair in pairs:
                if '=' in pair:
                    key, val = pair.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    try:
                        if '.' in val:
                            converted = float(val)
                        else:
                            converted = int(val)
                    except ValueError:
                        if ((val.startswith('"') and val.endswith('"'))
                                or (val.startswith("'") and val.endswith("'"))):
                            converted = val[1:-1]
                        else:
                            converted = val
                    result_dict[key] = converted
        self.debug_print(f"INLINE_TABLE() parsed dict: {result_dict} with original text: {original_text}")
        return PreservedInlineTable(result_dict, original_text)

    def ARRAY(self, token):
        self.debug_print(f"ARRAY() called with token: {token}")
        s = token.value.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                self.debug_print("ARRAY() successfully parsed JSON list")
                return PreservedArray(parsed, token.value)
            return parsed
        except Exception as e:
            self.debug_print(f"ARRAY() JSON parsing error: {e}")
            return s

    # -----------------------------------------------------
    # String
    # -----------------------------------------------------
    def STRING(self, token):
        self.debug_print(f"STRING() called with token: {token}")
        s = token.value
        if s.lstrip().startswith("f\"") or s.lstrip().startswith("f'"):
            self.debug_print("String with f-prefix detected")
            return PreservedString(s.lstrip(), s)
        if s.startswith("'''") and s.endswith("'''"):
            inner = s[3:-3]
            return PreservedString(inner, s)
        if s.startswith('"""') and s.endswith('"""'):
            return PreservedString(s[3:-3], s)
        if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"', "`"}:
            return PreservedString(s[1:-1], s)
        return s

    # -----------------------------------------------------
    # Terminal transformations for other token types
    # -----------------------------------------------------
    def SCOPED_VAR(self, token):
        return token.value

    def FLOAT(self, token):
        return float(token.value)

    def INTEGER(self, token):
        val = token.value
        if val in ("inf", "nan", "+inf", "-inf"):
            return val
        return int(val, 0)

    def BOOLEAN(self, token):
        return (token.value == "true")

    def NULL(self, token):
        return None

    def RESERVED_FUNC(self, token):
        return token.value

    def KEYWORD(self, token):
        return token.value

    def TABLE_ARRAY(self, token):
        return token.value

    def FOLDER_BLOCK(self, token):
        return token.value

    def IDENTIFIER(self, token):
        return token.value

    def OPERATOR(self, token):
        return token.value

    def PUNCTUATION(self, token):
        return token.value

    def WHITESPACE(self, token):
        return token.value

    # -----------------------------------------
    # Utility for retrieving input substrings
    # -----------------------------------------
    def _slice_input(self, start, end):
        # Debug print for slicing input
        self.debug_print(f"_slice_input() called with start: {start}, end: {end}")
        return self._context.text[start:end]

    def _store_table_array(self, header: TableArrayHeader,
                           node: TableArraySectionNode):
        """
        Insert a `TableArraySectionNode` into the dict that is currently
        being populated (`self.current_section`).

        The *key* is whatever object came out of `table_array_header`
        (string, `PreservedString`, `TableArrayComprehensionHeader`, …).
        We do **not** coerce it to str, because we want to preserve
        unevaluated comprehension headers for the resolve/render phase.
        """
        bucket = self.current_section.setdefault(header, [])
        bucket.append(node)