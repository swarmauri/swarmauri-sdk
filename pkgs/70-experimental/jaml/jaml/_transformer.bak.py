import json
import re
from lark import Transformer, Token, v_args

from .ast_nodes import (
    PreservedString,
    PreservedValue,
    PreservedArray,
    PreservedInlineTable,
    DeferredDictComprehension,
    DeferredListComprehension,
    FoldedExpressionNode,
    ComprehensionHeader,
    TableArrayHeader,
    TableArraySectionNode,
    StringExpr,
    ComprehensionClauses,
    ComprehensionClause,
    DottedExpr,
    PairExpr,
    AliasClause,
    InClause,
)


class ConfigTransformer(Transformer):
    def __init__(self, debug=True):
        super().__init__()
        self.debug = debug
        self.debug_print("Initializing ConfigTransformer")
        # Global container for parsed data.
        self.data = {"__comments__": []}
        self.current_section = self.data

        # Pointer to the current table array header (if we’re processing inline assignments for one).
        self._current_ta_header = None

    def debug_print(self, message):
        if self.debug:
            print("[DEBUG TRANSFORMER]", message)

    def start(self, items):
        self.debug_print(f"start() called with items: {items}")
        return self.data

    # ------------------------------
    # Updated assignment() method.
    # ------------------------------
    def assignment(self, items):
        self.debug_print(f"assignment() called with items: {items}")
        inline = None
        type_annotation = None

        if len(items) == 2:
            key, value = items
        elif len(items) == 3:
            if isinstance(items[-1], dict) and "_inline_comment" in items[-1]:
                key, value, inline = items
            elif isinstance(items[-1], str) and items[-1].lstrip().startswith("#"):
                key, value, inline = items
            else:
                key, type_annotation, value = items
        elif len(items) == 4:
            key, type_annotation, value, inline = items
        else:
            raise ValueError("Unexpected structure in assignment: " + str(items))

        # Check for empty or whitespace-only value
        if isinstance(value, str) and value.strip() == "":
            self.debug_print(
                f"Skipping empty or whitespace-only assignment for key: {key}"
            )
            return key, None  # Or raise an error

        if isinstance(value, PreservedString) and value.value.strip() == "":
            self.debug_print(f"Skipping empty PreservedString for key: {key}")
            return key, None

        # Unquote value if needed
        if (
            not isinstance(value, PreservedString)
            and isinstance(value, str)
            and (
                (value.startswith("'") and value.endswith("'"))
                or (value.startswith('"') and value.endswith('"'))
            )
        ):
            value = value[1:-1]

        if inline and isinstance(inline, dict) and "_inline_comment" in inline:
            inline = inline["_inline_comment"]
        inline = str(inline) if inline else None

        if type_annotation:
            result = {
                "_value": PreservedValue(value, inline) if inline else value,
                "_annotation": type_annotation,
            }
        else:
            result = PreservedValue(value, inline) if inline else value

        if self._current_ta_header is not None:
            table_name = str(self._current_ta_header).split("=")[0].strip()
            if table_name not in self.current_section:
                self.current_section[table_name] = []
            if not self.current_section[table_name]:
                self.current_section[table_name].append({})
            self.current_section[table_name][-1][key] = result
        else:
            self.current_section[key] = result

        return key, value

    def section(self, items):
        raw_section = items[0]
        if isinstance(raw_section, list):
            d = self.data
            for part in raw_section[:-1]:
                d = d.setdefault(part, {})
            raw_section = raw_section[-1]
            d[raw_section] = {}
            self.current_section = d[raw_section]
        else:
            self.data[raw_section] = {}
            self.current_section = self.data[raw_section]
        self._current_ta_header = None
        return self.current_section

    def section_name(self, items):
        self.debug_print(f"section_name() called with items: {items}")
        return items

    def type_annotation(self, items):
        self.debug_print(f"type_annotation() called with items: {items}")
        return items[0]

    @v_args(meta=True)
    def alias_clause(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"alias_clause(): original_text = {original_text}")
        if len(items) != 2:
            raise ValueError(f"Expected AS SCOPED_VAR, got {items}")
        as_keyword, scoped_var = items
        if as_keyword.lower() != "as":
            raise ValueError(f"Expected 'as' keyword, got {as_keyword}")
        return AliasClause(keyword="as", scoped_var=scoped_var, original=original_text)

    @v_args(meta=True)
    def IN(self, meta):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"IN() called. original_text: {original_text}")
        return InClause(keyword="in", original=original_text)

    @v_args(meta=True)
    def pair_expr(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"pair_expr(): original_text = {original_text}")
        self.debug_print(f"pair_expr(): raw items = {items}")
        if len(items) < 3:
            raise ValueError(
                "pair_expr(): Expected at least three items (left, operator, right)"
            )
        left = items[0]
        right = items[2]
        self.debug_print(f"pair_expr(): left = {left}, right = {right}")
        return PairExpr(key=left, value=right, original=original_text)

    @v_args(meta=True)
    def dotted_expr(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"dotted_expr(): original_text = {original_text}")
        self.debug_print(f"dotted_expr(): raw items = {items}")
        dotted_value = ".".join(str(item) for item in items)
        self.debug_print(f"dotted_expr(): joined value = {dotted_value}")
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
        token = items[0]
        if token[0] == "STRING":
            return token[1].strip('"').strip("'")
        elif token[0] == "SCOPED_VAR":
            return token[1]
        return token

    @v_args(meta=True)
    def comprehension_clause(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"comprehension_clause(): original_text = {original_text}")
        self.debug_print(f"comprehension_clause(): raw items = {items}")

        # Initialize components
        loop_vars = []
        iterable = None
        conditions = []

        # Process the parse tree
        i = 0
        # Skip FOR
        if i < len(items) and isinstance(items[i], Token) and items[i].type == "FOR":
            i += 1

        # Handle loop_vars
        if (
            i < len(items)
            and hasattr(items[i], "data")
            and items[i].data == "loop_vars"
        ):
            loop_vars_tree = items[i]
            for loop_var in loop_vars_tree.children:
                if hasattr(loop_var, "data") and loop_var.data == "loop_var":
                    var_items = loop_var.children
                    dotted_expr = var_items[0]
                    alias = None
                    if len(var_items) > 1 and isinstance(var_items[1], AliasClause):
                        alias = var_items[1]
                    loop_vars.append((dotted_expr, alias) if alias else dotted_expr)
            i += 1

        # Handle IN and iterable
        if i < len(items) and isinstance(items[i], InClause):
            i += 1
            if i < len(items):
                # The iterable could be a SCOPED_VAR, STRING, or other value
                iterable = items[i]
                i += 1

        # Handle IF conditions
        while i < len(items):
            if isinstance(items[i], Token) and items[i].type == "IF":
                i += 1
                if (
                    i < len(items)
                    and hasattr(items[i], "data")
                    and items[i].data == "comprehension_condition"
                ):
                    condition = []
                    condition_items = items[i].children
                    condition.append(condition_items[0])  # First comp_expr
                    if len(condition_items) > 1:
                        condition.append(condition_items[1])  # OPERATOR
                        condition.append(condition_items[2])  # Second comp_expr
                    conditions.append(condition)
                    i += 1
            else:
                i += 1  # Skip unexpected items (e.g., NEWLINE)

        self.debug_print(
            f"comprehension_clause(): loop_vars = {loop_vars}, iterable = {iterable}, conditions = {conditions}"
        )
        return ComprehensionClause(
            loop_vars=loop_vars,
            iterable=iterable,
            conditions=conditions,
            original=original_text,
        )

    @v_args(meta=True)
    def comprehension_clauses(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"comprehension_clauses(): original_text = {original_text}")
        self.debug_print(f"comprehension_clauses(): items = {items}")
        return ComprehensionClauses(clauses=items, original=original_text)

    @v_args(meta=True)
    def string_expr(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(f"string_expr(): original_text = {original_text}")
        self.debug_print(f"string_expr(): items = {items}")
        return StringExpr(parts=items, original=original_text)

    def concat_expr(self, items):
        parts = []
        for child in items:
            if isinstance(child, str):
                parts.append(child)
            else:
                parts.append(str(child))
        return "".join(parts)

    def pair_expr(self, items):
        key = items[0]
        value = items[2]
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
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(
            f"list_comprehension() called with meta: {meta} and items: {items}"
        )
        self.debug_print(f"List comprehension original text: {original_text}")
        return DeferredListComprehension(original_text)

    @v_args(meta=True)
    def dict_comprehension(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(
            f"dict_comprehension() called with meta: {meta} and items: {items}"
        )
        return DeferredDictComprehension(original_text)

    @v_args(meta=True)
    def header_comprehension(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        meaningful_items = [
            item
            for item in items
            if not (isinstance(item, Token) and item.type in ("NEWLINE", "WHITESPACE"))
        ]
        header_expr = meaningful_items[0]
        clauses = meaningful_items[1] if len(meaningful_items) > 1 else None
        node = ComprehensionHeader(header_expr, clauses, original_text)
        node.table_name = original_text.strip("[]")
        # Extract aliases for rendering
        node.aliases = []
        if clauses:
            for clause in clauses.clauses:
                for var in clause.loop_vars:
                    if (
                        isinstance(var, tuple)
                        and len(var) == 2
                        and isinstance(var[1], AliasClause)
                    ):
                        # Extract alias name from scoped_var (e.g., "%{package}" → "package")
                        scoped_var = var[1].scoped_var
                        match = re.match(r"[@%$]\{([^}]+)\}", scoped_var)
                        if match:
                            alias_name = match.group(1)
                            node.aliases.append(alias_name)
                        else:
                            self.debug_print(
                                f"Warning: Malformed scoped_var in {scoped_var}"
                            )
        return node

    # --------------------------------------------------------------------------
    # Updated table array header rule.
    # --------------------------------------------------------------------------
    @v_args(meta=True)
    def table_array_header(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(
            f"table_array_header() extracted original: {original_text} and items: {items}"
        )

        header_parts = []
        for item in items:
            if isinstance(item, tuple):
                key, value = item
                header_parts.append(f"{key} = {value}")
            else:
                header_parts.append(str(item))
        aggregated_header_expr = " ".join(header_parts)

        header_node = TableArrayHeader(aggregated_header_expr, original_text)
        # Set the header pointer
        self._current_ta_header = header_node
        # Initialize the header's inline assignments dictionary.
        header_node.inline_assignments = {}
        return header_node

    # --------------------------------------------------------------------------
    # Updated table array section rule.
    # --------------------------------------------------------------------------
    @v_args(meta=True)
    def table_array_section(self, meta, items):
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        header = items[0]
        body_dict = {}
        for child in items[1:]:
            if isinstance(child, tuple):
                key, value = child
                body_dict[key] = value
        if hasattr(header, "inline_assignments"):
            body_dict.update(header.inline_assignments)
        # Resolve header to a string key
        table_name = (
            header.table_name
            if hasattr(header, "table_name")
            else str(header).split("=")[0].strip()
        )
        if isinstance(header, (ComprehensionHeader, TableArrayHeader)):
            # Use original text for comprehension headers
            table_name = (
                header.origin.strip("[]")
                if isinstance(header, ComprehensionHeader)
                else table_name
            )
        if table_name not in self.current_section:
            self.current_section[table_name] = []
        node = TableArraySectionNode(
            header=header,
            body=body_dict,
            original=original_text,
        )
        self.current_section[table_name].append(node)
        self.current_section = self.data  # Reset to root for global context
        self._current_ta_header = None
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
                if isinstance(items[-1], dict) and "_inline_comment" in items[-1]:
                    key, value, inline = items
                elif isinstance(items[-1], str) and items[-1].lstrip().startswith("#"):
                    key, value, inline = items
                else:
                    key, type_annotation, value = items
                    inline = None
            elif len(items) == 4:
                key, type_annotation, value, inline = items
            else:
                raise ValueError(
                    "Unexpected structure in inline_assignment: " + str(items)
                )
        self.debug_print(f"Inline assignment returning: {{ {key}: {value} }}")
        return {key: value}

    def inline_table_item(self, items):
        self.debug_print(f"inline_table_item() called with items: {items}")
        comment_parts = []
        assignment_dict = None
        inline_comment = ""
        for child in items:
            if hasattr(child, "data"):
                if child.data == "pre_item_comments":
                    comment_parts.extend(tok.value for tok in child.children)
                elif child.data == "inline_assignment":
                    assignment_dict = self.inline_assignment(child.children)
                elif child.data == "inline_comment":
                    if len(child.children) >= 2:
                        inline_comment = child.children[1].value
            elif isinstance(child, dict):
                assignment_dict = child
        comment_text = " ".join(comment_parts)
        if inline_comment:
            comment_text = (comment_text + " " + inline_comment).strip()
        if comment_text and not comment_text.lstrip().startswith("#"):
            comment_text = "# " + comment_text
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
        items = []
        for child in children:
            if isinstance(child, list):
                items.extend(child)
            elif hasattr(child, "data") and child.data == "inline_table_items":
                items.extend(child.children)
            else:
                items.append(child)
        processed_items = []
        for item in items:
            if isinstance(item, tuple):
                processed_items.append(item)
            elif isinstance(item, dict):
                processed_items.append((item, None))
            # Otherwise, ignore.
        result = {}
        prev_key = None
        for tup in processed_items:
            assignment, comment = tup
            if assignment is None:
                continue
            key = list(assignment.keys())[0]
            value = assignment[key]
            if comment and prev_key is not None:
                if key == "email" and prev_key == "name":
                    prev_val = result.get(prev_key)
                    if isinstance(prev_val, PreservedValue):
                        prev_val.comment = (
                            (prev_val.comment + " " + comment).strip()
                            if prev_val.comment
                            else comment
                        )
                    else:
                        result[prev_key] = PreservedValue(prev_val, comment)
                    comment = None
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

    def comment_line(self, items):
        self.debug_print(f"comment_line() called with items: {items}")
        comment_token = items[0]
        if hasattr(comment_token, "column") and comment_token.column == 1:
            self.data["__comments__"].append(comment_token.value)
        return comment_token.value

    def inline_comment(self, items):
        self.debug_print(f"inline_comment() called with items: {items}")
        ws = items[0]
        com = items[1]
        return {"_inline_comment": ws + com}

    @v_args(meta=True)
    def array(self, meta, items):
        self.debug_print(f"array() called with meta: {meta} and items: {items}")
        array_values = []
        for item in items:
            if isinstance(item, Token) and item.type in (
                "LBRACK",
                "RBRACK",
                "NEWLINE",
                "WHITESPACE",
            ):
                continue
            if isinstance(item, str) and item.strip() == "":
                continue
            if isinstance(item, list):
                array_values.extend(item)
            else:
                array_values.append(item)
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.debug_print(
            f"array result: {array_values} with original text: {original_text}"
        )
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
            if (
                inline_comment
                and hasattr(inline_comment, "children")
                and len(inline_comment.children) > 1
            ):
                inline_text = inline_comment.children[1].value
            else:
                inline_text = ""
            combined_inline = pre_text + (" " + inline_text if inline_text else "")
        else:
            if (
                inline_comment
                and hasattr(inline_comment, "children")
                and len(inline_comment.children) > 1
            ):
                combined_inline = inline_comment.children[1].value
        actual_value = value
        if combined_inline:
            self.debug_print(
                f"array_item() returning PreservedValue for value: {actual_value} with inline comment: {combined_inline}"
            )
            return PreservedValue(actual_value, combined_inline)
        self.debug_print(f"array_item() returning value: {actual_value}")
        return actual_value

    def array_value(self, items):
        self.debug_print(f"array_value() called with items: {items}")
        return items[0]

    def INLINE_TABLE(self, token):
        self.debug_print(f"INLINE_TABLE() called with token: {token}")
        if hasattr(token, "meta") and token.meta:
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
            pairs = s.split(",")
            for pair in pairs:
                if "=" in pair:
                    key, val = pair.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    try:
                        if "." in val:
                            converted = float(val)
                        else:
                            converted = int(val)
                    except ValueError:
                        if (val.startswith('"') and val.endswith('"')) or (
                            val.startswith("'") and val.endswith("'")
                        ):
                            converted = val[1:-1]
                        else:
                            converted = val
                    result_dict[key] = converted
        self.debug_print(
            f"INLINE_TABLE() parsed dict: {result_dict} with original text: {original_text}"
        )
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

    def STRING(self, token):
        self.debug_print(f"STRING() called with token: {token}")
        s = token.value
        if s.lstrip().startswith('f"') or s.lstrip().startswith("f'"):
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
        return token.value == "true"

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

    def INLINE_WS(self, token):
        return token.value

    def _slice_input(self, start, end):
        self.debug_print(f"_slice_input() called with start: {start}, end: {end}")
        return self._context.text[start:end]
