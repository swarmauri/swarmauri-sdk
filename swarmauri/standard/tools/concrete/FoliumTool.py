# standard/tools/concrete/FoliumTool.py
import folium
from typing import List, Tuple, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class FoliumTool(ToolBase):
    type: Literal['FoliumTool'] = 'FoliumTool'
    name: str = Field("FoliumTool", description="Tool to generate maps using Folium.")
    description: str = Field("Generates maps with markers using Folium.", description="Description of the FoliumTool")

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="map_center",
                type="tuple",
                description="The (latitude, longitude) center of the map.",
                required=True
            ),
            Parameter(
                name="markers",
                type="list",
                description="A list of (latitude, longitude, popup) tuples for markers.",
                required=False,
                default=[]
            ),
            Parameter(
                name="output_file",
                type="string",
                description="The filename where the map will be saved.",
                required=True
            )
        ]
    )

    def __call__(self, map_center: Tuple[float, float], markers: List[Tuple[float, float, str]], output_file: str):
        # Generate Map
        map_ = folium.Map(location=map_center, zoom_start=13)

        for lat, lon, popup in markers:
            folium.Marker(location=[lat, lon], popup=popup).add_to(map_)

        map_.save(output_file)
        #print(f"Map generated and saved to {output_file}")