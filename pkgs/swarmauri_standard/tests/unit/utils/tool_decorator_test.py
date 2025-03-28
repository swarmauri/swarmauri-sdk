import pytest
from typing import List, Dict, Any
from swarmauri_standard.utils.tool_decorator import tool
from swarmauri_base.tools.ToolBase import ToolBase


@pytest.mark.unit
def test_tool_decorator_basic_functionality():
    """
    Test that the tool decorator correctly creates a ToolBase subclass from a decorated function.
    """

    # Define a simple function to decorate
    @tool
    def add_numbers(a: int, b: int = 0) -> int:
        """Add two numbers together and return the result."""
        return a + b

    # Verify the decorated function is now a ToolBase instance
    assert isinstance(add_numbers, ToolBase)

    # Verify the tool has the correct name and description
    assert add_numbers.name == "add_numbers"
    assert add_numbers.description == "Add two numbers together and return the result."
    assert add_numbers.version == "1.0.0"

    # Verify the parameters were correctly extracted
    assert len(add_numbers.parameters) == 2

    # Check first parameter (a)
    a_param = next((p for p in add_numbers.parameters if p.name == "a"), None)
    assert a_param is not None
    assert a_param.input_type == "int"
    assert a_param.required is True

    # Check second parameter (b)
    b_param = next((p for p in add_numbers.parameters if p.name == "b"), None)
    assert b_param is not None
    assert b_param.input_type == "int"
    assert b_param.required is False

    # Test calling the tool
    result = add_numbers(a=5, b=3)
    assert result == 8

    # Test calling with only required parameter
    result = add_numbers(a=10)
    assert result == 10
    assert add_numbers.type == "add_numbers"


@pytest.mark.unit
def test_tool_decorator_complex_types():
    """
    Test that the tool decorator handles more complex parameter types.
    """

    @tool
    def process_data(items: List[str], options: Dict[str, Any] = None) -> List[str]:
        """Process a list of items with optional configuration."""

        # Just return the items for this test
        return items

    # Verify parameters with complex types
    assert isinstance(process_data, ToolBase)
    assert len(process_data.parameters) == 2

    # Check list parameter
    items_param = next((p for p in process_data.parameters if p.name == "items"), None)
    assert items_param is not None
    assert items_param.input_type == "List"
    assert items_param.required is True

    # Check dict parameter
    options_param = next(
        (p for p in process_data.parameters if p.name == "options"), None
    )
    assert options_param is not None
    assert options_param.input_type == "Dict"
    assert options_param.required is False

    # Test calling the tool
    result = process_data(items=["a", "b", "c"])
    assert result == ["a", "b", "c"]


@pytest.mark.unit
def test_tool_decorator_no_docstring():
    """
    Test that the tool decorator works correctly with functions that have no docstring.
    """

    @tool
    def no_docs_function(x: str):
        return x.upper()

    assert isinstance(no_docs_function, ToolBase)
    assert no_docs_function.description == ""

    # Test calling the tool
    result = no_docs_function(x="hello")
    assert result == "HELLO"
