<p align="center">
  <img src="https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg" alt="Swarmauri logotype" width="420" />
</p>

<h1 align="center">EmbedXMP</h1>

<p align="center">
  <a href="https://pypi.org/project/EmbedXMP/"><img src="https://img.shields.io/pypi/dm/EmbedXMP?style=for-the-badge" alt="PyPI - Downloads" /></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP.svg?style=for-the-badge" alt="Repository views" /></a>
  <a href="https://pypi.org/project/EmbedXMP/"><img src="https://img.shields.io/pypi/pyversions/EmbedXMP?style=for-the-badge" alt="Supported Python versions" /></a>
  <a href="https://pypi.org/project/EmbedXMP/"><img src="https://img.shields.io/pypi/l/EmbedXMP?style=for-the-badge" alt="License" /></a>
  <a href="https://pypi.org/project/EmbedXMP/"><img src="https://img.shields.io/pypi/v/EmbedXMP?style=for-the-badge&label=EmbedXMP" alt="Latest release" /></a>
</p>

---

EmbedXMP collects every installed `EmbedXmpBase` implementation, discovers them via Swarmauri's dynamic registry, and exposes a unified manager that can embed, read, or remove XMP packets without worrying about container formats.

## Features

- **Dynamic discovery** – lazily imports modules named `swarmauri_xmp_*` and collects subclasses registered under `EmbedXmpBase`.
- **Unified interface** – delegates to the first handler whose `supports` method confirms compatibility with the payload.
- **Convenience wrappers** – module-level helpers (`embed`, `read`, `remove`) keep high-level workflows succinct.
- **Async-friendly APIs** – integrate inside event loops without blocking when calling out to plugin hooks.
- **Media-format coverage** – load handlers for PNG, GIF, JPEG, SVG, WEBP, TIFF, PDF, and MP4 assets through extras.

## Installation

### Using `uv`

```bash
uv add EmbedXMP
```

### Using `pip`

```bash
pip install EmbedXMP
```

## Usage

```python
from pathlib import Path

from EmbedXMP import EmbedXMP, embed, embed_file, read, read_file_xmp

manager = EmbedXMP()
image = Path("example.png")
packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed into the file in place.
embed_file(image, packet)

# Inspect metadata via the manager API.
xmp_text = manager.read(image.read_bytes(), str(image))
print(xmp_text)

# Remove metadata from the file when it is no longer required.
manager.remove(image.read_bytes(), str(image))
```

> **Note**
> You can provide either a `path` or a `hint` keyword argument when calling
> `embed`, `read`, or `remove` to help the manager pick the correct handler. The
> values are interchangeable as long as they match when both are supplied.

### Async orchestration

EmbedXMP's manager can be shared inside asynchronous workflows by deferring media-aware work to plugin hooks:

```python
import asyncio
from pathlib import Path

from EmbedXMP import EmbedXMP, embed


async def embed_all(paths: list[str], packet: str) -> None:
    manager = EmbedXMP()
    for path in paths:
        data = Path(path).read_bytes()
        await asyncio.to_thread(embed, data, packet, hint=path)


asyncio.run(embed_all(["one.png", "two.svg"], "<x:xmpmeta>...</x:xmpmeta>"))
```

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/EmbedXMP>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/EmbedXMP#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>
