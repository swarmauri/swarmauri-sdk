import pytest
from lark import Token

# Import the tokenization functions.
from jaml import parser


# Test that keywords are recognized before identifiers.
@pytest.mark.spec
@pytest.mark.mep0002
@pytest.mark.xfail(reason="should fail due to syntax error")
def test_keyword_precedence():
    # "if" is a reserved keyword.
    tokens = parser.parse("if condition")
    # Expected: KEYWORD "if", IDENTIFIER "condition"
    token_types = [t[0] for t in tokens]
    token_values = [t[1] for t in tokens]
    assert token_types == ["KEYWORD", "IDENTIFIER"]
    assert token_values[0] == "if"
    assert token_values[1] == "condition"


# Test that a string containing a hash is parsed entirely as a STRING.
@pytest.mark.spec
@pytest.mark.mep0002
def test_string_with_hash():
    sample = 'test = "Hello, # world"'
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    assert len(tokens) == 5
    assert "Hello, # world" in tokens[4].value


# Test that a standalone comment is parsed as a COMMENT.
@pytest.mark.spec
@pytest.mark.mep0002
def test_standalone_comment():
    sample = "# This is a comment\n"
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    assert len(tokens) == 2
    assert tokens[0].startswith("#")
    assert tokens[0] == "# This is a comment"


# Test that an inline table is recognized as INLINE_TABLE and that its nested tokens include comments.
@pytest.mark.spec
@pytest.mark.mep0002
def test_inline_table_nesting():
    sample = 'test = { key0 = "value0", key1 = "value1"  # Inline table comment\n , key2 = "value2" }'
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")
    for tok in tokens:
        print(f"[DEBUG]: {tok}")

    assert len(tokens) == 29
    assert tokens[0] == "test"
    assert "# Inline table comment" in tokens[18].value


# Test that a multiline array with commas is parsed as an ARRAY (not as a table section).
@pytest.mark.spec
@pytest.mark.mep0002
def test_multiline_array_precedence():
    sample = """
    test = [
      "red",    # Primary color
      "green",  # Secondary color
      "blue"    # Accent color
    ]
    """
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    for tok in tokens:
        print(f"[DEBUG]: {tok}")

    assert len(tokens) == 16
    # assert tokens[3] == "STRING"
    assert tokens[2].type == "SETTER"
    assert tokens[2].value == "="


# Test that a table section header (which should be single-line) is recognized as TABLE_SECTION.
@pytest.mark.spec
@pytest.mark.mep0002
def test_table_section_precedence():
    sample = "[globals]"
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    assert len(tokens) == 3
    assert "globals" in tokens


# Test that a table array header is recognized as TABLE_ARRAY.
@pytest.mark.spec
@pytest.mark.mep0002
# @pytest.mark.xfail(reason="support for table arrays not fully supported.")
def test_table_array_precedence():
    sample = "[[products]]"
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    assert len(tokens) == 3
    assert "products" in tokens[1]


# Test that punctuation (like '=') is parsed as OPERATOR.
@pytest.mark.spec
@pytest.mark.mep0002
def test_operator_precedence():
    sample = "test = 42"
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    # Expected order: IDENTIFIER, OPERATOR, IDENTIFIER.
    token_types = [t.type for t in tokens]
    assert token_types == ["IDENTIFIER", "HSPACES", "SETTER", "HSPACES", "INTEGER"]


# Test that scoped variables take precedence (e.g. '${base}' is a SCOPED_VAR).
@pytest.mark.spec
@pytest.mark.mep0002
def test_scoped_variable_precedence():
    sample = "config = ${base}"
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    token_types = [t.type for t in tokens]
    token_values = [t.value for t in tokens]
    assert token_types == [
        "IDENTIFIER",
        "HSPACES",
        "SETTER",
        "HSPACES",
        "CONTEXT_SCOPED_VAR",
    ]
    assert token_values[4].startswith("${")


# Test that comments inside a line with code are recognized separately.
@pytest.mark.spec
@pytest.mark.mep0002
def test_inline_comment_precedence():
    sample = 'name = "Alice"  # User name'
    tree = parser.parse(sample)
    print(f"[DEBUG]: {tree}")
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    print(f"[DEBUG]: {tokens}")

    # Expect tokens: IDENTIFIER, PUNCTUATION, STRING, COMMENT.
    token_types = [t.type for t in tokens]
    assert "INLINE_COMMENT" in token_types
