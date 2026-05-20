![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_xmp_mp4/">
        <img src="https://static.pepy.tech/badge/swarmauri_xmp_mp4/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_mp4/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_mp4.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_mp4" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_mp4/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_mp4?label=swarmauri_xmp_mp4&color=green" alt="PyPI - swarmauri_xmp_mp4"/></a>
</p>

# swarmauri_xmp_mp4

`swarmauri_xmp_mp4` publishes the `MP4XMP` scaffold so ISO-BMFF containers (MP4, MOV, HEIF, AVIF) can eventually embed XMP packets via UUID boxes.

## Features

- **Design-first** â€“ establishes the interface contract for ISO-BMFF metadata operations.
- **Registry-native** â€“ extends `EmbedXmpBase`, ensuring managers can discover it automatically.
- **Expectation management** â€“ explicit `NotImplementedError` keeps integrators aware of remaining work.

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

- **Design-first** â€“ establishes the interface contract for ISO-BMFF metadata operations.
- **Registry-native** â€“ extends `EmbedXmpBase`, ensuring managers can discover it automatically.
- **Expectation management** â€“ explicit `NotImplementedError` keeps integrators aware of remaining work.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
