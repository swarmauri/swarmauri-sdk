import pytest
from swarmauri.standard.tools.concrete.TemperatureConverterTool import TemperatureConverterTool as Tool

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
        ("celsius", "fahrenheit", "invalid_value",
         "An error occurred: could not convert string to float: 'invalid_value'"),
    ]
)
def test_call(from_unit, to_unit, value, expected_result):
    tool = Tool()

    result = tool(from_unit=from_unit, to_unit=to_unit, value=value)
    assert result == expected_result
