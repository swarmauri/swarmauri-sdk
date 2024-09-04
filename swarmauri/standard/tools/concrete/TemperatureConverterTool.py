from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class TemperatureConverterTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="from_unit",
            type="string",
            description="The unit of the input temperature ('celsius', 'fahrenheit', 'kelvin').",
            required=True,
            enum=["celsius", "fahrenheit", "kelvin"]
        ),
        Parameter(
            name="to_unit",
            type="string",
            description="The unit to convert the temperature to ('celsius', 'fahrenheit', 'kelvin').",
            required=True,
            enum=["celsius", "fahrenheit", "kelvin"]
        ),
        Parameter(
            name="value",
            type="number",
            description="The temperature value to convert.",
            required=True
        )
    ])
    name: str = 'TemperatureConverterTool'
    description: str = "Converts temperatures between Celsius, Fahrenheit, and Kelvin."
    type: Literal['TemperatureConverterTool'] = 'TemperatureConverterTool'

    def __call__(self, from_unit: str, to_unit: str, value: float) -> str:
        try:
            if from_unit == to_unit:
                return str(value)
            
            if from_unit == "celsius":
                if to_unit == "fahrenheit":
                    result = (value * 9/5) + 32
                elif to_unit == "kelvin":
                    result = value + 273.15
            elif from_unit == "fahrenheit":
                if to_unit == "celsius":
                    result = (value - 32) * 5/9
                elif to_unit == "kelvin":
                    result = (value - 32) * 5/9 + 273.15
            elif from_unit == "kelvin":
                if to_unit == "celsius":
                    result = value - 273.15
                elif to_unit == "fahrenheit":
                    result = (value - 273.15) * 9/5 + 32
            else:
                return "Error: Unknown temperature unit."
            
            return str(result)
        except Exception as e:
            return f"An error occurred: {str(e)}"

# Example usage:
tool = TemperatureConverterTool()
print(tool("celsius", "fahrenheit", 25))  # Should output: 77.0
print(tool("kelvin", "celsius", 0))       # Should output: -273.15
print(tool("fahrenheit", "kelvin", 32))   # Should output: 273.15