import pytest
from typing import Dict, List, Any, Union, Annotated

from swarmauri_standard.utils.tool_decorator import tool
from swarmauri_base.tools.ToolBase import ToolBase


@pytest.mark.unit
def test_tool_decorator_various_simple_types():
    """Create tools with simple parameter types and varying arity."""

    @tool
    def single(a: int) -> int:
        return a

    @tool
    def double(a: int, b: float) -> float:
        return a + b

    assert isinstance(single, ToolBase)
    assert isinstance(double, ToolBase)

    assert len(single.parameters) == 1
    assert single.parameters[0].input_type == "int"

    assert len(double.parameters) == 2
    assert double.parameters[0].input_type == "int"
    assert double.parameters[1].input_type == "float"

    assert single(a=5) == 5
    assert double(a=3, b=2.5) == pytest.approx(5.5)


@pytest.mark.unit
def test_tool_decorator_complex_nested_types():
    """Handle several complex typing constructs within a single tool."""

    @tool
    def complex_fn(
        a_dict: dict,
        mapping: Dict[str, str],
        union_map: Dict[str, Union[int, float, dict, str]],
        items: list,
        list_of_maps: List[Dict[str, Any]],
        annotated_value: Annotated[str, "meta"] = "foo",
    ) -> str:
        return annotated_value

    assert isinstance(complex_fn, ToolBase)
    assert len(complex_fn.parameters) == 6

    type_map = {p.name: p.input_type for p in complex_fn.parameters}

    assert type_map["a_dict"] == "dict"
    assert type_map["mapping"] == "Dict"
    assert type_map["union_map"] == "Dict"
    assert type_map["items"] == "list"
    assert type_map["list_of_maps"] == "List"
    assert type_map["annotated_value"] == "Annotated"

    result = complex_fn(
        a_dict={"a": 1},
        mapping={"x": "y"},
        union_map={"num": 1, "flt": 2.0, "inner": {"k": "v"}, "text": "hi"},
        items=[1, 2, 3],
        list_of_maps=[{"k": 1}],
    )
    assert result == "foo"
