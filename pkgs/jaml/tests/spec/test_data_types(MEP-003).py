import pytest
from pprint import pprint

# Import the tokenization functions.
from jaml._tokenizer import tokenize, nested_tokenize

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until full data type parser is implemented")
def test_string_scalar():
    # Test a simple string literal.
    source = 'greeting = "Hello, World!"'
    tokens = tokenize(source)
    # Expect one STRING token with "Hello, World!" and IDENTIFIER "greeting"
    string_tokens = [t for t in tokens if t[0] == "STRING"]
    assert len(string_tokens) == 1
    assert "Hello, World!" in string_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until multiline string support is complete")
def test_multiline_string():
    # Test that newlines are preserved in a string.
    source = 'description = "Line one\nLine two\nLine three"'
    tokens = tokenize(source)
    string_tokens = [t for t in tokens if t[0] == "STRING"]
    assert len(string_tokens) == 1
    # Check that newlines are preserved.
    assert "\n" in string_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until integer parsing is complete")
def test_decimal_integer():
    source = 'answer = 42'
    tokens = tokenize(source)
    int_tokens = [t for t in tokens if t[0] == "INTEGER"]
    assert len(int_tokens) == 1
    assert "42" in int_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until octal integer parsing is complete")
def test_octal_integer():
    source = 'octal = 0o52'
    tokens = tokenize(source)
    int_tokens = [t for t in tokens if t[0] == "INTEGER"]
    assert len(int_tokens) == 1
    assert "0o52" in int_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until hexadecimal integer parsing is complete")
def test_hexadecimal_integer():
    source = 'hex = 0x2A'
    tokens = tokenize(source)
    int_tokens = [t for t in tokens if t[0] == "INTEGER"]
    assert len(int_tokens) == 1
    assert "0x2A" in int_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until binary integer parsing is complete")
def test_binary_integer():
    source = 'binary = 0b101010'
    tokens = tokenize(source)
    int_tokens = [t for t in tokens if t[0] == "INTEGER"]
    assert len(int_tokens) == 1
    assert "0b101010" in int_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until float parsing is complete")
def test_standard_float():
    source = 'pi = 3.14'
    tokens = tokenize(source)
    float_tokens = [t for t in tokens if t[0] == "FLOAT"]
    assert len(float_tokens) == 1
    assert "3.14" in float_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until special float values are parsed")
def test_special_float():
    source = 'infinity = inf\nnot_a_number = nan'
    tokens = tokenize(source)
    float_tokens = [t for t in tokens if t[0] == "FLOAT"]
    # Expect two float tokens: one for 'inf' and one for 'nan'
    assert len(float_tokens) == 2
    found_inf = any("inf" in token[1] for token in float_tokens)
    found_nan = any("nan" in token[1] for token in float_tokens)
    assert found_inf and found_nan

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until boolean parsing is complete")
def test_boolean_literal():
    source = 'active = true\nvalid = false'
    tokens = tokenize(source)
    bool_tokens = [t for t in tokens if t[0] == "BOOLEAN"]
    assert len(bool_tokens) == 2
    found_true = any("true" in token[1] for token in bool_tokens)
    found_false = any("false" in token[1] for token in bool_tokens)
    assert found_true and found_false

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until null parsing is complete")
def test_null_literal():
    source = 'missing = null'
    tokens = tokenize(source)
    null_tokens = [t for t in tokens if t[0] == "NULL"]
    assert len(null_tokens) == 1
    assert "null" in null_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until inline arrays are tokenized correctly")
def test_inline_array():
    source = 'numbers = [1, 2, 3, 4]'
    tokens = nested_tokenize(source)
    array_tokens = [t for t in tokens if t[0] == "ARRAY"]
    assert len(array_tokens) == 1
    # Check that nested tokens include integers and punctuation (commas)
    sub_tokens = array_tokens[0][2]
    int_tokens = [st for st in sub_tokens if st[0] == "INTEGER"]
    assert len(int_tokens) >= 1

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until multiline arrays are tokenized correctly")
def test_multiline_array():
    source = '''
    colors = [
      "red",    # Primary color
      "green",  # Secondary color
      "blue"    # Accent color
    ]
    '''
    tokens = nested_tokenize(source)
    array_tokens = [t for t in tokens if t[0] == "ARRAY"]
    assert len(array_tokens) == 1
    sub_tokens = array_tokens[0][2]
    # Expect that comments within the array are tokenized.
    comment_tokens = [st for st in sub_tokens if st[0] == "COMMENT"]
    assert len(comment_tokens) >= 1

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until inline tables are tokenized correctly")
def test_inline_table():
    source = 'point = { x = 10, y = 20 }'
    tokens = nested_tokenize(source)
    inline_table_tokens = [t for t in tokens if t[0] == "INLINE_TABLE"]
    assert len(inline_table_tokens) == 1
    # Check that nested tokens include identifiers and punctuation.
    sub_tokens = inline_table_tokens[0][2]
    id_tokens = [st for st in sub_tokens if st[0] == "IDENTIFIER"]
    assert len(id_tokens) >= 1

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until standard table sections are tokenized correctly")
def test_standard_table_section():
    source = "[section]\nkey = \"value\""
    tokens = tokenize(source)
    table_section_tokens = [t for t in tokens if t[0] == "TABLE_SECTION"]
    assert len(table_section_tokens) == 1
    assert "section" in table_section_tokens[0][1]

@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until table arrays are tokenized correctly")
def test_table_array_header():
    source = "[[products]]\nname = \"Widget\""
    tokens = tokenize(source)
    table_array_tokens = [t for t in tokens if t[0] == "TABLE_ARRAY"]
    assert len(table_array_tokens) == 1
    assert "products" in table_array_tokens[0][1]

# Optionally, you can include a test for nested inline tables.
@pytest.mark.spec
# @pytest.mark.xfail(reason="Expected failure until nested inline tables are tokenized correctly")
def test_nested_inline_table():
    source = 'user = { name = "Azzy", details = { age = 9, role = "admin" } }'
    tokens = nested_tokenize(source)
    inline_table_tokens = [t for t in tokens if t[0] == "INLINE_TABLE"]
    # Expect two inline tables: one outer, one nested for "details"
    assert len(inline_table_tokens) >= 2
    # Verify that the nested table (details) has been tokenized.
    nested_details = [t for t in inline_table_tokens if "admin" in t[1]]
    assert len(nested_details) == 1
