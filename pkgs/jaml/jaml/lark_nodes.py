from importlib.resources import files, as_file
from lark import Lark
import json
from lark import Transformer

class PreservedArray:
    def __init__(self, items, original_text):
        self.items = items            # Parsed list of items
        self.original_text = original_text  # Entire "[ ... ]" substring (including commas, newlines, etc.)

    def __repr__(self):
        return f"PreservedArray(items={self.items}, text={self.original_text!r})"

    def __str__(self):
        # Return the bracketed text exactly as originally parsed (including trailing commas).
        return self.original_text

class PreservedInlineTable(dict):
    """
    Subclass dict so that tests expecting a plain dict will pass.
    We keep the original text for round-trip or debugging needs.
    """
    def __init__(self, data, original_text):
        super().__init__(data)  # Initialize 'dict' with the parsed key-value pairs
        self.original_text = original_text

    def __repr__(self):
        return f"PreservedInlineTable(data={dict(self)}, text={self.original_text!r})"

    def __str__(self):
        # Return the brace-delimited text exactly as originally parsed.
        return self.original_text



class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        # Initialize with a default section.
        self.data = {"__default__": {}}
        # Current section pointer (starts at default).
        self.current_section = self.data["__default__"]
        self.in_tilde = False  # Flag to track if we're inside a tilde block
        # We'll assign self._context or self.input_text externally
        # so _slice_input can find the entire input text.

    def start(self, items):
        # Return the complete configuration dictionary.
        return self.data

    def section(self, items):
        """
        Processes a section header. If the header is produced by the section_name rule
        (i.e. unquoted) then it will be a list of identifiers and we merge them into a nested
        namespace. Otherwise, if it’s a quoted string, use it literally.
        """
        raw_section = items[0]
        if isinstance(raw_section, list):
            # Unquoted section header: merge namespace.
            parts = raw_section
            d = self.data
            for part in parts:
                if part not in d:
                    d[part] = {}
                d = d[part]
            self.current_section = d
            return d
        else:
            # Quoted section header: use the literal string.
            key = raw_section
            if key not in self.data:
                self.data[key] = {}
            self.current_section = self.data[key]
            return self.data[key]

    def assignment(self, items):
        # items[0] is the key, items[1] is the value.
        key = items[0]
        value = items[1]
        self.current_section[key] = value
        return {key: value}

    def section_name(self, items):
        """
        section_name: IDENTIFIER ("." IDENTIFIER)*
        Returns a list of strings, e.g. ["app", "settings"].
        """
        return items

    def type_annotation(self, items):
        # type_annotation: TYPE
        return items[0]

    # ---------------------
    # Value and leaf rules
    # ---------------------

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
        """
        Expects a tilde block defined as: TILDE_START tilde_content TILDE_END.
        Uses the middle element as the content to evaluate.
        """
        was_in_tilde = self.in_tilde
        self.in_tilde = True
        if len(items) >= 3:
            content = items[1]
        else:
            content = self.tilde_content(items)
        self.in_tilde = was_in_tilde
        context = {"true": True, "false": False}
        try:
            result = eval(content, {"__builtins__": {}}, context)
            return result
        except Exception:
            return content

    # ----------------------
    # Preserved Array logic
    # ----------------------
    def array(self, items):
        """
        With propagate_positions=True, self.meta.start_pos and self.meta.end_pos
        should be valid. We'll slice the original input so we preserve newlines, indentation, etc.
        """
        array_values = []
        if items:
            # items[0] is array_content, which we can flatten or parse
            array_values = items[0] if items[0] else []

        # Retrieve the original "[ ... ]" text (including trailing comma, newlines, etc.)
        start = self.meta.start_pos
        end = self.meta.end_pos
        original_text = self._slice_input(start, end)

        # Return a PreservedArray that keeps both the parsed items and the original text.
        return PreservedArray(array_values, original_text)

    def array_content(self, items):
        """
        array_content: array_value ("," array_value)* ("," ws?)?
        'items' is a list of array_value plus commas in between.
        Filter out commas and return the actual values. 
        (We still keep them in the original_text, so we lose no formatting.)
        """
        values = [i for i in items if i != ","]
        return values

    def array_value(self, items):
        # 'items' is typically a list with one sub-value
        return items[0]

    # -----------------------------
    # Preserved Inline Table logic
    # -----------------------------
    def INLINE_TABLE(self, token):
        """
        Capture the entire "{ ... }" substring, plus parse basic key=value pairs
        into a dict (if you need programmatic access).
        """
        if hasattr(token, 'meta') and token.meta:
            start = token.meta.start_pos
            end = token.meta.end_pos
            original_text = self._slice_input(start, end)
        else:
            original_text = token.value

        # We'll still parse the content so we can store it in .data,
        # but preserve the entire text for round-trip.
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
                        # If in quotes, remove them
                        if (
                            (val.startswith('"') and val.endswith('"'))
                            or (val.startswith("'") and val.endswith("'"))
                        ):
                            converted = val[1:-1]
                        else:
                            converted = val
                    result_dict[key] = converted

        return PreservedInlineTable(result_dict, original_text)

    def ARRAY(self, token):
        """
        A fallback if the grammar still defines ARRAY as a token (like /\[\s*.*?\s*\]/s).
        Storing as a PreservedArray for consistency, if parseable by json.
        """
        s = token.value.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                original_text = token.value
                return PreservedArray(parsed, original_text)
            return parsed
        except Exception:
            return s

    # -----------------------------------------------------
    # Terminal transformations for other token types
    # -----------------------------------------------------
    def STRING(self, token):
        s = token.value
        if getattr(self, "in_tilde", False):
            # In tilde blocks, keep the original quoted string.
            return s
        # Outside tilde blocks, unquote the string.
        if s.startswith("'''") or s.startswith('"""') or s.startswith("```"):
            return s[3:-3]
        if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"', "`"}:
            return s[1:-1]
        return s

    def SCOPED_VAR(self, token):
        return token.value

    def COMMENT(self, token):
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
        Retrieve the exact substring from the original input text
        using self._context.text.
        Make sure that you set `self._context = parser` or store
        the entire text on this transformer before calling transform().
        """
        return self._context.text[start:end]
