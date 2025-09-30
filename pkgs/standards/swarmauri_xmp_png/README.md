![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_png" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_png/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_png.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_png" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_png" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_png?label=swarmauri_xmp_png&color=green" alt="PyPI - swarmauri_xmp_png"/></a>
</p>

---

# swarmauri_xmp_png

`swarmauri_xmp_png` packages the production-grade `PNGXMP` handler. It reads, writes, and removes XMP packets stored in uncompressed iTXt chunks that follow Adobe's keyword guidance, making it immediately compatible with downstream asset pipelines.

## Features

- **Registry-ready** – inherits from `EmbedXmpBase` so Swarmauri's dynamic registry can auto-discover the handler.
- **Spec compliant** – emits iTXt chunks with the `XML:com.adobe.xmp` keyword and UTF-8 payloads.
- **Safety guards** – `_ensure_xml` performs a minimal RDF/XML check before embedding metadata.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_xmp_png

# uv
uv add swarmauri_xmp_png
```

## Usage

```python
from pathlib import Path

from swarmauri_xmp_png import PNGXMP

handler = PNGXMP()
image_path = Path("example.png")
xmp_packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed an XMP packet
updated_bytes = handler.write_xmp(image_path.read_bytes(), xmp_packet)
image_path.write_bytes(updated_bytes)

# Verify the packet can be recovered
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove XMP if necessary
clean_bytes = handler.remove_xmp(updated_bytes)
```

### Why it works

- **Dynamic discovery** – the handler is automatically registered with `DynamicBase` consumers via inheritance.
- **Standards alignment** – PNG metadata lives in an iTXt chunk per ISO 16684 guidance.
- **Predictable behavior** – read/write/remove flows mirror each other so pipelines remain idempotent.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
