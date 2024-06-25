from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class WeatherTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="location",
            type="string",
            description="The location for which to fetch weather information",
            required=True
        ),
        Parameter(
            name="unit",
            type="string",
            description="The unit for temperature ('fahrenheit' or 'celsius')",
            required=True,
            enum=["fahrenheit", "celsius"]
        )
    ])
    
    description: str = "Fetch current weather info for a location"
    type: Literal['WeatherTool'] = 'WeatherTool'

    def __call__(self, location, unit="fahrenheit") -> str:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Weather Info: {weather_info}\n"
