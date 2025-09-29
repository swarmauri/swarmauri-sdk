![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_mp4" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_mp4/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_mp4.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_mp4" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_mp4" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_mp4?label=swarmauri_xmp_mp4&color=green" alt="PyPI - swarmauri_xmp_mp4"/></a>
</p>

---

# swarmauri_xmp_mp4

`swarmauri_xmp_mp4` publishes the `MP4XMP` scaffold so ISO-BMFF containers (MP4, MOV, HEIF, AVIF) can eventually embed XMP packets via UUID boxes.

## Features

- **Design-first** – establishes the interface contract for ISO-BMFF metadata operations.
- **Registry-native** – extends `EmbedXmpBase`, ensuring managers can discover it automatically.
- **Expectation management** – explicit `NotImplementedError` keeps integrators aware of remaining work.

## Installation

```bash
# pip
pip install swarmauri_xmp_mp4

# uv
uv add swarmauri_xmp_mp4
```

## Usage

```python
from swarmauri_xmp_mp4 import MP4XMP

handler = MP4XMP()

try:
    handler.write_xmp(b"\x00\x00\x00\x18ftypmp42...", "<rdf:RDF>...</rdf:RDF>")
except NotImplementedError:
    print("MP4 XMP support is forthcoming.")
```

### Why it works

- **Design-first** – establishes the interface contract for ISO-BMFF metadata operations.
- **Registry-native** – extends `EmbedXmpBase`, ensuring managers can discover it automatically.
- **Expectation management** – explicit `NotImplementedError` keeps integrators aware of remaining work.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
