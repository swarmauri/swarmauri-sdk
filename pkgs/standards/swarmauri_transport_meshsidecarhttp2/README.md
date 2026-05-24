![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_meshsidecarhttp2/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_meshsidecarhttp2/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_meshsidecarhttp2/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_meshsidecarhttp2.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_meshsidecarhttp2/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_meshsidecarhttp2/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_meshsidecarhttp2" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_meshsidecarhttp2/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_meshsidecarhttp2?label=swarmauri_transport_meshsidecarhttp2&color=green" alt="PyPI - swarmauri_transport_meshsidecarhttp2"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Transport â€“ Mesh Sidecar HTTP/2

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


