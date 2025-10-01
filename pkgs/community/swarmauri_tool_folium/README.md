![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_folium" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_folium/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_folium.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_folium" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_folium" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_folium/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_folium?label=swarmauri_tool_folium&color=green" alt="PyPI - swarmauri_tool_folium"/></a>
</p>

---

# Swarmauri Tool Folium

Generates an interactive Folium map with optional markers and returns the HTML as a base64-encoded string. Designed for embedding maps in Swarmauri workflows or downstream UIs.

## Features

- Accepts a map center `(lat, lon)` plus an optional list of markers `(lat, lon, popup)`.
- Creates a Folium map (HTML) and returns `{"image_b64": <base64-html>}`.
- Easy to extend with additional Folium layers/tiles by subclassing.

## Prerequisites

- Python 3.10 or newer.
- [`folium`](https://python-visualization.github.io/folium/) (installed automatically).
- Network access if Folium needs to load tiles from external providers at render time.

## Installation

```bash
# pip
pip install swarmauri_tool_folium

# poetry
poetry add swarmauri_tool_folium

# uv (pyproject-based projects)
uv add swarmauri_tool_folium
```

## Quickstart

```python
import base64
from pathlib import Path
from swarmauri_tool_folium import FoliumTool

map_center = (40.7128, -74.0060)
markers = [(40.7128, -74.0060, "Marker 1"), (40.7328, -74.0010, "Marker 2")]

result = FoliumTool()(map_center, markers)
html_bytes = base64.b64decode(result["image_b64"])
Path("map.html").write_bytes(html_bytes)
```

Open `map.html` in a browser to interact with the generated map.

## Tips

- Customize map appearance by subclassing and adjusting `folium.Map` parameters (`tiles`, `zoom_start`, etc.).
- Add other Folium layers (heatmaps, choropleths) before saving to build richer visualizations.
- When serving maps via APIs, return the base64 string directly or write to a temporary HTML file and send its path.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
