![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_tiff/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_tiff" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_tiff/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_tiff.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_tiff/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_tiff" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_tiff/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_tiff" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_tiff/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_tiff?label=swarmauri_xmp_tiff&color=green" alt="PyPI - swarmauri_xmp_tiff"/></a>
</p>

---

# swarmauri_xmp_tiff

`swarmauri_xmp_tiff` introduces the `TIFFXMP` handler scaffold for managing XMP metadata in TIFF and DNG images via tag 700.

## Features

- **Future ready** – codifies the contract for TIFF/DNG metadata manipulation ahead of implementation work.
- **Registry connected** – extends `EmbedXmpBase`, so the handler is automatically registered for discovery.
- **Explicit messaging** – each method raises `NotImplementedError`, clarifying expectations for contributors.

## Installation

```bash
# pip
pip install swarmauri_xmp_tiff

# uv
uv add swarmauri_xmp_tiff
```

## Usage

```python
from swarmauri_xmp_tiff import TIFFXMP

handler = TIFFXMP()

try:
    handler.read_xmp(b"II*\x00...")
except NotImplementedError:
    print("TIFF XMP support is planned and currently unimplemented.")
```

### Why it works

- **Future ready** – codifies the contract for TIFF/DNG metadata manipulation ahead of implementation work.
- **Registry connected** – extends `EmbedXmpBase`, so the handler is automatically registered for discovery.
- **Explicit messaging** – each method raises `NotImplementedError`, clarifying expectations for contributors.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
