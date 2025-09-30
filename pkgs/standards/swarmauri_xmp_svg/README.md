![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_svg/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_svg" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_svg/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_svg.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_svg/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_svg" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_svg/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_svg" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_svg/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_svg?label=swarmauri_xmp_svg&color=green" alt="PyPI - swarmauri_xmp_svg"/></a>
</p>

---

# swarmauri_xmp_svg

`swarmauri_xmp_svg` provides the `SVGXMP` handler so vector graphics can embed, retrieve, and remove RDF/XML metadata via `<metadata>` elements.

## Features

- **Registry ready** – derives from `EmbedXmpBase` so Swarmauri runtimes discover it through the dynamic registry.
- **XML aware** – uses `ElementTree` to place metadata deterministically as the first child of `<svg>`.
- **Text fallback** – gracefully injects raw strings when the SVG cannot be parsed structurally.

## Installation

```bash
# pip
pip install swarmauri_xmp_svg

# uv
uv add swarmauri_xmp_svg
```

## Usage

```python
from pathlib import Path

from swarmauri_xmp_svg import SVGXMP

handler = SVGXMP()
svg_path = Path("example.svg")
xmp_packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Insert metadata into the SVG root element
updated_bytes = handler.write_xmp(svg_path.read_bytes(), xmp_packet)
svg_path.write_bytes(updated_bytes)

# Read the packet back
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove it if necessary
clean_bytes = handler.remove_xmp(updated_bytes)
```

### Why it works

- **XML aware** – parsing via `ElementTree` ensures metadata lands as the first child under `<svg>`.
- **Resilient fallback** – gracefully degrades to text insertion when the document cannot be parsed as XML.
- **Registry ready** – inherits from `EmbedXmpBase`, making runtime discovery effortless.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
