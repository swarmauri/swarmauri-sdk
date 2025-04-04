import pytest

# Assume we have some hypothetical 'loads' function that parses
# the TOML/markup source and returns a data structure with inferred types.
# For demonstration, we'll assume loads is available in the current namespace.
# In reality, you'd import your parser, tokenizer, or inference engine here.
from jaml import loads

@pytest.mark.spec
# @pytest.mark.xfail(reason="Inference for basic scalar types is not yet implemented")
def test_infer_basic_scalars():
    """
    Tests basic scalar inference for integer, float, boolean, null, and string.
    """
    source = '''
    [scalars]
    int_value = 42
    float_value = 3.14
    bool_value = true
    none_value = null
    string_value = "Hello"
    '''
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
@pytest.mark.xfail(reason="Inference for numeric prefixes and special float values not yet implemented")
def test_infer_numeric_prefixes_and_specials():
    """
    Tests inference for octal, hexadecimal, binary integers, and special float values (inf, nan).
    """
    source = '''
    [numbers]
    octal_val = 0o52
    hex_val = 0x2A
    bin_val = 0b101010
    infinity = inf
    not_number = nan
    '''
    result = loads(source)

    numbers = result["numbers"]
    assert numbers["octal_val"] == 42  # 0o52 -> 42
    assert numbers["hex_val"] == 42    # 0x2A -> 42
    assert numbers["bin_val"] == 42    # 0b101010 -> 42
    # Typically, 'inf' and 'nan' are floats in Pythonic representation
    assert numbers["infinity"] == float("inf")
    assert isinstance(numbers["not_number"], float)

@pytest.mark.spec
@pytest.mark.xfail(reason="Inference in expressions not fully implemented")
def test_infer_expressions():
    """
    Ensures expressions (wrapped with ~()) are type-inferred from their result.
    """
    source = '''
    [exprs]
    # Arithmetic expression
    sum_val = ~(10 + 5)
    # String concatenation
    greeting = ~( "Hello, " + "World!" )
    # Boolean logic
    combo = ~( true and false )
    '''
    result = loads(source)
    exprs = result["exprs"]
    assert isinstance(exprs["sum_val"], int)
    assert exprs["sum_val"] == 15
    assert isinstance(exprs["greeting"], str)
    assert exprs["greeting"] == "Hello, World!"
    assert isinstance(exprs["combo"], bool)
    assert exprs["combo"] is False

@pytest.mark.spec
@pytest.mark.xfail(reason="Inference for lists, including multiline arrays, not fully implemented")
def test_infer_lists():
    """
    Tests that lists/arrays are correctly inferred as list types.
    """
    source = '''
    [arrays]
    inline_list = [1, 2, 3]
    multiline_list = [
      "red",
      "green",
      "blue"
    ]
    '''
    result = loads(source)
    arrays = result["arrays"]
    assert isinstance(arrays["inline_list"], list)
    assert arrays["inline_list"] == [1, 2, 3]
    assert isinstance(arrays["multiline_list"], list)
    assert arrays["multiline_list"] == ["red", "green", "blue"]

@pytest.mark.spec
@pytest.mark.xfail(reason="Inference for inline tables not fully implemented")
def test_infer_inline_tables():
    """
    Verifies that inline tables (dict-like structures) are inferred as 'table' objects.
    """
    source = '''
    [inline]
    point = { x = 10, y = 20 }
    '''
    result = loads(source)
    inline = result["inline"]
    assert isinstance(inline["point"], dict)
    assert inline["point"]["x"] == 10
    assert inline["point"]["y"] == 20

@pytest.mark.spec
@pytest.mark.xfail(reason="Inference with explicit override not fully enforced")
def test_explicit_type_override():
    """
    Checks that an explicit annotation override changes the final type.
    """
    source = '''
    [overrides]
    count: float = 3
    flag: str = true
    '''
    result = loads(source)
    overrides = result["overrides"]
    # Even though '3' is typically an int, it's annotated as float
    assert isinstance(overrides["count"], float)
    # 'true' is typically a bool, but annotated as str
    assert isinstance(overrides["flag"], str)
    # Check that the stored value might be "true" as a string
    assert overrides["flag"] == "true"

@pytest.mark.spec
@pytest.mark.xfail(reason="Error handling for conflicting types not fully implemented")
def test_conflicting_types():
    """
    Ensures an error is raised when an explicit annotation conflicts with the inferred type.
    """
    source = '''
    [conflict]
    num: str = 42
    '''
    # Expect a type conflict error or similar
    with pytest.raises(TypeError):
        loads(source)

@pytest.mark.spec
@pytest.mark.xfail(reason="Heterogeneous lists might require special behavior or error reporting")
def test_heterogeneous_list_inference():
    """
    MEP-004 open issue: lists with mixed types. Should it be a generic list or raise warning/error?
    """
    source = 'mixed = ["a", 1, true]'
    # Depending on how your spec decides, either this is valid (generic list)
    # or yields a type conflict. We assume a mild error or warning for demonstration.
    with pytest.raises(TypeError):
        loads(source)
