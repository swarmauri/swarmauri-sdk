# standard/tools/concrete/FoliumTool.py
import folium
from typing import List, Tuple, Literal, Dict
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
import base64
import io


class FoliumTool(ToolBase):
    type: Literal["FoliumTool"] = "FoliumTool"
    name: str = Field("FoliumTool", description="Tool to generate maps using Folium.")
    description: str = Field(
        "Generates maps with markers using Folium.",
        description="Description of the FoliumTool",
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="map_center",
                type="tuple",
                description="The (latitude, longitude) center of the map.",
                required=True,
            ),
            Parameter(
                name="markers",
                type="list",
                description="A list of (latitude, longitude, popup) tuples for markers.",
                required=False,
                default=[],
            ),
        ]
    )

    def __call__(
        self,
        map_center: Tuple[float, float],
        markers: List[Tuple[float, float, str]],
    ) -> Dict[str, str]:
        """
        Generate a folium map with markers and return the map as a base64-encoded image.

        Parameters:
        map_center (Tuple[float, float]): Latitude and longitude for the map's center.
        markers (List[Tuple[float, float, str]]): A list of markers, where each marker is a tuple containing latitude,
                                              longitude, and popup text.

        Returns:
        Dict[str, str]: A dictionary containing the base64-encoded image of the generated map, with the key 'image_b64'.

        Example:
        >>> tool = FoliumTool()
        >>> map_center = (40.7128, -74.0060)
        >>> markers = [(40.7128, -74.0060, "Marker 1"), (40.7328, -74.0010, "Marker 2")]
        >>> result = tool(map_center, markers)
        >>> print(result['image_b64'])  # Prints the base64 string of the map image
        """
        # Generate the folium map
        map_ = folium.Map(location=map_center, zoom_start=13)

        # Add markers to the map
        for lat, lon, popup in markers:
            folium.Marker(location=[lat, lon], popup=popup).add_to(map_)

        # Save the map to an in-memory BytesIO object
        map_img = io.BytesIO()
        map_.save(map_img, close_file=False)

        # Encode the map as base64
        map_img.seek(0)  # Go to the beginning of the BytesIO object
        map_b64 = base64.b64encode(map_img.getvalue()).decode("utf-8")

        # Return the encoded map as a base64 string
        return {"image_b64": map_b64}
