from importlib.resources import files, as_file
import json
import re
from lark import Lark, Transformer, Token, v_args
from ._helpers import (
    unquote, 
    resolve_scoped_variable, 
    evaluate_f_string, 
    evaluate_immediate_expression
)  

class DeferredExpression:
    def __init__(self, expr, local_env=None):
        self.expr = expr  # The raw inner text, e.g. "%{base} + '/config.toml'"
        self.local_env = local_env or {}
    def evaluate(self, global_env):
        # Combine the local environment stored with this expression with the global environment.
        env = {}
        env.update(global_env)
        env.update(self.local_env)
        # Substitute self-scope markers (e.g. %{...}) in self.expr.
        substituted = evaluate_immediate_expression(self.expr, {}, env)
        try:
            return eval(substituted, {"__builtins__": {}}, {"true": True, "false": False})
        except Exception:
            return self.expr
    def __str__(self):
        # When converting to string for dumping, output with delimiters.
        return f"<{{ {self.expr} }}>"
    def __repr__(self):
        return f"DeferredExpression({self.expr!r}, local_env={self.local_env!r})"
    def __eq__(self, other):
        if isinstance(other, str):
            return self.expr == other
        if isinstance(other, DeferredExpression):
            return self.expr == other.expr and self.local_env == other.local_env
        return False



class PreservedString(str):
    def __new__(cls, value, original):
        # Create a new string instance using the unquoted value.
        obj = super().__new__(cls, value)
        obj.value = value
        obj.original = original  # store the original text, e.g. '"Hello, World!"'
        return obj

    def __str__(self):
        # When converting to string for round-trip output, return the original quoted text.
        return self.original

    def __repr__(self):
        return f"PreservedString(value={super().__str__()!r}, original={self.original!r})"


class PreservedValue:
    def __init__(self, value, comment=None):
        self.value = value
        self.comment = comment  # e.g. '  # Inline comment: greeting message'
    
    def __str__(self):
        # When converting to string for round-trip output, append the comment if present.
        if self.comment:
            return f'{self.value}{self.comment}'
        return str(self.value)
    
    def __repr__(self):
        return f"PreservedValue(value={self.value!r}, comment={self.comment!r})"

class PreservedArray(list):
    """
    Stores both the parsed items (as a list) and the original bracketed text,
    allowing both list access and perfect round-trip.
    """
    def __init__(self, items, original_text):
        super().__init__(items)
        self.original_text = original_text  # the entire "[ ... ]" text

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self) == other
        return super().__eq__(other)

    def __repr__(self):
        return f"PreservedArray({list(self)!r}, text={self.original_text!r})"

    def __str__(self):
        return self.original_text


class PreservedInlineTable(dict):
    """
    Subclass dict so code using it sees a normal dict,
    but store 'original_text' for exact round-trip.
    """
    def __init__(self, data, original_text):
        super().__init__(data)  # parse dict content
        self.original_text = original_text

    def __repr__(self):
        return f"PreservedInlineTable(data={dict(self)}, text={self.original_text!r})"

    def __str__(self):
        # Return the brace-delimited text exactly as originally parsed.
        return self.original_text


class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        # Store normal data in __default__ or nested sections
        self.data = {
            "__default__": {},
            "__comments__": [] 
        }
        self.current_section = self.data["__default__"]
        self.in_tilde = False

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

    def tilde_content(self, items):
        def to_string(x):
            if isinstance(x, list):
                return "".join(to_string(subx) for subx in x)
            elif hasattr(x, '__iter__') and not isinstance(x, str):
                return "".join(to_string(subx) for subx in x)
            else:
                return str(x)
        return to_string(items)

    @v_args(meta=True)
    def tilde_block(self, meta, items):
        was_in_tilde = self.in_tilde
        self.in_tilde = True
        # Assume we capture the entire expression using meta information.
        # For example, get the original text from self._slice_input(meta.start_pos, meta.end_pos)
        # Here we'll assume that items[0] holds the entire expression text.
        # (You may need to adjust to your actual AST.)
        full_text = self._slice_input(meta.start_pos, meta.end_pos)
        self.in_tilde = was_in_tilde
        # Check the delimiter: immediate expressions start with "<{"
        if full_text.lstrip().startswith("<{"):
            # Strip off the delimiters and surrounding whitespace.
            inner_expr = full_text.lstrip()[2:-2].strip()
            # Defer evaluation by wrapping in DeferredExpression,
            # storing the current section as the local environment.
            return DeferredExpression(inner_expr, local_env=self.current_section.copy())
        elif full_text.lstrip().startswith("<("):
            # For folded expressions (<( ... )>), evaluate as much as possible immediately.
            content = full_text.lstrip()[2:-2].strip()
            if isinstance(content, str) and '%{' in content:
                content = evaluate_immediate_expression(content, self.data, self.current_section)
            context = {"true": True, "false": False}
            try:
                result = eval(content, {"__builtins__": {}}, context)
                return result
            except Exception:
                return content
        else:
            return self.tilde_content(items)


    def inline_assignment(self, items):
        """
        Transforms an inline assignment (e.g. x = 10) into a dictionary.
        Handles optional type annotations.
        """
        if len(items) == 2:
            key, value = items
        elif len(items) == 3:
            key, type_annotation, value = items
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
                array_values.append(item)
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
            # Evaluate the f-string using both global and local contexts.
            evaluated = evaluate_f_string(s.lstrip(), self.data, self.current_section)
            return evaluated
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
