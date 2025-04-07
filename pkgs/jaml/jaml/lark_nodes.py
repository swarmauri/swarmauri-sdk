import json
from lark import Transformer

class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        # Initialize with a default section.
        self.data = {"__default__": {}}
        # Current section pointer (starts at default).
        self.current_section = self.data["__default__"]
        self.in_tilde = False  # Flag to track if we're inside a tilde block

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

    # Terminal transformations.
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
        return int(token.value, 0) if token.value not in ("inf", "nan", "+inf", "-inf") else token.value

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

    def INLINE_TABLE(self, token):
        s = token.value.strip()
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1].strip()
        result = {}
        if not s:
            return result
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
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        converted = val[1:-1]
                    else:
                        converted = val
                result[key] = converted
        return result

    def ARRAY(self, token):
        s = token.value.strip()
        try:
            result = json.loads(s)
            if isinstance(result, list):
                return result
            return result
        except Exception:
            return s

    def IDENTIFIER(self, token):
        return token.value

    def OPERATOR(self, token):
        return token.value

    def PUNCTUATION(self, token):
        return token.value

    def WHITESPACE(self, token):
        return token.value
