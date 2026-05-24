![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_xmp_jpeg/">
        <img src="https://static.pepy.tech/badge/swarmauri_xmp_jpeg/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_jpeg/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_jpeg.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_jpeg" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_jpeg?label=swarmauri_xmp_jpeg&color=green" alt="PyPI - swarmauri_xmp_jpeg"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# swarmauri_xmp_jpeg

`swarmauri_xmp_jpeg` ships the `JPEGXMP` handler for embedding, reading, and removing XMP packets from JPEGs via APP1 segments that follow Adobe's namespace header.

## Features

- **Immediate discovery** â€“ derives from `EmbedXmpBase` so dynamic registry consumers can import it automatically.
- **Header accuracy** â€“ produces APP1 payloads prefixed with `http://ns.adobe.com/xap/1.0/\x00` as required by the specification.
- **Defensive parsing** â€“ iterates markers safely and halts at SOS to avoid corrupting scan data.

## Installation

```bash
# pip
pip install swarmauri_xmp_jpeg

# uv
uv add swarmauri_xmp_jpeg
```

## Usage

```python
from pathlib import Path

from swarmauri_xmp_jpeg import JPEGXMP

handler = JPEGXMP()
photo_path = Path("example.jpg")
xmp_packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Insert the packet right after the SOI marker
updated_bytes = handler.write_xmp(photo_path.read_bytes(), xmp_packet)
photo_path.write_bytes(updated_bytes)

# Confirm it can be recovered later
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Strip the packet if needed
clean_bytes = handler.remove_xmp(updated_bytes)
```

### Why it works

- **APP1 discipline** â€“ the implementation builds a compliant APP1 segment with the canonical XMP namespace string.
- **Dynamic registration** â€“ inheriting from `EmbedXmpBase` means the handler is registered automatically for plugin discovery.
- **Robust parsing** â€“ helper iterators validate segment structure, stopping safely at SOS or malformed markers.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0


