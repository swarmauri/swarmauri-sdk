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
    DeferredExpression,
    FoldedExpressionNode
    )

class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        # Store normal data in __default__ or nested sections
        self.data = {
            "__comments__": [] 
        }
        self.current_section = self.data
        self.in_deferred = False

    def start(self, items):
        return self.data

    def assignment(self, items):
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

        # Only unquote if value is a plain string
        if not isinstance(value, PreservedString) and isinstance(value, str) and (
            (value.startswith("'") and value.endswith("'")) or 
            (value.startswith('"') and value.endswith('"'))
        ):
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
        else:
            self.current_section[key] = PreservedValue(value, inline) if inline else value

        return None




    def section(self, items):
        raw_section = items[0]
        if isinstance(raw_section, list):
            # Nested unquoted section e.g. [user.profile]
            d = self.data
            for part in raw_section:
                d = d.setdefault(part, {})
            self.current_section = d
            return d
        else:
            # Quoted or single section name
            if raw_section not in self.data:
                self.data[raw_section] = {}
            self.current_section = self.data[raw_section]
            return self.data[raw_section]



    def section_name(self, items):
        return items

    def type_annotation(self, items):
        return items[0]

    # --------------------------
    # Simple leaf transformations
    # --------------------------
    def paren_expr(self, items):
        return "(" + " ".join(str(x) for x in items) + ")"

    def deferred_content(self, items):
        def to_string(x):
            if isinstance(x, list):
                return "".join(to_string(subx) for subx in x)
            elif hasattr(x, '__iter__') and not isinstance(x, str):
                return "".join(to_string(subx) for subx in x)
            else:
                return str(x)
        return to_string(items)

    @v_args(meta=True)
    def deferred_expr(self, meta, items):
        # Capture the entire literal substring
        full_text = self._slice_input(meta.start_pos, meta.end_pos)

        # If it starts with `<{`, proceed with a deferred expression:
        if full_text.lstrip().startswith("<{"):
            # e.g. "<{'Yes' if true else 'No'}>"
            # strip away <{  }>
            inner_expr = full_text.lstrip()[2:-2].strip()

            # Instead of forcibly wrapping in f"..." if there's ' if ', remove that hack.
            # We'll keep the expression exactly as is to pass your test.

            return DeferredExpression(
                expr=inner_expr,
                local_env=self.current_section.copy(),
                original_text=full_text
            )

        elif full_text.lstrip().startswith("<("):
            # This branch is for folded expressions, can be handled as before
            content = full_text.lstrip()[2:-2].strip()
            context = {"true": True, "false": False}
            try:
                result = eval(content, {"__builtins__": {}}, context)
                return result
            except Exception:
                return content
        else:
            # fallback or else-case
            return self.deferred_content(items)


    @v_args(meta=True)
    def folded_expr(self, meta, items):
        # items typically includes: [ FOLDED_START, <sub-tree for folded_content>, FOLDED_END ]
        # We'll build a FoldedExpressionNode that has: original_text + the token children.

        full_text = self._slice_input(meta.start_pos, meta.end_pos)

        # 'children' might be something like:
        # [
        #   Token('FOLDED_START', '<('),
        #   Tree(Token('RULE','folded_content'), children=[...]),
        #   Token('FOLDED_END', ')>')
        # ]
        # We'll pick out the folded_content portion:
        # The typical arrangement is items[1] if the grammar yields them in that order.

        folded_content_tree = None
        for child in items:
            if hasattr(child, "data") and child.data == "folded_content":
                folded_content_tree = child
                break
        
        return FoldedExpressionNode(full_text, folded_content_tree)

    def comprehension_expr(self, items):
        """
        Process a comprehension expression.
        In our grammar, the comprehension_expr rule might simply wrap a value.
        For simplicity, if there's a single child that is a string (or PreservedString),
        return its unwrapped value.
        """
        # If the item is a PreservedString, return its inner (unquoted) value.
        if len(items) == 1:
            child = items[0]
            if isinstance(child, PreservedString):
                return child.value
            return child
        # Otherwise, join the items together
        return "".join(str(i) for i in items)

    @v_args(meta=True)
    def list_comprehension(self, meta, items):
        """
        Transforms a list comprehension into a DeferredDictComprehension node.
        
        Instead of immediately evaluating:
          [f"item_{x}" for x in [1, 2, 3]]
        we capture the original raw text of the comprehension (including the enclosing square brackets)
        and wrap it in a DeferredDictComprehension node. This ensures that:
          - After round_trip_loads, the value equals the raw string:
                '[f"item_{x}" for x in [1, 2, 3]]'
          - In the resolve or render phase, the DeferredDictComprehension's evaluate() method
            will be called to produce the computed list (e.g. ["item_1", "item_2", "item_3"]).
        """
        # Obtain the entire original text (including brackets, etc.)
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        # Return a DeferredDictComprehension node containing the raw text.
        return DeferredListComprehension(original_text)



    # Optionally, add a transformer for dict comprehensions.
    @v_args(meta=True)
    def dict_comprehension(self, meta, items):
        """
        Process a dict comprehension.
        Instead of immediately evaluating, capture its raw text.
        For an input like:
          dict_config = {f"key_{x}" : x * 2 for x in [1, 2, 3]}
        we capture the full text including the outer braces,
        so that round_trip_loads produces:
          '{f"key_{x}" : x * 2 for x in [1, 2, 3]}'
        """
        # Use meta.start_pos and meta.end_pos to capture the original substring.
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        # Do not remove the outer braces: return the full original text.
        return DeferredDictComprehension(original_text)





    def inline_assignment(self, items):
        """
        Transforms an inline assignment (e.g. x = 10 or x: type = 10) into a dictionary.
        Handles optional type annotations. Supports both forms:
          - Without a colon: e.g. x = 10
          - With a colon: e.g. x: type = 10
        """
        # If the second item is a COLON token, then we expect the structure:
        # [IDENTIFIER, COLON, type_annotation, value, (optional inline_comment)]
        if len(items) >= 4 and isinstance(items[1], Token) and items[1].type == "COLON":
            key = items[0]
            type_annotation = items[2]
            value = items[3]
            inline = items[4] if len(items) > 4 else None
        else:
            # Otherwise, use the old cases.
            if len(items) == 2:
                key, value = items
                inline = None
            elif len(items) == 3:
                # Determine if the third is inline comment or a type annotation.
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
        
        return { key: value }


    def inline_table_item(self, items):
        """
        Unwrap the inline table item.
        Typically, an inline_table_item wraps an inline_assignment.
        """
        # Assuming there's a single child (the inline_assignment or a comment)
        return items[0]

    def inline_table_items(self, items):
        """
        Process the children of the inline_table_items rule.
        Filter out whitespace nodes.
        """
        def is_ignorable(x):
            if hasattr(x, "data") and x.data == "ws":
                return True
            if isinstance(x, str) and x.strip() == "":
                return True
            return False

        return [x for x in items if not is_ignorable(x)]

    @v_args(meta=True)
    def inline_table(self, meta, children):
        result = {}
        for item in children:
            if isinstance(item, list):
                # Process list items (e.g. the output of inline_table_items)
                for subitem in item:
                    if isinstance(subitem, dict):
                        result.update(subitem)
                    elif hasattr(subitem, "data") and subitem.data == "inline_table_item":
                        transformed = self.inline_table_item(subitem.children)
                        if isinstance(transformed, dict):
                            result.update(transformed)
            elif hasattr(item, "data") and item.data == "inline_table_items":
                for child in item.children:
                    if hasattr(child, "data") and child.data == "inline_table_item":
                        transformed = self.inline_table_item(child.children)
                        if isinstance(transformed, dict):
                            result.update(transformed)
                    elif isinstance(child, dict):
                        result.update(child)
            elif isinstance(item, dict):
                result.update(item)
        # Use meta.start_pos and meta.end_pos to capture the original text
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        return PreservedInlineTable(result, original_text)

    # -----------------------------
    # Comments
    # -----------------------------
    def comment_line(self, items):
        comment_token = items[0]
        # Only add a standalone comment if it begins at the start of the line.
        if hasattr(comment_token, "column") and comment_token.column == 1:
            self.data["__comments__"].append(comment_token.value)
        return comment_token.value


    def inline_comment(self, items):
        # items[0] is the INLINE_WS token, items[1] is the COMMENT token.
        ws = items[0].value
        com = items[1].value
        return {"_inline_comment": ws + com}

    # -----------------------------
    # Preserved Array logic
    # -----------------------------
    @v_args(meta=True)
    def array(self, meta, items):
        array_values = []
        for item in items:
            # Ignore tokens for array delimiters and whitespace/newlines.
            if isinstance(item, Token) and item.type in ("LBRACK", "RBRACK", "NEWLINE", "WHITESPACE"):
                continue
            # Also ignore plain strings that are empty/whitespace.
            if isinstance(item, str) and item.strip() == "":
                continue
            # If the item is a list, extend the values.
            if isinstance(item, list):
                array_values.extend(item)
            else:
                array_value
                s.append(item)
        original_text = self._slice_input(meta.start_pos, meta.end_pos)
        return PreservedArray(array_values, original_text)




    def array_content(self, items):
        def is_ignorable(x):
            if hasattr(x, "data") and x.data == "ws":
                return True
            if isinstance(x, str) and x.strip() == "":
                return True
            if isinstance(x, Token) and x.type in ("WHITESPACE", "NEWLINE"):
                return True
            return False

        # Do not filter out comment lines—preserve them in the array
        return [x for x in items if x != "," and not is_ignorable(x)]

    def array_item(self, items):
        # Expect items in the order:
        # [optional pre_item_comments, value, optional inline_comment, optional post_item_comments]
        pre_comments = None
        value = None
        inline_comment = None

        items = list(items)  # ensure we can pop items

        # If the first item is pre_item_comments, extract it.
        if items and hasattr(items[0], "data") and items[0].data == "pre_item_comments":
            pre_comments = items.pop(0)
        # Next, the value token should be present.
        if items:
            value = items.pop(0)
        # If the next item is an inline_comment, extract it.
        if items and hasattr(items[0], "data") and items[0].data == "inline_comment":
            inline_comment = items.pop(0)
        
        # At this point, post_item_comments (if any) are in items but we usually ignore them for the value.

        # Determine if the pre_comments should be merged into the inline comment:
        # We'll check if the last comment token in pre_comments is on the same line as the value.
        attach_pre_comments = False
        if pre_comments and hasattr(pre_comments, "children") and pre_comments.children:
            # Assume tokens have a 'line' attribute.
            last_comment = pre_comments.children[-1]
            # Also assume the value token (or its first child if it's a Tree) has a 'line' attribute.
            value_line = getattr(value, "line", None)
            if value_line is None and hasattr(value, "children") and value.children:
                value_line = getattr(value.children[0], "line", None)
            if last_comment.line == value_line:
                attach_pre_comments = True

        # If they are on the same line, combine their texts into the inline comment.
        combined_inline = None
        if attach_pre_comments:
            pre_text = " ".join(tok.value for tok in pre_comments.children)
            if inline_comment and hasattr(inline_comment, "children") and len(inline_comment.children) > 1:
                # inline_comment: [INLINE_WS, COMMENT]
                inline_text = inline_comment.children[1].value
            else:
                inline_text = ""
            combined_inline = pre_text + (" " + inline_text if inline_text else "")
        else:
            # Otherwise, ignore pre_comments for attaching to the value.
            if inline_comment and hasattr(inline_comment, "children") and len(inline_comment.children) > 1:
                combined_inline = inline_comment.children[1].value

        # Now, only include the value in the array if it's a real value,
        # not if it's coming solely from commented-out lines.
        # For example, if 'value' is an INTEGER token, convert it; if it's a Tree or already preserved, let it be.
        # (Your existing transformation for numeric tokens should already handle conversion.)
        actual_value = value

        # Wrap the value in a PreservedValue only if there is an inline comment to attach.
        if combined_inline:
            return PreservedValue(actual_value, combined_inline)
        return actual_value






    def array_value(self, items):
        # Typically a list with one element
        return items[0]

    # -----------------------------
    # Preserved Inline Table logic
    # -----------------------------
    def INLINE_TABLE(self, token):
        """
        Keep entire { ... } text, but also parse it to a dict so code can read the data.
        """
        if hasattr(token, 'meta') and token.meta:
            start = token.meta.start_pos
            end = token.meta.end_pos
            original_text = self._slice_input(start, end)
        else:
            original_text = token.value

        # Parse key=value pairs simply so we can store them in the dict portion.
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
                    # Attempt numeric conversion
                    try:
                        # If there's a '.', might be float
                        if '.' in val:
                            converted = float(val)
                        else:
                            converted = int(val)
                    except ValueError:
                        # If wrapped in quotes, remove them
                        if ((val.startswith('"') and val.endswith('"'))
                                or (val.startswith("'") and val.endswith("'"))):
                            converted = val[1:-1]
                        else:
                            converted = val
                    result_dict[key] = converted

        return PreservedInlineTable(result_dict, original_text)

    def ARRAY(self, token):
        """
        If the grammar had a token-based ARRAY fallback, keep it. 
        We'll just store it as PreservedArray if possible.
        """
        s = token.value.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                # Reconstruct bracketed text
                return PreservedArray(parsed, token.value)
            return parsed
        except Exception:
            return s



    # -----------------------------------------------------
    # String
    # -----------------------------------------------------

    def STRING(self, token):
        s = token.value
        # Check if the string (after stripping leading whitespace) starts with an f-prefix.
        if s.lstrip().startswith("f\"") or s.lstrip().startswith("f'"):
            # Preserve the f-string instead of evaluating it
            return PreservedString(s.lstrip(), s)
        
        # Standard handling for triple-quoted strings.
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
        """
        Return the exact substring from the original input text
        (assuming self._context.text was set).
        """
        return self._context.text[start:end]
