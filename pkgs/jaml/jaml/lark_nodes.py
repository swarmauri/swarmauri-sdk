from importlib.resources import files, as_file
from lark import Lark
import json
from lark import Transformer

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

    def assignment(self, items):
        """
        items typically:
          [key, (possibly type_annotation?), '=', value, (inline_comment?)]
        """
        # First let's parse out the parts we care about:
        key = items[0]

        # If we had an optional type_annotation in the grammar, handle or skip it
        # but for brevity let's assume we ignore it or you handle it your usual way
        #
        # items might have '=' as a separate token, so watch out for that indexing.
        # Or you can strip out punctuation in a separate rule. Example code:
        idx_val = 2
        if len(items) >= 2 and isinstance(items[1], str) and items[1].startswith(":"): 
            # that was the type annotation, or you'd check the rule
            # skip it for brevity
            idx_val = 4  # adjust if your grammar includes punctuation tokens

        value = items[idx_val]
        
        # Now check if there's an inline comment
        inline_cmt = None
        if len(items) > idx_val + 1:
            # The last item might be an inline_comment node
            last_item = items[idx_val + 1]
            # If the grammar structure is inline_comment -> (WS_INLINE?, COMMENT),
            # then 'last_item' might be a list. We'll try to parse it out:
            if isinstance(last_item, list) and len(last_item) > 0:
                # The actual COMMENT token might be last_item[-1]
                maybe_cmt = last_item[-1]
                if isinstance(maybe_cmt, str) and maybe_cmt.startswith("#"):
                    inline_cmt = maybe_cmt
            elif isinstance(last_item, str) and last_item.startswith("#"):
                # If the inline_comment rule returns just the comment string
                inline_cmt = last_item

        # We store everything in the current section. 
        # Instead of storing a raw value, store an object or tuple that includes the comment.
        # For a quick hack, store a dict with "value" and "comment":
        if inline_cmt:
            self.current_section[key] = {
                "_value": value,
                "_inline_comment": inline_cmt,
            }
        else:
            self.current_section[key] = value

        return {key: value}


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
        # Filter out ',' tokens so we get only the array values
        return [x for x in items if x != ","]

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
        if s.startswith("'''") or s.startswith('"""') or s.startswith("```"):
            return s[3:-3]
        if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"', "`"}:
            return s[1:-1]
        return s

    def SCOPED_VAR(self, token):
        return token.value

    def COMMENT(self, token):
        """
        Whenever we see a standalone comment, push it into our __comments__ list.
        """
        comment_line = token.value  # e.g. "# This is a standalone comment"
        self.data["__comments__"].append(comment_line)
        return comment_line

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
