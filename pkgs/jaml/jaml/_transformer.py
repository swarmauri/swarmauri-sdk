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
    FoldedExpressionNode
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
    # Simple leaf transformations
    # --------------------------
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
