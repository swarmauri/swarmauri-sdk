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
def test_call():
    tool = Tool()
    
    # Test Celsius to Fahrenheit conversion
    result = tool(from_unit="celsius", to_unit="fahrenheit", value=25)
    assert result == "77.0"  # 25°C = 77°F

    # Test Kelvin to Celsius conversion
    result = tool(from_unit="kelvin", to_unit="celsius", value=0)
    assert result == "-273.15"  # 0K = -273.15°C

    # Test Fahrenheit to Kelvin conversion
    result = tool(from_unit="fahrenheit", to_unit="kelvin", value=32)
    assert result == "273.15"  # 32°F = 273.15K

    # Test conversion with the same units
    result = tool(from_unit="celsius", to_unit="celsius", value=25)
    assert result == "25.0"  # Same unit conversion

    # Test invalid 'from_unit'
    result = tool(from_unit="invalid_unit", to_unit="fahrenheit", value=25)
    assert result == "Error: Unknown temperature unit."

    # Test invalid 'to_unit'
    result = tool(from_unit="celsius", to_unit="invalid_unit", value=25)
    assert result == "Error: Unknown temperature unit."

    # Test invalid value type
    result = tool(from_unit="celsius", to_unit="fahrenheit", value="invalid_value")
    assert result == "An error occurred: could not convert string to float: 'invalid_value'"

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'TemperatureConverterTool'
