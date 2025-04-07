from importlib.resources import files, as_file
from lark import Lark
import json
from lark import Transformer, Token, v_args

class PreservedString(str):
    def __new__(cls, value, original):
        # Create a new string instance using the unquoted value.
        obj = super().__new__(cls, value)
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


class PreservedArray:
    """
    Stores both the parsed items (list-like) AND the original bracketed text,
    to allow data access *and* perfect round-trip.
    """
    def __init__(self, items, original_text):
        self.items = items
        self.original_text = original_text  # entire "[ ... ]" substring

    def __repr__(self):
        return f"PreservedArray(items={self.items}, text={self.original_text!r})"

    def __str__(self):
        # Return the bracketed text exactly as originally parsed.
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
            "__comments__": []   # <--- new list for standalone comments
        }
        self.current_section = self.data["__default__"]
        self.in_tilde = False

    def start(self, items):
        return self.data

    def assignment(self, items):
        inline = None
        if len(items) == 2:
            key, value = items
        elif len(items) == 3:
            # Check if the last item is an inline comment dictionary.
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

        # Only unquote if value is a plain string (not already preserved)
        if not isinstance(value, PreservedString) and isinstance(value, str) and (
            (value.startswith("'") and value.endswith("'")) or 
            (value.startswith('"') and value.endswith('"'))
        ):
            value = value[1:-1]

        if inline is not None:
            # If inline is a dictionary, extract the comment.
            if isinstance(inline, dict) and '_inline_comment' in inline:
                inline = inline['_inline_comment']
            inline = str(inline)
            self.current_section[key] = PreservedValue(value, inline)
        else:
            self.current_section[key] = value

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

    def tilde_block(self, items):
        was_in_tilde = self.in_tilde
        self.in_tilde = True
        if len(items) >= 3:
            content = items[1]
        else:
            content = self.tilde_content(items)
        self.in_tilde = was_in_tilde
        context = {"true": True, "false": False}
        try:
            return eval(content, {"__builtins__": {}}, context)
        except Exception:
            return content

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
    def array(self, items):
        """Store entire bracketed substring so we keep newlines, trailing commas, etc."""
        if items:
            # items[0] is array_content
            array_values = items[0] if items[0] else []
        else:
            array_values = []

        start = self.meta.start_pos
        end = self.meta.end_pos
        original_text = self._slice_input(start, end)
        return PreservedArray(array_values, original_text)

    def array_content(self, items):
        def is_ignorable(x):
            if hasattr(x, "data") and x.data == "ws":
                return True
            if isinstance(x, str) and x.strip() == "":
                return True
            if isinstance(x, Token) and x.type in ("WHITESPACE", "NEWLINE"):
                return True
            # Ignore standalone comment lines (they start with "#")
            if isinstance(x, str) and x.strip().startswith("#"):
                return True
            return False

        return [x for x in items if x != "," and not is_ignorable(x)]

    def array_item(self, items):
        if len(items) == 2:
            value, inline = items
            # If the inline comment is coming as a dict, extract the comment string.
            if isinstance(inline, dict) and '_inline_comment' in inline:
                inline = inline['_inline_comment']
            return PreservedValue(value, inline)
        elif len(items) == 1:
            return items[0]
        else:
            raise ValueError("Unexpected structure in array_item: " + str(items))


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
    # Terminal transformations for other token types
    # -----------------------------------------------------
    def STRING(self, token):
        s = token.value
        if self.in_tilde:
            return s
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
