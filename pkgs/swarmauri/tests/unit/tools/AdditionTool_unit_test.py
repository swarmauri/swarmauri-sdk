import pytest
from swarmauri.tools.concrete import AdditionTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    def test():
        tool = Tool()
        assert tool.resource == 'Tool'
    test()

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'AdditionTool'

@pytest.mark.unit
def test_initialization():
    def test():
        tool = Tool()
        assert type(tool.swm_path) == str
        assert type(tool.id) == str
    test()

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
@pytest.mark.parametrize(
    "input_a, input_b, expected_keys, expected_type, expected_sum",
    [
        (2, 3, {'sum'}, str, "5"),     # Test case 1: positive integers
        (-2, -3, {'sum'}, str, "-5"),  # Test case 2: negative integers
        (0, 0, {'sum'}, str, "0"),     # Test case 3: zero values
        (2.5, 3.5, {'sum'}, str, "6.0"), # Test case 4: floating-point numbers
    ]
)
def test_call(input_a, input_b, expected_keys, expected_type, expected_sum):
    tool = Tool()

    result = tool(input_a, input_b)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("sum"), expected_type), f"Expected {expected_type.__name__}, but got {type(result.get('sum')).__name__}"
    assert result.get("sum") == expected_sum, f"Expected sum {expected_sum}, but got {result.get('sum')}"
