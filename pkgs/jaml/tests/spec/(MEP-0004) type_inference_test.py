import pytest

# Assume we have some hypothetical 'loads' function that parses
# the TOML/markup source and returns a data structure with inferred types.
# For demonstration, we'll assume loads is available in the current namespace.
# In reality, you'd import your parser, tokenizer, or inference engine here.
from jaml import loads


@pytest.mark.spec
@pytest.mark.mep0004
# @pytest.mark.xfail(reason="Inference for basic scalar types is not yet implemented")
def test_infer_basic_scalars():
    """
    Tests basic scalar inference for integer, float, boolean, null, and string.
    """
    source = """
    [scalars]
    int_value = 42
    float_value = 3.14
    bool_value = true
    none_value = null
    string_value = "Hello"
    """
    result = loads(source)  # hypothetical function

    # The result is presumably a dict-like structure with typed values.
    scalars = result["scalars"]
    # Check the inferred types (or however your system stores them).
    assert isinstance(scalars["int_value"], int)
    assert isinstance(scalars["float_value"], float)
    assert isinstance(scalars["bool_value"], bool)
    assert scalars["none_value"] is None
    assert isinstance(scalars["string_value"], str)


@pytest.mark.spec
@pytest.mark.mep0004
# @pytest.mark.xfail(reason="Inference for numeric prefixes and special float values not yet implemented")
def test_infer_numeric_prefixes_and_specials():
    """
    Tests inference for octal, hexadecimal, binary integers, and special float values (inf, nan).
    """
    source = """
    [numbers]
    octal_val = 0o52
    hex_val = 0x2A
    bin_val = 0b101010
    infinity = inf
    not_number = nan
    """
    result = loads(source)

    numbers = result["numbers"]
    assert numbers["octal_val"] == 42  # 0o52 -> 42
    assert numbers["hex_val"] == 42  # 0x2A -> 42
    assert numbers["bin_val"] == 42  # 0b101010 -> 42
    # Typically, 'inf' and 'nan' are floats in Pythonic representation
    assert numbers["infinity"] == float("inf")
    assert isinstance(numbers["not_number"], float)


@pytest.mark.spec
@pytest.mark.mep0004
# @pytest.mark.xfail(reason="Inference for lists, including multiline arrays, not fully implemented")
def test_infer_lists():
    """
    Tests that lists/arrays are correctly inferred as list types.
    """
    source = """
    [arrays]
    inline_list = [1, 2, 3]
    multiline_list = [
      "red",
      "green",
      "blue",
      f"purple",
    ]
    """
    result = loads(source)
    arrays = result["arrays"]
    assert isinstance(arrays["inline_list"], list)
    assert arrays["inline_list"] == [1, 2, 3]
    assert isinstance(arrays["multiline_list"], list)
    assert arrays["multiline_list"] == ["red", "green", "blue", "purple"]


@pytest.mark.spec
@pytest.mark.mep0004
# @pytest.mark.xfail(reason="Inference for inline tables not fully implemented")
def test_infer_inline_tables():
    """
    Verifies that inline tables (dict-like structures) are inferred as 'table' objects.
    """
    source = """
    [inline]
    point = { x = 10, y = 20 }
    """
    result = loads(source)
    inline = result["inline"]
    assert isinstance(inline["point"], dict)
    assert inline["point"]["x"] == 10
    assert inline["point"]["y"] == 20


@pytest.mark.spec
@pytest.mark.mep0004
# @pytest.mark.xfail(reason="Heterogeneous lists might require special behavior or error reporting")
def test_heterogeneous_list_inference():
    """
    MEP-004 open issue: lists with mixed types. Should it be a generic list or raise warning/error?
    """
    source = 'mixed = ["a", 1, true]'
    loads(source)
