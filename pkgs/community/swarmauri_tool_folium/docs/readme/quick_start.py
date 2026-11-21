import base64
from pathlib import Path
from swarmauri_tool_folium import FoliumTool

map_center = (40.7128, -74.0060)
markers = [(40.7128, -74.0060, "Marker 1"), (40.7328, -74.0010, "Marker 2")]

result = FoliumTool()(map_center, markers)
html_bytes = base64.b64decode(result["image_b64"])
Path("map.html").write_bytes(html_bytes)
