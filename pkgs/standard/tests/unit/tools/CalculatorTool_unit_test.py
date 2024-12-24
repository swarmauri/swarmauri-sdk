import pytest
from swarmauri.tools.concrete import CalculatorTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'CalculatorTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.swm_path) == str
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation, num1, num2, expected_result",
    [
        ('add', 2, 3, '5'),  # Addition
        ('subtract', 5, 3, '2'),  # Subtraction
        ('multiply', 2, 3, '6'),  # Multiplication
        ('divide', 6, 3, '2.0'),  # Division
        ('divide', 5, 0, 'Error: Division by zero.'),  # Division by zero, adjust based on your expected behavior
        ('unknown_ops', 5, 0, 'Error: Unknown operation.')
    ]
)
def test_call(operation, num1, num2, expected_result):
    tool = Tool()

    expected_keys = {"operation", "calculated_result"}
    result = tool(operation, num1, num2)

    if isinstance(result, str):
        assert result == expected_result

    else:
        assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
        assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
        assert isinstance(result.get("calculated_result"),
                      str), f"Expected str, but got {type(result.get('calculated_result')).__name__}"

        assert result.get(
            "calculated_result") == expected_result, f"Expected Calculated result {expected_result}, but got {result.get('calculated_result')}"
