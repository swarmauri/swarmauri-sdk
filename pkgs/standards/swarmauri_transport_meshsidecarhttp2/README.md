![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-meshsidecarhttp2/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-meshsidecarhttp2" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_meshsidecarhttp2/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_meshsidecarhttp2.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-meshsidecarhttp2/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-meshsidecarhttp2" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-meshsidecarhttp2/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-meshsidecarhttp2" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-meshsidecarhttp2/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-meshsidecarhttp2?label=swarmauri-transport-meshsidecarhttp2&color=green" alt="PyPI - swarmauri-transport-meshsidecarhttp2"/>
    </a>
</p>

---

# Swarmauri Transport – Mesh Sidecar HTTP/2

`swarmauri-transport-meshsidecarhttp2` connects to local service mesh sidecars that already terminate mutual TLS.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-meshsidecarhttp2 --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-meshsidecarhttp2
```

## Usage

```python
import asyncio
from swarmauri_transport_meshsidecarhttp2 import MeshSidecarHttp2

async def call_sidecar() -> None:
    transport = MeshSidecarHttp2()
    async with transport.client(host="127.0.0.1", port=15001):
        await asyncio.sleep(1)  # interact with the sidecar connection here

asyncio.run(call_sidecar())
```

Delegate authentication and encryption to the mesh while keeping full control over the payload protocol from Swarmauri agents.
