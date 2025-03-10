import pytest
from swarmauri_tool_lexicaldensity.LexicalDensityTool import (
    LexicalDensityTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "LexicalDensityTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_call():
    tool = Tool()
    input_text = "This is a test sentence."
    expected_lexical_density = tool.calculate_lexical_density(input_text)

    result = tool(input_text)
    assert isinstance(result, dict)
    assert set(["lexical_density"]).issubset(result.keys())

    assert result["lexical_density"] == pytest.approx(expected_lexical_density, 0.01)


@pytest.mark.unit
def test_call_empty_text():
    tool = Tool()
    input_text = ""
    expected_lexical_density = 0.0

    result = tool(input_text)
    assert isinstance(result, dict)
    assert set(["lexical_density"]).issubset(result.keys())

    assert result["lexical_density"] == pytest.approx(expected_lexical_density, 0.01)
