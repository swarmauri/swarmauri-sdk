import json
from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class WeatherTool(ToolBase):
    def __init__(self):
        parameters = [
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
        ]
        
        super().__init__(name="WeatherTool", description="Fetch current weather info for a location", parameters=parameters)

    def __call__(self, location, unit="fahrenheit") -> str:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Weather Info: {weather_info}\n"
