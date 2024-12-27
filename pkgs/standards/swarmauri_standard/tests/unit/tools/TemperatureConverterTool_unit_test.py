import pytest
from swarmauri.tools.concrete import TemperatureConverterTool as Tool

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'TemperatureConverterTool'


@pytest.mark.unit
@pytest.mark.parametrize(
    "from_unit, to_unit, value, expected_result",
    [
        ("celsius", "fahrenheit", 25, "77.0"),  # 25°C = 77°F
        ("kelvin", "celsius", 0, "-273.15"),  # 0K = -273.15°C
        ("fahrenheit", "kelvin", 32, "273.15"),  # 32°F = 273.15K
        ("celsius", "celsius", 25, "25"),  # Same unit conversion
        ("invalid_unit", "fahrenheit", 25, "Error: Unknown temperature unit."),
        ("celsius", "invalid_unit", 25, "Error: Unknown temperature unit."),
    ]
)
def test_call(from_unit, to_unit, value, expected_result):
    tool = Tool()
    expected_keys = {f"temperature_in_{to_unit}"}

    result = tool(from_unit=from_unit, to_unit=to_unit, value=value)

    if isinstance(result, str):
        assert result == expected_result
    else:
        assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
        assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
        assert isinstance(result.get(f"temperature_in_{to_unit}"), str), f"Expected str, but got {type(result.get(f'temperature_in_{to_unit}')).__name__}"

        assert result.get(f"temperature_in_{to_unit}") == expected_result, f"Expected Temperature {expected_result}, but got {result.get(f'temperature_in_{to_unit}')}"