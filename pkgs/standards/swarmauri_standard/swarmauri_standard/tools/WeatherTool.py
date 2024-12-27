from swarmauri_core.typing import SubclassUnion
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class WeatherTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="location",
                type="string",
                description="The location for which to fetch weather information",
                required=True,
            ),
            Parameter(
                name="unit",
                type="string",
                description="The unit for temperature ('fahrenheit' or 'celsius')",
                required=True,
                enum=["fahrenheit", "celsius"],
            ),
        ]
    )
    name: str = "WeatherTool"
    description: str = "Fetch current weather info for a location"
    type: Literal["WeatherTool"] = "WeatherTool"

    def __call__(self, location, unit="fahrenheit") -> Dict[str, str]:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return {"weather_info": str(weather_info)}


SubclassUnion.update(baseclass=ToolBase, type_name="WeatherTool", obj=WeatherTool)
