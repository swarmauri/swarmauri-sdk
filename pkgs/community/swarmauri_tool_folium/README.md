
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_folium" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_folium/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_folium/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_folium" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_folium" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_folium?label=swarmauri_tool_folium&color=green" alt="PyPI - swarmauri_tool_folium"/></a>
</p>

---

# Swarmauri Tool Folium

A tool to generate maps with markers using Folium.

## Installation

```bash
pip install swarmauri_tool_folium
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.tools.FoliumTool import FoliumTool

tool = FoliumTool()
map_center = (40.7128, -74.0060)
markers = [(40.7128, -74.0060, "Marker 1"), (40.7328, -74.0010, "Marker 2")]

result = tool(map_center, markers)
print(result['image_b64'])  # Prints the base64 string of the map image
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
