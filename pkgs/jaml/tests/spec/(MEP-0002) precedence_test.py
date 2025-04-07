import pytest
from pprint import pprint

# Import the tokenization functions.
from jaml._tokenizer import tokenize, nested_tokenize

# Test that keywords are recognized before identifiers.
@pytest.mark.spec
@pytest.mark.mep0002
def test_keyword_precedence():
    # "if" is a reserved keyword.
    tokens = tokenize("if condition")
    # Expected: KEYWORD "if", IDENTIFIER "condition"
    token_types = [t[0] for t in tokens]
    token_values = [t[1] for t in tokens]
    assert token_types == ["KEYWORD", "IDENTIFIER"]
    assert token_values[0] == "if"
    assert token_values[1] == "condition"

# Test that a string containing a hash is tokenized entirely as a STRING.
@pytest.mark.spec
@pytest.mark.mep0002
def test_string_with_hash():
    tokens = tokenize('"Hello, # world"')
    # Should be one STRING token; the inner '#' is part of the string.
    assert len(tokens) == 1
    assert tokens[0][0] == "STRING"
    assert "# world" in tokens[0][1]

# Test that a standalone comment is tokenized as a COMMENT.
@pytest.mark.spec
@pytest.mark.mep0002
def test_standalone_comment():
    tokens = tokenize("# This is a comment\n")
    assert len(tokens) == 1
    assert tokens[0][0] == "COMMENT"
    assert tokens[0][1].startswith("#")

# Test that an inline table is recognized as INLINE_TABLE and that its nested tokens include comments.
@pytest.mark.spec
@pytest.mark.mep0002
def test_inline_table_nesting():
    sample = '{ key1 = "value1"  # Inline table comment\n , key2 = "value2" }'
    tokens = nested_tokenize(sample)
    # Expect one INLINE_TABLE token with nested tokens.
    assert len(tokens) == 1
    typ, original, sub_tokens = tokens[0]
    assert typ == "INLINE_TABLE"
    # Check that one of the sub-tokens is a COMMENT.
    comment_tokens = [t for t in sub_tokens if t[0] == "COMMENT"]
    assert len(comment_tokens) >= 1

# Test that a multiline array with commas is tokenized as an ARRAY (not as a table section).
@pytest.mark.spec
@pytest.mark.mep0002
def test_multiline_array_precedence():
    sample = '''
    [
      "red",    # Primary color
      "green",  # Secondary color
      "blue"    # Accent color
    ]
    '''
    tokens = nested_tokenize(sample)
    # Expect the bracketed construct to be an ARRAY.
    array_tokens = [t for t in tokens if t[0] == "ARRAY"]
    assert len(array_tokens) == 1
    # Check nested tokens for comments.
    sub_tokens = array_tokens[0][2]
    comment_tokens = [st for st in sub_tokens if st[0] == "COMMENT"]
    assert len(comment_tokens) >= 1

# Test that a table section header (which should be single-line) is recognized as TABLE_SECTION.
@pytest.mark.spec
@pytest.mark.mep0002
def test_table_section_precedence():
    tokens = tokenize("[globals]")
    assert len(tokens) == 1
    assert tokens[0][0] == "TABLE_SECTION"
    assert "globals" in tokens[0][1]

# Test that a table array header is recognized as TABLE_ARRAY.
@pytest.mark.spec
@pytest.mark.mep0002
def test_table_array_precedence():
    tokens = tokenize("[[products]]")
    assert len(tokens) == 1
    assert tokens[0][0] == "TABLE_ARRAY"
    assert "products" in tokens[0][1]

# Test that punctuation (like '=') is tokenized as OPERATOR.
@pytest.mark.spec
@pytest.mark.mep0002
def test_operator_precedence():
    tokens = tokenize("a = b")
    # Expected order: IDENTIFIER, OPERATOR, IDENTIFIER.
    token_types = [t[0] for t in tokens]
    token_values = [t[1] for t in tokens]
    assert token_types == ["IDENTIFIER", "OPERATOR", "IDENTIFIER"]
    assert token_values[1] == "="

# Test that scoped variables take precedence (e.g. '${base}' is a SCOPED_VAR).
@pytest.mark.spec
@pytest.mark.mep0002
def test_scoped_variable_precedence():
    tokens = tokenize("config = ${base}")
    # Expect: IDENTIFIER 'config', OPERATOR '=', SCOPED_VAR '${base}'
    token_types = [t[0] for t in tokens]
    token_values = [t[1] for t in tokens]
    assert token_types == ["IDENTIFIER", "OPERATOR", "SCOPED_VAR"]
    assert token_values[2].startswith("${")

# Test that comments inside a line with code are recognized separately.
@pytest.mark.spec
@pytest.mark.mep0002
def test_inline_comment_precedence():
    sample = 'name = "Alice"  # User name'
    tokens = tokenize(sample)
    # Expect tokens: IDENTIFIER, PUNCTUATION, STRING, COMMENT.
    token_types = [t[0] for t in tokens]
    assert "COMMENT" in token_types

