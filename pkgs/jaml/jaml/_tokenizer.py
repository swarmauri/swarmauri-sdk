# _tokenizer.py

import re
from ._precedence import __PRECEDENCE_SPECIFICATION__

# ---------------------------
# Master Tokenizer (Flat)
# ---------------------------
def tokenize(source: str):
    """
    Tokenize the source code into a flat list of (token_type, token_value).
    Raises SyntaxError for unmatched brackets, missing closing quotes, 
    or other mismatch scenarios.
    """
    token_spec = __PRECEDENCE_SPECIFICATION__
    # Build the big master regex
    master_pattern = '|'.join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
    master_regex = re.compile(master_pattern, re.DOTALL)
    
    tokens = []
    for mo in master_regex.finditer(source):
        kind = mo.lastgroup
        value = mo.group()

        # ILLEGAL_ID check
        if kind == 'ILLEGAL_ID':
            raise SyntaxError("illegal identifier")

        if kind == 'INVALID_CHARACTER':
            raise SyntaxError("disallowed special character in identifier")

        if kind == "OPERATOR" and value == "|":
            raise SyntaxError("pipeline operator support is in discussion, but not planned.")

        if kind == "OPERATOR" and value == "<<":
            raise SyntaxError("merge operator not supported")

        # Skip whitespace
        if kind == 'WHITESPACE':
            continue

        # Mismatch handling
        elif kind == 'MISMATCH':
            # 1) Possibly unmatched bracket
            if value.startswith('['):
                raise SyntaxError("Unmatched bracket or unexpected EOF: missing ']' ?")
            # 2) Possibly missing closing quote
            if value.startswith('"') or value.startswith("'"):
                raise SyntaxError("missing closing quote or Syntax error in string literal")
            # 3) Fallback
            raise SyntaxError(f"Unexpected character {value!r}")

        tokens.append((kind, value))

    return tokens

# ---------------------------
# Nested Tokenizer for Structures
# ---------------------------
def nested_tokenize(source: str):
    """
    Tokenize the source using tokenize(source). Then, for tokens that represent
    nested structures (INLINE_TABLE, ARRAY, TABLE_ARRAY), remove the outer delimiters
    (e.g., '{' and '}') and recursively parse the inner content via nested_tokenize.
    
    Returns a list of tokens, where these nested structures become:
    (TYPE, original_value, [subtokens]).
    """
    tokens = tokenize(source)
    new_tokens = []
    for token in tokens:
        typ, value = token[:2]

        # If it's an INLINE_TABLE
        if typ == 'INLINE_TABLE':
            inner = value.strip()[1:-1]
            sub_tokens = nested_tokenize(inner)
            new_tokens.append((typ, value, sub_tokens))

        # If it's an ARRAY
        elif typ == 'ARRAY':
            # remove the [ ] from the ends
            inner = value.strip()[1:-1]
            sub_tokens = nested_tokenize(inner)
            new_tokens.append((typ, value, sub_tokens))

        # If it's a TABLE_ARRAY (i.e. [[ something ]])
        elif typ == 'TABLE_ARRAY':
            # remove the [[ ]] from the ends
            inner = value.strip()[2:-2]
            sub_tokens = nested_tokenize(inner)
            new_tokens.append((typ, value, sub_tokens))

        else:
            # For all other token types, keep as-is
            new_tokens.append(token)

    return new_tokens
