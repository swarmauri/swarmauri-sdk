![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_jpeg" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_jpeg/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_jpeg.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_jpeg" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_jpeg" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_jpeg/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_jpeg?label=swarmauri_xmp_jpeg&color=green" alt="PyPI - swarmauri_xmp_jpeg"/></a>
</p>

---

# swarmauri_xmp_jpeg

`swarmauri_xmp_jpeg` ships the `JPEGXMP` handler for embedding, reading, and removing XMP packets from JPEGs via APP1 segments that follow Adobe's namespace header.

## Features

- **Immediate discovery** – derives from `EmbedXmpBase` so dynamic registry consumers can import it automatically.
- **Header accuracy** – produces APP1 payloads prefixed with `http://ns.adobe.com/xap/1.0/\x00` as required by the specification.
- **Defensive parsing** – iterates markers safely and halts at SOS to avoid corrupting scan data.

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

- **APP1 discipline** – the implementation builds a compliant APP1 segment with the canonical XMP namespace string.
- **Dynamic registration** – inheriting from `EmbedXmpBase` means the handler is registered automatically for plugin discovery.
- **Robust parsing** – helper iterators validate segment structure, stopping safely at SOS or malformed markers.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
