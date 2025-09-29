![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/pypi/dm/EmbedXMP" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP.svg"/></a>
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/pypi/pyversions/EmbedXMP" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/pypi/l/EmbedXMP" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/pypi/v/EmbedXMP?label=EmbedXMP&color=green" alt="PyPI - EmbedXMP"/></a>
</p>

---

# EmbedXMP

`EmbedXMP` collects every installed `EmbedXmpBase` implementation, discovers them via Swarmauri's dynamic registry, and exposes a single orchestrator that can embed, read, or remove XMP packets without worrying about container formats.

## Features

- **Dynamic discovery** – lazily imports modules named `swarmauri_xmp_*` and collects subclasses registered under `EmbedXmpBase`.
- **Unified interface** – delegates to the first handler whose `supports` method confirms compatibility with the payload.
- **Convenience wrappers** – module-level helpers (`embed`, `read`, `remove`) keep high-level workflows succinct.

## Installation

```bash
# pip
pip install EmbedXMP

# uv
uv add EmbedXMP
```

## Usage

```python
from pathlib import Path

from EmbedXMP import EmbedXMP, embed, embed_file, read, read_file_xmp

orchestrator = EmbedXMP()
image = Path("example.png")
packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed into the file in-place
embed_file(image, packet)

# Inspect metadata via the orchestrator API
xmp_text = orchestrator.read(image.read_bytes(), str(image))
print(xmp_text)
```

### How it works

- **Dynamic discovery** – lazily imports modules named `swarmauri_xmp_*` and collects subclasses registered under `EmbedXmpBase`.
- **Unified interface** – delegates to the first handler whose `supports` method confirms compatibility with the payload.
- **Convenience wrappers** – module-level helpers (`embed`, `read`, `remove`) keep high-level workflows succinct.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
