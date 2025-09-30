![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_gif/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_gif" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_gif/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_gif.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_gif/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_gif" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_gif/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_gif" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_gif/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_gif?label=swarmauri_xmp_gif&color=green" alt="PyPI - swarmauri_xmp_gif"/></a>
</p>

---

# swarmauri_xmp_gif

`swarmauri_xmp_gif` includes the `GIFXMP` handler that preserves XMP packets inside GIF89a application extensions using the canonical `XMP Data` identifier and `XMP` authentication code.

## Features

- **Registry native** – extends `EmbedXmpBase` so managers such as `EmbedXMP` can discover it through Swarmauri's dynamic registry.
- **Block aware** – iterates GIF sub-blocks safely and terminates on sentinel bytes to avoid corrupting animations.
- **Spec aligned** – writes uncompressed UTF-8 payloads that match Adobe's guidance for GIF metadata.

## Installation

```bash
# pip
pip install swarmauri_xmp_gif

# uv
uv add swarmauri_xmp_gif
```

## Usage

```python
from pathlib import Path

from swarmauri_xmp_gif import GIFXMP

handler = GIFXMP()
gif_path = Path("example.gif")
xmp_packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed using an application extension block
updated_bytes = handler.write_xmp(gif_path.read_bytes(), xmp_packet)
gif_path.write_bytes(updated_bytes)

# Retrieve the RDF/XML payload
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove the extension again
clean_bytes = handler.remove_xmp(updated_bytes)
```

### Why it works

- **Standards-based** – uses the XMP-defined App ID and Auth Code from Adobe's reference implementation.
- **Chunk-aware** – scans GIF sub-blocks safely, terminating on sentinel bytes and ignoring malformed payloads.
- **Registry-native** – inherits from `EmbedXmpBase`, so managers only need to query the component registry.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
