![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_webp/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_webp" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_webp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_webp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_webp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_webp" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_webp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_webp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_webp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_webp?label=swarmauri_xmp_webp&color=green" alt="PyPI - swarmauri_xmp_webp"/></a>
</p>

---

# swarmauri_xmp_webp

`swarmauri_xmp_webp` declares the `WebPXMP` handler scaffold for RIFF/WEBP containers and prepares the dynamic registry for a full implementation.

## Features

- **Forward compatible** – establishes class signatures today so future implementations slot straight into existing workflows.
- **Registry aligned** – inherits from `EmbedXmpBase`, enabling automatic discovery through Swarmauri's dynamic registry.
- **Clear contracts** – raises `NotImplementedError` for read/write/remove until the RIFF logic is complete.

## Installation

```bash
# pip
pip install swarmauri_xmp_webp

# uv
uv add swarmauri_xmp_webp
```

## Usage

```python
from swarmauri_xmp_webp import WebPXMP

handler = WebPXMP()

# Raises NotImplementedError until read/write/remove are implemented
try:
    handler.read_xmp(b"RIFF....WEBP")
except NotImplementedError:
    print("WebP XMP support is forthcoming.")
```

### Why it works

- **Forward compatible** – declaring the handler today reserves the RIFF chunk namespace for future work.
- **Registry alignment** – subclassing `EmbedXmpBase` means discovery logic will work without code changes once implemented.
- **Clear contracts** – explicit `NotImplementedError` exceptions communicate the remaining work to contributors.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
