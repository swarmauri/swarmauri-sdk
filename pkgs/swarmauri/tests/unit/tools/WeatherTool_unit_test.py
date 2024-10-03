import pytest
from swarmauri.tools.concrete import WeatherTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'WeatherTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()
    location = 'Dallas'

    expected_result = "('Dallas', 'fahrenheit')"

    expected_keys = {'weather_info'}

    result = tool(location)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("weather_info"),
                      str), f"Expected str, but got {type(result.get('weather_info')).__name__}"

    assert result.get(
        "weather_info") == expected_result, f"Expected Weather Info is {expected_result}, but got {result.get('weather_info')}"

