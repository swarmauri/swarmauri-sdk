![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_xmp_png/">
        <img src="https://static.pepy.tech/badge/swarmauri_xmp_png/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_png/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_png.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_png" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_png/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_png?label=swarmauri_xmp_png&color=green" alt="PyPI - swarmauri_xmp_png"/></a>
</p>
---

# swarmauri_xmp_png

`swarmauri_xmp_png` packages the production-grade `PNGXMP` handler. It reads, writes, and removes XMP packets stored in uncompressed iTXt chunks that follow Adobe's keyword guidance, making it immediately compatible with downstream asset pipelines.

## Features

- **Registry-ready** â€“ inherits from `EmbedXmpBase` so Swarmauri's dynamic registry can auto-discover the handler.
- **Spec compliant** â€“ emits iTXt chunks with the `XML:com.adobe.xmp` keyword and UTF-8 payloads.
- **Safety guards** â€“ `_ensure_xml` performs a minimal RDF/XML check before embedding metadata.

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

- **Dynamic discovery** â€“ the handler is automatically registered with `DynamicBase` consumers via inheritance.
- **Standards alignment** â€“ PNG metadata lives in an iTXt chunk per ISO 16684 guidance.
- **Predictable behavior** â€“ read/write/remove flows mirror each other so pipelines remain idempotent.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
