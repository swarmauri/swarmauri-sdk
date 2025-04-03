import re

from ._precedence import __PRECEDENCE_SPECIFICATION__
# ---------------------------
# Master Tokenizer (Flat)
# ---------------------------
def tokenize(source):
    token_spec = __PRECEDENCE_SPECIFICATION__
    master_pattern = '|'.join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
    master_regex = re.compile(master_pattern, re.DOTALL)
    
    tokens = []
    for mo in master_regex.finditer(source):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'WHITESPACE':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character {value!r}')
        tokens.append((kind, value))
    return tokens

# ---------------------------
# Nested Tokenizer for Structures
# ---------------------------
def nested_tokenize(source):
    """
    First tokenizes the source with the flat lexer.
    Then, for tokens that represent nested structures (INLINE_TABLE, ARRAY, TABLE_ARRAY),
    it strips the outer delimiters and recursively tokenizes the inner content.
    Returns a list where such tokens become tuples:
    (TYPE, original_value, sub_tokens)
    """
    tokens = tokenize(source)
    new_tokens = []
    for token in tokens:
        typ, value = token[:2]
        if typ == 'INLINE_TABLE':
            inner = value.strip()[1:-1]
            sub_tokens = nested_tokenize(inner)
            new_tokens.append((typ, value, sub_tokens))
        elif typ == 'ARRAY':
            inner = value.strip()[1:-1]
            sub_tokens = nested_tokenize(inner)
            new_tokens.append((typ, value, sub_tokens))
        elif typ == 'TABLE_ARRAY':
            inner = value.strip()[2:-2]
            sub_tokens = nested_tokenize(inner)
            new_tokens.append((typ, value, sub_tokens))
        else:
            new_tokens.append(token)
    return new_tokens
