from lark import Lark, Transformer
import json

class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        # Top-level dictionary holding all sections
        self.config = {}
        # Keep track of the current nested dict
        self.current_section_ref = self.config
    
    def start(self, items):
        # The final transformation result is in self.config
        return self.config

    def section(self, items):
        """
        Matches [ section_name ]
        Items will be a single element (list of identifiers).
        E.g. section_name might be ["config"] or ["config", "subsection"].
        """
        section_parts = items[0]
        
        # Descend into nested dict structure
        ref = self.config
        for part in section_parts:
            if part not in ref:
                ref[part] = {}
            ref = ref[part]
        
        # Update current section reference
        self.current_section_ref = ref
        return ref

    def section_name(self, items):
        """
        section_name: IDENTIFIER ("." IDENTIFIER)*
        This rule returns a list of strings, e.g. ["config", "nested"].
        """
        # 'items' will be something like ["config", "nested"] if we see [config.nested]
        return items

    def assignment(self, items):
        """
        assignment: IDENTIFIER (":" type_annotation)? "=" value
        Depending on how Lark groups them, items could be:
           [identifier, type_annotation, value]   # if the type_annotation is present
        or
           [identifier, value]                    # if there's no type_annotation
        """
        if len(items) == 3:
            identifier, type_annot, val = items
            self.current_section_ref[identifier] = {
                "type": type_annot,
                "value": val
            }
        else:
            identifier, val = items
            self.current_section_ref[identifier] = val
        return None
    
    def type_annotation(self, items):
        """
        type_annotation: TYPE
        Usually just a single token (str, int, etc.)
        """
        return items[0]
    
    # ---------------------
    # Value and leaf rules
    # ---------------------

    def paren_expr(self, items):
        # Convert all items to str before joining
        return "(" + " ".join(str(x) for x in items) + ")"


    def tilde_content(self, items):
        # Recursively convert everything to a string
        def to_string(x):
            if isinstance(x, list):
                return "".join(to_string(subx) for subx in x)
            elif hasattr(x, '__iter__') and not isinstance(x, str):
                # In rare cases, if you return nested structures, flatten them
                return "".join(to_string(subx) for subx in x)
            else:
                return str(x)
        
        return to_string(items)

    # Treat all these terminal types as strings or raw values
    def STRING(self, token):
        return token.value

    def SCOPED_VAR(self, token):
        return token.value
    
    def COMMENT(self, token):
        return token.value

    def FLOAT(self, token):
        return float(token.value)

    def INTEGER(self, token):
        # Could parse int(...) but watch for hex, oct, etc.
        # For simplicity, store as string or do int(token, 0)
        # (which parses 0x..., 0o..., etc.)
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
        return token.value

    def ARRAY(self, token):
        return token.value

    def IDENTIFIER(self, token):
        return token.value

    def OPERATOR(self, token):
        return token.value

    def PUNCTUATION(self, token):
        return token.value

    def WHITESPACE(self, token):
        return token.value