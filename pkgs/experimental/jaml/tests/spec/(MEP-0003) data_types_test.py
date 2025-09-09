import pytest
from lark import Token

# Import the tokenization functions.
from jaml import parser


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until full data type parser is implemented")
def test_string_scalar():
    # Test a simple string literal.
    source = 'greeting = "Hello, World!"'
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    # Expect one STRING token with "Hello, World!" and IDENTIFIER "greeting"
    string_tokens = [t for t in tokens if t.type == "SINGLE_QUOTED_STRING"]
    assert len(string_tokens) == 1
    assert "Hello, World!" in string_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until multiline string support is complete")
def test_multiline_string():
    # Test that newlines are preserved in a string.
    source = 'description = "Line one\nLine two\nLine three"'
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    string_tokens = [t for t in tokens if t.type == "SINGLE_QUOTED_STRING"]
    assert len(string_tokens) == 1
    # Check that newlines are preserved.
    assert "\n" in string_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until integer parsing is complete")
def test_decimal_integer():
    source = "answer = 42"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    int_tokens = [t for t in tokens if t.type == "INTEGER"]
    assert len(int_tokens) == 1
    assert "42" in int_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until octal integer parsing is complete")
def test_octal_integer():
    source = "octal = 0o52"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    int_tokens = [t for t in tokens if t.type == "INTEGER"]
    assert len(int_tokens) == 1
    assert "0o52" in int_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until hexadecimal integer parsing is complete")
def test_hexadecimal_integer():
    source = "hex = 0x2A"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    int_tokens = [t for t in tokens if t.type == "INTEGER"]
    assert len(int_tokens) == 1
    assert "0x2A" in int_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until binary integer parsing is complete")
def test_binary_integer():
    source = "binary = 0b101010"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    int_tokens = [t for t in tokens if t.type == "INTEGER"]
    assert len(int_tokens) == 1
    assert "0b101010" in int_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until float parsing is complete")
def test_standard_float():
    source = "pi = 3.14"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    float_tokens = [t for t in tokens if t.type == "FLOAT"]
    assert len(float_tokens) == 1
    assert "3.14" in float_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until special float values are parsed")
def test_special_float():
    source = "infinity = inf\nnot_a_number = nan"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    float_tokens = [t for t in tokens if t.type == "FLOAT"]

    # Expect two float tokens: one for 'inf' and one for 'nan'
    assert len(float_tokens) == 2
    found_inf = any("inf" in token.value for token in float_tokens)
    found_nan = any("nan" in token.value for token in float_tokens)
    assert found_inf and found_nan


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until boolean parsing is complete")
def test_boolean_literal():
    source = "active = true\nvalid = false"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    bool_tokens = [t for t in tokens if t.type == "BOOLEAN"]

    assert len(bool_tokens) == 2
    found_true = any("true" in token.value for token in bool_tokens)
    found_false = any("false" in token.value for token in bool_tokens)
    assert found_true and found_false


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until null parsing is complete")
def test_null_literal():
    source = "missing = null"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    null_tokens = [t for t in tokens if t.type == "NULL"]

    assert len(null_tokens) == 1
    assert "null" in null_tokens[0].value


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Not fully implemented.")
def test_inline_array():
    source = "numbers = [1, 2, 3, 4]"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    array_tokens = [t for t in tokens]
    print(f"[DEBUG]: {array_tokens}")
    assert len(array_tokens) == 8


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until multiline arrays are parser.parsed correctly")
def test_multiline_array():
    source = """
    colors = [
      "red",    # Primary color
      "green",  # Secondary color
      "blue"    # Accent color
    ]
    """
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    assert len([t for t in tokens]) == 16


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until inline tables are parser.parsed correctly")
def test_inline_table():
    # source = 'point = { x = 10, y = 20 }'
    source = "point = { x = 10, y = 20 }"
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    assert len([t for t in tokens]) == 20


@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until standard table sections are parser.parsed correctly")
def test_standard_table_section():
    source = '[section]\nkey = "value"'
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    assert len([t for t in tokens]) == 8


@pytest.mark.spec
@pytest.mark.mep0003
@pytest.mark.xfail(reason="Table arrays are not fully supported.")
def test_table_array_header():
    source = '[[products]]\nname = "Widget"'
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    assert len([t for t in tokens]) == 1


# Optionally, you can include a test for nested inline tables.
@pytest.mark.spec
@pytest.mark.mep0003
# @pytest.mark.xfail(reason="Expected failure until nested inline tables are parser.parsed correctly")
def test_nested_inline_table():
    source = 'user = { name = "Azzy", details = { age = 9, role = "admin" } }'
    tree = parser.parse(source)
    tokens = [t for t in tree.scan_values(lambda v: isinstance(v, Token))]
    assert len([t for t in tokens]) == 35
