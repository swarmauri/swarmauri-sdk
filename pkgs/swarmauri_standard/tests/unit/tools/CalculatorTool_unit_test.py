import pytest
from swarmauri_standard.tools.CalculatorTool import CalculatorTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "CalculatorTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation, num1, num2, expected_result, is_error",
    [
        ("add", 2, 3, "5", False),
        ("subtract", 5, 3, "2", False),
        ("multiply", 2, 3, "6", False),
        ("divide", 6, 3, "2.0", False),
        ("divide", 5, 0, "Error: Division by zero.", True),
        ("unknown_ops", 5, 0, "Error: Unknown operation.", True),
    ],
)
def test_call(operation, num1, num2, expected_result, is_error):
    tool = Tool()
    result = tool(operation, num1, num2)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"

    if is_error:
        assert "error" in result
        assert result["error"] == expected_result
    else:
        assert "operation" in result
        assert "calculated_result" in result
        assert result["operation"] == operation
        assert result["calculated_result"] == expected_result
