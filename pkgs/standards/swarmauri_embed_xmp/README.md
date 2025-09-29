![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_embed_xmp/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embed_xmp" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embed_xmp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embed_xmp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embed_xmp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embed_xmp" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embed_xmp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embed_xmp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embed_xmp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embed_xmp?label=swarmauri_embed_xmp&color=green" alt="PyPI - swarmauri_embed_xmp"/></a>
</p>

---

# swarmauri_embed_xmp

`swarmauri_embed_xmp` ships the manager responsible for discovering every installed `EmbedXmpBase` implementation. It offers a single entry point to embed, read, or remove XMP packets without hard-coding individual container handlers.

## Features

- **Dynamic discovery** – eagerly imports all `swarmauri_xmp_*` packages and inspects Swarmauri's registry for registered handlers.
- **Unified API** – exposes an `EmbedXMP` component plus functional helpers (`embed`, `read`, `remove`) for ergonomic access.
- **File utilities** – convenience helpers read from and write back to disk while delegating the heavy lifting to the detected handler.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_embed_xmp

# uv
uv add swarmauri_embed_xmp
```

## Usage

```python
from pathlib import Path

from swarmauri_embed_xmp import EmbedXMP, embed, read, remove

xmp_packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""
image_path = Path("example.png")
image_bytes = image_path.read_bytes()

# Work with the class directly
manager = EmbedXMP()
updated_bytes = manager.embed(image_bytes, xmp_packet, path=str(image_path))
extracted = manager.read(updated_bytes, path=str(image_path))
stripped = manager.remove(updated_bytes, path=str(image_path))

# Or leverage the functional shortcuts
overwritten = embed(image_bytes, xmp_packet, path=str(image_path))
maybe_xml = read(updated_bytes, path=str(image_path))
clean_bytes = remove(updated_bytes, path=str(image_path))
```

### Why it works

- **Registry alignment** – by subclassing `EmbedXmpBase`, the manager shares the same lifecycle as container-specific handlers.
- **Predictable dispatch** – `_select` compares headers and extensions to choose the appropriate handler, raising when none match.
- **Friendly ergonomics** – the helpers accept raw bytes, making the manager trivial to integrate into existing pipelines.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
